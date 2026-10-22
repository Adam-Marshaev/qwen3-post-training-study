"""Dynamically pad completion-only SFT training batches."""

from collections.abc import Sequence
from dataclasses import dataclass

import torch

from llm_post_training.training.sft_tokenization import (
    IGNORE_INDEX,
    SFTTokenizedExample,
)


DEFAULT_MAX_SEQUENCE_LENGTH = 512


@dataclass(frozen=True)
class SFTBatchCollator:
    """Right-pad SFT examples without changing supervised targets."""

    pad_token_id: int
    eos_token_id: int
    max_seq_length: int = DEFAULT_MAX_SEQUENCE_LENGTH
    allow_pad_eos_collision: bool = False

    def __post_init__(self) -> None:
        if self.pad_token_id < 0:
            raise ValueError("PAD token ID must be nonnegative")

        if self.eos_token_id < 0:
            raise ValueError("EOS token ID must be nonnegative")

        if (
            self.pad_token_id == self.eos_token_id
            and not self.allow_pad_eos_collision
        ):
            raise ValueError(
                "PAD and EOS token IDs must be distinct "
                "unless explicitly allowed"
            )

        if self.max_seq_length < 1:
            raise ValueError(
                "Maximum sequence length must be positive"
            )

    def __call__(
        self,
        examples: Sequence[SFTTokenizedExample],
    ) -> dict[str, torch.Tensor]:
        """Return dynamically padded input IDs, masks, and labels.

        Output tensors have shape [batch_size, longest_sequence].

        All sequences are right-padded.

        Padding IDs are excluded from both attention and loss.
        """

        if not examples:
            raise ValueError("Cannot collate an empty SFT batch")

        batch_size = len(examples)

        batch_length = max(
            example.sequence_length
            for example in examples
        )

        if batch_length > self.max_seq_length:
            raise ValueError(
                f"SFT sequence length {batch_length} exceeds "
                f"configured limit {self.max_seq_length}"
            )

        input_ids = torch.full(
            (batch_size, batch_length),
            self.pad_token_id,
            dtype=torch.long,
        )

        attention_mask = torch.zeros(
            (batch_size, batch_length),
            dtype=torch.long,
        )

        labels = torch.full(
            (batch_size, batch_length),
            IGNORE_INDEX,
            dtype=torch.long,
        )

        for row, example in enumerate(examples):
            length = example.sequence_length
            prompt_length = example.prompt_token_count
            completion_length = example.completion_token_count

            if not (
                length
                == len(example.labels)
                == len(example.attention_mask)
            ):
                raise ValueError(
                    "Inconsistent SFT sequence length fields"
                )

            if (
                prompt_length < 1
                or completion_length < 1
                or length != prompt_length + completion_length + 1
            ):
                raise ValueError(
                    "Inconsistent SFT length metadata"
                )

            if (
                example.input_ids[-1] != self.eos_token_id
                or example.labels[-1] != self.eos_token_id
            ):
                raise ValueError(
                    "SFT example must end with a supervised EOS"
                )

            if any(
                value != 1
                for value in example.attention_mask
            ):
                raise ValueError(
                    "Unpadded SFT attention mask must contain only ones"
                )

            if any(
                label != IGNORE_INDEX
                for label in example.labels[:prompt_length]
            ):
                raise ValueError(
                    "SFT prompt labels must be ignored"
                )

            if (
                example.labels[prompt_length:]
                != example.input_ids[prompt_length:]
            ):
                raise ValueError(
                    "SFT completion labels must match input IDs"
                )

            input_ids[row, :length] = torch.tensor(
                example.input_ids,
                dtype=torch.long,
            )

            attention_mask[row, :length] = torch.tensor(
                example.attention_mask,
                dtype=torch.long,
            )

            labels[row, :length] = torch.tensor(
                example.labels,
                dtype=torch.long,
            )

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }
