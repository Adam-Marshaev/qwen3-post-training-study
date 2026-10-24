# E004-P2 — 250-question candidate-generation fork v1

## Purpose and safeguards

Fork the SHA256-pinned P1 generator rather than change P1 source or outputs.
This is **candidate generation only**, not DPO, GRPO, or fine-tuning.
Official GSM8K test and frozen 747-question validation are not used for
selection or evaluation. Training question selection is explicitly audited.

- Parent commit: `fde14abdf6791a0796799087f85154982e1628dd`.
- P1 generator SHA256: `87f5c398a65dd89dafe4830b564f57ed0c1e95924e81b5da3395b21e7a4f86d8`.
- P1 config SHA256: `3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6`.
- P1 candidates SHA256: `314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628`.
- Pinned Docker image ID: `sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e`.
- Frozen E002a epoch-2 adapter SHA256: `f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`.

## New selection

Re-verify the P1 code path, its E003 32+256 exclusions, completed P1
metadata/config/summary/candidates, and rederive all P1 250 source indices.
Union of exclusions must contain **538 distinct training source indices**.
Then sample **250 of the remaining 6,188 training sources** with Python
`random.Random(42005).sample` on increasing source-index order. Sample four
responses for each source (1,000 total), using the original per-response RNG
seed `42 + source_index * 100 + sample_index` and original E002a generation
parameters: temperature 0.8, top-p 0.95, cap 256, native EOS, eager attention.

The P2 fork inherits the original atomic per-question checkpoints, integrity
validation, resume logic, and output construction. P2 metadata records the
538-source provenance and P1 input file digests. Generated candidate labels
reflect final-answer agreement only, **not reasoning correctness**.

## Preflight gate (no GPU work)

Install builder/tests/note, run builder `--install`, run tests, then run:

```
python3 -m scripts.generate_e004_p2_v1 \
  --config configs/preference/e004_p2_v1.json \
  --output-dir /eval-output/e004_p2_placeholder \
  --code-revision <NEW_COMMITTED_40_CHARACTER_GIT_SHA> \
  --docker-image-id sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e \
  --preflight-only
```

Run inside the historical Docker image with the repository mounted read-only.
`--preflight-only` must not create an output directory or invoke the GPU.
Commit and sign off on the resulting SHA and selected-source fingerprint
**before** the two-group GPU smoke test.

## Staged execution only

- Two-group GPU smoke: `--stop-after-new-groups 2` in a new run directory.
- Audit two immutable per-source checkpoint files before resuming.
- Resume the existing run with `--resume` to reach 250 questions.
- Report valid extraction/EOS/cap/mixed groups, SHA256 and source disjointness.
- Apply the P1 arithmetic-first policy; its eight P1-specific exclusions are
  **not** transferable to unseen P2 questions.
- Perform 30-provisional-accept/10-reject QC on the fresh P2 outcomes.
- Never train without a separate explicit DPO/GRPO authorization.

### Code-generation boundary

The builder is offline stdlib-only. It refuses changes to the input SHA256 and
checks that the original model-generation, checkpoint, answer-grading, and
training-provenance functions are AST-identical in the generated fork. It does
not overwrite mismatched files. The two generated files are committed alongside
the versioned builder/tests/note for full traceability.
