# Reproducibility Guide

## Purpose

This guide describes the recorded environment, frozen data split,
evaluation protocol, and artifacts for the E001-E005 experiments.

It distinguishes inspection of a public source-code clone from
reproducing training and evaluation with external data and weights.

## Model and Hardware

- Base model: Qwen/Qwen3-0.6B-Base
- Model revision:
  57ca99e94acb83175495aa2c6b6b0cc498170924
- GPU used: NVIDIA Tesla V100-SXM2, 32 GB
- Base model precision: FP16
- Trainable LoRA precision: FP32
- Attention implementation: eager
- LoRA rank: 8
- LoRA alpha: 16
- LoRA target modules: q_proj, k_proj, v_proj, o_proj

The historical GPU training/evaluation runtime used Docker image ID:

sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e

Recorded package versions include PyTorch 2.14.0+cu126,
Transformers 4.57.6, TRL 0.26.2, and PEFT 0.18.1.

Inspect Dockerfile, docker/, and pyproject.toml for the
available local environment definitions.

A pinned historical image identity records the executed environment;
it does not guarantee that a fresh Docker build reproduces identical
binary dependencies.

## Dataset

Dataset: GSM8K (OpenAI grade-school-math).

Recorded source revision:
3101c7d5072418e28b9008a6636bde82a006892c

Original GSM8K training records: 7,473.

The frozen split contains:

- Development-training examples: 6,726
- Development-validation examples: 747
- Split definition: configs/data/gsm8k_split_v1.json

Frozen split SHA256:
31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719

Original source training JSONL SHA256:
17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465

The official GSM8K test partition was not evaluated.

## Evaluation Protocol

Identifier: gsm8k_val512_greedy_eager_cached_v1

- Same 747 frozen development examples
- Prompt version: gsm8k_qa_v1
- Answer extraction: explicit_numeric_v2
- Greedy generation
- Maximum 512 new tokens
- KV caching enabled
- FP16 base and eager attention
- Native EOS/PAD token ID: 151643

Use the versioned evaluators in scripts/ and their recorded
CLI contracts. Do not assume that a smoke-test mode constitutes
a formal protocol-matched evaluation.

The initial E002 evaluation used an older uncached protocol;
its 318/747 result is retained as a historical engineering
observation rather than a strictly protocol-matched comparison.

## Experimental Lineage

E001 evaluates the pretrained model.

E002 and E002a are SFT experiments.

E003 and E003b evaluate DPO using 109 signed preference pairs,
including a controlled learning-rate variation.

E004 evaluates DPO on 586 provisional, automatically screened
preference pairs.

E005 evaluates GRPO with a bounded 256-step training run,
four sampled completions per group, and numerical
final-answer correctness reward.

E003, E003b, E004, and E005 were separately initialized from
the final E002a native-EOS SFT checkpoint, not from one another.

## Verified Development Results

- E001 cached pretrained: 419/747 (56.09%)
- E002a SFT: 433/747 (57.97%)
- E003 DPO: 433/747 (57.97%)
- E003b DPO: 433/747 (57.97%)
- E004 DPO: 439/747 (58.77%)
- E005 GRPO: 440/747 (58.90%)

E005 versus E002a: 17 wins, 10 losses,
exact two-sided McNemar p = 0.24778856.

E005 versus E004: 11 wins, 10 losses,
exact two-sided McNemar p = 1.0.

Neither comparison establishes statistically significant superiority.

## Key Reproducibility References

- docs/experiments.md
- docs/project_log.md
- protocols/e004_dpo_preparation_v1/e004_research_result_v1.json
- protocols/e005_grpo_preparation_v1/e005_grpo_training_plan_v1.json
- protocols/e005_grpo_preparation_v1/e005_grpo_dev747_results_v1.md
- protocols/e005_grpo_preparation_v1/train_e005_grpo_v1.py
- scripts/evaluate_gsm8k.py
- scripts/evaluate_e005_grpo_gsm8k_v1.py
- src/llm_post_training/training/grpo_reward.py

