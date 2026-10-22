"""Run a pretrained Qwen3 evaluation on frozen GSM8K validation data."""

import argparse
import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import torch
import torch.backends.python_native as python_native
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.data.loader import load_gsm8k_split
from llm_post_training.evaluation.answer_extraction import (
    ANSWER_EXTRACTION_VERSION,
)
from llm_post_training.evaluation.metrics import (
    evaluate_response,
    summarize_evaluations,
)
from llm_post_training.evaluation.prompting import (
    BASELINE_PROMPT_VERSION,
    format_baseline_prompt,
)


MODEL_ID = "Qwen/Qwen3-0.6B-Base"
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"

MANIFEST_SHA256 = (
    "31030317d85b015263d05383bf69bb02"
    "daec5bc67874f5ad0e0b33fa5294c719"
)

SOURCE = Path("data/raw/gsm8k/train.jsonl")
MANIFEST = Path("configs/data/gsm8k_split_v1.json")

DEVICE = "cuda:0"
DEFAULT_MAX_NEW_TOKENS = 192
STOP_STRINGS = ["\nQuestion:", "\n[Question]"]



E002_CONFIG_SHA256 = (
    "43c002773e83228d2ae86854927c6fe679ec6a0ac054cbeb251f0415604b7fe9"
)
E002_TRAINING_REVISION = (
    "f293df899a9c073615d0bae9e5feee5e64bcf1bc"
)


def validate_adapter_evaluation_request(
    *,
    run_type,
    adapter_dir,
    expected_adapter_sha256,
    source_index,
    limit,
    validation_size,
    code_revision,
    max_new_tokens,
):
    """Enforce the frozen full-validation comparison protocol."""

    if (adapter_dir is None) != (expected_adapter_sha256 is None):
        raise ValueError(
            "Adapter path and expected SHA-256 must be provided together"
        )

    if expected_adapter_sha256 is not None:
        if re.fullmatch(
            r"[0-9a-f]{64}",
            expected_adapter_sha256,
        ) is None:
            raise ValueError("Invalid adapter SHA-256")

    if run_type == "development_baseline" and adapter_dir is not None:
        raise ValueError(
            "Pretrained baseline cannot load a LoRA adapter"
        )

    if run_type == "development_sft" and adapter_dir is None:
        raise ValueError(
            "E002 evaluation requires a LoRA adapter"
        )

    if run_type in ("development_baseline", "development_sft"):
        if source_index is not None or limit != validation_size:
            raise ValueError(
                "Development evaluation requires the full validation split"
            )

        if max_new_tokens != 512:
            raise ValueError(
                "Development evaluation requires max_new_tokens=512"
            )

        if code_revision is None or re.fullmatch(
            r"[0-9a-f]{40}",
            code_revision,
        ) is None:
            raise ValueError(
                "Development evaluation requires a 40-character Git SHA"
            )


