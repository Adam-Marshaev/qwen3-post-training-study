# E003 Batch 01 — Mathematical reasoning audit (advisory v1)

> **Assistant advisory screen only.** No independent human pair signoff; no reference change, dataset construction, or DPO/GRPO training authorization.

## Provenance

- Frozen E003 candidate dataset SHA256: `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`
- Uploaded Batch 01 review SHA256: `c22dab37d29f56b46d396a4d3eb6acb329db5c495c2fdc9def3a2ce538b644db`
- Uploaded Batch 01 selection SHA256: `2ca1ad3263504bcaeed4352162bfa9fa2db3cfbfe826aa57e6f782372e2c767c`
- Population: 20 source indices, four original completions each; labels and generated text unchanged.
- Source indices: 1512, 1520, 1651, 1859, 1870, 1889, 1927, 2125, 2272, 2277, 2477, 2491, 2515, 2717, 2731, 2786, 2860, 3012, 3181, 3287

## Summary

- Advisory recommendation: **16 PROVISIONAL APPROVE**, **4 HOLD**, **0 EXCLUDE**.
- All **80 completions** screened; reasoning counts: **BORDERLINE: 4**, **CONDITIONAL: 6**, **FLAWED: 50**, **SOUND: 20**.
- Proposed pairs: **16**; median absolute length gap **11.5 tokens**, maximum **50 tokens**.
- Ineligible 256-token-cap completions: **source 1927 samples 0 and 3**; neither is eligible for pairing.
- Human adjudication required: **1512** (bonus formula quantifier), **1651** (no sound reference-matching derivation), **2272** (comparative contradiction), **2515** (threshold “before” wording).

## Pair proposals (advisory only)

| Source | Verdict | Chosen → Rejected | Gap (tokens) | Key concern |
|---:|---|---|---:|---|
| 1512 | HOLD | — | — | The stem says “for every customer” but also defines the bonus as 20% of the number served, permitting both per-customer and aggregate readings (1280 versus 16). |
| 1520 | PROVISIONAL_APPROVE | 1 → 0 | 13 | Sample 1 cleanly calculates mother 5, brother 7, and 30−10−5−7=8. |
| 1651 | HOLD | — | — | Neither answer-matching candidate derives 4 cubic feet correctly. |
| 1859 | PROVISIONAL_APPROVE | 3 → 2 | 3 | Only sample 3 correctly multiplies each daily rate by 42 days and subtracts 3360−1260=2100. |
| 1870 | PROVISIONAL_APPROVE | 0 → 2 | 50 | Sample 0 derives 60+B+C=180, B=2C, then B=80. |
| 1889 | PROVISIONAL_APPROVE | 0 → 1 | 11 | Sample 0 correctly infers yearly spending 80,60,30 and multiplies 170 by four. |
| 1927 | PROVISIONAL_APPROVE | 1 → 2 | 22 | Sample 1 is sound and terminates with native EOS; sample 2 is an eligible incorrect negative. |
| 2125 | PROVISIONAL_APPROVE | 2 → 0 | 18 | Sample 2 cleanly converts dog age 3×7=21 and subtracts Max’s 3 years to obtain the reference difference 18. |
| 2272 | HOLD | — | — | Only sample 3 returns 225, but its sentence incorrectly states that week 2 has “50 fewer” employees than week 1 (250 versus 50 means 200 fewer). |
| 2277 | PROVISIONAL_APPROVE | 3 → 2 | 4 | Sample 3 correctly finds 14 total friends minus 3 girls = 11 boys; sample 0 first calls all 14 friends boys. |
| 2477 | PROVISIONAL_APPROVE | 0 → 1 | 19 | Sample 0 correctly assigns $108 to the SECOND job and subtracts it from $160. |
| 2491 | PROVISIONAL_APPROVE | 3 → 1 | 7 | Sample 3 correctly handles dozens: 20×2. |
| 2515 | HOLD | — | — | From 50 existing points, one throw reaches 75 without office referral; second reaches 100 and triggers referral. |
| 2717 | PROVISIONAL_APPROVE | 3 → 1 | 6 | Samples 2 and 3 both correctly derive district counts 322,625,644 and sum 1591. |
| 2731 | PROVISIONAL_APPROVE | 0 → 3 | 9 | Both samples 0 and 2 correctly count 27+15=42 laps and 98−42=56 remaining. |
| 2786 | PROVISIONAL_APPROVE | 3 → 1 | 29 | Sample 3 correctly applies 4 hours each way and $10/hour for $80 total. |
| 2860 | PROVISIONAL_APPROVE | 0 → 1 | 12 | Sample 0 correctly maps 6×12=72 total slices to 72 goals and divides by 8 games, despite a minor wording slip (“scored 8 games”). |
| 3012 | PROVISIONAL_APPROVE | 2 → 3 | 39 | Sample 2 has correct substance: 4×6=24 available, 8×2+3=19 eaten, 5 remain. |
| 3181 | PROVISIONAL_APPROVE | 3 → 1 | 0 | Only samples 2 and 3 correctly explain the dog closes a 160-foot gap at relative speed 20−12=8 ft/s. |
| 3287 | PROVISIONAL_APPROVE | 0 → 2 | 8 | Samples 0 and 3 correctly sum two workers $200, electrician $200, plumber $250, total $650. |

