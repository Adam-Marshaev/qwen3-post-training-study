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

---

<!-- e004_dpo_completed_validation_freeze_2026_10_25_v1 -->

## E004 — Arithmetic-First Preference Scaling, DPO Training, and Validation (2026-10-25)

**Status:** Completed, evaluated, paired-audited, and reproducibly frozen. This section supersedes the *status*, but not the historical observations, in the October 24 E004-P3 handoff above. **E004 is DPO, not GRPO.** No E005/GRPO training is authorized.

### Research question and design limitations

Does DPO on a larger set of automatically screened GSM8K preference pairs improve the frozen E002a SFT policy where E003/E003b did not? E004 changes **both pair count and curation method** relative to E003's independently approved 109 pairs; it is not a controlled size-only ablation. The 586 E004 pairs were automatically screened and remain **provisional, not independently reasoning-certified**. Any statement about preference quality must retain that distinction.

### Frozen training data and provenance

- Model: `Qwen/Qwen3-0.6B-Base`, revision `57ca99e94acb83175495aa2c6b6b0cc498170924`.
- Starting E002a epoch-2 adapter: `data/train_runs/e002a_sft_lora_native_eos_v1/epoch_0002/adapter/adapter_model.safetensors`; SHA256 `f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`.
- Frozen split: `configs/data/gsm8k_split_v1.json`, SHA256 `31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719`; original GSM8K training indices: 6,726; validation: 747; overlap: zero. No official GSM8K test access.
- P1: 250 training questions / 1,000 candidates / 83 provisional pairs.
- P2: 250 training questions / 1,000 candidates / 80 provisional pairs.
- P3: 1,200 additional training questions / 4,800 candidates / 641 mixed-correctness groups. Initial mechanical screening yielded 425 candidate accepts; two material reasoning defects (source indices 3115 and 4201) were held after QC, leaving **423 provisional pairs**. The **216 mechanical rejects were preserved**, not discarded. A mechanical screen is not independent reasoning review.
- Total frozen preference dataset: **586 source-unique pairs** = 83 + 80 + 423; all drawn from the GSM8K development-training partition, with zero development-validation overlap.
- P3 candidates SHA256: `7825edfec54b26427fa48876c087dc75ab53d38a6bd85cee54d8b6b207b10ed1`; triage manifest SHA256: `f67c32d754ff33a4418e9a92cbfa5fe0424cb684d9f1d5efa0984f8c310764fa`.
- Combined provisional pairs: `data/preference_runs/e004_combined_provisional_v1/outputs/provisional_pairs_586.jsonl`; SHA256 `2990b9da6294a125b8c92d755a226a50f32f4c1f6c8d1bbaa608d609be99e06e`.
- DPO-staged pairs: `data/preference_runs/e004_dpo_staging_preflight_v1/outputs/pairs_staged_586.jsonl`; SHA256 `cf0d3f4998306cbb9ce237d0c8dda2eba96163e6e2ddc95b7bbba330b1c47c86`; staging manifest SHA256 `daf30944f46030734e714eb30418877d0bf8b7d189f8e5fd460fcaed4dc1238a`.
- Combined dataset builder freeze commit: `83b08e3eb40de12e155e4e5dbb6514e94cde13dc`.

### Training configuration and integrity

