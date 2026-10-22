"""Tests for GSM8K supervised fine-tuning formatting."""

import unittest

from llm_post_training.training.sft_format import (
    format_sft_completion,
    format_sft_example,
)


class TestSFTFormatting(unittest.TestCase):

    def test_exact_prompt_and_completion(self):
        example = format_sft_example(
            question="What is 3 plus 2?",
            reference_solution=(
                "We compute <<3+2=5>>5.\n"
                "#### 5"
            ),
        )

        self.assertEqual(
            example.prompt,
            "Question: What is 3 plus 2?\nAnswer:",
        )

        self.assertEqual(
            example.completion,
            " We compute 5.\nThe answer is 5.",
        )

    def test_full_text_concatenation(self):
        example = format_sft_example(
            "What is 4 times 2?",
            "Multiply 4 and 2 to get 8.\n#### 8",
        )

        self.assertEqual(
            example.full_text,
            "Question: What is 4 times 2?\n"
            "Answer: Multiply 4 and 2 to get 8.\n"
            "The answer is 8.",
        )

    def test_negative_decimal_answer(self):
        completion = format_sft_completion(
            "The temperature changes by -12.5.\n"
            "#### -12.5"
        )

        self.assertEqual(
            completion,
            " The temperature changes by -12.5.\n"
            "The answer is -12.5.",
        )

    def test_thousands_separator_is_normalized(self):
        completion = format_sft_completion(
            "The total is 1,250.\n"
            "#### 1,250"
        )

        self.assertTrue(
            completion.endswith("The answer is 1250.")
        )

    def test_missing_answer_marker_rejected(self):
        with self.assertRaises(ValueError):
            format_sft_completion(
                "The result is five."
            )

    def test_empty_reasoning_rejected(self):
        with self.assertRaises(ValueError):
            format_sft_completion("#### 5")

    def test_malformed_calculator_annotation_rejected(self):
        with self.assertRaises(ValueError):
            format_sft_completion(
                "The result is <<3+2=5.\n"
                "#### 5"
            )

    def test_non_string_solution_rejected(self):
        with self.assertRaises(TypeError):
            format_sft_completion(None)


if __name__ == "__main__":
    unittest.main()
