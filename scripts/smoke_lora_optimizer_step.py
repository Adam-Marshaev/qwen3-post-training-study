"""Verify one real LoRA optimizer update on the pinned Qwen3 model."""

import math
import re

from pathlib import Path

import torch

from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.training.sft_collator import (
    SFTBatchCollator,
)
from llm_post_training.training.sft_data import (
    load_sft_training_examples,
)
from llm_post_training.training.sft_tokenization import (
    tokenize_sft_example,
)


MODEL_ID = "Qwen/Qwen3-0.6B-Base"
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"

TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]

LEARNING_RATE = 1e-4
MAX_GRAD_NORM = 1.0


def audit_gradients(trainable, stage):
    """Inspect gradient presence, finiteness, and magnitude."""

    nonzero_a = 0
    nonzero_b = 0
    layer_squared_norms = {}

    for name, parameter in trainable:
        gradient = parameter.grad

        assert gradient is not None, (
            f"Missing gradient: {name}"
        )

        assert gradient.dtype == torch.float32, (
            f"Unexpected gradient dtype: {name}"
        )

        assert torch.isfinite(gradient).all().item(), (
            f"Nonfinite gradient: {name}"
        )

        nonzero = bool(
            torch.count_nonzero(gradient).item()
        )

        if ".lora_A." in name and nonzero:
            nonzero_a += 1

        if ".lora_B." in name and nonzero:
            nonzero_b += 1

        match = re.search(r"\.layers\.(\d+)\.", name)

        assert match is not None, name

        layer_index = int(match.group(1))

        norm = gradient.detach().float().norm().item()

        layer_squared_norms[layer_index] = (
            layer_squared_norms.get(layer_index, 0.0)
            + norm**2
        )

    layer_norms = {
        index: math.sqrt(squared_norm)
        for index, squared_norm in layer_squared_norms.items()
    }

    assert len(layer_norms) == 28

    global_norm = math.sqrt(
        sum(layer_squared_norms.values())
    )

    print(f"\n=== {stage} ===")

    print("LoRA A tensors with nonzero gradients:", nonzero_a)
    print("LoRA B tensors with nonzero gradients:", nonzero_b)

    print("Global gradient norm:", f"{global_norm:.8f}")

    print(
        "Minimum layer gradient norm:",
        f"{min(layer_norms.values()):.8f}",
    )

    print(
        "Maximum layer gradient norm:",
        f"{max(layer_norms.values()):.8f}",
    )

    for index in (0, 13, 27):
        print(
            f"Layer {index:2d} gradient norm:",
            f"{layer_norms[index]:.8f}",
        )

    return {
        "nonzero_a": nonzero_a,
        "nonzero_b": nonzero_b,
        "global_norm": global_norm,
    }


