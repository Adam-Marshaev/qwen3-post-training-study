# E003 Pilot: Reasoning Quality Screen

## Scope and interpretation

This is an **advisory** content review of the uploaded pilot text. It is not a frozen DPO pair-selection manifest, independent human adjudication, or formal proof of reasoning correctness. No candidate text was modified. The original pilot artifacts must remain immutable.

- Pilot: `e003_pilot32_k4_v1`; code revision `dd3a80247c92e57d5d01d8e8531778e861b5b2ad`.
- Uploaded report SHA-256: `2f81688e37c88392d8e31cd2bf845dd50ee301dbc8d834c46a9e574e87efb657`.
- Mixed groups screened: **21**; provisionally approvable: **18**; hold: **1**; exclude: **2**.
- Provisional pair length gap: median **14.5** tokens; maximum **64** tokens.

## Group-by-group decisions

| Source index | Status | Chosen sample | Rejected sample | Length gap | Finding |
|---:|---|---:|---:|---:|---|
| 234 | HOLD | — | — | — | Sample 0 has false coin-value statements; sample 1 calculates eight nickels but reverses who pays whom (and whose till). Review sample 1 manually before approval. |
| 250 | PROVISIONAL_APPROVE | 0 | 3 | 17 | Chosen accounts for all ten plates and 20% increase; rejected calculates one plate rather than all ten. |
| 280 | PROVISIONAL_APPROVE | 1 | 3 | 2 | Chosen multiplies each distinct card price by six; rejected charges both prices for twelve cards. |
| 801 | PROVISIONAL_APPROVE | 3 | 2 | 23 | Chosen deducts tax, tithe, and water; rejected omits the tax from its final subtraction. |
| 859 | PROVISIONAL_APPROVE | 2 | 3 | 28 | Chosen uses 300/50 packets per minute; rejected mishandles packets per minute. |
| 937 | PROVISIONAL_APPROVE | 3 | 2 | 21 | Chosen subtracts the discount from the price; rejected adds the original price after finding the discounted price. |
| 1268 | PROVISIONAL_APPROVE | 0 | 2 | 0 | Chosen counts all four people brushing three times per day; rejected double-counts the three daily brushings. |
| 1989 | PROVISIONAL_APPROVE | 3 | 0 | 2 | Chosen adds lemonade revenue and babysitting income, then subtracts profit; rejected incorrectly subtracts the babysitting revenue. |
| 2029 | PROVISIONAL_APPROVE | 1 | 3 | 4 | Chosen subtracts Jeremy and Stacy purchases from the total; rejected assumes Emily already bought four and produces inconsistent counts. |
| 2511 | PROVISIONAL_APPROVE | 1 | 0 | 14 | Chosen counts both six-year arson sentences and doubles their total; rejected ignores one arson count. |
| 3818 | PROVISIONAL_APPROVE | 0 | 1 | 1 | Chosen divides equally across four color groups then takes half the yellow balloons; rejected invents eight groups. |
| 3839 | PROVISIONAL_APPROVE | 3 | 2 | 8 | Chosen computes three nickels spent and two gum pieces per nickel; rejected confuses coins retained with coins spent. |
| 4596 | PROVISIONAL_APPROVE | 3 | 0 | 64 | Chosen includes homework, quiz, and test points in the equation; rejected omits the homework term. Note 64-token pair length gap. |
| 4958 | PROVISIONAL_APPROVE | 2 | 3 | 17 | Chosen subtracts rose count and divides remaining daisy count by ten bouquets; rejected stops at total daisy count instead of per-bouquet count. |
| 4961 | PROVISIONAL_APPROVE | 2 | 1 | 8 | Chosen correctly applies one-half, one-quarter, then one-fifth; rejected stops after the one-quarter calculation. |
| 5106 | EXCLUDE | — | — | — | Only correct-final-answer sample 3 says Grace is 35 inches tall; Grace is 40 inches tall and the height DIFFERENCE is 35. No clean chosen response. |
| 5371 | PROVISIONAL_APPROVE | 3 | 0 | 17 | Chosen counts Jane and James gifts and the additional apples to give away; rejected invents an incorrect accounting step. |
| 5471 | PROVISIONAL_APPROVE | 3 | 0 | 24 | Chosen correctly derives Diana's ten-minute duration and Hani's seven-per-minute rate; rejected mistakes minutes for rate. |
| 5807 | PROVISIONAL_APPROVE | 3 | 0 | 15 | Chosen counts one initial round plus ten Saturday rounds and fifteen Sunday rounds; rejected adds rounds to minutes. |
| 6378 | EXCLUDE | — | — | — | Only correct-final-answer sample 3 states 34/19=2, which is false; it also miscounts eligible teeth. Correct divisor after initial payment and two missing teeth is 17. |
| 6710 | PROVISIONAL_APPROVE | 1 | 3 | 12 | Chosen computes 300 charms, $4,500 costs, and $6,000 revenue; rejected arithmetic and profit accounting are incoherent. |

## Critical observations

- Source **234**: sample 0 has fabricated values for coins. Sample 1 computes the right result but reverses the payer/payee; **HOLD** pending policy adjudication. Sample 1 must not be silently auto-approved.
- Source **5106**: sample 3 is answer-correct but calls the *difference* in tower heights Grace’s actual tower height; **EXCLUDE** under strict semantic consistency.
- Source **6378**: sample 3 has the false equality `34/19=2` and mishandles the two missing teeth; **EXCLUDE**.
- Source **1989**: sample 1 calls combined revenue the amount earned from babysitting; recommend the clearer, correct sample 3.
- Source **3839**: sample 1 claims three nickels were left; use sample 3, which correctly identifies the three nickels spent.
- Source **6710**: sample 0 says `30*10=$300 charms` (currency unit slip); prefer sample 1.
- Source **4596**: the only correct-answer response is 178 tokens versus 114 for the closest rejected response; this may warrant a pair-length stratification rule.

## Before training

1. Obtain human signoff or further independent review on chosen/rejected decisions; especially source 234.
2. Compare reasoned curated DPO pairs with a separately labeled answer-only preference-selection policy, if studying how supervision quality affects DPO.
3. Implement deterministic, tested pair extraction **from the immutable pilot JSONL**, not from this human-readable report.
4. Verify exact token IDs (including native EOS 151643), prompt equality, no duplicated pairs, source indices confined to frozen training partition, and SHA-256 hashes before freezing outputs.
5. Do not count 18 as a statistically representative full-dataset yield: this is a selected pilot sample screened by one assistant.
