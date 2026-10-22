"""Tests for reproducible GSM8K splitting."""

import unittest

from llm_post_training.data.splitting import build_split


def make_record(question: str, answer: int) -> dict[str, str]:
    return {
        "question": question,
        "answer": f"Calculation complete.\n#### {answer}",
    }


class TestDataSplitting(unittest.TestCase):

    def test_reproducible_split(self):
        records = [
            make_record(f"Question {index}", index)
            for index in range(20)
        ]

        first = build_split(records, seed=42)
        second = build_split(records, seed=42)

        self.assertEqual(first, second)

        training, validation = first

        self.assertEqual(len(training), 18)
        self.assertEqual(len(validation), 2)

        self.assertFalse(set(training) & set(validation))

        self.assertEqual(
            sorted(training + validation),
            list(range(20)),
        )

    def test_duplicates_remain_in_same_split(self):
        records = [
            make_record(f"Question {index}", index)
            for index in range(18)
        ]

        records.extend([
            make_record("How many apples?", 5),
            make_record("how many   apples?", 5),
        ])

        training, validation = build_split(records)

        self.assertEqual(18 in training, 19 in training)
        self.assertEqual(18 in validation, 19 in validation)

    def test_conflicting_duplicate_answers_rejected(self):
        records = [
            make_record("How many apples?", 5),
            make_record("how many apples?", 6),
        ]

        with self.assertRaises(ValueError):
            build_split(records)

    def test_invalid_validation_fraction_rejected(self):
        records = [
            make_record("Question one", 1),
            make_record("Question two", 2),
        ]

        with self.assertRaises(ValueError):
            build_split(records, validation_fraction=0)

        with self.assertRaises(ValueError):
            build_split(records, validation_fraction=1)

    def test_single_question_group_rejected(self):
        records = [
            make_record("Same question", 5),
            make_record("same question", 5),
        ]

        with self.assertRaises(ValueError):
            build_split(records)


if __name__ == "__main__":
    unittest.main()