- Historical E003 training image: `sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e`; Transformers 4.57.6, TRL 0.26.2, datasets 4.0.0, PEFT 0.18.1; Tesla V100-SXM2-32GB, FP16 base/eager attention, FP32 LoRA.
- DPO: `beta=0.1`, sigmoid loss, `learning_rate=1e-6`, 1 epoch, batch size 1, gradient accumulation 8, effective batch 8, seed 42, linear schedule, AdamW, native EOS/PAD ID `151643`, training KV cache **off**. Policy and reference begin as identical E002a LoRA weights; policy trainable, reference and base frozen.
- CPU preflights: historical TRL tokenization **586/586** (max prompt/chosen/rejected/joint tokens **144/237/250/387**); collator **586/586** with **1,534** verified padding checks. GPU no-training DPOTrainer preflight: **224/224** exact FP32 policy/reference tensors, matching chosen/rejected log-probabilities, initial sigmoid loss **0.693359**, optimizer absent, zero steps. Preflight peak allocated **1,296.1 MiB**, **not** peak training memory.
- Preparation-only configuration: `protocols/e004_dpo_preparation_v1/config_draft_v1.json`, SHA256 `a559c2b191f15d84cc6e502bad05b3186afc7b3b94f6b744e032a7bedcfdc5ff`; configuration freeze commit `8c4a3eba28475925190614b18764dbedb9230c6e`. Its `training_authorized=false` field records its earlier **preparation-only** state; separate explicit authorization preceded the later E004 run.
- No-training integration preflight: `protocols/e004_dpo_preparation_v1/preflight_e004_dpo_trainer_v1.py`, SHA256 `35c016b1124c40be7bb0a3b9c6344a6e706ee5250cd55cc0bd76cd2cbf24cb82`, commit `cf8cd7e91a1d09d6adda6cd79fe9c38a6615a566`.
- Authorized training-source commit: `c9e5141c8ba254dc509092eff929b8489002234e`; script `protocols/e004_dpo_preparation_v1/train_e004_dpo_autoscreened586_v1.py`.
- Training output: `data/train_runs/e004_dpo_autoscreened586_v1/run/`; **74/74 optimizer steps**, epoch 1.0, reported mean loss **0.6923210258419449**. Final adapter: `run/final_policy_adapter/policy/adapter_model.safetensors`; SHA256 `e63dd7bdbfc5b1b5444b9e83f400a98b00c792770f8e4d70ee26ab29cc62b6fa`. All **224/224** FP32 LoRA tensors finite and changed from E002a; maximum absolute tensor-element change `2.782023511826992e-05`. Original dataset and starting adapter unchanged.

### GSM8K development-validation evaluation

Protocol: `gsm8k_val512_greedy_eager_cached_v1`; frozen 747 validation examples, `gsm8k_qa_v1` prompt, `explicit_numeric_v2` extraction, FP16, eager attention, greedy generation, maximum 512 new tokens, native EOS/PAD `151643`, generation KV cache **on**. Neither the official test split nor additional training was used during evaluation.

| Checkpoint | Source preferences | Correct / 747 | Accuracy |
|---|---:|---:|---:|
| E002a native-EOS SFT | N/A | 433 | 57.97% |
| E003 DPO | 109 independently approved | 433 | 57.97% |
| E003b DPO (higher learning rate) | Same 109 | 433 | 57.97% |
| **E004 DPO** | **586 provisional** | **439** | **58.77%** |

E004 versus E002a: **+6/747 correct**, or **+0.803 percentage points**. E004 answer extraction rate **98.5%**, mean generated tokens **97.2**, and **11** responses at the 512-token cap. This is a point-estimate improvement, **not a statistically established superiority claim**.

- Evaluation source: `scripts/evaluate_e004_dpo_gsm8k_v1.py`, committed at `a198befdfcf8509326dbfe99d253fe99bd840e3f`.
- E004 output: `data/train_runs/e004_dpo_autoscreened586_v1/eval_gsm8k_val747_v1/full_validation/summary.json` and `predictions.jsonl`.
- Baseline comparison: `data/eval_runs/e002a_epoch2_cached_val747_v1/summary.json` and `predictions.jsonl`.
- Evaluation summary's adapter provenance uses the **legacy key `e003_training`**, but its embedded experiment identity, training source commit, 74 steps and checkpoint SHA256 all verify **E004**. Preserve the original output; this is a metadata-key defect, not use of the E003 checkpoint.

### Paired statistical and qualitative analysis

| Paired correctness | Count |
|---|---:|
| Both correct | 430 |
| Both incorrect | 305 |
| E004 corrected E002a | **9** |
| E004 regressed from E002a | **3** |

