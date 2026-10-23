# E003 — Batch 04 Mathematical Reasoning Audit (Advisory v1)

**Source review SHA256:** `409fd7f8e51e29b874b2a75f056eeb489ca5455a180c321738ca239c595239f8`  

**Source selection SHA256:** `815b976c8e92acdd155f7aaffa26fa9d73f229656f3c5d29712caf4a863734c6`  

**Frozen candidates SHA256:** `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`  

**Status:** advisory only; no independent pair signoff and no training permission.

## Screening Summary

- Sources screened: **20**; original completions: **80**.
- Provisional approvals: **17**; HOLD: **3**.
- Reasoning verdict counts: **{'BORDERLINE': 7, 'FLAWED': 40, 'SOUND': 33}**.
- Median proposed pair length gap: **7**; maximum: **57**.

## Group-by-group decisions

### Source 5819 — PROVISIONAL_APPROVE

**Prompt:** Casey is pumping water out of her well. She can pump 3 gallons a minute. She has 4 rows of 15 corn plants each, and each plant needs half a gallon of water. She also has 10 pigs, which each need 4 gallons of water, and 20 ducks that each need a quarter of a gallon of water. How many minutes does Casey need to spend pumping water?

**Original reference:** `25`  
**Proposed pair:** 3 → 2 (gap 4)

**Audit:** Crops require 30 gallons, pigs 40, ducks 5; 75 gallons ÷ 3 per minute =25 minutes. Sample 2 confuses water volume and time and multiplies crop use by the pumping rate.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 201 | SOUND |
| 1 | True | True | True | 134 | SOUND |
| 2 | False | True | True | 116 | FLAWED |
| 3 | True | True | True | 120 | SOUND |

### Source 5828 — PROVISIONAL_APPROVE

**Prompt:** Clyde's four children wanted to go see their favorite band perform.  The tickets were expensive so Clyde made a deal with his kids.  If the average of their scores on their next math test was higher than 89, then he would buy them tickets to the concert.   June earned a 97 on her math test, Patty earned an 85, Josh earned a 100 on his test and Henry earned a 94.  What was their average math test score?

**Original reference:** `94`  
**Proposed pair:** 0 → 2 (gap 47)

**Audit:** The four test scores add to 376, average 94. Sample 2 creates 16 alleged scores and nonsensical arithmetic.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 58 | SOUND |
| 1 | True | True | True | 48 | SOUND |
| 2 | False | True | True | 105 | FLAWED |
| 3 | True | True | True | 51 | SOUND |

### Source 5851 — HOLD

**Prompt:** Gilbert, the bearded dragon, eats 4 crickets per week when the temperature averages 90 degrees F per day, but he eats twice as many crickets per week when the temperature averages 100 degrees F.  How many crickets will he eat over 15 weeks if the temperature averages 90 degrees F for 80% of the time, and 100 degrees F for the remainder of the time?

**Original reference:** `72`  
**Proposed pair:** None; HOLD

**Audit:** Twelve weeks at 4 crickets and three weeks at 8 yield 72. Sample 1 arrives at 72 by weighted-average arithmetic but calls 4×0.8=3.2 “weeks” and multiplies by 15 as “crickets per week”; the unit and derivation are contradictory. Only answer-correct sample is unsound.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 187 | FLAWED |
| 1 | True | True | True | 199 | FLAWED |
| 2 | False | True | True | 147 | FLAWED |
| 3 | False | True | True | 177 | FLAWED |

- **Sample 1 (FLAWED):** Treats weighted average crickets per week as “weeks” and then as per-week counts; correct result is not reliably derived.

### Source 5870 — HOLD

**Prompt:** Keaton has a farm of oranges and apples. He can harvest his oranges every 2 months and can sell the harvest for $50.  He can harvest his apples every 3 months and can sell this harvest for $30. How much money can Keaton earn every year?

**Original reference:** `420`  
**Proposed pair:** None; HOLD

**Audit:** Six orange harvests yield $300 and four apple harvests yield $120. Correct-label sample 0 repeatedly labels apple harvests as oranges; sample 1 states “6 oranges” and “4 apples” rather than six and four harvests. Retain on HOLD under strict reasoning-quality standards.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 230 | BORDERLINE |
| 1 | True | True | True | 107 | BORDERLINE |
| 2 | False | True | True | 93 | FLAWED |
| 3 | False | True | True | 99 | FLAWED |

