#!/usr/bin/env bash
set -Eeuo pipefail

# E005 approved launch protocol.
#
# check: CPU-only validation; performs no training.
# train: executes the explicitly authorized 256-step experiment.
#
# Original GSM8K test data is never mounted or accessed.

if [[ $# -ne 1 ]]; then
    echo 'Usage: bash launch_e005_grpo_approved_v1.sh check|train' >&2
    exit 64
fi

MODE="$1"

case "$MODE" in
    check|train)
        ;;
    *)
        echo "Unsupported mode: $MODE" >&2
        exit 64
        ;;
esac

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

BASE_COMMIT='4e9b4469f7663de6b20c156c806b328208a78e73'

IMAGE='sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e'
CACHE="$HOME/.cache/huggingface"

PLAN='protocols/e005_grpo_preparation_v1/e005_grpo_training_plan_v1.json'
SCRIPT='protocols/e005_grpo_preparation_v1/train_e005_grpo_v1.py'

PARENT='data/train_runs/e005_grpo_from_e002a_v1'
INPUTS="$PARENT/inputs"
RUN="$PARENT/run"

PLAN_SHA='249c4d51f323b03ed92b3071e0da558adcbcb6b89e773c04bc1619dbd5b63102'

echo '=== E005 APPROVED LAUNCH PROTOCOL ==='
echo "Mode: $MODE"

SOURCE_COMMIT="$(git rev-parse HEAD)"

git merge-base --is-ancestor "$BASE_COMMIT" "$SOURCE_COMMIT"

if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
    echo 'ERROR: Git worktree must be clean.' >&2
    exit 1
fi

test ! -e "$RUN"

test -d "$PARENT"
test -d "$INPUTS"
test -d "$CACHE/hub/models--Qwen--Qwen3-0.6B-Base"

echo
echo '=== VERIFY FROZEN AND APPROVED INPUTS ==='

printf '%s  %s\n' \
  "$PLAN_SHA" \
  "$PLAN" \
  'dc1cac323d282bcfc0e8e1d96e715124010eb3c2d590ab602862cb001dd7c56b' \
  "$SCRIPT" \
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

test "$(docker image inspect --format '{{.Id}}' "$IMAGE")" = "$IMAGE"

echo
echo '=== VERIFY EXPLICIT APPROVAL ==='

python3 -B - "$PLAN" "$RUN" <<'PY'
import json
import sys
from pathlib import Path

plan = json.loads(Path(sys.argv[1]).read_text())

assert plan["experiment"] == "E005"
assert plan["status"] == "AUTHORIZED"
assert plan["training_approved"] is True

h = plan["hyperparameters"]

assert h["max_steps"] == 256
assert h["learning_rate"] == 1e-6
assert h["num_generations"] == 4
assert h["gradient_accumulation_steps"] == 4
assert h["generation_batch_size"] == 4
assert h["max_completion_length"] == 512

assert plan["output_dir"] == sys.argv[2]
assert not Path(sys.argv[2]).exists()

print("Experiment: E005")
print("Training authorization: VERIFIED")
print("Optimizer steps: 256")
print("Learning rate: 1e-6")
print("Generation group: 4")
print("Run directory: NEW")
PY

echo
echo "Source Git commit: $SOURCE_COMMIT"
echo "Approved plan SHA256: $PLAN_SHA"

echo
echo '=== BUILD CONTAINER ARGUMENTS ==='

# The repository and all frozen inputs remain read-only.
# Only the experiment output parent is writable.

DOCKER_ARGS=(
    --rm
    -i
    --network none
    --read-only
    --user "$(id -u):$(id -g)"
    --shm-size=1g
    --tmpfs /tmp:rw,nosuid,size=4g

    --mount "type=bind,src=$PWD,dst=/workspace,readonly"
    --mount "type=bind,src=$PWD/$PARENT,dst=/workspace/$PARENT"
    --mount "type=bind,src=$PWD/$INPUTS,dst=/workspace/$INPUTS,readonly"
    --mount "type=bind,src=$CACHE,dst=/hf-cache,readonly"

    --workdir /workspace

    --env HOME=/tmp
    --env HF_HOME=/hf-cache
    --env HF_HUB_CACHE=/hf-cache/hub
    --env HF_HUB_OFFLINE=1
    --env TRANSFORMERS_OFFLINE=1
    --env HF_DATASETS_OFFLINE=1
    --env HF_HUB_DISABLE_TELEMETRY=1
    --env PYTHONPATH=/workspace/src
    --env PYTHONDONTWRITEBYTECODE=1
    --env PYTHONUNBUFFERED=1
    --env XDG_CACHE_HOME=/tmp/cache
    --env TOKENIZERS_PARALLELISM=false

    --env E005_HOST_SOURCE_COMMIT="$SOURCE_COMMIT"
    --env E005_HOST_GIT_CLEAN=1

    --entrypoint /usr/bin/python3
)

if [[ "$MODE" == "check" ]]; then

    echo
    echo '=== CPU-ONLY APPROVED-PLAN PREFLIGHT ==='

    # No --gpus argument. No model initialization.
    # The trainer's --mode check never invokes trainer.train().

    docker run \
        "${DOCKER_ARGS[@]}" \
        "$IMAGE" \
        -B "$SCRIPT" --mode check

    test ! -e "$RUN"

    echo
    echo 'Approved plan check: PASSED'
    echo 'GPU exposed: NO'
    echo 'Optimizer updates: ZERO'
    echo 'E005 APPROVED PREFLIGHT: COMPLETE'

    exit 0
fi

echo
echo '=== START AUTHORIZED GPU TRAINING ==='

# The user authorized this exact experiment:
# 256 optimizer steps, learning rate 1e-6, from E002a.
#
# Do not reuse an existing run directory or overwrite a log.

CONSOLE_LOG="$PARENT/train_console_256_v1.log"

test ! -e "$CONSOLE_LOG"
test ! -e "$RUN"

echo "Console log: $CONSOLE_LOG"
echo 'Maximum optimizer steps: 256'
echo 'Learning rate: 1e-6'
echo 'Starting checkpoint: frozen E002a epoch 2'

docker run \
    --gpus all \
    --env CUDA_VISIBLE_DEVICES=0 \
    "${DOCKER_ARGS[@]}" \
    "$IMAGE" \
    -B "$SCRIPT" --mode train \
    2>&1 | tee "$CONSOLE_LOG"

echo
echo '=== VERIFY COMPLETED TRAINING OUTPUT ==='

test -f "$RUN/e005_training_summary.json"
test -f "$RUN/final_policy_adapter/policy/adapter_model.safetensors"

python3 -B - "$RUN/e005_training_summary.json" "$SOURCE_COMMIT" <<'PY'
import json
import sys
from pathlib import Path

summary = json.loads(Path(sys.argv[1]).read_text())

assert summary["experiment"] == "E005"
assert summary["source_git_commit"] == sys.argv[2]
assert summary["completed_steps"] == 256

print("Completed optimizer steps:", summary["completed_steps"])
print("Final adapter SHA256:", summary["final_adapter_sha256"])
print("Reward trace SHA256:", summary["rollouts_sha256"])
print("E005 TRAINING: COMPLETED")
PY
