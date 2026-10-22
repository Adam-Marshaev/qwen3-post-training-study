# E003 training-only reference erratum regrading v1

Status: CPU-only implementation; no optimization or pair selection.

Purpose: create a **derived** four-record overlay for GSM8K training source index 5436 after explicit project-owner authorization of the 55 -> 50 reference correction.

The script `scripts/regrade_e003_reference_erratum_v1.py` validates frozen source, split, proposal, adjudication, and committed approval by fixed SHA256. It audits the 1,024 original candidates and generator metadata, identifies the four selected source 5436 candidates, checks their native EOS token 151643, regrades twice using the project's numeric `Decimal` reference evaluator, and confirms the label flip.

Original candidate records are embedded intact in the derivative, next to corrected-reference fields. The original source file, selection split, original candidate dataset, reviews, proposal and approval files are never opened for writing. Output creation is fail-closed, only after checks; an existing output directory is never overwritten. Use `--preflight-only` before output creation.

New artifact directory: `data/preference_runs/e003_reference_erratum_5436_v1`.

Output files:

- `regraded_candidates.jsonl`: four original candidate dicts embedded under `original_candidate`, plus training-only corrected reference and corrected correctness labels. These are **not** DPO pairs.
- `manifest.json`: hashes of all six pinned inputs, implementation SHA, code revision, derivative file digest, and explicit no-training/no-pair-approval flags.

Expected label change by sample index:

| Sample | Extracted answer | Original correctness (ref 55) | Corrected correctness (ref 50) |
| ---: | ---: | :---: | :---: |
| 0 | 55 | True | False |
| 1 | 55 | True | False |
| 2 | 50 | False | True |
| 3 | 55 | True | False |

The erratum is **restricted to E003 training-derived preference labels**. Never retroactively alter original GSM8K, baseline/validation metrics, test data, or original E003 candidate labels. Reference correction approval **does not** imply pair approval. Sample 2 is a potential chosen candidate only; selection of any rejected candidate still requires independent adjudication. No DPO training is permitted by this artifact.

For canonical invocation, use `--code-revision "$(git rev-parse HEAD)" --output-dir /results/e003_reference_erratum_5436_v1` under the pinned, offline Docker image with `/workspace` read-only and `data/preference_runs` writable at `/results`.
