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
