"""Train pinned Qwen3 LoRA on the frozen GSM8K development-training partition.

Modes:
  engineering_smoke_test: at most two optimizer steps; no resumable epoch state.
  formal_training: all 422 steps, with epoch-boundary state checkpoints.
"""

import argparse
import hashlib
import json
import math
import os
import random
import re
import time
from pathlib import Path

import numpy as np
import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.training.sft_checkpoint import (
    restore_epoch_training_state,
    save_epoch_checkpoint,
    verify_epoch_checkpoint,
)
from llm_post_training.training.sft_collator import SFTBatchCollator
from llm_post_training.training.sft_data import load_sft_training_examples
from llm_post_training.training.sft_plan import build_sft_epoch_plan
from llm_post_training.training.sft_tokenization import tokenize_sft_example

MODEL_ID = "Qwen/Qwen3-0.6B-Base"
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]
EXPECTED_LORA_PARAMETERS = 2_293_760
EXPECTED_STEPS_PER_EPOCH = 211
EXPECTED_TOTAL_STEPS = 422
EXPECTED_SOURCE_SHA = "17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465"
EXPECTED_MANIFEST_SHA = "31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_new(path: Path, value: dict) -> None:
    # Do not silently overwrite metadata or results.
    with path.open("x", encoding="utf-8") as output:
        json.dump(value, output, sort_keys=True, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())


def get_supervised_eos_token_id(config: dict) -> int:
    """Return the explicitly selected SFT termination target."""
    return config["dataset"].get("target_eos_token_id", 151645)


def validate_config(config: dict) -> None:
    """Refuse protocol changes until a new config version is reviewed."""
    model = config["model"]
    data = config["dataset"]
    lora = config["lora"]
    train = config["training"]
    evaluation = config["evaluation"]

    is_native_eos = (
        config["config_version"] == "sft_lora_native_eos_v1"
    )

    if is_native_eos:
        if (
            type(data.get("target_eos_token_id")) is not int
            or data["target_eos_token_id"] != 151643
        ):
            raise ValueError(
                "E002a must supervise native EOS token 151643"
            )

        if evaluation.get("protocol_version") != (
            "gsm8k_val512_greedy_eager_cached_v1"
        ):
            raise ValueError(
                "E002a must declare the cached evaluation protocol"
            )
    else:
        if "target_eos_token_id" in data:
            raise ValueError(
                "E002 must not override its original EOS target"
            )

        if "protocol_version" in evaluation:
            raise ValueError(
                "E002 must preserve its original evaluation protocol"
            )

    expected = [
        (
            config["config_version"] in (
                "sft_lora_v1",
                "sft_lora_native_eos_v1",
            ),
            "config version",
        ),
        (
            config["experiment_id"]
            == ("E002a" if is_native_eos else "E002"),
            "experiment ID",
        ),
        (config["experiment_type"] == "supervised_fine_tuning", "experiment type"),
        (config["seed"] == 42, "seed"),
        (model["model_id"] == MODEL_ID, "model ID"),
        (model["revision"] == MODEL_REVISION, "model revision"),
        (model["base_dtype"] == "float16", "base dtype"),
        (model["adapter_dtype"] == "float32", "adapter dtype"),
        (model["attention_implementation"] == "eager", "attention"),
        (model["use_cache"] is False, "training KV cache"),
        (data["split"] == "training", "training split"),
        (data["expected_examples"] == 6726, "training coverage"),
        (data["prompt_version"] == "gsm8k_qa_v1", "training prompt"),
        (data["max_sequence_length"] == 512, "sequence length"),
        (data["truncation"] is False, "truncation"),
        (lora["rank"] == 8, "LoRA rank"),
        (lora["alpha"] == 16, "LoRA alpha"),
        (lora["dropout"] == 0.05, "LoRA dropout"),
        (lora["bias"] == "none", "LoRA bias"),
        (lora["target_modules"] == TARGET_MODULES, "LoRA modules"),
        (train["num_epochs"] == 2, "epochs"),
        (train["microbatch_size"] == 4, "microbatch size"),
        (train["gradient_accumulation_steps"] == 8, "gradient accumulation"),
        (train["expected_optimizer_steps_per_epoch"] == EXPECTED_STEPS_PER_EPOCH, "steps per epoch"),
        (train["expected_total_optimizer_steps"] == EXPECTED_TOTAL_STEPS, "total steps"),
        (train["accumulation_normalization"] == "supervised_tokens", "loss weighting"),
        (train["optimizer"] == "adamw", "optimizer"),
        (train["learning_rate"] == 1e-4, "learning rate"),
        (train["weight_decay"] == 0.0, "weight decay"),
        (train["adam_beta1"] == 0.9, "Adam beta1"),
        (train["adam_beta2"] == 0.999, "Adam beta2"),
        (train["adam_epsilon"] == 1e-8, "Adam epsilon"),
        (train["scheduler"] == "cosine", "LR scheduler"),
        (train["warmup_steps"] == 13, "warmup"),
        (train["max_grad_norm"] == 1.0, "gradient clipping"),
        (train["log_every_optimizer_steps"] == 10, "logging cadence"),
        (train["save_checkpoint_each_epoch"] is True, "checkpoint cadence"),
        (evaluation["split"] == "validation", "evaluation split"),
        (evaluation["expected_examples"] == 747, "validation size"),
        (evaluation["prompt_version"] == "gsm8k_qa_v1", "evaluation prompt"),
        (evaluation["answer_extraction_version"] == "explicit_numeric_v2", "answer extraction"),
        (evaluation["max_new_tokens"] == 512, "generation budget"),
        (evaluation["decoding"] == "greedy", "decoding"),
        (
            evaluation["use_cache"] is is_native_eos,
            "evaluation KV cache",
        ),
    ]
    for valid, field in expected:
        if not valid:
            raise ValueError(
                f"Unexpected {config['experiment_id']} "
                f"configuration: {field}"
            )

    if len({data["source_path"], data["manifest_path"]}) != 2:
        raise ValueError("Source and manifest paths must differ")


