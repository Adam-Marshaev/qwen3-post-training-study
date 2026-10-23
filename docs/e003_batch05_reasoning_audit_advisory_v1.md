# E003 — Batch 05 Mathematical Reasoning Audit (Advisory v1)

**Source review SHA256:** `dad81c72689b50432a8bb9a701e9c7fff378ac0ab37cafe8a7c1b990e24114df`  

**Source selection SHA256:** `4e123050a9cc099dcc877068907449ce0f57f8e6532c4ef93f51e3c62ec9a682`  

**Frozen candidates SHA256:** `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`  

**Status:** advisory only; no independent pair signoff and no training permission.

## Screening Summary

- Sources screened: **20**; original completions: **80**.
- Provisional approvals: **19**; HOLD: **1**.
- Reasoning verdict counts: **{'BORDERLINE': 7, 'FLAWED': 33, 'SOUND': 40}**.
- Median proposed pair length gap: **7**; maximum: **112**.

## Group-by-group decisions

### Source 6288 — PROVISIONAL_APPROVE

**Prompt:** Alice is making a big stack of dishes to see how tall she can make it before it topples over and falls. She starts off by placing 27 plates on top of each other. The tower holds fine so she adds 37 more plates. She is in the process of placing more and more plates when it finally topples over and crashes down, all 83 plates. How many more was Alice able to add before the tower fell and crashed?

**Original reference:** `19`  
**Proposed pair:** 0 → 1 (gap 0)

**Audit:** Initial 27 plus 37 gives 64; tower falls at 83, so 19 were subsequently added. Incorrect samples add 83 as extra plates.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 71 | SOUND |
| 1 | False | True | True | 71 | FLAWED |
| 2 | True | True | True | 45 | SOUND |
| 3 | False | True | True | 40 | FLAWED |

### Source 6297 — PROVISIONAL_APPROVE

**Prompt:** Jordan decides to start an exercise program when he weighs 250 pounds.  For the first 4 weeks, he loses 3 pounds a week.  After that, he loses 2 pounds a week for 8 weeks.  How much does Jordan now weigh?

**Original reference:** `222`  
**Proposed pair:** 2 → 1 (gap 3)

**Audit:** Weight after 12 pounds then 16 pounds of loss: 250−12−16=222. Incorrect sample 1 gives 192 despite displaying the correct subtraction expression.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 91 | SOUND |
| 1 | False | True | True | 86 | FLAWED |
| 2 | True | True | True | 89 | SOUND |
| 3 | True | True | True | 103 | SOUND |

### Source 6354 — PROVISIONAL_APPROVE

**Prompt:** Nick is 13 years old. His sister is 6 years older and their brother is half their combined age. How old would their brother be in 5 years?

**Original reference:** `21`  
**Proposed pair:** 1 → 2 (gap 3)

**Audit:** Sister is 19, Nick 13, their ages total 32; brother is 16 now, 21 later. Sample 0 mislabels Nick as brother in one intermediate statement. Sample 2 subtracts the present age from his future age.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 89 | BORDERLINE |
| 1 | True | True | True | 81 | SOUND |
| 2 | False | True | True | 84 | FLAWED |
| 3 | True | True | True | 91 | SOUND |

- **Sample 0 (BORDERLINE):** Calls Nick and his sister “Nick’s sister and Nick’s brother”, misidentifying a participant.

### Source 6389 — PROVISIONAL_APPROVE

**Prompt:** Central Park had 8 more than half of the number of trash cans as in Veteran's Park.  Then one night, someone took half of the trash cans from Central Park and put them in Veteran's Park.  If originally there were 24 trash cans in Veteran's Park, how many trash cans are now in Veteran's Park?

**Original reference:** `34`  
**Proposed pair:** 3 → 2 (gap 14)

**Audit:** Veteran’s initially 24; Central has half of 24 plus 8 = 20; moving half adds ten, resulting in 34. Samples 0–1 incorrectly calculate 24/2+8 as 16 or use 20/2 as 8; sample 2 subtracts rather than adds.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 85 | FLAWED |
| 1 | False | True | True | 57 | FLAWED |
| 2 | False | True | True | 117 | FLAWED |
| 3 | True | True | True | 103 | SOUND |

