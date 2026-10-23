# E003 Batch 02 — Mathematical reasoning audit (advisory v1)

> **Assistant advisory screen only.** No independent human pair signoff; no reference change, dataset construction, or DPO/GRPO training authorization.

## Provenance

- Frozen E003 candidate dataset SHA256: `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`
- Uploaded Batch 02 review SHA256: `b238ae97a6c1e6a0c657f9961606bc9ad7866e963c767fab5630f5506e84a54e`
- Uploaded Batch 02 selection SHA256: `5dd9ded0613103844c318428eb53ebc04eaab4dc26418ba1b943fafd6c18503a`
- Population: 20 source indices, four original completions each; labels and generated text unchanged.
- Source indices: 3419, 3530, 3631, 3674, 3785, 3948, 3992, 4067, 4151, 4156, 4168, 4200, 4275, 4317, 4320, 4446, 4456, 4499, 4500, 4674

## Summary

- Advisory recommendation: **17 PROVISIONAL APPROVE**, **3 HOLD**, **0 EXCLUDE**.
- All **80 completions** screened; reasoning counts: **BORDERLINE: 3**, **FLAWED: 48**, **SOUND: 29**.
- Proposed pairs: **17**; median absolute length gap **8 tokens**, maximum **53 tokens**.
- Human adjudication required: **3631** (coincidental correct answer via invalid pairs arithmetic), **4151** (inaccurate mixed-item wording in sole answer-correct response), **4456** (school-versus-class weekly paper usage contradiction).
- Parser QA: source **4456 sample 2** extracted answer `6` while the full final answer in the report is `6 2/7`; it remains answer-incorrect.
- Length-bias QA: source **3419 gap 53** and source **4200 gap 41** should be separately checked against any future dataset-level length threshold.

## Pair proposals (advisory only)

| Source | Verdict | Chosen → Rejected | Gap (tokens) | Key concern |
|---:|---|---|---:|---|
| 3419 | PROVISIONAL_APPROVE | 3 → 1 | 53 | Reference $5: red pairs cost $12; remaining $30 divided by six blue pairs. |
| 3530 | PROVISIONAL_APPROVE | 0 → 1 | 34 | Weekly pay 5 days ×4 hours ×$5=$100; 3/4 is $75. |
| 3631 | HOLD | — | — | The only answer-matching candidate (sample 3) incorrectly says the already-owned three shoes equal nine, then conflates number of shoes with number of pairs. |
| 3674 | PROVISIONAL_APPROVE | 1 → 3 | 8 | Let female F; male F+4; 2F+4=120 gives F=58, male=62. |
| 3785 | PROVISIONAL_APPROVE | 0 → 1 | 14 | For three equally weighted tests, target total 270 percentage points; first two sum to 175, leaving minimum 95%. |
| 3948 | PROVISIONAL_APPROVE | 3 → 2 | 0 | Clean and jerk 80×2=160 kg; snatch 50×1.8=90 kg; total 250 kg. |
| 3992 | PROVISIONAL_APPROVE | 1 → 0 | 11 | The two smaller harbors hold 160 lb; Hooper holds twice their combined amount (320); three harbors total 480. |
| 4067 | PROVISIONAL_APPROVE | 1 → 2 | 8 | Ferris wheel 3×$5=$15; merry-go-round 5×$3=$15; ice cream 5×2×$8=$80; total $110. |
| 4151 | HOLD | — | — | The only answer-matching sample describes the 20 items as “cans and bottles together” but values all 20 at the can weight. |
| 4156 | PROVISIONAL_APPROVE | 2 → 3 | 11 | Needed top-ups are 20−10=10 truck gallons plus 12−4=8 car gallons, totaling 18. |
| 4168 | PROVISIONAL_APPROVE | 1 → 3 | 6 | Jimmy 81 lb, Adam 60 lb, Rachel 75 lb; mean (81+60+75)/3=72 lb. |
| 4200 | PROVISIONAL_APPROVE | 1 → 0 | 41 | Alexis’s 60 is four times Dilan and Ashley combined, so the two together have 15; full total 75. |
| 4275 | PROVISIONAL_APPROVE | 1 → 2 | 3 | Mary 5×$600=$3000, Scott $3000/3=$1000; total $4600 exceeds the goal by $600. |
| 4317 | PROVISIONAL_APPROVE | 3 → 1 | 6 | Last month 4 books, this month 8; both months together 12. |
| 4320 | PROVISIONAL_APPROVE | 0 → 2 | 2 | Mural area 6×3=18 m²; paint $72, 12 labor hours at $10=$120; total $192. |
| 4446 | PROVISIONAL_APPROVE | 2 → 1 | 1 | Deposit is $20 flat +10 adults×$3 +2 children×$1=$52. |
| 4456 | HOLD | — | — | The sole answer-matching completion explicitly says the SCHOOL uses 200×5=1000 sheets weekly, though 1000 is the amount per CLASS. |
| 4499 | PROVISIONAL_APPROVE | 0 → 3 | 29 | Current weekly wage $80; new weekly wage $60+$35=$95 given bonus assumption; difference $15. |
| 4500 | PROVISIONAL_APPROVE | 1 → 3 | 3 | $300 becomes six $50 bills and $700 becomes seven $100 bills, hence 13 bills. |
| 4674 | PROVISIONAL_APPROVE | 1 → 2 | 2 | Five feet six inches is 66 inches, plus six inches growth =72. |

