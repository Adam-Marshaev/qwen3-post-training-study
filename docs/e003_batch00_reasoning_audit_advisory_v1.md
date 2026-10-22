# E003 M3.15 — Batch 00 reasoning-quality screen (advisory v1)

> **Not independent signoff; not training authorization.** This review preserves all original candidate answer labels and unmodified source data.

## Provenance

- Frozen original candidate SHA256: `3366d277c6ada2dd9a8469b3e3f870b020955e2464c60974e9db14ef57cb9bd4`
- Uploaded review report SHA256: `c510bce0ff9a2b637a48dc4094c687495e684adc144fbb065f6225488f30a4f8`
- Uploaded selection SHA256: `31dc2ee5a1984655718074acacda72ab7ce2cb559f23a3f49290354918ee5d2f`
- Scope: Batch 00 only, 20 questions, 80 original responses; 122 remaining groups are split into seven batches.
- Batch 00 original reference labels were **not** corrected or overwritten.

## Summary

- **18** provisional groups with a possible SOUND-over-FLAWED preference; **2** on HOLD; **0** excluded.
- Suggested pairs: **18**, median absolute token gap **7.0**, maximum **31**.
- Hold **303** because the sole correct-answer solution contains the explicit arithmetic error `4.8 + 1 = 5` and lacks a proof of minimum cost.
- Hold **1293** because the problem does not establish whether Jimmy and Irene are eligible for a senior-citizen discount.
- Note extraction/writeup inconsistencies in source **144 sample 2** (`10` versus `10 2/3`) and source **815 sample 3** (`10` versus `10/3`). These are wrong answers under either interpretation; preserve original automatic labels and flag for parser QA.
- **No proposed preference pair is independently approved.**

## Proposed batch results

| Source | Advisory outcome | Chosen → rejected | Absolute token gap | Comment |
|---:|---|---|---:|---|
| 81 | PROVISIONAL_APPROVE | 2 → 1 | 28 | Sound explanation exists; proposed negative misreads the third-round relation. |
| 144 | PROVISIONAL_APPROVE | 1 → 3 | 5 | Correctly converts each four-pound package to the remaining number of packages. |
| 158 | PROVISIONAL_APPROVE | 2 → 1 | 7 | Sound positive correctly accounts for first 12 days; negative adds an extra 12 miles. |
| 303 | HOLD | — | — | HOLD: only answer-correct response explicitly asserts false arithmetic “4.8 + 1 = 5” and omits a least-cost comparison. $50 itself is defensible; request independent tolerance decision or exclude under strict standard. |
| 376 | PROVISIONAL_APPROVE | 1 → 3 | 14 | Sound positive computes the requested difference; negative reports Suraya’s total. |
| 434 | PROVISIONAL_APPROVE | 0 → 1 | 10 | Positive uses 8/10 completed; negative inverts the fraction. |
| 468 | PROVISIONAL_APPROVE | 1 → 0 | 8 | Positive handles both jacket discount and tax; negative misapplies additional arithmetic to jacket cost. |
| 485 | PROVISIONAL_APPROVE | 3 → 0 | 4 | Positive computes the correct per-day pay; negative mistakes hours for days. |
| 528 | PROVISIONAL_APPROVE | 1 → 2 | 6 | Positive handles seven registrations; negative registers only four. Chosen has minor non-numeric noun slip (“trucks”). |
| 552 | PROVISIONAL_APPROVE | 1 → 0 | 28 | Positive computes usable square footage and divides by car footprint; negative multiplies instead. |
| 557 | PROVISIONAL_APPROVE | 0 → 2 | 7 | Positive properly subtracts sauce usage from tomatoes remaining after drying. |
| 755 | PROVISIONAL_APPROVE | 2 → 0 | 9 | Positive multiplies running speed by four; negative invents inconsistent extra distance. |
| 815 | PROVISIONAL_APPROVE | 2 → 3 | 6 | Positive correctly computes bracelet transfer and remaining count. Rejected final written fraction 10/3 differs from auto-extracted 10; both are wrong versus 6. |
| 853 | PROVISIONAL_APPROVE | 3 → 1 | 5 | Positive divides by toothpicks per box, not toothpicks per card. |
| 1150 | PROVISIONAL_APPROVE | 0 → 3 | 23 | Positive uses six working days; negative multiplies by seven days. |
| 1219 | PROVISIONAL_APPROVE | 1 → 0 | 3 | Positive includes three barbecue pieces per order; negative uses two. |
| 1293 | HOLD | — | — | HOLD: original question gives a discount for senior citizens without asserting either shopper is eligible. $117 is conditional on an unstated premise; no preference pair until adjudicated. |
| 1357 | PROVISIONAL_APPROVE | 2 → 1 | 4 | Positive correctly adds uncle’s gift; negative incorrectly treats it as expense. |
| 1429 | PROVISIONAL_APPROVE | 3 → 2 | 7 | Positive correctly amortizes desired total profit over all 200 units; negative adds aggregate profit to unit cost. |
| 1438 | PROVISIONAL_APPROVE | 2 → 3 | 31 | Positive applies four successive reductions; negative treats halving as an absolute daily subtraction. |

