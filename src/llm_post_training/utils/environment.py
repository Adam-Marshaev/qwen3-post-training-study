"""Utilities for inspecting the machine learning runtime environment."""

import platform

import torch


def collect_environment() -> dict[str, object]:
    """Return information about the current PyTorch environment."""

    cuda_available = torch.cuda.is_available()

    info = {
        "python_version": platform.python_version(),
        "pytorch_version": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "cuda_available": cuda_available,
        "gpu_name": None,
        "compute_capability": None,
        "native_bf16": None,
    }

    if cuda_available:
        info["gpu_name"] = torch.cuda.get_device_name(0)
        info["compute_capability"] = torch.cuda.get_device_capability(0)
        info["native_bf16"] = torch.cuda.is_bf16_supported(
            including_emulation=False
        )

    return info