## Mathematical review — all original completions

### Source 3419 — PROVISIONAL_APPROVE

**Question:** Luis needed to buy some socks. He bought 4 pairs of red socks and 6 pairs of blue ones. In total, he spent $42. If the red socks cost $3 each, how much did he pay for each blue pair?

**Frozen reference:** `5`

**Group assessment:** Reference $5: red pairs cost $12; remaining $30 divided by six blue pairs. All three correct-labelled responses have valid arithmetic.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`54`, extracted answer=`5`. 4×$3=$12; ($42−$12)/6=$5.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`112`, extracted answer=`2`. Invents blue-pair price from $12−$3, confuses expenditures and gets $2 without a coherent constraint.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`54`, extracted answer=`5`. Correctly subtracts red costs and divides $30 by six blue pairs.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`59`, extracted answer=`5`. Correct 12,30,5 calculation with matching units.

**Provisional pair:** chosen `3` > rejected `1`; absolute token gap **53**. Not independently approved.

### Source 3530 — PROVISIONAL_APPROVE

**Question:** Walter works 5 days a week in a fast-food chain and earns $5 per hour. Since he is a working student, he can only work 4 hours a day and allocates 3/4 of his weekly earning for his schooling. How much does he allocate for school?

**Frozen reference:** `75`

**Group assessment:** Weekly pay 5 days ×4 hours ×$5=$100; 3/4 is $75.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`75`, extracted answer=`75`. $20 per day, $100 per week, three-quarters=$75.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`41`, extracted answer=`15`. Treats one day’s $20 pay as the entire weekly paycheck; ignores five days.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`83`, extracted answer=`75`. 20 hours/week ×$5/hour=$100; schooling=$75.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`89`, extracted answer=`75`. Correct total weekly hours and 3/4 allocation.

**Provisional pair:** chosen `0` > rejected `1`; absolute token gap **34**. Not independently approved.

### Source 3631 — HOLD

**Question:** Codger is a three-footed sloth.  He has a challenging time buying shoes because the stores only sell the shoes in pairs. If he already owns the 3-piece set of shoes he is wearing, how many pairs of shoes does he need to buy to have 5 complete 3-piece sets of shoes?

**Frozen reference:** `6`

**Group assessment:** The only answer-matching candidate (sample 3) incorrectly says the already-owned three shoes equal nine, then conflates number of shoes with number of pairs. The correct derivation is (5×3−3)/2=6 pairs; no SOUND chosen exists.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`94`, extracted answer=`16`. Falsely calls one three-shoe set four shoe pairs, then extrapolates to 16 pairs.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`61`, extracted answer=`9`. Correctly needs 15 shoes but subtracts six already owned instead of three and treats nine shoes as nine pairs.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`64`, extracted answer=`12`. Finds 12 additional shoes but calls that 12 pairs instead of six pairs.
- **Sample 3** — **FLAWED**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`57`, extracted answer=`6`. Coincidentally answers six, but 3×3=9 shoes already owned contradicts three; 15−9=6 is shoes, not pairs.

**No pair proposed:** HOLD pending project-owner decision.

### Source 3674 — PROVISIONAL_APPROVE

