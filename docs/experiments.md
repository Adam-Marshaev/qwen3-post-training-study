# Experiment Registry

Project: Small Language Model Post-Training Laboratory

Purpose:
Maintain a reproducible record of baseline evaluations,
supervised fine-tuning, preference optimization, and
reinforcement learning experiments.

## Experiment Tracking Rules

1. Assign each experiment a unique ID: E001, E002, E003, etc.
2. Never fabricate or estimate measured benchmark results.
3. Record failed experiments when they provide useful evidence.
4. Preserve original observations when conclusions change.
5. Record the Git commit and model revision.
6. Record dataset identity, version, and split.
7. Record the random seed and relevant configuration.
8. Keep validation and final test results clearly distinguished.
9. Record hardware performance when relevant.
10. Compare experiments only under documented evaluation conditions.

---

## Experiment Status

Current status as of 2026-10-23:

- E001: Pretrained baseline completed.
- E002: Original SFT completed; EOS regression documented.
- E002a: Corrected native-EOS SFT completed and evaluated.
- E003: Signed-109 DPO training and validation completed; 433/747 (57.97%).
- E003b: Controlled DPO learning-rate ablation completed; 433/747 (57.97%), no net accuracy improvement.
- E004: GRPO not started.

The official GSM8K test partition remains untouched.

---

## Experiment Entry Template

### EXXX - Experiment Title

Date:
Status: Planned / Running / Completed / Failed

#### Goal / Hypothesis

Describe the research question and expected behavior.

#### Reproducibility

Git commit:
Model:
Model revision:
Dataset:
Dataset version:
Dataset split:
Random seed:

#### Configuration

Training method:
Precision:
Attention implementation:
Optimizer:
Learning rate:
Batch size:
Gradient accumulation:
Sequence length:
Epochs / training steps:

Generation settings:
- Decoding strategy:
- Temperature:
- Maximum new tokens:
- Stopping condition:
- KV cache:

#### Hardware

GPU:
CUDA runtime:
PyTorch version:
Peak allocated VRAM:
Runtime:

#### Results

Training loss:
Validation loss:
In-distribution accuracy:
Out-of-distribution accuracy:
Format compliance:
Average generated tokens:
Inference throughput:
Training GPU-hours:

Use N/A for genuinely inapplicable fields.
Use "Not measured" when a relevant measurement is unavailable.

#### Observations

Describe measured behavior, failure modes, and limitations.

#### Conclusion

Explain what the results support.

#### Follow-up

Identify the next experiment or investigation.

---

## E001 - Pretrained Qwen3 GSM8K Baseline

**Status:** Completed and verified
**Recorded:** 2026-10-22
**Evaluation type:** Frozen development-validation baseline

### Model and configuration

- Model: Qwen/Qwen3-0.6B-Base
- Model revision: 57ca99e94acb83175495aa2c6b6b0cc498170924
- Code revision: 08c71acb4e36e465f3c1c66e2f232fcb1c96a15f
- Dataset: GSM8K development validation
- Validation examples: 747
- Split manifest: configs/data/gsm8k_split_v1.json
- Split manifest SHA-256: 31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719
- Prompt version: gsm8k_qa_v1
- Answer extraction version: explicit_numeric_v2
- Precision: FP16
- Attention: eager
- Decoding: greedy
- KV cache: disabled
- Maximum new tokens: 512

### Results

- Correct: 420/747
- Exact-match accuracy: 56.2249%
- Valid extractions: 704
- Incorrect extracted numerical answers: 284
- Missing answers: 42
- Ambiguous answers: 1
- Extraction rate: 94.2436%
- Unwanted continuation rate: 89.8260%
- Responses reaching token cap: 15
- Token-cap rate: 2.0080%
- Mean generated tokens: 109.44

### Artifacts

