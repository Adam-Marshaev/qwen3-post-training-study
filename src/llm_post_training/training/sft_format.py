"""Prepare GSM8K reference solutions for supervised fine-tuning."""

import re

from dataclasses import dataclass

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)
from llm_post_training.evaluation.prompting import (
    format_baseline_prompt,
)


# GSM8K contains inline calculator annotations such as:
#
#   <<16-3-4=9>>9
#
# Remove the annotation while retaining the visible result.
CALCULATOR_ANNOTATION_PATTERN = re.compile(
    r"<<[^<>\n]*>>"
)


# The final reference answer is introduced by a line beginning
# with ####.
REFERENCE_MARKER_PATTERN = re.compile(
    r"^[ \t]*####[ \t]*",
    flags=re.MULTILINE,
)


@dataclass(frozen=True)
class SFTTextExample:
    """Text fields used to construct a causal-LM training example."""

    prompt: str
    completion: str

    @property
    def full_text(self) -> str:
        """Return the prompt followed by the target completion."""
        return self.prompt + self.completion


def format_sft_completion(reference_solution: str) -> str:
    """Convert one GSM8K reference solution into a model completion.

    The final numerical answer is obtained through our existing
    strict GSM8K reference parser.

    Calculator annotations are removed, but their rendered
    numerical results are retained.

    Only the reference's final #### marker is converted into
    the evaluation-compatible 'The answer is ...' declaration.
    """

    if not isinstance(reference_solution, str):
        raise TypeError("reference_solution must be a string")

    reference_answer = parse_gsm8k_reference_answer(
        reference_solution
    )

    markers = list(
        REFERENCE_MARKER_PATTERN.finditer(reference_solution)
    )

    if len(markers) != 1:
        raise ValueError(
            "Expected exactly one GSM8K final-answer marker"
        )

    reasoning = reference_solution[:markers[0].start()].strip()

    if not reasoning:
        raise ValueError("Reference reasoning cannot be empty")

    reasoning = CALCULATOR_ANNOTATION_PATTERN.sub(
        "",
        reasoning,
    ).strip()

    # Reject malformed calculator annotations rather than
    # silently training on partially processed markup.
    if "<<" in reasoning or ">>" in reasoning:
        raise ValueError("Malformed GSM8K calculator annotation")

    if not reasoning:
        raise ValueError(
            "Reference reasoning is empty after cleanup"
        )

    return (
        f" {reasoning}\n"
        f"The answer is {reference_answer}."
    )


def format_sft_example(
    question: str,
    reference_solution: str,
) -> SFTTextExample:
    """Produce separate prompt and completion fields."""

    prompt = format_baseline_prompt(question)

    completion = format_sft_completion(
        reference_solution
    )

    return SFTTextExample(
        prompt=prompt,
        completion=completion,
    )
