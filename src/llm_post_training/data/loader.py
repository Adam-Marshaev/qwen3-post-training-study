"""Load GSM8K examples using a verified split manifest."""

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Literal

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)
from llm_post_training.data.splitting import normalize_question


SplitName = Literal["training", "validation"]


@dataclass(frozen=True)
class GSM8KExample:
    """One verified GSM8K example for evaluation."""

    source_index: int
    question: str
    reference_answer: Decimal


def load_gsm8k_split(
    source_path: Path,
    manifest_path: Path,
    split: SplitName,
) -> list[GSM8KExample]:
    """Load a verified subset of the official GSM8K training data.

    Validates:
    - Dataset checksum and source revision
    - Manifest version and record counts
    - Index ranges and uniqueness
    - Disjoint and complete partitioning
    - Absence of normalized-question leakage
    """

    if split not in ("training", "validation"):
        raise ValueError(f"Unknown split: {split!r}")

    source_bytes = source_path.read_bytes()

    actual_sha256 = hashlib.sha256(source_bytes).hexdigest()

    manifest = json.loads(
        manifest_path.read_text(encoding="utf-8")
    )

    if manifest.get("split_version") != 1:
        raise ValueError("Unsupported split manifest version")

    if manifest.get("dataset") != "openai/grade-school-math":
        raise ValueError("Unexpected dataset identity")

    if manifest.get("source_sha256") != actual_sha256:
        raise ValueError("Dataset checksum mismatch")

    revision_path = source_path.parent / "source_commit.txt"

    actual_revision = revision_path.read_text(
        encoding="utf-8"
    ).strip()

    if manifest.get("source_commit") != actual_revision:
        raise ValueError("Dataset source revision mismatch")

    records = [
        json.loads(line)
        for line in source_bytes.decode("utf-8").splitlines()
    ]

    total = len(records)

    if manifest.get("total_examples") != total:
        raise ValueError("Dataset record count mismatch")

    split_indices = {}

    for name in ("training", "validation"):
        indices = manifest.get(f"{name}_indices")

        if not isinstance(indices, list):
            raise ValueError(f"Missing {name} indices")

        if any(
            type(index) is not int or not 0 <= index < total
            for index in indices
        ):
            raise ValueError(f"Invalid {name} indices")

        if len(indices) != len(set(indices)):
            raise ValueError(f"Duplicate indices in {name}")

        if manifest.get(f"{name}_count") != len(indices):
            raise ValueError(f"Incorrect {name} count")

        split_indices[name] = indices

    training = set(split_indices["training"])
    validation = set(split_indices["validation"])

    if training & validation:
        raise ValueError("Training and validation indices overlap")

    if training | validation != set(range(total)):
        raise ValueError("Split does not cover all examples")

    training_questions = {
        normalize_question(records[index]["question"])
        for index in training
    }

    validation_questions = {
        normalize_question(records[index]["question"])
        for index in validation
    }

    if training_questions & validation_questions:
        raise ValueError(
            "Normalized question appears in both splits"
        )

    examples = []

    for index in split_indices[split]:
        record = records[index]

        answer = parse_gsm8k_reference_answer(
            record["answer"]
        )

        examples.append(
            GSM8KExample(
                source_index=index,
                question=record["question"],
                reference_answer=answer,
            )
        )

    return examples