### Source 6404 — PROVISIONAL_APPROVE

**Prompt:** Jimmy is at the candy store and buys 2 candy bars for $.75 each. He then buys 4 lollipops that cost $.25 each. He spent 1/6 of the money he earned from shoveling snow. If he charges $1.5 per driveway, how many driveways did he shovel?

**Original reference:** `10`  
**Proposed pair:** 2 → 3 (gap 1)

**Audit:** Two bars cost $1.50, four pops cost $1, spent $2.50 =1/6 earnings; earnings $15 across ten driveways. Sample 1 calls the $15 earnings “spent on candy,” whereas sample 2 correctly distinguishes spending and earnings.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 104 | FLAWED |
| 1 | True | True | True | 117 | BORDERLINE |
| 2 | True | True | True | 109 | SOUND |
| 3 | False | True | True | 110 | FLAWED |

- **Sample 1 (BORDERLINE):** Says Jimmy spent $15 on candy and lollipops when $15 is total earnings.

### Source 6417 — HOLD

**Prompt:** Harold makes $2500.00 a month from his job. His rent is $700.00, his car payment is $300.00, his utilities cost 1/2 the amount of his car payment and he spends $50.00 on groceries.  He wants to put half of the remaining money into a retirement account.  How much money will that leave him?

**Original reference:** `650`  
**Proposed pair:** None; HOLD

**Audit:** Expenses total $1200, remaining income $1300, and half is $650 after retirement contribution. Sole answer-correct sample 0 erroneously describes the $650 as money “left in his retirement account”, rather than money remaining outside the account. Its numerical result is coincidentally the same; HOLD for ambiguous referent.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 104 | BORDERLINE |
| 1 | False | True | True | 131 | FLAWED |
| 2 | False | True | True | 106 | FLAWED |
| 3 | False | True | True | 136 | FLAWED |

- **Sample 0 (BORDERLINE):** Calls $650 money left inside retirement account, though question asks money left after depositing half.

### Source 6485 — PROVISIONAL_APPROVE

**Prompt:** My age is five times that of my son. Next year, my son will be eight years old. How old am I now?

**Original reference:** `35`  
**Proposed pair:** 3 → 0 (gap 4)

**Audit:** Son is 7 today, parent is five times his age =35. Incorrect samples compute ages from next year instead of the present.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | False | True | True | 61 | FLAWED |
| 1 | True | True | True | 35 | SOUND |
| 2 | False | True | True | 94 | FLAWED |
| 3 | True | True | True | 57 | SOUND |

### Source 6515 — PROVISIONAL_APPROVE

**Prompt:** The total cost of staying at High Services Hotel is $40 per night per person. Jenny and two of her friends went to the hotel and stayed for three nights. What's the total amount of money they all paid together?

**Original reference:** `360`  
**Proposed pair:** 0 → 2 (gap 5)

**Audit:** Three people times three nights at $40/person/night = $360. Incorrect sample 2 counts four people.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 58 | SOUND |
| 1 | True | True | True | 47 | SOUND |
| 2 | False | True | True | 63 | FLAWED |
| 3 | True | True | True | 56 | SOUND |

### Source 6525 — PROVISIONAL_APPROVE

**Prompt:** Jared likes to draw monsters. He drew a monster family portrait. The mom had 1 eye and the dad had 3. They had 3 kids, each with 4 eyes. How many eyes did the whole family have?

**Original reference:** `16`  
**Proposed pair:** 3 → 2 (gap 4)

**Audit:** Mom one eye, dad three, three kids four each: 16. Sample 0 says both parents “each had 1 eye” despite summing one and three; sample 3 is sound. Sample 1 counts parents twice; sample 2 invents four kids.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 70 | BORDERLINE |
| 1 | False | True | True | 106 | FLAWED |
| 2 | False | True | True | 73 | FLAWED |
| 3 | True | True | True | 69 | SOUND |

- **Sample 0 (BORDERLINE):** Says both parents “each had 1 eye” although the father has 3.

### Source 6576 — PROVISIONAL_APPROVE

