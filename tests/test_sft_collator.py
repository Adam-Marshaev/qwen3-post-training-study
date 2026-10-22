"""Tests for dynamic SFT batch padding and label masking."""

import unittest

from dataclasses import replace

from llm_post_training.training.sft_collator import (
    SFTBatchCollator,
)
from llm_post_training.training.sft_tokenization import (
    IGNORE_INDEX,
    SFTTokenizedExample,
)


PAD = 151643
EOS = 151645


def make_example(
    source_index,
    prompt_ids,
    completion_ids,
):
    """Construct a valid synthetic tokenized SFT example."""

    prompt_ids = tuple(prompt_ids)
    completion_ids = tuple(completion_ids)

    input_ids = prompt_ids + completion_ids + (EOS,)

    labels = (
        (IGNORE_INDEX,) * len(prompt_ids)
        + completion_ids
        + (EOS,)
    )

    return SFTTokenizedExample(
        source_index=source_index,
        input_ids=input_ids,
        attention_mask=(1,) * len(input_ids),
        labels=labels,
        prompt_token_count=len(prompt_ids),
        completion_token_count=len(completion_ids),
    )


class TestSFTBatchCollator(unittest.TestCase):

    def setUp(self):
        self.collator = SFTBatchCollator(
            pad_token_id=PAD,
            eos_token_id=EOS,
            max_seq_length=512,
        )

        self.short = make_example(
            source_index=0,
            prompt_ids=[10, 11],
            completion_ids=[20, 21],
        )

        self.long = make_example(
            source_index=1,
            prompt_ids=[12, 13, 14],
            completion_ids=[22, 23, 24, 25],
        )

    def test_dynamic_padding_and_shapes(self):
        batch = self.collator(
            [self.short, self.long]
        )

        self.assertEqual(
            tuple(batch["input_ids"].shape),
            (2, 8),
        )

        self.assertEqual(
            tuple(batch["attention_mask"].shape),
            (2, 8),
        )

        self.assertEqual(
            tuple(batch["labels"].shape),
            (2, 8),
        )

        self.assertEqual(
            batch["input_ids"][0].tolist(),
            [10, 11, 20, 21, EOS, PAD, PAD, PAD],
        )

        self.assertEqual(
            batch["attention_mask"][0].tolist(),
            [1, 1, 1, 1, 1, 0, 0, 0],
        )

        self.assertEqual(
            batch["labels"][0].tolist(),
            [-100, -100, 20, 21, EOS, -100, -100, -100],
        )

    def test_eos_is_supervised_before_padding(self):
        batch = self.collator(
            [self.short, self.long]
        )

        self.assertEqual(
            batch["input_ids"][0, 4].item(),
            EOS,
        )

        self.assertEqual(
            batch["labels"][0, 4].item(),
            EOS,
        )

        self.assertEqual(
            batch["attention_mask"][0, 4].item(),
            1,
        )

    def test_single_example_has_no_padding(self):
        batch = self.collator([self.short])

        self.assertEqual(
            tuple(batch["input_ids"].shape),
            (1, 5),
        )

        self.assertEqual(
            batch["attention_mask"][0].tolist(),
            [1, 1, 1, 1, 1],
        )

    def test_empty_batch_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "empty",
        ):
            self.collator([])

    def test_sequence_limit_enforced(self):
        collator = SFTBatchCollator(
            pad_token_id=PAD,
            eos_token_id=EOS,
            max_seq_length=7,
        )

        with self.assertRaisesRegex(
            ValueError,
            "exceeds",
        ):
            collator([self.short, self.long])

    def test_wrong_eos_rejected(self):
        malformed = replace(
            self.short,
            input_ids=self.short.input_ids[:-1] + (PAD,),
        )

        with self.assertRaisesRegex(
            ValueError,
            "EOS",
        ):
            self.collator([malformed])

    def test_unmasked_prompt_rejected(self):
        malformed = replace(
            self.short,
            labels=(10,) + self.short.labels[1:],
        )

        with self.assertRaisesRegex(
            ValueError,
            "prompt labels",
        ):
            self.collator([malformed])

    def test_masked_completion_rejected(self):
        malformed = replace(
            self.short,
            labels=(
                self.short.labels[:2]
                + (-100,)
                + self.short.labels[3:]
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "completion labels",
        ):
            self.collator([malformed])

    def test_inconsistent_length_metadata_rejected(self):
        malformed = replace(
            self.short,
            completion_token_count=3,
        )

        with self.assertRaisesRegex(
            ValueError,
            "length metadata",
        ):
            self.collator([malformed])

    def test_pad_and_eos_must_differ(self):
        with self.assertRaisesRegex(
            ValueError,
            "distinct",
        ):
            SFTBatchCollator(
                pad_token_id=EOS,
                eos_token_id=EOS,
            )


if __name__ == "__main__":
    unittest.main()
