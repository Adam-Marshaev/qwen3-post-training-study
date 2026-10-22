# E003 Intermediate Preference-Generation Study — v1

**Purpose:** Estimate preference-pair yield across 256 *new* frozen GSM8K training questions with the E002a epoch-2 SFT policy, before investing in complete-scale generation or DPO optimization. This is **not training** and does not modify E002a.

## Frozen experimental protocol

- New code and config: `scripts/generate_e003_scale_v1.py`, `configs/preference/e003_scale_v1.json`.
- Dataset: 6,726-example frozen training partition only; no validation/test responses are used for candidate creation.
- Disjoint selection: reproduce the original 32 pilot indices using `Random(42).sample` over the sorted training set, validate against original pilot metadata, exclude them, and sample 256 questions from the remainder with `Random(42003).sample`. The selected indices are saved in `metadata.json`.
- Per question: 4 samples with seed `42 + 100 * source_index + sample_index`, sampling temperature `0.8`, top-p `0.95`, max 256 new tokens, eager attention, FP16 base weights, frozen E002a adapter, native EOS and PAD `151643`, **KV caching enabled**. No custom stop strings.
- Candidates: original pilot-compatible response format, including generated token IDs, decoded text, answer extraction and correctness labels. Regrade all checkpoints on resume with the numeric GSM8K reference answer, not the serialized string.
- No chosen/rejected pairs are created; groups with both eligible correct and incorrect candidates are only potential pairs. Reasoning quality is **not** established by final-answer correctness.

## Resumption and immutability

- Initial invocation refuses an existing output directory. An interrupted run is restarted explicitly with `--resume` and the **same Git revision, Docker image, config, pilot metadata and selected question indices**.
- Each completed 4-candidate group is fsynced and atomically renamed to `progress/source_XXXXX.jsonl`. On resume every committed group is revalidated against its original question, per-sample seed, token decoding, extracted answer and stored correctness. Completed groups are never regenerated or overwritten.
- `fcntl.flock` excludes competing processes. Incomplete `.incomplete_*` temporary files, if any, can be examined before manual removal; the program ignores them and trusts only the atomically committed `.jsonl` groups.
- `--stop-after-new-groups N` supports a deliberate test of restart behavior. It leaves the run incomplete, without final candidate/summary files. Then rerun with `--resume` to finish.
- After 256 groups the program writes an aggregate `candidates.jsonl` and `summary.json` with the hash of the aggregate file. A later `--resume` rechecks all checkpoints and outputs without generating new model tokens.
- Reported generation times are observational and may differ between reruns. Per-sample RNG seeds reduce dependence on interruption boundaries but do not guarantee bit-for-bit generation reproducibility across different hardware/software stacks.
- There is no independent human signoff and **no approval for DPO training**.

## Checks before launch

Use `--preflight-only` to verify frozen inputs and the disjoint selection without loading a model or creating an output. Then run with `--stop-after-new-groups 2`, verify two atomic group checkpoints and absence of final artifacts, and only then continue the same run with `--resume`. This staged restart check is not covered by the synthetic CPU unit tests; it must pass in the pinned GPU Docker environment.

Run the installed regression suite, verify the image checksum, ensure the Git worktree is clean, and verify the fixed E002a adapter hash. Preserve the original E003 32-question pilot and 18-pair provisional artifact. The original pilot source and its configuration are not modified.