## Complete assessment of 80 completions

Definitions: **SOUND** means mathematically/materially correct; **FLAWED** means a substantive arithmetic or interpretation error; **BORDERLINE** indicates a correct-number response with material narration or calculation defects; **CONDITIONAL** requires an unstated eligibility premise. These labels are assistant-generated assessments.

### Source 81 — PROVISIONAL_APPROVE

**Question:** Sam and Jeff had a skipping competition at recess. The competition was split into four rounds. Sam completed 1 more skip than Jeff in the first round. Jeff skipped 3 fewer times than Sam in the second round. Jeff skipped 4 more times than Sam in the third round. Jeff got tired and only completed half the number of skips as Sam in the last round. If Sam skipped 16 times in each round, what is the average number of skips per round completed by Jeff?

**Original reference:** 14

**Group rationale:** Sound explanation exists; proposed negative misreads the third-round relation.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 121 | FLAWED | Reverses the first-round relation (17 rather than 15) and gives an invalid total/average equation. |
| 1 | Incorrect | 129 | FLAWED | Misreads the third round as half of Sam’s count instead of four more, giving 8 rather than 20. |
| 2 | Correct | 157 | SOUND | Jeff skips 15, 13, 20 and 8; sum 56 divided by four is 14. |
| 3 | Incorrect | 185 | FLAWED | Obtains 56/4=14 correctly but then divides the average by four again; also invents Sam’s round counts. |

**Advisory preference:** chosen sample 2 > rejected sample 1; absolute token gap 28. **Not independently approved.**

### Source 144 — PROVISIONAL_APPROVE

**Question:** The owner of a Turkish restaurant wanted to prepare traditional dishes for an upcoming celebration. She ordered ground beef, in four-pound packages, from three different butchers. The following morning, the first butcher delivered 10 packages. A couple of hours later, 7 packages arrived from the second butcher. Finally, the third butcher’s delivery arrived at dusk. If all the ground beef delivered by the three butchers weighed 100 pounds, how many packages did the third butcher deliver?

**Original reference:** 8

**Group rationale:** Correctly converts each four-pound package to the remaining number of packages.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 66 | FLAWED | Subtracts a package count from a weight, overlooking four pounds per package. |
| 1 | Correct | 81 | SOUND | 17 packages weigh 68 lb, leaving 32 lb or eight packages. |
| 2 | Incorrect | 133 | FLAWED | Assumes three third-butcher packages without evidence and infers each weighed 10⅔ lb; report-extracted answer 10 differs from written 10⅔. |
| 3 | Incorrect | 76 | FLAWED | Misstates first-two-butcher count as 25+7 and subtracts package counts from total weight. |

**Advisory preference:** chosen sample 1 > rejected sample 3; absolute token gap 5. **Not independently approved.**

### Source 158 — PROVISIONAL_APPROVE

**Question:** Jerome is taking a 150-mile bicycle trip. He wants to ride 12 miles for 12 days. How long will he ride on the 13th day to finish his goal?

**Original reference:** 6

**Group rationale:** Sound positive correctly accounts for first 12 days; negative adds an extra 12 miles.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 54 | SOUND | Twelve miles for 12 days totals 144 miles; six miles remain. |
| 1 | Incorrect | 80 | FLAWED | Finds six remaining miles but adds the original 12-mile daily target, obtaining 18. |
| 2 | Correct | 73 | SOUND | Computes 12×12=144 and subtracts from 150 to get six. |
| 3 | Correct | 44 | SOUND | Equivalent compact calculation 150−12×12=6. |

**Advisory preference:** chosen sample 2 > rejected sample 1; absolute token gap 7. **Not independently approved.**