**Prompt:** Aaron is gathering can lids to take to the recycling center. He uses 3 equal-sized boxes of canned tomatoes and adds the lids he gets to the 14 can lids he already has. He is now taking 53 can lids to the recycling center. How many cans lids did he get from each box?

**Original reference:** `13`  
**Proposed pair:** 3 → 1 (gap 66)

**Audit:** From 53 lids subtract existing 14, divide remaining 39 over three boxes =13. Sample 2 poorly describes the subtraction but sample 0/3 is sound. Sample 1 adds boxes as individual lids.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 49 | SOUND |
| 1 | False | True | True | 132 | FLAWED |
| 2 | True | True | True | 51 | BORDERLINE |
| 3 | True | True | True | 66 | SOUND |

- **Sample 2 (BORDERLINE):** Describes remainder lids “from the can lids he got to the recycling center”, obscuring distinction between existing lids and new lids.

### Source 6655 — PROVISIONAL_APPROVE

**Prompt:** The three angles of a triangle add up to 180 degrees.  The largest angle is 5 times bigger than the smallest. The middle angle is 3 times bigger than the smallest. How many degrees is the smallest angle?

**Original reference:** `20`  
**Proposed pair:** 1 → 2 (gap 2)

**Audit:** Let smallest be S, then S+3S+5S=180, S=20. Incorrect sample 2 adds coefficients to 19 rather than 9.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 55 | SOUND |
| 1 | True | True | True | 78 | SOUND |
| 2 | False | True | True | 80 | FLAWED |
| 3 | True | True | True | 64 | SOUND |

### Source 6726 — PROVISIONAL_APPROVE

**Prompt:** The epic poem currently contains 24 lines. If a person adds 3 lines to the poem every month, in how many months will the poem contain 90 lines?

**Original reference:** `22`  
**Proposed pair:** 0 → 1 (gap 16)

**Audit:** Requires 90−24=66 new lines at three/month, or 22 months. Incorrect samples use starting count or target incorrectly.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 51 | SOUND |
| 1 | False | True | True | 35 | FLAWED |
| 2 | False | True | True | 117 | FLAWED |
| 3 | True | True | True | 91 | SOUND |

### Source 6804 — PROVISIONAL_APPROVE

**Prompt:** The sum of the three sides of a triangle is 50. The right side of the triangle is 2 cm longer than the left side. Find the value of the triangle base if the left side has a value of 12 cm.

**Original reference:** `24`  
**Proposed pair:** 1 → 2 (gap 14)

**Audit:** Right side 14, left side 12, base 50−26=24. Incorrect samples double-count the right side.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 71 | SOUND |
| 1 | True | True | True | 84 | SOUND |
| 2 | False | True | True | 98 | FLAWED |
| 3 | False | True | True | 117 | FLAWED |

### Source 6959 — PROVISIONAL_APPROVE

**Prompt:** Debelyn, Christel, and Andrena collect dolls. Debelyn had 20 dolls before she gave Andrena 2 dolls. Christel had 24 dolls before giving Andrena 5 dolls. After all the gifts, Andrena now has 2 more dolls  than Christel, how many more dolls does andrena have now than Debelyn?

**Original reference:** `3`  
**Proposed pair:** 0 → 1 (gap 4)

**Audit:** Debelyn now has 18; Christel has 19; Andrena has 21, so Andrena has three more. Sample 3 gives a contradictory temporary value 26 before correcting; sample 0 is sound.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 95 | SOUND |
| 1 | False | True | True | 91 | FLAWED |
| 2 | False | True | True | 129 | FLAWED |
| 3 | True | True | True | 102 | BORDERLINE |

- **Sample 3 (BORDERLINE):** Temporarily asserts Andrena has 26 dolls with no basis before correctly calculating 21.

### Source 7189 — PROVISIONAL_APPROVE

**Prompt:** There are 11 boys and 13 girls in a class. If 1 boy is added to the class, what percentage of the class are girls?

**Original reference:** `52`  
**Proposed pair:** 2 → 3 (gap 39)

**Audit:** After a boy joins, class size is 25 and girls stay at 13: 52%. Sample 3 counts the new boy as a girl.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 73 | SOUND |
| 1 | True | True | True | 83 | SOUND |
| 2 | True | True | True | 98 | SOUND |
| 3 | False | True | True | 137 | FLAWED |

