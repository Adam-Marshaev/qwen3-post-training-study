"""Materialize *provisional* E003 DPO pilot pairs. Read-only inputs, no training.

Usage: python scripts/build_e003_pilot_pairs.py --output-dir /results/e003_pilot_pairs18_v1 --code-revision <40-hex>

This script deliberately refuses to label any pair as independently signed off.
"""

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

NATIVE_EOS = 151643
TOKENIZER_EOS = 151645
MODEL_ID = "Qwen/Qwen3-0.6B-Base"
MODEL_REVISION = "57ca99e94acb83175495aa2c6b6b0cc498170924"
ADAPTER_SHA = "f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625"
SOURCE_SHA = "17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465"
SPLIT_SHA = "31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719"
PILOT_CONFIG_SHA = "e57f800f08dc58c8b4c8d4f97ce641762950c0955e1375739e652f3079b24d1c"
REVIEW_SHA = "052715d89455b9932cecef699a25912c3bb3b8165e2c0919837ea888583ea5c8"
PILOT_REVISION = "dd3a80247c92e57d5d01d8e8531778e861b5b2ad"
EXPECTED_IMAGE_ID = "sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e"

DEFAULT_PILOT = Path("data/preference_runs/e003_pilot32_k4_v1")
DEFAULT_REVIEW = Path("configs/preference/e003_pilot_reasoning_screen_v1.json")
DEFAULT_CONFIG = Path("configs/preference/e003_pilot_v1.json")
SOURCE = Path("data/raw/gsm8k/train.jsonl")
SPLIT = Path("configs/data/gsm8k_split_v1.json")
ADAPTER = Path("data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/adapter_model.safetensors")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def candidate_is_eligible(record: dict) -> bool:
    """Match the frozen E003 pilot predicate without importing CUDA packages."""
    return (
        record["native_eos_stop"] is True
        and record["reached_token_cap"] is False
        and record["extraction_status"] == "valid"
        and record["unwanted_continuation"] is False
        and "the answer is" in record["response"].lower()
    )


def audit_review(review: dict) -> dict[int, dict]:
    require(review["schema"] == "e003_pilot_reasoning_screen_v1", "Review schema mismatch")
    require(review["classification"] == "advisory_only_not_frozen_training_dataset", "Not an advisory review")
    require(review["human_signoff_required_before_training"] is True, "Missing signoff safeguard")
    require(review["pilot_run"] == DEFAULT_PILOT.name, "Wrong pilot run")
    require(review["pilot_code_revision"] == PILOT_REVISION, "Pilot revision mismatch")
    require(review["reference_policy_adapter_sha256"] == ADAPTER_SHA, "Review adapter mismatch")
    rows = review["rows"]
    require(len(rows) == 21, "Expected 21 reviewed mixed groups")
    keyed = {row["source_index"]: row for row in rows}
    require(len(keyed) == 21, "Duplicate reviewed source index")
    require(
        Counter(row["screening_status"] for row in rows)
        == Counter({"PROVISIONAL_APPROVE": 18, "HOLD": 1, "EXCLUDE": 2}),
        "Wrong review status counts",
    )
    for row in rows:
        status = row["screening_status"]
        if status == "PROVISIONAL_APPROVE":
            require(row["manual_signoff_required"] is True, "Missing per-pair signoff safeguard")
            for field in ("chosen_sample_index", "rejected_sample_index"):
                require(type(row[field]) is int and 0 <= row[field] < 4, "Bad sample index")
            require(row["chosen_sample_index"] != row["rejected_sample_index"], "Identical chosen/rejected samples")
        else:
            require(row["chosen_sample_index"] is None and row["rejected_sample_index"] is None,
                    "Unapproved group contains a pair")
    return keyed


