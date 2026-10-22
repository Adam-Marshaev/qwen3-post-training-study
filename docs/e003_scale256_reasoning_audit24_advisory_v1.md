# E003 scale-256: mathematical reasoning review of 24 mixed groups

**Status: advisory only. No independent signoff, no DPO training authorization.**

## Provenance

- Candidate dataset SHA256: `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`
- Original report SHA256: `21f1ba9222a7d4b91f18286e0e5e01834a7dfdba41ff2ceb0235fda496c73add`
- Selection manifest SHA256: `0f94473f4081c2cf141528f01e51fac59a11043e48f123d500b077d82afbea71`
- Generator revision: `ab39e3bab29a9a3115e6ec754086187092dcf89e`
- Deterministic selection seed: `20261022`
- Selection population: 146 mixed groups; reviewed 24 groups / 96 completions.

## Method and limitations

Each original completion was checked for arithmetic, problem interpretation, dimensional consistency, and whether its steps justify its final answer. Correctness against the provided GSM8K reference is recorded separately from reasoning validity. `SOUND` means the explanation is mathematically coherent; `FLAWED` means it contains a material reasoning error; `BORDERLINE` requires independent adjudication; `SOURCE_CONFLICT_SOUND` means the explanation accords with the literal question but conflicts with the supplied reference. This is a model-assisted **provisional screen**, not independent human review.

For each recommended APPROVE group, the suggested chosen response is correct-labelled and SOUND; the suggested rejected response is incorrect-labelled and FLAWED. The deterministic suggestions minimize absolute response-length difference, then chosen/rejected sample index; they are **not training artifacts**.

## Summary

- **APPROVE: 21/24** (87.5%)
- **HOLD: 2/24**
- **EXCLUDE: 1/24**
- Indicative Wilson 95% interval for approval fraction: **69.0%–95.7%**, without finite-population correction; this is exploratory and conditional on mixed groups, and excludes independent-review uncertainty.
- Per-candidate reasoning verdicts: `{'FLAWED': 57, 'SOUND': 36, 'BORDERLINE': 2, 'SOURCE_CONFLICT_SOUND': 1}`.
- Among answer-correct-labelled completions: `{'SOUND': 36, 'BORDERLINE': 2, 'FLAWED': 8}`.
- Advisory pair proposals: **21**, median absolute length gap **14** tokens, maximum **66** tokens.

## Review table