## Mathematical review — all original completions

### Source 1512 — HOLD

**Question:** In a certain company, for every customer served, an employee gets as many bonus points, as 20% of the number of customers served. On Monday, Tom served 10 customers per hour for 8 hours. How many bonus points did Tom earn that day?

**Frozen reference:** `16`

**Group assessment:** The stem says “for every customer” but also defines the bonus as 20% of the number served, permitting both per-customer and aggregate readings (1280 versus 16). Do not select a training pair until the reward rule is clarified.

- **Sample 0** — **CONDITIONAL**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`75`, extracted answer=`16`. Correct 80 customers and 20% = 16 under the aggregate bonus interpretation; stem could imply points awarded per individual customer.
- **Sample 1** — **CONDITIONAL**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`118`, extracted answer=`1280`. 80 customers, 16 points calculated for EACH of 80 customers gives 1280; plausible under literal per-customer interpretation, inconsistent with the reference convention.
- **Sample 2** — **CONDITIONAL**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`45`, extracted answer=`16`. Computes 80 × 20% = 16 under total-bonus interpretation; ambiguous use of “for every customer”.
- **Sample 3** — **CONDITIONAL**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`77`, extracted answer=`16`. Computes 20% of 80 = 16, but text could specify 20%-of-total award per customer.

**No pair proposed:** HOLD pending project-owner decision.

### Source 1520 — PROVISIONAL_APPROVE

**Question:** Monica made cookies for herself and her family. Her father ate 10 cookies and her mother ate half as much as the father. Her brother ate 2 more than her mother. How many cookies are left for Monica if she made 30 cookies in total?

**Frozen reference:** `8`

**Group assessment:** Sample 1 cleanly calculates mother 5, brother 7, and 30−10−5−7=8. Sample 2 misidentifies family members as “three girls” despite sound arithmetic.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`63`, extracted answer=`0`. Computes mother=5 and brother=7 but invents subtraction 7−10=−3 and concludes zero.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`76`, extracted answer=`8`. Mother=5, brother=7, parents=15, leaving 30−15−7=8.
- **Sample 2** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`81`, extracted answer=`8`. Correct 10+5+7=22 and 30−22=8 but refers to father, mother and brother as “three girls”.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`59`, extracted answer=`6`. Writes 30−10−5−7=6, an explicit arithmetic error: the expression equals 8.

**Provisional pair:** chosen `1` > rejected `0`; absolute token gap **13**. Not independently approved.

### Source 1651 — HOLD

**Question:** John builds a box.  The box is 26 inches by 26 inches by 14 inches.  The walls are 1 inch thick on each side.  How much is the internal volume in cubic feet?

