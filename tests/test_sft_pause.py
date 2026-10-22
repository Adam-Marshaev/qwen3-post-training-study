"""Tests for controlled formal-training epoch pauses."""

import unittest
from pathlib import Path

from scripts.train_sft import validate_pause_request


class TestFormalTrainingPause(unittest.TestCase):

    def test_formal_epoch_one_pause_allowed(self):
        validate_pause_request(
            "formal_training",
            1,
            None,
        )

    def test_normal_execution_without_pause_allowed(self):
        validate_pause_request(
            "formal_training",
            None,
            None,
        )

        validate_pause_request(
            "engineering_smoke_test",
            None,
            None,
        )

    def test_smoke_test_cannot_request_pause(self):
        with self.assertRaisesRegex(
            ValueError,
            "formal training only",
        ):
            validate_pause_request(
                "engineering_smoke_test",
                1,
                None,
            )

    def test_only_first_epoch_pause_supported(self):
        with self.assertRaisesRegex(
            ValueError,
            "Only --stop-after-epoch 1",
        ):
            validate_pause_request(
                "formal_training",
                2,
                None,
            )

    def test_resume_cannot_request_another_pause(self):
        with self.assertRaisesRegex(
            ValueError,
            "Cannot request a pause",
        ):
            validate_pause_request(
                "formal_training",
                1,
                Path("/results/e002/epoch_0001"),
            )


if __name__ == "__main__":
    unittest.main()
