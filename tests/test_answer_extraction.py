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


    def test_latex_boxed_final_answer(self):
        response = (
            "The calculation gives 3 + 6 = 9.\n"
            "### Final Answer\n"
            + r"\[\boxed{9}\]"
        )

        result = extract_final_answer(response)

        self.assertEqual(result.status, "valid")
        self.assertEqual(result.answer, Decimal("9"))
        self.assertFalse(result.unwanted_continuation)


    def test_latex_boxed_negative_decimal(self):
        result = extract_final_answer(
            r"\boxed{ -12.5 }"
        )

        self.assertEqual(result.status, "valid")
        self.assertEqual(result.answer, Decimal("-12.5"))

    def test_matching_text_and_boxed_answers(self):
        response = (
            "Final answer: 1,250\n"
            + r"\boxed{1250}"
        )

        result = extract_final_answer(response)

        self.assertEqual(result.status, "valid")
        self.assertEqual(result.answer, Decimal("1250"))

    def test_conflicting_text_and_boxed_answers(self):
        response = (
            "Final answer: 8\n"
            + r"\boxed{9}"
        )

        result = extract_final_answer(response)

        self.assertEqual(result.status, "ambiguous")
        self.assertIsNone(result.answer)

    def test_boxed_answer_after_next_question_is_ignored(self):
        response = (
            "The answer is 4.\n"
            "[Question] Another problem.\n"
            + r"\boxed{7}"
        )

        result = extract_final_answer(response)

        self.assertEqual(result.status, "valid")
        self.assertEqual(result.answer, Decimal("4"))
        self.assertTrue(result.unwanted_continuation)

    def test_boxed_expression_is_not_a_numeric_answer(self):
        result = extract_final_answer(
            r"\boxed{3+6}"
        )

        self.assertEqual(result.status, "missing")
        self.assertIsNone(result.answer)


    def test_extraction_policy_version(self):
        from llm_post_training.evaluation.answer_extraction import (
            ANSWER_EXTRACTION_VERSION,
        )

        self.assertEqual(
            ANSWER_EXTRACTION_VERSION,
            "explicit_numeric_v2",
        )


if __name__ == "__main__":
    unittest.main()