**Frozen reference:** `4`

**Group assessment:** Neither answer-matching candidate derives 4 cubic feet correctly. Assuming 1-inch walls on each side, internal dimensions 24×24×12 inches produce 6912/1728=4 ft³.

- **Sample 0** — **FLAWED**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`78`, extracted answer=`4`. Uses 24×24×13 (wrong height) and claims 24×24×13=7680 and 7680/1728=4; both equalities are false.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`102`, extracted answer=`73.67`. Confuses area/volume, calculates 26×26×14 incorrectly, and uses a false cubic-inch conversion.
- **Sample 2** — **FLAWED**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`93`, extracted answer=`4`. Uses 24×26×12 instead of 24×24×12; falsely claims 24×26×12=7728 and 7728/1728=4.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`103`, extracted answer=`53.1`. Correctly sets 24×24×12=6912 cubic inches, then wrongly uses 128 instead of 1728 cubic inches per cubic foot.

**No pair proposed:** HOLD pending project-owner decision.

### Source 1859 — PROVISIONAL_APPROVE

**Question:** If Janet reads 80 pages a day and Belinda reads 30 pages a day, how many more pages does Janet read in 6 weeks?

**Frozen reference:** `2100`

**Group assessment:** Only sample 3 correctly multiplies each daily rate by 42 days and subtracts 3360−1260=2100.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`128`, extracted answer=`42.84`. Divides daily page rates by 7 rather than multiplying by 7 days per week.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`86`, extracted answer=`350`. Computes one-week difference 350 but fails to multiply by 6 weeks.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`120`, extracted answer=`1100`. Correctly computes totals 3360 and 1260, then reports the invalid subtraction 1260−3360=1100.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`123`, extracted answer=`2100`. 80×7×6=3360, 30×7×6=1260, difference 2100.

**Provisional pair:** chosen `3` > rejected `2`; absolute token gap **3**. Not independently approved.

### Source 1870 — PROVISIONAL_APPROVE

**Question:** In a triangle with angles A, B, and C, A is 60 degrees, and B is two times as big as C. Calculate the angle of B.

**Frozen reference:** `80`

**Group assessment:** Sample 0 derives 60+B+C=180, B=2C, then B=80. Sample 3 begins with an incorrect B+C=180 claim before correcting it.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`180`, extracted answer=`80`. Sets B+C=120, B=2C, yielding C=40, B=80.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`45`, extracted answer=`120`. Treats B as twice A=60 rather than twice C.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`130`, extracted answer=`120`. Omits known angle A=60 when summing triangle angles, giving B+C=180.
- **Sample 3** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`230`, extracted answer=`80`. Opens by falsely asserting B+C=180, then gives a valid derivation B+C=120 and B=80.

**Provisional pair:** chosen `0` > rejected `2`; absolute token gap **50**. Not independently approved.

### Source 1889 — PROVISIONAL_APPROVE

**Question:** Trevor and two of his neighborhood friends go to the toy shop every year to buy toys. Trevor always spends $20 more than his friend Reed on toys, and Reed spends 2 times as much money as their friend Quinn on the toys. If Trevor spends $80 every year to buy his toys, calculate how much money in total the three spend in 4 years.

**Frozen reference:** `680`

**Group assessment:** Sample 0 correctly infers yearly spending 80,60,30 and multiplies 170 by four.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`142`, extracted answer=`680`. Reed=80−20=60, Quinn=60/2=30; (80+60+30)×4=680.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`131`, extracted answer=`740`. Counts 30 for Reed’s already inferred amount as a separate person and invents another $15 Quinn, yielding four terms for three people.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`123`, extracted answer=`480`. Uses Trevor’s $80 incorrectly as Reed/Quinn starting amount and omits Quinn.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`111`, extracted answer=`1440`. Treats Reed as spending 2×60, double counts expenditures and arbitrarily multiplies by 2.