**Question:** At a UFO convention, there are 120 conference attendees. If there are 4 more male attendees than female attendees, how many male attendees are there?

**Frozen reference:** `62`

**Group assessment:** Let female F; male F+4; 2F+4=120 gives F=58, male=62.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`81`, extracted answer=`64`. Solves equal genders then adds four instead of incorporating the difference into 120.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`115`, extracted answer=`62`. Correct equations F+M=120 and M=F+4 give M=62.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`72`, extracted answer=`116`. Treats 4+F=120 and wrongly assigns 116 males, discarding female attendees.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`107`, extracted answer=`64`. First assumes equal male/female counts then adds four without adjusting total.

**Provisional pair:** chosen `1` > rejected `3`; absolute token gap **8**. Not independently approved.

### Source 3785 — PROVISIONAL_APPROVE

**Question:** Kat gets a 95% on her first math test and an 80% on her second math test. If she wants an average grade of at least 90% in her math class, what does she need to get on her third final math test?

**Frozen reference:** `95`

**Group assessment:** For three equally weighted tests, target total 270 percentage points; first two sum to 175, leaving minimum 95%.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`62`, extracted answer=`95`. 3×90−(95+80)=95, correctly answers minimum third-test score.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`76`, extracted answer=`90`. Miscomputes first-two-test average and simply assigns the target mean 90 to the final test.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`116`, extracted answer=`125`. Invents a 50-point scale and has multiple incorrect calculations.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`79`, extracted answer=`270`. Computes required total 270 but incorrectly identifies 270 as the third test result.

**Provisional pair:** chosen `0` > rejected `1`; absolute token gap **14**. Not independently approved.

### Source 3948 — PROVISIONAL_APPROVE

**Question:** John started weightlifting when he was 16.  When he first started he could Clean & Jerk 80 kg and he could Snatch 50 kg.  He manages to double his clean and jerk and increase his snatch by 80%.  What is his new combined total lifting capacity?

**Frozen reference:** `250`

**Group assessment:** Clean and jerk 80×2=160 kg; snatch 50×1.8=90 kg; total 250 kg.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`73`, extracted answer=`250`. Correct doubling and 80% increase yield 160+90=250.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`88`, extracted answer=`250`. Correctly multiplies snatch by 1.8 and combines with doubled lift.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`76`, extracted answer=`290`. Claims 50+0.8×50=130 (actual 90); misreports combined capacity.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`76`, extracted answer=`250`. Correct 160+90=250 calculation.

**Provisional pair:** chosen `3` > rejected `2`; absolute token gap **0**. Not independently approved.

### Source 3992 — PROVISIONAL_APPROVE

**Question:** Hooper Bay has twice as many pounds of lobster than the two other harbors combined. If the other two harbors have 80 pounds of lobster each, how many pounds of lobster are the three harbors holding?

**Frozen reference:** `480`

**Group assessment:** The two smaller harbors hold 160 lb; Hooper holds twice their combined amount (320); three harbors total 480.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`103`, extracted answer=`640`. Misstates Hooper inventory and double-counts subtotal, obtaining 640.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`92`, extracted answer=`480`. 80+80=160, double it for Hooper=320, then add for total 480.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`50`, extracted answer=`320`. Assigns only 160 lb to Hooper and gives 320 total.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`54`, extracted answer=`320`. Calculates twice the smaller-harbors subtotal but omits their 160 lb from the full total.

**Provisional pair:** chosen `1` > rejected `0`; absolute token gap **11**. Not independently approved.

### Source 4067 — PROVISIONAL_APPROVE

**Question:** A group of 5 children are taken to an amusement park. Only 3 of them were daring enough to get on the Ferris wheel which cost $5 per child. Everyone had a go at the merry-go-round (at $3 per child). On their way home, they bought 2 cones of ice cream each (each cone cost $8). How much did they spend altogether?

**Frozen reference:** `110`

**Group assessment:** Ferris wheel 3×$5=$15; merry-go-round 5×$3=$15; ice cream 5×2×$8=$80; total $110.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`103`, extracted answer=`120`. Interchanges number of children and price, then assigns ice-cream charges without using $8 per cone.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`89`, extracted answer=`110`. Correct contributions $15+$15+$80=$110.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`81`, extracted answer=`34`. Uses 2×2 for ice-cream cost, ignoring five children and $8 per cone.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`81`, extracted answer=`60`. Prices ice cream as twice $15, not five children × two cones ×$8.

