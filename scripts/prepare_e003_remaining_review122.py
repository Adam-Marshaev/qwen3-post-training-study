"""M3.15: deterministic, read-only preparation of seven E003 reasoning-review batches.

Consumes only pinned GSM8K TRAIN split, frozen E003 candidate file, and review
manifests. No regrading, pair selection, model inference, or training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

VERSION = "e003_remaining_review122_v1"
BATCH_SIZE = 20
SOURCE_SHA = "17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465"
SPLIT_SHA = "31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719"
CANDIDATE_SHA = "3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4"
SCREEN_SHA = "90d832c8cfb01c9d7d29c7e7b44563fb0616184f22a48ba42bc42ead08a07f36"
PAIR_APPROVAL_SHA = "cb66fb12aae28eaac87a4dd0bdb0d32caab2d3fde19ebdd05506c34becec1705"
ADAPTER_SHA = "f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625"
GENERATOR_REV = "ab39e3bab29a9a3115e6ec754086187092dcf89e"
NATIVE_EOS = 151643
FIRST_BATCH = [81, 144, 158, 303, 376, 434, 468, 485, 528, 552,
               557, 755, 815, 853, 1150, 1219, 1293, 1357, 1429, 1438]
LAST_BATCH = [7304, 7340]


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError(detail)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    text = path.read_text(encoding="utf-8")
    require(text.endswith("\n"), f"Unterminated JSONL: {path}")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def validate_record(record: dict, example, prompt_fn) -> None:
    source = example.source_index
    sample = record.get("sample_index")
    require(type(sample) is int and 0 <= sample < 4, "Invalid sample index")
    require(record.get("source_index") == source, "Wrong source index")
    require(record.get("sample_seed") == 42 + source * 100 + sample, "Sample seed mismatch")
    require(record.get("prompt") == prompt_fn(example.question), "Original prompt mismatch")
    require(record.get("reference_answer") == str(example.reference_answer), "Original reference mismatch")
    ids = record.get("generated_token_ids")
    require(isinstance(ids, list) and 1 <= len(ids) <= 256 and
            all(type(token) is int and token >= 0 for token in ids), "Generated token IDs invalid")
    require(record.get("generated_tokens") == len(ids), "Generated token count mismatch")
    require(record.get("native_eos_stop") is (ids[-1] == NATIVE_EOS), "Native EOS mismatch")
    require(record.get("reached_token_cap") is (len(ids) == 256), "Token cap mismatch")
    require(type(record.get("eligible")) is bool and type(record.get("correct")) is bool,
            "Candidate eligibility/correctness flags invalid")
    require(type(record.get("response")) is str and record["response"], "Empty/non-string response")
    require(record.get("extracted_answer") is None or
            type(record["extracted_answer"]) is str, "Extracted answer type invalid")


def is_mixed(rows: list[dict]) -> bool:
    return (any(row["eligible"] and row["correct"] for row in rows)
            and any(row["eligible"] and not row["correct"] for row in rows))


def choose_remaining(groups: dict, reviewed: list[int]) -> list[int]:
    mixed = {index for index, rows in groups.items() if is_mixed(rows)}
    require(len(mixed) == 146, "Mixed group count differs from frozen E003 summary")
    require(len(reviewed) == 24 and len(set(reviewed)) == 24, "Reviewed indices invalid")
    require(set(reviewed).issubset(mixed), "Reviewed sample is not contained in mixed groups")
    remaining = sorted(mixed - set(reviewed))
    require(len(remaining) == 122, "Remaining group count differs from inventory")
    require(remaining[:20] == FIRST_BATCH, "First batch differs from M3.14 inventory")
    require(remaining[-2:] == LAST_BATCH, "Last batch differs from M3.14 inventory")
    return remaining


def partition(indices: list[int], size: int = BATCH_SIZE) -> list[list[int]]:
    require(size > 0, "Batch size must be positive")
    return [indices[position:position + size]
            for position in range(0, len(indices), size)]


def render_review(batch_number: int, indices: list[int], examples: dict, groups: dict) -> str:
    lines = [
        "E003 REMAINING MIXED-GROUP REASONING REVIEW",
        f"Protocol: {VERSION}",
        f"Batch number: {batch_number:02d}",
        f"Frozen candidate SHA256: {CANDIDATE_SHA}",
        "Population: 122 previously unreviewed mixed groups",
        f"Questions in this batch: {len(indices)}",
        "Original candidate responses and answer labels are UNMODIFIED.",
        "These are candidate-level ORIGINAL reference labels; no erratum is applied.",
        "Review status: UNREVIEWED; no pair is approved for training.",
        "=" * 78,
    ]
    for source in indices:
        example = examples[source]
        rows = sorted(groups[source], key=lambda row: row["sample_index"])
        lines.extend(["", "=" * 78, f"SOURCE INDEX: {source}", "=" * 78, "",
                      "QUESTION:", example.question, "", "ORIGINAL REFERENCE ANSWER:",
                      str(example.reference_answer)])
        for row in rows:
            lines.extend(["", "-" * 66, f"SAMPLE: {row['sample_index']}",
                          f"ORIGINAL CORRECT FINAL ANSWER: {row['correct']}",
                          f"ELIGIBLE: {row['eligible']}",
                          f"GENERATED TOKENS: {row['generated_tokens']}",
                          f"NATIVE EOS: {row['native_eos_stop']}",
                          f"EXTRACTED ANSWER: {row['extracted_answer']}",
                          "", "COMPLETE ORIGINAL REASONING:", row["response"]])
        lines.extend(["", "REASONING-QUALITY SCREEN (NOT YET PERFORMED):",
                      "Sound chosen sample(s): ______", "Reasoning errors: ______",
                      "Possible rejected sample(s): ______",
                      "Recommendation: APPROVE / HOLD / EXCLUDE", ""])
    lines.extend(["=" * 78, "END OF BATCH", ""])
    return "\n".join(lines)


def load_and_verify(root: Path):
    from llm_post_training.data.loader import load_gsm8k_split
    from llm_post_training.evaluation.prompting import format_baseline_prompt

    input_files = {
        "raw_training_source": ("data/raw/gsm8k/train.jsonl", SOURCE_SHA),
        "frozen_split": ("configs/data/gsm8k_split_v1.json", SPLIT_SHA),
        "candidates": ("data/preference_runs/e003_scale256_k4_v1/candidates.jsonl", CANDIDATE_SHA),
        "screen24": ("configs/preference/e003_scale256_reasoning_screen24_advisory_v1.json", SCREEN_SHA),
        "source5436_pair_approval": ("configs/preference/e003_source5436_pair_approval_v1.json", PAIR_APPROVAL_SHA),
    }
    for label, (relative, expected) in input_files.items():
        require(sha256_file(root / relative) == expected, f"Input checksum mismatch: {label}")

    screen = read_json(root / input_files["screen24"][0])
    require(screen["schema"] == "e003_scale256_reasoning_screen24_advisory_v1", "Screen schema mismatch")
    require(screen["original_candidate_dataset_sha256"] == CANDIDATE_SHA, "Screen input mismatch")
    require(screen["classification"] == "advisory_only_not_frozen_training_dataset", "Screen status mismatch")
    require(screen["training_approved"] is False, "Screen unexpectedly training-approved")
    require(screen["official_test_used"] is False, "Screen unexpectedly used test")
    require(screen["population_mixed_groups"] == 146, "Screen mixed count mismatch")

    approval = read_json(root / input_files["source5436_pair_approval"][0])
    require(approval["schema"] == "e003_source5436_pair_approval_v1" and
            approval["source_index"] == 5436 and
            approval["chosen_sample_index"] == 2 and
            approval["rejected_sample_index"] == 0 and
            approval["flags"]["dpo_training_approved"] is False, "Pair approval mismatch")

    metadata = read_json(root / "data/preference_runs/e003_scale256_k4_v1/metadata.json")
    summary = read_json(root / "data/preference_runs/e003_scale256_k4_v1/summary.json")
    require(metadata["training_only"] is True and
            metadata["official_test_used"] is False and metadata["training_performed"] is False,
            "Generation metadata flags invalid")
    require(metadata["code_revision"] == GENERATOR_REV and
            summary["code_revision"] == GENERATOR_REV and
            summary["candidates_sha256"] == CANDIDATE_SHA and
            summary["candidates"] == 1024 and summary["scale_questions"] == 256 and
            summary["mixed_groups_with_potential_pair"] == 146 and
            summary["reference_policy_adapter_sha256"] == ADAPTER_SHA and
            summary["training_performed"] is False and summary["official_test_used"] is False,
            "Generation summary provenance mismatch")

    training = load_gsm8k_split(root / input_files["raw_training_source"][0],
                                root / input_files["frozen_split"][0], "training")
    examples = {row.source_index: row for row in training}
    require(len(training) == len(examples) == 6726, "Training split count invalid")
    records = read_jsonl(root / input_files["candidates"][0])
    require(len(records) == 1024, "Candidate count invalid")
    groups = defaultdict(list)
    for row in records:
        source = row.get("source_index")
        require(source in examples, "Candidate outside frozen training partition")
        validate_record(row, examples[source], format_baseline_prompt)
        groups[source].append(row)
    require(len(groups) == 256, "Generated group count invalid")
    require(set(groups) == set(metadata["selected_source_indices"]), "Selected question mismatch")
    for source, rows in groups.items():
        require(len(rows) == 4 and sorted(row["sample_index"] for row in rows) == [0, 1, 2, 3],
                f"Group incomplete/duplicate: {source}")
    remaining = choose_remaining(groups, screen["source_index_order"])
    require(not set(remaining).intersection(screen["source_index_order"]), "Prior review overlap")
    require(5436 not in remaining and 744 not in remaining and 2320 not in remaining,
            "Adjudicated group appears in remaining inventory")
    return examples, groups, remaining, input_files


def prepare(root: Path, output_dir: Path, code_revision: str, preflight_only: bool):
    root = root.resolve()
    output_dir = output_dir.resolve()
    require(len(code_revision) == 40 and all(c in "0123456789abcdef" for c in code_revision),
            "Git revision must be 40 lowercase hex digits")
    repo_revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                             text=True).strip()
    require(repo_revision == code_revision, "Code revision does not match checked-out Git HEAD")
    examples, groups, remaining, inputs = load_and_verify(root)
    batches = partition(remaining)
    require([len(batch) for batch in batches] == [20, 20, 20, 20, 20, 20, 2],
            "Unexpected batch partition")
    entries = []
    payloads: dict[str, bytes] = {}
    for index, indices in enumerate(batches):
        report_name = f"batch_{index:02d}_review.txt"
        selection_name = f"batch_{index:02d}_selection.json"
        report = render_review(index, indices, examples, groups).encode("utf-8")
        selection = {
            "schema": f"{VERSION}_batch_selection",
            "batch_number": index,
            "selected_source_indices": indices,
            "source_count": len(indices),
            "candidate_count": 4 * len(indices),
            "candidate_dataset_sha256": CANDIDATE_SHA,
            "review_status": "UNREVIEWED",
            "independent_pair_signoff": False,
            "training_approved": False,
            "training_performed": False,
            "official_test_used": False,
        }
        selection_data = json_bytes(selection)
        payloads[report_name] = report
        payloads[selection_name] = selection_data
        entries.append({"batch_number": index, "source_indices": indices,
                        "review_file": report_name, "review_sha256": sha256_bytes(report),
                        "selection_file": selection_name,
                        "selection_sha256": sha256_bytes(selection_data)})
    manifest = {
        "schema": VERSION,
        "code_revision": code_revision,
        "preparation_script_sha256": sha256_file(Path(__file__)),
        "population_mixed_groups": 146,
        "previously_reviewed_groups": 24,
        "remaining_groups": 122,
        "remaining_candidates": 488,
        "batch_size": BATCH_SIZE,
        "batches": entries,
        "remaining_source_indices": remaining,
        "input_provenance": {key: {"path": path, "sha256": checksum}
                             for key, (path, checksum) in inputs.items()},
        "flags": {"training_only": True, "review_unperformed": True,
                  "independent_pair_signoff": False, "pair_selection_performed": False,
                  "training_approved": False, "training_performed": False,
                  "official_test_used": False, "original_candidates_modified": False},
    }
    payloads["manifest.json"] = json_bytes(manifest)
    print("=== E003 M3.15 REVIEW BATCH PREPARATION ===")
    print("Mixed groups: 146 | Previously reviewed: 24 | Remaining: 122")
    print("Original completions to screen: 488 | Batches: 7 (20,20,20,20,20,20,2)")
    print("Original candidate SHA256: VERIFIED")
    print("Batch 00 indices:", batches[0])
    print("Last batch indices:", batches[-1])
    if preflight_only:
        print("PRE-FLIGHT PASSED; NO OUTPUT WRITTEN; NO GPU OR TRAINING")
        return
    require(not output_dir.exists(), f"Refusing to overwrite existing directory: {output_dir}")
    require(output_dir.parent.is_dir(), "Output parent is missing")
    with tempfile.TemporaryDirectory(prefix=f".{output_dir.name}.pending_", dir=output_dir.parent) as tmp:
        staging = Path(tmp)
        for name, content in payloads.items():
            (staging / name).write_bytes(content)
        require(all(sha256_file(staging / name) == sha256_bytes(content)
                    for name, content in payloads.items()), "Staging data verification failed")
        require(not output_dir.exists(), "Destination created concurrently")
        staging.rename(output_dir)
    print("Output:", output_dir)
    print("Master manifest SHA256:", sha256_file(output_dir / "manifest.json"))
    print("No original files modified; no pair selection; no training authorized")
    print("E003 M3.15 REVIEW BATCH PREPARATION: PASSED")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    prepare(args.repo_root, args.output_dir, args.code_revision, args.preflight_only)


if __name__ == "__main__":
    main()