**Provisional pair:** chosen `0` > rejected `1`; absolute token gap **11**. Not independently approved.

### Source 1927 — PROVISIONAL_APPROVE

**Question:** Mike and Leo have to print as many pamphlets as possible for a social gathering. Mike manages to print as fast as 600 pamphlets per hour for 9 consecutive hours. After a break, he resumes the task for another 2 hours achieving a third of the speed he was doing before. Leo, on the other hand, only works a third as many hours as Mike did before his break, but was twice as fast as Mike before he took his break. How many pamphlets do both manage to print at the end?

**Frozen reference:** `9400`

**Group assessment:** Sample 1 is sound and terminates with native EOS; sample 2 is an eligible incorrect negative. Samples 0 and 3 are truncated/ineligible and cannot form preference pairs.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`false`, native EOS=`false`, tokens=`256`, extracted answer=`None`. INELIGIBLE/TRUNCATED at 256 tokens without final answer; also incorrectly adds old/new printing speeds and reverses Leo’s conditions.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`189`, extracted answer=`9400`. Mike prints 600×9+200×2=5800; Leo prints (2×600)×(9/3)=3600; total 9400.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`211`, extracted answer=`8250`. Treats printed total as hourly speed, miscalculates post-break quantity and invents Leo output.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`false`, native EOS=`false`, tokens=`256`, extracted answer=`None`. INELIGIBLE/TRUNCATED at 256 tokens without final answer; confuses Mike’s reduced speed and Leo’s speed/hours.

**Provisional pair:** chosen `1` > rejected `2`; absolute token gap **22**. Not independently approved.

### Source 2125 — PROVISIONAL_APPROVE

**Question:** For every 1 year a human ages, a dog ages 7 years.  When Max is 3, how much older, in dog years, will his 3-year-old dog be?

**Frozen reference:** `18`

**Group assessment:** Sample 2 cleanly converts dog age 3×7=21 and subtracts Max’s 3 years to obtain the reference difference 18.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`63`, extracted answer=`21`. Computes dog age 21 but omits subtraction of Max’s 3 years.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`67`, extracted answer=`15`. Computes 21−3=18 and then subtracts Max’s age a second time to obtain 15.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`45`, extracted answer=`18`. Dog=21 dog years; difference from Max’s 3-year age =18.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`108`, extracted answer=`15`. Double-subtracts the human age, giving 15 instead of 18.

**Provisional pair:** chosen `2` > rejected `0`; absolute token gap **18**. Not independently approved.

### Source 2272 — HOLD

**Question:** A company hires employees on a contract basis, depending on the availability of work. In a particular month, they hired 200 more employees on the first week than on the second week, and 150 fewer employees on the second week than on the third week. If the number of employees hired on the fourth week was twice the number hired in the third week,  and the number of employees on the fourth week was 400, what's the average number of employees hired per week?

**Frozen reference:** `225`

**Group assessment:** Only sample 3 returns 225, but its sentence incorrectly states that week 2 has “50 fewer” employees than week 1 (250 versus 50 means 200 fewer). Preserve as borderline until independent reviewer accepts or rejects the explanatory contradiction.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`249`, extracted answer=`190`. Correctly derives week counts 250,50,200,400 but invents five weekly entries and divides by 5.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`169`, extracted answer=`262.5`. Derives correct weekly counts but substitutes 200 for week 2 instead of 50 in the total.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`201`, extracted answer=`575`. Transforms the stated fourth-week total of 400 into 800, then uses internally inconsistent algebra.
- **Sample 3** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`170`, extracted answer=`225`. Arithmetic for week counts 250,50,200,400 and mean 225 is correct, but describes week 2 as 50 fewer than week 1, rather than 200 fewer.

**No pair proposed:** HOLD pending project-owner decision.

### Source 2277 — PROVISIONAL_APPROVE

**Question:** Davante has twice as many friends as there are days in the week. 3 of his friends are girls. How many friends does he have that are boys?

