#!/usr/bin/env bash
set -Eeuo pipefail

# E005 host launcher, version 1.
#
# CHECK ONLY.
# This version cannot launch GRPO training.
# Training requires a separately reviewed and approved launcher.

if [[ $# -ne 1 || "$1" != "check" ]]; then
    echo 'TRAINING NOT AUTHORIZED: launcher supports check only.' >&2
    exit 64
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

BASE_COMMIT='04459f91a51913bbed5c385b974d34f518f51b35'

IMAGE='sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e'
CACHE="$HOME/.cache/huggingface"

PARENT='data/train_runs/e005_grpo_from_e002a_v1'
INPUTS="$PARENT/inputs"
RUN="$PARENT/run"

SCRIPT='protocols/e005_grpo_preparation_v1/train_e005_grpo_v1.py'
PLAN='protocols/e005_grpo_preparation_v1/e005_grpo_training_plan_v1.json'

echo '=== E005 HOST PREFLIGHT ==='

SOURCE_COMMIT="$(git rev-parse HEAD)"

git merge-base --is-ancestor "$BASE_COMMIT" "$SOURCE_COMMIT"

if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
    echo 'ERROR: Git working tree is not clean.' >&2
    exit 1
fi

test ! -e "$RUN"
test -d "$PARENT"
test -d "$INPUTS"
test -d "$CACHE/hub/models--Qwen--Qwen3-0.6B-Base"

echo
echo '=== VERIFY FROZEN ARTIFACTS ==='

printf '%s  %s\n' \
  'dc1cac323d282bcfc0e8e1d96e715124010eb3c2d590ab602862cb001dd7c56b' \
  "$SCRIPT" \
  'e523a051e47c33a5fff3870ff4006e5efc27b791d7d7b0faf89a4e9c1b1fccf9' \
  "$PLAN" \
  '93cc63e8e57cab769cc27b136707b63943b47be02de5a82d889bd0196e6ee866' \
  "$INPUTS/grpo_train6726_v1.jsonl" \
  '3df8da3c32b5a6d06995346c2e166e60442c17c2fdffcaf9727ab6b60ade5c19' \
  'protocols/e005_grpo_preparation_v1/grpo_dataset_manifest_v1.json' \
  '152d7cac32736fb8f797644642ea2351427b8c6e2b911531c1b88acbfc4b7acb' \
  'src/llm_post_training/training/grpo_reward.py' \
  'f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625' \
  'data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/adapter_model.safetensors' \
  '31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719' \
  'configs/data/gsm8k_split_v1.json' \
  '17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465' \
  'data/raw/gsm8k/train.jsonl' \
  | sha256sum -c -

echo
echo '=== VERIFY DOCKER IMAGE ==='

test "$(docker image inspect --format '{{.Id}}' "$IMAGE")" = "$IMAGE"

echo 'Pinned Docker image: VERIFIED'
echo "Host Git commit: $SOURCE_COMMIT"
echo 'Host working tree: CLEAN'

echo
echo '=== CPU-ONLY CONTAINER PREFLIGHT ==='

# The complete repository is read-only.
# Only the E005 output parent is writable.
# The frozen training inputs are overmounted read-only.
#
# There is deliberately no --gpus argument.

docker run \
  --rm \
  -i \
  --network none \
  --read-only \
  --user "$(id -u):$(id -g)" \
  --tmpfs /tmp:rw,nosuid,size=1g \
  --mount "type=bind,src=$PWD,dst=/workspace,readonly" \
  --mount "type=bind,src=$PWD/$PARENT,dst=/workspace/$PARENT" \
  --mount "type=bind,src=$PWD/$INPUTS,dst=/workspace/$INPUTS,readonly" \
  --mount "type=bind,src=$CACHE,dst=/hf-cache,readonly" \
  --workdir /workspace \
  --env HOME=/tmp \
  --env HF_HOME=/hf-cache \
  --env HF_HUB_CACHE=/hf-cache/hub \
  --env HF_HUB_OFFLINE=1 \
  --env TRANSFORMERS_OFFLINE=1 \
  --env HF_DATASETS_OFFLINE=1 \
  --env PYTHONPATH=/workspace/src \
  --env PYTHONDONTWRITEBYTECODE=1 \
  --env XDG_CACHE_HOME=/tmp/cache \
  --env E005_HOST_SOURCE_COMMIT="$SOURCE_COMMIT" \
  --env E005_HOST_GIT_CLEAN=1 \
  --entrypoint /usr/bin/python3 \
  "$IMAGE" \
  -B - <<'PY'
import importlib.util
import os
import tempfile
from pathlib import Path

import torch

SCRIPT = Path(
    "protocols/e005_grpo_preparation_v1/"
    "train_e005_grpo_v1.py"
)

PARENT = Path("data/train_runs/e005_grpo_from_e002a_v1")
INPUTS = PARENT / "inputs"
RUN = PARENT / "run"

def require(condition, message):
    if not condition:
        raise RuntimeError(message)


print("=== VERIFY NO GPU ACCESS ===", flush=True)

require(not torch.cuda.is_available(), "GPU unexpectedly available")
require(not RUN.exists(), "Real training run exists")

print("CUDA available: FALSE")


print("\n=== VERIFY MOUNT ISOLATION ===", flush=True)

require(
    bool(os.statvfs("/workspace").f_flag & os.ST_RDONLY),
    "Repository root is writable",
)

require(
    bool(os.statvfs(INPUTS).f_flag & os.ST_RDONLY),
    "Frozen input directory is writable",
)

require(
    not bool(os.statvfs(PARENT).f_flag & os.ST_RDONLY),
    "Training output parent is read-only",
)

print("Repository: READ-ONLY")
print("Frozen inputs: READ-ONLY")
print("Output parent: WRITABLE")


print("\n=== VERIFY OUTPUT PERMISSIONS ===", flush=True)

with tempfile.NamedTemporaryFile(
    mode="w",
    encoding="utf-8",
    prefix=".e005_p4k_write_probe_",
    dir=PARENT,
    delete=True,
) as handle:
    handle.write("E005 preflight only\n")
    handle.flush()

    require(
        Path(handle.name).is_file(),
        "Temporary write test failed",
    )

require(not RUN.exists(), "Run directory unexpectedly created")

print("Temporary output write: PASSED")
print("Temporary output cleanup: PASSED")


print("\n=== IMPORT COMMITTED TRAINER ===", flush=True)

spec = importlib.util.spec_from_file_location(
    "e005_grpo_training",
    SCRIPT,
)

require(
    spec is not None and spec.loader is not None,
    "Cannot import trainer module",
)

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

revision = module.verified_host_revision()

require(
    len(revision) == 40,
    "Host revision is malformed",
)

print("Host-provided Git provenance: VERIFIED")
print("Source commit:", revision)


print("\n=== VERIFY FROZEN INPUTS ===", flush=True)

plan, rows, tokenizer = module.validate_plan()

require(len(rows) == 6726, "Wrong dataset size")

require(
    plan["training_approved"] is False,
    "Training unexpectedly authorized",
)

require(
    plan["status"] == "PROPOSED_NOT_AUTHORIZED",
    "Unexpected training-plan status",
)

require(
    plan["output_dir"] == str(RUN),
    "Unexpected real training directory",
)

print("Dataset and checkpoint checks: PASSED")
print("Training authorization: FALSE")


print("\n=== BUILD PROPOSED GRPO CONFIG ===", flush=True)

config = module.build_config(plan)

require(config.max_steps == 256, "Wrong step budget")
require(config.learning_rate == 1e-6, "Wrong learning rate")
require(config.num_generations == 4, "Wrong group size")
require(config.generation_batch_size == 4, "Wrong rollout batch")
require(config.gradient_accumulation_steps == 4, "Wrong accumulation")
require(config.max_completion_length == 512, "Wrong completion limit")
require(config.max_prompt_length is None, "Unexpected truncation")
require(config.beta == 0.0, "Unexpected KL configuration")
require(config.loss_type == "dapo", "Unexpected loss")
require(config.fp16 is True, "FP16 disabled")
require(config.use_vllm is False, "Unexpected vLLM usage")
require(config.save_steps == 64, "Wrong checkpoint interval")

print("Real GRPOConfig: PASSED")
print("Proposed optimizer steps:", config.max_steps)
print("Learning rate:", config.learning_rate)
print("Checkpoint interval:", config.save_steps)


print("\n=== FINAL SAFETY ASSERTIONS ===", flush=True)

require(not RUN.exists(), "Real training directory appeared")
require(plan["training_approved"] is False, "Authorization changed")

print("GPU model instantiated: NO")
print("GRPOTrainer instantiated: NO")
print("Optimizer instantiated: NO")
print("Optimizer updates: ZERO")
print("Real training directory: ABSENT")

print("\nE005-P4K HOST LAUNCH PREFLIGHT: PASSED")
PY

echo
echo '=== VERIFY HOST INTEGRITY ==='

test -z "$(git status --porcelain --untracked-files=all)"
test ! -e "$RUN"

echo 'Host Git worktree: CLEAN'
echo 'Training authorization: FALSE'
echo 'Optimizer updates: ZERO'
echo 'E005 CHECK-ONLY LAUNCHER: COMPLETE'
