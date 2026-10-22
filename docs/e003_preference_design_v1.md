# E003 Preference Dataset — Initial Design and Pilot

## Fixed reference policy

- Base: `Qwen/Qwen3-0.6B-Base`, revision `57ca99e94acb83175495aa2c6b6b0cc498170924`.
- Starting LoRA: E002a epoch-2 adapter, SHA256 `f56bb5b7129de7ef4ba0b76cc3c6890136fe34270e410224493a051bb192c625`.
- E003 and E004 will start from the same frozen E002a checkpoint.

## Frozen validation baseline

Under `gsm8k_val512_greedy_eager_cached_v1`: E001 419/747 (56.09%); E002a 433/747 (57.97%); difference +14/747 (+1.874 percentage points). McNemar exact two-sided p=0.362761; paired bootstrap 95% CI [-2.01, +5.62] percentage points. This does **not** establish a statistically significant accuracy improvement. E002 historical uncached 318/747 (42.57%) is retained as a negative control, not a matched cached result.

## Data boundary

- Use only the frozen 6,726-example GSM8K **training** partition for preference-data creation and DPO optimization.
- Do not use the 747-example development validation split to construct candidates, preference labels, or rewards.
- Official GSM8K test remains untouched.

## Bounded pilot

- 32 deterministic training questions, 4 sampled responses per question (128 candidates maximum).
- Seed 42, temperature 0.8, top-p 0.95, max 256 new tokens, eager attention, cached sampling.
- Use native EOS `151643` for generation and pad handling; tokenizer EOS `151645` must **not** be used as the target.
- No stop strings. Prefer actual native-EOS-complete responses.
- Store all raw candidates with token IDs, numerical extraction, correctness, termination reason and provenance.
- A candidate is *eligible* only with native EOS, no cap, valid extraction, no unwanted continuation, and an explicit final-answer marker.
- An initial pairable question must have at least one eligible correct and one eligible incorrect response.
- **Do not train DPO or freeze a full preference dataset based on the pilot alone.** Inspect pair yield, failures, lengths and potential answer-format artifacts first.

## Next controls before a full preference-data run

- Choose fixed candidate budget from observed pilot pair yield and compute cost.
- Version, test and freeze the pair-selection algorithm, including length disparity limits and duplicate removal.
- Save complete sampled candidate provenance and freeze chosen/rejected pairs before DPO training.
- Ensure native EOS has loss/log-prob supervision even though PAD and EOS share ID `151643` (mask by attention/label positions, never by ID).
- DPO should initialize a new trainable policy from E002a and use a frozen E002a reference policy, with a separately audited DPO loss.
- Keep all inference and generation with `use_cache=True`; disable caching for gradient-bearing training forwards.
