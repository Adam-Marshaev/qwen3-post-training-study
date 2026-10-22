"""Tests for manifest-restricted GSM8K SFT data preparation."""

import json
import tempfile
import unittest

from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from llm_post_training.data.loader import GSM8KExample
from llm_post_training.training.sft_data import (
    load_sft_training_examples,
)


class TestSFTTrainingData(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.source = Path(temporary.name) / "train.jsonl"
        self.manifest = Path(temporary.name) / "split.json"

        self.records = [
            {
                "question": "What is 2 + 3?",
                "answer": "Add <<2+3=5>>5.\n#### 5",
            },
            {
                "question": "What is 8 + 1?",
                "answer": "Add <<8+1=9>>9.\n#### 9",
            },
            {
                "question": "What is 4 + 3?",
                "answer": "Add <<4+3=7>>7.\n#### 7",
            },
        ]

        self.write_records()

        # Only indices 0 and 2 are approved for training.
        # Index 1 represents an excluded validation example.
        self.approved = [
            GSM8KExample(
                source_index=0,
                question="What is 2 + 3?",
                reference_answer=Decimal("5"),
            ),
            GSM8KExample(
                source_index=2,
                question="What is 4 + 3?",
                reference_answer=Decimal("7"),
            ),
        ]

    def write_records(self):
        content = "".join(
            json.dumps(record) + "\n"
            for record in self.records
        )

        self.source.write_text(
            content,
            encoding="utf-8",
        )

    def load_with_approved_split(self):
        with patch(
            "llm_post_training.training.sft_data."
            "load_gsm8k_split",
            return_value=self.approved,
        ) as loader:
            result = load_sft_training_examples(
                self.source,
                self.manifest,
            )

            loader.assert_called_once_with(
                self.source,
                self.manifest,
                "training",
            )

            return result

    def test_only_approved_training_indices_returned(self):
        examples = self.load_with_approved_split()

        self.assertEqual(
            [example.source_index for example in examples],
            [0, 2],
        )

        self.assertNotIn(
            1,
            {example.source_index for example in examples},
        )

    def test_prompt_and_completion_are_formatted(self):
        examples = self.load_with_approved_split()

        self.assertEqual(
            examples[0].prompt,
            "Question: What is 2 + 3?\nAnswer:",
        )

        self.assertEqual(
            examples[0].completion,
            " Add 5.\nThe answer is 5.",
        )

        self.assertEqual(
            examples[0].full_text,
            examples[0].prompt + examples[0].completion,
        )

    def test_mismatched_question_is_rejected(self):
        self.approved[0] = GSM8KExample(
            source_index=0,
            question="Different question",
            reference_answer=Decimal("5"),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Question mismatch",
        ):
            self.load_with_approved_split()

    def test_mismatched_reference_answer_is_rejected(self):
        self.approved[0] = GSM8KExample(
            source_index=0,
            question="What is 2 + 3?",
            reference_answer=Decimal("100"),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Reference answer mismatch",
        ):
            self.load_with_approved_split()

    def test_malformed_solution_is_rejected(self):
        self.records[0]["answer"] = (
            "Add <<2+3=5.\n#### 5"
        )
        self.write_records()

        with self.assertRaisesRegex(
            ValueError,
            "Malformed GSM8K calculator annotation",
        ):
            self.load_with_approved_split()


if __name__ == "__main__":
    unittest.main()