- Predictions: data/eval_runs/e001_pretrained_val512_v1/predictions.jsonl
- Summary: data/eval_runs/e001_pretrained_val512_v1/summary.json
- Predictions SHA-256: 47c63293195a6fa729b5bd5af6532b9a9699dcbbb8170fd75ef44f53e9c1fbf3
- Summary SHA-256: 93c709884b98b9f7aa3a427b9370df5062a08ff927b5ebb1a1ee09ed8a6f9469

### Integrity verification

- All 747 expected validation source indices evaluated exactly once.
- No missing or unexpected validation examples.
- Saved correctness and token-cap counts match the summary.
- Model, code, prompt, extractor, and generation configuration verified.

### Interpretation

This is a development-validation result, not an independent
official GSM8K test-set estimate.

The official GSM8K test split remains untouched.

The generation and grading configuration must remain identical
for subsequent model comparisons unless a change is explicitly
versioned and applied consistently across all variants.

<!-- sft_eos_ablation_and_e003_pilot_2026_10_22 -->

## E002/E002a: SFT EOS-Supervision Ablation

**Status:** Complete and audited, 2026-10-22.

### Experimental design

Both experiments fine-tuned the same pinned Qwen3-0.6B-Base
checkpoint on the frozen 6,726-example GSM8K training partition.

The sole intended difference in the training objective was
the supervised completion-termination token:

| Property | E002 | E002a |
|---|---|---|
| Supervised EOS | 151645 (`<|im_end|>`) | 151643 (`<|endoftext|>`) |
| Base model | Same | Same |
| Training examples | 6,726 | 6,726 |
| Epochs | 2 | 2 |
| Optimizer steps | 422 | 422 |
| Supervised tokens | 1,264,128 | 1,264,128 |
| LoRA and optimizer settings | Original | Identical |

The full dataset audit verified that corresponding tokenized
examples differed only in their final EOS token. Actual EOS labels
were supervised even when native EOS and PAD shared ID 151643;
padding labels remained -100.

### Validation results

GSM8K validation partition: 747 questions.

| Model | Correct | Accuracy | Protocol |
|---|---:|---:|---|
| E001 pretrained | 420/747 | 56.22% | Historical uncached |
| E002 original SFT | 318/747 | 42.57% | Historical uncached |
| E001 pretrained | 419/747 | 56.09% | Cached v1 |
| E002a native-EOS SFT | 433/747 | 57.97% | Cached v1 |

Cached v1 uses eager attention, FP16 base weights, greedy decoding,
a 512-token generation limit, native EOS 151643, KV caching,
the frozen gsm8k_qa_v1 prompt, and explicit_numeric_v2 extraction.

Historical E002 and cached E002a accuracy results are not
a perfectly protocol-matched full-validation comparison.

### Protocol-matched E001 versus E002a

- E001 correct: 419/747.
- E002a correct: 433/747.
- Observed improvement: +14/747 (+1.874 percentage points).
- Both correct: 324.
- E001 only correct: 95.
- E002a only correct: 109.
- Both incorrect: 219.
- Discordant pairs: 204.
- Exact two-sided McNemar p-value: 0.362761.
- Paired bootstrap 95% CI: [-2.01, +5.62] percentage points.

The observed accuracy increase is not statistically significant.
These findings do not establish equivalence between the models.

### Termination behavior

| Metric | E001 cached | E002a cached |
|---|---:|---:|
| Native-EOS stops | 65/747 | 734/747 |
| Token-cap responses | 13/747 | 13/747 |
| Mean generated tokens | 108.77 | 97.71 |
| Answer extraction rate | 94.2% | 98.3% |

Historical E002 generated an average of 448.8 tokens and reached
the 512-token cap on 579/747 validation responses.

At matched epoch-1 checkpoints, E002 strongly suppressed native EOS
on eight tested training completions, whereas E002a ranked native
EOS first on all eight with mean probability 0.999813.

On a separate 12-question held-out generation diagnostic,
E002a epoch 1 stopped with native EOS in all 12 responses.

