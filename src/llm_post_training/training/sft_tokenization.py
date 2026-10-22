"""Tokenize SFT examples with completion-only causal-LM labels."""

from dataclasses import dataclass
from typing import Protocol

from llm_post_training.training.sft_data import (
    SFTTrainingExample,
)


IGNORE_INDEX = -100


class SFTTokenizer(Protocol):
    """Minimal tokenizer interface required for SFT preparation."""

    eos_token_id: int | None

    def encode(
        self,
        text: str,
        *,
        add_special_tokens: bool,
    ) -> list[int]:
        ...


@dataclass(frozen=True)
class SFTTokenizedExample:
    """One tokenized example before padding or batching."""

    source_index: int

    input_ids: tuple[int, ...]
    attention_mask: tuple[int, ...]
    labels: tuple[int, ...]

    prompt_token_count: int
    completion_token_count: int

    @property
    def sequence_length(self) -> int:
        return len(self.input_ids)


def tokenize_sft_example(
    example: SFTTrainingExample,
    tokenizer: SFTTokenizer,
) -> SFTTokenizedExample:
    """Construct completion-only labels, including an EOS target.

    Tokenize the prompt independently to preserve the exact
    prefix token IDs used during baseline evaluation.

    Do not pad or truncate here. Sequence-length limits and
    batch padding will be handled in separate components.
    """

    eos_id = tokenizer.eos_token_id

    if eos_id is None:
        raise ValueError("Tokenizer must define an EOS token")

    prompt_ids = tokenizer.encode(
        example.prompt,
        add_special_tokens=False,
    )

    completion_ids = tokenizer.encode(
        example.completion,
        add_special_tokens=False,
    )

    if not prompt_ids:
        raise ValueError("Prompt produced no tokens")

    if not completion_ids:
        raise ValueError("Completion produced no tokens")

    input_ids = tuple(
        prompt_ids + completion_ids + [eos_id]
    )

    labels = tuple(
        [IGNORE_INDEX] * len(prompt_ids)
        + completion_ids
        + [eos_id]
    )

    attention_mask = (1,) * len(input_ids)

    assert len(input_ids) == len(labels) == len(attention_mask)

    return SFTTokenizedExample(
        source_index=example.source_index,
        input_ids=input_ids,
        attention_mask=attention_mask,
        labels=labels,
        prompt_token_count=len(prompt_ids),
        completion_token_count=len(completion_ids),
    )
