"""Regression tests for pinned cached GSM8K inference and E002a provenance."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_gsm8k import (
    E002A_CONFIG_SHA256,
    E002A_TRAINING_REVISION,
    INFERENCE_PROTOCOL_VERSION,
    MODEL_ID,
    MODEL_REVISION,
    NATIVE_EOS_TOKEN_ID,
    cached_generation_kwargs,
    validate_adapter_evaluation_request,
    verify_adapter_checkpoint,
)


class TestCachedEvaluator(unittest.TestCase):
    def test_generation_kwargs_are_cached_and_native_eos(self):
        tokenizer = object()
        args = cached_generation_kwargs(512, tokenizer)
        self.assertEqual(args["use_cache"], True)
        self.assertEqual(args["eos_token_id"], 151643)
        self.assertEqual(args["pad_token_id"], 151643)
        self.assertEqual(args["max_new_tokens"], 512)
        self.assertEqual(args["do_sample"], False)
        self.assertIs(args["tokenizer"], tokenizer)
        self.assertEqual(INFERENCE_PROTOCOL_VERSION, "gsm8k_val512_greedy_eager_cached_v1")

    def request(self, run_type="development_native_eos", epoch=2, **overrides):
        params = dict(
            run_type=run_type,
            adapter_dir=Path("/tmp/checkpoint/epoch_0002/adapter"),
            expected_adapter_sha256="a" * 64,
            source_index=None,
            limit=747,
            validation_size=747,
            code_revision="b" * 40,
            max_new_tokens=512,
            native_eos_epoch=epoch,
        )
        params.update(overrides)
        return validate_adapter_evaluation_request(**params)

    def test_native_full_valid(self):
        self.request()
        self.request(epoch=1)

    def test_native_full_rejects_missing_epoch(self):
        with self.assertRaises(ValueError):
            self.request(epoch=None)

    def test_native_full_rejects_subset_and_short_budget(self):
        with self.assertRaises(ValueError):
            self.request(limit=12)
        with self.assertRaises(ValueError):
            self.request(max_new_tokens=192)

    def test_old_run_types_preserve_validation_rules(self):
        self.request(run_type="development_sft", epoch=None)
        self.request(
            run_type="development_baseline", epoch=None,
            adapter_dir=None, expected_adapter_sha256=None,
        )
        with self.assertRaises(ValueError):
            self.request(run_type="development_sft", epoch=1)

    def test_native_smoke_may_be_bounded_but_is_pinned(self):
        self.request(run_type="engineering_smoke_test", limit=12, epoch=2)
        with self.assertRaises(ValueError):
            self.request(
                run_type="engineering_smoke_test", limit=12,
                adapter_dir=None, expected_adapter_sha256=None,
            )

    @staticmethod
    def make_checkpoint(root, epoch):
        adapter_dir = root / f"epoch_{epoch:04d}" / "adapter"
        adapter_dir.mkdir(parents=True)
        weights = b"synthetic non-model weights for checksum tests"
        (adapter_dir / "adapter_model.safetensors").write_bytes(weights)
        sha = hashlib.sha256(weights).hexdigest()
        (adapter_dir / "adapter_config.json").write_text(json.dumps({
            "base_model_name_or_path": MODEL_ID,
            "r": 8, "lora_alpha": 16,
            "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
        }))
        manifest = {
            "completed_optimizer_steps": 211 * epoch,
            "next_epoch": epoch,
            "config_sha256": E002A_CONFIG_SHA256,
            "code_revision": E002A_TRAINING_REVISION,
            "model_revision": MODEL_REVISION,
            "checksums": {"adapter/adapter_model.safetensors": sha},
        }
        metadata = {
            "run_type": "formal_training",
            "experiment_id": "E002a",
            "supervised_eos_token_id": NATIVE_EOS_TOKEN_ID,
            "config_sha256": E002A_CONFIG_SHA256,
            "code_revision": E002A_TRAINING_REVISION,
            "model_revision": MODEL_REVISION,
        }
        (adapter_dir.parent / "manifest.json").write_text(json.dumps(manifest))
        (root / "run_metadata.json").write_text(json.dumps(metadata))
        return adapter_dir, sha

    def test_epoch_checkpoints_verified(self):
        for epoch in (1, 2):
            with self.subTest(epoch=epoch), tempfile.TemporaryDirectory() as tmp:
                adapter_dir, sha = self.make_checkpoint(Path(tmp), epoch)
                provenance = verify_adapter_checkpoint(
                    adapter_dir, sha,
                    require_completed_e002=False,
                    native_eos_epoch=epoch,
                )
                self.assertEqual(
                    provenance["training_manifest"]["completed_optimizer_steps"],
                    211 * epoch,
                )

    def test_provenance_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            adapter_dir, sha = self.make_checkpoint(Path(tmp), 2)
            manifest_file = adapter_dir.parent / "manifest.json"
            manifest = json.loads(manifest_file.read_text())
            manifest["config_sha256"] = "0" * 64
            manifest_file.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                verify_adapter_checkpoint(
                    adapter_dir, sha,
                    require_completed_e002=False,
                    native_eos_epoch=2,
                )


if __name__ == "__main__":
    unittest.main()
