"""Run exactly one token-weighted SFT optimizer step."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.training.sft_collator import SFTBatchCollator
from llm_post_training.training.sft_data import load_sft_training_examples
from llm_post_training.training.sft_plan import build_sft_epoch_plan
from llm_post_training.training.sft_tokenization import tokenize_sft_example


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def learning_rate_factor(step, warmup_steps, total_steps):
    """Warm up, then use cosine learning-rate decay."""

    if step < warmup_steps:
        return (step + 1) / warmup_steps

    progress = (step - warmup_steps) / max(
        1, total_steps - warmup_steps
    )
    progress = min(1.0, max(0.0, progress))

    return 0.5 * (1.0 + math.cos(math.pi * progress))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))

    model_config = config["model"]
    data_config = config["dataset"]
    lora_settings = config["lora"]
    training = config["training"]

    # This program must NEVER silently become a full training run.
    assert config["config_version"] == "sft_lora_v1"
    assert config["experiment_id"] == "E002"
    assert training["expected_total_optimizer_steps"] == 422
    assert training["microbatch_size"] == 4
    assert training["gradient_accumulation_steps"] == 8
    assert training["accumulation_normalization"] == "supervised_tokens"
    assert training["warmup_steps"] == 13
    assert training["scheduler"] == "cosine"

    assert model_config["model_id"] == "Qwen/Qwen3-0.6B-Base"
    assert model_config["revision"] == (
        "57ca99e94acb83175495aa2c6b6b0cc498170924"
    )

    assert model_config["base_dtype"] == "float16"
    assert model_config["adapter_dtype"] == "float32"
    assert model_config["attention_implementation"] == "eager"
    assert model_config["use_cache"] is False

    assert data_config["split"] == "training"
    assert data_config["expected_examples"] == 6726
    assert data_config["max_sequence_length"] == 512
    assert data_config["truncation"] is False

    assert torch.cuda.is_available()
    assert torch.cuda.get_device_capability(0) == (7, 0)

    torch.manual_seed(config["seed"])
    torch.cuda.manual_seed_all(config["seed"])
    torch.backends.python_native.triton.enabled = False

    # Refuse to overwrite any existing run artifacts.
    args.output_dir.mkdir(parents=True, exist_ok=False)

    print("=== SFT TRAINING-LOOP SMOKE TEST ===", flush=True)
    print("GPU:", torch.cuda.get_device_name(0))
    print("Optimizer steps permitted: 1")
    print("Output directory:", args.output_dir)

    print("\n=== PREPARING DATA ===", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(
        model_config["model_id"],
        revision=model_config["revision"],
        local_files_only=True,
    )

    assert tokenizer.eos_token_id == 151645
    assert tokenizer.pad_token_id == 151643

    examples = load_sft_training_examples(
        Path(data_config["source_path"]),
        Path(data_config["manifest_path"]),
    )

    assert len(examples) == 6726

    tokenized = [
        tokenize_sft_example(example, tokenizer)
        for example in examples
    ]

    plan = build_sft_epoch_plan(
        tokenized,
        epoch=0,
        seed=config["seed"],
        microbatch_size=training["microbatch_size"],
        gradient_accumulation_steps=(
            training["gradient_accumulation_steps"]
        ),
        max_sequence_length=data_config["max_sequence_length"],
    )

    assert plan.optimizer_steps == 211

    # Process ONE complete accumulation group, not the epoch.
    group = plan.groups[0]

    assert len(group.microbatches) == 8
    assert sum(map(len, group.microbatches)) == 32

    print("Dataset examples:", len(tokenized))
    print("Epoch optimizer steps:", plan.optimizer_steps)
    print("Microbatches in this smoke test:", len(group.microbatches))
    print("Examples in this smoke test:", 32)
    print(
        "Supervised tokens in accumulation group:",
        group.total_supervised_tokens,
    )

    collator = SFTBatchCollator(
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        max_seq_length=512,
    )

    print("\n=== LOADING MODEL ===", flush=True)

    base = AutoModelForCausalLM.from_pretrained(
        model_config["model_id"],
        revision=model_config["revision"],
        local_files_only=True,
        dtype=torch.float16,
        attn_implementation="eager",
    )

    base.config.use_cache = False

    lora_config = LoraConfig(
        r=lora_settings["rank"],
        lora_alpha=lora_settings["alpha"],
        lora_dropout=lora_settings["dropout"],
        bias=lora_settings["bias"],
        target_modules=lora_settings["target_modules"],
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(
        base,
        lora_config,
        autocast_adapter_dtype=True,
    ).to("cuda")

    model.train()

    trainable = [
        (name, parameter)
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    ]

    frozen = [
        (name, parameter)
        for name, parameter in model.named_parameters()
        if not parameter.requires_grad
    ]

    parameters = [parameter for _, parameter in trainable]

    assert sum(p.numel() for p in parameters) == 2_293_760
    assert all(p.dtype == torch.float32 for p in parameters)
    assert all(p.dtype == torch.float16 for _, p in frozen)

    # Verify a representative frozen weight remains unchanged.
    probes = [
        parameter
        for name, parameter in frozen
        if name.endswith(
            "layers.0.self_attn.q_proj.base_layer.weight"
        )
    ]

    assert len(probes) == 1

    frozen_probe = probes[0]
    frozen_before = frozen_probe.detach().clone()

    # Verify the optimizer changes a LoRA B matrix.
    b_probes = [
        parameter
        for name, parameter in trainable
        if name.endswith(
            "layers.0.self_attn.q_proj.lora_B.default.weight"
        )
    ]

    assert len(b_probes) == 1

    b_probe = b_probes[0]
    b_before = b_probe.detach().clone()

    optimizer = torch.optim.AdamW(
        parameters,
        lr=training["learning_rate"],
        betas=(
            training["adam_beta1"],
            training["adam_beta2"],
        ),
        eps=training["adam_epsilon"],
        weight_decay=training["weight_decay"],
    )

    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lr_lambda=lambda step: learning_rate_factor(
            step,
            training["warmup_steps"],
            training["expected_total_optimizer_steps"],
        ),
    )

    print("Trainable LoRA parameters: 2,293,760")
    print("Optimizer:", training["optimizer"])
    print("Scheduler:", training["scheduler"])
    print("Warmup steps:", training["warmup_steps"])

    print("\n=== GRADIENT ACCUMULATION ===", flush=True)

    optimizer.zero_grad(set_to_none=True)
    torch.cuda.reset_peak_memory_stats()

    weighted_loss_sum = 0.0
    observed_tokens = 0
    source_indices = []

    for microbatch_number, (
        positions,
        expected_tokens,
        weight,
    ) in enumerate(
        zip(
            group.microbatches,
            group.supervised_tokens_per_batch,
            group.loss_weights,
        ),
        start=1,
    ):
        selected = [tokenized[index] for index in positions]

        source_indices.extend(
            example.source_index for example in selected
        )

        batch = collator(selected)

        actual_tokens = int(
            (batch["labels"][:, 1:] != -100).sum().item()
        )

        assert actual_tokens == expected_tokens

        batch = {
            key: value.to("cuda")
            for key, value in batch.items()
        }

        outputs = model(**batch)
        loss = outputs.loss

        assert torch.isfinite(loss).item()

        loss_value = float(loss.detach().item())

        (loss * weight).backward()

        weighted_loss_sum += loss_value * weight
        observed_tokens += actual_tokens

        print(
            f"Microbatch {microbatch_number}/8: "
            f"length={batch['input_ids'].shape[1]}, "
            f"tokens={actual_tokens}, "
            f"mean_loss={loss_value:.6f}",
            flush=True,
        )

        del outputs, loss, batch

    assert observed_tokens == group.total_supervised_tokens
    assert len(source_indices) == 32
    assert len(set(source_indices)) == 32

    assert all(
        parameter.grad is not None
        and torch.isfinite(parameter.grad).all().item()
        for parameter in parameters
    )

    assert all(
        parameter.grad is None
        for _, parameter in frozen
    )

    print("\n=== OPTIMIZER UPDATE ===", flush=True)

    global_grad_norm = torch.nn.utils.clip_grad_norm_(
        parameters,
        max_norm=training["max_grad_norm"],
        error_if_nonfinite=True,
    )

    assert torch.isfinite(global_grad_norm).item()
    assert global_grad_norm.item() > 0

    learning_rate_used = optimizer.param_groups[0]["lr"]

    optimizer.step()
    scheduler.step()

    assert not torch.equal(
        b_probe.detach(),
        b_before,
    )

    assert torch.equal(
        frozen_probe.detach(),
        frozen_before,
    )

    assert all(
        torch.isfinite(parameter).all().item()
        for parameter in parameters
    )

    torch.cuda.synchronize()

    allocated_mib = (
        torch.cuda.max_memory_allocated() / 1024**2
    )

    reserved_mib = (
        torch.cuda.max_memory_reserved() / 1024**2
    )

    print("Weighted accumulation loss:", weighted_loss_sum)
    print("Gradient norm before clipping:", global_grad_norm.item())
    print("Learning rate used:", learning_rate_used)
    print("Next scheduled LR:", optimizer.param_groups[0]["lr"])
    print("Frozen weights unchanged: PASSED")
    print("LoRA B parameter updated: PASSED")
    print("Peak allocated VRAM (MiB):", round(allocated_mib, 2))
    print("Peak reserved VRAM (MiB):", round(reserved_mib, 2))

    print("\n=== SAVING DIAGNOSTIC ADAPTER ===", flush=True)

    adapter_dir = args.output_dir / "smoke_step_0001"

    model.save_pretrained(
        adapter_dir,
        safe_serialization=True,
    )

    assert (adapter_dir / "adapter_config.json").is_file()
    assert (adapter_dir / "adapter_model.safetensors").is_file()

    summary = {
        "run_type": "engineering_smoke_test",
        "experiment_config_id": config["config_version"],
        "config_sha256": sha256_file(args.config),
        "dataset_manifest_sha256": sha256_file(
            Path(data_config["manifest_path"])
        ),
        "model_id": model_config["model_id"],
        "model_revision": model_config["revision"],
        "seed": config["seed"],
        "optimizer_steps": 1,
        "microbatches": 8,
        "training_examples": 32,
        "source_indices": source_indices,
        "supervised_tokens": observed_tokens,
        "weighted_loss": weighted_loss_sum,
        "gradient_norm_before_clipping": global_grad_norm.item(),
        "learning_rate_used": learning_rate_used,
        "peak_allocated_vram_mib": allocated_mib,
        "peak_reserved_vram_mib": reserved_mib,
        "adapter_path": str(adapter_dir),
    }

    write_json(args.output_dir / "summary.json", summary)

    print("Adapter:", adapter_dir)
    print("Summary:", args.output_dir / "summary.json")
    print("Full E002 training started: NO")
    print("\nSFT training-loop smoke test: PASSED")


if __name__ == "__main__":
    main()
