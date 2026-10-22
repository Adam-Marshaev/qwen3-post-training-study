"""CPU-only safety tests for versioned E003 intermediate candidate generation."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.generate_e003_scale_v1 import (
    ADAPTER_SHA, MAX_TOKENS, NATIVE_EOS, PILOT_CONFIG_SHA, PILOT_REVISION,
    SELECTED_COUNT, SAMPLES, atomic_write, candidate_is_eligible,
    choose_disjoint_questions, group_is_mixed, output_summary,
    read_group, validate_config, validate_group, validate_record,
)

CONFIG = Path("configs/preference/e003_scale_v1.json")
PILOT_CONFIG = Path("configs/preference/e003_pilot_v1.json")


def mock_pilot():
    cfg = json.loads(PILOT_CONFIG.read_text(encoding="utf-8"))
    from random import Random
    training = [SimpleNamespace(source_index=i, question=f"Problem {i}",
                                reference_answer=2) for i in range(6726)]
    excluded = sorted(Random(42).sample(range(6726), 32))
    meta = {
        "run_type": "e003_preference_candidate_pilot", "code_revision": PILOT_REVISION,
        "config_sha256": PILOT_CONFIG_SHA, "config": cfg,
        "training_only": True, "reference_policy_adapter_sha256": ADAPTER_SHA,
        "selected_source_indices": excluded,
    }
    summary = {
        "candidates": 128, "pilot_questions": 32,
        "training_performed": False, "official_test_used": False,
        "code_revision": PILOT_REVISION,
    }
    return training, meta, summary, cfg


class Tokenizer:
    def __len__(self):
        return 160000

    def decode(self, ids, skip_special_tokens):
        return " Work. The answer is 2." if ids == [18, NATIVE_EOS] else "mismatch"


def fake_candidate(sample):
    return {
        "source_index": 250, "sample_index": sample,
        "sample_seed": 42 + 250 * 100 + sample,
        "prompt": "Question: Problem 250\nAnswer:",
        "reference_answer": "2", "response": " Work. The answer is 2.",
        "generated_token_ids": [18, NATIVE_EOS], "generated_tokens": 2,
        "generation_seconds": 1.5, "native_eos_stop": True,
        "reached_token_cap": False, "extraction_status": "valid",
        "extracted_answer": "2", "unwanted_continuation": False,
        "correct": True, "eligible": True,
    }


class TestE003ScaleGenerator(unittest.TestCase):
    def test_config_exact(self):
        validate_config(json.loads(CONFIG.read_text(encoding="utf-8")))

    def test_reject_changed_budget_cache_and_split(self):
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        for path, value in (
            (("scale_questions",), 32),
            (("samples_per_question",), 8),
            (("split",), "validation"),
            (("generation", "use_cache"), False),
            (("generation", "eos_token_id"), 151645),
            (("selection_seed",), 42),
        ):
            changed = copy.deepcopy(cfg)
            if len(path) == 1:
                changed[path[0]] = value
            else:
                changed[path[0]][path[1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_config(changed)

    def test_disjoint_and_reproducible_selection(self):
        training, meta, summary, cfg = mock_pilot()
        a, excluded = choose_disjoint_questions(training, meta, summary, cfg)
        b, excluded2 = choose_disjoint_questions(list(reversed(training)), meta, summary, cfg)
        self.assertEqual([x.source_index for x in a], [x.source_index for x in b])
        self.assertEqual(excluded, excluded2)
        self.assertEqual(len(a), SELECTED_COUNT)
        self.assertTrue(set(excluded).isdisjoint(x.source_index for x in a))

    def test_reject_modified_pilot_selected_indices(self):
        training, meta, summary, cfg = mock_pilot()
        meta["selected_source_indices"][0] = 99999
        with self.assertRaisesRegex(ValueError, "Pilot selected indices"):
            choose_disjoint_questions(training, meta, summary, cfg)

    def test_reject_modified_pilot_provenance(self):
        training, meta, summary, cfg = mock_pilot()
        meta["code_revision"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "Pilot revision"):
            choose_disjoint_questions(training, meta, summary, cfg)

    def test_reject_modified_pilot_summary(self):
        training, meta, summary, cfg = mock_pilot()
        summary["official_test_used"] = True
        with self.assertRaisesRegex(ValueError, "Pilot summary"):
            choose_disjoint_questions(training, meta, summary, cfg)

    def test_atomic_write_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "source_00250.jsonl"
            atomic_write(f, "first\n")
            self.assertEqual(f.read_text(), "first\n")
            with self.assertRaises(FileExistsError):
                atomic_write(f, "second\n")
            self.assertEqual(f.read_text(), "first\n")
            self.assertFalse(any(p.name.startswith(".incomplete_") for p in Path(d).iterdir()))

    def test_validate_all_four_candidates(self):
        example = SimpleNamespace(source_index=250, question="Problem 250", reference_answer=2)
        rows = [fake_candidate(i) for i in range(SAMPLES)]
        with patch("scripts.generate_e003_scale_v1.format_baseline_prompt",
                   return_value="Question: Problem 250\nAnswer:"), patch(
                "scripts.generate_e003_scale_v1.evaluate_response",
                return_value=SimpleNamespace(correct=True, extraction=SimpleNamespace(
                    status="valid", answer=2, unwanted_continuation=False))):
            validate_group(rows, example, Tokenizer())

    def test_reject_corrupted_token_text_and_eos(self):
        example = SimpleNamespace(source_index=250, question="Problem 250", reference_answer=2)
        with patch("scripts.generate_e003_scale_v1.format_baseline_prompt",
                   return_value="Question: Problem 250\nAnswer:"), patch(
                "scripts.generate_e003_scale_v1.evaluate_response",
                return_value=SimpleNamespace(correct=True, extraction=SimpleNamespace(
                    status="valid", answer=2, unwanted_continuation=False))):
            record = fake_candidate(0)
            record["generated_token_ids"] = [19, NATIVE_EOS]
            with self.assertRaisesRegex(ValueError, "Token-to-text"):
                validate_record(record, example, Tokenizer())
            record = fake_candidate(0)
            record["native_eos_stop"] = False
            with self.assertRaisesRegex(ValueError, "EOS label"):
                validate_record(record, example, Tokenizer())

    def test_reject_wrong_regraded_correctness_and_type(self):
        example = SimpleNamespace(source_index=250, question="Problem 250", reference_answer=2)
        seen = []
        def evaluator(**kwargs):
            seen.append(kwargs["expected_answer"])
            return SimpleNamespace(correct=True, extraction=SimpleNamespace(
                status="valid", answer=2, unwanted_continuation=False))
        with patch("scripts.generate_e003_scale_v1.format_baseline_prompt",
                   return_value="Question: Problem 250\nAnswer:"), patch(
                "scripts.generate_e003_scale_v1.evaluate_response", side_effect=evaluator):
            validate_record(fake_candidate(0), example, Tokenizer())
            self.assertEqual(seen, [2])
            record = fake_candidate(0)
            record["correct"] = False
            with self.assertRaisesRegex(ValueError, "Regraded correctness"):
                validate_record(record, example, Tokenizer())

    def test_read_group_rejects_duplicate_sample(self):
        example = SimpleNamespace(source_index=250, question="Problem 250", reference_answer=2)
        rows = [fake_candidate(i) for i in [0, 1, 2, 2]]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "source_00250.jsonl"
            p.write_text("".join(json.dumps(r) + "\n" for r in rows))
            with self.assertRaisesRegex(ValueError, "Duplicate or missing"):
                read_group(p, example, Tokenizer())

    def test_summary_aggregates_and_no_training(self):
        # All 256 groups and 1024 candidates; deterministic purely CPU fixture.
        selected = [SimpleNamespace(source_index=i) for i in range(SELECTED_COUNT)]
        rows = []
        for index in range(SELECTED_COUNT):
            for sample in range(SAMPLES):
                r = fake_candidate(sample)
                r["source_index"] = index
                r["correct"] = sample == 0
                rows.append(r)
        result = output_summary(rows, selected, "abc", "f" * 40, None)
        self.assertEqual(result["candidates"], 1024)
        self.assertEqual(result["mixed_groups_with_potential_pair"], SELECTED_COUNT)
        self.assertIs(result["training_performed"], False)
        self.assertIs(result["official_test_used"], False)


if __name__ == "__main__":
    unittest.main()
