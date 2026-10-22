"""Load manifest-approved GSM8K examples for supervised fine-tuning."""

import json

from dataclasses import dataclass
from pathlib import Path

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)
from llm_post_training.data.loader import (
    load_gsm8k_split,
)
from llm_post_training.training.sft_format import (
    format_sft_example,
)


@dataclass(frozen=True)
class SFTTrainingExample:
    """One manifest-approved supervised fine-tuning example."""

    source_index: int
    prompt: str
    completion: str

    @property
    def full_text(self) -> str:
        return self.prompt + self.completion


def load_sft_training_examples(
    source_path: Path,
    manifest_path: Path,
) -> list[SFTTrainingExample]:
    """Load only the frozen GSM8K development-training partition.

    The existing manifest-aware loader establishes which original
    source indices are allowed.

    Original reference solutions are retrieved only for those
    approved training examples.

    The evaluation/validation examples are not returned.
    """

    source_path = Path(source_path)
    manifest_path = Path(manifest_path)

    # Retain the source bytes so we can verify that the dataset
    # did not change between split verification and formatting.
    source_bytes = source_path.read_bytes()

    training = load_gsm8k_split(
        source_path,
        manifest_path,
        "training",
    )

    if source_path.read_bytes() != source_bytes:
        raise ValueError(
            "GSM8K source changed during training-data loading"
        )

    source_lines = source_bytes.splitlines()

    examples = []

    for approved in training:
        index = approved.source_index

        if index < 0 or index >= len(source_lines):
            raise ValueError(
                f"Approved source index out of range: {index}"
            )

        record = json.loads(source_lines[index])

        if record["question"] != approved.question:
            raise ValueError(
                f"Question mismatch at source index {index}"
            )

        raw_answer = record["answer"]

        reference_answer = parse_gsm8k_reference_answer(
            raw_answer
        )

        if reference_answer != approved.reference_answer:
            raise ValueError(
                f"Reference answer mismatch at source index {index}"
            )

        formatted = format_sft_example(
            question=record["question"],
            reference_solution=raw_answer,
        )

        examples.append(
            SFTTrainingExample(
                source_index=index,
                prompt=formatted.prompt,
                completion=formatted.completion,
            )
        )

    return examples
