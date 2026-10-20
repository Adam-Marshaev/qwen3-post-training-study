"""Tests for runtime environment inspection."""

import unittest

from llm_post_training.utils.environment import collect_environment


class TestEnvironment(unittest.TestCase):

    def test_required_fields_exist(self):
        info = collect_environment()

        required_fields = {
            "python_version",
            "pytorch_version",
            "cuda_runtime",
            "cuda_available",
            "gpu_name",
            "compute_capability",
            "native_bf16",
        }

        self.assertTrue(required_fields.issubset(info.keys()))

    def test_cuda_availability_is_boolean(self):
        info = collect_environment()

        self.assertIsInstance(info["cuda_available"], bool)

    def test_gpu_information_is_consistent(self):
        info = collect_environment()

        if info["cuda_available"]:
            self.assertIsNotNone(info["gpu_name"])
            self.assertIsNotNone(info["compute_capability"])
        else:
            self.assertIsNone(info["gpu_name"])
            self.assertIsNone(info["compute_capability"])


if __name__ == "__main__":
    unittest.main()
