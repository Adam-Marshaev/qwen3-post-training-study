# E003 — Batch 03 Mathematical Reasoning Audit (Advisory v1)

**Source review SHA256:** `3b7ecb8904c5bfabb11e713ef03cd9f36752bb9e16d462fe843c8784d5821993`  

**Source selection SHA256:** `f4d7a86d3e7883079b4807d77271dbed244de4e14f0c3bb0375fcb25ea76b79c`  

**Frozen candidates SHA256:** `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`  

**Status:** advisory only; no independent pair signoff and no training permission.

## Screening Summary

- Sources screened: **20**; original completions: **80**.
- Provisional approvals: **15**; HOLD: **5**.
- Reasoning verdict counts: **{'BORDERLINE': 4, 'CONDITIONAL': 5, 'FLAWED': 34, 'SOUND': 37}**.
- Median proposed pair length gap: **6**; maximum: **29**.

## Group-by-group decisions

### Source 4775 — PROVISIONAL_APPROVE

**Prompt:** In 7 years, Kaylee will be 3 times as old as Matt is now. If Matt is currently 5 years old, how old is Kaylee now?

**Original reference:** `8`  
**Proposed pair:** 0 → 2 (gap 25)

**Audit:** Kaylee will be 15 in seven years, hence 8 now. Sample 2 subtracts seven years twice; sample 3 uses Matt’s future age rather than his current age.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 42 | SOUND |
| 1 | True | True | True | 42 | SOUND |
| 2 | False | True | True | 67 | FLAWED |
| 3 | False | True | True | 89 | FLAWED |

### Source 4821 — PROVISIONAL_APPROVE

**Prompt:** Joanie wants to join a gym to get into shape. The gym costs $12 per month and has a $50 down payment. How much will she need to pay for the first 3 years?

**Original reference:** `482`  
**Proposed pair:** 0 → 2 (gap 3)

**Audit:** 36 monthly fees total $432 plus one $50 down payment. Sample 2 charges the down payment annually; sample 3 omits the down payment.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 90 | SOUND |
| 1 | True | True | True | 98 | SOUND |
| 2 | False | True | True | 93 | FLAWED |
| 3 | False | True | True | 68 | FLAWED |

### Source 4830 — PROVISIONAL_APPROVE

**Prompt:** Martha spends 10 minutes turning the router off and on again, six times that long on hold with Comcast, and half as much time as she spent on hold yelling at a customer service representative. How much time did Martha spend on these activities total?

**Original reference:** `100`  
**Proposed pair:** 1 → 0 (gap 11)

**Audit:** Total must include 10 minutes troubleshooting, 60 waiting, and 30 yelling. Sample 0 omits the initial 10 minutes.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 61 | FLAWED |
| 1 | True | True | True | 72 | SOUND |
| 2 | True | True | True | 81 | SOUND |
| 3 | True | True | True | 88 | SOUND |

### Source 4847 — PROVISIONAL_APPROVE

**Prompt:** Lucy plans to purchase potato chips for a party. Ten people will be at the party, including Lucy. The potato chips cost 25 cents per pound. How much will Lucy pay (in dollars) for the potato chips if she wants each person to get 1.2 pounds?

**Original reference:** `3`  
**Proposed pair:** 2 → 3 (gap 6)

**Audit:** Ten people need 12 pounds total costing 300 cents. Sample 0 confusingly says EACH person gets 12 pounds, though it then calculates the correct total; sample 3 divides by price rather than multiplying correctly.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 85 | BORDERLINE |
| 1 | True | True | True | 63 | SOUND |
| 2 | True | True | True | 69 | SOUND |
| 3 | False | True | True | 75 | FLAWED |

- **Sample 0 (BORDERLINE):** Claims each of 10 guests gets 12 pounds, then correctly prices 12 pounds total; material quantity-label inconsistency.

### Source 4949 — HOLD

**Prompt:** Françoise sells pots of lily of the valley to fund humanitarian work. She buys them at €12 each and sells them at a 25% higher cost. How much will she give back to the association by selling 150 pots of lily of the valley?

**Original reference:** `450`  
**Proposed pair:** None; HOLD