### Source 303 — HOLD

**Question:** Tommy is making 12 loaves of bread. He needs 4 pounds of flour per loaf. A 10-pound bag of flour costs $10 and a 12-pound bag costs $13. When he is done making his bread, he has no use for flour and so he will throw away whatever is left. How much does he spend on flour if he buys the cheapest flour to get enough?

**Original reference:** 50

**Group rationale:** HOLD: only answer-correct response explicitly asserts false arithmetic “4.8 + 1 = 5” and omits a least-cost comparison. $50 itself is defensible; request independent tolerance decision or exclude under strict standard.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 164 | FLAWED | Confuses bag weights and prices and derives $88 through unrelated calculations. |
| 1 | Incorrect | 233 | FLAWED | Treats pounds per loaf as bags; inconsistent bag quantities and price arithmetic. |
| 2 | Incorrect | 198 | FLAWED | Uses an incorrect 144-lb requirement and several unsupported calculations. |
| 3 | Correct | 115 | BORDERLINE | Selects five 10-lb bags costing $50 (indeed optimal), but explicitly writes false arithmetic “4.8 + 1 = 5” and does not compare against 12-lb bags or mixed purchases. |

**Advisory preference:** none; review hold must be adjudicated before any pair construction.

### Source 376 — PROVISIONAL_APPROVE

**Question:** Suraya picked 12 apples more than Caleb, and Caleb picked 5 apples less than Kayla. If Kayla picked 20 apples, how many more apples did Suraya pick than Kayla?

**Original reference:** 7

**Group rationale:** Sound positive computes the requested difference; negative reports Suraya’s total.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 58 | SOUND | Caleb 15, Suraya 27; Suraya exceeds Kayla’s 20 by seven. |
| 1 | Correct | 50 | SOUND | Correct 20−5=15, 15+12=27, 27−20=7. |
| 2 | Correct | 53 | SOUND | Correct three-step comparison yielding seven. |
| 3 | Incorrect | 36 | FLAWED | Computes Suraya’s count 27 but fails to subtract Kayla’s 20. |

**Advisory preference:** chosen sample 1 > rejected sample 3; absolute token gap 14. **Not independently approved.**

### Source 434 — PROVISIONAL_APPROVE

**Question:** Calvin has been saving his hair clippings after each haircut to make a wig for his dog. He has gotten 8 haircuts and knows that he needs 2 more to reach his goal. What percentage towards his goal is he?

**Original reference:** 80

**Group rationale:** Positive uses 8/10 completed; negative inverts the fraction.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 79 | SOUND | Goal is 10 haircuts and 8/10=80% completed. |
| 1 | Incorrect | 69 | FLAWED | Inverts the completion fraction, using 10/8 instead of 8/10. |
| 2 | Incorrect | 68 | FLAWED | Mistakenly counts two haircuts still needed as already completed and miscalculates percentage. |
| 3 | Incorrect | 47 | FLAWED | Treats all ten needed haircuts as already completed and claims 100%. |

**Advisory preference:** chosen sample 0 > rejected sample 1; absolute token gap 10. **Not independently approved.**

### Source 468 — PROVISIONAL_APPROVE

**Question:** A shopping center sells T-shirts at $8 each, a sweater at $18,  and a jacket at $80. The jacket is on sale with a 10% discount. The sales tax is 5%.  Kevin wants to buy six T-shirts, four sweaters, and five jackets for his children. How much does Kevin have to pay for all the items, including the sales tax?

**Original reference:** 504

**Group rationale:** Positive handles both jacket discount and tax; negative misapplies additional arithmetic to jacket cost.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 198 | FLAWED | Correctly computes $360 discounted jackets, then treats 0.5 as tax, double counts costs, and sums incorrectly. |
| 1 | Correct | 190 | SOUND | Correctly discounts each jacket to $72 and applies 5% tax to $480 subtotal for $504. |
| 2 | Incorrect | 112 | FLAWED | Omits the advertised 10% jacket discount. |
| 3 | Incorrect | 145 | FLAWED | States an incorrect $64 discounted jacket price, then ignores discount in total and taxes $520. |

**Advisory preference:** chosen sample 1 > rejected sample 0; absolute token gap 8. **Not independently approved.**

### Source 485 — PROVISIONAL_APPROVE

