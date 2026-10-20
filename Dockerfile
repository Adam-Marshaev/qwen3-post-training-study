# Base image: CUDA 12.6 on Ubuntu 22.04
FROM nvidia/cuda:12.6.3-base-ubuntu22.04

# Configure Python and pip behavior
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Python and essential system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install CUDA 12.6-compatible PyTorch
RUN python3 -m pip install \
    torch==2.14.0 \
    --index-url https://download.pytorch.org/whl/cu126

# Install NumPy for numerical processing and PyTorch interoperability
RUN python3 -m pip install numpy==1.26.4

# Set the working directory
WORKDIR /workspace

# Default command
CMD ["python3"]