**Interpretation:** The controlled evidence strongly supports
native-EOS supervision as a major correction for E002's termination
regression. It does not prove that EOS selection was the only cause
of every accuracy or generation difference.

### Provenance

- Base model revision:
  `57ca99e94acb83175495aa2c6b6b0cc498170924`
- E002a training revision:
  `31b73e9ac15572b44ee479ce047048d6404bb72f`
- E002a training config SHA256:
  `11c9977d2edc288129a2fafdf6331e473fab79beee88d6fc32cb0e4b7cedae52`
- E002a final adapter SHA256:
  `f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`
- Cached evaluator revision:
  `d734c6c5da15f29ab01e455b8cb70a91522f4aed`
- Inference protocol:
  `gsm8k_val512_greedy_eager_cached_v1`
- E002a final adapter:
  `data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/`
- Cached E001 results:
  `data/eval_runs/e001_pretrained_cached_val747_v1/`
- Cached E002a results:
  `data/eval_runs/e002a_epoch2_cached_val747_v1/`

The official GSM8K test set was not used.

### E003: Preference-Generation Pilot

**Status:** Pilot complete; DPO training not started.

The frozen E002a epoch-2 adapter generated four sampled candidates
for each of 32 selected GSM8K training questions.

| Metric | Result |
|---|---:|
| Questions | 32 |
| Candidates | 128 |
| Eligible candidates | 127 |
| Correct eligible candidates | 53 |
| Native-EOS stops | 127 |
| Token-cap responses | 1 |
| Mixed groups allowing potential pairs | 21 |
| Groups with no correct eligible candidate | 8 |
| Groups with all four candidates correct | 3 |
| Mean generated tokens | 95.2578 |
| Mean generation seconds | 1.8191 |

The observed potential-pair yield was 21/32 (65.625%).
This is a small pilot estimate, not a guaranteed full-dataset yield.

Pilot code revision:
`dd3a80247c92e57d5d01d8e8531778e861b5b2ad`

Pilot configuration SHA256:
`e57f800f08dc58c8b4c8d4f97ce641762950c0955e1375739e652f3079b24d1c`

Pilot artifacts:
`data/preference_runs/e003_pilot32_k4_v1/`

The pilot used the GSM8K training partition only and performed
no model optimization.

**Decision:** Proceed to candidate-quality auditing and deterministic
preference-pair construction before scaling generation or starting DPO.


<!-- e003_provisional_pairs18_verified_v1 -->

### E003: Verified Provisional Preference-Pair Artifact

**Status:** CPU-only construction and integrity audit complete.

- Input: 128 frozen E002a-generated pilot candidates.
- Mixed correct/incorrect groups: 21.
- Provisionally selected preference pairs: 18.
- Held groups: 1.
- Excluded groups: 2.
- Unique training questions represented: 18.
- Median selected-pair length difference: 14.5 tokens.
- Maximum selected-pair length difference: 64 tokens.
- Native completion EOS: 151643.
- Candidate token sequences preserved exactly.
- Builder revision: `6c911165cc8643c11550b7e71d389d35c14ea7e3`.
- Regression suite: 149 passing tests.
- Artifact: `data/preference_runs/e003_pilot_pairs18_v1/`.
- Pairs SHA256: `ecc3748b6c54f4ea66d8173bb4a81e7b3b412db59d69d1307a07da825778dca8`.
- Independent human signoff: not obtained.
- Training authorization: not granted.
- DPO optimization: not started.

The original candidate generation, screening decisions, and pair
construction are separately versioned and auditable.

These 18 pairs validate the data pipeline. They are not a
full-scale DPO training dataset.

---

## E003 — Signed-109 DPO Training

**Training status:** Completed, 2026-10-23.
**Validation status:** Completed, 433/747 (57.97%); see paired audit below.

### Reproducibility

- Training code revision:
  `f16e90360690df121132bc6055282f27302a132a`
- Starting checkpoint:
  `data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/`
