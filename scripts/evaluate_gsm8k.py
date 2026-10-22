"""Run a pretrained Qwen3 evaluation on frozen GSM8K validation data."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import torch
import torch.backends.python_native as python_native
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.data.loader import load_gsm8k_split
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=DEFAULT_MAX_NEW_TOKENS,
    )
    parser.add_argument("--output-dir", type=Path, required=True)
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

    examples = validation[:args.limit]

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
        "run_type": "engineering_smoke_test",
        "model": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "dataset_split": "development_validation",
        "manifest_sha256": MANIFEST_SHA256,
        "prompt_version": BASELINE_PROMPT_VERSION,
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
