# E004-P1 — Disjoint candidate-generation protocol (v1)

**Status: candidate generation only; DPO/GRPO training is not authorized.**

- Model: pinned `Qwen/Qwen3-0.6B-Base`, frozen E002a epoch-2 LoRA adapter (same as E003).
- Inputs: only the pinned 6,726-question GSM8K **training** partition. Validation is loaded solely to assert disjoint indices; official GSM8K test is not accessed.
- Historical exclusions: original E003 32-question pilot plus the 256-question E003 scale pool (**288 unique source indices**), independently recomputed with original seeds and cross-checked against metadata and pinned original candidate SHA256.
- Sampling: 250 new source questions, `Random(42004)` after historical exclusions, 4 completions each, per-sample `42 + 100*source_index + sample_index`. Immutable ordered IDs in metadata.
- Generation: FP16 E002a, eager attention, 0.8 temperature, top-p 0.95, `max_new_tokens=256`, KV cache ON, native EOS/PAD `151643`. Same generation and extraction logic as E003.
- Checkpointing: atomic, fsynced four-completion question checkpoints; `--resume` revalidates completed checkpoints. Existing completed outputs are not silently overwritten; process lock excludes concurrent writers.
- Preflight: fail closed on pinned model/data/adapter/checksums and the original E003 generation script/config hashes; `--preflight-only` must run without loading the GPU model or creating output. Fail closed on unexpected Docker image ID.
- Two-group engineering pause: `--stop-after-new-groups 2`, then inspect output and use `--resume` under the **same committed Git revision**.
- Collected correctness labels use numerical final-answer extraction and are **NOT proof of valid reasoning**. `mixed_groups_with_potential_pair` is **NOT accepted pairs**. No pair-construction or quality-screening algorithm is included in this versioned generation package.

## QC/filtering gate before dataset approval

1. Retain only integrity-valid EOS-terminated and extracted completions.
2. Apply separate *versioned* strict mathematical reasoning, unit, arithmetic, answer consistency, and question ambiguity screens to both sides of each proposed pair. These screens **cannot be certified using final-answer correctness alone**.
3. Reject doubtful candidates instead of manually fixing them. Cap chosen/rejected absolute token gap at 40 unless a future separately recorded protocol explicitly changes it.
4. Sample 30 provisional accepted and 10 rejected examples reproducibly for manual spot check; **do not** claim independent mathematical verification of all pairs based on this small sample.
5. Record fixed selection policy before full-scale generation or pair construction; reserve preference holdout. Only after approval create immutable training pairs. No DPO run is permitted by this pilot.

## Pinned provenance

Expected original E003 scale candidates SHA256: `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`.

Prior scale generator script SHA256: `bd951a51e6e8a41094246da4045b1188a08a0df9c5541e3c683912c9af51967e`.

Prior scale config SHA256: `102bcdea4c6af29dbc5b6cbdb5b0f28ad2a4892f5d3f93b9c2b8d331f4762d14`.

If local original scripts differ from these archived versions, STOP and investigate rather than editing the expected hashes to make checks pass.
