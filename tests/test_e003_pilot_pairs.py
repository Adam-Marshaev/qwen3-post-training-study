"""CPU-only tests for E003 provisional pair materialization (no GPU, no training)."""

import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from scripts.build_e003_pilot_pairs import (
    NATIVE_EOS, audit_candidate, audit_review,
    candidate_is_eligible, select_pairs,
)

REVIEW_PATH = Path("configs/preference/e003_pilot_reasoning_screen_v1.json")


def frozen_review():
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def synthetic_candidates(review):
    """Make 32 four-candidate groups with the exact 21 audited mixed groups."""
    records = []
    reviewed = {r["source_index"]: r for r in review["rows"]}
    all_indices = sorted(reviewed) + list(range(8000, 8011))
    for index in all_indices:
        row = reviewed.get(index)
        for sample in range(4):
            correct = sample == 0 if row else False
            length = 12
            if row:
                if row["screening_status"] == "PROVISIONAL_APPROVE":
                    correct = sample == row["chosen_sample_index"]
                    if sample == row["chosen_sample_index"]:
                        length = row["chosen_generated_tokens"]
                    if sample == row["rejected_sample_index"]:
                        length = row["rejected_generated_tokens"]
                else:
                    correct = sample == 0
            ids = [7] * (length - 1) + [NATIVE_EOS]
            records.append({
                "source_index": index, "sample_index": sample,
                "eligible": True, "correct": correct, "native_eos_stop": True,
                "reached_token_cap": False, "extraction_status": "valid",
                "unwanted_continuation": False,
                "generated_token_ids": ids, "generated_tokens": length,
                "prompt": f"Question {index}", "reference_answer": "4",
                "response": f"Sample {index}:{sample}. The answer is {4 if correct else 5}.",
            })
    return records