The E005 frozen results report records checkpoint and prediction
SHA256 hashes and the matched-question analysis.

## What a Public Clone Contains

Tracked source code, tests, versioned configurations,
research documentation, and selected review artifacts.

A public clone does not automatically contain:

- The original local GSM8K dataset copy
- Cached Qwen pretrained weights
- Saved trained LoRA adapters
- Local inference predictions and training traces
- The original historical Docker image, unless separately available

The data/ directory is ignored by Git.

<!-- verified_cpu_tests_2026_10_25_v1 -->

## Verified CPU Test Run — 2026-10-25

The existing automated test suite was executed successfully against
the E001-E005 repository using the historical Docker environment.

### Result

- **257 passed**
- **5 skipped**
- **0 failed**
- Test execution time: **3.38 seconds**
- pytest version: **8.4.2**
- Python version: **3.10.12**

The five skipped tests were not investigated individually during
this validation. The result therefore establishes that all
non-skipped tests passed, not that every possible test ran.

### Environment

Historical Docker image:

`sha256:07c6ab54329a0e930842c184979de941bba850c2e03daea8656a65848a7ee80e`

Verified packages:

| Package | Version |
|---|---|
| PyTorch | 2.14.0+cu126 |
| Transformers | 4.57.6 |
| PEFT | 0.18.1 |
| TRL | 0.26.2 |
| datasets | 4.0.0 |
| accelerate | 1.12.0 |
| safetensors | 0.8.0 |

The historical image did not contain pytest.

For validation, pytest 8.4.2 and its dependencies were downloaded
to a temporary wheel directory using a separate network-enabled
container without the project repository mounted.

The wheels were then installed into `/tmp/pytestdeps` inside a
disposable test container using an offline pip installation.

The test execution container used:

- Repository bind mount: read-only
- Network access: disabled
- GPU access: disabled
- Historical Docker image: unchanged
- Temporary pytest dependencies: not committed or added to the image
- Python import path: `/tmp/pytestdeps:/workspace/src:/workspace`
- Python bytecode writing: disabled
- pytest cache provider: disabled

The test command executed inside that environment was:

```bash
/usr/bin/python3 -m pytest -q -p no:cacheprovider tests/
```

### Installation and Reproduction Scope

`pyproject.toml` declares the project package and Python requirement,
but does not currently declare the full ML runtime dependency set.

The historically used versions are installed through the
versioned Docker environment definitions.

Consequently, `pip install -e .` alone is **not** a verified way
to reproduce the full experimental environment.

Reusing the exact historical Docker image requires that the image
already be available locally or be obtained from an appropriate
trusted source. A fresh Docker build has not been established to
produce an identical historical binary environment.

This validation checked the CPU-compatible test suite. It did
**not** rerun GPU training, regenerate model predictions, or verify
checkpoint reproduction from a fresh clone.

## Reproduction Levels

1. Source review: inspect code, configurations, and the recorded
   experimental results without a GPU.
2. Software validation: install compatible dependencies and run
   relevant tests from tests/, subject to their environment needs.
3. Model evaluation: acquire the pinned base model, frozen dataset,
   and a compatible adapter checkpoint; verify hashes, then use
   the appropriate evaluator and frozen protocol.
4. Full training reproduction: rebuild or obtain the appropriate
   runtime, recreate permitted training inputs, and execute the
   relevant versioned training protocol.

The repository does not claim that a fresh clone alone can recreate
the historical checkpoints or measured predictions automatically.

## Methodological Limitations

The same 747-question development partition informed multiple
rounds of experimental development. These evaluations are exploratory
and are not an independent final test of generalization.

The official GSM8K test partition remains unused.

A correct numeric final answer does not establish that all
intermediate written reasoning is correct.

No additional training or test-set evaluation is required to
inspect the completed E001-E005 research phase.
