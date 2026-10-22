"""Create a reproducible GSM8K development split."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)


SOURCE_COMMIT = "3101c7d5072418e28b9008a6636bde82a006892c"

SOURCE_SHA256 = (
    "17f347dc51477c50d4efb83959dbb7"
    "c56297aba886e5544ee2aaed3024813465"
)

SEED = 42
VALIDATION_FRACTION = 0.10


def normalize_question(question: str) -> str:
    """Normalize capitalization and whitespace."""
    return " ".join(question.casefold().split())


def build_split(
    records: list[dict[str, str]],
    seed: int = SEED,
    validation_fraction: float = VALIDATION_FRACTION,
) -> tuple[list[int], list[int]]:
    """Return training and validation indices.

    Questions with identical normalized text are kept together.
    Assignment is based on a stable SHA-256 ranking.
    """

    if len(records) < 2:
        raise ValueError("At least two records are required")

    if not 0 < validation_fraction < 1:
        raise ValueError("Validation fraction must be between 0 and 1")

    groups = defaultdict(list)
    reference_answers = {}

    for index, record in enumerate(records):
        question = normalize_question(record["question"])
        answer = parse_gsm8k_reference_answer(record["answer"])

        if not question:
            raise ValueError(f"Empty question at index {index}")

        previous_answer = reference_answers.get(question)

        if previous_answer is not None and previous_answer != answer:
            raise ValueError(
                f"Conflicting answers for duplicate question: {index}"
            )

        reference_answers[question] = answer
        groups[question].append(index)

    def ranking_key(question: str) -> tuple[str, str]:
        encoded = f"{seed}\n{question}".encode("utf-8")
        return hashlib.sha256(encoded).hexdigest(), question

    ranked_questions = sorted(groups, key=ranking_key)

    target_validation = round(len(records) * validation_fraction)
    target_validation = max(1, min(target_validation, len(records) - 1))

    training = []
    validation = []

    for question in ranked_questions:
        group = groups[question]

        if len(validation) < target_validation:
            validation.extend(group)
        else:
            training.extend(group)

    if not training or not validation:
        raise ValueError("Unable to form two nonempty splits")

    return sorted(training), sorted(validation)


def main() -> None:
    """Validate source data and write the immutable split manifest."""

    source = Path("data/raw/gsm8k/train.jsonl")
    revision_file = Path("data/raw/gsm8k/source_commit.txt")
    destination = Path("configs/data/gsm8k_split_v1.json")

    if destination.exists():
        raise FileExistsError(
            f"{destination} already exists; refusing to overwrite"
        )

    source_bytes = source.read_bytes()
    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()

    if actual_sha256 != SOURCE_SHA256:
        raise ValueError("GSM8K source checksum mismatch")

    revision = revision_file.read_text(encoding="utf-8").strip()

    if revision != SOURCE_COMMIT:
        raise ValueError("GSM8K source revision mismatch")

    records = [
        json.loads(line)
        for line in source_bytes.decode("utf-8").splitlines()
    ]

    if len(records) != 7473:
        raise ValueError("Unexpected GSM8K training record count")

    training, validation = build_split(records)

    manifest = {
        "dataset": "openai/grade-school-math",
        "source_commit": SOURCE_COMMIT,
        "source_sha256": SOURCE_SHA256,
        "split_version": 1,
        "seed": SEED,
        "validation_fraction": VALIDATION_FRACTION,
        "strategy": "SHA-256 ranking grouped by normalized question",
        "total_examples": len(records),
        "training_count": len(training),
        "validation_count": len(validation),
        "training_indices": training,
        "validation_indices": validation,
    }

    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("=== GSM8K SPLIT CREATED ===")
    print("Training examples:", len(training))
    print("Validation examples:", len(validation))
    print("Total:", len(records))
    print("Seed:", SEED)
    print("Manifest:", destination)
    print("Manifest SHA-256:", hashlib.sha256(
        destination.read_bytes()
    ).hexdigest())


if __name__ == "__main__":
    main()
