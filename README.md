# Small Language Model Post-Training

**A controlled comparison of supervised fine-tuning (SFT), Direct Preference Optimization (DPO), and Group Relative Policy Optimization (GRPO) for mathematical reasoning.**

Built and evaluated LoRA post-training workflows for **Qwen3-0.6B-Base**, using a pinned Docker/PyTorch environment on an NVIDIA Tesla V100 (32 GB). The project emphasizes end-to-end implementation, frozen evaluation settings, checkpoint provenance, paired statistics, and failure analysis—not benchmark optimization alone.

> **Main finding:** GRPO attained the highest observed GSM8K development accuracy (**440/747; 58.90%**), compared with **433/747 (57.97%)** for the final SFT checkpoint and **439/747 (58.77%)** for the later DPO experiment. Neither paired GRPO comparison was statistically significant.

## Results at a glance

| Experiment | Training or evaluation method | Correct / 747 | Accuracy | Evaluation context |
|:--|:--|--:|--:|:--|
| E001 | Pretrained Qwen3-0.6B-Base | 419 | 56.09% | Cached v1 baseline |
| E002 | Initial LoRA SFT | 318 | 42.57% | **Historical uncached** evaluation; not fully protocol-matched |
| E002a | Corrected native-EOS LoRA SFT | 433 | 57.97% | Cached v1; downstream initialization |
| E003 | DPO on 109 signed preference pairs | 433 | 57.97% | Cached v1 |
| E003b | DPO learning-rate ablation | 433 | 57.97% | Cached v1 |
| E004 | DPO on 586 autoscreened, provisional pairs | 439 | 58.77% | Cached v1 |
| **E005** | **GRPO, 256 optimizer updates** | **440** | **58.90%** | **Cached v1** |

**How to interpret the table:** The E001 cached baseline and E002a/E003/E003b/E004/E005 results follow `gsm8k_val512_greedy_eager_cached_v1`. E002's original 318/747 measurement predates the cached protocol and is shown as an engineering failure, not as a strictly controlled head-to-head comparison. An earlier historical E001 run measured **420/747** without caching; it is not used as the main baseline.

### Paired comparisons on the same 747 questions

| Comparison | GRPO gains | GRPO regressions | Net gain | Exact two-sided McNemar p |
|:--|--:|--:|--:|--:|
| E005 vs. E002a SFT | 17 | 10 | +7 | 0.2478 |
| E005 vs. E004 DPO | 11 | 10 | +1 | 1.0000 |

**None of these comparisons establishes a statistically significant performance improvement at α = 0.05.** E001-to-E002a was also not significant in the original paired analysis (p ≈ 0.363). The numbers are descriptive development-set measurements, not independent official-test results.

## Research design

