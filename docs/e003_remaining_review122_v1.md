# M3.15 — E003 Remaining 122 Mixed-Group Reasoning-Review Export

**Purpose:** Create a deterministic, CPU-only seven-batch review inventory for **all 122 previously unreviewed** correct/incorrect mixed groups from the 256-question E003 study.

## Scope and invariants

- The source is frozen `e003_scale256_k4_v1/candidates.jsonl` (SHA256 `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`).
- The original 24-group advisory manifest is explicitly pinned and those source indices are excluded. The independently approved 5436 pair is explicitly pinned and not re-exported.
- GSM8K source and training/validation split manifests are pinned by SHA256. Only frozen **training** questions are used, and each candidate prompt/reference is verified against the training loader.
- Each candidate's original answer, original auto-grade, four sample IDs, seed, token count, EOS, and **unmodified response text** are preserved in the review report. No reference correction is applied to the remaining groups.
- Six batches contain 20 source questions (80 completions) each; the seventh batch contains two questions (eight completions). Batches partition the ascending sorted 122-source list.
- The review files start as **UNREVIEWED**. No reasoning assessments, chosen/rejected pairs, training approval, or DPO training are produced.
- `--preflight-only` performs integrity checks and selection without creating any output.
- Normal execution builds output in a temporary directory, verifies checksums, then publishes a new directory without overwriting existing output. Each report and selection manifest is hashed in the master `manifest.json`.
- The report contains original completion text, not independent mathematical judgements. A subsequent advisory review and independent signoff require separate, versioned artifacts.

## Execution protocol

The script must be committed before running and invoked with exact `--code-revision` from `git rev-parse HEAD`, with a clean working tree. Docker's repository mount is read-only and output mount is writable. No GPU, network, or model cache is needed.

```bash
# CPU preflight
python3 scripts/prepare_e003_remaining_review122.py \
  --repo-root . \
  --output-dir data/preference_runs/e003_remaining_review122_v1 \
  --code-revision "$(git rev-parse HEAD)" \
  --preflight-only
```

For Docker execution, bind repository to `/workspace:ro`, `data/preference_runs` to `/results`, and set `PYTHONPATH=/workspace:/workspace/src`.

Expected output files:

- `manifest.json` (master checksums, input provenance, all 122 indices, and no-training flags)
- `batch_00_review.txt` through `batch_06_review.txt`
- `batch_00_selection.json` through `batch_06_selection.json`

This protocol does **not** select or construct any training pairs. Do not use the review files as approval manifests.