**Frozen reference:** `11`

**Group assessment:** Sample 3 correctly finds 14 total friends minus 3 girls = 11 boys; sample 0 first calls all 14 friends boys.

- **Sample 0** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`77`, extracted answer=`11`. Incorrectly labels 14 total friends as 14 boys, then correctly subtracts three girls for final 11.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`46`, extracted answer=`24`. Contradictory statements: 7×4 is not 28-to-36, 36−3 is not 36, and final answer 24 unsupported.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`42`, extracted answer=`9`. States he has five friends despite computing 7×2=14, then falsely evaluates 14−3=9.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`38`, extracted answer=`11`. Twice the seven days gives 14 total friends; 14−3=11 boys.

**Provisional pair:** chosen `3` > rejected `2`; absolute token gap **4**. Not independently approved.

### Source 2477 — PROVISIONAL_APPROVE

**Question:** Mike has earned a total of $160 in wages this week. He received the wages for his first job, then later received the wages from his second job where he works 12 hours a week. If his second job pays $9 per hour then how much money, in dollars, did Mike receive from his first job?

**Frozen reference:** `52`

**Group assessment:** Sample 0 correctly assigns $108 to the SECOND job and subtracts it from $160. Other answer-correct samples wrongly attribute the $9/hour job to the first job.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`72`, extracted answer=`52`. Second-job pay=12×9=108; first-job pay=160−108=52.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`53`, extracted answer=`108`. Correctly computes second-job $108 but then relabels $108 as first-job earnings.
- **Sample 2** — **FLAWED**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`83`, extracted answer=`52`. Falsely assigns $9/hour and 12 hours to first job while separately calling its $52 remainder first-job earnings.
- **Sample 3** — **FLAWED**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`76`, extracted answer=`52`. Falsely assigns $9/hour and 12 hours to first job while calling the residual $52 first-job pay.

**Provisional pair:** chosen `0` > rejected `1`; absolute token gap **19**. Not independently approved.

### Source 2491 — PROVISIONAL_APPROVE

**Question:** A candy store sold 20 pounds of fudge for $2.50/pound, 5 dozen chocolate truffles for $1.50 each and 3 dozen chocolate-covered pretzels at $2.00 each.  How much money did the candy store make?

**Frozen reference:** `212`

**Group assessment:** Sample 3 correctly handles dozens: 20×2.50+5×12×1.50+3×12×2=212.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`102`, extracted answer=`63.5`. Treats five and three DOZEN as five and three items, giving $7.50 and $6 instead of $90 and $72.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`79`, extracted answer=`182`. Counts truffles as $60, omitting $1.50-per-truffle multiplier.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`97`, extracted answer=`63`. Treats dozen counts as unit counts and also falsely adds 50+7.5+6 as 63.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`86`, extracted answer=`212`. Revenue $50 fudge + $90 truffles + $72 pretzels = $212.

**Provisional pair:** chosen `3` > rejected `1`; absolute token gap **7**. Not independently approved.

### Source 2515 — HOLD

**Question:** Mrs. Carlton gives out penalty points whenever her students misbehave. They get 5 points for interrupting, 10 points for insulting their classmates, and 25 points for throwing things. If they get 100 points, they have to go to the office. Jerry already interrupted twice and insulted his classmates 4 times. How many times can he throw things before he gets sent to the office?

**Frozen reference:** `2`

**Group assessment:** From 50 existing points, one throw reaches 75 without office referral; second reaches 100 and triggers referral. “How many times can he throw things before he gets sent” could mean one safely before referral or two including the triggering throw.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`88`, extracted answer=`17`. Ignores event frequencies and incorrectly assigns throwing the five-point penalty.
- **Sample 1** — **CONDITIONAL**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`122`, extracted answer=`2`. Correctly gets 50 points remaining and two 25-point throws to REACH threshold; phrasing may ask for throws strictly before referral.
- **Sample 2** — **CONDITIONAL**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`100`, extracted answer=`2`. Correct arithmetic to reach the threshold in two throws; the question’s “before” may exclude the referral-triggering throw.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`166`, extracted answer=`5`. Confuses interruptions/insults and interprets remaining penalty points as times to throw.