class TestE003ProvisionalPairs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = frozen_review()

    def test_review_counts_and_guardrails(self):
        rows = audit_review(self.review)
        self.assertEqual(len(rows), 21)
        self.assertEqual(sum(r["screening_status"] == "PROVISIONAL_APPROVE" for r in rows.values()), 18)

    def test_selects_exactly_18_provisional_pairs(self):
        data = synthetic_candidates(self.review)
        pairs = select_pairs(self.review, data)
        self.assertEqual(len(pairs), 18)
        self.assertEqual(len({p["source_index"] for p in pairs}), 18)
        self.assertTrue(all(p["training_approved"] is False for p in pairs))
        self.assertTrue(all(p["chosen_generated_token_ids"][-1] == NATIVE_EOS for p in pairs))

    def test_determinism_and_nonmutation(self):
        data = synthetic_candidates(self.review)
        before = copy.deepcopy(data)
        self.assertEqual(select_pairs(self.review, data), select_pairs(self.review, list(reversed(data))))
        self.assertEqual(data, before)

    def test_review_cannot_self_approve_training(self):
        review = copy.deepcopy(self.review)
        review["human_signoff_required_before_training"] = False
        with self.assertRaisesRegex(ValueError, "signoff"):
            audit_review(review)

    def test_review_rejects_duplicate_source_index(self):
        review = copy.deepcopy(self.review)
        review["rows"][1]["source_index"] = review["rows"][0]["source_index"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit_review(review)

    def test_rejects_bad_chosen_correctness(self):
        data = synthetic_candidates(self.review)
        chosen = next(r for r in data if r["source_index"] == 250 and r["sample_index"] == 0)
        chosen["correct"] = False
        # Preserve a mixed group so this reaches the selected-chosen audit.
        alternative = next(r for r in data if r["source_index"] == 250 and r["sample_index"] == 1)
        alternative["correct"] = True
        with self.assertRaisesRegex(ValueError, "Chosen"):
            select_pairs(self.review, data)

    def test_rejects_bad_native_eos(self):
        data = synthetic_candidates(self.review)
        chosen = next(r for r in data if r["source_index"] == 250 and r["sample_index"] == 0)
        chosen["generated_token_ids"][-1] = 151645
        with self.assertRaisesRegex(ValueError, "EOS"):
            select_pairs(self.review, data)

    def test_rejects_duplicate_candidate_identity(self):
        data = synthetic_candidates(self.review)
        data[1]["sample_index"] = data[0]["sample_index"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            select_pairs(self.review, data)

    def test_rejects_nonmixed_review_group(self):
        data = synthetic_candidates(self.review)
        for r in data:
            if r["source_index"] == 234:
                r["correct"] = False
        with self.assertRaisesRegex(ValueError, "mixed groups"):
            select_pairs(self.review, data)

    def test_candidate_integrity_regrades_extraction(self):
        response = " Work. The answer is 4."
        ids = [15, 16, NATIVE_EOS]
        record = {
            "source_index": 250, "sample_index": 2,
            "prompt": "Question 250", "reference_answer": "4",
            "sample_seed": 42 + 250 * 100 + 2,
            "generated_token_ids": ids, "generated_tokens": 3,
            "native_eos_stop": True, "reached_token_cap": False,
            "response": response, "eligible": True,
            "extraction_status": "valid", "unwanted_continuation": False,
            "extracted_answer": "4", "correct": True,
        }
        class Tokenizer:
            def __len__(self): return 160000
            def decode(self, ids, skip_special_tokens):
                return response if ids == [15, 16, NATIVE_EOS] and skip_special_tokens else "wrong"
        def evaluator(**kwargs):
            # Catch the integration bug: JSON stores "4", but metric grading
            # requires the original numeric reference-answer semantics.
            self.assertIsInstance(kwargs["expected_answer"], Decimal)
            self.assertEqual(kwargs["expected_answer"], Decimal("4"))
            return SimpleNamespace(
                correct=(kwargs["expected_answer"] == Decimal("4")),
                extraction=SimpleNamespace(
                    answer=4, status="valid", unwanted_continuation=False,
                ),
            )
        audit_candidate(record, "Question 250", "4", 256, 42, Tokenizer(), evaluator)
        record["generated_token_ids"] = [15, 17, NATIVE_EOS]
        with self.assertRaisesRegex(ValueError, "Token/text"):
            audit_candidate(record, "Question 250", "4", 256, 42, Tokenizer(), evaluator)

    def test_numeric_reference_preserved_for_wrong_answer(self):
        response = " Work. The answer is 5."
        ids = [15, 16, NATIVE_EOS]
        record = {
            "source_index": 250, "sample_index": 2,
            "prompt": "Question 250", "reference_answer": "4",
            "sample_seed": 42 + 250 * 100 + 2,
            "generated_token_ids": ids, "generated_tokens": 3,
            "native_eos_stop": True, "reached_token_cap": False,
            "response": response, "eligible": True,
            "extraction_status": "valid", "unwanted_continuation": False,
            "extracted_answer": "5", "correct": False,
        }
        class Tokenizer:
            def __len__(self): return 160000
            def decode(self, ids, skip_special_tokens):
                return response if ids == [15, 16, NATIVE_EOS] and skip_special_tokens else "wrong"
        def evaluator(**kwargs):
            self.assertIsInstance(kwargs["expected_answer"], Decimal)
            self.assertEqual(kwargs["expected_answer"], Decimal("4"))
            return SimpleNamespace(
                correct=(Decimal("5") == kwargs["expected_answer"]),
                extraction=SimpleNamespace(
                    answer=Decimal("5"), status="valid", unwanted_continuation=False,
                ),
            )
        audit_candidate(record, "Question 250", "4", 256, 42, Tokenizer(), evaluator)

    def test_advisory_review_must_not_become_training_approval(self):
        pairs = select_pairs(self.review, synthetic_candidates(self.review))
        self.assertEqual({p["annotation_status"] for p in pairs},
                         {"provisional_requires_independent_signoff"})
        self.assertFalse(any(p["training_approved"] for p in pairs))


if __name__ == "__main__":
    unittest.main()
