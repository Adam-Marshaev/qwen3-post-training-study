# E004-P2 arithmetic-first review — reproducible advisory package

The package contains the original uploaded compact input (137 mixed source groups), a **byte-exact narrow fork** of the frozen E004-P1 arithmetic mechanical screen, and an assistant advisory arithmetic-first review. The review is **not** a signed training dataset, general semantic verifier, or permission to train.

## Contents

- `inputs/mixed137.jsonl`: uploaded source-group input, exact SHA256 `fe4c4f034417b73be7862975889e102882be6d9f67352d62b9a568eaeb66faf9`.
- `references/strict_equation_screen_reference_v1.py`: unchanged E004-P1 mechanical screen reference, SHA256 `dbf7ba5a335748c799998975f812b2a33bf1d11709607207c5f9f825232b7df5`.
- `scripts/p2_screen_v1.py`: P2-specific mechanical screen with only version/count/SHA updates, SHA256 `d42011b8e9f89d28f4ab556429dd3041f5a96fca76f102167600281e10107a0e`.
- `scripts/review_p2_arithmetic_first_v1.py`: source-level assistant review annotations, deterministic pair classification, and QC sampling.
- `tests/test_e004_p2_arithmetic_first_v1.py`: 10 structural tests, including byte-for-byte screen derivation, pair validity, QC reproducibility, and refusal of tampered input.
- `outputs/review/`: decisions, mechanical decisions, summary, source-level report, 30 accepted QC worksheet, 10 rejected QC worksheet.
- `manifest.json`: SHA256 of every package member except itself.

## Replay commands (CPU only)

From the directory above `e004_p2_arithmetic_first_v1`:

```bash
ROOT=e004_p2_arithmetic_first_v1
python3 -m unittest discover -s "$ROOT/tests" -v
python3 "$ROOT/scripts/review_p2_arithmetic_first_v1.py" \
  --input "$ROOT/inputs/mixed137.jsonl" \
  --output-dir "$ROOT/outputs/review"
```

Replay is deterministic. Any preexisting output must match **byte-for-byte** or execution aborts rather than overwriting it. `manifest.json` pins the archival bytes. The source-specific seven manual holds are P2 evidence only, not automatic rules for unseen items.

## Decision meaning

- `PROVISIONAL_ACCEPT_QC_REQUIRED`: mechanically qualifying selected pair; no material issue spotted in assistant review; independently unverified.
- `REJECT_MATH_OR_MATERIAL_RELATION`: mechanical pass, but the selected response contains material reasoning or source-ambiguity concern.
- `REJECT_MECHANICAL`: no selected pair passed the pinned mechanical gate. It does *not* mean all responses in the group are mathematically wrong.

Not a substitute for independent QA. **Approved for training: 0.** No changes to the frozen GPU P2 run.