- Approved preference pairs: 109.
- Pair dataset SHA256:
  `7d088bd70dc1d3d8b05f251a5560b37aca24a064ec7c4c81c91a03b8d84dc8e9`
- Docker image:
  `sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e`

### Training configuration

- Method: LoRA DPO, sigmoid loss.
- Beta: 0.1.
- Learning rate: 1e-6.
- Epochs: 1.
- Effective batch size: 8.
- Optimizer updates: 14.
- GPU: Tesla V100-SXM2-32GB.
- Precision: FP16 base, FP32 LoRA.
- Attention: eager.
- PyTorch native Triton overrides: disabled.
- Reference: frozen E002a epoch-2 adapter.
- Native completion EOS: 151643.
- Training KV cache: disabled.
- Generation/evaluation KV cache: enabled.

### Observed training results

- Training runtime: 16.0518 seconds.
- Mean training loss: 0.692963821547372.
- Completed steps: 14/14.
- Final adapter tensors changed versus E002a: 224/224.
- Layers containing changed tensors: 28/28.
- Maximum absolute tensor-weight difference: approximately 7.39e-6.
- Saved adapter tensors: finite.
- Gradient-checkpointing warning observed; subsequent tensor audit
  confirmed updates across all saved LoRA tensors.

### Artifacts

- Training output:
  `data/train_runs/e003_dpo_signed109_f16e903_v1/`
- Final adapter:
  `data/train_runs/e003_dpo_signed109_f16e903_v1/final_policy_adapter/policy/`
- Final adapter SHA256:
  `10ae46d412f87e39e95891455fd41e7b6d9bd20bd8e9110a304b38d37a09af4a`
- Training log:
  `data/train_runs/e003_dpo_signed109_f16e903_v1.launch.log`
- Validation evaluator revision:
  `44fba97f6decaaf802713056f12ebd89984584d6`
- Validation run:
  `data/eval_runs/e003_dpo_signed109_cached_val747_v1_retry1/`

### Interpretation

Training completed and produced measurable adapter-weight changes.
No reasoning-accuracy improvement is claimed before the frozen
747-question development-validation evaluation is verified.
The official GSM8K test partition was not used.

---

## E003 — Frozen Validation and Paired Audit

**Status:** Completed and paired-audited, 2026-10-23.

- Validation examples: 747.
- E002a correct: 433/747 (57.97%).
- E003 DPO correct: 433/747 (57.97%).
- Net accuracy change: 0.00 percentage points.
- Both correct: 427.
- Both incorrect: 308.
- DPO correctness gains: 6.
- DPO correctness losses: 6.
- Discordant correctness pairs: 12.
- Exact two-sided McNemar p-value: 1.0.
- Changed raw responses: 82/747.
- Unchanged raw responses: 665/747.
- DPO mean generated tokens: approximately 97.5.
- DPO answer extraction rate: approximately 98.3%.
- DPO responses reaching the 512-token cap: 13.

### Evaluation provenance

- Evaluation code revision:
  `44fba97f6decaaf802713056f12ebd89984584d6`
- Inference protocol: `gsm8k_val512_greedy_eager_cached_v1`.
- Greedy decoding, FP16, eager attention.
- Native EOS: 151643.
- Maximum new tokens: 512.
- KV cache: enabled.
- Frozen GSM8K development-validation split.
- Official GSM8K test set: untouched.

E002a predictions SHA256:
`b14a887d3942dcd0dec56abac1f4ea9ec748573d4a2d703dac1457e52df31b9c`

E003 predictions SHA256:
`7da6283538b92f27518be8b140785fc5a6bd21fd34b674ac9549d3d3f8399d7c`

E003 evaluation artifacts:
`data/eval_runs/e003_dpo_signed109_cached_val747_v1_retry1/`

### Interpretation

The first E003 DPO run changed 82 raw validation responses,
including six correctness gains and six correctness losses.

Aggregate accuracy was unchanged relative to E002a.
The paired comparison provides no evidence of an accuracy
improvement in this run, but does not establish model equivalence.

