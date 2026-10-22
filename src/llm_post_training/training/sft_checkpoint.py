"""Epoch-boundary SFT checkpoints with optimizer, scheduler, and RNG state."""

import hashlib
import json
import os
import random
import re
import shutil
import tempfile
from pathlib import Path

import numpy as np
import torch


FORMAT_VERSION = "sft_epoch_checkpoint_v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as source:
        for chunk in iter(
            lambda: source.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def capture_rng_state() -> dict:
    """Capture the random states needed at an epoch boundary."""

    numpy_state = np.random.get_state()

    return {
        "python": random.getstate(),
        "numpy": (
            numpy_state[0],
            numpy_state[1].tolist(),
            int(numpy_state[2]),
            int(numpy_state[3]),
            float(numpy_state[4]),
        ),
        "torch_cpu": torch.get_rng_state(),
        "torch_cuda": (
            torch.cuda.get_rng_state_all()
            if torch.cuda.is_available()
            else []
        ),
    }


def restore_rng_state(state: dict) -> None:
    """Restore Python, NumPy, PyTorch, and CUDA RNG state."""

    saved_cuda_states = state["torch_cuda"]

    if saved_cuda_states:
        if not torch.cuda.is_available():
            raise RuntimeError(
                "Checkpoint contains CUDA RNG state, "
                "but CUDA is unavailable"
            )

        if len(saved_cuda_states) != torch.cuda.device_count():
            raise RuntimeError(
                "CUDA device count differs from checkpoint"
            )

    random.setstate(state["python"])

    name, keys, position, has_gauss, cached_gaussian = (
        state["numpy"]
    )

    np.random.set_state(
        (
            name,
            np.asarray(keys, dtype=np.uint32),
            position,
            has_gauss,
            cached_gaussian,
        )
    )

    torch.set_rng_state(state["torch_cpu"])

    if saved_cuda_states:
        torch.cuda.set_rng_state_all(saved_cuda_states)


def save_epoch_checkpoint(
    directory: Path,
    *,
    model,
    optimizer,
    scheduler,
    completed_optimizer_steps: int,
    next_epoch: int,
    config_sha256: str,
    code_revision: str,
    model_revision: str,
) -> dict:
    """Publish a new checkpoint after a completed training epoch.

    The checkpoint directory contains:
      adapter/
      training_state.pt
      manifest.json

    Files are written to a temporary directory first.
    The completed directory is then published with a rename.
    """

    directory = Path(directory)

    if directory.exists():
        raise FileExistsError(directory)

    if completed_optimizer_steps < 1 or next_epoch < 1:
        raise ValueError(
            "Checkpoint must follow a completed training epoch"
        )

    expected_formats = (
        (config_sha256, 64),
        (code_revision, 40),
        (model_revision, 40),
    )

    for value, length in expected_formats:
        if re.fullmatch(
            rf"[0-9a-f]{{{length}}}",
            value,
        ) is None:
            raise ValueError("Invalid provenance hash")

    directory.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = Path(
        tempfile.mkdtemp(
            prefix=f".{directory.name}.tmp-",
            dir=directory.parent,
        )
    )

    try:
        adapter_dir = temporary / "adapter"

        model.save_pretrained(
            str(adapter_dir),
            safe_serialization=True,
        )

        adapter_weights = (
            adapter_dir / "adapter_model.safetensors"
        )

        adapter_config = (
            adapter_dir / "adapter_config.json"
        )

        if (
            not adapter_weights.is_file()
            or not adapter_config.is_file()
        ):
            raise ValueError("Adapter export is incomplete")

        metadata = {
            "format_version": FORMAT_VERSION,
            "completed_optimizer_steps": completed_optimizer_steps,
            "next_epoch": next_epoch,
            "config_sha256": config_sha256,
            "code_revision": code_revision,
            "model_revision": model_revision,
        }

        state_path = temporary / "training_state.pt"

        torch.save(
            {
                "metadata": metadata,
                "optimizer": optimizer.state_dict(),
                "scheduler": scheduler.state_dict(),
                "rng": capture_rng_state(),
            },
            state_path,
        )

        manifest = {
            **metadata,
            "checksums": {
                "adapter/adapter_model.safetensors": _sha256(
                    adapter_weights
                ),
                "adapter/adapter_config.json": _sha256(
                    adapter_config
                ),
                "training_state.pt": _sha256(state_path),
            },
        }

        (temporary / "manifest.json").write_text(
            json.dumps(
                manifest,
                indent=2,
                sort_keys=True,
            ) + "\n",
            encoding="utf-8",
        )

        # Both directories are on the same filesystem.
        # This publishes the completed checkpoint together.
        os.rename(temporary, directory)

        return metadata

    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def verify_epoch_checkpoint(
    directory: Path,
    *,
    expected_config_sha256: str,
    expected_code_revision: str,
    expected_model_revision: str,
) -> dict:
    """Verify artifact hashes and expected training provenance."""

    directory = Path(directory)

    manifest = json.loads(
        (directory / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    if manifest["format_version"] != FORMAT_VERSION:
        raise ValueError("Unexpected checkpoint format version")

    if manifest["config_sha256"] != expected_config_sha256:
        raise ValueError("Checkpoint configuration mismatch")

    if manifest["code_revision"] != expected_code_revision:
        raise ValueError("Checkpoint code revision mismatch")

    if manifest["model_revision"] != expected_model_revision:
        raise ValueError("Checkpoint model revision mismatch")

    required_files = {
        "adapter/adapter_model.safetensors",
        "adapter/adapter_config.json",
        "training_state.pt",
    }

    if set(manifest["checksums"]) != required_files:
        raise ValueError("Checkpoint file inventory mismatch")

    for relative_path, expected_digest in (
        manifest["checksums"].items()
    ):
        actual_digest = _sha256(
            directory / relative_path
        )

        if actual_digest != expected_digest:
            raise ValueError(
                f"Checkpoint checksum mismatch: {relative_path}"
            )

    return manifest


def restore_epoch_training_state(
    directory: Path,
    *,
    optimizer,
    scheduler,
    expected_config_sha256: str,
    expected_code_revision: str,
    expected_model_revision: str,
) -> dict:
    """Restore optimization state after loading model and adapter.

    IMPORTANT:
    The caller must first load the pretrained model and saved
    LoRA adapter, then construct the optimizer and scheduler.

    Call this function only after those objects exist.
    """

    manifest = verify_epoch_checkpoint(
        directory,
        expected_config_sha256=expected_config_sha256,
        expected_code_revision=expected_code_revision,
        expected_model_revision=expected_model_revision,
    )

    state = torch.load(
        Path(directory) / "training_state.pt",
        map_location="cpu",
        weights_only=True,
    )

    metadata = {
        key: value
        for key, value in manifest.items()
        if key != "checksums"
    }

    if state["metadata"] != metadata:
        raise ValueError("Checkpoint metadata mismatch")

    optimizer.load_state_dict(state["optimizer"])
    scheduler.load_state_dict(state["scheduler"])

    # Restore RNG last: loading models and constructing
    # optimizers can themselves consume random numbers.
    restore_rng_state(state["rng"])

    return metadata