**Audit:** The reference 450 is the markup profit (€3 per pot × 150), whereas samples 0–2 report €2250 gross revenue. Wording “give back to the association” never specifies whether the charity receives gross proceeds or profit; hold reference interpretation.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 101 | FLAWED |
| 1 | False | True | True | 67 | FLAWED |
| 2 | False | True | True | 68 | FLAWED |
| 3 | True | True | True | 112 | CONDITIONAL |

- **Sample 3 (CONDITIONAL):** Correct as net sales profit, but payment to association is not explicitly limited to profit.

### Source 4997 — PROVISIONAL_APPROVE

**Prompt:** In 2004, there were 60 kids at a cookout. In 2005, half the number of kids came to the cookout as compared to 2004. In 2006, 2/3 as many kids came to the cookout as in 2005. How many kids came to the cookout in 2006?

**Original reference:** `20`  
**Proposed pair:** 2 → 3 (gap 12)

**Audit:** 2005 attendance is 30 and 2006 attendance is 20. Sample 3 halves the 2004 value twice and then divides by three.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 57 | SOUND |
| 1 | True | True | True | 89 | SOUND |
| 2 | True | True | True | 87 | SOUND |
| 3 | False | True | True | 75 | FLAWED |

### Source 5008 — PROVISIONAL_APPROVE

**Prompt:** A gumball machine has red, green, and blue gumballs. The machine has half as many blue gumballs as red gumballs. For each blue gumball, the machine has 4 times as many green gumballs. If the machine has 16 red gumballs how many gumballs are in the machine?

**Original reference:** `56`  
**Proposed pair:** 3 → 1 (gap 2)

**Audit:** There are 16 red, 8 blue, and 32 green gumballs. Sample 1 counts only eight red gumballs instead of sixteen.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 99 | SOUND |
| 1 | False | True | True | 70 | FLAWED |
| 2 | True | True | True | 66 | SOUND |
| 3 | True | True | True | 72 | SOUND |

### Source 5064 — HOLD

**Prompt:** Jackson is laying tile in a courtyard that measures 10 feet by 25 feet. He needs 4 tiles per square foot of space. 40% of the tiles are green marble that costs $3/tile, and the rest are red tile that costs $1.50/tile. How much does he pay total for tile?

**Original reference:** `2100`  
**Proposed pair:** None; HOLD

**Audit:** Correct total is 400×$3 + 600×$1.50 = $2100. Sample 1 calls 400 “the total number of green and red tiles” despite 1000 overall; sample 3 writes the mathematically false chained equality 40/100 = .40×1000 = 400. Both correct-label derivations have material contradictions.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 128 | FLAWED |
| 1 | True | True | True | 130 | BORDERLINE |
| 2 | False | True | True | 189 | FLAWED |
| 3 | True | True | True | 214 | BORDERLINE |

- **Sample 1 (BORDERLINE):** States 400 is combined count of red and green tiles; correct counts are 400 green and 600 red.

- **Sample 3 (BORDERLINE):** Writes a false chained equality 40/100=.40*1000=400, although subsequent costs are correct.

### Source 5200 — PROVISIONAL_APPROVE

**Prompt:** Bryan bought 5 t-shirts and 4 pairs of pants for $1500. If a t-shirt costs $100, how much does each pair of pants cost?

**Original reference:** `250`  
**Proposed pair:** 2 → 1 (gap 6)

**Audit:** Five shirts cost $500; four pants cost $1000, or $250 each. Sample 0 fails to divide by four pairs; sample 1 double-counts the $1500 total.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 118 | FLAWED |
| 1 | False | True | True | 82 | FLAWED |
| 2 | True | True | True | 76 | SOUND |
| 3 | True | True | True | 76 | SOUND |

### Source 5341 — PROVISIONAL_APPROVE

**Prompt:** Mark is 5 feet 3 inches tall and Mike is 6 feet and 1 inch tall. How much taller is Mike than Mark in inches if 1 foot is equal to 12 inches?

**Original reference:** `10`  
**Proposed pair:** 2 → 3 (gap 2)

**Audit:** Mike is 73 inches tall and Mark is 63 inches tall. Sample 3 miscalculates Mark’s conversion as 69 inches.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 72 | SOUND |
| 1 | True | True | True | 62 | SOUND |
| 2 | True | True | True | 96 | SOUND |
| 3 | False | True | True | 94 | FLAWED |

