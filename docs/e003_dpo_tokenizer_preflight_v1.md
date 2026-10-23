# E003 DPO109 — read-only TRL tokenizer preflight v1

## Purpose

Check the **already-staged**, previously audited 109 original DPO pairs using the
new `llm-post-training-lab:dpo0262` Docker image. The existing E002a epoch-2
adapter is the starting policy checkpoint, not a new SFT run.

No script in this package starts DPO training, SFT training, a DPOTrainer
instance, a model forward pass, a GPU job, or writes to the repository. The
`--network none`, read-only mounts and `/tmp` tmpfs invocation keep the check
offline and nonmutating.

## Why this check matters

- The Qwen3 tokenizer's default EOS is **151645**, whereas E002a and the
  generated DPO continuations used native completion ending **151643**.
  TRL v0.26.2's `DPOTrainer.tokenize_row` appends the tokenizer's current
  `eos_token_id` to each completion. The script adjusts **only the in-memory
  tokenizer object** to EOS 151643 and audits all 218 completions. It does not
  alter Qwen's tokenizer files, the base model, or the 109 DPO responses.
- Qwen's pad token is also 151643, so an end-of-response token must remain
  **unmasked** while padding at the same token ID is masked. The script
  checks the official TRL preference collator on two differently sized rows.
- TRL's text preparation tokenizes the prompt and completion **separately**.
  This may give different token IDs from the *original generated continuation*
  or from joint prompt-plus-completion tokenization. The script reports those
  counts. Differences between original generation and TRL completion tokens
  require explicit analysis before release and exit code **2**; joint-vs-
  separate differences are recorded for analysis without silently rewriting
  data.
- With an existing `PeftModel`, the default TRL reference context disables
  LoRA, yielding the *base model*, **not E002a**. The eventual trainer must
  load **both policy and reference adapters from the same frozen E002a epoch-2
  checkpoint**, with explicit `model_adapter_name='policy'` and
  `ref_adapter_name='reference'`. This package does NOT verify those loaded
  models yet; that is the following GPU read-only preflight.

## Prerequisites

Host paths: `data/preference_runs/e003_dpo_signed109_staged_277c863_v1/`
and `data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/`.
The staged 109-pair hashes are pinned in code and the manifest revision must
be the dataset-selection commit `277c8636d7930c278fa8068a4c70f55b60ea770f`.
Exact offline tokenizer Qwen revision is
`57ca99e94acb83175495aa2c6b6b0cc498170924`.

Docker image dependencies verified by user: TRL 0.26.2, Transformers 4.57.6,
PEFT 0.18.1, PyTorch 2.14.0+cu126. The tokenizer must already be available
in the read-only Hugging Face host cache.

## Host run (after installing the scripts)

```
cd ~/projects/llm-post-training-lab

# Optional package tests in the Docker environment (not system Python):
docker run --rm -i --network none --read-only --tmpfs /tmp \
  --mount "type=bind,src=$PWD,dst=/workspace,readonly" \
  -w /workspace --entrypoint /usr/bin/python3 \
  llm-post-training-lab:dpo0262 \
  tests/test_preflight_e003_dpo_tokenizer_v1.py

# Read-only tokenizer check; must mount the same HF_HOME used for E002a:
test -d "$HOME/.cache/huggingface" || { echo 'HF cache not found'; exit 1; }
docker run --rm -i --network none --read-only --tmpfs /tmp \
  --mount "type=bind,src=$PWD,dst=/workspace,readonly" \
  --mount "type=bind,src=$HOME/.cache/huggingface,dst=/hf-cache,readonly" \
  -e HF_HOME=/hf-cache -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  -e PYTHONDONTWRITEBYTECODE=1 -e HF_HUB_DISABLE_TELEMETRY=1 \
  -w /workspace --entrypoint /usr/bin/python3 \
  llm-post-training-lab:dpo0262 \
  scripts/preflight_e003_dpo_tokenizer_v1.py --repo-root .
```

A successful run says **TOKENIZER PREFLIGHT: PASSED** but still says
**REFERENCE/GPU PREFLIGHT PENDING**. This is not a dataset freeze, a trainer
initialization test, or training authorization. A nonzero result is a hold.

Next phase: verify the two E002a adapter copies and reference-policy identity
on the V100 without optimizer/training, then pin hyperparameters/image digest,
freeze the dataset/config, and obtain a **separate explicit go/no-go**.