| Source | Advisory | SOUND chosen candidates | Flagged correct-labelled candidates | Suggested chosen → rejected | Key issue |
|---:|---|---|---|---|---|
| 5 | APPROVE | s3 | — | s3 → s2 (Δ21) | The green-flower count must use 25% of all 28 yellow and purple flowers; only sample 3 does so. |
| 744 | HOLD | — | s3 | — | Numerically correct sample 3 does not explain the relative closing speed: it substitutes the cyclist’s 20 mph into 5/20 and mentions a nonexistent restaurant. Needs independent adjudication. |
| 780 | APPROVE | s0, s1, s2 | — | s0 → s3 (Δ37) | Correct 36 pages/hour × 2 hours = 72. |
| 784 | APPROVE | s1, s2 | — | s1 → s3 (Δ11) | Jessica’s 27-pound pumpkin is the lightest, not Brad’s 54-pound pumpkin. |
| 1035 | APPROVE | s0, s1 | s3 | s1 → s2 (Δ7) | Samples 0 and 1 are valid; sample 3 gets 960 despite stating the wrong difference. |
| 1576 | APPROVE | s0, s2, s3 | — | s0 → s1 (Δ16) | Grimzi leaves 3 footprints per 6 meters rather than 3 per meter. |
| 1767 | APPROVE | s2 | s1 | s2 → s0 (Δ2) | Sample 1 has a wrong extra intermediate calculation, but sample 2 is fully sound. |
| 1920 | APPROVE | s0, s2 | — | s2 → s3 (Δ18) | Both samples 0 and 2 account for breakfast, lunch, snack, and dinner. |
| 2320 | HOLD | — | s1 | — | Only correct-labelled sample 1 claims “2 toppings to each pizza” despite the question specifying 3. Its multiplication 2×3 and final $50 are correct; independent reviewer must resolve whether this is a harmless typo or invalid rationale. |
| 2738 | APPROVE | s1, s3 | — | s3 → s2 (Δ6) | Two correct-labelled solutions sum $40+$15+$4.50=$59.50 and subtract $17.50. |
| 2909 | APPROVE | s0, s2, s3 | — | s0 → s1 (Δ2) | Wrong sample makes elementary addition error; correct candidates are valid. |
| 3027 | APPROVE | s3 | — | s3 → s1 (Δ14) | Only sample 3 faithfully tracks the starting 72 books, all additions, and both removals. |
| 3087 | APPROVE | s1, s3 | — | s3 → s2 (Δ9) | 20 required pages/day minus 18 planned pages/day equals two. |
| 3612 | APPROVE | s1 | — | s1 → s0 (Δ14) | Thirty-six 50-card packs at $3 each cost $108. |
| 3676 | APPROVE | s1, s3 | — | s1 → s0 (Δ17) | Two cups per night require two servings; 96 servings last 48 nights. |
| 3869 | APPROVE | s2 | — | s2 → s0 (Δ66) | Sample 2 correctly compares ideal 56 hours against actual 37. |
| 3912 | APPROVE | s3 | — | s3 → s1 (Δ1) | $250×12×5=$15000 financed; adding $5000 down gives $20000. |
| 4324 | APPROVE | s3 | — | s3 → s0 (Δ5) | Combined $15 divided by five people gives $3/person; each cousin receives $1. |
| 4457 | APPROVE | s0 | — | s0 → s3 (Δ48) | Twenty pounds produce ten dozen (120) cookies; 105 remain. |
| 4503 | APPROVE | s0, s3 | s1 | s0 → s2 (Δ9) | Samples 0 and 3 have valid units; sample 1 misstates the number of egg whites per cake. |
| 5436 | EXCLUDE | — | s0, s1, s3 | — | Question says five products with waits BETWEEN products (four intervals), making 20+30=50 minutes. Reference 55 and three correct-labelled completions assume five waiting intervals; sample 2 marked incorrect is mathematically and linguistically justified. Reference/text conflict: do not make a pair. |
| 6117 | APPROVE | s2 | s1, s3 | s2 → s0 (Δ20) | Sample 2 correctly solves x+(2x−8)=40. Samples 1 and 3 have correct final answers but logically invalid intermediate equations. |
| 6771 | APPROVE | s1, s2, s3 | — | s2 → s0 (Δ1) | Five office entries a day times two pull-ups times seven days is 70. |
| 7207 | APPROVE | s1 | — | s1 → s3 (Δ29) | Current anniversary age is 100; 200th anniversary minus five years occurs in 95 years. |

## Candidate-level audit (all 96 completions)

### Source 5 — APPROVE

The green-flower count must use 25% of all 28 yellow and purple flowers; only sample 3 does so.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 100 tokens. Uses 25% of purple flowers alone (18), omitting yellow flowers.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 74 tokens. Miscomputes green flowers as 0.25×10 + 18 rather than 0.25×(10+18).
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 117 tokens. Uses 18/4 green flowers rather than (10+18)/4.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 138 tokens. 10 yellow; 18 purple; 7 green; total 35.

### Source 744 — HOLD

Numerically correct sample 3 does not explain the relative closing speed: it substitutes the cyclist’s 20 mph into 5/20 and mentions a nonexistent restaurant. Needs independent adjudication.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 101 tokens. Invalid conversion of 20 mph to miles/minute and inconsistent time arithmetic.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 170 tokens. Computes the time to reach Yolanda’s starting head start, ignoring that she keeps cycling.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 137 tokens. Also ignores Yolanda’s continued motion; 5/40 hours is not catch-up time.
- **Sample 3** — reference answer match: **True**; reasoning: **BORDERLINE**; 147 tokens. Correct 15 minutes, but incorrectly attributes closing-speed calculation to her own speed; relative speed 40−20=20 mph is never justified.

