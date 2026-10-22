"""Bounded E003 preference-candidate pilot. Generate only; do not train DPO.

Creates an immutable directory containing config/provenance, candidate JSONL,
and a summary. Uses ONLY frozen GSM8K training-partition questions.
"""

import argparse
import hashlib
import json
import os
import random
import re
from pathlib import Path
from time import perf_counter

import torch
import torch.backends.python_native as python_native
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.data.loader import load_gsm8k_split
from llm_post_training.evaluation.answer_extraction import ANSWER_EXTRACTION_VERSION
from llm_post_training.evaluation.metrics import evaluate_response
from llm_post_training.evaluation.prompting import (
    BASELINE_PROMPT_VERSION,
    format_baseline_prompt,
)

MODEL_ID = "Qwen/Qwen3-0.6B-Base"
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"
ADAPTER_SHA = "f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625"
SOURCE_SHA = "17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465"
MANIFEST_SHA = "31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719"
NATIVE_EOS = 151643
TOKENIZER_EOS = 151645
EXPECTED_IMAGE_ID = "sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def candidate_is_eligible(record: dict) -> bool:
    """Only finite, explicit, EOS-terminated, unambiguous solutions qualify."""
    return (
        record["native_eos_stop"] is True
        and record["reached_token_cap"] is False
        and record["extraction_status"] == "valid"
        and record["unwanted_continuation"] is False
        and "the answer is" in record["response"].lower()
    )


def group_is_mixed(records: list[dict]) -> bool:
    eligible = [r for r in records if candidate_is_eligible(r)]
    return any(r["correct"] for r in eligible) and any(
        not r["correct"] for r in eligible
    )


