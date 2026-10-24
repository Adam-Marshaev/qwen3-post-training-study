# E004-P1 to E004-P2 — Filtering Protocol Transfer v1

## Frozen P1 evidence

- E004-P1 used 250 GSM8K TRAIN source questions.
- Generation used four E002a samples per question.
- The original 1,000 responses are not modified.
- Exactly 135 source groups had mixed eligible outcomes.
- Exactly 91 groups passed the frozen mechanical pair screen.
- The arithmetic-first advisory review retained 83 provisional pairs.
- No pair is independently approved for DPO training.
- The official GSM8K test split was not used.

The complete 12-file review package is preserved at:
`protocols/e004_p1_arithmetic_first_v1/`

Its manifest independently records the SHA256 of every member.

## Portable policy

Retain the existing response eligibility, arithmetic-expression,
terminal-answer, token-length, and deterministic pair-selection checks.

Allow minor grammar, wording, and unit-label defects when the underlying
mathematical operations establish the intended numeric answer.

Reject substantively wrong arithmetic or quantity relationships,
coincidental correct answers, and material question ambiguity.

Do not rewrite or repair candidate responses.

## Important transfer limitation

The P1 reclassification script contains source-index-specific exclusions
and depends on previous assistant advisory reviews.

Those exclusions are historical P1 evidence, NOT an automatic semantic
validator and NOT a rule to apply to unseen P2 source questions.

The bundled mechanical screen also contains P1-specific source counts
and input hashes. A separate, versioned P2 wrapper is required before
using the portable checks with new data.

Do not silently modify the frozen P1 implementation.

## P2 generation gate

Before GPU generation:

1. Confirm clean Git revision and immutable Docker image.
2. Freeze a new P2 configuration and source-selection seed.
3. Select 250 new GSM8K TRAIN questions disjoint from the 538
   previously sampled pilot/E003/E004-P1 source questions.
4. Retain four E002a samples per question and existing EOS settings.
5. Run structural tests and a preflight before generation.

After generation, use the portable mechanical criteria and the
arithmetic-first review policy. Sample 30 provisional accepts and
10 rejects from the fresh batch for quality control.

Track material mathematical defects separately from tolerated wording
defects. Report all acceptance rates as provisional until audited.

Do not use validation item-level outcomes for source selection.
Do not use the official GSM8K test split.

No DPO or GRPO training is authorized by this protocol.