**Model and training:** Qwen3-0.6B-Base at frozen Hugging Face revision `57ca99e94acb83175495aa2c6b6b0cc498170924`; LoRA on attention projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`), rank 8 and alpha 16. Training uses FP16 base weights and FP32 trainable LoRA parameters on a Tesla V100-SXM2-32GB. Implementations use PyTorch, Transformers, PEFT, and TRL.

**Data:** The original GSM8K training partition (7,473 questions with worked reference solutions) was divided into **6,726 training** and **747 held-out development** questions by a frozen, duplicate-audited manifest at [`configs/data/gsm8k_split_v1.json`](configs/data/gsm8k_split_v1.json). Reference solutions supplied supervision for SFT; later methods used the permitted training partition. The **official GSM8K test partition was not evaluated**.

**Frozen evaluation:** Same held-out questions, `gsm8k_qa_v1` prompt, answer extraction (`explicit_numeric_v2`), greedy decoding, FP16/eager attention, native EOS/PAD ID 151643, KV cache on, and a **512-new-token limit** for protocol-matched evaluations. Original and experiment-specific evaluators also validate checkpoint provenance.

**Experimental lineage:** E003, E003b, E004, and E005 were separately initialized from the verified **E002a SFT checkpoint**; the E005 GRPO policy was **not** initialized from E004 DPO.

## Experiment sequence

### E001: Pretrained baseline

Established inference, answer extraction, reproducible data loading, and a development benchmark before post-training. The comparable cached baseline scored **419/747 (56.09%)**.

### E002 / E002a: Supervised fine-tuning and EOS correction

SFT learned from GSM8K worked solutions using completion-only supervision. The initial E002 experiment exhibited degraded stopping behavior; correcting supervision to the model's native EOS token in E002a yielded **433/747 (57.97%)** under the frozen cached protocol. This became the starting point for the DPO and GRPO branches.

### E003 / E003b: DPO controlled experiments

Constructed signed preference pairs from sampled training-question completions and trained LoRA DPO on **109 reviewed pairs**. A fivefold learning-rate ablation produced larger policy updates but no aggregate development-accuracy gain: both variants scored **433/747**.

### E004: Larger provisional DPO preference dataset

Expanded the preference dataset to **586 source-unique, mechanically screened provisional pairs** (not independently certified as valid reasoning). The DPO model scored **439/747 (58.77%)**. Relative to E002a, it corrected nine questions and regressed on three; the paired difference was not significant (**p ≈ 0.146**). Pair count and curation procedure changed together, so this is not an isolated data-size ablation.

### E005: GRPO from E002a

Completed **256 optimizer steps** with **four sampled completions per group** and a numerical-final-answer correctness reward. Training produced **1,024 sampled completions**. The model scored **440/747 (58.90%)** on the same development questions. Its paired advantage over DPO was **11 corrections versus 10 regressions**; there was no significant difference.

See the [frozen E005 research record](protocols/e005_grpo_preparation_v1/e005_grpo_dev747_results_v1.md) for hashes, provenance, and the exact statistical comparison.

## What the error analysis showed

Question-by-question inspection identified genuine GRPO corrections to percentage calculations, quantity accounting, unit conversions, and arithmetic grouping. It also identified regressions involving incorrect intermediate arithmetic, omitted quantities, answer-target mismatches, and a repetition loop. Some correct final answers had incomplete or internally inconsistent written steps.

**Takeaway:** Answer-only GRPO rewards can change which problems a model solves, but these experiments do not demonstrate uniformly more reliable intermediate reasoning. This is a research observation, not proof of a causal reward-design mechanism.

## Repository map

| Path | Contents |
|:--|:--|
| [`configs/`](configs/) | Frozen data splits and training/evaluation configurations |
| [`src/`](src/) | Reusable data, training, prompting, and evaluation code |
| [`scripts/`](scripts/) | Evaluation and training entry points |
| [`protocols/`](protocols/) | Versioned experiment instructions, approvals, and frozen result records |
| [`tests/`](tests/) | Unit and integration tests |
| [`docs/experiments.md`](docs/experiments.md) | Chronological experiment registry and measured results |
| [`docs/project_log.md`](docs/project_log.md) | Engineering and debugging timeline |
| [`docs/README.md`](docs/README.md) | Existing technical documentation |
| [`Dockerfile`](Dockerfile) | Container environment |

**Start reading:** [Experiment registry](docs/experiments.md) → [Project development log](docs/project_log.md) → [E005 result record](protocols/e005_grpo_preparation_v1/e005_grpo_dev747_results_v1.md).

## Reproducibility and scope

Key experiments record exact model and dataset revisions, source commits, Docker image identities, training configurations, adapter and prediction SHA256 hashes, and the frozen evaluation protocol. See the experiment-specific protocols for execution instructions and prerequisites. Large model checkpoints and raw datasets are maintained as local artifacts and are **not guaranteed to be included in a public repository clone**.

### Limitations

- All reported scores use a **development split derived from GSM8K training data**, not the official test partition.
- Multiple rounds of experiment design used the same development set; the results are **exploratory**, not an untouched confirmatory assessment.
- Accuracy changes are small and the tested paired GRPO differences are **not statistically significant**.
- Exact final-answer correctness does not validate every intermediate mathematical step; the automatically screened E004 preference pairs were provisional.
- The results describe one model, dataset, and compute budget and do not establish a general ordering of SFT, DPO, and GRPO.

**Potential next phase:** Evaluate carefully checked arithmetic/process-consistency rewards using GSM8K's worked solutions, while preserving a separate untouched final assessment. No E006 experiment is reported as completed.
