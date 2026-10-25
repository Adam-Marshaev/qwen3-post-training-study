"""E005 GRPO reward for exact GSM8K numerical correctness.

Reward version: gsm8k_exact_numeric_v1.

Expected dataset columns:
    prompt: str
    answer: str  (original GSM8K solution ending in #### NUMBER)

This function is designed for TRL 0.26.2 with non-conversational
string completions.

It intentionally reuses the frozen project answer parsers.

No model loading, inference, or training occurs in this module.
"""

from collections.abc import Sequence

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)
from llm_post_training.evaluation.answer_extraction import (
    extract_final_answer,
)


GRPO_REWARD_VERSION = "gsm8k_exact_numeric_v1"


def gsm8k_exact_numeric_reward(
    *,
    completions: Sequence[str],
    answer: Sequence[str],
    **kwargs,
) -> list[float]:
    """Return one binary numerical-correctness reward per completion.

    A reward of 1.0 requires:
      - a valid, unambiguous final numerical answer;
      - numerical equality with the GSM8K reference;
      - no detected continuation into another question.

    Otherwise the reward is 0.0.

    Invalid reference data and unexpected completion types are errors,
    not silently assigned a zero reward.

    Additional keyword arguments supplied by TRL are accepted but
    do not influence the reward.
    """
    del kwargs

    if isinstance(completions, (str, bytes)) or not isinstance(
        completions, Sequence
    ):
        raise TypeError("completions must be a sequence of strings")

    if isinstance(answer, (str, bytes)) or not isinstance(
        answer, Sequence
    ):
        raise TypeError("answer must be a sequence of GSM8K solutions")

    if len(completions) != len(answer):
        raise ValueError(
            "Completion/reference batch length mismatch: "
            f"{len(completions)} vs {len(answer)}"
        )

    rewards: list[float] = []

    for index, (completion, solution) in enumerate(
        zip(completions, answer, strict=True)
    ):
        if not isinstance(completion, str):
            raise TypeError(
                f"Completion at batch index {index} is not a string"
            )

        if not isinstance(solution, str):
            raise TypeError(
                f"Reference at batch index {index} is not a string"
            )

        try:
            reference = parse_gsm8k_reference_answer(solution)
        except ValueError as exc:
            raise ValueError(
                f"Invalid GSM8K reference at batch index {index}"
            ) from exc

        extracted = extract_final_answer(completion)

        correct = (
            extracted.status == "valid"
            and not extracted.unwanted_continuation
            and extracted.answer == reference
        )

        rewards.append(1.0 if correct else 0.0)

    return rewards