### Source 5509 — PROVISIONAL_APPROVE

**Prompt:** A box of rainbow nerds contains 10 purple candies, 4 more yellow candies, and 2 fewer green candies than yellow candies. How many rainbow nerds are there in the box?

**Original reference:** `36`  
**Proposed pair:** 3 → 2 (gap 8)

**Audit:** Yellow = 14, green = 12, purple = 10. Sample 2 takes two fewer green candies than purple, not yellow.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 59 | SOUND |
| 1 | True | True | True | 93 | SOUND |
| 2 | False | True | True | 76 | FLAWED |
| 3 | True | True | True | 68 | SOUND |

### Source 5599 — HOLD

**Prompt:** When doing her exercises, Mairead runs for 40 miles, walks for 3/5 times as many miles as she ran, and walks for five times the number of miles she jogged. Calculate the total distance Mairead has covered while doing her exercises.

**Original reference:** `184`  
**Proposed pair:** None; HOLD

**Audit:** Problem defines “walks” twice, first as 3/5 of running and then as five times jogging, but supplies no jogging distance. Sample 2 assumes the 24-mile walking distance also equals jogging distance; this is not stated. Hold the source rather than invent a correction.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 76 | FLAWED |
| 1 | False | True | True | 82 | FLAWED |
| 2 | True | True | True | 104 | CONDITIONAL |
| 3 | False | True | True | 94 | FLAWED |

- **Sample 2 (CONDITIONAL):** Assumes the missing jogging distance is 24 miles; wording does not establish this.

### Source 5611 — PROVISIONAL_APPROVE

**Prompt:** The outdoor scouts went on a hike to see a waterfall. To get to the hike, the club members took 3 cars, 6 taxis and 2 vans. There were 4 people in each car, 6 people in each taxis and 5 people in each van. How many people went on the hike?

**Original reference:** `58`  
**Proposed pair:** 0 → 2 (gap 2)

**Audit:** 3×4 + 6×6 + 2×5 = 58. Sample 2 double-counts an extra six people.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 94 | SOUND |
| 1 | True | True | True | 128 | SOUND |
| 2 | False | True | True | 96 | FLAWED |
| 3 | True | True | True | 117 | SOUND |

### Source 5625 — PROVISIONAL_APPROVE

**Prompt:** Hannah is buying some apples for $5 per kilogram. If she would get a 40% discount on each kilogram of apples, how much would she pay for 10 kilograms of them?

**Original reference:** `30`  
**Proposed pair:** 1 → 2 (gap 1)

**Audit:** 40% off $5 means $3/kg, $30 for 10 kg. Sample 2 erroneously evaluates 5−(5×40%) as $2.50.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 47 | SOUND |
| 1 | True | True | True | 64 | SOUND |
| 2 | False | True | True | 63 | FLAWED |
| 3 | True | True | True | 100 | SOUND |

### Source 5656 — HOLD

**Prompt:** Every day in a week, Siena bookmarks 30 website pages from the research she does on her browser. If Siena has 400 bookmarked pages on her bookmarks library now, how many pages will she have in her bookmarks library at the end of March?

**Original reference:** `1330`  
**Proposed pair:** None; HOLD

**Audit:** 31 March days ×30 bookmarks +400 =1330 only if the current 400 bookmarks are counted before March begins. The question gives no “now” date, so the number of future bookmarking days is unspecified.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 89 | CONDITIONAL |
| 1 | False | True | True | 189 | FLAWED |
| 2 | False | True | True | 231 | FLAWED |
| 3 | False | True | True | 87 | FLAWED |

- **Sample 0 (CONDITIONAL):** Assumes 400 existing bookmarks counted before the beginning of March, though the current date is unspecified.

### Source 5679 — PROVISIONAL_APPROVE

**Prompt:** Kelly puts string cheeses in her kids lunches 5 days per week.  Her oldest wants 2 every day and her youngest will only eat 1.  The packages come with 30 string cheeses per pack.  How many packages of string cheese will Kelly need to fill her kids lunches for 4 weeks?

