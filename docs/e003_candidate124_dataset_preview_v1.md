# E003 candidate124 — safeguarded preference-dataset preview

This is a **candidate preview, not a training dataset**. It creates 124 proposed source-unique preference pairs from the already-reviewed frozen E003 1,024-candidate study. It does **not** train, approve a dataset, or convert advisory judgments to independent human signoff.

## Included/excluded decisions

- **123 standard pairs** selected deterministically from the eight pinned reasoning-screen manifests. All remain **advisory** pending pair-level and full-dataset independent signoff.
- **Source 5436**: the separately human-approved exact `sample 2 > sample 0` pair, using the **training-only corrected reference 50**. Its frozen original reference is **55**; the original candidate texts and original labels remain unmodified. This single-pair human approval **does not** approve the complete dataset or DPO training.
- **Source 2320**: group-only human approval; **not included**, because no exact rejected sample has been independently accepted.
- **21 HOLD sources** are **never included**: 303, 744, 1293, 1512, 1651, 2272, 2515, 3631, 4151, 4456, 4949, 5064, 5599, 5656, 5775, 5851, 5870, 5994, 6417, 7304, 7340.
- **11 ordinary proposed pairs** have token gaps above 40; reported in `review_worklist.json`, not silently omitted. Source 7217 has the largest gap (112 tokens).

## Inputs and integrity

Requires the exact original candidate dataset SHA256 `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4` and the pinned all-screen consolidated auditor SHA256 `4b5ba849d4edf47cf6cf56d86f2d80a7f10aa13a9d232fecbe2703a727d9160e`. The auditor verifies the initial 24-screen, all seven batch manifests, 146 unique group indices, 584 original candidate metadata entries and human authorization overlays; the builder additionally checks frozen raw train and split hashes, all chosen/rejected native EOS tokens and eligibility, source-5436 derivative identity, and all source restrictions.

**Native EOS warning:** The `chosen` and `rejected` strings are original decoded responses (EOS is normally omitted by decoding with `skip_special_tokens=True`); corresponding `*_generated_token_ids` preserve the actual token sequence, including the native EOS ID **151643**. No training-specific sequence/label normalization has been performed.

## Reproducible workflow

From a clean committed checkout with the pinned all-screen auditor installed and committed:

```bash
python3 tests/test_build_e003_candidate124_v1.py
REVISION="$(git rev-parse HEAD)"
OUT="data/preference_runs/e003_dpo_candidate124_v1"
python3 scripts/build_e003_candidate124_v1.py --repo-root . --output-dir "$OUT" --code-revision "$REVISION" --preflight-only
python3 scripts/build_e003_candidate124_v1.py --repo-root . --output-dir "$OUT" --code-revision "$REVISION"
```

The output directory **must not already exist**. Original inputs are **read only**. The second command atomically creates three immutable preview files:

- `pairs_candidate.jsonl`: 124 rows of original prompts, chosen/rejected complete response text and native-EOS token IDs; each pair has explicit signoff and training-status flags.
- `review_worklist.json`: pair-level independent review queue, the group-only source2320 gap, 21 HOLD exclusions, and 11 long-gap flags.
- `manifest.json`: parent code revision, code and input SHA256, output file SHA256, counts, restrictions, reference-erratum status.

Do **not** point a DPO runner at this preview. A separately versioned, explicitly authorized **training-ready** preference manifest and EOS/tokenization audit are still required. The official GSM8K test set is prohibited and never accessed.