- **Sample 0 (BORDERLINE):** Labels apple-harvest frequency and income repeatedly as oranges, contradicting the question.

- **Sample 1 (BORDERLINE):** Calls six and four harvest events “oranges” and “apples”; inaccurate units of count.

### Source 5885 — PROVISIONAL_APPROVE

**Prompt:** As Dan is learning to screen-print t-shirts to sell at the craft fair, he makes t-shirts, over the first hour, at the rate of one every 12 minutes. Then, in the second hour, he makes one at the rate of every 6 minutes. How many t-shirts does he make over the course of those two hours?

**Original reference:** `15`  
**Proposed pair:** 1 → 3 (gap 57)

**Audit:** Sixty minutes per hour yields 5 shirts then 10 shirts, total 15. Sample 0 mislabels produced-shirt counts as hours; samples 1 and 2 are sound. Sample 3 multiplies rather than divides time by production interval.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 92 | FLAWED |
| 1 | True | True | True | 65 | SOUND |
| 2 | True | True | True | 61 | SOUND |
| 3 | False | True | True | 122 | FLAWED |

- **Sample 0 (FLAWED):** Calls 5 and 10 shirts “hours of work”; wrong dimensional description despite correct total.

### Source 5903 — PROVISIONAL_APPROVE

**Prompt:** The coffee shop sold 8 more than four times the number of lattes as it did teas. If 6 teas were sold how many lattes did the coffee shop sell?

**Original reference:** `32`  
**Proposed pair:** 2 → 1 (gap 7)

**Audit:** Four times six teas plus eight extra lattes gives 32. Sample 1 evaluates 4×6+8 incorrectly as 28.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 25 | SOUND |
| 1 | False | True | True | 54 | FLAWED |
| 2 | True | True | True | 47 | SOUND |
| 3 | True | True | True | 47 | SOUND |

### Source 5980 — PROVISIONAL_APPROVE

**Prompt:** Chuck breeds dogs.  He has 3 pregnant dogs.  They each give birth to 4 puppies.  Each puppy needs 2 shots and each shot costs $5.  How much did the shots cost?

**Original reference:** `120`  
**Proposed pair:** 1 → 2 (gap 15)

**Audit:** Three dogs produce twelve puppies, each needs two $5 shots, total $120. Sample 3 wrongly says each dog produced twelve puppies; sample 2 doubles shots required per puppy.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 51 | SOUND |
| 1 | True | True | True | 62 | SOUND |
| 2 | False | True | True | 77 | FLAWED |
| 3 | True | True | True | 55 | BORDERLINE |

- **Sample 3 (BORDERLINE):** Claims each mother dog has 4×3=12 puppies; twelve is the count across all three dogs.

### Source 5994 — HOLD

**Prompt:** Dani has 3 cats; Binkie, Frankie and Spaatz.  Each cat has a collar decorated with gemstones.  Binkie has four times as many gemstones on his collar as does Frankie but Spaatz has two less than half as many gemstones on her collar as does Frankie.  If Spaatz has 1 Gemstone on her collar, how many gemstones does Binkie have on his collar?

**Original reference:** `24`  
**Proposed pair:** None; HOLD

**Audit:** If Spaatz has one and is two fewer than half of Frankie, then 1 = F/2−2 and F=6, Binkie=24. Sole correct sample 1 instead derives F using unsupported 2×2+2, ignoring the given one gemstone; no valid derivation is supplied.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 78 | FLAWED |
| 1 | True | True | True | 84 | FLAWED |
| 2 | False | True | True | 75 | FLAWED |
| 3 | False | True | True | 100 | FLAWED |

- **Sample 1 (FLAWED):** Equation 2×2+2=6 ignores the supplied one gemstone and is not derived from 1=F/2−2.

### Source 6000 — PROVISIONAL_APPROVE

**Prompt:** If it takes 8 days for 3 builders to build a cottage. How long will it take 6 builders to build the same size cottage working at the same rate?

**Original reference:** `4`  
**Proposed pair:** 2 → 0 (gap 3)

**Audit:** Cottage requires 3×8=24 builder-days; six builders require four days. Incorrect samples invert the worker-time relationship.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 72 | FLAWED |
| 1 | True | True | True | 60 | SOUND |
| 2 | True | True | True | 69 | SOUND |
| 3 | False | True | True | 37 | FLAWED |

