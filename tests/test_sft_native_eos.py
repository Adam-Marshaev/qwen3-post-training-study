"""Regression tests for configurable SFT EOS supervision."""

import unittest
from types import SimpleNamespace

from llm_post_training.training.sft_collator import (
    SFTBatchCollator,
)
from llm_post_training.training.sft_tokenization import (
    IGNORE_INDEX,
    tokenize_sft_example,
)


TOKENIZER_EOS = 151645
NATIVE_EOS = 151643


class TinyTokenizer:
    eos_token_id = TOKENIZER_EOS

    def encode(self, text, *, add_special_tokens):
        assert add_special_tokens is False

        return [
            10 + ord(character) % 100
            for character in text
        ]


def example(index, completion):
    return SimpleNamespace(
        source_index=index,
        prompt="Question:",
        completion=completion,
    )


class TestNativeEOS(unittest.TestCase):

    def setUp(self):
        self.tokenizer = TinyTokenizer()

    def test_original_e002_behavior_unchanged(self):
        record = tokenize_sft_example(
            example(0, " The answer is 48."),
            self.tokenizer,
        )

        self.assertEqual(
            record.input_ids[-1],
            TOKENIZER_EOS,
        )

        self.assertEqual(
            record.labels[-1],
            TOKENIZER_EOS,
        )

        self.assertEqual(
            self.tokenizer.eos_token_id,
            TOKENIZER_EOS,
        )

    def test_native_eos_override(self):
        record = tokenize_sft_example(
            example(1, " The answer is 400."),
            self.tokenizer,
            target_eos_token_id=NATIVE_EOS,
        )

        self.assertEqual(
            record.input_ids[-1],
            NATIVE_EOS,
        )

        self.assertEqual(
            record.labels[-1],
            NATIVE_EOS,
        )

        self.assertEqual(
            record.attention_mask[-1],
            1,
        )

        # The tokenizer itself must not be modified.
        self.assertEqual(
            self.tokenizer.eos_token_id,
            TOKENIZER_EOS,
        )

    def test_collision_requires_explicit_permission(self):
        with self.assertRaisesRegex(
            ValueError,
            "distinct",
        ):
            SFTBatchCollator(
                pad_token_id=NATIVE_EOS,
                eos_token_id=NATIVE_EOS,
            )

    def test_real_eos_supervised_padding_ignored(self):
        records = [
            tokenize_sft_example(
                example(0, " Long completion."),
                self.tokenizer,
                target_eos_token_id=NATIVE_EOS,
            ),
            tokenize_sft_example(
                example(1, " Short."),
                self.tokenizer,
                target_eos_token_id=NATIVE_EOS,
            ),
        ]

        collator = SFTBatchCollator(
            pad_token_id=NATIVE_EOS,
            eos_token_id=NATIVE_EOS,
            max_seq_length=512,
            allow_pad_eos_collision=True,
        )

        batch = collator(records)

        for row, record in enumerate(records):
            last_real_position = record.sequence_length - 1

            # Genuine EOS is both attended and supervised.
            self.assertEqual(
                batch["input_ids"][
                    row, last_real_position
                ].item(),
                NATIVE_EOS,
            )

            self.assertEqual(
                batch["attention_mask"][
                    row, last_real_position
                ].item(),
                1,
            )

            self.assertEqual(
                batch["labels"][
                    row, last_real_position
                ].item(),
                NATIVE_EOS,
            )

            # Prompt tokens are excluded from the loss.
            self.assertTrue(
                (
                    batch["labels"][
                        row, :record.prompt_token_count
                    ] == IGNORE_INDEX
                ).all().item()
            )

            # Padding uses the same input ID,
            # but MUST NOT contribute to the loss.
            if record.sequence_length < batch["input_ids"].shape[1]:
                self.assertTrue(
                    (
                        batch["input_ids"][
                            row, record.sequence_length:
                        ] == NATIVE_EOS
                    ).all().item()
                )

                self.assertTrue(
                    (
                        batch["attention_mask"][
                            row, record.sequence_length:
                        ] == 0
                    ).all().item()
                )

                self.assertTrue(
                    (
                        batch["labels"][
                            row, record.sequence_length:
                        ] == IGNORE_INDEX
                    ).all().item()
                )

            # Causal-LM supervised-token count must include EOS.
            supervised_tokens = (
                batch["labels"][row, 1:] != IGNORE_INDEX
            ).sum().item()

            self.assertEqual(
                supervised_tokens,
                record.completion_token_count + 1,
            )

    def test_invalid_eos_override_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "nonnegative integer",
        ):
            tokenize_sft_example(
                example(2, " Answer."),
                self.tokenizer,
                target_eos_token_id=-1,
            )


if __name__ == "__main__":
    unittest.main()
