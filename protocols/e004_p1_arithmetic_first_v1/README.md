# E004-P1 Arithmetic-First Relaxation — advisory v1

**Purpose:** Reclassify the **same selected top pair** in each of 135 frozen GSM8K TRAIN mixed-outcome source groups with a more practical DPO data-quality policy. **No training, no additional inference, no official test, no modifications of existing dataset/checkpoints.** This package is intentionally independent of the Git repository; install/extract under Downloads, not into the repository.

## Frozen inputs

- Source candidate run SHA256: `314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628` (the compact export was independently verified against this original on the host previously).
- Compact 135-group export SHA256: `fe0ce3a7bb4cd20fedf4ee25e15e171e0047ff786ae39f16c2db4118934dcff0`.
- Prior 135-source advisory review SHA256: `42952af0b07b90eb2a591d7651e97880d33b56b7414218babfa3a8925fc99707`.
- Frozen mechanical screen has been bundled byte-for-byte (its original checks remain unchanged).
- E002a baseline diagnostic Git revision: `0ae13a5870ebf0771c0abb6176d4a16f1eb52c93` (not consumed for filtering).

## Revised acceptance policy

1. Chosen response must meet the **existing mechanical gates**: final numeric reference match, at least two arithmetically true explicit equalities, no unverified/false explicit equalities, eligible native EOS, untruncated, sufficiently explanatory, and a rejected response with valid extraction and at least one checked equality. Chosen/rejected token gap ≤40. Do not alter pair ranking or rescue alternatives.
2. **Allow** spelling, pronoun, unit *labels*, reversed labels, incomplete descriptions, and messy rejected arithmetic **when** the mathematical operations in the chosen response still construct the intended numeric answer from the question. Such issues remain prominently documented.
3. **Reject** demonstrably wrong mathematical relationships, coincidences where the chosen intermediate quantities are not the question's quantities, materially ambiguous source prompts, and one wildly incoherent negative. Each such hard exclusion is explicitly source-ID listed in `scripts/reclassify_arithmetic_first_v1.py`, with reasons. No silent rewriting.
4. Every passing pair is **PROVISIONAL_ACCEPT_QC_REQUIRED**, never `approved_for_training`. This run reuses assistant judgments and does **not** constitute independent reasoning verification.

## Outcome

| Group | Count |
|---|---:|
| Pilot source questions | 250 |
| Mixed eligible questions | 135 |
| Mechanical top-pair passes | 91 |
| Hard rejects: material math or question relationships | 7 |
| Hard rejects: one unsuitable negative | 1 |
| **Provisional arithmetic-first pairs** | **83** |
| Other groups rejected mechanically | 44 |
| **Approved for training** | **0** |

Provisional yield **83/135 = 61.48% of mixed groups** or **83/250 = 33.20% of pilot questions**; this is **not an estimated training-usable verified-pair yield**.

## Reproduce without writing data

From the extracted package root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/reclassify_arithmetic_first_v1.py --verify
```

The script independently replays the arithmetic screening from its immutable 135-group input, rechecks previous selected pair indices, rebuilds the new decisions and the fixed QC worksheets, and compares each byte against the bundled outputs.

Optional **in-sample baseline-overlap diagnostic** from the host's pre-existing evaluation (read-only; parses the evaluator's non-standard pretty-printed concatenated JSON):

```bash
python3 scripts/reclassify_arithmetic_first_v1.py --verify \
  --coverage ~/projects/llm-post-training-lab/data/eval_runs/e004_p1_e002a_greedy250_0ae13a5_v1/coverage.jsonl
```

This additionally reports how many provisional groups were greedy-wrong vs greedy-correct; it doesn't affect acceptance or select training items.

## QC

- `outputs/qc_accepted30_unreviewed.md`: 30 randomly selected from 83 provisional pairs (seed `20261024`).
- `outputs/qc_rejected10_unreviewed.md`: eight explicit nonmechanical holds plus two random mechanical rejects; this sample is intentionally **stratified**, not a representative negative random sample.
- Review **critical mathematical errors** separately from tolerated **language defects**. All previous QC flags, even ones relaxed here, remain in the decision metadata.
- Do not treat this same-assistant retrospective review or this sample as independent human validation; a separate independent QC pass would be necessary to support a quality claim.
- Next decision gate: inspect 30 provisional accepts and 10 rejected candidates, measure material mathematical-error rate, then decide whether to scale generation. Do not start DPO or GRPO until separately authorized.
