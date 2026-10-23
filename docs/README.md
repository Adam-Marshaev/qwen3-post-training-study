# Documentation Index

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
