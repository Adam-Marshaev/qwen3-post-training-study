#!/usr/bin/env python3
"""CPU-only E004 combined provisional export; never approves or trains."""
import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

BASE = "a8f8795f02d8f5a8e027bc4e4319bdf057d4d938"
TRIAGE = "f67c32d754ff33a4418e9a92cbfa5fe0424cb684d9f1d5efa0984f8c310764fa"

SPECS = {
    "P1": (
        "e004_p1_250_k4_fc6d484_v1",
        "e004_p1_arithmetic_first_v1",
        "fe0ce3a7bb4cd20fedf4ee25e15e171e0047ff786ae39f16c2db4118934dcff0",
        "314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628",
        "outputs/decisions_relaxed.jsonl",
        135, 83, None,
    ),
    "P2": (
        "e004_p2_250_k4_f543aa4_v1",
        "e004_p2_arithmetic_first_v1",
        "fe4c4f034417b73be7862975889e102882be6d9f67352d62b9a568eaeb66faf9",
        "568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79",
        "outputs/review/decisions_advisory.jsonl",
        137, 80,
        "8e5adf5663b753ff14b9db1ee5a845643e7dfb1c07ca69f8b948bf29919e0cdb",
    ),
}


def check(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path, expected=None):
    check(
        path.is_file() and not path.is_symlink(),
        f"Missing or unsafe file: {path}",
    )
    data = path.read_bytes()
    if expected is not None:
        check(digest(data) == expected, f"SHA256 mismatch: {path}")
    return data


def stream(data):
    """Read JSONL or legacy concatenated JSON records."""
    text = data.decode("utf-8")
    decoder = json.JSONDecoder()
    pos = 0
    result = []

    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1

        if pos == len(text):
            return result

        obj, pos = decoder.raw_decode(text, pos)
        result.extend(obj if isinstance(obj, list) else [obj])


def indexed(rows, label):
    out = {}

    for row in rows:
        source = row["source_index"]
        check(
            type(source) is int and source not in out,
            f"{label}: duplicate/invalid source {source}",
        )
        out[source] = row

    return out


def pair(phase, source, chosen_id, rejected_id,
         samples, selection, provenance):

    check(
        type(chosen_id) is int
        and type(rejected_id) is int
        and chosen_id != rejected_id
        and chosen_id in samples
        and rejected_id in samples,
        f"{phase}/{source}: invalid pair IDs",
    )

    chosen = samples[chosen_id]
    rejected = samples[rejected_id]

    check(
        chosen["source_index"] == source
        and rejected["source_index"] == source
        and chosen["sample_index"] == chosen_id
        and rejected["sample_index"] == rejected_id,
        f"{phase}/{source}: candidate identity mismatch",
    )

    check(
        chosen["eligible"] is True
        and chosen["correct"] is True
        and rejected["eligible"] is True
        and rejected["correct"] is False,
        f"{phase}/{source}: incorrect chosen/rejected labels",
    )

    check(
        chosen["prompt"] == rejected["prompt"]
        and chosen["reference_answer"] == rejected["reference_answer"]
        and isinstance(chosen["response"], str)
        and bool(chosen["response"].strip())
        and isinstance(rejected["response"], str)
        and bool(rejected["response"].strip()),
        f"{phase}/{source}: inconsistent prompt or response",
    )

    return {
        "phase": phase,
        "source_index": source,
        "prompt": chosen["prompt"],
        "reference_answer": chosen["reference_answer"],
        "chosen": chosen["response"],
        "rejected": rejected["response"],
        "chosen_sample_index": chosen_id,
        "rejected_sample_index": rejected_id,
        "chosen_candidate": chosen,
        "rejected_candidate": rejected,
        "selection_decision": selection,
        "input_sha256": provenance,
        "quality_status": "AUTO_SCREENED_PROVISIONAL_NOT_CERTIFIED",
        "reasoning_independently_verified": False,
        "approved_for_training": False,
    }