def audit_candidate(record: dict, expected_prompt: str, expected_answer: str,
                    max_new_tokens: int, seed: int, tokenizer, evaluate_response) -> None:
    index, sample = record["source_index"], record["sample_index"]
    require(type(index) is int and type(sample) is int and 0 <= sample < 4, "Invalid candidate identity")
    require(record["prompt"] == expected_prompt, "Candidate prompt differs from frozen training question")
    require(record["reference_answer"] == expected_answer, "Candidate answer differs from frozen training reference")
    require(record["sample_seed"] == seed + index * 100 + sample, "Candidate sample seed mismatch")
    ids = record["generated_token_ids"]
    require(isinstance(ids, list) and 1 <= len(ids) <= max_new_tokens, "Invalid generated ID length")
    require(all(type(t) is int and 0 <= t < len(tokenizer) for t in ids), "Invalid token IDs")
    require(len(ids) == record["generated_tokens"], "Generated-token count mismatch")
    require(record["native_eos_stop"] is (ids[-1] == NATIVE_EOS), "EOS flag mismatch")
    require(NATIVE_EOS not in ids[:-1], "Embedded native EOS in generated token IDs")
    require(record["reached_token_cap"] is (len(ids) == max_new_tokens), "Token-cap flag mismatch")
    require(tokenizer.decode(ids, skip_special_tokens=True) == record["response"], "Token/text mismatch")
    require(record["eligible"] is candidate_is_eligible(record), "Candidate eligibility mismatch")
    judged = evaluate_response(
        response=record["response"], expected_answer=expected_answer,
        generated_tokens=len(ids), reached_token_cap=record["reached_token_cap"]
    )
    require(record["correct"] is bool(judged.correct), "Incorrect correctness label")
    require(record["extraction_status"] == judged.extraction.status, "Extraction status mismatch")
    require(record["unwanted_continuation"] is bool(judged.extraction.unwanted_continuation),
            "Continuation flag mismatch")
    extracted = (str(judged.extraction.answer) if judged.extraction.answer is not None else None)
    require(record["extracted_answer"] == extracted, "Extracted answer mismatch")


def select_pairs(review: dict, candidates: list[dict]) -> list[dict]:
    """Return exactly 18 provisional pairs; inputs must already be audited."""
    rows = audit_review(review)
    by_id = {(r["source_index"], r["sample_index"]): r for r in candidates}
    require(len(by_id) == len(candidates), "Duplicate candidate identity")
    groups = defaultdict(list)
    for rec in candidates:
        groups[rec["source_index"]].append(rec)
    require(len(groups) == 32, "Wrong pilot group count")
    for index, records in groups.items():
        require(len(records) == 4 and {r["sample_index"] for r in records} == {0, 1, 2, 3},
                f"Incomplete pilot group {index}")
    mixed = {
        index for index, records in groups.items()
        if any(r["eligible"] and r["correct"] for r in records)
        and any(r["eligible"] and not r["correct"] for r in records)
    }
    require(mixed == set(rows), "Review groups do not match candidate mixed groups")
    result = []
    for index, row in sorted(rows.items()):
        if row["screening_status"] != "PROVISIONAL_APPROVE":
            continue
        chosen = by_id[(index, row["chosen_sample_index"])]
        rejected = by_id[(index, row["rejected_sample_index"])]
        require(chosen["eligible"] is True and chosen["correct"] is True, "Chosen is not eligible-correct")
        require(rejected["eligible"] is True and rejected["correct"] is False, "Rejected is not eligible-incorrect")
        require(chosen["generated_token_ids"][-1] == NATIVE_EOS
                and rejected["generated_token_ids"][-1] == NATIVE_EOS, "Pair missing native EOS")
        require(chosen["prompt"] == rejected["prompt"], "Pair prompts differ")
        require(chosen["reference_answer"] == rejected["reference_answer"], "Pair references differ")
        require(chosen["response"] != rejected["response"], "Identical pair responses")
        require(chosen["generated_tokens"] == row["chosen_generated_tokens"], "Chosen length differs from review")
        require(rejected["generated_tokens"] == row["rejected_generated_tokens"], "Rejected length differs from review")
        gap = abs(chosen["generated_tokens"] - rejected["generated_tokens"])
        require(gap == row["length_gap_tokens"], "Pair length gap differs from review")
        result.append({
            "source_index": index,
            "prompt": chosen["prompt"],
            "reference_answer": chosen["reference_answer"],
            "chosen_sample_index": chosen["sample_index"],
            "rejected_sample_index": rejected["sample_index"],
            "chosen_response": chosen["response"],
            "rejected_response": rejected["response"],
            "chosen_generated_token_ids": chosen["generated_token_ids"],
            "rejected_generated_token_ids": rejected["generated_token_ids"],
            "chosen_generated_tokens": chosen["generated_tokens"],
            "rejected_generated_tokens": rejected["generated_tokens"],
            "length_gap_tokens": gap,
            "review_observation": row["observation"],
            "training_approved": False,
            "annotation_status": "provisional_requires_independent_signoff",
        })
    require(len(result) == 18, "Wrong provisional pair count")
    return result


