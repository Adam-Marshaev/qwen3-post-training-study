# Project Development Log

Project: Small Language Model Post-Training Laboratory

Repository: llm-post-training-lab

Purpose:
Chronological record of implementation milestones, engineering
decisions, debugging, verification results, and next steps.

The repository is the authoritative record of project progress.

Historical entries should not be overwritten when decisions change.
Append new entries documenting updated evidence and decisions.

---

## 2026-10-21 - Initial Project Infrastructure and Baseline Inference

### Objective

Establish a reproducible development environment and validate
inference using the pretrained Qwen3-0.6B-Base model.

### Completed

Infrastructure:
- Created dedicated Docker development environment.
- Validated NVIDIA GPU passthrough.
- Validated PyTorch CUDA execution.
- Verified FP16 matrix multiplication.
- Configured Git repository and ignore rules.
- Established Python src/ package structure.
- Implemented runtime environment inspection.

Model infrastructure:
- Installed Transformers.
- Loaded Qwen3-0.6B-Base tokenizer.
- Verified tokenization round-trip.
- Loaded pretrained model weights.
- Inspected transformer architecture and parameter dimensions.
- Executed successful model forward pass.
- Implemented greedy autoregressive generation.
- Added custom generation stopping condition.

Evaluation infrastructure:
- Implemented numerical answer extraction.
- Added missing/ambiguous answer detection.
- Added unwanted-continuation detection.
- Implemented unit tests.

### Environment

OS: Ubuntu 22.04.5
GPU: NVIDIA Tesla V100-SXM2-32GB
Compute capability: 7.0
Driver: 580.178.04

Container:
- Python 3.10.12
- PyTorch 2.14.0+cu126
- CUDA runtime 12.6
- NumPy 1.26.4
- Transformers 4.57.6

Precision: FP16
Attention implementation: eager

### Model

Model: Qwen/Qwen3-0.6B-Base

Revision:
57ca99e94acb83175495aa2c6b6b0cc498170924

Measured architecture:
- Parameters: 596,049,920
- Transformer layers: 28
- Hidden dimension: 1024
- Query heads: 16
- Key/value heads: 8
- Head dimension: 128
- MLP intermediate dimension: 3072
- Vocabulary allocation: 151936

### Verified Results

FP16 parameter storage: 1136.88 MiB

GPU allocation after model loading: 1136.89 MiB

Peak allocated memory during inspected forward pass:
1167.27 MiB

Forward pass:
- Input shape: (1, 21)
- Logits shape: (1, 21, 151936)

Generation smoke test:
- Input tokens: 34
- Original generated tokens: 96
- Generated tokens with stopping condition: 58
- Reduction in generated tokens: approximately 39.6%

The model correctly answered the tested inventory problem:

240 - (240 * 0.35) + 48 = 204

This is a single example, not a benchmark accuracy result.

Automated tests:
- 10 tests passed.

### Problems Encountered

The initial Qwen3 forward pass failed during a Triton-backed
operation while initializing the Triton cache.

The traceback ended with a filesystem permission error.

Disabling PyTorch native Triton operator overrides allowed
the forward pass to complete.

A subsequent successful run confirmed that the workaround
worked without custom Triton cache environment variables.

### Engineering Decisions

- Keep the project independent of the previous vision project.
- Use Docker for reproducible GPU execution.
- Use FP16 rather than native BF16 on the V100.
- Use eager attention initially.
- Pin the pretrained model revision.
- Keep mathematical verification independent of the model.
- Separate mathematical correctness from output-format quality.
- Design future model loading to support larger checkpoints.

### Limitations

- No full dataset evaluation has been performed.
- No baseline accuracy has been measured.
- No model fine-tuning has been performed.
- Training stability has not been validated.
- Pretraining contamination remains an evaluation consideration.
- The integrated generation/evaluation script still requires
  end-to-end verification.

### Next Step

Validate integrated generation and answer evaluation.

Then implement reusable evaluation metrics and begin preparing
the mathematical reasoning datasets.

---

## 2026-10-21 - Integrated Mathematical Answer Evaluation

### Completed

Integrated the reusable numerical answer extractor into
the Qwen3 baseline generation script.

The end-to-end pipeline now performs:

1. Prompt tokenization
2. Pretrained Qwen3 inference
3. Greedy autoregressive generation
4. Numerical answer extraction
5. Comparison against independently defined ground truth
6. Reporting of correctness and unwanted continuation

### Configuration

Model: Qwen/Qwen3-0.6B-Base
Model revision: 57ca99e94acb83175495aa2c6b6b0cc498170924

Precision: FP16
Attention implementation: eager
Decoding: greedy
KV cache: disabled
Maximum new tokens: 96
Stop string: newline followed by "Question:"

### Verified Results

Test problem:
A warehouse starts with 240 components, ships 35%,
and receives 48 more.

Expected answer: 204
Extracted answer: 204
Extraction status: valid
Mathematically correct: True
Unwanted continuation: True

Input tokens: 34
Generated tokens: 58
Total tokens: 92
Peak PyTorch-allocated GPU memory: 1150.63 MiB

The integrated generation smoke test passed.

The existing 10 unit tests also passed.

### Observations

The pretrained model generated a mathematically correct
multi-step solution without task-specific fine-tuning.

The model continued into another question, but the custom
stopping condition terminated generation at the new
question marker.

The answer extractor correctly detected both the numerical
answer and the unwanted continuation.

### Limitations

These results represent one engineering smoke test,
not a statistical model evaluation.

The reference answer is currently hardcoded.

The answer extractor requires an explicit final-answer
declaration.

The script does not yet evaluate a dataset or aggregate
metrics across multiple examples.

### Decision

Keep mathematical correctness separate from format and
stopping-behavior metrics.

Do not record this smoke test as formal experiment E001.

### Next Step

Implement reusable evaluation metrics and unit tests.

Then prepare mathematical reasoning datasets and establish
a reproducible pretrained baseline evaluation.

---

## 2026-10-21 - Mathematical Evaluation Metrics

### Completed

Implemented reusable dataset-level evaluation metrics.

Added:
- Per-problem evaluation records
- Numerical correctness calculation
- Accuracy aggregation
- Valid extraction rate
- Missing and ambiguous answer rates
- Unwanted continuation rate
- Mean generated token count

### Engineering Decisions

Primary mathematical accuracy uses all evaluated problems
as the denominator, including extraction failures.

Numerical answers are compared using Decimal.

Model correctness is kept separate from response-format
and continuation behavior.

Empty evaluation sets raise an error rather than returning
misleading metrics.

### Validation

Verified metrics using synthetic examples with known results.

Expected synthetic accuracy: 40%
Expected synthetic extraction rate: 60%
Expected mean generated tokens: 30

Four new unit tests were added.

### Limitations

No real dataset-level model evaluation has been run yet.

The metrics currently operate on in-memory records.

Results are not yet automatically saved to JSON or JSONL.

### Next Step

Implement dataset loading and begin preparing GSM8K
and procedurally generated mathematical problems.

---

## 2026-10-21 - Evaluation Metrics Verified

### Completed

Implemented per-problem evaluation records and dataset-level
metrics aggregation.

Metrics:
- Mathematical accuracy
- Valid answer extraction rate
- Missing answer rate
- Ambiguous answer rate
- Unwanted continuation rate
- Mean generated token count

### Verification

All 14 automated tests passed.

A five-example synthetic evaluation produced:
- Accuracy: 40%
- Extraction rate: 60%
- Missing answer rate: 20%
- Ambiguous answer rate: 20%
- Mean generated tokens: 30

These are synthetic software-test results, not Qwen3
benchmark measurements.

### Engineering Decision

Primary accuracy includes every evaluated problem in its
denominator, including missing or ambiguous answers.

### Next Step

Inspect GSM8K and establish reproducible dataset splits
before the first pretrained baseline experiment.

---

## 2026-10-21 - GSM8K Reference Validation

### Completed

Downloaded the official GSM8K training split.

Implemented and tested a strict parser for GSM8K reference
answers using the #### final-answer marker.

Validated all training examples.

### Dataset Provenance

Dataset: openai/grade-school-math
Source commit:
3101c7d5072418e28b9008a6636bde82a006892c

Training file SHA-256:
17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465

Training examples: 7473

The raw dataset is excluded from Git.

### Validation Results

- Successfully parsed: 7473
- Parsing failures: 0
- Non-integral final answers: 0
- Negative final answers: 3
- Comma-formatted final answers: 79
- Automated tests: 21 passed

### Engineering Decisions

Keep the GSM8K reference-answer parser separate from the
model-generated answer extractor.

Require exactly one valid final-answer declaration in each
GSM8K reference solution.

Reject malformed references rather than silently dropping
or modifying examples.

Continue using Decimal for numerical representation.

### Limitations

Only the official training split has been downloaded.

No training/validation split has been created.

No full-dataset model evaluation has been conducted.

The official test split remains untouched.

### Next Step

Audit duplicate questions and create a deterministic,
leakage-aware training/validation split.

---

## 2026-10-21 - GSM8K Development Split

### Completed

Audited all 7473 official GSM8K training examples for
duplicate questions.

Implemented a deterministic, duplicate-aware development
training/validation split.

Created and validated:

configs/data/gsm8k_split_v1.json

### Duplicate Audit

Exact duplicate question groups: 0
Normalized duplicate question groups: 0
Conflicting answers among duplicate groups: 0

Normalization:
- Unicode-aware case folding
- Whitespace normalization

The audit does not establish the absence of semantic
duplicates or pretraining contamination.

### Source Dataset

Dataset: openai/grade-school-math

Source commit:
3101c7d5072418e28b9008a6636bde82a006892c

Training data SHA-256:
17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465

### Split Configuration

Split version: 1
Random seed: 42
Validation fraction: 0.10

Assignment method:
SHA-256 ranking grouped by normalized question.

Development training examples: 6726
Development validation examples: 747
Total examples: 7473

Overlapping indices: 0
Missing indices: 0

Manifest SHA-256:
31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719

### Verification

All 26 unit tests passed.

Manifest integrity verification passed:
- Correct split sizes
- No overlapping indices
- Complete coverage
- Correct source checksum

### Engineering Decisions

The v1 split manifest is frozen for future experiments.

SFT, DPO, and GRPO training must use the same
development-training partition.

Validation examples must not be used as training prompts,
preference-training examples, or GRPO training prompts.

The official GSM8K test split remains untouched.

Any future split changes require a new versioned manifest.

### Next Step

Implement manifest-aware dataset loading.

Then build the pretrained baseline evaluation runner
using the frozen development-validation split.

---

## 2026-10-21 - Manifest-Aware GSM8K Loader

### Completed

Implemented a dataset loader that retrieves GSM8K examples
according to the frozen development split manifest.

Implementation commit:
7abbde6

### Verification

Automated tests: 32 passed.

Real dataset verification:
- Development training examples: 6726
- Development validation examples: 747
- Overlapping indices: 0
- Total unique examples: 7473

Frozen split manifest SHA-256:
31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719

The loader verifies:
- Source dataset checksum
- Source revision
- Manifest version and counts
- Index validity and uniqueness
- Complete partition coverage
- No training/validation overlap
- No normalized-question leakage

### Observations

First validation example:
- Original source index: 6
- Subject: pizza slice arithmetic
- Reference numerical answer: 48

### Engineering Decisions

Keep the evaluation-facing example representation separate
from the full reference solution used for supervised training.

Preserve the frozen GSM8K split for all subsequent model
comparisons.

### Next Step

Implement and freeze a deterministic baseline prompt format.

Then build a multi-question inference runner and begin
small-scale validation smoke tests.

---

## 2026-10-21 - Baseline Prompt Verified

### Completed

Implemented the versioned GSM8K baseline prompt builder.

Prompt version: gsm8k_qa_v1

Template:
Question: {question}
Answer:

### Verification

All 38 automated tests passed.

Verified the prompt against the first frozen GSM8K
validation example:
- Source index: 6
- Topic: pizza slice arithmetic
- Reference answer: 48

The reference answer was not included in the model prompt.

### Engineering Decisions

Centralize evaluation prompt formatting.

Treat prompt version as part of experimental configuration.

Do not silently modify a frozen prompt version.
Create a new version for intentional prompt experiments.

### Next Step

Build a multi-question GPU inference smoke test
that saves individual predictions and aggregate metrics.