def verify_adapter_checkpoint(
    adapter_dir,
    expected_sha256,
    *,
    require_completed_e002,
):
    """Verify the exact LoRA checkpoint before loading the model."""

    adapter_dir = Path(adapter_dir)

    weights_path = adapter_dir / "adapter_model.safetensors"
    config_path = adapter_dir / "adapter_config.json"

    if not weights_path.is_file() or not config_path.is_file():
        raise ValueError("Incomplete LoRA adapter checkpoint")

    digest = hashlib.sha256()

    with weights_path.open("rb") as source:
        for chunk in iter(
            lambda: source.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    actual_sha256 = digest.hexdigest()

    if actual_sha256 != expected_sha256:
        raise ValueError("Adapter SHA-256 mismatch")

    adapter_config = json.loads(
        config_path.read_text(encoding="utf-8")
    )

    if adapter_config.get("base_model_name_or_path") != MODEL_ID:
        raise ValueError("Unexpected adapter base model")

    if (
        adapter_config.get("r") != 8
        or adapter_config.get("lora_alpha") != 16
        or set(adapter_config.get("target_modules", []))
        != {"q_proj", "k_proj", "v_proj", "o_proj"}
    ):
        raise ValueError("Unexpected E002 LoRA configuration")

    provenance = {
        "adapter_sha256": actual_sha256,
        "adapter_dir": str(adapter_dir),
    }

    if require_completed_e002:
        manifest_path = adapter_dir.parent / "manifest.json"

        if not manifest_path.is_file():
            raise ValueError("Completed E002 manifest is missing")

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        if (
            manifest.get("completed_optimizer_steps") != 422
            or manifest.get("next_epoch") != 2
            or manifest.get("config_sha256") != E002_CONFIG_SHA256
            or manifest.get("code_revision") != E002_TRAINING_REVISION
            or manifest.get("model_revision") != MODEL_REVISION
        ):
            raise ValueError(
                "Checkpoint is not the completed, pinned E002 run"
            )

        if manifest.get("checksums", {}).get(
            "adapter/adapter_model.safetensors"
        ) != actual_sha256:
            raise ValueError(
                "Adapter checksum differs from training manifest"
            )

        provenance["training_manifest"] = {
            "completed_optimizer_steps": 422,
            "config_sha256": E002_CONFIG_SHA256,
            "code_revision": E002_TRAINING_REVISION,
            "model_revision": MODEL_REVISION,
        }

    return provenance



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--run-type",
        choices=("engineering_smoke_test", "development_baseline", "development_sft"),
        default="engineering_smoke_test",
    )
    parser.add_argument("--code-revision", default=None)
    parser.add_argument(
        "--source-index",
        type=int,
        default=None,
        help="Evaluate one example by its original GSM8K index",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=DEFAULT_MAX_NEW_TOKENS,
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--adapter-dir", type=Path)
    parser.add_argument("--expected-adapter-sha256")
    args = parser.parse_args()

    if args.limit < 1:
        raise ValueError("--limit must be positive")

    if args.max_new_tokens < 1:
        raise ValueError("--max-new-tokens must be positive")

    if args.output_dir.exists():
        raise FileExistsError(
            f"Output directory already exists: {args.output_dir}"
        )

    assert torch.cuda.is_available(), "CUDA is required"

    actual_hash = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()

    if actual_hash != MANIFEST_SHA256:
        raise ValueError("Frozen split manifest checksum mismatch")

    validation = load_gsm8k_split(
        SOURCE,
        MANIFEST,
        "validation",
    )

    if args.source_index is None:
        examples = validation[:args.limit]
    else:
        examples = [
            example
            for example in validation
            if example.source_index == args.source_index
        ]

        if len(examples) != 1:
            raise ValueError(
                f"Source index {args.source_index} "
                "not found in validation split"
            )

    validate_adapter_evaluation_request(
        run_type=args.run_type,
        adapter_dir=args.adapter_dir,
        expected_adapter_sha256=args.expected_adapter_sha256,
        source_index=args.source_index,
        limit=args.limit,
        validation_size=len(validation),
        code_revision=args.code_revision,
        max_new_tokens=args.max_new_tokens,
    )

    adapter_provenance = None

    if args.adapter_dir is not None:
        adapter_provenance = verify_adapter_checkpoint(
            args.adapter_dir,
            args.expected_adapter_sha256,
            require_completed_e002=(
                args.run_type == "development_sft"
            ),
        )

    if args.run_type == "development_baseline":
        if args.source_index is not None or args.limit != len(validation):
            raise ValueError(
                "Development baseline requires the full validation split"
            )
        if not args.code_revision or not re.fullmatch(
            r"[0-9a-f]{40}", args.code_revision
        ):
            raise ValueError(
                "Development baseline requires a 40-character Git SHA"
            )

    print("Validation examples selected:", len(examples))
    print("Prompt version:", BASELINE_PROMPT_VERSION)

    # Avoid native Triton operator overrides on the V100.
    python_native.triton.enabled = False

    print("Loading tokenizer...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
    )

    print("Loading model...")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        dtype=torch.float16,
        attn_implementation="eager",
        use_safetensors=True,
    ).to(DEVICE)

    if args.adapter_dir is not None:
        print("Loading verified LoRA adapter...")

        model = PeftModel.from_pretrained(
            model,
            str(args.adapter_dir),
            is_trainable=False,
            autocast_adapter_dtype=True,
        )

        if len(model.peft_config) != 1:
            raise ValueError("Expected exactly one active LoRA adapter")

    model.config.use_cache = False
    model.eval()
    torch.cuda.reset_peak_memory_stats()

    args.output_dir.mkdir(parents=True, exist_ok=False)

    records = []
    predictions_path = args.output_dir / "predictions.jsonl"

    with predictions_path.open("w", encoding="utf-8") as output:
        for position, example in enumerate(examples, start=1):
            prompt = format_baseline_prompt(example.question)

            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                add_special_tokens=False,
            ).to(DEVICE)

            input_tokens = inputs["input_ids"].shape[1]

            torch.cuda.synchronize()
            started = perf_counter()

            with torch.inference_mode():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    use_cache=False,
                    stop_strings=STOP_STRINGS,
                    tokenizer=tokenizer,
                    pad_token_id=tokenizer.eos_token_id,
                )

            torch.cuda.synchronize()
            elapsed_seconds = perf_counter() - started

            new_token_ids = generated_ids[0, input_tokens:]

            reached_token_cap = (
                len(new_token_ids) == args.max_new_tokens
            )

            response = tokenizer.decode(
                new_token_ids,
                skip_special_tokens=True,
            )

            record = evaluate_response(
                response=response,
                expected_answer=example.reference_answer,
                generated_tokens=len(new_token_ids),
                reached_token_cap=reached_token_cap,
            )

            records.append(record)

            result = {
                "source_index": example.source_index,
                "answer_extraction_version": ANSWER_EXTRACTION_VERSION,
                "question": example.question,
                "prompt": prompt,
                "reference_answer": str(example.reference_answer),
                "raw_response": response,
                "extracted_answer": (
                    str(record.extraction.answer)
                    if record.extraction.answer is not None
                    else None
                ),
                "extraction_status": record.extraction.status,
                "correct": record.correct,
                "unwanted_continuation": (
                    record.extraction.unwanted_continuation
                ),
                "input_tokens": input_tokens,
                "generated_tokens": len(new_token_ids),
                "reached_token_cap": reached_token_cap,
                "generation_seconds": elapsed_seconds,
            }

            output.write(json.dumps(result, ensure_ascii=False) + "\n")
            output.flush()

            print(
                f"[{position}/{len(examples)}] "
                f"index={example.source_index} "
                f"correct={record.correct} "
                f"status={record.extraction.status} "
                f"tokens={len(new_token_ids)} "
                f"cap={reached_token_cap}",
                flush=True,
            )

    summary = summarize_evaluations(records)

    report = {
        "run_type": args.run_type,
        "code_revision": args.code_revision,
        "model": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "model_variant": (
            "sft_lora" if args.adapter_dir is not None
            else "pretrained"
        ),
        "adapter_provenance": adapter_provenance,
        "dataset_split": "development_validation",
        "selected_source_indices": [
            example.source_index for example in examples
        ],
        "manifest_sha256": MANIFEST_SHA256,
        "prompt_version": BASELINE_PROMPT_VERSION,
        "answer_extraction_version": ANSWER_EXTRACTION_VERSION,
        "precision": "float16",
        "attention_implementation": "eager",
        "decoding": "greedy",
        "kv_cache": False,
        "max_new_tokens": args.max_new_tokens,
        "stop_strings": STOP_STRINGS,
        "metrics": asdict(summary),
        "peak_allocated_vram_mib": (
            torch.cuda.max_memory_allocated() / 1024**2
        ),
    }

    summary_path = args.output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\n=== SMOKE TEST SUMMARY ===")
    print("Problems evaluated:", summary.total)
    print("Correct answers:", summary.correct)
    print(f"Accuracy: {summary.accuracy:.1%}")
    print(f"Extraction rate: {summary.extraction_rate:.1%}")
    print(f"Mean generated tokens: {summary.mean_generated_tokens:.1f}")
    print(
        "Responses reaching token cap:",
        summary.reached_token_cap_count,
    )
    print("Predictions:", predictions_path)
    print("Summary:", summary_path)
    print("\nEvaluation smoke test: PASSED")


if __name__ == "__main__":
    main()
