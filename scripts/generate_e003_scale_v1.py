"""E003 256-question disjoint, resumable generation study. Never train.

Immutable per-question, atomic checkpoints. --resume is mandatory for an existing
output directory. A completed run is verified and not regenerated.
"""

import argparse
import fcntl
import json
import os
import random
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from time import perf_counter

import torch
import torch.backends.python_native as python_native
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm_post_training.data.loader import load_gsm8k_split
from llm_post_training.evaluation.answer_extraction import ANSWER_EXTRACTION_VERSION
from llm_post_training.evaluation.metrics import evaluate_response
from llm_post_training.evaluation.prompting import BASELINE_PROMPT_VERSION, format_baseline_prompt
from scripts.pilot_dpo_preferences import (
    ADAPTER_SHA, EXPECTED_IMAGE_ID, MANIFEST_SHA, MODEL_ID,
    MODEL_REVISION, NATIVE_EOS, SOURCE_SHA, TOKENIZER_EOS,
    candidate_is_eligible, group_is_mixed, sha256_file,
)

PILOT_REVISION = "dd3a80247c92e57d5d01d8e8531778e861b5b2ad"
PILOT_CONFIG_SHA = "e57f800f08dc58c8b4c8d4f97ce641762950c0955e1375739e652f3079b24d1c"
TRAIN_CONFIG_SHA = "11c9977d2edc288129a2fafdf6331e473fab79beee88d6fc32cb0e4b7cedae52"
TRAIN_REVISION = "31b73e9ac15572b44ee479ce047048d6404bb72f"
SCALE_VERSION = "e003_scale_v1"
SELECTED_COUNT = 256
SAMPLES = 4
MAX_TOKENS = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def atomic_write(path, contents):
    """Replace file only after durable complete write; never replace a checkpoint."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".incomplete_", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(contents)
            output.flush()
            os.fsync(output.fileno())
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite: {path}")
        os.replace(temp, path)
        dirfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def canonical_json(doc):
    return json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def validate_config(c):
    required = {
        "config_version": SCALE_VERSION,
        "experiment_id": "E003",
        "purpose": "intermediate_candidate_generation_only",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "adapter_dir": "data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter",
        "adapter_sha256": ADAPTER_SHA,
        "source_path": "data/raw/gsm8k/train.jsonl",
        "source_sha256": SOURCE_SHA,
        "manifest_path": "configs/data/gsm8k_split_v1.json",
        "manifest_sha256": MANIFEST_SHA,
        "split": "training",
        "expected_training_questions": 6726,
        "prompt_version": BASELINE_PROMPT_VERSION,
        "answer_extraction_version": ANSWER_EXTRACTION_VERSION,
        "seed": 42,
        "scale_questions": SELECTED_COUNT,
        "selection_seed": 42003,
        "samples_per_question": SAMPLES,
        "excluded_pilot_dir": "data/preference_runs/e003_pilot32_k4_v1",
        "generation": {
            "do_sample": True, "temperature": 0.8, "top_p": 0.95,
            "max_new_tokens": MAX_TOKENS, "use_cache": True,
            "attn_implementation": "eager", "eos_token_id": NATIVE_EOS,
            "pad_token_id": NATIVE_EOS, "stop_strings": [],
        },
    }
    require(c == required, "Scale config must exactly match the versioned protocol")


def verify_training(c):
    for p, expected in (
        (c["source_path"], SOURCE_SHA),
        (c["manifest_path"], MANIFEST_SHA),
        (c["adapter_dir"] + "/adapter_model.safetensors", ADAPTER_SHA),
    ):
        require(sha256_file(Path(p)) == expected, f"Pinned checksum mismatch: {p}")
    adapter = Path(c["adapter_dir"])
    require((adapter / "adapter_config.json").is_file(), "Adapter config missing")
    root = adapter.parent.parent
    meta = json.loads((root / "run_metadata.json").read_text(encoding="utf-8"))
    epoch = json.loads((adapter.parent / "manifest.json").read_text(encoding="utf-8"))
    require(meta.get("experiment_id") == "E002a" and
            meta.get("supervised_eos_token_id") == NATIVE_EOS and
            meta.get("config_sha256") == TRAIN_CONFIG_SHA and
            meta.get("code_revision") == TRAIN_REVISION and
            epoch.get("config_sha256") == TRAIN_CONFIG_SHA and
            epoch.get("code_revision") == TRAIN_REVISION and
            epoch.get("completed_optimizer_steps") == 422 and
            epoch.get("next_epoch") == 2 and
            epoch.get("checksums", {}).get("adapter/adapter_model.safetensors") == ADAPTER_SHA,
            "E002a final checkpoint provenance mismatch")


def choose_disjoint_questions(training, pilot_meta, pilot_summary, pilot_config):
    require(pilot_meta.get("run_type") == "e003_preference_candidate_pilot", "Pilot run type mismatch")
    require(pilot_meta.get("code_revision") == PILOT_REVISION, "Pilot revision mismatch")
    require(pilot_meta.get("config_sha256") == PILOT_CONFIG_SHA, "Pilot config checksum mismatch")
    require(pilot_meta.get("config") == pilot_config, "Pilot metadata config mismatch")
    require(pilot_meta.get("training_only") is True, "Pilot not training only")
    require(pilot_meta.get("reference_policy_adapter_sha256") == ADAPTER_SHA, "Pilot adapter mismatch")
    require(pilot_summary.get("candidates") == 128 and
            pilot_summary.get("pilot_questions") == 32 and
            pilot_summary.get("training_performed") is False and
            pilot_summary.get("official_test_used") is False and
            pilot_summary.get("code_revision") == PILOT_REVISION,
            "Pilot summary mismatch")
    ordered = sorted(training, key=lambda r: r.source_index)
    require(len(ordered) == 6726 and len({r.source_index for r in ordered}) == 6726,
            "Unexpected frozen training partition")
    positions = random.Random(42).sample(range(len(ordered)), 32)
    expected_pilot = sorted(ordered[i].source_index for i in positions)
    require(pilot_meta.get("selected_source_indices") == expected_pilot,
            "Pilot selected indices do not match original seeded selection")
    remaining = [r for r in ordered if r.source_index not in set(expected_pilot)]
    selection = random.Random(42003).sample(remaining, SELECTED_COUNT)
    selection = sorted(selection, key=lambda r: r.source_index)
    require(set(r.source_index for r in selection).isdisjoint(expected_pilot),
            "Pilot question overlap")
    return selection, expected_pilot


def validate_record(rec, example, tokenizer):
    """On resume independently regrade every previously generated candidate."""
    index = example.source_index
    sample_index = rec.get("sample_index")
    require(type(sample_index) is int and 0 <= sample_index < SAMPLES, "Sample index invalid")
    require(rec.get("source_index") == index, "Source index mismatch")
    require(rec.get("sample_seed") == 42 + index * 100 + sample_index, "Sample RNG mismatch")
    require(rec.get("prompt") == format_baseline_prompt(example.question), "Prompt mismatch")
    require(rec.get("reference_answer") == str(example.reference_answer), "Reference mismatch")
    ids = rec.get("generated_token_ids")
    require(isinstance(ids, list) and 1 <= len(ids) <= MAX_TOKENS and
            all(type(i) is int and 0 <= i < len(tokenizer) for i in ids), "Token IDs invalid")
    require(rec.get("generated_tokens") == len(ids), "Token count mismatch")
    require(rec.get("native_eos_stop") is (ids[-1] == NATIVE_EOS), "EOS label mismatch")
    require(rec.get("reached_token_cap") is (len(ids) == MAX_TOKENS), "Token cap mismatch")
    require(rec.get("response") == tokenizer.decode(ids, skip_special_tokens=True),
            "Token-to-text mismatch")
    judged = evaluate_response(response=rec["response"],
                               expected_answer=example.reference_answer,
                               generated_tokens=len(ids),
                               reached_token_cap=len(ids) == MAX_TOKENS)
    require(rec.get("correct") is bool(judged.correct), "Regraded correctness mismatch")
    require(rec.get("extraction_status") == judged.extraction.status, "Extraction status mismatch")
    require(rec.get("extracted_answer") == (
        str(judged.extraction.answer) if judged.extraction.answer is not None else None),
        "Extracted numeric answer mismatch")
    require(rec.get("unwanted_continuation") is bool(judged.extraction.unwanted_continuation),
            "Continuation label mismatch")
    require(rec.get("eligible") is candidate_is_eligible(rec), "Eligibility mismatch")
    require(type(rec.get("generation_seconds")) in (int, float) and
            0 <= rec["generation_seconds"] < 100000, "Timing invalid")


def validate_group(rows, example, tokenizer):
    require(len(rows) == SAMPLES, "Incomplete question group")
    require(sorted(r.get("sample_index") for r in rows) == list(range(SAMPLES)),
            "Duplicate or missing sample index")
    for rec in rows:
        validate_record(rec, example, tokenizer)


def generate_group(model, tokenizer, example):
    prompt = format_baseline_prompt(example.question)
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to("cuda")
    prompt_size = inputs["input_ids"].shape[1]
    rows = []
    for sample_index in range(SAMPLES):
        seed = 42 + example.source_index * 100 + sample_index
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.cuda.synchronize()
        started = perf_counter()
        with torch.inference_mode():
            tokens = model.generate(
                **inputs, max_new_tokens=MAX_TOKENS, do_sample=True,
                temperature=0.8, top_p=0.95, use_cache=True,
                eos_token_id=NATIVE_EOS, pad_token_id=NATIVE_EOS,
            )
        torch.cuda.synchronize()
        elapsed = perf_counter() - started
        ids = tokens[0, prompt_size:].tolist()
        text = tokenizer.decode(ids, skip_special_tokens=True)
        cap = len(ids) == MAX_TOKENS
        judged = evaluate_response(
            response=text, expected_answer=example.reference_answer,
            generated_tokens=len(ids), reached_token_cap=cap,
        )
        rec = {
            "source_index": example.source_index,
            "sample_index": sample_index,
            "sample_seed": seed,
            "prompt": prompt,
            "reference_answer": str(example.reference_answer),
            "response": text,
            "generated_token_ids": ids,
            "generated_tokens": len(ids),
            "generation_seconds": elapsed,
            "native_eos_stop": bool(ids) and ids[-1] == NATIVE_EOS,
            "reached_token_cap": cap,
            "extraction_status": judged.extraction.status,
            "extracted_answer": (str(judged.extraction.answer)
                                 if judged.extraction.answer is not None else None),
            "unwanted_continuation": bool(judged.extraction.unwanted_continuation),
            "correct": bool(judged.correct),
        }
        rec["eligible"] = candidate_is_eligible(rec)
        rows.append(rec)
        del tokens
    validate_group(rows, example, tokenizer)
    return rows


def read_group(path, example, tokenizer):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    validate_group(rows, example, tokenizer)
    return sorted(rows, key=lambda r: r["sample_index"])


def output_summary(rows, selected, cfg_sha, code_revision, peak_vram):
    n = len(rows)
    require(n == SELECTED_COUNT * SAMPLES, "Incorrect total candidate count")
    by_source = defaultdict(list)
    for row in rows:
        by_source[row["source_index"]].append(row)
    require(len(by_source) == SELECTED_COUNT, "Incorrect question count")
    for group in by_source.values():
        require(len(group) == SAMPLES, "Incomplete group in summary")
    return {
        "run_type": "e003_intermediate_candidate_generation",
        "code_revision": code_revision,
        "config_sha256": cfg_sha,
        "reference_policy_adapter_sha256": ADAPTER_SHA,
        "training_questions": 6726,
        "scale_questions": len(selected),
        "candidates": n,
        "native_eos_stops": sum(r["native_eos_stop"] for r in rows),
        "token_caps": sum(r["reached_token_cap"] for r in rows),
        "valid_extractions": sum(r["extraction_status"] == "valid" for r in rows),
        "eligible_candidates": sum(r["eligible"] for r in rows),
        "correct_eligible_candidates": sum(r["eligible"] and r["correct"] for r in rows),
        "mixed_groups_with_potential_pair": sum(group_is_mixed(g) for g in by_source.values()),
        "mean_generated_tokens": sum(r["generated_tokens"] for r in rows) / n,
        "mean_generation_seconds": sum(r["generation_seconds"] for r in rows) / n,
        "peak_allocated_vram_mib": peak_vram,
        "training_performed": False,
        "official_test_used": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--docker-image-id", required=True)
    parser.add_argument("--preflight-only", action="store_true",
                        help="Audit data, adapter and disjoint selection without model or output")
    parser.add_argument("--resume", action="store_true",
                        help="Resume an existing incomplete run; verify every completed group")
    parser.add_argument("--stop-after-new-groups", type=int,
                        help="Engineering pause after exactly this many newly generated groups")
    args = parser.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", args.code_revision) is not None,
            "Code revision must be a full Git SHA")
    require(args.docker_image_id == EXPECTED_IMAGE_ID, "Unexpected Docker image ID")
    if args.stop_after_new_groups is not None:
        require(args.stop_after_new_groups >= 1, "Invalid group pause count")
    c = json.loads(args.config.read_text(encoding="utf-8"))
    validate_config(c)
    cfg_sha = sha256_file(args.config)
    verify_training(c)
    pilot_dir = Path(c["excluded_pilot_dir"])
    pilot_meta = json.loads((pilot_dir / "metadata.json").read_text(encoding="utf-8"))
    pilot_summary = json.loads((pilot_dir / "summary.json").read_text(encoding="utf-8"))
    pilot_cfg = json.loads(Path("configs/preference/e003_pilot_v1.json").read_text(encoding="utf-8"))
    require(sha256_file(Path("configs/preference/e003_pilot_v1.json")) == PILOT_CONFIG_SHA,
            "Original pilot config checksum mismatch")
    require(pilot_summary.get("config_sha256") == PILOT_CONFIG_SHA, "Pilot summary config mismatch")
    training = load_gsm8k_split(Path(c["source_path"]), Path(c["manifest_path"]), "training")
    validation = load_gsm8k_split(Path(c["source_path"]), Path(c["manifest_path"]), "validation")
    require(set(r.source_index for r in training).isdisjoint(r.source_index for r in validation),
            "Frozen training and validation overlap")
    selected, excluded = choose_disjoint_questions(training, pilot_meta, pilot_summary, pilot_cfg)
    if args.preflight_only:
        require(not args.resume and args.stop_after_new_groups is None,
                "Preflight cannot resume or generate groups")
        print("=== E003 SCALE PREFLIGHT PASSED ===")
        print(f"Training questions: {len(training)}")
        print(f"Excluded original pilot questions: {len(excluded)}")
        print(f"New disjoint questions: {len(selected)}")
        print(f"Planned candidate completions: {len(selected) * SAMPLES}")
        print(f"Config SHA256: {cfg_sha}")
        print("GPU inference: NOT STARTED; output created: NO")
        return
    meta = {
        "run_type": "e003_intermediate_candidate_generation",
        "version": SCALE_VERSION,
        "code_revision": args.code_revision,
        "docker_image_id": args.docker_image_id,
        "config_sha256": cfg_sha,
        "config": c,
        "pilot_metadata_sha256": sha256_file(pilot_dir / "metadata.json"),
        "pilot_summary_sha256": sha256_file(pilot_dir / "summary.json"),
        "excluded_pilot_source_indices": excluded,
        "selected_source_indices": [r.source_index for r in selected],
        "reference_policy_adapter_sha256": ADAPTER_SHA,
        "training_only": True,
        "training_performed": False,
        "official_test_used": False,
    }
    if args.resume:
        require(args.output_dir.is_dir(), "Resume requires an existing output directory")
        stored_meta = json.loads((args.output_dir / "metadata.json").read_text(encoding="utf-8"))
        require(stored_meta == meta, "Resume provenance/selection mismatch")
    else:
        require(not args.output_dir.exists(), "Output directory already exists; use --resume")
        args.output_dir.mkdir(parents=True, exist_ok=False)
        atomic_write(args.output_dir / "metadata.json", canonical_json(meta))
    # flock prevents two concurrent writers, including resume attempts.
    with (args.output_dir / ".generation.lock").open("a+") as lockfile:
        try:
            fcntl.flock(lockfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Another generation process is using this run") from exc
        if (args.output_dir / "summary.json").exists():
            require((args.output_dir / "candidates.jsonl").is_file(), "Completed run missing output")
        # Load model only when actually generating missing groups.
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID, revision=MODEL_REVISION, local_files_only=True)
        require(tokenizer.eos_token_id == TOKENIZER_EOS and
                tokenizer.pad_token_id == NATIVE_EOS, "Tokenizer special token mismatch")
        progress = args.output_dir / "progress"
        progress.mkdir(exist_ok=True)
        expected_names = {f"source_{x.source_index:05d}.jsonl" for x in selected}
        existing_names = {p.name for p in progress.iterdir() if p.suffix == ".jsonl"}
        require(existing_names <= expected_names, "Unexpected checkpoint source index")
        selected_map = {r.source_index: r for r in selected}
        rows_by_index = {}
        for p in sorted(progress.glob("source_*.jsonl")):
            idx = int(p.stem.split("_")[-1])
            require(idx in selected_map, "Unexpected existing question checkpoint")
            rows_by_index[idx] = read_group(p, selected_map[idx], tokenizer)
        print(f"Verified existing groups: {len(rows_by_index)}/{SELECTED_COUNT}", flush=True)
        if len(rows_by_index) < SELECTED_COUNT:
            require(torch.cuda.is_available() and torch.cuda.get_device_capability(0) == (7, 0),
                    "Expected V100 sm70 GPU")
            python_native.triton.enabled = False
            base = AutoModelForCausalLM.from_pretrained(
                MODEL_ID, revision=MODEL_REVISION, local_files_only=True,
                dtype=torch.float16, attn_implementation="eager", use_safetensors=True)
            require(base.config.eos_token_id == NATIVE_EOS, "Base native EOS mismatch")
            base.config.use_cache = True
            model = PeftModel.from_pretrained(
                base, str(c["adapter_dir"]), is_trainable=False,
                autocast_adapter_dtype=True).to("cuda")
            require(len(model.peft_config) == 1, "Unexpected adapter count")
            model.config.use_cache = True
            model.eval()
            torch.cuda.reset_peak_memory_stats()
            new_groups = 0
            for position, example in enumerate(selected, 1):
                index = example.source_index
                if index in rows_by_index:
                    continue
                rows = generate_group(model, tokenizer, example)
                checkpoint = progress / f"source_{index:05d}.jsonl"
                atomic_write(checkpoint, "".join(json.dumps(
                    r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))
                rows_by_index[index] = rows
                new_groups += 1
                print(f"[{position}/{SELECTED_COUNT}] source={index} "
                      f"eligible={sum(r['eligible'] for r in rows)}/4 "
                      f"correct_eligible={sum(r['eligible'] and r['correct'] for r in rows)} "
                      f"mixed={group_is_mixed(rows)}", flush=True)
                if args.stop_after_new_groups == new_groups:
                    print("Engineering pause after committed question groups; "
                          "use --resume. No summary or final dataset emitted.", flush=True)
                    return
            peak_vram = torch.cuda.max_memory_allocated() / 1024**2
        else:
            peak_vram = None  # Recorded peak of original process cannot be recovered.
        require(len(rows_by_index) == SELECTED_COUNT, "Incomplete scale run")
        rows = [r for example in selected for r in rows_by_index[example.source_index]]
        generated_contents = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                                     for r in rows)
        final_path = args.output_dir / "candidates.jsonl"
        if final_path.exists():
            require(final_path.read_text(encoding="utf-8") == generated_contents,
                    "Completed candidate file differs from checked checkpoints")
        else:
            atomic_write(final_path, generated_contents)
        summary = output_summary(rows, selected, cfg_sha, args.code_revision, peak_vram)
        summary["candidates_sha256"] = sha256_file(final_path)
        if (args.output_dir / "summary.json").exists():
            prev = json.loads((args.output_dir / "summary.json").read_text(encoding="utf-8"))
            stable = {key: value for key, value in summary.items()
                      if key != "peak_allocated_vram_mib"}
            require({k: v for k, v in prev.items() if k != "peak_allocated_vram_mib"} == stable,
                    "Existing summary mismatch")
        else:
            atomic_write(args.output_dir / "summary.json", canonical_json(summary))
        print("\n=== E003 INTERMEDIATE GENERATION COMPLETE ===")
        print(canonical_json(json.loads((args.output_dir / "summary.json").read_text(encoding="utf-8"))))
        print(f"Candidates SHA256: {sha256_file(final_path)}")
        print("Model weights changed: NO; DPO training: NOT STARTED")


if __name__ == "__main__":
    main()
