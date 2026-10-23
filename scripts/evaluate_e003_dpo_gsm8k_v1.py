"""Evaluate E003 DPO on frozen GSM8K validation using the E002a protocol.

Derived from scripts/evaluate_gsm8k.py. The baseline/SFT paths are retained,
with a strict E003-specific completed-checkpoint verification path.
No training, no changed split, no changed decoding or answer extraction.
"""

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
E002A_CONFIG_SHA256 = (
    "11c9977d2edc288129a2fafdf6331e473fab79beee88d6fc32cb0e4b7cedae52"
)
E002A_TRAINING_REVISION = (
    "31b73e9ac15572b44ee479ce047048d6404bb72f"
)
NATIVE_EOS_TOKEN_ID = 151643
INFERENCE_PROTOCOL_VERSION = "gsm8k_val512_greedy_eager_cached_v1"

# E003: pinned artifact identities; the new evaluator never treats E003 as SFT.
E003_TRAINING_REVISION = "f16e90360690df121132bc6055282f27302a132a"
E003_TRAINER_SCRIPT_SHA256 = (
    "0a4babc9f82fd55a470cdffabaed0df954b3bc40c2b73fae05c02ef5818cd26d"
)
E003_SOURCE_PAIRS_SHA256 = (
    "7d088bd70dc1d3d8b05f251a5560b37aca24a064ec7c4c81c91a03b8d84dc8e9"
)
E003_SOURCE_E002A_SHA256 = (
    "f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625"
)
E003_SOURCE_ADAPTER = Path(
    "data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter"
)
E003_RUN_DIR = Path("data/train_runs/e003_dpo_signed109_f16e903_v1")
E003_ADAPTER_DIR = E003_RUN_DIR / "final_policy_adapter/policy"
E003_PAIRS_PATH = Path(
    "data/preference_runs/e003_dpo_signed109_staged_277c863_v1/pairs_staged.jsonl"
)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_e003_dpo_run(adapter_dir):
    """Require the exact authorized E003 output and completed training evidence."""
    if Path(adapter_dir).resolve() != E003_ADAPTER_DIR.resolve():
        raise ValueError("E003 evaluation requires the pinned final policy adapter")

    summary_path = E003_RUN_DIR / "e003_training_summary.json"
    state_path = E003_RUN_DIR / "trainer_state.json"
    if not summary_path.is_file() or not state_path.is_file():
        raise ValueError("Missing E003 training summary or final trainer state")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))

    if (
        summary.get("experiment") != "E003"
        or summary.get("steps") != 14
        or state.get("global_step") != 14
        or summary.get("native_eos_id") != NATIVE_EOS_TOKEN_ID
        or summary.get("base_revision") != MODEL_REVISION
        or summary.get("source_pairs_sha256") != E003_SOURCE_PAIRS_SHA256
        or summary.get("source_adapter_dir") != str(E003_SOURCE_ADAPTER)
        or summary.get("training_use_cache") is not False
        or summary.get("generation_use_cache") is not True
        or summary.get("seed") != 42
    ):
        raise ValueError("E003 summary/trainer-state provenance mismatch")
    if not isinstance(summary.get("train_loss"), (int, float)) or not (
        0 <= summary["train_loss"] < 100
    ):
        raise ValueError("E003 training loss missing or invalid")
    if sha256_file(E003_SOURCE_ADAPTER / "adapter_model.safetensors") != E003_SOURCE_E002A_SHA256:
        raise ValueError("E003 source E002a adapter checksum mismatch")
    if sha256_file(E003_PAIRS_PATH) != E003_SOURCE_PAIRS_SHA256:
        raise ValueError("E003 approved preference dataset checksum mismatch")
    if sha256_file("scripts/train_e003_dpo_signed109_v1.py") != E003_TRAINER_SCRIPT_SHA256:
        raise ValueError("Pinned E003 training code checksum mismatch")

    return {
        "experiment": "E003",
        "training_code_revision": E003_TRAINING_REVISION,
        "training_script_sha256": E003_TRAINER_SCRIPT_SHA256,
        "trainer_global_step": 14,
        "training_loss": summary["train_loss"],
        "approved_pairs_sha256": E003_SOURCE_PAIRS_SHA256,
        "starting_e002a_adapter_sha256": E003_SOURCE_E002A_SHA256,
        "training_summary_sha256": sha256_file(summary_path),
        "trainer_state_sha256": sha256_file(state_path),
    }