**No pair proposed:** HOLD pending project-owner decision.

### Source 2717 — PROVISIONAL_APPROVE

**Question:** There are 322 voters in District 1. District 2 has 19 less voters than District 3. District 3 has twice as many voters as District 1. How many total voters are in Districts 1 - 3?

**Frozen reference:** `1591`

**Group assessment:** Samples 2 and 3 both correctly derive district counts 322,625,644 and sum 1591.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`73`, extracted answer=`1269`. Correctly computes district 2 and 3 but omits district 1 from total.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`77`, extracted answer=`1691`. Correct district values, incorrect addition: 625+322+644 is 1591, not 1691.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`84`, extracted answer=`1591`. District 3=644, district 2=625; 625+644+322=1591.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`83`, extracted answer=`1591`. District counts 322,625,644; sum 1591.

**Provisional pair:** chosen `3` > rejected `1`; absolute token gap **6**. Not independently approved.

### Source 2731 — PROVISIONAL_APPROVE

**Question:** Jeff’s swimming coach required him to swim 98 laps over the weekend. On Saturday, Jeff swam 27 laps. On Sunday morning, he swam 15 laps, took a break, then resumed practice in the afternoon. How many laps did Jeff have remaining when he took the break?

**Frozen reference:** `56`

**Group assessment:** Both samples 0 and 2 correctly count 27+15=42 laps and 98−42=56 remaining.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`79`, extracted answer=`56`. Counts 42 laps completed at break and subtracts from 98 to get 56.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`66`, extracted answer=`46`. Correctly gets 56 at break but invents an extra 10 laps after it, yielding 46.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`44`, extracted answer=`56`. 98−(27+15)=56 laps at the break.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`70`, extracted answer=`68`. Ignores 27 Saturday laps and invents an extra 15 laps after break.

**Provisional pair:** chosen `0` > rejected `3`; absolute token gap **9**. Not independently approved.

### Source 2786 — PROVISIONAL_APPROVE

**Question:** Tom decided to go on a trip. During this trip, he needs to cross a lake, which in one direction takes 4 hours. During this time, Tom needs an assistant to help him with the crossing. Hiring an assistant costs $10 per hour. How much would Tom have to pay for help with crossing the lake back and forth?

**Frozen reference:** `80`

**Group assessment:** Sample 3 correctly applies 4 hours each way and $10/hour for $80 total.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`43`, extracted answer=`40`. Calculates one-way cost only, omitting return crossing.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`106`, extracted answer=`120`. Correctly finds $80 for eight hours then double-counts return trip for $120.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`33`, extracted answer=`40`. Assumes round trip takes only four hours rather than eight.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`77`, extracted answer=`80`. 4×2=8 total hours, 8×$10=$80.

**Provisional pair:** chosen `3` > rejected `1`; absolute token gap **29**. Not independently approved.

### Source 2860 — PROVISIONAL_APPROVE

**Question:** Mr. Mitchell is buying pizzas for the soccer team. He buys one slice for every goal they scored on the season. A large pizza has 12 slices. If he bought 6 pizzas, and the team had 8 games, how many goals did they score per game on average?

**Frozen reference:** `9`

**Group assessment:** Sample 0 correctly maps 6×12=72 total slices to 72 goals and divides by 8 games, despite a minor wording slip (“scored 8 games”).

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`66`, extracted answer=`9`. Total slices=6×12=72, one slice per goal, average 72/8=9 goals per game; minor “scored 8 games” wording slip.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`54`, extracted answer=`1.5`. Divides slices by number of pizzas (72/6) rather than mapping slices to goals.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`53`, extracted answer=`6`. Divides total slices by slices per pizza instead of by eight games.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`84`, extracted answer=`0.75`. Treats six pizzas as six goals rather than 72 slices/goals.