### Source 6006 — PROVISIONAL_APPROVE

**Prompt:** Jose had 400 tabs opened up in his windows browser. After about one hour of browsing, he closed 1/4 of the tabs to allows easy browsing. He read some news from different pages, then closed 2/5 of the remaining tabs. If he closed half of the remaining tabs after further analyzing some pages, how many windows tabs did he have remaining open?

**Original reference:** `90`  
**Proposed pair:** 3 → 2 (gap 7)

**Audit:** After successive closures 300, then 180, then 90 tabs remain. Sample 1 says “closed 180/2=90 tabs remaining open,” a contradictory operation/result, whereas sample 3 is unambiguous. Sample 2 forgets to remove the 120 tabs closed at step two.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 129 | FLAWED |
| 1 | True | True | True | 94 | BORDERLINE |
| 2 | False | True | True | 135 | FLAWED |
| 3 | True | True | True | 142 | SOUND |

- **Sample 1 (BORDERLINE):** Says it “closed 180/2=90 tabs remaining open”; contradicts the meaning of closed versus remaining.

### Source 6015 — PROVISIONAL_APPROVE

**Prompt:** 3 years ago James turned 27.  In 5 years Matt will be twice James age.  How old is Matt now?

**Original reference:** `65`  
**Proposed pair:** 3 → 1 (gap 1)

**Audit:** James is 30 now, 35 in five years; Matt will then be 70 and is currently 65. Wrong samples confuse the ages and multiply/divide in the wrong direction.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 108 | FLAWED |
| 1 | False | True | True | 65 | FLAWED |
| 2 | False | True | True | 51 | FLAWED |
| 3 | True | True | True | 66 | SOUND |

### Source 6030 — PROVISIONAL_APPROVE

**Prompt:** A car driving cross-country traveled 180 miles in 4 hours. At this rate of speed, how many miles further will the car travel in the next 3 hours?

**Original reference:** `135`  
**Proposed pair:** 0 → 1 (gap 1)

**Audit:** Speed 180/4 =45 mph, next three hours give 135 miles. Sample 1 states 180/4=480.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 59 | SOUND |
| 1 | False | True | True | 58 | FLAWED |
| 2 | True | True | True | 57 | SOUND |
| 3 | True | True | True | 54 | SOUND |

### Source 6047 — PROVISIONAL_APPROVE

**Prompt:** Kyle bakes 60 cookies and 32 brownies. Kyle eats 2 cookies and 2 brownies. Kyle's mom eats 1 cookie and 2 brownies. If Kyle sells a cookie for $1 and a brownie for $1.50, how much money will Kyle make if he sells all of his baked goods?

**Original reference:** `99`  
**Proposed pair:** 0 → 2 (gap 33)

**Audit:** Sell 57 cookies and 28 brownies: $57+$42=$99. All incorrect samples omit consumed items or subtract counts incorrectly.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 135 | SOUND |
| 1 | False | True | True | 94 | FLAWED |
| 2 | False | True | True | 168 | FLAWED |
| 3 | False | True | True | 217 | FLAWED |

### Source 6103 — PROVISIONAL_APPROVE

**Prompt:** Tim has 22 cans of soda. Jeff comes by, and takes 6 cans of soda from Tim. Tim then goes and buys another half the amount of soda cans he had left. How many cans of soda does Tim have in the end?

**Original reference:** `24`  
**Proposed pair:** 3 → 0 (gap 8)

**Audit:** After losing six cans Tim has sixteen; he purchases eight and ends with 24. Samples 1–2 misattribute removal to Tim rather than Jeff, while sample 3 correctly describes it. Sample 0 subtracts purchased soda.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 90 | FLAWED |
| 1 | True | True | True | 90 | BORDERLINE |
| 2 | True | True | True | 76 | BORDERLINE |
| 3 | True | True | True | 82 | SOUND |

- **Sample 1 (BORDERLINE):** Says Tim took the six cans to Jeff, while Jeff actually took them from Tim.

- **Sample 2 (BORDERLINE):** Says Tim takes the six cans, whereas Jeff is the actor.

### Source 6159 — PROVISIONAL_APPROVE