This result applies to the signed-109 dataset and the specific
one-epoch, 14-step, 1e-6-learning-rate configuration tested.

---

<!-- e003b_lr5e6_complete_2026_10_23 -->

## E003b — Controlled DPO Learning-Rate Ablation

**Status:** Training, preference audit, validation and paired analysis completed.

### Experimental design

E003b tests a fivefold DPO learning-rate increase while preserving
the approved E003 preference dataset and all other training settings.

| Setting | E003 | E003b |
|---|---|---|
| Starting checkpoint | E002a epoch 2 | Same |
| Preference pairs | 109 | 109 |
| Epochs | 1 | 1 |
| Optimizer steps | 14 | 14 |
| Learning rate | 1e-6 | 5e-6 |
| DPO beta | 0.1 | 0.1 |
| Effective batch size | 8 | 8 |
| Training KV cache | Disabled | Disabled |

Approved preference-pair dataset SHA256:
`7d088bd70dc1d3d8b05f251a5560b37aca24a064ec7c4c81c91a03b8d84dc8e9`

Starting E002a adapter SHA256:
`f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`

### Training provenance

Training Git revision:
`66822ee01f2b3958dc30ef764479534214eed922`

Training script:
`scripts/train_e003b_dpo_signed109_lr5e6_v1.py`

Training run:
`data/train_runs/e003b_dpo_signed109_lr5e6_66822ee_v1/`

Final adapter SHA256:
`f28b9644a9f656f46894720a0c42ae339d25705260985092b2453e735d60a741`

Measured training:
- Completed optimizer steps: 14.
- Reported average training loss: 0.691045480115073.
- Training runtime: 15.9834 seconds.
- Modified LoRA tensors: 224/224.
- All adapter tensors finite.
- Training native EOS: 151643.
- Training KV cache: disabled.

Global L2 adapter difference from E002a:
- E003: 0.00452754008633176.
- E003b: 0.022666958783056874.
- E003b/E003 magnitude ratio: 5.0065.

### Training-pair preference audit

| Measurement | E003 | E003b |
|---|---:|---:|
| Mean preference-margin improvement | +0.060744 | +0.330544 |
| Median improvement | +0.031250 | +0.218750 |
| Final mean training-pair DPO loss | 0.69012507 | 0.67696388 |
| Positive margin changes | 69 | 91 |
| Negative margin changes | 31 | 16 |
| Zero margin changes | 9 | 2 |
| Pairs preferring chosen | 79/109 | 79/109 |

These measurements use the training preference pairs, not held-out
preference examples. They establish stronger optimization of the
training objective, not generalization.

### Frozen GSM8K development validation

Evaluation protocol:
`gsm8k_val512_greedy_eager_cached_v1`

- Questions: 747.
- Decoding: greedy.
- Precision: FP16.
- Attention: eager.
- Maximum new tokens: 512.
- Native EOS: 151643.
- Evaluation KV cache: enabled.
- Official GSM8K test set: untouched.

| Model | Correct | Accuracy |
|---|---:|---:|
| E002a | 433/747 | 57.97% |
| E003 | 433/747 | 57.97% |
| E003b | 433/747 | 57.97% |

E003b evaluation artifacts:
`data/eval_runs/e003b_dpo_signed109_lr5e6_cached_val747_v1/`

E003b predictions SHA256:
`9026502bf9c23e9490df2eb1d14c38adedfe2b1f07b649f14877717c6d2d0dcd`

### Paired evaluation

E003b versus E002a:
- Both correct: 422.
- Both incorrect: 303.
- Correctness gains: 11.
- Correctness losses: 11.
- Changed raw responses: 178/747.
- Exact two-sided McNemar p-value: 1.0.

E003b versus E003:
- Both correct: 421.
- Both incorrect: 302.
- Correctness gains: 12.
- Correctness losses: 12.
- Changed raw responses: 158/747.
- Exact two-sided McNemar p-value: 1.0.

