"""CPU-only E003 source-5436 reference-erratum regrading; NEVER trains.

The original 1,024 candidates, raw GSM8K, and frozen split are read only.
Produces four source-specific provenance-carrying derivative rows and a manifest.
No pair selection or approval is performed.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from decimal import Decimal
from pathlib import Path

SOURCE = 5436
ORIGINAL = "55"
CORRECTED = "50"
SCHEMA = "e003_reference_erratum_regrade_v1"
APPROVAL_SHA = "a031184e0abaaa345bc38adbb794f4521c7e60ac5eb51c5acba7d55a14143f69"
PROPOSAL_SHA = "c547546d5008ec7b8320edf9171263adbbf5fed66e92ed6b1aff0a4dfa194d2c"
ADJUDICATION_SHA = "23886515468df3c4d00f079d744b8eb62224d7d0f97820a665e06feb4adeb3e2"
CANDIDATE_SHA = "3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4"
SOURCE_SHA = "17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465"
SPLIT_SHA = "31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719"
GENERATOR_REV = "ab39e3bab29a9a3115e6ec754086187092dcf89e"
CONFIG_SHA = "102bcdea4c6af29dbc5b6cbdb5b0f28ad2a4892f5d3f93b9c2b8d331f4762d14"
APPROVAL_PARENT_REV = "78ef9440573f1714f78bb9c9d59d042dbb4526eb"

INPUTS = {
    "approval": ("configs/preference/e003_training_reference_erratum_approval_v1.json", APPROVAL_SHA),
    "proposal": ("configs/preference/e003_training_reference_erratum_proposal_v1.json", PROPOSAL_SHA),
    "adjudication": ("configs/preference/e003_scale256_independent_adjudication3_v1.json", ADJUDICATION_SHA),
    "candidates": ("data/preference_runs/e003_scale256_k4_v1/candidates.jsonl", CANDIDATE_SHA),
    "raw_gsm8k": ("data/raw/gsm8k/train.jsonl", SOURCE_SHA),
    "split_manifest": ("configs/data/gsm8k_split_v1.json", SPLIT_SHA),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        require(bool(line.strip()), f"Unexpected blank JSONL line {number}")
        rows.append(json.loads(line))
    return rows


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def canonical_jsonl(rows):
    return "".join(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)


def check_input_provenance(root):
    for name, (relative_path, expected_sha) in INPUTS.items():
        file_path = root / relative_path
        require(file_path.is_file(), f"Missing {name}: {relative_path}")
        require(sha256_file(file_path) == expected_sha, f"Checksum mismatch for {name}: {relative_path}")


def check_approval(approval, proposal, adjudication):
    require(approval.get("schema") == "e003_training_reference_erratum_approval_v1", "Approval schema mismatch")
    require(approval.get("decision") == "APPROVED", "Reference correction not approved")
    require(approval.get("decision_authority") == "project_owner", "Approval authority mismatch")
    require(approval.get("scope") == "E003_training_derived_preference_labels_only", "Approval scope mismatch")
    require(approval.get("source_index") == SOURCE, "Approval source mismatch")
    require(approval.get("original_reference_answer") == ORIGINAL, "Original reference mismatch")
    require(approval.get("approved_reference_answer") == CORRECTED, "Corrected reference mismatch")
    provenance = approval.get("provenance", {})
    require(provenance.get("proposal_sha256") == PROPOSAL_SHA, "Approval/proposal mismatch")
    require(provenance.get("adjudication_sha256") == ADJUDICATION_SHA, "Approval/adjudication mismatch")
    require(provenance.get("candidate_dataset_sha256") == CANDIDATE_SHA, "Approval/candidates mismatch")
    require(provenance.get("approval_parent_revision") == APPROVAL_PARENT_REV, "Approval parent revision mismatch")
    authorized = approval.get("authorized_actions", {})
    require(authorized.get("training_only_reference_override") is True and
            authorized.get("versioned_derivative_regrading") is True and
            authorized.get("preserve_original_candidate_labels") is True and
            authorized.get("preserve_original_generated_tokens") is True,
            "Missing required permissions or preservation commitments")
    prohibited = approval.get("prohibited_actions", {})
    require(all(prohibited.get(x) is True for x in (
        "modify_original_gsm8k", "modify_frozen_split", "modify_original_candidates",
        "modify_validation_references", "use_official_test_set")), "Source preservation restrictions missing")
    status = approval.get("status", {})
    require(status.get("reference_correction_approved") is True and
            status.get("reference_correction_implemented") is False and
            status.get("derivative_regrading_performed") is False and
            status.get("source_5436_pair_approved") is False and
            status.get("full_training_dataset_approved") is False and
            status.get("dpo_training_approved") is False and
            status.get("training_performed") is False, "Approval status mismatch")
    require(proposal.get("source_index") == SOURCE and
            proposal.get("original_reference_answer") == ORIGINAL and
            proposal.get("proposed_reference_answer") == CORRECTED and
            proposal.get("status") == "PROPOSED_NOT_APPROVED", "Proposal mismatch")
    decisions = {d["source_index"]: d for d in adjudication["decisions"]}
    require(set(decisions) == {744, 2320, SOURCE}, "Adjudication scope mismatch")
    require(decisions[SOURCE].get("user_adjudication") ==
            "HOLD_FOR_REFERENCE_CORRECTION_ELSE_EXCLUDE", "Adjudication decision mismatch")
    return True


def check_generation_metadata(metadata, summary):
    require(metadata.get("training_only") is True and metadata.get("training_performed") is False and
            metadata.get("official_test_used") is False, "Generation metadata permissions mismatch")
    require(metadata.get("code_revision") == GENERATOR_REV and
            metadata.get("config_sha256") == CONFIG_SHA, "Generator version mismatch")
    require(metadata.get("reference_policy_adapter_sha256") ==
            "f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625",
            "Adapter mismatch")
    require(SOURCE in metadata.get("selected_source_indices", []), "Source not in selected train questions")
    require(SOURCE not in metadata.get("excluded_pilot_source_indices", []), "Pilot source overlap")
    require(summary.get("candidates_sha256") == CANDIDATE_SHA and
            summary.get("candidates") == 1024 and
            summary.get("scale_questions") == 256 and
            summary.get("official_test_used") is False and
            summary.get("training_performed") is False, "Generation summary mismatch")


def choose_source_records(rows):
    require(len(rows) == 1024, "Expected complete original 1024-candidate dataset")
    require(len({(r["source_index"], r["sample_index"]) for r in rows}) == 1024,
            "Duplicate candidate identifiers in source dataset")
    source_rows = sorted((r for r in rows if r["source_index"] == SOURCE),
                         key=lambda r: r["sample_index"])
    require(len(source_rows) == 4, "Exactly four source 5436 records required")
    require([r["sample_index"] for r in source_rows] == [0, 1, 2, 3],
            "Missing or duplicate source 5436 sample index")
    return source_rows


def candidate_is_eligible(row):
    return (row["native_eos_stop"] is True and
            row["reached_token_cap"] is False and
            row["extraction_status"] == "valid" and
            row["unwanted_continuation"] is False and
            "the answer is" in row["response"].lower())


def build_derivative(source_rows, expected_prompt, grader):
    """Immutable original-candidate record plus newly graded reference overlay.

    `grader` must implement evaluation.metrics.evaluate_response. Tests inject a
    small deterministic fake; actual execution regrades with the pinned grader.
    """
    require([r["sample_index"] for r in source_rows] == [0, 1, 2, 3], "Incorrect source samples")
    expected_answers = ["55", "55", "50", "55"]
    expected_original = [True, True, False, True]
    expected_corrected = [False, False, True, False]
    derived = []
    for sample, row in enumerate(source_rows):
        require(row["source_index"] == SOURCE and type(row["sample_index"]) is int and
                row["sample_index"] == sample, "Incorrect candidate identity")
        require(row["sample_seed"] == 42 + SOURCE * 100 + sample, "Generation seed mismatch")
        require(row["prompt"] == expected_prompt, "Original candidate prompt mismatch")
        require(row["reference_answer"] == ORIGINAL, "Original reference mismatch")
        ids = row["generated_token_ids"]
        require(type(ids) is list and 1 <= len(ids) <= 256 and
                all(type(tok) is int and tok >= 0 for tok in ids), "Invalid original tokens")
        require(row["generated_tokens"] == len(ids), "Generated token count mismatch")
        require(ids[-1] == 151643 and row["native_eos_stop"] is True,
                "Expected EOS-terminated candidate")
        require(row["reached_token_cap"] is False, "Unexpected token-cap candidate")
        require(row["eligible"] is True and candidate_is_eligible(row),
                "Candidate not eligible under frozen grading protocol")
        require(row["extracted_answer"] == expected_answers[sample],
                "Unexpected original extracted answer")
        old_judgment = grader(
            response=row["response"], expected_answer=Decimal(ORIGINAL),
            generated_tokens=len(ids), reached_token_cap=False,
        )
        new_judgment = grader(
            response=row["response"], expected_answer=Decimal(CORRECTED),
            generated_tokens=len(ids), reached_token_cap=False,
        )
        require(type(row["correct"]) is bool and row["correct"] == expected_original[sample] and
                row["correct"] == bool(old_judgment.correct), "Original correctness audit failed")
        for judged in (old_judgment, new_judgment):
            require(judged.extraction.status == row["extraction_status"] and
                    (str(judged.extraction.answer) if judged.extraction.answer is not None else None) ==
                    row["extracted_answer"] and
                    bool(judged.extraction.unwanted_continuation) is row["unwanted_continuation"],
                    "Original extraction changed during independent regrading")
        require(bool(new_judgment.correct) == expected_corrected[sample],
                "Corrected-answer judgment mismatch")
        derived.append({
            "source_index": SOURCE,
            "sample_index": sample,
            "original_candidate": row,
            "approved_training_only_reference_answer": CORRECTED,
            "corrected_correct": bool(new_judgment.correct),
            "pair_approved": False,
            "training_approved": False,
        })
    require(sum(rec["corrected_correct"] for rec in derived) == 1,
            "Expected exactly one candidate to match corrected answer")
    return derived


def create_manifest(rows, approval, script_sha, revision, jsonl_sha):
    return {
        "schema": SCHEMA,
        "run_type": "source_specific_training_reference_regrade_only",
        "source_index": SOURCE,
        "original_reference_answer": ORIGINAL,
        "approved_training_only_reference_answer": CORRECTED,
        "candidate_count": 4,
        "original_correct_count": sum(r["original_candidate"]["correct"] for r in rows),
        "corrected_correct_count": sum(r["corrected_correct"] for r in rows),
        "corrected_chosen_candidate_if_separately_approved": 2,
        "advisory_potential_rejected_samples": [0, 1, 3],
        "pair_selection_performed": False,
        "inputs": {name: {"path": path, "sha256": digest} for name, (path, digest) in INPUTS.items()},
        "approval_decision": approval["decision"],
        "approval_scope": approval["scope"],
        "regrading_script_sha256": script_sha,
        "regrading_code_revision": revision,
        "derived_candidates_jsonl_sha256": jsonl_sha,
        "flags": {
            "reference_correction_approved": True,
            "derived_regrading_performed": True,
            "original_source_modified": False,
            "original_candidates_modified": False,
            "reference_regrade_scoped_to_E003_training_only": True,
            "source_5436_pair_approved": False,
            "independent_pair_signoff": False,
            "full_training_dataset_approved": False,
            "dpo_training_approved": False,
            "training_performed": False,
            "official_test_used": False,
        },
    }


def atomic_publish(output_dir, files):
    """Write all files to a sibling temp dir, rename only on complete success."""
    output_dir = Path(output_dir)
    require(output_dir.parent.is_dir(), "Output parent must exist")
    require(not output_dir.exists(), "Refusing to overwrite existing output directory")
    temporary = Path(tempfile.mkdtemp(prefix=".e003_erratum_pending_", dir=output_dir.parent))
    try:
        for name, text in files.items():
            p = temporary / name
            with p.open("x", encoding="utf-8") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
        require(not output_dir.exists(), "Output directory appeared concurrently")
        temporary.rename(output_dir)
        dirfd = os.open(output_dir.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def run(root, output_dir, code_revision, preflight_only=False):
    require(re.fullmatch(r"[0-9a-f]{40}", code_revision) is not None,
            "Code revision must be a full Git SHA")
    root = Path(root)
    check_input_provenance(root)
    approval = read_json(root / INPUTS["approval"][0])
    proposal = read_json(root / INPUTS["proposal"][0])
    adjudication = read_json(root / INPUTS["adjudication"][0])
    check_approval(approval, proposal, adjudication)
    run_dir = root / "data/preference_runs/e003_scale256_k4_v1"
    metadata = read_json(run_dir / "metadata.json")
    summary = read_json(run_dir / "summary.json")
    check_generation_metadata(metadata, summary)
    # Import only after all input checks. This reuses the exact frozen evaluator.
    from llm_post_training.data.loader import load_gsm8k_split
    from llm_post_training.evaluation.metrics import evaluate_response
    from llm_post_training.evaluation.prompting import format_baseline_prompt
    training = load_gsm8k_split(root / INPUTS["raw_gsm8k"][0],
                                root / INPUTS["split_manifest"][0], "training")
    require(len(training) == 6726, "Training partition size mismatch")
    examples = [e for e in training if e.source_index == SOURCE]
    require(len(examples) == 1 and str(examples[0].reference_answer) == ORIGINAL,
            "Source 5436 is not an unmodified training example with reference 55")
    candidates = read_jsonl(root / INPUTS["candidates"][0])
    source_rows = choose_source_records(candidates)
    derivative = build_derivative(source_rows, format_baseline_prompt(examples[0].question),
                                  evaluate_response)
    print("=== E003 REFERENCE ERRATUM REGRADING ===")
    for rec in derivative:
        original = rec["original_candidate"]
        print(f"Sample {rec['sample_index']}: extracted={original['extracted_answer']} "
              f"original_correct={original['correct']} "
              f"corrected_correct={rec['corrected_correct']}")
    jsonl_text = canonical_jsonl(derivative)
    jsonl_sha = sha256_bytes(jsonl_text.encode("utf-8"))
    manifest = create_manifest(derivative, approval, sha256_file(Path(__file__)),
                               code_revision, jsonl_sha)
    require(not Path(output_dir).exists(), "Refusing to overwrite output directory")
    if preflight_only:
        print("Preflight only: NO OUTPUT WRITTEN")
    else:
        atomic_publish(output_dir, {
            "regraded_candidates.jsonl": jsonl_text,
            "manifest.json": canonical_json(manifest),
        })
        require(sha256_file(Path(output_dir) / "regraded_candidates.jsonl") == jsonl_sha,
                "Post-write candidate checksum mismatch")
        print(f"Output: {output_dir}")
        print(f"Derived candidates SHA256: {jsonl_sha}")
    print("Original data modified: NO; Pair approval: NO; DPO training: NOT AUTHORIZED")
    print("E003 ERRATUM REGRADING: PASSED")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    run(args.repo_root, args.output_dir, args.code_revision, args.preflight_only)


if __name__ == "__main__":
    main()