def legacy(root, phase, spec):
    (
        run, protocol, mixed_sha, candidate_sha,
        decision_name, mixed_n, accepted_n, decision_sha,
    ) = spec

    home = root / "protocols" / protocol

    matches = [
        path
        for path in (home / "inputs").glob("*.jsonl")
        if path.is_file()
        and not path.is_symlink()
        and digest(read(path)) == mixed_sha
    ]

    check(
        len(matches) == 1,
        f"{phase}: frozen mixed input not uniquely identified",
    )

    mixed = indexed(
        stream(read(matches[0], mixed_sha)),
        f"{phase} mixed",
    )

    decision_path = home / decision_name
    decision_bytes = read(decision_path, decision_sha)

    decisions = indexed(
        stream(decision_bytes),
        f"{phase} decisions",
    )

    check(
        len(mixed) == mixed_n
        and set(mixed) == set(decisions),
        f"{phase}: mixed/decision mismatch",
    )

    candidate_path = (
        root / "data/preference_runs" / run / "candidates.jsonl"
    )

    all_rows = stream(read(candidate_path, candidate_sha))
    originals = defaultdict(dict)

    for record in all_rows:
        source = record["source_index"]
        sample = record["sample_index"]

        check(
            type(source) is int
            and type(sample) is int
            and sample in range(4)
            and sample not in originals[source],
            f"{phase}: duplicate/invalid candidate sample",
        )

        originals[source][sample] = record

    check(
        len(all_rows) == 1000
        and len(originals) == 250
        and all(set(v) == set(range(4)) for v in originals.values())
        and set(mixed) <= set(originals),
        f"{phase}: original candidate inventory mismatch",
    )

    accepted = [
        decision
        for decision in decisions.values()
        if decision["decision"] == "PROVISIONAL_ACCEPT_QC_REQUIRED"
    ]

    check(
        len(accepted) == accepted_n,
        f"{phase}: provisional count mismatch",
    )

    provenance = {
        "candidates_sha256": candidate_sha,
        "mixed_sha256": mixed_sha,
        "decisions_sha256": digest(decision_bytes),
    }

    rows = []

    for decision in sorted(
        accepted,
        key=lambda x: x["source_index"],
    ):
        source = decision["source_index"]
        group = mixed[source]
        samples = originals[source]

        check(
            decision["approved_for_training"] is False
            and group["prompt"] == samples[0]["prompt"]
            and group["reference_answer"]
            == samples[0]["reference_answer"],
            f"{phase}/{source}: group or approval mismatch",
        )

        compact = group["responses"]

        check(
            len(compact) == 4
            and {r["sample_index"] for r in compact} == set(range(4)),
            f"{phase}/{source}: incomplete mixed group",
        )

        for response in compact:
            original = samples[response["sample_index"]]

            check(
                all(
                    key in original and original[key] == value
                    for key, value in response.items()
                ),
                f"{phase}/{source}: mixed/candidate mismatch",
            )

        rows.append(
            pair(
                phase,
                source,
                decision["chosen_sample_index"],
                decision["rejected_sample_index"],
                samples,
                decision["decision"],
                provenance,
            )
        )

    print(
        f"{phase}: {len(rows)} verified pairs; "
        f"decision SHA256 {digest(decision_bytes)}",
        flush=True,
    )

    return rows, {
        "accepted_pairs": len(rows),
        **provenance,
        "decision_file": str(decision_path.relative_to(root)),
        "mixed_file": str(matches[0].relative_to(root)),
    }


