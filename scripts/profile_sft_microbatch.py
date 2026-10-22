"""Profile LoRA training memory using the longest GSM8K examples."""

from pathlib import Path

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.training.sft_collator import SFTBatchCollator
from llm_post_training.training.sft_data import load_sft_training_examples
from llm_post_training.training.sft_tokenization import tokenize_sft_example


MODEL_ID = "Qwen/Qwen3-0.6B-Base"
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"

# Longest approved training examples, measured in M2.4.
SOURCE_INDICES = (3331, 7364, 310, 6274)
EXPECTED_LENGTHS = (449, 445, 431, 413)

MICROBATCH_SIZES = (2, 4)
MAX_SEQUENCE_LENGTH = 512
LEARNING_RATE = 1e-4
MAX_GRAD_NORM = 1.0


def gib(number_of_bytes):
    return number_of_bytes / (1024 ** 3)


def main():
    print("=== ENVIRONMENT ===", flush=True)

    assert torch.cuda.is_available()
    assert torch.cuda.get_device_capability(0) == (7, 0)

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)

    # Same V100 compatibility workaround as E001.
    torch.backends.python_native.triton.enabled = False

    print("GPU:", torch.cuda.get_device_name(0))
    print("Maximum training length:", MAX_SEQUENCE_LENGTH)
    print("Microbatch sizes:", MICROBATCH_SIZES)

    print("\n=== LOADING TRAINING DATA ===", flush=True)

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

    by_index = {
        example.source_index: example
        for example in examples
    }

    selected = [
        tokenize_sft_example(by_index[index], tokenizer)
        for index in SOURCE_INDICES
    ]

    observed_lengths = tuple(
        example.sequence_length
        for example in selected
    )

    assert observed_lengths == EXPECTED_LENGTHS

    print("Source indices:", SOURCE_INDICES)
    print("Sequence lengths:", observed_lengths)

    collator = SFTBatchCollator(
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        max_seq_length=MAX_SEQUENCE_LENGTH,
    )

    print("\n=== LOADING MODEL ===", flush=True)

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
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
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

    parameters = [parameter for _, parameter in trainable]

    assert len(trainable) == 224

    assert sum(
        parameter.numel() for parameter in parameters
    ) == 2_293_760

    assert all(
        parameter.dtype == torch.float32
        for parameter in parameters
    )

    assert all(
        parameter.dtype == torch.float16
        for _, parameter in frozen
    )

    # Compare one frozen projection bit-for-bit after both updates.
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

    # Track an actual trainable LoRA B matrix.
    b_probes = [
        (name, parameter)
        for name, parameter in trainable
        if name.endswith(
            "layers.0.self_attn.q_proj.lora_B.default.weight"
        )
    ]

    assert len(b_probes) == 1

    b_name, b_parameter = b_probes[0]

    optimizer = torch.optim.AdamW(
        parameters,
        lr=LEARNING_RATE,
        weight_decay=0.0,
    )

    print("Trainable LoRA parameters: 2,293,760")

    print("\n=== MICROBATCH MEMORY PROFILE ===", flush=True)

    for batch_size in MICROBATCH_SIZES:
        optimizer.zero_grad(set_to_none=True)

        batch = collator(selected[:batch_size])

        batch = {
            name: tensor.to("cuda")
            for name, tensor in batch.items()
        }

        padded_length = batch["input_ids"].shape[1]

        assert padded_length <= MAX_SEQUENCE_LENGTH

        supervised_tokens = int(
            (batch["labels"] != -100).sum().item()
        )

        b_before = b_parameter.detach().clone()

        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

        print(
            f"\n--- Microbatch {batch_size} ---",
            flush=True,
        )

        print(
            "Batch shape:",
            tuple(batch["input_ids"].shape),
            flush=True,
        )

        print(
            "Supervised tokens:",
            supervised_tokens,
            flush=True,
        )

        loss = model(**batch).loss

        assert torch.isfinite(loss).item()

        loss_value = loss.detach().item()

        loss.backward()

        # clip_grad_norm_ returns the norm BEFORE clipping.
        gradient_norm = torch.nn.utils.clip_grad_norm_(
            parameters,
            max_norm=MAX_GRAD_NORM,
            error_if_nonfinite=True,
        )

        assert torch.isfinite(gradient_norm).item()
        assert gradient_norm.item() > 0.0

        assert all(
            parameter.grad is not None
            for parameter in parameters
        )

        assert all(
            parameter.grad is None
            for _, parameter in frozen
        )

        optimizer.step()
        torch.cuda.synchronize()

        assert not torch.equal(
            b_parameter.detach(),
            b_before,
        ), b_name

        assert torch.equal(
            frozen_parameter.detach(),
            frozen_before,
        ), frozen_name

        assert all(
            torch.isfinite(parameter).all().item()
            for parameter in parameters
        )

        peak_allocated = gib(
            torch.cuda.max_memory_allocated()
        )

        peak_reserved = gib(
            torch.cuda.max_memory_reserved()
        )

        print("Loss:", f"{loss_value:.6f}")
        print(
            "Gradient norm before clipping:",
            f"{gradient_norm.item():.6f}",
        )
        print(
            "Peak allocated VRAM (GiB):",
            f"{peak_allocated:.3f}",
        )
        print(
            "Peak reserved VRAM (GiB):",
            f"{peak_reserved:.3f}",
        )
        print("LoRA update: PASSED")
        print("Frozen weight check: PASSED")

        # Release this batch's graph and gradients before
        # profiling the next batch size.
        optimizer.zero_grad(set_to_none=True)
        del loss, batch, b_before

        torch.cuda.empty_cache()

    print("\n=== FINAL RESULT ===")
    print("Microbatch sizes verified:", MICROBATCH_SIZES)
    print("Optimizer updates performed:", len(MICROBATCH_SIZES))
    print("Checkpoint written: No")
    print("All batches used the frozen training partition.")

    print("\nSFT microbatch memory profiling: PASSED")


if __name__ == "__main__":
    main()