def build(args) -> None:
    require(re.fullmatch(r"[0-9a-f]{40}", args.code_revision) is not None, "Invalid Git revision")
    require(not args.output_dir.exists(), "Output directory already exists")
    for path, expected in (
        (DEFAULT_REVIEW, REVIEW_SHA), (DEFAULT_CONFIG, PILOT_CONFIG_SHA),
        (SOURCE, SOURCE_SHA), (SPLIT, SPLIT_SHA), (ADAPTER, ADAPTER_SHA),
    ):
        require(file_sha256(path) == expected, f"Input SHA256 mismatch: {path}")
    review = read_json(DEFAULT_REVIEW)
    audit_review(review)
    metadata = read_json(DEFAULT_PILOT / "metadata.json")
    summary = read_json(DEFAULT_PILOT / "summary.json")
    config = read_json(DEFAULT_CONFIG)
    require(metadata["config"] == config and metadata["config_sha256"] == PILOT_CONFIG_SHA,
            "Pilot configuration provenance mismatch")
    require(metadata["code_revision"] == PILOT_REVISION, "Pilot code revision mismatch")
    require(metadata["docker_image_id"] == EXPECTED_IMAGE_ID, "Pilot Docker image mismatch")
    require(metadata["run_type"] == "e003_preference_candidate_pilot"
            and summary["run_type"] == "e003_preference_candidate_pilot", "Wrong pilot run type")
    require(summary["code_revision"] == PILOT_REVISION, "Pilot summary revision mismatch")
    require(summary["config_sha256"] == PILOT_CONFIG_SHA, "Pilot summary config mismatch")
    require(metadata["reference_policy_adapter_sha256"] == ADAPTER_SHA
            and summary["reference_policy_adapter_sha256"] == ADAPTER_SHA,
            "Pilot adapter provenance mismatch")
    require(metadata["training_only"] is True and summary["official_test_used"] is False
            and summary["training_performed"] is False, "Pilot is not strictly generation-only training data")
    require(config["model_id"] == MODEL_ID and config["model_revision"] == MODEL_REVISION
            and config["adapter_sha256"] == ADAPTER_SHA, "Pilot model provenance mismatch")
    require(config["source_sha256"] == SOURCE_SHA and config["manifest_sha256"] == SPLIT_SHA,
            "Pilot split provenance mismatch")
    require(config["split"] == "training" and config["expected_training_questions"] == 6726,
            "Wrong data split")
    require(config["generation"] == {
        "do_sample": True, "temperature": 0.8, "top_p": 0.95,
        "max_new_tokens": 256, "use_cache": True, "attn_implementation": "eager",
        "eos_token_id": NATIVE_EOS, "pad_token_id": NATIVE_EOS, "stop_strings": [],
    }, "Pilot generation protocol mismatch")
    require(config["seed"] == 42 and config["pilot_questions"] == 32
            and config["samples_per_question"] == 4, "Pilot selection config mismatch")

    # Model-free CPU run, but use the pinned tokenizer for exact token/text checks.
    from transformers import AutoTokenizer
    from llm_post_training.data.loader import load_gsm8k_split
    from llm_post_training.evaluation.metrics import evaluate_response
    from llm_post_training.evaluation.prompting import format_baseline_prompt

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, local_files_only=True
    )
    require(tokenizer.eos_token_id == TOKENIZER_EOS
            and tokenizer.pad_token_id == NATIVE_EOS, "Unexpected tokenizer EOS/PAD")
    train = load_gsm8k_split(SOURCE, SPLIT, "training")
    valid = load_gsm8k_split(SOURCE, SPLIT, "validation")
    require(len(train) == 6726 and len(valid) == 747, "Frozen split size mismatch")
    training_by_index = {e.source_index: e for e in train}
    require(len(training_by_index) == len(train)
            and not (set(training_by_index) & {e.source_index for e in valid}), "Training/validation overlap")

    records = read_jsonl(DEFAULT_PILOT / "candidates.jsonl")
    require(len(records) == 128 and summary["candidates"] == 128, "Unexpected candidate count")
    ids = [(r["source_index"], r["sample_index"]) for r in records]
    require(len(set(ids)) == 128, "Duplicate candidate ID")
    selected = metadata["selected_source_indices"]
    require(len(selected) == 32 and len(set(selected)) == 32, "Bad selected indices")
    require({r["source_index"] for r in records} == set(selected), "Candidate source-index mismatch")
    require(set(selected).issubset(training_by_index), "Validation or unknown examples in candidate data")
    for record in records:
        example = training_by_index[record["source_index"]]
        audit_candidate(
            record, format_baseline_prompt(example.question), str(example.reference_answer),
            256, config["seed"], tokenizer, evaluate_response,
        )
    require(sum(r["eligible"] for r in records) == summary["eligible_candidates"] == 127,
            "Eligible count differs from summary")
    require(sum(r["eligible"] and r["correct"] for r in records)
            == summary["correct_eligible_candidates"] == 53, "Correct-eligible count mismatch")
    require(sum(r["native_eos_stop"] for r in records) == summary["native_eos_stops"] == 127,
            "EOS stops mismatch")
    require(sum(r["reached_token_cap"] for r in records) == summary["token_caps"] == 1,
            "Cap count mismatch")
    pairs = select_pairs(review, records)
    for pair in pairs:
        # The prompt is tokenized without special tokens, exactly as in generation.
        prompt_ids = tokenizer(pair["prompt"], add_special_tokens=False)["input_ids"]
        require(len(prompt_ids) > 0, "Empty tokenized prompt")
        pair["prompt_token_ids"] = prompt_ids
        pair["chosen_full_token_ids"] = prompt_ids + pair["chosen_generated_token_ids"]
        pair["rejected_full_token_ids"] = prompt_ids + pair["rejected_generated_token_ids"]

    # Perform every read-only integrity check before creating a new directory.
    args.output_dir.mkdir(parents=True, exist_ok=False)
    pairs_path = args.output_dir / "pairs.jsonl"
    with pairs_path.open("x", encoding="utf-8") as out:
        for pair in pairs:
            out.write(json.dumps(pair, sort_keys=True, ensure_ascii=False) + "\n")
        out.flush()
        os.fsync(out.fileno())
    gap_list = [r["length_gap_tokens"] for r in pairs]
    from statistics import median
    manifest = {
        "schema": "e003_provisional_pilot_pairs_v1",
        "run_type": "cpu_only_provisional_pair_materialization",
        "builder_code_revision": args.code_revision,
        "pilot_code_revision": PILOT_REVISION,
        "pilot_config_sha256": PILOT_CONFIG_SHA,
        "pilot_metadata_sha256": file_sha256(DEFAULT_PILOT / "metadata.json"),
        "pilot_summary_sha256": file_sha256(DEFAULT_PILOT / "summary.json"),
        "pilot_candidates_sha256": file_sha256(DEFAULT_PILOT / "candidates.jsonl"),
        "screening_review_sha256": REVIEW_SHA,
        "source_sha256": SOURCE_SHA,
        "split_manifest_sha256": SPLIT_SHA,
        "adapter_sha256": ADAPTER_SHA,
        "model_revision": MODEL_REVISION,
        "eos_token_id": NATIVE_EOS,
        "kv_cache_during_original_generation": True,
        "pair_count": len(pairs),
        "held_groups": 1,
        "excluded_groups": 2,
        "median_pair_length_gap_tokens": median(gap_list),
        "max_pair_length_gap_tokens": max(gap_list),
        "pairs_jsonl_sha256": file_sha256(pairs_path),
        "independent_human_signoff": False,
        "training_approved": False,
        "training_performed": False,
        "official_test_used": False,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print("=== E003 PROVISIONAL PAIR BUILDER ===")
    print(f"Pairs: {len(pairs)}")
    print(f"Median length gap: {manifest['median_pair_length_gap_tokens']}")
    print(f"Max length gap: {manifest['max_pair_length_gap_tokens']}")
    print(f"Pairs SHA256: {manifest['pairs_jsonl_sha256']}")
    print(f"Output directory: {args.output_dir}")
    print("Independent signoff: REQUIRED; Training: NOT AUTHORIZED")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--code-revision", required=True)
    args = p.parse_args()
    build(args)


if __name__ == "__main__":
    main()
