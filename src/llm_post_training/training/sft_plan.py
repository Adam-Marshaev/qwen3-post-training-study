"""Deterministic SFT epoch plans and supervised-token accumulation weights."""

import random
from dataclasses import dataclass
from typing import Sequence

from llm_post_training.training.sft_tokenization import (
    IGNORE_INDEX,
    SFTTokenizedExample,
)


@dataclass(frozen=True)
class AccumulationGroup:
    """One optimizer step; indices refer to positions in the tokenized dataset."""

    microbatches: tuple[tuple[int, ...], ...]
    supervised_tokens_per_batch: tuple[int, ...]
    total_supervised_tokens: int

    @property
    def loss_weights(self) -> tuple[float, ...]:
        """Scale mean microbatch losses for token-weighted accumulation."""
        return tuple(
            count / self.total_supervised_tokens
            for count in self.supervised_tokens_per_batch
        )


@dataclass(frozen=True)
class SFTEpochPlan:
    """Shuffled, fully covered epoch with optimizer-step boundaries."""

    epoch: int
    example_count: int
    groups: tuple[AccumulationGroup, ...]

    @property
    def optimizer_steps(self) -> int:
        return len(self.groups)

    @property
    def microbatch_count(self) -> int:
        return sum(len(group.microbatches) for group in self.groups)


def build_sft_epoch_plan(
    examples: Sequence[SFTTokenizedExample],
    *,
    epoch: int,
    seed: int,
    microbatch_size: int,
    gradient_accumulation_steps: int,
    max_sequence_length: int,
) -> SFTEpochPlan:
    """Shuffle locally, preserve all examples, and group optimizer updates.

    Microbatch indices are positional offsets into 'examples', NOT
    original GSM8K source indices.

    The final partial accumulation group is never dropped.

    For a model returning mean cross-entropy over supervised tokens,
    multiply each microbatch loss by its corresponding loss weight
    before backward().
    """

    if epoch < 0:
        raise ValueError("epoch must be nonnegative")

    if microbatch_size < 1 or gradient_accumulation_steps < 1:
        raise ValueError("Batch and accumulation sizes must be positive")

    if max_sequence_length < 1:
        raise ValueError("max_sequence_length must be positive")

    if not examples:
        raise ValueError("SFT training dataset cannot be empty")

    source_indices = [example.source_index for example in examples]

    if len(source_indices) != len(set(source_indices)):
        raise ValueError("Duplicate training source index")

    supervised_by_position = []

    for example in examples:
        if example.sequence_length > max_sequence_length:
            raise ValueError(
                f"Source index {example.source_index} exceeds "
                f"training sequence limit {max_sequence_length}"
            )

        if len(example.labels) != example.sequence_length:
            raise ValueError("SFT labels/input length mismatch")

        # A causal LM predicts token t using preceding tokens.
        # The label at position zero is never a training target.
        supervised = sum(
            label != IGNORE_INDEX
            for label in example.labels[1:]
        )

        expected = example.completion_token_count + 1

        if supervised != expected:
            raise ValueError(
                f"Unexpected supervised token count for source "
                f"index {example.source_index}"
            )

        supervised_by_position.append(supervised)

    # Use a local RNG so shuffling does not change global
    # Python random state.
    positions = list(range(len(examples)))

    random.Random(seed + epoch).shuffle(positions)

    microbatches = [
        tuple(positions[start:start + microbatch_size])
        for start in range(0, len(positions), microbatch_size)
    ]

    groups = []

    for start in range(
        0,
        len(microbatches),
        gradient_accumulation_steps,
    ):
        batches = tuple(
            microbatches[
                start:start + gradient_accumulation_steps
            ]
        )

        counts = tuple(
            sum(supervised_by_position[index] for index in batch)
            for batch in batches
        )

        groups.append(
            AccumulationGroup(
                microbatches=batches,
                supervised_tokens_per_batch=counts,
                total_supervised_tokens=sum(counts),
            )
        )

    return SFTEpochPlan(
        epoch=epoch,
        example_count=len(examples),
        groups=tuple(groups),
    )