### Source 780 — APPROVE

Correct 36 pages/hour × 2 hours = 72.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 64 tokens. Triples the reading rate and multiplies by two hours.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 90 tokens. Correctly computes 36 pages/hour for two hours.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 85 tokens. Correct rate and duration.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 27 tokens. Stops at the one-hour enhanced rate (36); omits the two-hour factor.

### Source 784 — APPROVE

Jessica’s 27-pound pumpkin is the lightest, not Brad’s 54-pound pumpkin.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 82 tokens. Mistakes Brad’s 54-pound pumpkin for the lightest instead of Jessica’s 27-pound pumpkin.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 66 tokens. Correctly identifies 108 pounds and 27 pounds; difference 81.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 106 tokens. Correctly compares heaviest Betty (108) with lightest Jessica (27).
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 77 tokens. Mistakes Brad’s 54-pound pumpkin for the lightest.

### Source 1035 — APPROVE

Samples 0 and 1 are valid; sample 3 gets 960 despite stating the wrong difference.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 146 tokens. 600 boys, 1000 girls, 1600 total, 60%=960.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 84 tokens. Computes 1000 girls and 60% of 1600 correctly.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 91 tokens. Assumes girls are 400 fewer than boys despite the explicit opposite condition.
- **Sample 3** — reference answer match: **True**; reasoning: **FLAWED**; 105 tokens. Incorrectly states the girl/boy difference is 600, then uses 400 to compute girls; internal contradiction.

### Source 1576 — APPROVE

Grimzi leaves 3 footprints per 6 meters rather than 3 per meter.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 109 tokens. 24000 + 3000 = 27000.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 125 tokens. Misreads Grimzi’s footprint rate as 3 per meter.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 93 tokens. Correctly scales 3/6 footprints per meter over 6000 meters.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 89 tokens. Correct footprint rates and total.

### Source 1767 — APPROVE

Sample 1 has a wrong extra intermediate calculation, but sample 2 is fully sound.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 89 tokens. Subtracts number of non-chive rows (5) directly from the plant count (200).
- **Sample 1** — reference answer match: **True**; reasoning: **FLAWED**; 79 tokens. Falsely claims first 3 rows contain 20×3=60 plants; correct is 3×10=30, although final result is right.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 91 tokens. 200 plants minus 30 parsley and 20 rosemary =150 chives.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 153 tokens. Subtracts 50 plants from 20 rows, mixing units, and invents zero chives.

### Source 1920 — APPROVE

Both samples 0 and 2 account for breakfast, lunch, snack, and dinner.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 95 tokens. Subtracts all four consumptions; two remain.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 40 tokens. Omits 5 slices eaten at dinner.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 85 tokens. Correct successive subtractions, including dinner.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 67 tokens. Omits the 2 lunch slices, yielding four instead of two.

### Source 2320 — HOLD

Only correct-labelled sample 1 claims “2 toppings to each pizza” despite the question specifying 3. Its multiplication 2×3 and final $50 are correct; independent reviewer must resolve whether this is a harmless typo or invalid rationale.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 105 tokens. Contradicts topping count and charges only $4 for six toppings instead of $12.
- **Sample 1** — reference answer match: **True**; reasoning: **BORDERLINE**; 164 tokens. Correct amount $50 and correct 2×3×$2 math, but explicitly says 2 toppings per pizza rather than 3.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 140 tokens. Treats six toppings as $6 rather than $12, ignoring the per-topping price.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 159 tokens. Reassigns the $14 pizza price and $2 topping price nonsensically.

### Source 2738 — APPROVE

Two correct-labelled solutions sum $40+$15+$4.50=$59.50 and subtract $17.50.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 91 tokens. Incorrectly adds $40+$15+$4.50 as $59 and computes $59−$17.50 as $41.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 156 tokens. Correctly computes $59.50 initial and $42.00 remaining.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 96 tokens. Repeats the same $59 and $41 arithmetic errors as sample 0.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 102 tokens. Correct $59.50 total and $42 balance; slight informal phrasing about loose change does not alter reasoning.