def main(root, check_only):
    check(
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE, "HEAD"],
            cwd=root,
            capture_output=True,
        ).returncode == 0,
        "Missing frozen P3 Git ancestor",
    )

    triage = (
        root / "data/preference_runs/e004_p3_quality_triage_v1"
    )

    manifest = json.loads(read(triage / "manifest.json", TRIAGE))

    check(
        manifest["approved_training_pairs"] == 0
        and manifest["training_performed"] is False,
        "P3 triage authorization mismatch",
    )

    for name, expected in manifest["files"].items():
        relative = Path(name)

        check(
            not relative.is_absolute()
            and ".." not in relative.parts,
            "Unsafe manifest path",
        )

        read(triage / relative, expected)

    retained = stream(
        read(
            triage
            / "outputs/auto_retained_provisional_423.jsonl"
        )
    )

    holds = indexed(
        stream(
            read(triage / "outputs/known_reasoning_holds_2.jsonl")
        ),
        "P3 holds",
    )

    rejects = indexed(
        stream(
            read(
                triage
                / "outputs/mechanical_rejects_preserved_216.jsonl"
            )
        ),
        "P3 rejects",
    )

    check(
        len(retained) == 423
        and set(holds) == {3115, 4201}
        and len(rejects) == 216
        and 1958 in rejects,
        "P3 triage partition mismatch",
    )

    combined = []
    provenance = {}

    for phase, spec in SPECS.items():
        rows, source_info = legacy(root, phase, spec)

        combined.extend(rows)
        provenance[phase] = source_info

    for item in retained:
        source = item["source_index"]
        chosen = item["chosen_candidate"]
        rejected = item["rejected_candidate"]

        check(
            item["status"] == "AUTO_SCREENED_PROVISIONAL"
            and item["approved_for_training"] is False
            and item["reasoning_independently_verified"] is False
            and source not in holds
            and source not in rejects,
            "P3 retained/hold mismatch",
        )

        combined.append(
            pair(
                "P3",
                source,
                item["chosen_sample_index"],
                item["rejected_sample_index"],
                {
                    chosen["sample_index"]: chosen,
                    rejected["sample_index"]: rejected,
                },
                "AUTO_SCREENED_PROVISIONAL",
                {"triage_manifest_sha256": TRIAGE},
            )
        )

    check(
        len(combined) == 586
        and len({row["source_index"] for row in combined}) == 586,
        "Combined count or source uniqueness failure",
    )

    combined.sort(key=lambda row: row["source_index"])

    def encode_json(obj):
        return (
            json.dumps(
                obj,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            ) + "\n"
        ).encode()

    pair_bytes = "".join(
        json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"
        for row in combined
    ).encode()

    provenance["P3"] = {
        "triage_manifest_sha256": TRIAGE,
        "accepted_pairs": 423,
    }

    summary = {
        "schema": "e004_combined_provisional_v1",
        "pair_count": 586,
        "pair_counts": {"P1": 83, "P2": 80, "P3": 423},
        "source_unique": True,
        "source_split": "GSM8K frozen development-train only",
        "p3_known_reasoning_holds": 2,
        "p3_reject_groups_preserved_separately": 216,
        "pairs_reasoning_certified": 0,
        "approved_training_pairs": 0,
        "official_test_used": False,
        "training_performed": False,
        "requires_separate_training_authorization": True,
        "input_provenance": provenance,
    }

    outputs = {
        "outputs/provisional_pairs_586.jsonl": pair_bytes,
        "outputs/summary.json": encode_json(summary),
    }

    outputs["manifest.json"] = encode_json({
        "schema": "e004_combined_provisional_manifest_v1",
        "members_sha256": {
            name: digest(data)
            for name, data in sorted(outputs.items())
        },
        "pairs_sha256": digest(pair_bytes),
        "approved_training_pairs": 0,
        "training_performed": False,
    })

    target = (
        root / "data/preference_runs/e004_combined_provisional_v1"
    )

    check(not target.is_symlink(), "Unsafe output directory")

    for name, data in outputs.items():
        path = target / name

        check(
            not path.is_symlink()
            and not path.parent.is_symlink(),
            f"Unsafe output: {path}",
        )

        if path.exists():
            check(
                read(path) == data,
                f"Refusing to overwrite changed output: {path}",
            )

    if not check_only:
        for name, data in outputs.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)

            if not path.exists():
                with path.open("xb") as f:
                    f.write(data)

            check(
                read(path) == data,
                f"Post-write mismatch: {path}",
            )

    print(json.dumps({
        "mode": (
            "READ_ONLY_PREFLIGHT"
            if check_only
            else "WRITTEN_IDEMPOTENTLY"
        ),
        "P1": 83,
        "P2": 80,
        "P3": 423,
        "total_provisional": 586,
        "pairs_sha256": digest(pair_bytes),
        "manifest_sha256": digest(outputs["manifest.json"]),
        "approved_training_pairs": 0,
        "training_performed": False,
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
    )

    parser.add_argument(
        "--check-only",
        action="store_true",
    )

    args = parser.parse_args()
    main(args.repo.resolve(), args.check_only)
