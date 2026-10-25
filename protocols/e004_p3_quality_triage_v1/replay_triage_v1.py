#!/usr/bin/env python3
"""Read-only byte-exact replay of frozen E004-P3 provisional triage."""

import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path.cwd()

REV = "a8f8795f02d8f5a8e027bc4e4319bdf057d4d938"
P3_SHA = "7825edfec54b26427fa48876c087dc75ab53d38a6bd85cee54d8b6b207b10ed1"
SCREEN_SHA = "c74e1f84126b486ba47a7697d2f0e38f2221750758450a24edb188fdc38f7dd5"
TRIAGE_SHA = "f67c32d754ff33a4418e9a92cbfa5fe0424cb684d9f1d5efa0984f8c310764fa"

P3 = ROOT / "data/preference_runs/e004_p3_1200_k4_331499d_v1"
SCR = ROOT / "data/preference_runs/e004_p3_arithmetic_first_screen_v1"
OUT = ROOT / "data/preference_runs/e004_p3_quality_triage_v1"

HOLDS = {
    3115: "Incorrect intermediate bean color categories",
    4201: "Unsupported quarter-by-quarter scoring relationships",
}

REFERENCE_FLAG = 1958


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path, expected=None):
    require(
        path.is_file() and not path.is_symlink(),
        f"Missing or unsafe file: {path}",
    )

    data = path.read_bytes()

    if expected:
        require(sha(data) == expected, f"SHA mismatch: {path}")

    return data


def jsonl(data):
    return [
        json.loads(line)
        for line in data.splitlines()
        if line.strip()
    ]


def encode_jsonl(records):
    return "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
        for r in records
    ).encode()


def encode_json(obj):
    return (
        json.dumps(
            obj,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
    ).encode()


def by_source(path):
    records = {}

    for record in jsonl(read(path)):
        index = record["source_index"]

        require(
            type(index) is int and index not in records,
            f"Invalid or duplicate source: {index}",
        )

        records[index] = record

    return records


print("=== VERIFY FROZEN SOURCE PROVENANCE ===")

require(
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", REV, "HEAD"]
    ).returncode == 0,
    "Frozen generator revision is not in Git history",
)

candidates = jsonl(read(P3 / "candidates.jsonl", P3_SHA))

manifest = json.loads(
    read(SCR / "manifest.json", SCREEN_SHA)
)

require(
    manifest["original_candidates_sha256"] == P3_SHA
    and manifest["source_git_revision"] == REV
    and manifest["approved_training_pairs"] == 0
    and manifest["training_performed"] is False,
    "Screening provenance mismatch",
)

require(len(manifest["files"]) == 8, "Unexpected manifest")

for name, expected in manifest["files"].items():
    relative = Path(name)

    require(
        not relative.is_absolute()
        and ".." not in relative.parts,
        "Unsafe manifest path",
    )

    read(SCR / relative, expected)

summary = json.loads(read(SCR / "outputs/summary.json"))

require(
    (
        summary["mixed_groups"],
        summary["mechanical_pass_groups"],
        summary["mechanical_reject_groups"],
        summary["approved_training_pairs"],
    ) == (641, 425, 216, 0),
    "Unexpected screening counts",
)

require(
    summary["semantics_verified"] is False,
    "Unexpected semantic certification",
)

print("Frozen source artifacts: VERIFIED")


print("\n=== RECONSTRUCT ORIGINAL CANDIDATE IDENTITIES ===")

original = defaultdict(dict)

for record in candidates:
    source = record["source_index"]
    sample = record["sample_index"]

    require(
        type(source) is int
        and type(sample) is int
        and 0 <= sample < 4
        and sample not in original[source],
        "Invalid or duplicate candidate",
    )

    original[source][sample] = record

require(
    len(candidates) == 4800
    and len(original) == 1200
    and all(set(v) == set(range(4)) for v in original.values()),
    "Original candidate set mismatch",
)

groups = by_source(SCR / "inputs/mixed641.jsonl")
decisions = by_source(SCR / "outputs/mechanical_decisions.jsonl")
shortlist = by_source(
    SCR / "outputs/mechanical_shortlist_semantic_hold.jsonl"
)

require(
    len(groups) == 641
    and len(decisions) == 641
    and len(shortlist) == 425
    and set(groups) == set(decisions)
    and set(shortlist) <= set(groups),
    "Screening group mismatch",
)


print("\n=== REPRODUCE QUALITY TRIAGE IN MEMORY ===")

retained = []
rejected = []
held = []
flags = []
decision_index = []

