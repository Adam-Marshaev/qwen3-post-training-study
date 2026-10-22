"""Tests for versioned mathematical reasoning prompts."""

import unittest

from llm_post_training.evaluation.prompting import (
    BASELINE_PROMPT_VERSION,
    format_baseline_prompt,
)


class TestBaselinePrompt(unittest.TestCase):

    def test_prompt_version(self):
        self.assertEqual(
            BASELINE_PROMPT_VERSION,
            "gsm8k_qa_v1",
        )

    def test_exact_prompt_format(self):
        prompt = format_baseline_prompt(
            "What is 5 + 3?"
        )

        self.assertEqual(
            prompt,
            "Question: What is 5 + 3?\nAnswer:",
        )

    def test_trims_outer_whitespace(self):
        prompt = format_baseline_prompt(
            "  What is 5 + 3? \n"
        )

        self.assertEqual(
            prompt,
            "Question: What is 5 + 3?\nAnswer:",
        )

    def test_preserves_multiline_questions(self):
        prompt = format_baseline_prompt(
            "A shop sells apples.\nHow many remain?"
        )

        self.assertEqual(
            prompt,
            "Question: A shop sells apples.\n"
            "How many remain?\n"
            "Answer:",
        )

    def test_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            format_baseline_prompt("   ")

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            format_baseline_prompt(None)


if __name__ == "__main__":
    unittest.main()
