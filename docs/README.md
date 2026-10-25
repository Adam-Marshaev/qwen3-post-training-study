# Documentation Index

<!-- portfolio_navigation_v1 -->

## Documentation and repository navigation

**Project status:** E001–E005 are complete. The phase-1 research
results are frozen. The original GSM8K official test partition
was not evaluated.

### Recommended reading order

| Start here | What it explains |
|---|---|
| [Project overview](../README.md) | Research questions, experimental lineage, and headline results |
| [Reproducibility guide](reproducibility.md) | Environment, datasets, artifacts, and reproduction requirements |
| [Experiment registry](experiments.md) | E001–E005 configurations, results, and provenance |
| [E005 research results](../protocols/e005_grpo_preparation_v1/e005_grpo_dev747_results_v1.md) | Detailed GRPO evaluation and paired statistics |
| [Development log](project_log.md) | Chronological engineering decisions, debugging, and milestones |

### Where the code lives

| Directory | Role |
|---|---|
| [`src/llm_post_training/`](../src/llm_post_training/) | Reusable Python library: data loading, SFT utilities, answer extraction, metrics, and GRPO reward |
| [`scripts/`](../scripts/) | Training, evaluation, generation, auditing, and diagnostic entry points |
| [`protocols/`](../protocols/) | Frozen, experiment-specific procedures, runners, configurations, reviews, and result records |
| [`configs/`](../configs/) | Versioned dataset splits, preference decisions, and training configurations |
| [`tests/`](../tests/) | Automated tests for the reusable library and experimental tooling |
| [`docker/`](../docker/) | Historical container environments |
| `data/` | Local datasets, checkpoints, and run outputs; excluded from Git |

### Why some Python scripts are outside src/

The `src/` directory contains reusable components.

The `scripts/` directory contains command-line entry points and
historical experiment utilities. Some later experiment-specific
runners live beside their frozen configurations in `protocols/`.

For example:

- Reusable reward logic:
  `src/llm_post_training/training/grpo_reward.py`
- General GSM8K evaluator:
  `scripts/evaluate_gsm8k.py`
- E005-specific evaluator:
  `scripts/evaluate_e005_grpo_gsm8k_v1.py`
- Frozen E005 training runner:
  `protocols/e005_grpo_preparation_v1/train_e005_grpo_v1.py`

This organization preserves the original implementations and paths
referenced by experiment records, source revisions, and hashes.

Moving historical scripts merely for appearance would complicate
the reproducibility of past experiments.

### Why docs contains many E003 files

The E003 documents record preference-generation reviews, arithmetic
and reasoning audits, adjudications, tokenizer checks, and debugging.

They are **supporting research evidence**, not required reading for
a first-time visitor.

For the main research narrative, begin with
[experiments.md](experiments.md). Consult the detailed E003 records
only when investigating how a particular preference dataset or
training decision was produced.

---


Project: Small Language Model Post-Training Laboratory

This index organizes the existing project documentation.
Historical audit records are retained for reproducibility.

## Core Project Records

- [experiments.md](experiments.md)
- [project_log.md](project_log.md)

## E003 Methodology and Release Documentation

- [e003_dpo109_staging_v1.md](e003_dpo109_staging_v1.md)
- [e003_dpo_tokenizer_preflight_v1.md](e003_dpo_tokenizer_preflight_v1.md)
- [e003_intermediate_generation_v1.md](e003_intermediate_generation_v1.md)
- [e003_preference_design_v1.md](e003_preference_design_v1.md)

## E003 Batch Reasoning Audits

- [e003_batch00_reasoning_audit_advisory_v1.md](e003_batch00_reasoning_audit_advisory_v1.md)
- [e003_batch01_reasoning_audit_advisory_v1.md](e003_batch01_reasoning_audit_advisory_v1.md)
- [e003_batch02_reasoning_audit_advisory_v1.md](e003_batch02_reasoning_audit_advisory_v1.md)
- [e003_batch03_reasoning_audit_advisory_v1.md](e003_batch03_reasoning_audit_advisory_v1.md)
- [e003_batch04_reasoning_audit_advisory_v1.md](e003_batch04_reasoning_audit_advisory_v1.md)
- [e003_batch05_reasoning_audit_advisory_v1.md](e003_batch05_reasoning_audit_advisory_v1.md)
- [e003_batch06_reasoning_audit_advisory_v1.md](e003_batch06_reasoning_audit_advisory_v1.md)

## E003 Historical Reviews and Pilot Studies

- [e003_batches03_06_advisory_release_summary_v1.json](e003_batches03_06_advisory_release_summary_v1.json)
- [e003_candidate124_dataset_preview_v1.md](e003_candidate124_dataset_preview_v1.md)
- [e003_candidate124_second_pass_review_v1.md](e003_candidate124_second_pass_review_v1.md)
- [e003_pilot_reasoning_screen_v1.md](e003_pilot_reasoning_screen_v1.md)
- [e003_provisional_pair_builder_v1.md](e003_provisional_pair_builder_v1.md)
- [e003_reference_erratum_regrade_v1.md](e003_reference_erratum_regrade_v1.md)
- [e003_remaining_review122_v1.md](e003_remaining_review122_v1.md)
- [e003_scale256_independent_adjudication3_v1.md](e003_scale256_independent_adjudication3_v1.md)
- [e003_scale256_reasoning_audit24_advisory_v1.md](e003_scale256_reasoning_audit24_advisory_v1.md)

## E003 Training and Evaluation Logs

These files are runtime artifacts and must not be deleted
or moved without a separate provenance review.

- `data/train_runs/e003_dpo_signed109_f16e903_v1.launch.log`
- `data/eval_runs/e003_dpo_signed109_cached_val747_v1.log`
- `data/eval_runs/e003_dpo_signed109_cached_val747_v1_retry1.log`

## Repository Rules

- Preserve experiment histories and original audit decisions.
- Do not relocate referenced documents without updating consumers.
- Keep historical failures and their logs.
- Do not modify active experiment dependencies.
- Keep the official GSM8K test partition separate.
