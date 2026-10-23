# E003 DPO109 — signed-selection staging and independent audit (v1)

## Scope

This package is **DPO-only**. The existing E002a SFT adapter is the intended
starting point for the later DPO experiment. **There is no SFT retraining, model
loading, GPU work, DPOTrainer execution, or training authorization in these
scripts.** The three SFT-only corrections (sources 528, 3012 and 6515) are not
substituted into any original chosen/rejected preference pair.

The frozen 124-pair candidate preview is reduced to exactly **109 source-unique
pairs**: 108 previously reviewed and requester-self-attested original DPO
preferences, plus the separately approved source 5436 exception (sample 2
preferred over sample 0, derivative training reference 50; original reference 55
stays immutable). The 11 long-gap sources, four flagged for reasoning re-review,
21 original HOLD groups, and group-only source 2320 are not admitted.

The signed archive explicitly records requester self-attestation and explicitly
does *not* claim an independently authenticated signature, validation clearance,
or training authorization. Staging preserves that provenance.

## Files produced by staging

`pairs_staged.jsonl`: 109 lines in deterministic ascending `source_index` order;
each line contains only `prompt`, `chosen`, and `rejected` (original decoded text
untouched; **do not append EOS text**).

`pair_metadata.jsonl`: 109 corresponding records, with source/sample identities,
original byte hashes, original generated token ID streams (each ending in native
EOS ID **151643**), signed token-length gaps, and approval provenance.

`manifest.json`: exact input and output SHA256 digests, source exclusions,
validation screening outcome, Git revision, and explicit **NOT TRAINING AUTHORIZED**
status. Output is staged, *not* a frozen training release.

## Required inputs

- `~/Downloads/e003_final_review_signed_off_package.zip` SHA256
  `04b1e1ecd1daac8053f5a6a9a2143517169bfd8c6c2252b70325d0f69ea9f4aa`.
  The ZIP's internal four payload digests are also checked.
- Existing, independently audited
  `data/preference_runs/e003_dpo_candidate124_v1/{pairs_candidate.jsonl,manifest.json}`.
- Existing `configs/preference/e003_candidate124_second_pass_advisory_v1.json`,
  original frozen GSM8K train file and split config, plus pinned source 5436
  approval record.
- Repository canonical Python loader: `llm_post_training.data.loader.load_gsm8k_split`.
  If this loader cannot be imported, staging fails closed rather than guessing
  the split JSON schema. Official GSM8K test is never accessed.

## Recommended host sequence

Run these on the **host** from the repo root; do not run inside the model-serving
Docker container. First verify/install the package and run tests. Commit the
three new files. Then use the resulting Git HEAD in both invocations:

```bash
REVISION="$(git rev-parse HEAD)"
SIGNED="$HOME/Downloads/e003_final_review_signed_off_package.zip"
OUT="data/preference_runs/e003_dpo_signed109_staged_v1"

python3 scripts/stage_e003_dpo109_v1.py \
  --repo-root . --signed-review-zip "$SIGNED" \
  --output-dir "$OUT" --code-revision "$REVISION" --preflight-only

# Only after preflight exit code 0:
python3 scripts/stage_e003_dpo109_v1.py \
  --repo-root . --signed-review-zip "$SIGNED" \
  --output-dir "$OUT" --code-revision "$REVISION"

# Independent check, does not call the builder:
python3 scripts/audit_e003_dpo109_staged_v1.py \
  --repo-root . --signed-review-zip "$SIGNED" --output-dir "$OUT"
sha256sum "$OUT"/{pairs_staged.jsonl,pair_metadata.jsonl,manifest.json}
```

The stage command refuses to overwrite any existing target directory, even if
its contents match. Preflight mode writes nothing.

## Validation leakage policy

The builder checks all 109 source indices against the **frozen 6,726-train /
747-validation split** through the canonical repository loader. It requires the
staged question to match its original train question and blocks normalized exact
validation matches. It additionally blocks any validation question with five-word
shingle Jaccard similarity >=0.88, considering questions with >=12 unique
five-word shingles. This screening is conservative and may produce false
positives; if it does, **do not relax the threshold silently**. Inspect the
reported source/validation indices, document a clearance decision, and version
the policy explicitly. It is not a general guarantee of zero semantic leakage.

## Remaining release gates

1. Independent staged-dataset audit returns exit code 0.
2. Check DPOTrainer prompt/answer tokenization, EOS inclusion and loss masking
   using the exact offline Qwen3 tokenizer, base model and existing E002a adapter;
   pin training hyperparameters and reference policy treatment. Note: original
   **completion-only** token ID arrays are evidence, not automatically identical
   to tokenizer IDs for `prompt+completion` in every training template.
3. Version and freeze the dataset/configuration with a release manifest.
4. Obtain a **separate explicit human go/no-go** for the GPU DPO run.
5. Only then run DPO training, evaluate frozen validation vs E001/E002a and
   report metrics. Do not revise E002a or start E004 GRPO as part of this stage.