Across the three models:
- All three correct: 418.
- All three incorrect: 300.
- Differing correctness outcomes: 29.

### Qualitative error analysis

The 11 E003b gains versus E002a involved genuine corrections to
mathematical reasoning or previously incomplete solutions.

The 11 losses involved incorrect arithmetic, mathematical relationships,
quantity aggregation, dimensional reasoning, or incomplete solutions.

In particular:
- Source 1374: corrected double-counting of books.
- Source 3668: correctly doubled ingredients after efficacy was halved.
- Source 1034: completed a previously repetitive solution.
- Source 5348: introduced an incorrect square-unit conversion.
- Source 7366: introduced double-counting of packages.
- Source 1533: introduced repetitive, unfinished reasoning.

The same broad reasoning operations occurred among improvements
and regressions. No uniformly more reliable reasoning procedure
was demonstrated.

### Conclusion

Increasing DPO learning rate from 1e-6 to 5e-6 strengthened
optimization of the 109 training preferences and produced larger
adapter updates and more changed validation responses.

However, aggregate GSM8K accuracy remained unchanged at 433/747.

These findings do not establish model equivalence or prove that
dataset size alone caused the lack of improvement.

Preserve the original E003 and E003b checkpoints and evaluation
artifacts. Any expanded preference dataset must be separately
versioned, reviewed and authorized.

<!-- e004_p3_handoff_2026_10_24_v1 -->

---

## E003: DPO Results and E004 Experiment Handoff (2026-10-24)

**Status:** E003 completed; E004 preference-data generation in progress;
no E004 DPO or GRPO training authorized or performed.

### E003 DPO results (frozen 747-question development validation)

E002a native-EOS SFT reference: **433/747 (57.97%)**. E003 began
from the frozen E002a epoch-2 LoRA adapter (SHA256
`f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`).

| Run | Preference data | Settings | Validation result |
|---|---|---|---|
| E003 | 109 signed unique-source pairs | beta=0.1; LR=1e-6; 1 epoch; 14 steps | 433/747 (57.97%) |
| E003b | Same 109 pairs | LR=5e-6 | 433/747 (57.97%) |

E003 changed six validation responses from correct to wrong and six
from wrong to correct relative to E002a. E003b had 11 gains and 11
losses relative to E002a. Neither improved overall validation accuracy.
A correct numeric answer did not always imply sound intermediate reasoning.
Do not use the official GSM8K test set for selection or tuning.

### E004: Arithmetic-first DPO preference-data scaling

**Goal:** approximately 500–1,000 useful source-unique preference
pairs, subject to quality auditing; target is not a hard acceptance quota.
**E004 is DPO data-scale work; E005 GRPO is only a possible later path.**
Historical notes describing E004 as GRPO are superseded by this entry.

Frozen GSM8K development split: 6,726 training questions and 747
validation questions. E004 sampled *training* questions only, disjoint
from previously sampled preference pools. Generation used frozen E002a,
four responses per source, temperature 0.8, top-p 0.95, maximum 256
new tokens, native EOS 151643, and no weight updates.

| Measure | P1 | P2 | Combined |
|---|---:|---:|---:|
| Distinct source questions | 250 | 250 | 500 |
| Generated responses | 1,000 | 1,000 | 2,000 |
| Eligible responses | 987 | 991 | 1,978 |
| Eligible correct responses | 525 | 539 | 1,064 |
| Mixed eligible correct/incorrect groups | 135 | 137 | 272 |
| Groups passing mechanical screen | 91 | 87 | 178 |
| Arithmetic-first provisional pairs | 83 | 80 | **163** |
| Provisional yield per source question | 33.2% | 32.0% | 32.6% |