for source in sorted(groups):
    group = groups[source]
    decision = decisions[source]
    samples = original[source]

    require(
        len(group["responses"]) == 4
        and group["prompt"] == samples[0]["prompt"]
        and group["reference_answer"] == samples[0]["reference_answer"],
        "Group identity mismatch",
    )

    require(
        {r["sample_index"] for r in group["responses"]}
        == set(range(4)),
        "Missing group sample",
    )

    for response in group["responses"]:
        original_response = samples[response["sample_index"]]

        require(
            all(
                original_response.get(k) == v
                for k, v in response.items()
            ),
            "Group response differs from original candidate",
        )

    require(
        any(
            r["eligible"] is True and r["correct"] is True
            for r in samples.values()
        )
        and any(
            r["eligible"] is True and r["correct"] is False
            for r in samples.values()
        ),
        "Non-mixed group encountered",
    )

    pair = decision["top_pair"]

    if pair is None:
        require(
            source not in shortlist,
            "Rejected source appears in shortlist",
        )

        status = "MECHANICAL_REJECT_PRESERVED"

        item = {
            "source_index": source,
            "status": status,
            "mechanical_decision": decision,
            "original_candidates": [samples[i] for i in range(4)],
            "approved_for_training": False,
            "reasoning_independently_verified": False,
        }

        if source == REFERENCE_FLAG:
            item["advisory_flag"] = (
                "POSSIBLE_REFERENCE_INCONSISTENCY"
            )

            flags.append({
                "source_index": source,
                "status": "ADVISORY_REFERENCE_REVIEW",
                "approved_for_training": False,
            })

        rejected.append(item)

    else:
        require(
            source in shortlist and source != REFERENCE_FLAG,
            "Invalid mechanical pass",
        )

        chosen = pair["chosen_sample_index"]
        wrong = pair["rejected_sample_index"]

        require(
            (chosen, wrong) == (
                shortlist[source]["chosen_sample_index"],
                shortlist[source]["rejected_sample_index"],
            ),
            "Pair identity mismatch",
        )

        require(
            chosen != wrong
            and samples[chosen]["eligible"] is True
            and samples[chosen]["correct"] is True
            and samples[wrong]["eligible"] is True
            and samples[wrong]["correct"] is False,
            "Incorrect pair labels",
        )

        status = (
            "KNOWN_ADVISORY_REASONING_HOLD"
            if source in HOLDS
            else "AUTO_SCREENED_PROVISIONAL"
        )

        item = {
            "source_index": source,
            "status": status,
            "chosen_sample_index": chosen,
            "rejected_sample_index": wrong,
            "chosen_candidate": samples[chosen],
            "rejected_candidate": samples[wrong],
            "mechanical_decision": decision,
            "approved_for_training": False,
            "reasoning_independently_verified": False,
            "training_performed": False,
        }

        if source in HOLDS:
            item["advisory_note"] = HOLDS[source]
            held.append(item)
        else:
            retained.append(item)

    decision_index.append({
        "source_index": source,
        "status": status,
        "approved_for_training": False,
    })


require(
    (
        len(retained),
        len(held),
        len(rejected),
        len(flags),
        len(decision_index),
    ) == (423, 2, 216, 1, 641),
    "Reconstructed partition mismatch",
)

require(
    {r["source_index"] for r in held} == set(HOLDS),
    "Expected reasoning holds missing",
)

require(
    flags[0]["source_index"] == REFERENCE_FLAG,
    "Expected reference flag missing",
)


report = {
    "schema": "e004_p3_quality_triage_inline_v1",
    "source_git_revision": REV,
    "original_candidates_sha256": P3_SHA,
    "screen_manifest_sha256": SCREEN_SHA,
    "mixed_groups": 641,
    "mechanical_pass_groups": 425,
    "auto_retained_provisional": 423,
    "known_reasoning_holds": 2,
    "mechanical_rejects_preserved": 216,
    "reference_adjudication_flags": 1,
    "p1_p2_provisional": 163,
    "combined_provisional_after_holds": 586,
    "independent_reasoning_certification": False,
    "approved_training_pairs": 0,
    "official_test_used": False,
    "training_performed": False,
    "gpu_inference": False,
}

outputs = {
    "outputs/auto_retained_provisional_423.jsonl":
        encode_jsonl(retained),

    "outputs/mechanical_rejects_preserved_216.jsonl":
        encode_jsonl(rejected),

    "outputs/known_reasoning_holds_2.jsonl":
        encode_jsonl(held),

    "outputs/reference_adjudication_flags_1.jsonl":
        encode_jsonl(flags),

    "outputs/decision_index_641.jsonl":
        encode_jsonl(decision_index),

    "outputs/summary.json":
        encode_json(report),
}

outputs["manifest.json"] = encode_json({
    "schema": "e004_p3_quality_triage_inline_manifest_v1",
    "files": {
        name: sha(data)
        for name, data in sorted(outputs.items())
    },
    "original_candidates_sha256": P3_SHA,
    "screen_manifest_sha256": SCREEN_SHA,
    "approved_training_pairs": 0,
    "training_performed": False,
})


print("\n=== BYTE-EXACT FROZEN OUTPUT VERIFICATION ===")

require(
    sha(outputs["manifest.json"]) == TRIAGE_SHA,
    "Reconstructed manifest differs from frozen manifest",
)

for name, expected_data in outputs.items():
    path = OUT / name

    require(
        path.is_file() and not path.is_symlink(),
        f"Missing or unsafe output: {path}",
    )

    require(
        path.read_bytes() == expected_data,
        f"Frozen output differs from replay: {path}",
    )

    print("BYTE-EXACT:", name)

print()
print("E004-P3 TRIAGE REPLAY: PASSED")
print("Frozen manifest SHA256:", TRIAGE_SHA)
print("Provisional P3 pairs:", len(retained))
print("Preserved rejects:", len(rejected))
print("Approved training pairs: 0")
print("GPU inference: NO")
print("Training: NO")