**Prompt:** A restaurant is counting their sales for the day. They sold 10 meals at $8 each, 5 meals at $10 each, and 20 meals at $4 each. In dollars, how much money did the restaurant make throughout the day?

**Original reference:** `210`  
**Proposed pair:** 2 → 1 (gap 2)

**Audit:** Revenue $80+$50+$80=$210. Incorrect samples carry out the item multiplications but add them incorrectly.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 111 | FLAWED |
| 1 | False | True | True | 105 | FLAWED |
| 2 | True | True | True | 107 | SOUND |
| 3 | True | True | True | 90 | SOUND |

### Source 6190 — PROVISIONAL_APPROVE

**Prompt:** Angela slept 6.5 hours every night in December. She decided she should get more sleep and began sleeping 8.5 hours a night in January. How much more sleep did Angela get in January?

**Original reference:** `62`  
**Proposed pair:** 0 → 2 (gap 54)

**Audit:** January and December each have 31 days; sleeping 2 additional hours per night gives 62 more monthly hours. Samples 1–2 only report the difference per night, not the requested January total.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 82 | SOUND |
| 1 | False | True | True | 24 | FLAWED |
| 2 | False | True | True | 28 | FLAWED |
| 3 | True | True | True | 109 | SOUND |

### Source 6194 — PROVISIONAL_APPROVE

**Prompt:** Matt and Blake want to watch every episode of the show The Office. There are 201 episodes. If they watch 1 episode every Monday and 2 episodes every Wednesday each week, how many weeks will it take them to watch the whole series?

**Original reference:** `67`  
**Proposed pair:** 0 → 3 (gap 16)

**Audit:** Three episodes/week over 201 episodes gives 67 weeks. Incorrect samples misread the schedule or use the wrong divisor.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 84 | SOUND |
| 1 | False | True | True | 63 | FLAWED |
| 2 | False | True | True | 126 | FLAWED |
| 3 | False | True | True | 100 | FLAWED |

### Source 6204 — PROVISIONAL_APPROVE

**Prompt:** The Tigers played 56 home games this year. They had 12 losses and half as many ties. How many games did they win?

**Original reference:** `38`  
**Proposed pair:** 1 → 3 (gap 0)

**Audit:** Six ties and twelve losses leave 38 wins out of 56. Sample 0 calls the 18 nonwins “losses” rather than losses plus ties. Sample 1 is sound; incorrect samples miscount ties/wins.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 50 | BORDERLINE |
| 1 | True | True | True | 71 | SOUND |
| 2 | False | True | True | 48 | FLAWED |
| 3 | False | True | True | 71 | FLAWED |

- **Sample 0 (BORDERLINE):** Calls twelve losses plus six ties “losses”, rather than non-wins.

### Source 6208 — PROVISIONAL_APPROVE

**Prompt:** One batch of cookies requires 4 cups of flour and 1.5 cups of sugar. How many cups of flour and sugar combined would be needed for 8 batches?

**Original reference:** `44`  
**Proposed pair:** 0 → 3 (gap 1)

**Audit:** Eight cookie batches each need 4+1.5=5.5 cups total, hence 44. Sample 3 invents a factor of three.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 56 | SOUND |
| 1 | True | True | True | 88 | SOUND |
| 2 | True | True | True | 101 | SOUND |
| 3 | False | True | True | 55 | FLAWED |

### Source 6239 — PROVISIONAL_APPROVE

**Prompt:** Vlad is 6 feet, 3 inches tall. His younger sister is 2 feet, 10 inches tall. How many inches taller is Vlad than his sister?

**Original reference:** `41`  
**Proposed pair:** 1 → 0 (gap 20)

**Audit:** Vlad is 75 inches, sister 34 inches, difference 41. Sample 0 ignores the extra inches. Sample 2 is truncated and ineligible; do not pair with it.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 63 | FLAWED |
| 1 | True | True | True | 83 | SOUND |
| 2 | False | False | False | 256 | FLAWED |
| 3 | True | True | True | 87 | SOUND |

## Interpretation and safeguards

These review decisions are assistant advisory assessments, not independent human signoff. Only source-level proposals meeting eligible, native-EOS, SOUND-chosen, FLAWED-rejected, and originally-correct-versus-incorrect constraints are proposed. Ties use the lowest chosen then rejected sample index.

HOLD groups are excluded from pair proposals. No model training or optimizer update occurred. No original candidate or reference labels have been modified.
