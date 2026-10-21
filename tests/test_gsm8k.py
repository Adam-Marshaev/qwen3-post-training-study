"""Tests for GSM8K reference-answer parsing."""

import unittest
from decimal import Decimal

from llm_post_training.data.gsm8k import (
    parse_gsm8k_reference_answer,
)


class TestGSM8KReferenceParsing(unittest.TestCase):

    def test_realistic_gsm8k_solution(self):
        solution = (
            "Natalia sold 48/2 = <<48/2=24>>24 clips in May.\n"
            "Natalia sold 48+24 = <<48+24=72>>72 clips.\n"
            "#### 72"
        )

        result = parse_gsm8k_reference_answer(solution)

        self.assertEqual(result, Decimal("72"))

    def test_thousands_separator(self):
        result = parse_gsm8k_reference_answer(
            "The calculation gives 1250.\n#### 1,250"
        )

        self.assertEqual(result, Decimal("1250"))

    def test_negative_decimal(self):
        result = parse_gsm8k_reference_answer(
            "Compute the difference.\n#### -12.5"
        )

        self.assertEqual(result, Decimal("-12.5"))

    def test_missing_marker_rejected(self):
        with self.assertRaises(ValueError):
            parse_gsm8k_reference_answer(
                "The final answer is 72."
            )

    def test_invalid_number_rejected(self):
        with self.assertRaises(ValueError):
            parse_gsm8k_reference_answer(
                "Calculation complete.\n#### 1,25"
            )

    def test_trailing_text_rejected(self):
        with self.assertRaises(ValueError):
            parse_gsm8k_reference_answer(
                "Calculation complete.\n"
                "#### 72\n"
                "Another answer: 73"
            )

    def test_multiple_final_answers_rejected(self):
        with self.assertRaises(ValueError):
            parse_gsm8k_reference_answer(
                "#### 72\n#### 73"
            )


if __name__ == "__main__":
    unittest.main()