- Exact two-sided McNemar **p = 0.14599609375**, not significant at alpha 0.05.
- Corrected original GSM8K source indices: `182, 276, 768, 1034, 4502, 4542, 5065, 7033, 7415`.
- Regressed original source indices: `494, 2061, 6596`.
- Seven corrections had coherent arithmetic, relation, completeness, or question-target reasoning; index **1034** escaped a baseline repetitive 512-token generation loop; index **4502** yielded the correct final answer despite an inconsistent intermediate sign calculation.
- Regressions: index **494** sign/direction error (the baseline's correct final answer also followed a flawed subtraction statement); **2061** omitted rectangle width when finding perimeter; **6596** used one-half instead of the required `5/9` ratio.

### Research conclusion and frozen record

The larger automatically screened E004 dataset yielded the first positive **aggregate** DPO validation change in this series, but its +0.80-point advantage is small and **not statistically significant** under the paired exact McNemar test. Because data quality/curation and volume changed together, causal attribution to pair count alone is unsupported. Correct numerical answers do not guarantee valid intermediate reasoning.

- Reproducibly frozen research record: `protocols/e004_dpo_preparation_v1/e004_research_result_v1.json`; SHA256 `683b6d7ed950ce01a17802cc670c6d5dff85bd1f3c5485cca37b9fae51dfd4ed`.
- Research-result freeze commit: `e7d5a4296e9978b97a24bbd8534aec810f99fc29`.
- This record contains SHA256 hashes of the historical baseline and E004 **evaluation summary/prediction artifacts** and 12 source-index-specific audit annotations; avoid substituting estimated hashes in documentation.
- Next possible investigation: controlled preference-data quality/curation study (or separately designed GRPO), without assuming that more pairs, steps, or learning rate will improve generalization. **No E005 training initiated or authorized.**


---

<!-- e005_grpo_completed_validation_freeze_2026_10_25_v1 -->

## E005 — GRPO Training, Development Validation, and Paired Audit (2026-10-25)

**Status:** Training completed, evaluated, paired-audited, and reproducibly frozen. This later entry supersedes earlier *planning/status* notes that E005 was hypothetical or unauthorized; those earlier entries are retained as historical observations. **E004 is DPO; E005 is GRPO.** The official GSM8K test partition remains unused.

### Research question and design

Does bounded final-answer-reward GRPO starting from the validated E002a native-EOS SFT checkpoint improve mathematical reasoning on the frozen GSM8K development partition? E005 is a **separate branch from E002a**, not a continuation of E004 DPO. It uses exact final-answer correctness, not explicit intermediate-reasoning verification.

### Frozen training identity

- Model: `Qwen/Qwen3-0.6B-Base`; revision `57ca99e94acb83175495aa2c6b6b0cc498170924`.
- Starting E002a adapter SHA256: `f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`.
- Frozen split: `configs/data/gsm8k_split_v1.json`; SHA256 `31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719`; **6,726 training / 747 development** questions.
- Frozen GRPO training input: `data/train_runs/e005_grpo_from_e002a_v1/inputs/grpo_train6726_v1.jsonl`; SHA256 `93cc63e8e57cab769cc27b136707b63943b47be02de5a82d889bd0196e6ee866`.
- Training plan: `protocols/e005_grpo_preparation_v1/e005_grpo_training_plan_v1.json`; SHA256 `249c4d51f323b03ed92b3071e0da558adcbcb6b89e773c04bc1619dbd5b63102`.
- Reward implementation: `src/llm_post_training/training/grpo_reward.py`; SHA256 `152d7cac32736fb8f797644642ea2351427b8c6e2b911531c1b88acbfc4b7acb`.
- Authorized training-source commit: `ab42f55475fcc104261e380ef52dd143c50b66ca`; code: `protocols/e005_grpo_preparation_v1/train_e005_grpo_v1.py`.

### Completed training

- Method: LoRA GRPO; **256/256 optimizer updates**, learning rate `1e-6`, four sampled completions per group, maximum completion length 512; FP16 base and eager attention on a Tesla V100-SXM2-32GB.
- Sampled training trace: **1,024 completions**, of which **367** had correct final answers; **150/256** groups had mixed rewards. These are on-policy *training rollout statistics*, not held-out accuracy.
- Reported training runtime: approximately **963.7 seconds**; mean reported training loss: **0.02954345**. These measurements are training diagnostics, not evidence of generalization.
- Final adapter: `data/train_runs/e005_grpo_from_e002a_v1/run/final_policy_adapter/policy/adapter_model.safetensors`; SHA256 `4246d1c0a2381be6fe50066d21c35390d69086f2975b4ef9e76b3bc658a1ae59`.
- Reward rollout trace SHA256: `56c35638b477840ee6232dc267ee1b0d6593afa7d69972b0368ac6d3c1148dfb`.

### Frozen development evaluation

- Evaluation-source commit: `6dea3a6e60892ca76934c767e5dafb361d590564`; evaluator: `scripts/evaluate_e005_grpo_gsm8k_v1.py`; evaluator SHA256: `bb079bcd0436e7d73a6fd0ff13ebbe2583c48bd3eecd3b50ed3b236cef7baa98`.
- Formal inference protocol: `gsm8k_val512_greedy_eager_cached_v1`; 747 frozen development questions, `gsm8k_qa_v1`, `explicit_numeric_v2`, FP16/eager, greedy generation, EOS/PAD 151643, KV cache **on**, maximum 512 new tokens.
- E005: **440/747 (58.90%)**; answer extraction **98.8%**, mean generated tokens **96.10**, token-cap responses **9/747**.
- Predictions: `data/eval_runs/e005_grpo_val747_v1/full_validation/predictions.jsonl`; SHA256 `36bd0fce55f400127dd31e961259dde658f58cb45524c3e035bb013c833248d0`.
- Summary: `data/eval_runs/e005_grpo_val747_v1/full_validation/summary.json`. The evaluation matched the historical 747 source indices, prompts, answers, and frozen protocol.

| Protocol-matched checkpoint | Correct / 747 | Accuracy |
|---|---:|---:|
| E001 cached pretrained | 419 | 56.09% |
| E002a native-EOS SFT | 433 | 57.97% |
| E003 / E003b DPO | 433 / 433 | 57.97% / 57.97% |
| E004 DPO | 439 | 58.77% |
| **E005 GRPO** | **440** | **58.90%** |

The historical uncached **E002 original SFT** score of 318/747 belongs to a *different inference protocol* and is not part of this protocol-matched table.

### Paired significance and error analysis

| GRPO comparison | Both correct | GRPO wins | GRPO losses | Both wrong | Exact two-sided McNemar p |
|---|---:|---:|---:|---:|---:|
| vs. E002a SFT | 423 | 17 | 10 | 297 | 0.24778856 |
| vs. E004 DPO | 429 | 11 | 10 | 297 | 1.00000000 |

Neither difference is statistically significant at alpha 0.05. Across SFT/DPO/GRPO, **423** questions were correct for all three, **294** were incorrect for all three, and **11** were uniquely correct for GRPO. The inspected 11 GRPO-only successes involved percentage arithmetic, units, tracking quantities, and groupings; two correct final answers had incomplete or inconsistent intermediate explanations. The 10 regressions relative to DPO included arithmetic errors, omitted quantities, answering for the wrong variable, and one repetition/token-cap failure. Those selected examples are qualitative diagnostics, not causal proof of skill-level changes.

### Interpretation and reproducibility

E005 has the highest observed development accuracy of this set of experiments, **but not a statistically established advantage over SFT or DPO**. The common development split was used repeatedly to guide experiments, so these findings are exploratory. Final-answer reward alone does not establish process-level reasoning correctness. No official GSM8K test evaluation was performed.

- Frozen research report (complete hashes and comparisons): `protocols/e005_grpo_preparation_v1/e005_grpo_dev747_results_v1.md`.
- Result-report freeze commit: `bd99b01a9f48a8e4587958a90f70f407fc9af164`.
- **Decision:** Close E005 as the completed phase-1 GRPO experiment. Any future process-aware reward/E006 study would be a separately designed experiment; none is claimed here.