**Provisional pair:** chosen `0` > rejected `1`; absolute token gap **12**. Not independently approved.

### Source 3012 — PROVISIONAL_APPROVE

**Question:** Amber is baking cakes for her party. She has invited 8 friends and each one will want two slices of cake. Each cake makes 6 slices. If she bakes 4 cakes, how many slices will be left over at the end if she eats three herself?

**Frozen reference:** `5`

**Group assessment:** Sample 2 has correct substance: 4×6=24 available, 8×2+3=19 eaten, 5 remain. Minor “need” wording does not alter its calculations.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`83`, extracted answer=`4`. Invents 16+4=20 slices, then computes nonsensical fractional leftovers.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`63`, extracted answer=`93`. Mistakenly multiplies 16 slices for guests by 6 slices/cake, giving 96 rather than 24 available.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`123`, extracted answer=`5`. 24 baked slices minus 16 guests’ slices and 3 for Amber =5; calls 24 “needed” once, but correctly uses it as available supply.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`84`, extracted answer=`24`. Treats 24 baked slices as demand, adds 3, then misreports available slices as remaining.

**Provisional pair:** chosen `2` > rejected `3`; absolute token gap **39**. Not independently approved.

### Source 3181 — PROVISIONAL_APPROVE

**Question:** Mary's sheep can run 12 feet per second, and her sheepdog can run 20 feet per second. A sheep standing 160 feet away from the sheep dog bolts, and the dog runs after it. How many seconds does it take the dog to catch the sheep?

**Frozen reference:** `20`

**Group assessment:** Only samples 2 and 3 correctly explain the dog closes a 160-foot gap at relative speed 20−12=8 ft/s. Sample 0 incorrectly says sheep gains 8 ft/s.

- **Sample 0** — **FLAWED**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`55`, extracted answer=`20`. Gets final time 20 but states that the slower sheep gains 8 feet per second on the faster dog; reasoning direction is false.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`57`, extracted answer=`2`. Invents dog speed 80 ft/s and a false division 20/2=10 =>80.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`67`, extracted answer=`20`. Relative approach speed 20−12=8 ft/s; time 160/8=20 s.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`57`, extracted answer=`20`. Dog runs 8 ft/s faster, so closes 160 feet in 20 seconds.

**Provisional pair:** chosen `3` > rejected `1`; absolute token gap **0**. Not independently approved.

### Source 3287 — PROVISIONAL_APPROVE

**Question:** Jason is hiring two construction workers, one electrician and one plumber. If the construction workers each make $100/day, the electrician makes double what a worker is paid and the plumber makes 250% of a worker's salary, how much are the overall labor costs for one day?

**Frozen reference:** `650`

**Group assessment:** Samples 0 and 3 correctly sum two workers $200, electrician $200, plumber $250, total $650.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`145`, extracted answer=`650`. Two laborers $200, electrician $200, plumber $250; sum $650.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`68`, extracted answer=`550`. Counts only one $100/day construction worker, giving $550.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`153`, extracted answer=`850`. Correctly computes $200 worker wages and $450 specialist wages, then adds the electrician $200 a second time.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`131`, extracted answer=`650`. Two construction workers $200, electrician $200, plumber $250; total $650.

**Provisional pair:** chosen `0` > rejected `2`; absolute token gap **8**. Not independently approved.

## Review limits and authorization boundary

- This is a mathematical/semantic assistant review of the uploaded report, **not** an external independent mathematical certification.
- Original grader labels and extracted strings are quoted and preserved; disputed cases require separately versioned adjudication if changed.
- Source 1927 samples 0 and 3 are incomplete 256-token-cap outputs, so they are not negatives despite being answer-incorrect.
- Correct-final-answer completions with false or contradictory arithmetic are not elevated to SOUND by their labels.
- All pair proposals require independent human review and explicit approval before inclusion; no training is authorized.
- No official GSM8K test data or GPU inference was used in this review.