**Provisional pair:** chosen `1` > rejected `2`; absolute token gap **8**. Not independently approved.

### Source 4151 — HOLD

**Question:** Jenny collects cans and bottles to take down to the recycling center. Each bottle weighs 6 ounces and each can weighs 2 ounces. Jenny can carry a total of 100 ounces. She collects 20 cans and as many bottles as she can carry. If she gets paid 10 cents per bottle and 3 cents per can, how much money does she make (in cents)?

**Frozen reference:** `160`

**Group assessment:** The only answer-matching sample describes the 20 items as “cans and bottles together” but values all 20 at the can weight. The intended computation uses 20 cans, 40 ounces, 10 bottles, and 160 cents; preserve as BORDERLINE for an independent semantic review.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`131`, extracted answer=`4`. Mixes ounces, dollars, and cents; invents 30 cans from the available bottle mass.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`89`, extracted answer=`780`. Treats ounce counts as item counts and multiplies them by redemption amounts.
- **Sample 2** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`116`, extracted answer=`160`. Numerically computes 20×2=40 ounces, 60/6=10 bottles, 100+60=160 cents; incorrectly calls 20 a combined count of “cans and bottles” instead of 20 cans.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`162`, extracted answer=`135`. Treats a can+bottle as an eight-ounce unit, mislabels twenty cans, and allows fractional bottles.

**No pair proposed:** HOLD pending project-owner decision.

### Source 4156 — PROVISIONAL_APPROVE

**Question:** Wendy's truck has a gas tank that can hold 20 gallons. She also has a car with a gas tank that holds 12 gallons. The truck's tank is half full. The car's tank is 1/3 full. If she fills them both up completely, how many gallons does she add?

**Frozen reference:** `18`

**Group assessment:** Needed top-ups are 20−10=10 truck gallons plus 12−4=8 car gallons, totaling 18.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`79`, extracted answer=`6`. Subtracts combined initial gasoline from truck capacity alone, ignoring separate tank volumes.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`47`, extracted answer=`14`. Answers with gas already present (10+4), rather than gas needed to fill tanks.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`93`, extracted answer=`18`. Correctly evaluates remaining capacity in each tank: 10+8=18 gallons.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`82`, extracted answer=`14`. Computes initial combined fill (14 gallons), not required added gallons.

**Provisional pair:** chosen `2` > rejected `3`; absolute token gap **11**. Not independently approved.

### Source 4168 — PROVISIONAL_APPROVE

**Question:** Rachel weighs 75 pounds, 6 pounds less than Jimmy and 15 pounds more than Adam. What is the average weight of the three people, in pounds?

**Frozen reference:** `72`

**Group assessment:** Jimmy 81 lb, Adam 60 lb, Rachel 75 lb; mean (81+60+75)/3=72 lb.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`111`, extracted answer=`96`. Misassigns difference constraints and double-counts weights, giving 96.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`91`, extracted answer=`72`. Correctly derives both other weights and arithmetic mean 72.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`71`, extracted answer=`135`. Adds the two differences incorrectly, computes Jimmy’s weight wrongly, and omits division by three.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`85`, extracted answer=`122`. Reassigns Rachel’s weight to Jimmy and falsely states 222/3=122.

**Provisional pair:** chosen `1` > rejected `3`; absolute token gap **6**. Not independently approved.

### Source 4200 — PROVISIONAL_APPROVE

**Question:** Alexis has four times as many mangoes as Dilan and Ashley combined. If Alexis has 60 mangoes, how many mangoes does all of them have combined?

**Frozen reference:** `75`

**Group assessment:** Alexis’s 60 is four times Dilan and Ashley combined, so the two together have 15; full total 75.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`112`, extracted answer=`135`. Obtains correct intermediate 75 for all three and then adds Alexis’s 60 again.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`71`, extracted answer=`75`. 60/4=15; combined 60+15=75.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`39`, extracted answer=`75`. Succinct correct calculation of 15+60=75.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`119`, extracted answer=`15`. Sets up the combined unknown incorrectly and reports only the smaller pair’s 15.

**Provisional pair:** chosen `1` > rejected `0`; absolute token gap **41**. Not independently approved.

