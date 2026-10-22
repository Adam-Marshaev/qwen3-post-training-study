"""Tests for mathematical answer extraction."""

import unittest

from decimal import Decimal

from llm_post_training.evaluation.answer_extraction import (
    extract_final_answer,
)


class TestAnswerExtraction(unittest.TestCase):

    def test_explicit_final_answer(self):
        result = extract_final_answer(
            "The calculation gives 204.\nFinal answer: 204"
        )

        self.assertEqual(result.answer, Decimal("204"))
        self.assertEqual(result.status, "valid")
        self.assertFalse(result.unwanted_continuation)

    def test_natural_language_answer(self):
        result = extract_final_answer(
            "The answer is 204."
        )

        self.assertEqual(result.answer, Decimal("204"))
        self.assertEqual(result.status, "valid")

    def test_negative_decimal_answer(self):
        result = extract_final_answer(
            "Final answer: -12.5"
        )

        self.assertEqual(result.answer, Decimal("-12.5"))

    def test_thousands_separator(self):
        result = extract_final_answer(
            "Final answer: 1,250"
        )

        self.assertEqual(result.answer, Decimal("1250"))

    def test_missing_final_answer(self):
        result = extract_final_answer(
            "240 - 84 = 156. Then 156 + 48 = 204."
        )

        self.assertIsNone(result.answer)
        self.assertEqual(result.status, "missing")

    def test_conflicting_answers(self):
        result = extract_final_answer(
            "The answer is 204. Actually, the answer is 205."
        )

        self.assertIsNone(result.answer)
        self.assertEqual(result.status, "ambiguous")

    def test_unwanted_question_continuation(self):
        response = (
            "240 * .35 = 84 components are shipped. "
            "240 - 84 = 156 components remain. "
            "156 + 48 = 204 components remain. "
            "The answer is 204.\n\n"
            "Question: A train is 100 meters long. "
            "What is its speed?"
        )

        result = extract_final_answer(response)

        self.assertEqual(result.answer, Decimal("204"))
        self.assertEqual(result.status, "valid")
        self.assertTrue(result.unwanted_continuation)


    def test_bracketed_question_continuation(self):
        response = (
            "The answer is 48.\n"
            "[Question]A group of friends buys tickets."
        )

        result = extract_final_answer(response)

        self.assertEqual(result.answer, Decimal("48"))
        self.assertEqual(result.status, "valid")
        self.assertTrue(result.unwanted_continuation)


if __name__ == "__main__":
    unittest.main()
