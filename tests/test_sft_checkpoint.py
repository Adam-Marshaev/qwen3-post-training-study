"""Tests for resumable SFT epoch checkpoints."""

import json
import random
import tempfile
import unittest

from pathlib import Path

import numpy as np
import torch

from safetensors.torch import load_file, save_file

from llm_post_training.training.sft_checkpoint import (
    restore_epoch_training_state,
    save_epoch_checkpoint,
    verify_epoch_checkpoint,
)


CONFIG_SHA = "a" * 64
CODE_SHA = "b" * 40
MODEL_SHA = "c" * 40


class ToyAdapter(torch.nn.Module):
    """Tiny trainable model with a PEFT-like save interface."""

    def __init__(self):
        super().__init__()

        self.weight = torch.nn.Parameter(
            torch.tensor([0.2, -0.4])
        )

    def save_pretrained(
        self,
        directory,
        safe_serialization,
    ):
        assert safe_serialization

        directory = Path(directory)
        directory.mkdir()

        save_file(
            {
                "lora_B.weight": (
                    self.weight.detach().cpu().contiguous()
                )
            },
            str(
                directory / "adapter_model.safetensors"
            ),
        )

        (directory / "adapter_config.json").write_text(
            json.dumps({"r": 8}),
            encoding="utf-8",
        )


def make_training_objects():
    model = ToyAdapter()

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=0.01,
    )

    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lr_lambda=lambda step: 1.0 / (step + 1),
    )

    return model, optimizer, scheduler


def optimizer_step(model, optimizer, scheduler):
    optimizer.zero_grad(set_to_none=True)

    target = torch.tensor([0.4, 0.3])

    loss = ((model.weight - target) ** 2).sum()

    loss.backward()

    optimizer.step()
    scheduler.step()


class TestSFTCheckpoint(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()

        self.addCleanup(temporary.cleanup)

        self.directory = (
            Path(temporary.name) / "epoch_checkpoint"
        )

        random.seed(123)
        np.random.seed(123)
        torch.manual_seed(123)

        (
            self.model,
            self.optimizer,
            self.scheduler,
        ) = make_training_objects()

        optimizer_step(
            self.model,
            self.optimizer,
            self.scheduler,
        )

    def save(self):
        return save_epoch_checkpoint(
            self.directory,
            model=self.model,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            completed_optimizer_steps=1,
            next_epoch=1,
            config_sha256=CONFIG_SHA,
            code_revision=CODE_SHA,
            model_revision=MODEL_SHA,
        )

    def verify(
        self,
        config_sha=CONFIG_SHA,
        code_sha=CODE_SHA,
        model_sha=MODEL_SHA,
    ):
        return verify_epoch_checkpoint(
            self.directory,
            expected_config_sha256=config_sha,
            expected_code_revision=code_sha,
            expected_model_revision=model_sha,
        )

    def test_checkpoint_saved_and_verified(self):
        self.save()

        manifest = self.verify()

        self.assertEqual(
            manifest["completed_optimizer_steps"],
            1,
        )

        self.assertTrue(
            (
                self.directory
                / "adapter"
                / "adapter_model.safetensors"
            ).is_file()
        )

    def test_existing_checkpoint_is_not_overwritten(self):
        self.save()

        with self.assertRaises(FileExistsError):
            self.save()

    def test_tampered_training_state_is_rejected(self):
        self.save()

        with (
            self.directory / "training_state.pt"
        ).open("ab") as output:
            output.write(b"modified")

        with self.assertRaisesRegex(
            ValueError,
            "checksum mismatch",
        ):
            self.verify()

    def test_wrong_provenance_is_rejected(self):
        self.save()

        with self.assertRaisesRegex(
            ValueError,
            "configuration mismatch",
        ):
            self.verify(config_sha="d" * 64)

        with self.assertRaisesRegex(
            ValueError,
            "code revision mismatch",
        ):
            self.verify(code_sha="d" * 40)

        with self.assertRaisesRegex(
            ValueError,
            "model revision mismatch",
        ):
            self.verify(model_sha="d" * 40)

    def test_resume_matches_uninterrupted_cpu_training(self):
        self.save()

        # Observe the RNG values that should follow the save.
        expected_random = (
            random.random(),
            float(np.random.rand()),
            torch.rand(3),
        )

        # Continue the original model.
        optimizer_step(
            self.model,
            self.optimizer,
            self.scheduler,
        )

        expected_weights = (
            self.model.weight.detach().clone()
        )

        expected_lr = (
            self.optimizer.param_groups[0]["lr"]
        )

        # Reconstruct independent training objects.
        (
            resumed_model,
            resumed_optimizer,
            resumed_scheduler,
        ) = make_training_objects()

        # Restore adapter weights as the formal runner will.
        saved_weights = load_file(
            str(
                self.directory
                / "adapter"
                / "adapter_model.safetensors"
            )
        )

        with torch.no_grad():
            resumed_model.weight.copy_(
                saved_weights["lora_B.weight"]
            )

        # Deliberately disturb all three RNGs.
        random.seed(999)
        np.random.seed(999)
        torch.manual_seed(999)

        metadata = restore_epoch_training_state(
            self.directory,
            optimizer=resumed_optimizer,
            scheduler=resumed_scheduler,
            expected_config_sha256=CONFIG_SHA,
            expected_code_revision=CODE_SHA,
            expected_model_revision=MODEL_SHA,
        )

        self.assertEqual(
            metadata["next_epoch"],
            1,
        )

        actual_random = (
            random.random(),
            float(np.random.rand()),
            torch.rand(3),
        )

        self.assertEqual(
            expected_random[:2],
            actual_random[:2],
        )

        self.assertTrue(
            torch.equal(
                expected_random[2],
                actual_random[2],
            )
        )

        # Continue training after restoring the checkpoint.
        optimizer_step(
            resumed_model,
            resumed_optimizer,
            resumed_scheduler,
        )

        self.assertTrue(
            torch.equal(
                resumed_model.weight.detach(),
                expected_weights,
            )
        )

        self.assertEqual(
            resumed_optimizer.param_groups[0]["lr"],
            expected_lr,
        )


if __name__ == "__main__":
    unittest.main()