### Source 4275 — PROVISIONAL_APPROVE

**Question:** Scott, Mary, and Ken committed to raising $4,000 for their local children’s cancer hospital. Right now, Mary’s collection is five times what Ken has, but three times Scott’s funds. If Ken has $600, by how much have the three exceeded their goal?

**Frozen reference:** `600`

**Group assessment:** Mary 5×$600=$3000, Scott $3000/3=$1000; total $4600 exceeds the goal by $600.

- **Sample 0** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`126`, extracted answer=`600`. Adds an irrelevant and unfounded reference to $1 coins in an unused x variable; all subsequent calculations are correct.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`109`, extracted answer=`600`. Correctly computes Mary=3000, Scott=1000, excess=600.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`106`, extracted answer=`0`. Omits Ken’s $600 from the total despite correctly computing Mary and Scott.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`137`, extracted answer=`600`. All three fund totals and excess are correctly derived.

**Provisional pair:** chosen `1` > rejected `2`; absolute token gap **3**. Not independently approved.

### Source 4317 — PROVISIONAL_APPROVE

**Question:** For this month, Lily wants to finish reading twice as many books as she finished last month. If she finished reading 4 books last month, what will be the total number of books that she will finish for two months?

**Frozen reference:** `12`

**Group assessment:** Last month 4 books, this month 8; both months together 12.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`47`, extracted answer=`12`. Finds 2×4=8 this month; 4+8=12 total.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`62`, extracted answer=`16`. Applies the doubling to both months and calls each eight books.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`44`, extracted answer=`12`. Correct compact 8+4=12 calculation.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`68`, extracted answer=`12`. Correctly distinguishes last month from this month and adds.

**Provisional pair:** chosen `3` > rejected `1`; absolute token gap **6**. Not independently approved.

### Source 4320 — PROVISIONAL_APPROVE

**Question:** John paints a giant mural that is 6m by 3m. The paint costs $4 per square meter. The artist can paint 1.5 square meters per hour and charges $10 per hour. How much does the mural cost?

**Frozen reference:** `192`

**Group assessment:** Mural area 6×3=18 m²; paint $72, 12 labor hours at $10=$120; total $192.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`87`, extracted answer=`192`. Computes 18 area, $72 paint, 12 hours, $120 labor, $192 total; “m*square meter” is imprecise unit typography.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`83`, extracted answer=`168`. Multiplies $4/m² by 12 labor hours rather than 18 m².
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`89`, extracted answer=`168`. Repeats the confusion between painting time and paint-area charge.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`172`, extracted answer=`34622`. Combines paint cost with hourly rate, invents 48 hours and reports a vastly inflated figure.

**Provisional pair:** chosen `0` > rejected `2`; absolute token gap **2**. Not independently approved.

### Source 4446 — PROVISIONAL_APPROVE

**Question:** Hans reserved a table at a fine dining restaurant for twelve people. He has to pay a deposit for the reservation, and the deposit is a flat $20 plus an extra $3 per adult but only $1 per child. Two of the people in Hans’s party are his kid cousins, and the rest are adults. How many dollars does Hans have to pay as a deposit for the restaurant reservation?

**Frozen reference:** `52`

**Group assessment:** Deposit is $20 flat +10 adults×$3 +2 children×$1=$52.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`225`, extracted answer=`36`. Invents free food/drinks charges and never calculates reservation deposit as specified.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`78`, extracted answer=`50`. Computes base plus adult charge but omits two children at $1 each.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`79`, extracted answer=`52`. Correctly counts ten adults and two children; total $20+$30+$2=$52.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`46`, extracted answer=`50`. Omits the child-specific deposit charge.

**Provisional pair:** chosen `2` > rejected `1`; absolute token gap **1**. Not independently approved.

### Source 4456 — HOLD

**Question:** Each class uses 200 sheets of paper per day. The school uses a total of 9000 sheets of paper every week. If there are 5 days of school days, how many classes are there in the school?

**Frozen reference:** `9`

