# E004-P3 candidate generation protocol v1

## Scope

An inference-only continuation of E004 using frozen Qwen3-0.6B-Base + the
E002a epoch-2 native-EOS SFT LoRA adapter. No DPO or GRPO training is
permitted. Only GSM8K TRAIN examples are used; the validation partition and
official GSM8K test split are not used for candidate generation.

## Frozen selection and configuration

- Git parent: `331499df3175737bb9464a3d9a53a365fc494431`.
- Input P2 generator SHA256: `5069415d1068f5099db7b4da068d82fcdc2f77e2615e3972db565e9a89b55556`.
- Input P2 config SHA256: `1ba4f7bc96971aab5004eb78ff8ce30e7183389ff45c21d641068f719c8eb8a5`.
- P2 candidates SHA256: `568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79`.
- P2 metadata SHA256: `cefdb0f7f9cd9c32a49b6ecdfebea3097e2a093d5a0c3e69f8fda704e943851f`.
- P2 summary SHA256: `fd240de075f87f10c5f756bc733a4cc59741fdd76795a66150fbd27ce19457b7`.
- Frozen P2/P1/E003 provenance is rederived and verified before source selection.
- Exclude all **788** training indices from E003 pilot (32), E003 scale (256), E004-P1 (250), and E004-P2 (250).
- Sample **1,200** fresh GSM8K TRAIN questions from the remaining **5,938**, sorted by `source_index` before `random.Random(42006).sample`.
- Planned inference: **1,200 x 4 = 4,800 sampled responses**.
- Expected SHA256 of `json.dumps(selected_indices, separators=(',', ':')).encode()`:
  `bfeb83304623bfdb2c8c952cba46d48ac36e251414b79d4763fb24f21b6ffed9`.
- Temperature **0.8**, top-p **0.95**, max new tokens **256**, eager attention, cached FP16 inference, native EOS 151643, `seed=42`, individual sample seed `42 + source_index * 100 + sample_index`.
- Immutable Docker **image ID**: `sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e` (not the mutable tag).

## Safeguards

The builder performs a narrow, deterministic fork of the SHA256-pinned P2
source. Historical P1 and P2 selectors retain their original **250**-question
counts even though the P3 global target is **1,200**. All model loading,
response decoding, record validation, checkpoint creation, resumption,
locking and final output reconstruction functions are unchanged.

Workflow gates:

1. Verify frozen files, install the builder/tests/docs without overwriting.
2. Generate the P3 source and config; run structural tests.
3. Run the Docker `--preflight-only` without GPU access or output creation.
4. Commit exactly the five new files with clean tree.
5. Run a two-question / eight-response GPU smoke test; audit checkpoints.
6. Resume the remaining 1,198 questions, then independently reconstruct and
   hash the completed candidate file from the 1,200 immutable checkpoints.
7. Apply the arithmetic-first mechanical screen. P1/P2 source-specific
   assistant review exclusions are historical only, **not transferable**.
8. Require separate QC/review before any preference-training approval.

P3 uses **TRAIN-partition** questions, not a held-out evaluation. Preference
correctness labels verify only terminal answers, not complete reasoning.