### Source 2909 — APPROVE

Wrong sample makes elementary addition error; correct candidates are valid.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 64 tokens. 20×$2=$40; 6×$8=$48; total $88.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 62 tokens. Adds $40+$48 as $98 instead of $88.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 80 tokens. Correct egg and chicken subtotals.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 59 tokens. Correct cost and sum.

### Source 3027 — APPROVE

Only sample 3 faithfully tracks the starting 72 books, all additions, and both removals.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 183 tokens. Misinterprets monthly books, omits starting 72 and other purchases, and produces conflicting totals.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 154 tokens. Misaccounts for purchases/gifts and treats sold books as additions.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 194 tokens. Omits original 72 and double-counts a daughter’s gift.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 168 tokens. 72+12+5+2+1+4−12−3=81.

### Source 3087 — APPROVE

20 required pages/day minus 18 planned pages/day equals two.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 68 tokens. Subtracts one day’s 18 pages from the total 140 pages before dividing, mixing time horizons.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 58 tokens. 140/7−3×6=2 more pages per day.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 91 tokens. Compares 18 pages/day with six pages per reading, never incorporating the 140-page target correctly.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 82 tokens. Correct daily target and increment.

### Source 3612 — APPROVE

Thirty-six 50-card packs at $3 each cost $108.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 58 tokens. Uses one period’s students and treats card packs as dollars; omits pack price.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 72 tokens. 180 students ×10 =1800 cards; 36 packs ×$3=$108.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 91 tokens. Finds 36 packs but fails to multiply by $3 per pack.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 135 tokens. Changes the class size from 30 to 36 and computes a fractional pack count.

### Source 3676 — APPROVE

Two cups per night require two servings; 96 servings last 48 nights.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 126 tokens. Adds cups and servings (2+1) instead of multiplying 2×1 servings.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 109 tokens. Correct 96 total servings /2 per night =48 nights.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 208 tokens. Chains incorrect quantities and inconsistent units, ultimately concluding four nights.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 90 tokens. Correct rate and division.

### Source 3869 — APPROVE

Sample 2 correctly compares ideal 56 hours against actual 37.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 109 tokens. Uses only two nights for ideal sleep and reverses the deficit.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 67 tokens. Applies 3-hour weeknight deficit to two nights rather than five; omits weekends.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 175 tokens. Weeknights 25, weekend 12, ideal 56, deficit 19.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 71 tokens. Misreads nights and equates total sleeping hours with sleep deficit.

### Source 3912 — APPROVE

$250×12×5=$15000 financed; adding $5000 down gives $20000.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 71 tokens. Counts 12 payments instead of the 60 payments in five years.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 68 tokens. Invents interest despite explicitly interest-free loan and uses unrelated arithmetic.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 91 tokens. Subtracts down payment from the already-financed payment total instead of adding it.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 67 tokens. Correct loan payments plus down payment.

### Source 4324 — APPROVE

Combined $15 divided by five people gives $3/person; each cousin receives $1.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 81 tokens. Treats total money and transfer amounts inconsistently; concludes $2/cousin.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 95 tokens. Reverses payment direction and divides a one-dollar difference by four.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 66 tokens. Subtracts the cousins’ aggregate money from Carmela’s amount rather than equalizing all five.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 76 tokens. Conserves $15 and equalizes each of five people at $3.

### Source 4457 — APPROVE

Twenty pounds produce ten dozen (120) cookies; 105 remain.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 69 tokens. 4×5=20 lb; 20/2=10 dozen; 120−15=105.
- **Sample 1** — reference answer match: **False**; reasoning: **FLAWED**; 122 tokens. Divides 20 pounds by six cookies per pound instead of multiplying and mishandles units.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 130 tokens. Confuses cookies and dozens, and inconsistently subtracts 15 from eight.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 117 tokens. Incorrect conversions between pounds, dozens, and cookies.

### Source 4503 — APPROVE

Samples 0 and 3 have valid units; sample 1 misstates the number of egg whites per cake.