**Original reference:** `2`  
**Proposed pair:** 1 → 0 (gap 2)

**Audit:** Both children consume three cheeses per day, five days/week, four weeks =60 cheeses, or two packs. Sample 0 divides weekly total by five again and then misapplies the four-week multiplier.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 147 | FLAWED |
| 1 | True | True | True | 149 | SOUND |
| 2 | True | True | True | 84 | SOUND |
| 3 | True | True | True | 78 | SOUND |

### Source 5721 — PROVISIONAL_APPROVE

**Prompt:** Chenny has 10 pieces of candies to be given out to her friends. She realized that she needs to buy 4 more so each of her friends will receive 2 candies. How many friends does Chenny have?

**Original reference:** `7`  
**Proposed pair:** 2 → 1 (gap 17)

**Audit:** Four added candies yield 14, shared two per friend, hence seven friends. Sample 0 says seven “pieces of candy each” rather than seven friends, but sample 2 is unambiguous. Samples 1 and 3 invent additional candy.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 54 | BORDERLINE |
| 1 | False | True | True | 54 | FLAWED |
| 2 | True | True | True | 37 | SOUND |
| 3 | False | True | True | 70 | FLAWED |

- **Sample 0 (BORDERLINE):** Correct quotient seven but says each friend receives seven pieces of candy instead of two.

### Source 5727 — PROVISIONAL_APPROVE

**Prompt:** Jack is making flower crowns out of red, pink and white daisies. There are nine times as many pink daisies as white daisies and three less than four times as many red daisies as pink daisies. If there are 6 white daisies, how many daisies are there total?

**Original reference:** `273`  
**Proposed pair:** 0 → 1 (gap 29)

**Audit:** White 6; pink 54; red 213; total 273. Sample 2 reverses the pink/red labels despite the same numerical total. Sample 1 substitutes division by three for the red count.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 86 | SOUND |
| 1 | False | True | True | 57 | FLAWED |
| 2 | True | True | True | 138 | FLAWED |
| 3 | True | True | True | 105 | SOUND |

- **Sample 2 (FLAWED):** Reverses pink and red counts while accidentally preserving the combined sum.

### Source 5741 — PROVISIONAL_APPROVE

**Prompt:** Keesha wants to get her hair and nails done for prom.  Hair updos cost $50 and manicures cost $30.  How much will these two services cost her with a 20% tip for each beautician?

**Original reference:** `96`  
**Proposed pair:** 1 → 2 (gap 29)

**Audit:** Base services $80 plus tips $10 and $6 give $96. Sample 0 adds the tips twice; sample 2 calculates the tip multiple times.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 155 | FLAWED |
| 1 | True | True | True | 115 | SOUND |
| 2 | False | True | True | 144 | FLAWED |
| 3 | True | True | True | 68 | SOUND |

### Source 5775 — HOLD

**Prompt:** There are 30 spaces for each vehicle in a parking lot. A caravan takes up a total of 2 spaces of parking space. How many vehicles can still park if there are 3 caravans currently parking?

**Original reference:** `24`  
**Proposed pair:** None; HOLD

**Audit:** The intended arithmetic treats 30 as the TOTAL lot capacity and three caravans as consuming six spaces. However “There are 30 spaces for each vehicle in a parking lot” is poorly specified, not explicitly 30 total spaces. Retain on HOLD for prompt clarification.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 53 | CONDITIONAL |
| 1 | True | True | True | 73 | CONDITIONAL |
| 2 | False | True | True | 52 | FLAWED |
| 3 | False | True | True | 76 | FLAWED |

- **Sample 0 (CONDITIONAL):** Interprets the ambiguous “30 spaces for each vehicle” as exactly 30 parking spaces in total.

- **Sample 1 (CONDITIONAL):** Assumes the lot has 30 spaces in total though wording says “for each vehicle”.

## Interpretation and safeguards

These review decisions are assistant advisory assessments, not independent human signoff. Only source-level proposals meeting eligible, native-EOS, SOUND-chosen, FLAWED-rejected, and originally-correct-versus-incorrect constraints are proposed. Ties use the lowest chosen then rejected sample index.

HOLD groups are excluded from pair proposals. No model training or optimizer update occurred. No original candidate or reference labels have been modified.