def main():
    print("=== ENVIRONMENT ===", flush=True)

    assert torch.cuda.is_available()
    assert torch.cuda.get_device_capability(0) == (7, 0)

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    # Established V100-compatible attention workaround.
    torch.backends.python_native.triton.enabled = False

    print("GPU:", torch.cuda.get_device_name(0))
    print("Learning rate:", LEARNING_RATE)
    print("Gradient clipping threshold:", MAX_GRAD_NORM)

    print("\n=== PREPARING TRAINING BATCH ===", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=True,
    )

    assert tokenizer.eos_token_id == 151645
    assert tokenizer.pad_token_id == 151643

    examples = load_sft_training_examples(
        Path("data/raw/gsm8k/train.jsonl"),
        Path("configs/data/gsm8k_split_v1.json"),
    )

    assert len(examples) == 6726

    selected = [
        tokenize_sft_example(example, tokenizer)
        for example in examples[:2]
    ]

    collator = SFTBatchCollator(
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        max_seq_length=512,
    )

    batch = {
        name: tensor.to("cuda")
        for name, tensor in collator(selected).items()
    }

    print(
        "Source indices:",
        [item.source_index for item in selected],
    )

    print("Batch shape:", tuple(batch["input_ids"].shape))

    assert tuple(batch["input_ids"].shape) == (2, 87)

    print("\n=== LOADING QWEN3 + LORA ===", flush=True)

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=True,
        dtype=torch.float16,
        attn_implementation="eager",
    )

    base_model.config.use_cache = False

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        target_modules=TARGET_MODULES,
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(
        base_model,
        lora_config,
        autocast_adapter_dtype=True,
    )

    model = model.to("cuda")
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

    trainable_parameters = [
        parameter
        for _, parameter in trainable
    ]

    assert len(trainable) == 224

    assert sum(
        parameter.numel()
        for parameter in trainable_parameters
    ) == 2_293_760

    assert all(
        parameter.dtype == torch.float32
        for parameter in trainable_parameters
    )

    assert all(
        parameter.dtype == torch.float16
        for _, parameter in frozen
    )

    print("Trainable LoRA tensors:", len(trainable))
    print("Frozen parameter tensors:", len(frozen))

    # Keep snapshots of all LoRA tensors.
    # This is small: approximately 9 MiB of FP32 weights.
    with torch.no_grad():
        original_adapters = {
            name: parameter.detach().clone()
            for name, parameter in trainable
        }

    # Save one representative frozen projection for an
    # explicit bit-for-bit comparison after optimization.
    frozen_probes = [
        (name, parameter)
        for name, parameter in frozen
        if name.endswith(
            "layers.0.self_attn.q_proj.base_layer.weight"
        )
    ]

    assert len(frozen_probes) == 1

    frozen_name, frozen_parameter = frozen_probes[0]

    frozen_before = frozen_parameter.detach().clone()

    optimizer = torch.optim.AdamW(
        trainable_parameters,
        lr=LEARNING_RATE,
        weight_decay=0.0,
    )

    torch.cuda.reset_peak_memory_stats()

    print("\n=== FIRST FORWARD PASS ===", flush=True)

    optimizer.zero_grad(set_to_none=True)

    loss_before = model(**batch).loss

    print("Initial loss:", loss_before.detach().item())

    assert torch.isfinite(loss_before).item()

    print("\n=== FIRST BACKWARD PASS ===", flush=True)

    loss_before.backward()

    initial_stats = audit_gradients(
        trainable,
        "INITIAL GRADIENT AUDIT",
    )

    assert initial_stats["nonzero_b"] == 112

    # Standard zero-initialized LoRA B matrices imply that
    # LoRA A receives zero gradients on the first backward.
    assert initial_stats["nonzero_a"] == 0

    assert initial_stats["global_norm"] > 0.0

    assert all(
        parameter.grad is None
        for _, parameter in frozen
    )

    print("\n=== GRADIENT CLIPPING ===")

    # This returns the norm BEFORE clipping.
    norm_before_clipping = torch.nn.utils.clip_grad_norm_(
        trainable_parameters,
        max_norm=MAX_GRAD_NORM,
        error_if_nonfinite=True,
    )

    norm_before_clipping = norm_before_clipping.item()

    norm_after_clipping = math.sqrt(
        sum(
            parameter.grad.detach().float().norm().item() ** 2
            for parameter in trainable_parameters
        )
    )

    print(
        "Norm before clipping:",
        f"{norm_before_clipping:.8f}",
    )

    print(
        "Norm after clipping:",
        f"{norm_after_clipping:.8f}",
    )

    assert math.isfinite(norm_before_clipping)
    assert math.isfinite(norm_after_clipping)

    assert norm_after_clipping <= MAX_GRAD_NORM + 1e-4

    print("Gradient clipping: PASSED")

    print("\n=== FIRST OPTIMIZER STEP ===", flush=True)

    optimizer.step()

    changed_a = 0
    changed_b = 0

    for name, parameter in trainable:
        assert torch.isfinite(parameter).all().item(), name

        changed = not torch.equal(
            parameter.detach(),
            original_adapters[name],
        )

        if ".lora_A." in name and changed:
            changed_a += 1

        if ".lora_B." in name and changed:
            changed_b += 1

    print("LoRA A tensors changed:", changed_a)
    print("LoRA B tensors changed:", changed_b)

    assert changed_b > 0

    assert torch.equal(
        frozen_parameter.detach(),
        frozen_before,
    ), frozen_name

    assert all(
        parameter.grad is None
        for _, parameter in frozen
    )

    print("LoRA parameter update: PASSED")
    print("Frozen parameter integrity: PASSED")

    print("\n=== SECOND FORWARD/BACKWARD ===", flush=True)

    optimizer.zero_grad(set_to_none=True)

    loss_after = model(**batch).loss

    print("Post-update loss:", loss_after.detach().item())

    assert torch.isfinite(loss_after).item()

    loss_after.backward()

    updated_stats = audit_gradients(
        trainable,
        "POST-UPDATE GRADIENT AUDIT",
    )

    # After B changes, A can now receive gradient signals.
    assert updated_stats["nonzero_a"] > 0
    assert updated_stats["nonzero_b"] > 0

    assert all(
        parameter.grad is None
        for _, parameter in frozen
    )

    print("\n=== GPU MEMORY ===")

    torch.cuda.synchronize()

    print(
        "Peak allocated VRAM (MiB):",
        round(
            torch.cuda.max_memory_allocated() / 1024**2,
            2,
        ),
    )

    print(
        "Peak reserved VRAM (MiB):",
        round(
            torch.cuda.max_memory_reserved() / 1024**2,
            2,
        ),
    )

    print("\nOptimizer updates performed: 1")
    print("Checkpoint written: No")

    print("\nLoRA optimizer-step smoke test: PASSED")


if __name__ == "__main__":
    main()