**Question:** During the holidays, Lance works as a merchandiser. He works 35 hours a week, spread equally over 5 workdays. If Lance earns $9 an hour, how much does he make on each workday?

**Original reference:** 63

**Group rationale:** Positive computes the correct per-day pay; negative mistakes hours for days.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 36 | FLAWED | Mistakes workdays for hours, claiming $45 weekly pay instead of $315. |
| 1 | Correct | 43 | SOUND | Weekly earnings $9×35=$315, divided by five workdays gives $63. |
| 2 | Correct | 68 | SOUND | Seven hours per workday at $9 per hour gives $63. |
| 3 | Correct | 40 | SOUND | Weekly $315 over five days yields $63 per day. |

**Advisory preference:** chosen sample 3 > rejected sample 0; absolute token gap 4. **Not independently approved.**

### Source 528 — PROVISIONAL_APPROVE

**Question:** James buys 3 dirt bikes for $150 each and 4 off-road vehicles for $300 each.  It also cost him $25 to register each of these.  How much did he pay for everything?

**Original reference:** 1825

**Group rationale:** Positive handles seven registrations; negative registers only four. Chosen has minor non-numeric noun slip (“trucks”).

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 71 | FLAWED | Counts eight registrations instead of seven vehicles. |
| 1 | Correct | 126 | SOUND | 3×$150 + 4×$300 + 7×$25 = $1,825; calls the vehicles “trucks” once, a harmless noun slip. |
| 2 | Incorrect | 120 | FLAWED | Counts only four registration fees rather than seven. |
| 3 | Incorrect | 79 | FLAWED | Counts four registrations rather than seven. |

**Advisory preference:** chosen sample 1 > rejected sample 2; absolute token gap 6. **Not independently approved.**

### Source 552 — PROVISIONAL_APPROVE

**Question:** James paves a new parking lot.  It is 400 feet by 500 feet.  Only 80% of that is useable for parking.  It takes 10 square feet to park a car.  How many cars can be parked?

**Original reference:** 16000

**Group rationale:** Positive computes usable square footage and divides by car footprint; negative multiplies instead.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 135 | FLAWED | Multiplies usable parking area by 10 sq ft per car instead of dividing. |
| 1 | Correct | 107 | SOUND | 200,000 square feet, 160,000 usable, 16,000 cars. |
| 2 | Correct | 80 | SOUND | Correct area, 80% portion and division by ten. |
| 3 | Correct | 67 | SOUND | Correct compact area and capacity calculation. |

**Advisory preference:** chosen sample 1 > rejected sample 0; absolute token gap 28. **Not independently approved.**

### Source 557 — PROVISIONAL_APPROVE

**Question:** Andy harvests all the tomatoes from 18 plants that have 7 tomatoes each. If he dries half the tomatoes and turns a third of the remainder into marinara sauce, how many tomatoes are left?

**Original reference:** 42

**Group rationale:** Positive properly subtracts sauce usage from tomatoes remaining after drying.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 78 | SOUND | 126 tomatoes, dry 63, sauce uses 21 of remaining 63, leaving 42. |
| 1 | Correct | 89 | BORDERLINE | Correct 42 and usable arithmetic, but describes the 63 dried tomatoes as the tomatoes used for sauce, an internal narration inconsistency. |
| 2 | Incorrect | 71 | FLAWED | Computes one-third of the remaining 63 as 21 but treats that as the number left, not used for sauce. |
| 3 | Correct | 88 | SOUND | Correctly subtracts one-third of the 63 remaining tomatoes, leaving 42. |

**Advisory preference:** chosen sample 0 > rejected sample 2; absolute token gap 7. **Not independently approved.**

### Source 755 — PROVISIONAL_APPROVE

**Question:** Tom swims for 2 hours at a speed of 2 miles per hour.  He then runs for half the time at 4 times the speed.  How many miles did he cover?

**Original reference:** 12

**Group rationale:** Positive multiplies running speed by four; negative invents inconsistent extra distance.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 82 | FLAWED | Invents an additional running distance and has inconsistent multiplication and addition. |
| 1 | Incorrect | 106 | FLAWED | Uses 4 mph instead of four times the 2-mph swimming speed when running. |
| 2 | Correct | 91 | SOUND | Swims four miles and runs one hour at eight mph, totaling 12 miles. |
| 3 | Correct | 71 | SOUND | Correct swimming and running durations, speeds and distances. |

