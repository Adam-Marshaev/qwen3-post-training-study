"""Tests for manifest-aware GSM8K loading."""

import hashlib
import json
import tempfile
import unittest

from decimal import Decimal
from pathlib import Path

from llm_post_training.data.loader import load_gsm8k_split


SOURCE_REVISION = "3101c7d5072418e28b9008a6636bde82a006892c"


def make_fixture(
    directory: Path,
) -> tuple[Path, Path, dict]:
    """Create a minimal synthetic GSM8K dataset and manifest."""

    records = [
        {"question": "Question A", "answer": "Work.\n#### 1"},
        {"question": "Question B", "answer": "Work.\n#### 2"},
        {"question": "Question C", "answer": "Work.\n#### 3"},
        {"question": "Question D", "answer": "Work.\n#### 4"},
    ]

    source = directory / "train.jsonl"
    manifest_path = directory / "split.json"

    payload = "".join(
        json.dumps(record) + "\n"
        for record in records
    ).encode("utf-8")

    source.write_bytes(payload)

    (directory / "source_commit.txt").write_text(
        SOURCE_REVISION + "\n",
        encoding="utf-8",
    )

    manifest = {
        "dataset": "openai/grade-school-math",
        "source_commit": SOURCE_REVISION,
        "source_sha256": hashlib.sha256(payload).hexdigest(),
        "split_version": 1,
        "total_examples": 4,
        "training_count": 3,
        "validation_count": 1,
        "training_indices": [0, 1, 2],
        "validation_indices": [3],
    }

    manifest_path.write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )

    return source, manifest_path, manifest


class TestDatasetLoader(unittest.TestCase):

    def test_loads_expected_validation_example(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest_path, _ = make_fixture(
                Path(temporary)
            )

            examples = load_gsm8k_split(
                source,
                manifest_path,
                "validation",
            )

            self.assertEqual(len(examples), 1)
            self.assertEqual(examples[0].source_index, 3)
            self.assertEqual(examples[0].question, "Question D")
            self.assertEqual(
                examples[0].reference_answer,
                Decimal("4"),
            )

    def test_rejects_modified_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest_path, _ = make_fixture(
                Path(temporary)
            )

            source.write_bytes(
                source.read_bytes() + b"\n"
            )

            with self.assertRaisesRegex(
                ValueError, "checksum"
            ):
                load_gsm8k_split(
                    source, manifest_path, "training"
                )

    def test_rejects_overlapping_indices(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest_path, manifest = make_fixture(
                Path(temporary)
            )

            manifest["validation_indices"] = [2]
            manifest_path.write_text(json.dumps(manifest))

            with self.assertRaisesRegex(
                ValueError, "overlap"
            ):
                load_gsm8k_split(
                    source, manifest_path, "validation"
                )

    def test_rejects_out_of_range_index(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest_path, manifest = make_fixture(
                Path(temporary)
            )

            manifest["validation_indices"] = [99]
            manifest_path.write_text(json.dumps(manifest))

            with self.assertRaisesRegex(
                ValueError, "Invalid"
            ):
                load_gsm8k_split(
                    source, manifest_path, "validation"
                )

    def test_rejects_question_leakage(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)

            source, manifest_path, manifest = make_fixture(
                directory
            )

            records = [
                json.loads(line)
                for line in source.read_text().splitlines()
            ]

            records[3]["question"] = "question   a"

            payload = "".join(
                json.dumps(record) + "\n"
                for record in records
            ).encode("utf-8")

            source.write_bytes(payload)

            manifest["source_sha256"] = hashlib.sha256(
                payload
            ).hexdigest()

            manifest_path.write_text(json.dumps(manifest))

            with self.assertRaisesRegex(
                ValueError, "Normalized question"
            ):
                load_gsm8k_split(
                    source, manifest_path, "validation"
                )

    def test_rejects_revision_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)

            source, manifest_path, _ = make_fixture(
                directory
            )

            (directory / "source_commit.txt").write_text(
                "different-revision\n"
            )

            with self.assertRaisesRegex(
                ValueError, "revision"
            ):
                load_gsm8k_split(
                    source, manifest_path, "validation"
                )


if __name__ == "__main__":
    unittest.main()
