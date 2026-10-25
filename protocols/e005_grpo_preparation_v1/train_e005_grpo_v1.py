"""E005 GRPO training implementation.

Default mode: CHECK ONLY.
Training is blocked while training_approved is false.

This script must run from the repository root in the pinned
Docker environment. Never uses the official GSM8K test set.
"""

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path


PLAN_PATH = Path(
    "protocols/e005_grpo_preparation_v1/"
    "e005_grpo_training_plan_v1.json"
)

SPLIT_PATH = Path("configs/data/gsm8k_split_v1.json")
RAW_PATH = Path("data/raw/gsm8k/train.jsonl")

SPLIT_SHA = (
    "31030317d85b015263d05383bf69bb02daec"
    "5bc67874f5ad0e0b33fa5294c719"
)

RAW_SHA = (
    "17f347dc51477c50d4efb83959dbb7c56297"
    "aba886e5544ee2aaed3024813465"
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(
        ["git", *args], text=True
    ).strip()


def validate_plan():
    """Read-only input, dependency, and configuration validation."""
    from transformers import AutoTokenizer
    from trl import GRPOConfig

    from llm_post_training.data.gsm8k import (
        parse_gsm8k_reference_answer,
    )
    from llm_post_training.evaluation.prompting import (
        BASELINE_PROMPT_VERSION,
        format_baseline_prompt,
    )
    from llm_post_training.training.grpo_reward import (
        GRPO_REWARD_VERSION,
        gsm8k_exact_numeric_reward,
    )

    plan = json.loads(PLAN_PATH.read_text())

    require(plan["experiment"] == "E005", "Wrong experiment")
    require(
        plan["schema_version"] == "e005_grpo_training_plan_v1",
        "Wrong plan schema",
    )

    require(
        plan["input_freeze_commit"]
        == "09e62a1ead14ede13bf7a39d14894dc0c85be502",
        "Unexpected dataset-freeze revision",
    )

    require(
        plan["docker_image_digest"]
        == "sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e",
        "Unexpected image digest",
    )

    require(
        plan["base_revision"]
        == "57ca99e94acb83175495aa2c6b6b0cc498170924",
        "Base model revision mismatch",
    )

    require(
        plan["base_model"] == "Qwen/Qwen3-0.6B-Base",
        "Base model mismatch",
    )

    require(
        importlib.metadata.version("trl") == "0.26.2",
        "TRL version changed",
    )
    require(
        importlib.metadata.version("transformers") == "4.57.6",
        "Transformers version changed",
    )
    require(
        importlib.metadata.version("peft") == "0.18.1",
        "PEFT version changed",
    )

    require(digest(SPLIT_PATH) == SPLIT_SHA, "Split SHA mismatch")
    require(digest(RAW_PATH) == RAW_SHA, "Raw GSM8K SHA mismatch")

    adapter_path = (
        Path(plan["initial_adapter"]["path"])
        / "adapter_model.safetensors"
    )

    require(
        digest(adapter_path) == plan["initial_adapter"]["sha256"],
        "Initial E002a adapter SHA mismatch",
    )

    dataset_info = plan["dataset"]
    dataset_path = Path(dataset_info["path"])

    require(
        digest(dataset_path) == dataset_info["sha256"],
        "GRPO dataset SHA mismatch",
    )

    require(
        digest(dataset_info["manifest_path"])
        == dataset_info["manifest_sha256"],
        "Dataset manifest SHA mismatch",
    )

    reward_info = plan["reward"]

    require(
        digest(reward_info["path"]) == reward_info["sha256"],
        "Reward implementation SHA mismatch",
    )

    require(
        GRPO_REWARD_VERSION == reward_info["version"],
        "Reward version mismatch",
    )

    require(
        BASELINE_PROMPT_VERSION == "gsm8k_qa_v1",
        "Prompt format changed",
    )

    split = json.loads(SPLIT_PATH.read_text())

    with RAW_PATH.open("r", encoding="utf-8") as handle:
        records = [
            json.loads(line)
            for line in handle
            if line.strip()
        ]

    with dataset_path.open("r", encoding="utf-8") as handle:
        rows = [
            json.loads(line)
            for line in handle
            if line.strip()
        ]

    indices = split["training_indices"]
    validation = set(split["validation_indices"])

    require(len(records) == 7473, "GSM8K row count changed")
    require(len(rows) == len(indices) == 6726, "Dataset size mismatch")
    require(len(validation) == 747, "Validation size changed")
    require(
        not (set(indices) & validation),
        "Training/validation overlap",
    )

    require(
        [row["source_index"] for row in rows] == indices,
        "Training source-index order changed",
    )

    for row in rows:
        idx = row["source_index"]
        reference = records[idx]

        require(
            row["prompt"]
            == format_baseline_prompt(reference["question"]),
            f"Training prompt mismatch at {idx}",
        )

        require(
            row["answer"] == reference["answer"],
            f"Reference answer mismatch at {idx}",
        )

        require(
            parse_gsm8k_reference_answer(row["answer"]).is_finite(),
            f"Invalid reference answer at {idx}",
        )

    tokenizer = AutoTokenizer.from_pretrained(
        plan["base_model"],
        revision=plan["base_revision"],
        local_files_only=True,
    )

    require(tokenizer.pad_token_id == 151643, "PAD mismatch")

    tokenizer.eos_token = tokenizer.convert_ids_to_tokens(151643)

    require(tokenizer.eos_token_id == 151643, "EOS mismatch")

    max_tokens = max(
        len(tokenizer.encode(row["prompt"], add_special_tokens=False))
        for row in rows
    )

    require(
        max_tokens == 215
        and max_tokens <= dataset_info["maximum_prompt_tokens"],
        "Training prompt lengths changed",
    )

    require(
        dataset_info["truncate_prompts"] is False,
        "Prompt truncation must be disabled",
    )

    h = plan["hyperparameters"]

    expected_h = {
        "max_steps": 256,
        "learning_rate": 1e-6,
        "num_generations": 4,
        "per_device_train_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "generation_batch_size": 4,
        "max_completion_length": 512,
        "temperature": 1.0,
        "top_p": 1.0,
        "beta": 0.0,
        "loss_type": "dapo",
        "scale_rewards": "group",
        "num_iterations": 1,
        "mask_truncated_completions": False,
        "optimizer": "adamw_torch",
        "lr_scheduler_type": "constant",
        "warmup_steps": 0,
        "weight_decay": 0.0,
        "max_grad_norm": 1.0,
        "save_steps": 64,
        "save_total_limit": 4,
        "logging_steps": 1,
        "seed": 42,
    }

    require(h == expected_h, "Unexpected training hyperparameters")

    e = plan["execution"]

    expected_e = {
        "precision": "fp16",
        "attention": "eager",
        "native_eos_pad_id": 151643,
        "disable_native_triton_overrides": True,
        "training_use_cache": False,
        "generation_use_cache": True,
        "use_vllm": False,
        "gradient_checkpointing": True,
        "gradient_checkpointing_use_reentrant": False,
        "official_test_access": False,
    }

    require(e == expected_e, "Unexpected execution settings")

    require(
        h["generation_batch_size"] % h["num_generations"] == 0,
        "Incomplete generation groups",
    )

    require(
        h["generation_batch_size"]
        == h["per_device_train_batch_size"]
        * h["gradient_accumulation_steps"],
        "Generation/accumulation mismatch",
    )

    required_fields = {
        "num_generations",
        "generation_batch_size",
        "max_completion_length",
        "generation_kwargs",
        "mask_truncated_completions",
        "loss_type",
        "num_iterations",
    }

    require(
        required_fields.issubset(GRPOConfig.__dataclass_fields__),
        "Required TRL fields unavailable",
    )

    sample_rewards = gsm8k_exact_numeric_reward(
        completions=[
            "The answer is 85.",
            "The answer is 55.",
            "The answer is 85.",
            "No final answer.",
        ],
        answer=["#### 85"] * 4,
    )

    require(
        sample_rewards == [1.0, 0.0, 1.0, 0.0],
        "Frozen reward smoke test failed",
    )

    print("Input dataset SHA256:", dataset_info["sha256"])
    print("Input rows:", len(rows))
    print("Maximum prompt tokens:", max_tokens)
    print("Reward smoke test: PASSED")
    print("TRL configuration fields: VERIFIED")
    print("Proposed optimizer steps:", h["max_steps"])
    print("Proposed learning rate:", h["learning_rate"])
    print("Training authorization:", plan["training_approved"])

    return plan, rows, tokenizer


def build_config(plan):
    """Construct the GPU training configuration after authorization."""
    from trl import GRPOConfig

    h = plan["hyperparameters"]

    config = GRPOConfig(
        output_dir=plan["output_dir"],

        max_steps=h["max_steps"],
        learning_rate=h["learning_rate"],

        num_generations=h["num_generations"],
        per_device_train_batch_size=h["per_device_train_batch_size"],
        gradient_accumulation_steps=h["gradient_accumulation_steps"],
        generation_batch_size=h["generation_batch_size"],

        max_prompt_length=None,
        max_completion_length=h["max_completion_length"],

        temperature=h["temperature"],
        top_p=h["top_p"],
        beta=h["beta"],
        loss_type=h["loss_type"],
        scale_rewards=h["scale_rewards"],
        num_iterations=h["num_iterations"],
        mask_truncated_completions=h["mask_truncated_completions"],

        optim=h["optimizer"],
        lr_scheduler_type=h["lr_scheduler_type"],
        warmup_steps=h["warmup_steps"],
        weight_decay=h["weight_decay"],
        max_grad_norm=h["max_grad_norm"],

        save_strategy="steps",
        save_steps=h["save_steps"],
        save_total_limit=h["save_total_limit"],

        logging_strategy="steps",
        logging_steps=h["logging_steps"],

        seed=h["seed"],
        data_seed=h["seed"],

        fp16=True,
        bf16=False,

        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={
            "use_reentrant": False,
        },

        generation_kwargs={
            "use_cache": True,
        },

        use_vllm=False,
        remove_unused_columns=False,

        dataloader_num_workers=0,
        dataloader_pin_memory=False,

        report_to="none",
        eval_strategy="no",
    )

    require(config.num_generations == 4, "Wrong group size")
    require(config.generation_batch_size == 4, "Wrong batch")
    require(config.steps_per_generation == 4, "Wrong generation interval")
    require(config.beta == 0.0, "Wrong reference setting")

    return config


def run_training(plan, rows, tokenizer):
    """Locked training path. Never called by check mode."""
    import torch
    from datasets import Dataset
    from peft import PeftModel
    from peft.utils.save_and_load import get_peft_model_state_dict
    from safetensors.torch import load_file
    from transformers import AutoModelForCausalLM
    from trl import GRPOTrainer

    from llm_post_training.training.grpo_reward import (
        gsm8k_exact_numeric_reward,
    )

    # Previously validated on the V100.
    torch.backends.python_native.triton.enabled = False

    require(
        torch.backends.python_native.triton.enabled is False,
        "Native Triton overrides must be disabled",
    )

    require(torch.cuda.is_available(), "CUDA unavailable")
    require(torch.cuda.device_count() == 1, "Expected one GPU")

    # Fresh run directory: never silently resume or overwrite.
    run_dir = Path(plan["output_dir"])

    require(not run_dir.exists(), "Run directory already exists")
    require(run_dir.parent.is_dir(), "Missing run parent directory")

    # Build GRPOConfig before creating output files.
    config = build_config(plan)

    tokenizer.padding_side = "left"

    base = AutoModelForCausalLM.from_pretrained(
        plan["base_model"],
        revision=plan["base_revision"],
        local_files_only=True,
        use_safetensors=True,
        dtype=torch.float16,
        attn_implementation="eager",
    ).to("cuda")

    require(base.config.eos_token_id == 151643, "Base EOS mismatch")

    base.config.use_cache = False

    adapter_dir = Path(plan["initial_adapter"]["path"])

    model = PeftModel.from_pretrained(
        base,
        str(adapter_dir),
        adapter_name="policy",
        is_trainable=True,
        autocast_adapter_dtype=True,
    )

    require(model.active_adapter == "policy", "Wrong adapter")

    frozen = load_file(
        str(adapter_dir / "adapter_model.safetensors"),
        device="cpu",
    )

    live = get_peft_model_state_dict(
        model,
        adapter_name="policy",
    )

    require(
        len(frozen) == len(live) == 224,
        "Initial LoRA tensor count mismatch",
    )

    require(set(frozen) == set(live), "Initial LoRA keys changed")

    for key in frozen:
        require(
            torch.equal(frozen[key], live[key].detach().cpu()),
            f"Initial LoRA tensor mismatch: {key}",
        )

    trainable = [
        name
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    ]

    require(len(trainable) == 224, "Wrong trainable tensor count")
    require(
        all("lora_" in name for name in trainable),
        "Unexpected trainable base-model weights",
    )

    print("Initial E002a LoRA weights: 224/224 VERIFIED", flush=True)

    # Create the output directory only after checks succeed.
    run_dir.mkdir(parents=False, exist_ok=False)

    trace_path = run_dir / "rollouts.jsonl"
    trace_path.touch(exist_ok=False)

    def traced_reward(
        *,
        completions,
        answer,
        source_index,
        **kwargs,
    ):
        rewards = gsm8k_exact_numeric_reward(
            completions=completions,
            answer=answer,
            **kwargs,
        )

        require(
            len(completions) == len(source_index) == len(rewards),
            "Reward-trace alignment failure",
        )

        with trace_path.open("a", encoding="utf-8") as output:
            for idx, completion, reward in zip(
                source_index,
                completions,
                rewards,
                strict=True,
            ):
                record = {
                    "source_index": int(idx),
                    "completion": completion,
                    "reward": float(reward),
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

        return rewards

    trainer = GRPOTrainer(
        model=model,
        reward_funcs=traced_reward,
        args=config,
        train_dataset=Dataset.from_list(rows),
        processing_class=tokenizer,
        peft_config=None,
    )

    require(trainer.optimizer is None, "Unexpected optimizer")
    require(trainer.state.global_step == 0, "Unexpected prior steps")
    require(trainer.ref_model is None, "Unexpected reference model")

    # Capture source and approved-plan identities before optimization.
    provenance = {
        "experiment": "E005",
        "source_git_commit": git("rev-parse", "HEAD"),
        "training_plan_sha256": digest(PLAN_PATH),
        "dataset_sha256": plan["dataset"]["sha256"],
        "initial_adapter_sha256": plan["initial_adapter"]["sha256"],
        "reward_sha256": plan["reward"]["sha256"],
        "base_revision": plan["base_revision"],
        "max_steps": config.max_steps,
        "seed": config.seed,
    }

    (run_dir / "run_provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )

    print("AUTHORIZED E005 TRAINING START", flush=True)

    result = trainer.train()

    require(
        trainer.state.global_step == config.max_steps,
        "Training ended before expected optimizer-step budget",
    )

    final_dir = run_dir / "final_policy_adapter"

    require(not final_dir.exists(), "Final adapter path exists")

    trainer.save_model(str(final_dir))
    trainer.save_state()

    final_weights = final_dir / "policy" / "adapter_model.safetensors"

    require(final_weights.is_file(), "Final adapter missing")

    summary = {
        **provenance,
        "completed_steps": trainer.state.global_step,
        "train_loss": result.training_loss,
        "train_metrics": result.metrics,
        "final_adapter_sha256": digest(final_weights),
        "rollouts_sha256": digest(trace_path),
    }

    summary_path = run_dir / "e005_training_summary.json"

    require(not summary_path.exists(), "Summary already exists")

    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )

    print("Completed optimizer steps:", trainer.state.global_step)
    print("Final adapter SHA256:", digest(final_weights))
    print("Training summary:", summary_path)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["check", "train"],
        default="check",
    )

    args = parser.parse_args()

    print("=== E005 GRPO TRAINER ===")
    print("Mode:", args.mode)

    plan, rows, tokenizer = validate_plan()

    if args.mode == "check":
        print("GPU model loading: NONE")
        print("Generation: NONE")
        print("Optimizer creation: NONE")
        print("Training: NONE")
        print("E005 TRAINER CHECK: PASSED")
        return

    # Explicit authorization barrier.
    # The current committed proposal always fails this check.
    require(
        plan["training_approved"] is True
        and plan["status"] == "AUTHORIZED",
        "TRAINING NOT AUTHORIZED: "
        "the E005 plan requires a separately approved revision",
    )

    require(
        not git("status", "--porcelain", "--untracked-files=all"),
        "Git worktree must be clean before training",
    )

    run_training(plan, rows, tokenizer)


if __name__ == "__main__":
    main()