**Advisory preference:** chosen sample 2 > rejected sample 0; absolute token gap 9. **Not independently approved.**

### Source 815 — PROVISIONAL_APPROVE

**Question:** Bingley has 5 bracelets. Kelly gives Bingley a fourth of her 16 bracelets. Then Bingley gives a third of his bracelets to his little sister. How many bracelets does Bingley have remaining?

**Original reference:** 6

**Group rationale:** Positive correctly computes bracelet transfer and remaining count. Rejected final written fraction 10/3 differs from auto-extracted 10; both are wrong versus 6.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 69 | SOUND | Receives four bracelets, has nine, gives away three, retains six. |
| 1 | Correct | 71 | SOUND | Correct steps; minor pronoun error does not change the calculation. |
| 2 | Correct | 81 | SOUND | Correct one-fourth receipt and one-third donation. |
| 3 | Incorrect | 87 | FLAWED | Misapplies one-third of bracelets and obtains an impossible expression; extracted answer 10 differs from written fractional 10/3. |

**Advisory preference:** chosen sample 2 > rejected sample 3; absolute token gap 6. **Not independently approved.**

### Source 853 — PROVISIONAL_APPROVE

**Question:** Eugene built a model house out of toothpicks and a deck of playing cards.  For every card, he used 75 toothpicks.  The deck of playing cards had 52 cards, and Eugene used all but 16 of the cards to build his house.  If a box of toothpicks contains 450 toothpicks, how many boxes of toothpicks did Eugene use to create his model house?

**Original reference:** 6

**Group rationale:** Positive divides by toothpicks per box, not toothpicks per card.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 76 | SOUND | Uses 36 cards and 2,700 toothpicks, equal to six 450-toothpick boxes. |
| 1 | Incorrect | 67 | FLAWED | Divides 2,700 toothpicks by 75 per card instead of 450 per box. |
| 2 | Correct | 99 | SOUND | Correct 52−16, then multiply by 75 and divide by 450. |
| 3 | Correct | 72 | SOUND | Correct 36×75/450=6. |

**Advisory preference:** chosen sample 3 > rejected sample 1; absolute token gap 5. **Not independently approved.**

### Source 1150 — PROVISIONAL_APPROVE

**Question:** A driver travels 30 miles per hour for 3 hours and 25 miles per hour for 4 hours to deliver goods to a town every day from Monday to Saturday. How many miles does the driver travel in a week?

**Original reference:** 1140

**Group rationale:** Positive uses six working days; negative multiplies by seven days.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 117 | SOUND | Daily segments across six working days total 540+600=1,140 miles. |
| 1 | Incorrect | 86 | FLAWED | Computes an incorrect daily total of 165 miles and multiplies by seven rather than six days. |
| 2 | Incorrect | 230 | FLAWED | Incorrectly treats the two travel segments as occurring on alternating days. |
| 3 | Incorrect | 140 | FLAWED | Calculates 190 miles/day but multiplies by seven days, not Monday through Saturday (six). |

**Advisory preference:** chosen sample 0 > rejected sample 3; absolute token gap 23. **Not independently approved.**

### Source 1219 — PROVISIONAL_APPROVE

**Question:** Victor works at Clucks Delux, a restaurant specializing in chicken. An order of Chicken Pasta uses 2 pieces of chicken, an order of Barbecue Chicken uses 3 pieces of chicken, and a family-size Fried Chicken Dinner uses 8 pieces of chicken. Tonight, Victor has 2 Fried Chicken Dinner orders, 6 Chicken Pasta orders, and 3 Barbecue Chicken orders. How many pieces of chicken does he need for all the orders?

**Original reference:** 37

**Group rationale:** Positive includes three barbecue pieces per order; negative uses two.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 97 | FLAWED | Calculates barbecue chicken as 2×3 instead of 3×3, undercounting three pieces. |
| 1 | Correct | 94 | SOUND | Correct components 16, 12 and 9 sum to 37. |
| 2 | Correct | 104 | SOUND | Correct order counts and total 37. |
| 3 | Correct | 91 | SOUND | Correct counts of all three kinds of chicken orders. |

**Advisory preference:** chosen sample 1 > rejected sample 0; absolute token gap 3. **Not independently approved.**

### Source 1293 — HOLD

**Question:** Jimmy and Irene go shopping for clothes on a Tuesday, where senior citizens get a 10% discount on their purchases.  Jimmy picks out 3 shorts from the $15 rack.  Irene grabs 5 shirts from the $17 rack.  How much money do they give to the cashier?

