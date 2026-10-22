"""Safeguards for adapter-aware GSM8K evaluation."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_gsm8k import (
    E002_CONFIG_SHA256,
    E002_TRAINING_REVISION,
    MODEL_ID,
    MODEL_REVISION,
    validate_adapter_evaluation_request,
    verify_adapter_checkpoint,
)


ADAPTER_SHA = "a" * 64
EVALUATOR_SHA = "b" * 40


def validate(
    run_type,
    *,
    adapter_dir=None,
    adapter_sha=None,
    limit=747,
    source_index=None,
    max_new_tokens=512,
):
    return validate_adapter_evaluation_request(
        run_type=run_type,
        adapter_dir=adapter_dir,
        expected_adapter_sha256=adapter_sha,
        source_index=source_index,
        limit=limit,
        validation_size=747,
        code_revision=EVALUATOR_SHA,
        max_new_tokens=max_new_tokens,
    )


class TestSFTAdapterEvaluation(unittest.TestCase):

    def test_pretrained_full_validation_allowed(self):
        validate("development_baseline")

    def test_pretrained_baseline_rejects_adapter(self):
        with self.assertRaisesRegex(ValueError, "cannot load"):
            validate(
                "development_baseline",
                adapter_dir=Path("adapter"),
                adapter_sha=ADAPTER_SHA,
            )

    def test_sft_requires_adapter(self):
        with self.assertRaisesRegex(ValueError, "requires"):
            validate("development_sft")

    def test_sft_full_validation_allowed(self):
        validate(
            "development_sft",
            adapter_dir=Path("adapter"),
            adapter_sha=ADAPTER_SHA,
        )

    def test_partial_or_changed_protocol_rejected(self):
        for changes in (
            {"limit": 5},
            {"source_index": 0},
            {"max_new_tokens": 192},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    validate(
                        "development_sft",
                        adapter_dir=Path("adapter"),
                        adapter_sha=ADAPTER_SHA,
                        **changes,
                    )

    def test_adapter_checksum_required(self):
        with self.assertRaisesRegex(ValueError, "together"):
            validate(
                "engineering_smoke_test",
                adapter_dir=Path("adapter"),
            )

    def test_completed_checkpoint_verification(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            adapter = root / "adapter"
            adapter.mkdir()

            weights = b"synthetic adapter checksum test"

            (adapter / "adapter_model.safetensors").write_bytes(
                weights
            )

            sha = hashlib.sha256(weights).hexdigest()

            (adapter / "adapter_config.json").write_text(
                json.dumps({
                    "base_model_name_or_path": MODEL_ID,
                    "r": 8,
                    "lora_alpha": 16,
                    "target_modules": [
                        "q_proj", "k_proj", "v_proj", "o_proj"
                    ],
                }),
                encoding="utf-8",
            )

            (root / "manifest.json").write_text(
                json.dumps({
                    "completed_optimizer_steps": 422,
                    "next_epoch": 2,
                    "config_sha256": E002_CONFIG_SHA256,
                    "code_revision": E002_TRAINING_REVISION,
                    "model_revision": MODEL_REVISION,
                    "checksums": {
                        "adapter/adapter_model.safetensors": sha,
                    },
                }),
                encoding="utf-8",
            )

            provenance = verify_adapter_checkpoint(
                adapter,
                sha,
                require_completed_e002=True,
            )

            self.assertEqual(provenance["adapter_sha256"], sha)

            with self.assertRaisesRegex(
                ValueError, "SHA-256 mismatch"
            ):
                verify_adapter_checkpoint(
                    adapter,
                    ADAPTER_SHA,
                    require_completed_e002=True,
                )

    def test_incomplete_checkpoint_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                verify_adapter_checkpoint(
                    Path(temporary),
                    ADAPTER_SHA,
                    require_completed_e002=True,
                )


if __name__ == "__main__":
    unittest.main()