- **Sample 0** — reference answer match: **True**; reasoning: **SOUND**; 69 tokens. Two cakes need 16 egg whites, each replaced by two tablespoons, totaling 32.
- **Sample 1** — reference answer match: **True**; reasoning: **FLAWED**; 56 tokens. Says 16 egg whites per cake, although 16 is the combined total for two cakes; final total happens to be correct.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 60 tokens. Divides 16 by the replacement rate of two tablespoons per egg white instead of multiplying.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 70 tokens. Correct total eggs and aquafaba conversion.

### Source 5436 — EXCLUDE

Question says five products with waits BETWEEN products (four intervals), making 20+30=50 minutes. Reference 55 and three correct-labelled completions assume five waiting intervals; sample 2 marked incorrect is mathematically and linguistically justified. Reference/text conflict: do not make a pair.

- **Sample 0** — reference answer match: **True**; reasoning: **FLAWED**; 46 tokens. Assumes five waiting intervals; between five products there are four.
- **Sample 1** — reference answer match: **True**; reasoning: **FLAWED**; 46 tokens. Again assumes five waits instead of four.
- **Sample 2** — reference answer match: **False**; reasoning: **SOURCE_CONFLICT_SOUND**; 74 tokens. Four intervals ×5 minutes +30 makeup =50, a sound reading of the literal source; nevertheless marked incorrect against reference 55.
- **Sample 3** — reference answer match: **True**; reasoning: **FLAWED**; 42 tokens. Assumes five gaps/waits, contradicting “between each product.”

### Source 6117 — APPROVE

Sample 2 correctly solves x+(2x−8)=40. Samples 1 and 3 have correct final answers but logically invalid intermediate equations.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 152 tokens. Equates Cape May’s own count 2d−8 to the combined total, omitting Daytona from the total.
- **Sample 1** — reference answer match: **True**; reasoning: **FLAWED**; 76 tokens. Writes an unjustified 2x−8+16=40, obtains x=12, and then incorrectly claims 2×12−8=24.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 132 tokens. Sets x+(2x−8)=40, solves x=16 and Cape May=24.
- **Sample 3** — reference answer match: **True**; reasoning: **FLAWED**; 138 tokens. Substitutes an invented Cape May relationship x+8 for the stated 2x−8; answer 24 is coincidental.

### Source 6771 — APPROVE

Five office entries a day times two pull-ups times seven days is 70.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 78 tokens. Invents five rooms and extra room/day factors; original specifies one office, five visits daily.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 46 tokens. 5×2=10 per day, 10×7=70 per week.
- **Sample 2** — reference answer match: **True**; reasoning: **SOUND**; 77 tokens. Correct daily and weekly multiplication.
- **Sample 3** — reference answer match: **True**; reasoning: **SOUND**; 52 tokens. Correct rate calculation.

### Source 7207 — APPROVE

Current anniversary age is 100; 200th anniversary minus five years occurs in 95 years.

- **Sample 0** — reference answer match: **False**; reasoning: **FLAWED**; 113 tokens. Misuses the remaining 100 years and subtracts five years inconsistently.
- **Sample 1** — reference answer match: **True**; reasoning: **SOUND**; 48 tokens. Compressed but valid reasoning: 100 years remain until the 200th anniversary; five years earlier is 95 years away.
- **Sample 2** — reference answer match: **False**; reasoning: **FLAWED**; 101 tokens. Introduces arbitrary calendar years and incorrect subtraction.
- **Sample 3** — reference answer match: **False**; reasoning: **FLAWED**; 77 tokens. Adds five years to the 200th anniversary rather than subtracting five.

## Mandatory restrictions

- This is **not** independent human signoff.
- No DPO preference training is authorized; the source run performed no training.
- The 21 advisory pairs are suggestions, not a constructed or frozen preference dataset.
- Review source 744 (relative-speed justification) and 2320 (topping-count contradiction) independently.
- Exclude source 5436 because the literal problem and supplied reference/labels disagree.
- This review sample is representative of the **146 mixed groups only**, not of all 256 questions or all 1,024 completions.