def validate_config(c: dict) -> None:
    checks = [
        (c["config_version"] == "e003_preference_pilot_v1", "version"),
        (c["experiment_id"] == "E003", "experiment"),
        (c["purpose"] == "pilot_candidate_generation_only", "purpose"),
        (c["model_id"] == MODEL_ID, "model id"),
        (c["model_revision"] == MODEL_REVISION, "model revision"),
        (c["adapter_sha256"] == ADAPTER_SHA, "adapter sha"),
        (c["source_sha256"] == SOURCE_SHA, "source sha"),
        (c["manifest_sha256"] == MANIFEST_SHA, "manifest sha"),
        (c["split"] == "training", "split"),
        (c["expected_training_questions"] == 6726, "training size"),
        (c["prompt_version"] == BASELINE_PROMPT_VERSION, "prompt"),
        (c["answer_extraction_version"] == ANSWER_EXTRACTION_VERSION, "extraction"),
        (type(c["seed"]) is int and c["seed"] == 42, "seed"),
        (type(c["pilot_questions"]) is int and c["pilot_questions"] == 32, "pilot n"),
        (type(c["samples_per_question"]) is int and c["samples_per_question"] == 4, "samples"),
        (c["generation"] == {
            "do_sample": True, "temperature": 0.8, "top_p": 0.95,
            "max_new_tokens": 256, "use_cache": True,
            "attn_implementation": "eager", "eos_token_id": NATIVE_EOS,
            "pad_token_id": NATIVE_EOS, "stop_strings": [],
        }, "sampling protocol"),
    ]
    for ok, label in checks:
        if not ok:
            raise ValueError(f"Unexpected E003 pilot configuration: {label}")
    # Refuse non-pinned source locations as well as non-pinned content.
    for key, required in (
        ("adapter_dir", "data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter"),
        ("source_path", "data/raw/gsm8k/train.jsonl"),
        ("manifest_path", "configs/data/gsm8k_split_v1.json"),
    ):
        if c[key] != required:
            raise ValueError(f"Unexpected E003 pilot path: {key}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--docker-image-id", required=True)
    args = parser.parse_args()

    if re.fullmatch(r"[0-9a-f]{40}", args.code_revision) is None:
        raise ValueError("--code-revision must be a full Git SHA")
    if args.docker_image_id != EXPECTED_IMAGE_ID:
        raise ValueError("Unexpected Docker image ID")
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)

    c = json.loads(args.config.read_text(encoding="utf-8"))
    validate_config(c)
    cfg_sha = sha256_file(args.config)
    source = Path(c["source_path"])
    manifest = Path(c["manifest_path"])
    adapter_dir = Path(c["adapter_dir"])
    for path, expected in (
        (source, SOURCE_SHA),
        (manifest, MANIFEST_SHA),
        (adapter_dir / "adapter_model.safetensors", ADAPTER_SHA),
    ):
        if sha256_file(path) != expected:
            raise ValueError(f"Checksum mismatch: {path}")
    if not (adapter_dir / "adapter_config.json").is_file():
        raise FileNotFoundError("Adapter config missing")

    training_run_dir = adapter_dir.parent.parent
    training_metadata = json.loads(
        (training_run_dir / "run_metadata.json").read_text(encoding="utf-8")
    )
    epoch_manifest = json.loads(
        (adapter_dir.parent / "manifest.json").read_text(encoding="utf-8")
    )
    expected_training_sha = "11c9977d2edc288129a2fafdf6331e473fab79beee88d6fc32cb0e4b7cedae52"
    expected_training_revision = "31b73e9ac15572b44ee479ce047048d6404bb72f"
    if not (
        training_metadata.get("experiment_id") == "E002a"
        and training_metadata.get("supervised_eos_token_id") == NATIVE_EOS
        and training_metadata.get("config_sha256") == expected_training_sha
        and training_metadata.get("code_revision") == expected_training_revision
        and epoch_manifest.get("config_sha256") == expected_training_sha
        and epoch_manifest.get("code_revision") == expected_training_revision
        and epoch_manifest.get("completed_optimizer_steps") == 422
        and epoch_manifest.get("next_epoch") == 2
        and epoch_manifest.get("checksums", {}).get(
            "adapter/adapter_model.safetensors"
        ) == ADAPTER_SHA
    ):
        raise ValueError("E002a epoch-2 training provenance does not match")

    if not torch.cuda.is_available() or torch.cuda.get_device_capability(0) != (7, 0):
        raise RuntimeError("Expected NVIDIA V100 GPU")
    python_native.triton.enabled = False

    training = load_gsm8k_split(source, manifest, "training")
    assert len(training) == 6726
    assert len({x.source_index for x in training}) == 6726
    validation = load_gsm8k_split(source, manifest, "validation")
    assert not ({x.source_index for x in training} & {x.source_index for x in validation})
    training = sorted(training, key=lambda x: x.source_index)
    sampled_positions = random.Random(c["seed"]).sample(
        range(len(training)), c["pilot_questions"]
    )
    selected = sorted((training[i] for i in sampled_positions), key=lambda x: x.source_index)

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, local_files_only=True
    )
    assert tokenizer.eos_token_id == TOKENIZER_EOS
    assert tokenizer.pad_token_id == NATIVE_EOS
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, local_files_only=True,
        dtype=torch.float16, attn_implementation="eager", use_safetensors=True,
    )
    assert base.config.eos_token_id == NATIVE_EOS
    base.config.use_cache = True
    model = PeftModel.from_pretrained(
        base, str(adapter_dir), is_trainable=False, autocast_adapter_dtype=True
    ).to("cuda")
    assert len(model.peft_config) == 1
    model.config.use_cache = True
    model.eval()
    torch.cuda.reset_peak_memory_stats()

    args.output_dir.mkdir(parents=True, exist_ok=False)
    metadata = {
        "run_type": "e003_preference_candidate_pilot",
        "config_sha256": cfg_sha,
        "config": c,
        "code_revision": args.code_revision,
        "docker_image_id": args.docker_image_id,
        "selected_source_indices": [x.source_index for x in selected],
        "reference_policy_adapter_sha256": ADAPTER_SHA,
        "training_only": True,
    }
    (args.output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    generated = 0
    eos_stops = 0
    caps = 0
    valid = 0
    eligible = 0
    correct_eligible = 0
    mixed = 0
    seconds = 0.0
    token_total = 0
    with (args.output_dir / "candidates.jsonl").open("x", encoding="utf-8") as output:
        for prompt_num, example in enumerate(selected, start=1):
            prompt = format_baseline_prompt(example.question)
            inputs = tokenizer(
                prompt, return_tensors="pt", add_special_tokens=False
            ).to("cuda")
            prompt_size = inputs["input_ids"].shape[1]
            candidates = []
            for sample_index in range(c["samples_per_question"]):
                # Stable per-(question, sample) RNG; no reliance on Python hash().
                sample_seed = c["seed"] + example.source_index * 100 + sample_index
                torch.manual_seed(sample_seed)
                torch.cuda.manual_seed_all(sample_seed)
                torch.cuda.synchronize()
                started = perf_counter()
                with torch.inference_mode():
                    tokens = model.generate(
                        **inputs,
                        max_new_tokens=256,
                        do_sample=True,
                        temperature=0.8,
                        top_p=0.95,
                        use_cache=True,
                        eos_token_id=NATIVE_EOS,
                        pad_token_id=NATIVE_EOS,
                    )
                torch.cuda.synchronize()
                elapsed = perf_counter() - started
                ids = tokens[0, prompt_size:].tolist()
                text = tokenizer.decode(ids, skip_special_tokens=True)
                eos_stop = bool(ids) and ids[-1] == NATIVE_EOS
                cap = len(ids) == 256
                judged = evaluate_response(
                    response=text,
                    expected_answer=example.reference_answer,
                    generated_tokens=len(ids),
                    reached_token_cap=cap,
                )
                rec = {
                    "source_index": example.source_index,
                    "sample_index": sample_index,
                    "sample_seed": sample_seed,
                    "prompt": prompt,
                    "reference_answer": str(example.reference_answer),
                    "response": text,
                    "generated_token_ids": ids,
                    "generated_tokens": len(ids),
                    "generation_seconds": elapsed,
                    "native_eos_stop": eos_stop,
                    "reached_token_cap": cap,
                    "extraction_status": judged.extraction.status,
                    "extracted_answer": (
                        str(judged.extraction.answer)
                        if judged.extraction.answer is not None else None
                    ),
                    "unwanted_continuation": bool(judged.extraction.unwanted_continuation),
                    "correct": bool(judged.correct),
                }
                rec["eligible"] = candidate_is_eligible(rec)
                output.write(json.dumps(rec, ensure_ascii=False) + "\n")
                output.flush()
                candidates.append(rec)
                generated += 1
                eos_stops += int(eos_stop)
                caps += int(cap)
                valid += int(rec["extraction_status"] == "valid")
                eligible += int(rec["eligible"])
                correct_eligible += int(rec["eligible"] and rec["correct"])
                seconds += elapsed
                token_total += len(ids)
                del tokens
            mixed += int(group_is_mixed(candidates))
            print(
                f"[{prompt_num}/{len(selected)}] source={example.source_index} "
                f"eligible={sum(r['eligible'] for r in candidates)}/4 "
                f"correct_eligible={sum(r['eligible'] and r['correct'] for r in candidates)} "
                f"mixed={group_is_mixed(candidates)}",
                flush=True,
            )
        os.fsync(output.fileno())

    assert generated == 128
    summary = {
        "run_type": "e003_preference_candidate_pilot",
        "code_revision": args.code_revision,
        "config_sha256": cfg_sha,
        "reference_policy_adapter_sha256": ADAPTER_SHA,
        "training_questions": len(training),
        "pilot_questions": len(selected),
        "candidates": generated,
        "native_eos_stops": eos_stops,
        "token_caps": caps,
        "valid_extractions": valid,
        "eligible_candidates": eligible,
        "correct_eligible_candidates": correct_eligible,
        "mixed_groups_with_potential_pair": mixed,
        "mean_generated_tokens": token_total / generated,
        "mean_generation_seconds": seconds / generated,
        "peak_allocated_vram_mib": torch.cuda.max_memory_allocated() / 1024**2,
        "training_performed": False,
        "official_test_used": False,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("\n=== E003 PREFERENCE PILOT SUMMARY ===")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("\nCandidate generation: COMPLETE; DPO training: NOT STARTED")


if __name__ == "__main__":
    main()