The arithmetic-first policy permits minor wording and unit-label
imperfections but holds material arithmetic/quantity-relation errors,
coincidental correct answers, and material question ambiguity. Original
answers are not rewritten or repaired. P1/P2 source-specific assistant
holds are historical advisory decisions, **not a general-purpose
automatic semantic verifier**. QC worksheets contain 30 provisional
accepts and 10 rejects per pilot; assistant review is not independent
quality certification. **Approved E004 training pairs: 0.**

#### Immutable provenance

- P1 generator commit: `fc6d48475f018c1a26d98d81694c8b6fbc31b815`.
- P1 candidates SHA256: `314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628`.
- P1 review freeze commit: `fde14abdf6791a0796799087f85154982e1628dd`.
- P1 advisory decision SHA256: `b7114a4f91f22dd30fd0e66b5818e2f3c8cc9f05023ff308c508416f89ee945c`.
- P2 generator commit: `f543aa41ff917d96b8f26b38df9c6c00f91b1619`.
- P2 candidates SHA256: `568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79`.
- P2 selection SHA256: `3bd3ebf184b551394f7137ec6cf0096c312139ea68d94a61e051b5f9a4c40d72`.
- P2 review decision SHA256: `8e5adf5663b753ff14b9db1ee5a845643e7dfb1c07ca69f8b948bf29919e0cdb`.
- P2 review freeze commit: `331499df3175737bb9464a3d9a53a365fc494431`.
- Docker image ID: `sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e` (do not use mutable tag).
- P1 run: `data/preference_runs/e004_p1_250_k4_fc6d484_v1/`.
- P2 run: `data/preference_runs/e004_p2_250_k4_f543aa4_v1/`.
- Reviews: `protocols/e004_p1_arithmetic_first_v1/` and
  `protocols/e004_p2_arithmetic_first_v1/`.

#### E004-P1 deterministic baseline coverage (TRAIN partition diagnostic)

E002a greedy inference on all 250 P1 training sources: 145 correct,
105 wrong (58.00% accuracy). Of 135 mixed-response questions, 84 were
correct and 51 wrong (37.78% error); among 115 other questions, 61
correct and 54 wrong (46.96% error). Of the 83 provisional P1 pairs,
27 corresponded to greedy baseline errors and 56 to successes.
This is **in-sample training-partition coverage**, not held-out
validation or evidence that DPO improves generalization.

- Predictions SHA256: `f549c524edb4720a6bdabb372ab75892faae0d35b6e3f72ad149fed0c471150c`.
- Coverage SHA256: `1e8aab76fd3bb271c40c79393fb678ba335b9a9a77d18594dbd1a5bdb49a7c52`.
- Note: original final files named `.jsonl` contain concatenated pretty
  JSON records, not newline-delimited JSON objects; preserve originals.

#### E004-P3 selected, generation NOT started

- Starting revision for planning: `331499df3175737bb9464a3d9a53a365fc494431`.
- Excluded prior source questions: 788 = 32 E003 pilot + 256 E003
  scale + 250 P1 + 250 P2; 5,938 previously unused training sources.
- P3 selection seed: `42006`; exactly **1,200** new questions.
- Frozen selection SHA256: `bfeb83304623bfdb2c8c952cba46d48ac36e251414b79d4763fb24f21b6ffed9`.
- First 10 source indices: `[12, 30, 31, 46, 48, 50, 52, 54, 56, 63]`.
- Previous-pool and development-validation source overlap: zero.
- Planned generation: 4,800 responses (four per question).
- **Not yet done:** P3 generator/config commit, GPU smoke test,
  full P3 run, P3 filtering/QC, E004 training.
- P3 generator/config files are now installed as five untracked local
  repository files (config, protocol, builder, generator, tests), but
  have NOT been committed or used for GPU inference.

Continue by forking the pinned P2 generator with **separate historical
250-question selection counts** and new P3 1,200-question count; keep
historical E003/P1/P2 selections immutable. Verify code, config,
selection SHA, 788-source exclusions, preflight, and two-group smoke
before resuming generation. Do not use validation for question selection.
No E004 DPO/GRPO training without separate explicit authorization.
