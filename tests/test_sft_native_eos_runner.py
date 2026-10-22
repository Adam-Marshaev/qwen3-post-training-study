"""Validate E002 and E002a training-runner configuration isolation."""

import copy
import json
import unittest
from pathlib import Path

from scripts.train_sft import (
    get_supervised_eos_token_id,
    validate_config,
)


CONFIG_DIR = Path("configs/training")


def load_config(filename):
    return json.loads(
        (CONFIG_DIR / filename).read_text(encoding="utf-8")
    )


class TestNativeEOSRunner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original = load_config("sft_lora_v1.json")
        cls.native = load_config(
            "sft_lora_native_eos_v1.json"
        )

    def test_original_e002_accepted(self):
        validate_config(self.original)

        self.assertEqual(
            get_supervised_eos_token_id(self.original),
            151645,
        )

    def test_native_e002a_accepted(self):
        validate_config(self.native)

        self.assertEqual(
            get_supervised_eos_token_id(self.native),
            151643,
        )

    def test_native_requires_correct_eos(self):
        mutated = copy.deepcopy(self.native)
        mutated["dataset"]["target_eos_token_id"] = 151645

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_native_requires_explicit_eos(self):
        mutated = copy.deepcopy(self.native)
        del mutated["dataset"]["target_eos_token_id"]

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_original_rejects_eos_override(self):
        mutated = copy.deepcopy(self.original)
        mutated["dataset"]["target_eos_token_id"] = 151643

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_mismatched_experiment_id_rejected(self):
        mutated = copy.deepcopy(self.native)
        mutated["experiment_id"] = "E002"

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_native_requires_cached_evaluation(self):
        mutated = copy.deepcopy(self.native)
        mutated["evaluation"]["use_cache"] = False

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_native_requires_versioned_protocol(self):
        mutated = copy.deepcopy(self.native)
        mutated["evaluation"]["protocol_version"] = "unknown"

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_original_rejects_new_evaluation_protocol(self):
        mutated = copy.deepcopy(self.original)
        mutated["evaluation"]["protocol_version"] = (
            "gsm8k_val512_greedy_eager_cached_v1"
        )

        with self.assertRaises(ValueError):
            validate_config(mutated)

    def test_optimization_settings_identical(self):
        for section in ("model", "lora", "training"):
            self.assertEqual(
                self.original[section],
                self.native[section],
            )

        original_dataset = copy.deepcopy(
            self.original["dataset"]
        )

        native_dataset = copy.deepcopy(
            self.native["dataset"]
        )

        del native_dataset["target_eos_token_id"]

        self.assertEqual(
            original_dataset,
            native_dataset,
        )


if __name__ == "__main__":
    unittest.main()
