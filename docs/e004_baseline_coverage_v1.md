# E004-P1 baseline-error coverage — inference-only diagnostic

Run frozen **E002a epoch-2** on all 250 training questions sampled in E004-P1, using the established E002a **greedy 512-token** evaluation protocol. Classify these questions into the 135 with both correct and incorrect E004 sampled completions and the remaining 115. Report a 2-by-2 contingency table, error rates, and count of mixed-group baseline errors. Outputs are *training-partition diagnostics*; do not report them as held-out accuracy or generalization results.

## Inputs pinned

- GSM8K frozen training source: `data/raw/gsm8k/train.jsonl`, SHA256 `17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465`
- Frozen split manifest SHA256 `31030317d85b015263d05383bf69bb02daec5bc67874f5ad0e0b33fa5294c719`
- E004 source candidate JSONL SHA256 `314626f08e0ac24c84efe9c6c2a1aae1a60018f74856613942bf84eb92eda628`
- E004 generation commit `fc6d48475f018c1a26d98d81694c8b6fbc31b815`
- E004 config SHA256 `3bf70dedbb024536d715b08d8ee5e28b8f07e2d3c07166fcd25d5272f458a1d6`
- E002a adapter weights SHA256 `f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`
- Docker image ID `sha256:e6248de1867ccb6aae297a49228532721014f16888b126b8532705e0d9e8ee0e`

## Decoding and output

Use `scripts.evaluate_gsm8k.verify_adapter_checkpoint` and `cached_generation_kwargs` from the frozen E002a evaluation code. Greedy, 512 tokens, FP16, eager attention, KV cache enabled, native EOS=151643, stop strings `\nQuestion:` and `\n[Question]`, same `format_baseline_prompt` and answer extractor. Disable native Triton override on V100. Network disabled; load pinned model and tokenizer from HF cache.

- Read-only preflight must not create output directory.
- Two-question inference smoke run `--stop-after-new 2` creates durable, immutable per-source checkpoints; no final output.
- Resume from validated checkpoints with `--resume` to 250; no regeneration of existing checkpoints.
- Outputs `metadata.json`, `progress/source_XXXXX.json`, `predictions.jsonl`, `coverage.jsonl`, `summary.json`, with summary written last.
- Every input source index must belong to the **training split**. The **validation and official test partitions must not be loaded**.

**No training, pair selection, pair approval, DPO, or GRPO occurs.**

## Interpretation

Mixed-selection enriches for non-deterministic failures, not necessarily for failures under greedy decoding. In-sample training performance is not a valid replacement for held-out GSM8K validation performance. Reporting must separate baseline accuracy of mixed vs nonmixed questions, count of baseline-error questions among mixed groups, and the fraction of all 250 baseline errors located in mixed groups.