def cached_generation_kwargs(max_new_tokens, tokenizer):
    """Frozen greedy decoding settings for new inference runs."""
    return {
        "max_new_tokens": max_new_tokens,
        "do_sample": False,
        "use_cache": True,
        "eos_token_id": NATIVE_EOS_TOKEN_ID,
        "pad_token_id": NATIVE_EOS_TOKEN_ID,
        "stop_strings": STOP_STRINGS,
        "tokenizer": tokenizer,
    }


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
    native_eos_epoch=None,
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

    if native_eos_epoch is not None:
        if native_eos_epoch not in (1, 2):
            raise ValueError("Native-EOS epoch must be 1 or 2")
        if run_type not in ("engineering_smoke_test", "development_native_eos"):
            raise ValueError("Native-EOS epoch requires native-EOS evaluation")
        if adapter_dir is None:
            raise ValueError("Native-EOS epoch requires an adapter")

    if run_type == "development_native_eos":
        if adapter_dir is None or native_eos_epoch not in (1, 2):
            raise ValueError("Native-EOS development evaluation requires a pinned epoch")

    if run_type == "development_baseline" and adapter_dir is not None:
        raise ValueError(
            "Pretrained baseline cannot load a LoRA adapter"
        )

    if run_type == "development_sft" and adapter_dir is None:
        raise ValueError(
            "E002 evaluation requires a LoRA adapter"
        )

    if run_type == "development_dpo":
        if adapter_dir is None or native_eos_epoch is not None:
            raise ValueError("E003 DPO evaluation needs its own pinned adapter")


    if run_type in (
        "development_baseline", "development_sft", "development_native_eos",
        "development_dpo",
    ):
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
    native_eos_epoch=None,
    dpo_e003=False,
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

    if dpo_e003:
        if require_completed_e002 or native_eos_epoch is not None:
            raise ValueError("E003 cannot use E002 or E002a verification mode")
        provenance["e003_training"] = verify_e003_dpo_run(adapter_dir)

    if native_eos_epoch is not None:
        if require_completed_e002:
            raise ValueError("Cannot verify E002 and E002a simultaneously")
        if native_eos_epoch not in (1, 2):
            raise ValueError("Unexpected native-EOS epoch")
        if adapter_dir.name != "adapter" or (
            adapter_dir.parent.name != f"epoch_{native_eos_epoch:04d}"
        ):
            raise ValueError("Native-EOS adapter must be inside its epoch directory")

        manifest_path = adapter_dir.parent / "manifest.json"
        metadata_path = adapter_dir.parent.parent / "run_metadata.json"
        if not manifest_path.is_file() or not metadata_path.is_file():
            raise ValueError("Native-EOS checkpoint provenance is incomplete")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        completed_steps = 211 * native_eos_epoch

        if (
            manifest.get("completed_optimizer_steps") != completed_steps
            or manifest.get("next_epoch") != native_eos_epoch
            or manifest.get("config_sha256") != E002A_CONFIG_SHA256
            or manifest.get("code_revision") != E002A_TRAINING_REVISION
            or manifest.get("model_revision") != MODEL_REVISION
            or manifest.get("checksums", {}).get(
                "adapter/adapter_model.safetensors"
            ) != actual_sha256
        ):
            raise ValueError("Native-EOS epoch checkpoint manifest mismatch")

        if (
            metadata.get("run_type") != "formal_training"
            or metadata.get("experiment_id") != "E002a"
            or metadata.get("supervised_eos_token_id") != NATIVE_EOS_TOKEN_ID
            or metadata.get("config_sha256") != E002A_CONFIG_SHA256
            or metadata.get("code_revision") != E002A_TRAINING_REVISION
            or metadata.get("model_revision") != MODEL_REVISION
        ):
            raise ValueError("Native-EOS run metadata mismatch")

        provenance["training_manifest"] = {
            "completed_optimizer_steps": completed_steps,
            "config_sha256": E002A_CONFIG_SHA256,
            "code_revision": E002A_TRAINING_REVISION,
            "model_revision": MODEL_REVISION,
            "supervised_eos_token_id": NATIVE_EOS_TOKEN_ID,
        }

    return provenance



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--run-type",
        choices=(
            "engineering_smoke_test", "development_baseline",
            "development_sft", "development_native_eos", "development_dpo",
        ),
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
    parser.add_argument("--native-eos-epoch", type=int, choices=(1, 2))
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
        native_eos_epoch=args.native_eos_epoch,
    )

    adapter_provenance = None

    if args.adapter_dir is not None:
        adapter_provenance = verify_adapter_checkpoint(
            args.adapter_dir,
            args.expected_adapter_sha256,
            require_completed_e002=(
                args.run_type == "development_sft"
            ),
            native_eos_epoch=args.native_eos_epoch,
            dpo_e003=(args.run_type == "development_dpo"),
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
        local_files_only=True,
    )

    if tokenizer.eos_token_id != 151645 or tokenizer.pad_token_id != 151643:
        raise ValueError("Unexpected pinned Qwen3 tokenizer EOS/PAD IDs")

    print("Loading model...")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        local_files_only=True,
        dtype=torch.float16,
        attn_implementation="eager",
        use_safetensors=True,
    ).to(DEVICE)

    if model.config.eos_token_id != NATIVE_EOS_TOKEN_ID:
        raise ValueError("Unexpected pinned base-model native EOS")

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

    # Frozen E002a cached v1 inference protocol: generation KV cache ON.
    model.config.use_cache = True
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
                    **cached_generation_kwargs(args.max_new_tokens, tokenizer),
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
                "native_eos_stop": bool(
                    len(new_token_ids) > 0
                    and int(new_token_ids[-1]) == NATIVE_EOS_TOKEN_ID
                ),
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
            "dpo_lora_from_e002a_native_eos" if args.run_type == "development_dpo"
            else "sft_lora_native_eos" if args.native_eos_epoch is not None
            else "sft_lora" if args.adapter_dir is not None
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
        "kv_cache": True,
        "eos_token_id": NATIVE_EOS_TOKEN_ID,
        "pad_token_id": NATIVE_EOS_TOKEN_ID,
        "inference_protocol_version": INFERENCE_PROTOCOL_VERSION,
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

    print("\n=== EVALUATION SUMMARY ===")
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
    print("\nEvaluation run: COMPLETED")


if __name__ == "__main__":
    main()