def learning_rate_factor(step: int, warmup: int, total: int) -> float:
    if step < warmup:
        return (step + 1) / warmup
    progress = min(1.0, max(0.0, (step - warmup) / (total - warmup)))
    return 0.5 * (1.0 + math.cos(math.pi * progress))


def read_records(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def reconcile_logs_for_resume(path: Path, completed_steps: int) -> None:
    """Discard progress past a committed epoch checkpoint after a crash."""
    records = read_records(path)
    committed = [r for r in records if r["optimizer_step"] <= completed_steps]
    observed = [r["optimizer_step"] for r in committed]
    if observed != list(range(1, completed_steps + 1)):
        raise ValueError("Training log missing or duplicates committed optimizer steps")
    temp = path.with_name(path.name + ".recovered.tmp")
    if temp.exists():
        raise FileExistsError(temp)
    with temp.open("x", encoding="utf-8") as output:
        for record in committed:
            output.write(json.dumps(record, sort_keys=True) + "\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temp, path)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--run-type", required=True,
        choices=("engineering_smoke_test", "formal_training"),
    )
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--docker-image-id", required=True)
    parser.add_argument("--smoke-optimizer-steps", type=int)
    parser.add_argument("--resume-from", type=Path)
    parser.add_argument("--stop-after-epoch", type=int)
    return parser.parse_args()


def validate_pause_request(run_type, stop_after_epoch, resume_from):
    """Allow a deliberate stop only after formal epoch one."""
    if stop_after_epoch is None:
        return
    if run_type != "formal_training":
        raise ValueError("Epoch pause is for formal training only")
    if stop_after_epoch != 1:
        raise ValueError("Only --stop-after-epoch 1 is supported")
    if resume_from is not None:
        raise ValueError("Cannot request a pause while resuming")


def main():
    args = parse_args()
    validate_pause_request(args.run_type, args.stop_after_epoch, args.resume_from)
    if re.fullmatch(r"[0-9a-f]{40}", args.code_revision) is None:
        raise ValueError("--code-revision must be a 40-character Git SHA")
    if re.fullmatch(r"sha256:[0-9a-f]{64}", args.docker_image_id) is None:
        raise ValueError("--docker-image-id must be a Docker SHA-256 image ID")
    if args.run_type == "engineering_smoke_test":
        if args.resume_from is not None:
            raise ValueError("Smoke runs cannot resume formal checkpoints")
        if args.smoke_optimizer_steps is None or not 1 <= args.smoke_optimizer_steps <= 2:
            raise ValueError("Smoke runs require --smoke-optimizer-steps 1 or 2")
    else:
        if args.smoke_optimizer_steps is not None:
            raise ValueError("Formal training cannot specify smoke step limit")

    config = json.loads(args.config.read_text(encoding="utf-8"))
    validate_config(config)
    supervised_eos_id = get_supervised_eos_token_id(config)
    config_sha = sha256_file(args.config)
    data_config = config["dataset"]
    train_config = config["training"]
    checkpoint_mode = args.run_type == "formal_training"
    source_hash = sha256_file(Path(data_config["source_path"]))
    manifest_hash = sha256_file(Path(data_config["manifest_path"]))
    if source_hash != EXPECTED_SOURCE_SHA or manifest_hash != EXPECTED_MANIFEST_SHA:
        raise ValueError("Frozen GSM8K source or split manifest checksum differs from E001")

    assert torch.cuda.is_available(), "CUDA is required"
    assert torch.cuda.get_device_capability(0) == (7, 0), "Expected V100 (sm_70)"
    torch.backends.python_native.triton.enabled = False
    torch.backends.cudnn.benchmark = False
    random.seed(config["seed"])
    np.random.seed(config["seed"])
    torch.manual_seed(config["seed"])
    torch.cuda.manual_seed_all(config["seed"])

    metadata = {
        "run_type": args.run_type,
        "experiment_id": config["experiment_id"],
        "config_sha256": config_sha,
        "code_revision": args.code_revision,
        "docker_image_id": args.docker_image_id,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "dataset_source_sha256": source_hash,
        "dataset_manifest_sha256": manifest_hash,
        "seed": config["seed"],
        "planned_optimizer_steps": EXPECTED_TOTAL_STEPS if checkpoint_mode else args.smoke_optimizer_steps,
        "resume_policy": "epoch_boundary_only" if checkpoint_mode else "not_resumable",
    }

    if config["experiment_id"] == "E002a":
        metadata["supervised_eos_token_id"] = supervised_eos_id

    output_dir = args.output_dir
    log_path = output_dir / "training_log.jsonl"
    start_epoch = 0
    completed_steps = 0

    if args.resume_from is None:
        output_dir.mkdir(parents=True, exist_ok=False)
        write_json_new(output_dir / "run_metadata.json", metadata)
        log_path.touch(exist_ok=False)
    else:
        if not checkpoint_mode:
            raise ValueError("Resume requires formal training")
        if not output_dir.is_dir():
            raise FileNotFoundError(output_dir)
        old_meta = json.loads((output_dir / "run_metadata.json").read_text(encoding="utf-8"))
        if old_meta != metadata:
            raise ValueError("Existing run metadata differs from requested training configuration")
        resume_dir = args.resume_from.resolve()
        if resume_dir.parent != output_dir.resolve():
            raise ValueError("Resume checkpoint must be inside this run directory")
        manifest = verify_epoch_checkpoint(
            resume_dir,
            expected_config_sha256=config_sha,
            expected_code_revision=args.code_revision,
            expected_model_revision=MODEL_REVISION,
        )
        start_epoch = manifest["next_epoch"]
        completed_steps = manifest["completed_optimizer_steps"]
        if not 0 < start_epoch < train_config["num_epochs"]:
            raise ValueError("Resume checkpoint must be from an unfinished run")
        if resume_dir.name != f"epoch_{start_epoch:04d}":
            raise ValueError("Checkpoint directory does not match epoch")
        if completed_steps != start_epoch * EXPECTED_STEPS_PER_EPOCH:
            raise ValueError("Checkpoint step count does not match epoch")
        reconcile_logs_for_resume(log_path, completed_steps)

    print(
        f"=== {config['experiment_id']} SFT TRAINING ===",
        flush=True,
    )
    print("Mode:", args.run_type, flush=True)
    print("Config SHA-256:", config_sha, flush=True)
    print("Code revision:", args.code_revision, flush=True)
    print("Start epoch:", start_epoch + 1, flush=True)
    print("Completed steps before run:", completed_steps, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, local_files_only=True,
    )
    assert tokenizer.eos_token_id == 151645
    assert tokenizer.pad_token_id == 151643
    examples = load_sft_training_examples(
        Path(data_config["source_path"]),
        Path(data_config["manifest_path"]),
    )
    assert len(examples) == 6726
    tokenized = [
        tokenize_sft_example(
            example,
            tokenizer,
            target_eos_token_id=supervised_eos_id,
        )
        for example in examples
    ]

    assert max(x.sequence_length for x in tokenized) <= 512

    assert all(
        record.input_ids[-1] == supervised_eos_id
        and record.labels[-1] == supervised_eos_id
        and record.attention_mask[-1] == 1
        for record in tokenized
    ), "Dataset contains an invalid supervised EOS target"

    collator = SFTBatchCollator(
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=supervised_eos_id,
        max_seq_length=512,
        allow_pad_eos_collision=(
            supervised_eos_id == tokenizer.pad_token_id
        ),
    )

    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=True,
        dtype=torch.float16,
        attn_implementation="eager",
    )
    base.config.use_cache = False

    if config["experiment_id"] == "E002a":
        assert base.config.eos_token_id == supervised_eos_id, (
            "E002a target must match the base model's native EOS"
        )

    if args.resume_from is None:
        lora = config["lora"]
        model = get_peft_model(
            base,
            LoraConfig(
                r=lora["rank"],
                lora_alpha=lora["alpha"],
                lora_dropout=lora["dropout"],
                bias=lora["bias"],
                target_modules=lora["target_modules"],
                task_type=TaskType.CAUSAL_LM,
            ),
            autocast_adapter_dtype=True,
        )
    else:
        model = PeftModel.from_pretrained(
            base,
            str(resume_dir / "adapter"),
            is_trainable=True,
            autocast_adapter_dtype=True,
        )

    model = model.to("cuda")
    model.train()
    trainable = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    frozen = [p for p in model.parameters() if not p.requires_grad]
    parameters = [p for _, p in trainable]
    assert sum(p.numel() for p in parameters) == EXPECTED_LORA_PARAMETERS
    assert len(trainable) == 224
    assert all("lora_" in n and p.dtype == torch.float32 for n, p in trainable)
    assert all(p.dtype == torch.float16 for p in frozen)

    optimizer = torch.optim.AdamW(
        parameters,
        lr=train_config["learning_rate"],
        betas=(train_config["adam_beta1"], train_config["adam_beta2"]),
        eps=train_config["adam_epsilon"],
        weight_decay=train_config["weight_decay"],
    )
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lr_lambda=lambda step: learning_rate_factor(
            step, train_config["warmup_steps"], EXPECTED_TOTAL_STEPS
        ),
    )

    if args.resume_from is not None:
        restored = restore_epoch_training_state(
            resume_dir,
            optimizer=optimizer,
            scheduler=scheduler,
            expected_config_sha256=config_sha,
            expected_code_revision=args.code_revision,
            expected_model_revision=MODEL_REVISION,
        )
        assert restored["completed_optimizer_steps"] == completed_steps
        assert scheduler.last_epoch == completed_steps, (
            "Restored scheduler step differs from completed optimizer steps"
        )
        print("Optimizer, scheduler, and RNG state restored.", flush=True)

    epoch_logs = []
    last_step_record = None
    smoke_limit = args.smoke_optimizer_steps
    with log_path.open("a", encoding="utf-8", buffering=1) as log:
        for epoch in range(start_epoch, train_config["num_epochs"]):
            plan = build_sft_epoch_plan(
                tokenized,
                epoch=epoch,
                seed=config["seed"],
                microbatch_size=train_config["microbatch_size"],
                gradient_accumulation_steps=train_config["gradient_accumulation_steps"],
                max_sequence_length=data_config["max_sequence_length"],
            )
            assert plan.optimizer_steps == EXPECTED_STEPS_PER_EPOCH
            assert plan.microbatch_count == 1682
            epoch_tokens = 0
            epoch_loss_numerator = 0.0
            epoch_examples = 0
            epoch_started = time.monotonic()
            print(f"\n=== EPOCH {epoch+1}/2 ===", flush=True)

            for epoch_step, group in enumerate(plan.groups, 1):
                optimizer.zero_grad(set_to_none=True)
                weighted_loss = 0.0
                counted_tokens = 0
                examples_in_group = 0
                for positions, token_count, weight in zip(
                    group.microbatches,
                    group.supervised_tokens_per_batch,
                    group.loss_weights,
                ):
                    selected = [tokenized[index] for index in positions]
                    batch = collator(selected)
                    actual_tokens = int((batch["labels"][:, 1:] != -100).sum().item())
                    if actual_tokens != token_count:
                        raise ValueError("Planner/collator supervised-token disagreement")
                    batch = {name: tensor.to("cuda") for name, tensor in batch.items()}
                    loss = model(**batch).loss
                    if not torch.isfinite(loss).item():
                        raise FloatingPointError("Nonfinite SFT loss")
                    (loss * weight).backward()
                    weighted_loss += float(loss.detach().item()) * weight
                    counted_tokens += actual_tokens
                    examples_in_group += len(positions)
                    del loss, batch
                if counted_tokens != group.total_supervised_tokens:
                    raise ValueError("Accumulation-group supervised-token mismatch")
                assert examples_in_group == (6 if epoch_step == 211 else 32)
                norm = torch.nn.utils.clip_grad_norm_(
                    parameters,
                    max_norm=train_config["max_grad_norm"],
                    error_if_nonfinite=True,
                )
                if not torch.isfinite(norm).item():
                    raise FloatingPointError("Nonfinite gradient norm")
                lr_used = optimizer.param_groups[0]["lr"]
                optimizer.step()
                scheduler.step()
                completed_steps += 1
                epoch_tokens += counted_tokens
                epoch_examples += examples_in_group
                epoch_loss_numerator += weighted_loss * counted_tokens
                record = {
                    "optimizer_step": completed_steps,
                    "epoch": epoch + 1,
                    "epoch_step": epoch_step,
                    "examples": examples_in_group,
                    "supervised_tokens": counted_tokens,
                    "mean_supervised_token_loss": weighted_loss,
                    "gradient_norm_before_clipping": float(norm.item()),
                    "learning_rate_used": lr_used,
                }
                log.write(json.dumps(record, sort_keys=True) + "\n")
                last_step_record = record
                if (not checkpoint_mode or epoch_step % train_config["log_every_optimizer_steps"] == 0
                        or epoch_step == plan.optimizer_steps):
                    print(
                        f"epoch={epoch+1} epoch_step={epoch_step}/211 "
                        f"total_step={completed_steps} loss={weighted_loss:.5f} "
                        f"tokens={counted_tokens} grad_norm={norm.item():.4f} "
                        f"lr={lr_used:.8g}",
                        flush=True,
                    )
                if not checkpoint_mode and completed_steps >= smoke_limit:
                    break

            if not checkpoint_mode:
                break
            if epoch_examples != 6726 or epoch_tokens != 632064:
                raise ValueError("Epoch data-coverage audit failed")
            if completed_steps != (epoch + 1) * EXPECTED_STEPS_PER_EPOCH:
                raise ValueError("Epoch optimizer-step audit failed")

            # Durably persist step logs before the checkpoint is published.
            log.flush()
            os.fsync(log.fileno())
            checkpoint_dir = output_dir / f"epoch_{epoch+1:04d}"
            save_epoch_checkpoint(
                checkpoint_dir,
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                completed_optimizer_steps=completed_steps,
                next_epoch=epoch + 1,
                config_sha256=config_sha,
                code_revision=args.code_revision,
                model_revision=MODEL_REVISION,
            )
            verify_epoch_checkpoint(
                checkpoint_dir,
                expected_config_sha256=config_sha,
                expected_code_revision=args.code_revision,
                expected_model_revision=MODEL_REVISION,
            )
            epoch_logs.append({
                "epoch": epoch + 1,
                "examples": epoch_examples,
                "supervised_tokens": epoch_tokens,
                "mean_supervised_token_loss": epoch_loss_numerator / epoch_tokens,
                "optimizer_steps": EXPECTED_STEPS_PER_EPOCH,
                "seconds": time.monotonic() - epoch_started,
                "checkpoint": str(checkpoint_dir),
            })
            print(f"Saved verified epoch checkpoint: {checkpoint_dir}", flush=True)
            if args.stop_after_epoch == epoch + 1:
                torch.cuda.synchronize()
                print("Formal run intentionally paused after verified epoch 1.", flush=True)
                print("No completion summary has been written.", flush=True)
                return

    torch.cuda.synchronize()
    summary = {
        **metadata,
        "completed_optimizer_steps": completed_steps,
        "epochs_completed": 2 if checkpoint_mode else 0,
        "training_complete": bool(checkpoint_mode and completed_steps == EXPECTED_TOTAL_STEPS),
        "epoch_summaries_this_invocation": epoch_logs,
        "last_optimizer_step_metrics": last_step_record,
        "peak_allocated_vram_mib": torch.cuda.max_memory_allocated() / 1024**2,
        "peak_reserved_vram_mib": torch.cuda.max_memory_reserved() / 1024**2,
    }
    if checkpoint_mode:
        if completed_steps != EXPECTED_TOTAL_STEPS:
            raise RuntimeError("Formal training did not reach 422 optimizer steps")
        write_json_new(output_dir / "summary.json", summary)
        print(
            f"{config['experiment_id']} SFT training: "
            "COMPLETED (evaluation still required)",
            flush=True,
        )
    else:
        model.save_pretrained(output_dir / "smoke_adapter", safe_serialization=True)
        write_json_new(output_dir / "summary.json", summary)
        print("Bounded SFT training smoke test: PASSED", flush=True)
        print(
            f"Full {config['experiment_id']} training started: NO",
            flush=True,
        )
    print("Steps completed:", completed_steps, flush=True)
    print("Training log:", log_path, flush=True)
    print("Summary:", output_dir / "summary.json", flush=True)


if __name__ == "__main__":
    main()