---

## 2026-10-21 - GSM8K Evaluation Smoke Test and Stopping Fix

### Completed

Implemented and executed the first five-example GSM8K
validation evaluation runner.

The runner saves:
- Individual model predictions as JSONL
- Per-example correctness and extraction status
- Generation token counts
- Aggregate metrics and configuration as JSON

### Original Smoke Test

Run: smoke_5_v1

Examples: 5
Correct: 4
Accuracy: 80%
Extraction rate: 80%
Mean generated tokens: 96.0

The original unwanted-continuation metric was unreliable.

The evaluator recognized Question: but did not recognize
the [Question] marker generated by Qwen3.

All five examples reached the 96-token generation limit.

### Corrected Smoke Test

Run: smoke_5_v2_stop

Examples: 5
Correct: 4
Accuracy: 80%
Extraction rate: 80%
Unwanted continuation rate: 80%
Mean generated tokens: 69.8

Total generated tokens:
- Original: 480
- Corrected: 349

Generated token reduction: approximately 27.3%.

All 39 automated tests passed.

### Engineering Decisions

Expanded continuation detection to recognize [Question].

Expanded generation stopping strings accordingly.

Added a regression test for the observed continuation format.

Preserved the original smoke-test results rather than
overwriting them.

### Limitations

Five examples are insufficient for benchmark conclusions.

No inference latency comparison has been conducted.

The stopping marker remains in the raw response.

One problem failed extraction after exhausting the
96-token generation limit.

### Next Step

Investigate the effect of increasing the generation budget
to 192 tokens while keeping other settings fixed.

---

## 2026-10-21 - GSM8K Generation Budget Investigation

### Objective

Investigate whether the 96-token generation limit caused
an incomplete solution in the initial GSM8K smoke test.

### Configuration

Model: Qwen/Qwen3-0.6B-Base
Prompt version: gsm8k_qa_v1
Decoding: greedy
KV cache: disabled
Precision: FP16

Same five validation examples and stopping strings.

Only the maximum generation budget changed.

### Results

96-token budget:
- Correct answers: 4/5
- Accuracy: 80%
- Mean generated tokens: 69.8
- Unwanted continuation rate: 80%

192-token budget:
- Correct answers: 5/5
- Accuracy: 100%
- Mean generated tokens: 85.2
- Unwanted continuation rate: 100%

Source index 44:
- 96-token result: incomplete, missing final answer
- 192-token result: correct numerical answer, 300
- Generated tokens: 96 -> 173

The other four examples produced unchanged token counts
and remained correct.

### Conclusion

The failure on source index 44 was sensitive to the
generation budget.

The 96-token limit truncated its solution before a final
answer was produced.

This does not establish that 192 tokens is sufficient
for the entire GSM8K validation set.

Five-example accuracy is not a benchmark estimate.

### Next Step

Make generation settings configurable and record them
in run metadata.

Investigate longer problems before freezing the full
baseline evaluation configuration.

---

## 2026-10-21 - Token-Cap Diagnostics Verified

### Completed

Extended the GSM8K evaluation framework to detect when
generation reaches its configured maximum token budget.

Added:
- Per-example reached_token_cap field
- Aggregate token-cap count
- Aggregate token-cap rate
- Regression test for correct answers reaching the cap

### Verification

Automated tests: 40 passed.

Test question:
GSM8K validation source index 6.

16-token configuration:
- Generated tokens: 16
- Reached token cap: True
- Extraction status: missing
- Correct: False

192-token configuration:
- Generated tokens: 63
- Reached token cap: False
- Extracted answer: 48
- Correct: True

Both GPU smoke tests passed.

Per-example diagnostics agreed with aggregate metrics.

### Engineering Decision

Reaching the generation cap is recorded separately
from mathematical correctness.

The field indicates possible truncation, not proof
that generation was interrupted mid-answer.

Primary accuracy continues to include all examples
in its denominator.

### Limitations

These were single-question engineering tests,
not benchmark accuracy measurements.

No representative GSM8K accuracy estimate exists yet.

### Next Step

Run a 20-question diagnostic evaluation to investigate
generation lengths, answer extraction, continuation
behavior, and token-cap frequency.

---