### Source 7210 — PROVISIONAL_APPROVE

**Prompt:** Peter is eating chips. Each chip is 10 calories. A bag has 24 chips and costs $2. If he wants to eat 480 calories, how much does he have to spend on chips?

**Original reference:** `4`  
**Proposed pair:** 0 → 3 (gap 17)

**Audit:** 24 chips at 10 calories =240 calories/bag, two bags for 480 calories, cost $4. Incorrect samples conflate price per bag and chips.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 95 | SOUND |
| 1 | True | True | True | 101 | SOUND |
| 2 | False | True | True | 118 | FLAWED |
| 3 | False | True | True | 78 | FLAWED |

### Source 7217 — PROVISIONAL_APPROVE

**Prompt:** The mayor commissioned two artists to paint 50 murals around the city. Once the work was completed, Celina was paid $1,000 more than 4 times the amount Diego got. If the mayor paid the two a total of $50,000, how much did Diego get?

**Original reference:** `9800`  
**Proposed pair:** 3 → 2 (gap 112)

**Audit:** Diego payment D obeys D+(4D+1000)=50000, giving D=9800. Incorrect sample 2 invents figures inconsistent with the total.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 106 | SOUND |
| 1 | True | True | True | 106 | SOUND |
| 2 | False | True | True | 236 | FLAWED |
| 3 | True | True | True | 124 | SOUND |

### Source 7251 — PROVISIONAL_APPROVE

**Prompt:** Melissa sells a coupe for $30,000 and an SUV for twice as much. If her commission is 2%, how much money did she make from these sales?

**Original reference:** `1800`  
**Proposed pair:** 0 → 1 (gap 39)

**Audit:** SUV sells for $60000 and coupe for $30000; 2% of $90000 gives $1800. Incorrect samples omit coupe or conflate commission percentage with currency.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 112 | SOUND |
| 1 | False | True | True | 151 | FLAWED |
| 2 | True | True | True | 100 | SOUND |
| 3 | False | True | True | 57 | FLAWED |

### Source 7259 — PROVISIONAL_APPROVE

**Prompt:** Sally sold 20 cups of lemonade last week. She sold 30% more lemonade this week. How many cups of lemonade did she sell in total for both weeks?

**Original reference:** `46`  
**Proposed pair:** 3 → 1 (gap 7)

**Audit:** 30% of 20 is six additional cups; this week 26, total 46. Sample 0 incorrectly says the six additional cups were sold last week; other correct candidates are sound.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 71 | BORDERLINE |
| 1 | False | True | True | 84 | FLAWED |
| 2 | True | True | True | 63 | SOUND |
| 3 | True | True | True | 91 | SOUND |

- **Sample 0 (BORDERLINE):** Attributes the extra six cups to last week instead of this week.

### Source 7284 — PROVISIONAL_APPROVE

**Prompt:** Talia is playing football with her friends. The park they're playing at is 5 miles from Talia's house. After their game, Talia is planning to go to the grocery store 3 miles away from the park and 8 miles from her home. Starting and ending at Talia's house, how many miles does Talia drive that day?

**Original reference:** `16`  
**Proposed pair:** 3 → 1 (gap 57)

**Audit:** Drive home→park 5, park→store 3, store→home 8, total 16 miles. Incorrect sample 1 double-counts part of the route.

| Sample | Original correct | Eligible | Native EOS | Tokens | Reasoning verdict |
|---:|:---:|:---:|:---:|---:|---|
| 0 | True | True | True | 61 | SOUND |
| 1 | False | True | True | 123 | FLAWED |
| 2 | True | True | True | 31 | SOUND |
| 3 | True | True | True | 66 | SOUND |

## Interpretation and safeguards

These review decisions are assistant advisory assessments, not independent human signoff. Only source-level proposals meeting eligible, native-EOS, SOUND-chosen, FLAWED-rejected, and originally-correct-versus-incorrect constraints are proposed. Ties use the lowest chosen then rejected sample index.

HOLD groups are excluded from pair proposals. No model training or optimizer update occurred. No original candidate or reference labels have been modified.
