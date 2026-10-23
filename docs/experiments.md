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
- E003: Signed-109 DPO training completed; validation result pending.
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
**Validation status:** Full frozen 747-question evaluation launched;
result not yet recorded.

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
