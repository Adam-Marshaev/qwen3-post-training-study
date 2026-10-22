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

No controlled benchmark or post-training experiment has been
completed yet.

The initial Qwen3 inference tests were engineering smoke tests,
not statistical evaluations.

The first planned experiment is:

E001 - Pretrained Qwen3 Mathematical Reasoning Baseline

Status: Planned

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