**Group assessment:** The sole answer-matching completion explicitly says the SCHOOL uses 200×5=1000 sheets weekly, though 1000 is the amount per CLASS. The correct division is shown but relies on an unstated correction to the mislabeled premise.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`70`, extracted answer=`45`. Correctly computes nine classes per day then changes to 9000/200=45, dropping the five-day factor.
- **Sample 1** — **BORDERLINE**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`68`, extracted answer=`9`. Correct 200×5=1000 sheets per CLASS per week, then 9000/1000=9, but explicitly calls 1000 the SCHOOL weekly usage.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`110`, extracted answer=`6`. Introduces seven days, a false calculation of weeks, and fractional class counts.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`114`, extracted answer=`1`. Claims 5×7=35 days in a week, giving invalid school paper totals.

**No pair proposed:** HOLD pending project-owner decision.

### Source 4499 — PROVISIONAL_APPROVE

**Question:** Maisy has been offered a new job and now has the option of continuing to work at her current job or take the new job. Her current job is 8 hours a week with a wage of $10 per hour. The new job is offering 4 hours a week with a wage of $15 per hour with an additional bonus of $35 per week if she exceeds her quota. Maisy is confident that she will exceed her quota and decides to include this when calculating her wage at the new job. How much more money, in dollars, will Maisy earn at her new job?

**Frozen reference:** `15`

**Group assessment:** Current weekly wage $80; new weekly wage $60+$35=$95 given bonus assumption; difference $15.

- **Sample 0** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`68`, extracted answer=`15`. Correctly compares $80 versus $95 including intended bonus and finds $15 increase.
- **Sample 1** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`124`, extracted answer=`55`. Assigns new-job bonus to current wages and reverses subtraction.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`147`, extracted answer=`30`. Invents an extra fifth hour at the new job, inflating weekly pay.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`97`, extracted answer=`50`. Adds $35 bonus to hourly rate and current earnings without calculating new-job pay.

**Provisional pair:** chosen `0` > rejected `3`; absolute token gap **29**. Not independently approved.

### Source 4500 — PROVISIONAL_APPROVE

**Question:** Uncle Bradley has a $1000 bill that he wants to change into smaller bills so he could give them to his nieces and nephews. He wants to change 3/10 of the money into $50 bills while the rest into $100 bills. How many pieces of bills will Uncle Bradley have in all?

**Frozen reference:** `13`

**Group assessment:** $300 becomes six $50 bills and $700 becomes seven $100 bills, hence 13 bills.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`143`, extracted answer=`1000`. Correctly calculates six and seven bills but answers the original dollar amount ($1000) rather than number of bills.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`195`, extracted answer=`13`. Correctly calculates 300/50=6 bills, 700/100=7 bills, total 13.
- **Sample 2** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`127`, extracted answer=`13`. All counts correct; minor dollar-sign notation preceding bill counts does not change the result.
- **Sample 3** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`198`, extracted answer=`15`. Subtracts six bills instead of $300 from $1000 and uses an incoherent 940/100 calculation.

**Provisional pair:** chosen `1` > rejected `3`; absolute token gap **3**. Not independently approved.

### Source 4674 — PROVISIONAL_APPROVE

**Question:** Steve is 5'6".  He grows 6 inches.  How tall is he in inches?

**Frozen reference:** `72`

**Group assessment:** Five feet six inches is 66 inches, plus six inches growth =72.

- **Sample 0** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`31`, extracted answer=`24`. Incorrectly converts five feet six inches into 18 inches and reports 24.
- **Sample 1** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`42`, extracted answer=`72`. 5×12+6=66, plus 6=72 inches.
- **Sample 2** — **FLAWED**; original correct=`false`, eligible=`true`, native EOS=`true`, tokens=`44`, extracted answer=`78`. Erroneously multiplies a six-inch growth by 12, then adds it inconsistently.
- **Sample 3** — **SOUND**; original correct=`true`, eligible=`true`, native EOS=`true`, tokens=`53`, extracted answer=`72`. Correctly converts feet and inches, then adds six inches growth.

**Provisional pair:** chosen `1` > rejected `2`; absolute token gap **2**. Not independently approved.

## Review limits and authorization boundary

- This is a mathematical/semantic assistant review of the uploaded report, **not** independent mathematical certification.
- Original answer labels, original candidate texts and extracted-answer strings are unchanged; no source reference erratum is proposed.
- Correct-final-answer completions with false or contradictory reasoning do not become SOUND by matching the reference.
- All pair proposals require independent approval before inclusion; no DPO or GRPO training is authorized.
- No official GSM8K test data or GPU inference was used in this review.