**Original reference:** 117

**Group rationale:** HOLD: original question gives a discount for senior citizens without asserting either shopper is eligible. $117 is conditional on an unstated premise; no preference pair until adjudicated.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 46 | FLAWED | Computes undiscounted subtotal $130 without addressing the senior discount; whether it applies is unspecified. |
| 1 | Correct | 135 | CONDITIONAL | Computes $117 only IF both shoppers qualify as senior citizens; the source does not state their ages or eligibility. |
| 2 | Correct | 101 | CONDITIONAL | Correct discounted arithmetic assuming eligibility, not established by the question. |
| 3 | Correct | 103 | CONDITIONAL | Correct discounted arithmetic assuming eligibility, not established by the question. |

**Advisory preference:** none; review hold must be adjudicated before any pair construction.

### Source 1357 — PROVISIONAL_APPROVE

**Question:** Lizzy's mother gave her 80 cents and her father gave her 40 cents for keeping to her promise. She went to her uncle's and spent 50 cents buying candy for her little cousin. Her uncle gave her another 70 cents. How many cents does she have now?

**Original reference:** 140

**Group rationale:** Positive correctly adds uncle’s gift; negative incorrectly treats it as expense.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 79 | SOUND | Combines cents received and subtracts 50 cents to obtain 140. |
| 1 | Incorrect | 50 | FLAWED | Treats the uncle’s 70-cent gift as another expense. |
| 2 | Correct | 54 | SOUND | 80+40+70−50=140 cents. |
| 3 | Correct | 87 | SOUND | Correctly follows receipt, purchase and gift sequence to 140 cents. |

**Advisory preference:** chosen sample 2 > rejected sample 1; absolute token gap 4. **Not independently approved.**

### Source 1429 — PROVISIONAL_APPROVE

**Question:** Ronald wants to make profits by re-selling some phones he bought a week ago. He bought 200 units for just $3000, and he wants to gain a third of the initial investment in profits when all units are sold. Including the profit margin, what will be the selling price for each phone?

**Original reference:** 20

**Group rationale:** Positive correctly amortizes desired total profit over all 200 units; negative adds aggregate profit to unit cost.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Correct | 99 | BORDERLINE | Numerically computes $1,000 intended profit, $4,000 needed revenue and $20 each, but twice calls revenue “total profit.” |
| 1 | Correct | 112 | SOUND | Adds desired profit to original cost, divides $4,000 by 200 phones. |
| 2 | Incorrect | 83 | FLAWED | Miscomputes $3,000/200 as $150 and adds the entire $1,000 total profit to a per-unit price. |
| 3 | Correct | 76 | SOUND | Correct concise $3,000/3=$1,000 profit, $4,000 revenue, $20 per phone. |

**Advisory preference:** chosen sample 3 > rejected sample 2; absolute token gap 7. **Not independently approved.**

### Source 1438 — PROVISIONAL_APPROVE

**Question:** Bobby made a big batch of soup weighing 80 kg. Each day the batch gets reduced by half. How many kg will it reach on the fourth day after he made the soup?

**Original reference:** 5

**Group rationale:** Positive applies four successive reductions; negative treats halving as an absolute daily subtraction.

| Sample | Original correctness | Tokens | Verdict | Review rationale |
|---:|---|---:|---|---|
| 0 | Incorrect | 67 | FLAWED | Counts only three reductions by half rather than four days after creation. |
| 1 | Correct | 134 | SOUND | Correct four successive halvings: 80→40→20→10→5 kg. |
| 2 | Correct | 107 | SOUND | Correct four successive halvings: 80→40→20→10→5 kg. |
| 3 | Incorrect | 76 | FLAWED | Treats repeated halving as a fixed 40-kg daily reduction. |

**Advisory preference:** chosen sample 2 > rejected sample 3; absolute token gap 31. **Not independently approved.**

## Dataset safeguards

The uploaded original candidate text and correctness labels are not modified. The local review cannot certify unuploaded checkpoint file bytes independently; those were validated in the separate user-reported M3.15 batch integrity audit. No inference, data regrading, pair construction, dataset approval, or model training was conducted to create this advisory document.

**Next:** independent review of HOLD groups 303 and 1293, and project-owner review/approval of proposed pairs or an explicitly defined larger-dataset signoff protocol.
