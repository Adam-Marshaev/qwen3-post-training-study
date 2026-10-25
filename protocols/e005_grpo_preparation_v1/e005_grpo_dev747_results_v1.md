# E005 GRPO — Frozen Development Results

## Experiment identity

- Training experiment: E005 GRPO from frozen E002a
- Training commit: `ab42f55475fcc104261e380ef52dd143c50b66ca`
- Evaluation commit: `6dea3a6e60892ca76934c767e5dafb361d590564`
- Training budget: 256 optimizer steps
- Learning rate: `1e-6`
- Final GRPO adapter SHA256:
  `4246d1c0a2381be6fe50066d21c35390d69086f2975b4ef9e76b3bc658a1ae59`
- Frozen development partition: 747 questions
- Inference protocol: `gsm8k_val512_greedy_eager_cached_v1`
- Official GSM8K test partition: not evaluated

## Development accuracy

| Model | Correct | Accuracy |
|---|---:|---:|
| E002a SFT | 433/747 | 57.9652% |
| E004 DPO | 439/747 | 58.7684% |
| E005 GRPO | 440/747 | 58.9023% |

The threshold for at least 60% accuracy is 449/747.
E005 is nine correct answers below that threshold.

## Paired correctness comparisons

| Comparison | GRPO wins | GRPO losses | Net | Exact two-sided McNemar p |
|---|---:|---:|---:|---:|
| E005 vs E002a | 17 | 10 | +7 | 0.24778856 |
| E005 vs E004 | 11 | 10 | +1 | 1.00000000 |

Neither comparison is significant at alpha = 0.05.

## Three-model correctness patterns

Bit order: E002a / E004 / E005.
One means correct, zero means incorrect.

| Pattern | Questions |
|---|---:|
| `000` | 294 |
| `001` | 11 |
| `010` | 3 |
| `011` | 6 |
| `100` | 3 |
| `110` | 7 |
| `111` | 423 |

## Prediction provenance

| Model | Predictions SHA256 | Summary SHA256 |
|---|---|---|
| E002a | `b14a887d3942dcd0dec56abac1f4ea9ec748573d4a2d703dac1457e52df31b9c` | `f65b18e8f6dbfe4584af59db3d5791db478eec4e343705ec5ac7fbd2b6b64229` |
| E004 | `1ba7ad571cc662ffcfba621abc4791838a434e64c3e0c219b21a26b721452c97` | `b331b4386fc35c0b2b913b652efc5214d5da4745c7ba6e68fc63a093d005d427` |
| E005 | `36bd0fce55f400127dd31e961259dde658f58cb45524c3e035bb013c833248d0` | `688aa49c5d213556d6655be1ca11620b2080986805f2300d0c5c3fb944b86924` |

## Interpretation

E005 achieved the highest observed development accuracy,
but the differences against E002a and E004 are small and
not statistically significant.

Compared with SFT, GRPO corrected 17 previously incorrect
answers and regressed on 10 previously correct answers.

Compared with DPO, GRPO corrected 11 answers and regressed
on 10 answers.

The 294 questions missed by all three models are candidates
for qualitative error analysis.

The development partition has been used for repeated
experimental comparisons. These results are exploratory,
not independent confirmatory evidence of generalization.

No further training or official-test evaluation is implied
or authorized by this report.
