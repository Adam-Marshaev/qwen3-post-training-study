"""CPU-only safety and deterministic-output tests for E003 regrading."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts import regrade_e003_reference_erratum_v1 as mod


def fake_judgment(response, expected_answer, generated_tokens, reached_token_cap):
    import re
    from decimal import Decimal
    last = re.findall(r"The answer is (\d+)\.", response)[-1]
    extraction = SimpleNamespace(status="valid", answer=Decimal(last), unwanted_continuation=False)
    return SimpleNamespace(correct=(Decimal(last) == expected_answer), extraction=extraction)


def sample_rows():
    rows = []
    for idx, answer in enumerate(("55", "55", "50", "55")):
        rows.append({
            "source_index": mod.SOURCE,
            "sample_index": idx,
            "sample_seed": 42 + mod.SOURCE * 100 + idx,
            "prompt": "Question: Test\nAnswer:",
            "reference_answer": "55",
            "response": "There are four intervals. The answer is " + answer + ".",
            "generated_token_ids": [100, 101, 151643],
            "generated_tokens": 3,
            "native_eos_stop": True,
            "reached_token_cap": False,
            "extraction_status": "valid",
            "extracted_answer": answer,
            "unwanted_continuation": False,
            "correct": idx != 2,
            "eligible": True,
        })
    return rows


class RegradeTests(unittest.TestCase):
    def test_expected_label_inversion(self):
        derived = mod.build_derivative(sample_rows(), "Question: Test\nAnswer:", fake_judgment)
        self.assertEqual([r["corrected_correct"] for r in derived], [False, False, True, False])
        self.assertEqual([r["original_candidate"]["correct"] for r in derived], [True, True, False, True])

    def test_source_rows_untouched(self):
        rows = sample_rows()
        before = json.dumps(rows, sort_keys=True)
        mod.build_derivative(rows, "Question: Test\nAnswer:", fake_judgment)
        self.assertEqual(before, json.dumps(rows, sort_keys=True))

    def test_numeric_reference_types_are_decimal(self):
        def strict_grader(**kwargs):
            from decimal import Decimal
            self.assertIsInstance(kwargs["expected_answer"], Decimal)
            return fake_judgment(**kwargs)
        mod.build_derivative(sample_rows(), "Question: Test\nAnswer:", strict_grader)

    def test_bad_reference_rejected(self):
        rows = sample_rows()
        rows[0]["reference_answer"] = "50"
        with self.assertRaisesRegex(ValueError, "Original reference mismatch"):
            mod.build_derivative(rows, "Question: Test\nAnswer:", fake_judgment)

    def test_bad_eos_rejected(self):
        rows = sample_rows()
        rows[1]["generated_token_ids"][-1] = 151645
        with self.assertRaisesRegex(ValueError, "EOS"):
            mod.build_derivative(rows, "Question: Test\nAnswer:", fake_judgment)

    def test_bad_original_correctness_rejected(self):
        rows = sample_rows()
        rows[2]["correct"] = True
        with self.assertRaisesRegex(ValueError, "Original correctness audit"):
            mod.build_derivative(rows, "Question: Test\nAnswer:", fake_judgment)

    def test_bad_sample_seed_rejected(self):
        rows = sample_rows()
        rows[1]["sample_seed"] += 1
        with self.assertRaisesRegex(ValueError, "seed"):
            mod.build_derivative(rows, "Question: Test\nAnswer:", fake_judgment)

    def test_bad_extraction_rejected(self):
        rows = sample_rows()
        rows[1]["extraction_status"] = "missing"
        with self.assertRaisesRegex(ValueError, "eligible"):
            mod.build_derivative(rows, "Question: Test\nAnswer:", fake_judgment)

    def test_duplicate_source_record_rejected(self):
        rows = sample_rows()
        with self.assertRaises(ValueError):
            mod.choose_source_records(rows * 256)

    def test_canonical_serialization_is_deterministic(self):
        rows = mod.build_derivative(sample_rows(), "Question: Test\nAnswer:", fake_judgment)
        first = mod.canonical_jsonl(rows)
        self.assertEqual(first, mod.canonical_jsonl(rows))
        self.assertTrue(first.endswith("\n"))
        self.assertEqual(first.count("\n"), 4)

    def test_no_existing_output_overwritten(self):
        with tempfile.TemporaryDirectory() as dirname:
            output = Path(dirname) / "immutable"
            output.mkdir()
            original = output / "keep.txt"
            original.write_text("unchanged", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "overwrit"):
                mod.atomic_publish(output, {"keep.txt": "changed"})
            self.assertEqual(original.read_text(encoding="utf-8"), "unchanged")

    def test_atomic_output_and_manifest_flags(self):
        rows = mod.build_derivative(sample_rows(), "Question: Test\nAnswer:", fake_judgment)
        contents = mod.canonical_jsonl(rows)
        manifest = mod.create_manifest(rows, {"decision": "APPROVED", "scope": "test"},
                                       "scriptsha", "f" * 40,
                                       mod.sha256_bytes(contents.encode("utf-8")))
        flags = manifest["flags"]
        self.assertTrue(flags["derived_regrading_performed"])
        self.assertFalse(flags["dpo_training_approved"])
        self.assertFalse(flags["source_5436_pair_approved"])
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "derivative"
            mod.atomic_publish(path, {
                "regraded_candidates.jsonl": contents,
                "manifest.json": mod.canonical_json(manifest),
            })
            self.assertEqual(mod.sha256_file(path / "regraded_candidates.jsonl"),
                             manifest["derived_candidates_jsonl_sha256"])


if __name__ == "__main__":
    unittest.main()
