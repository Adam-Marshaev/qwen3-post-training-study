"""Tests for completion-only SFT tokenization."""

import unittest

from llm_post_training.training.sft_data import (
    SFTTrainingExample,
)
from llm_post_training.training.sft_tokenization import (
    IGNORE_INDEX,
    tokenize_sft_example,
)


class FakeTokenizer:
    eos_token_id = 151645
    pad_token_id = 151643

    def __init__(self):
        self.calls = []

    def encode(self, text, *, add_special_tokens):
        self.calls.append((text, add_special_tokens))
        return list(text.encode("utf-8"))


class TestSFTTokenization(unittest.TestCase):

    def setUp(self):
        self.tokenizer = FakeTokenizer()

        self.example = SFTTrainingExample(
            source_index=11,
            prompt="Question: 2 + 3?\nAnswer:",
            completion=" Add 2 and 3 to get 5.\nThe answer is 5.",
        )

    def test_exact_training_sequence(self):
        result = tokenize_sft_example(
            self.example,
            self.tokenizer,
        )

        prompt_ids = list(
            self.example.prompt.encode("utf-8")
        )

        completion_ids = list(
            self.example.completion.encode("utf-8")
        )

        expected_input = (
            prompt_ids
            + completion_ids
            + [151645]
        )

        expected_labels = (
            [IGNORE_INDEX] * len(prompt_ids)
            + completion_ids
            + [151645]
        )

        self.assertEqual(result.source_index, 11)
        self.assertEqual(result.input_ids, tuple(expected_input))
        self.assertEqual(result.labels, tuple(expected_labels))
        self.assertEqual(
            result.attention_mask,
            (1,) * len(expected_input),
        )

    def test_prompt_positions_are_ignored(self):
        result = tokenize_sft_example(
            self.example,
            self.tokenizer,
        )

        boundary = result.prompt_token_count

        self.assertTrue(
            all(label == -100 for label in result.labels[:boundary])
        )

        self.assertEqual(
            result.labels[boundary:-1],
            result.input_ids[boundary:-1],
        )

    def test_eos_is_supervised_not_padding(self):
        result = tokenize_sft_example(
            self.example,
            self.tokenizer,
        )

        self.assertEqual(result.input_ids[-1], 151645)
        self.assertEqual(result.labels[-1], 151645)

        self.assertNotEqual(
            result.labels[-1],
            self.tokenizer.pad_token_id,
        )

    def test_no_automatic_special_tokens(self):
        tokenize_sft_example(
            self.example,
            self.tokenizer,
        )

        self.assertEqual(
            self.tokenizer.calls,
            [
                (self.example.prompt, False),
                (self.example.completion, False),
            ],
        )

    def test_missing_eos_is_rejected(self):
        self.tokenizer.eos_token_id = None

        with self.assertRaisesRegex(ValueError, "EOS"):
            tokenize_sft_example(
                self.example,
                self.tokenizer,
            )

    def test_empty_completion_is_rejected(self):
        example = SFTTrainingExample(
            source_index=11,
            prompt="Question: 2 + 3?\nAnswer:",
            completion="",
        )

        with self.assertRaisesRegex(ValueError, "Completion"):
            tokenize_sft_example(
                example,
                self.tokenizer,
            )


if __name__ == "__main__":
    unittest.main()
