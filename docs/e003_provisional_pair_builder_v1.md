# E003 Pilot Pair Builder v1

Status: **provisional extraction pipeline**, not an approved DPO dataset.

The builder reads the existing `e003_pilot32_k4_v1` immutable candidate data and
`e003_pilot_reasoning_screen_v1.json` advisory decisions. It does not generate
new model outputs, train, or touch the GSM8K test split. It validates every
candidate against the frozen GSM8K training split, recomputes answer grading,
compares stored generated token IDs to their tokenizer-decoded text, and refuses
incorrect or unterminated approved pairs. The exact generated token IDs are
retained; in particular, EOS 151643 is not reconstructed from the tokenizer's
EOS setting of 151645.

The selection manifest currently marks 18 groups `PROVISIONAL_APPROVE`, one
`HOLD`, and two `EXCLUDE`. This builder respects those decisions and emits
exactly one chosen/rejected pair from each provisionally approved group.

Output directory (must not exist):

- `pairs.jsonl`: 18 sorted pairs with unedited chosen/rejected response text,
  exact prompt IDs, exact original completion IDs (including final 151643),
  combined sequence IDs, source/sample identities, and explicit
  `training_approved: false`.
- `manifest.json`: hashes of all input and output artifacts, provenance,
  counts, termination protocol, and explicit `independent_human_signoff: false`.

**Do not use the 18 pairs for DPO model optimization.** They are an end-to-end
pipeline test and require independent review and a new versioned approval
manifest before training can start. Moreover, 18 pairs are not a useful
production DPO dataset.

## Reproducibility rules

- Source questions must belong to the frozen 6,726-question training partition;
  the held-out 747 validation questions are excluded and untouched.
- No source artifact is overwritten. Outputs must be created in a new directory.
- Frozen E002a adapter checksum and original candidate-generation provenance
  are checked before writing any outputs.
- KV caching was enabled during original generation. The builder is CPU-only,
  loads only the tokenizer and evaluation modules, and performs no inference.
- For any future DPO implementation, prompt tokens must be loss-masked;
  genuine EOS 151643 must remain scored although PAD also uses 151643;
  padding must be distinguished by attention mask, not equality to EOS ID.
- Human/independent adjudication and training-dataset approval require separate
  explicit artifacts. This builder cannot authorize training.
