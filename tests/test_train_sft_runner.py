"""Pure-control tests for formal E002 SFT runner; no GPU/model load."""

import json
import tempfile
import unittest
from pathlib import Path

from scripts.train_sft import (
    learning_rate_factor,
    read_records,
    reconcile_logs_for_resume,
    validate_config,
)


class TestFormalSFTControls(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(
            Path("configs/training/sft_lora_v1.json").read_text(encoding="utf-8")
        )

    def test_pinned_configuration_accepted(self):
        validate_config(self.config)

    def test_changed_evaluation_budget_rejected(self):
        self.config["evaluation"]["max_new_tokens"] = 1024
        with self.assertRaisesRegex(ValueError, "generation budget"):
            validate_config(self.config)

    def test_changed_accumulation_policy_rejected(self):
        self.config["training"]["accumulation_normalization"] = "microbatch"
        with self.assertRaisesRegex(ValueError, "loss weighting"):
            validate_config(self.config)

    def test_scheduler_warmup_and_decay(self):
        self.assertAlmostEqual(learning_rate_factor(0, 13, 422), 1 / 13)
        self.assertAlmostEqual(learning_rate_factor(12, 13, 422), 1.0)
        self.assertAlmostEqual(learning_rate_factor(13, 13, 422), 1.0)
        self.assertAlmostEqual(learning_rate_factor(422, 13, 422), 0.0)
        self.assertTrue(0 < learning_rate_factor(200, 13, 422) < 1)

    def test_resume_discards_only_uncommitted_logs(self):
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "training_log.jsonl"
            with log_path.open("w", encoding="utf-8") as output:
                for step in range(1, 4):
                    output.write(json.dumps({"optimizer_step": step, "loss": step / 10}) + "\n")
            reconcile_logs_for_resume(log_path, completed_steps=2)
            self.assertEqual(
                [r["optimizer_step"] for r in read_records(log_path)], [1, 2]
            )

    def test_resume_rejects_missing_committed_log(self):
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "training_log.jsonl"
            log_path.write_text(json.dumps({"optimizer_step": 2}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing or duplicates"):
                reconcile_logs_for_resume(log_path, completed_steps=2)


if __name__ == "__main__":
    unittest.main()
