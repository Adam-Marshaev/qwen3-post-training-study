"""Tests for mathematical evaluation metrics."""

import unittest

from decimal import Decimal

from llm_post_training.evaluation.metrics import (
    evaluate_response,
    summarize_evaluations,
)


class TestEvaluationMetrics(unittest.TestCase):

    def test_mixed_results(self):
        records = [
            evaluate_response(
                "The answer is 204.\nQuestion: Another problem",
                Decimal("204"),
                generated_tokens=10,
            ),
            evaluate_response(
                "Final answer: 999",
                Decimal("204"),
                generated_tokens=20,
            ),
            evaluate_response(
                "I could not solve this problem.",
                Decimal("3"),
                generated_tokens=30,
            ),
            evaluate_response(
                "The answer is 4. Actually, the answer is 5.",
                Decimal("5"),
                generated_tokens=40,
            ),
            evaluate_response(
                "Final answer: -12.5",
                Decimal("-12.5"),
                generated_tokens=50,
            ),
        ]

        summary = summarize_evaluations(records)

        self.assertEqual(summary.total, 5)
        self.assertEqual(summary.correct, 2)
        self.assertEqual(summary.valid_extractions, 3)
        self.assertEqual(summary.missing_answers, 1)
        self.assertEqual(summary.ambiguous_answers, 1)
        self.assertEqual(summary.unwanted_continuations, 1)

        self.assertAlmostEqual(summary.accuracy, 0.4)
        self.assertAlmostEqual(summary.extraction_rate, 0.6)
        self.assertAlmostEqual(summary.missing_rate, 0.2)
        self.assertAlmostEqual(summary.ambiguous_rate, 0.2)
        self.assertAlmostEqual(
            summary.unwanted_continuation_rate,
            0.2,
        )
        self.assertAlmostEqual(
            summary.mean_generated_tokens,
            30.0,
        )

    def test_empty_evaluation_rejected(self):
        with self.assertRaises(ValueError):
            summarize_evaluations([])

    def test_negative_generated_tokens_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_response(
                "Final answer: 5",
                Decimal("5"),
                generated_tokens=-1,
            )

    def test_decimal_answers_compared_exactly(self):
        expected = Decimal("0.1") + Decimal("0.2")

        record = evaluate_response(
            "Final answer: 0.3",
            expected,
            generated_tokens=5,
        )

        self.assertTrue(record.correct)


    def test_token_cap_aggregation(self):
        records = [
            evaluate_response(
                "Final answer: 48",
                Decimal("48"),
                generated_tokens=10,
                reached_token_cap=True,
            ),
            evaluate_response(
                "Incomplete calculation.",
                Decimal("300"),
                generated_tokens=10,
                reached_token_cap=True,
            ),
            evaluate_response(
                "Final answer: 99",
                Decimal("100"),
                generated_tokens=6,
                reached_token_cap=False,
            ),
        ]

        summary = summarize_evaluations(records)

        self.assertEqual(summary.total, 3)
        self.assertEqual(summary.correct, 1)
        self.assertEqual(summary.reached_token_cap_count, 2)
        self.assertAlmostEqual(
            summary.reached_token_cap_rate,
            2 / 3,
        )

        # Reaching the cap does not automatically mean incorrect.
        self.assertTrue(records[0].correct)
        self.assertTrue(records[0].reached_token_cap)


if __name__ == "__main__":
    unittest.main()
