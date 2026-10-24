# E004-P1 relaxed arithmetic-first QC — 30 provisional accepts

- QC selection seed: `20261024`, Python `random.Random`.
- Sample from source-sorted decisions; excludes no source on correctness/baseline grounds.
- Rejected sample is intentionally STRATIFIED: all eight nonmechanical holds + two random mechanical rejects. Not representative of all rejects.
- This is an **unreviewed audit worksheet**. These are not signed or independently approved training pairs.
- Do not repair source responses. Review arithmetic validity and material relationships; minor wording slips are allowed.

---

## Source 204 — chosen sample 2 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen says the six books are six inches thick, although the stack is 12 inches; arithmetic answer is coincidentally correct.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Jack has a stack of books that is 12 inches thick. He knows from experience that 80 pages is one inch thick. If he has 6 books, how many pages is each one on average?
Answer:
```

**Chosen:**

```text
Since there are 80 pages in 1 inch of thickness, the number of pages in 12 inches of thickness is 80*12=960 pages
Since the books are 6 inches thick, each book is 960/6=160 pages
The answer is 160.
```

**Rejected:**

```text
Jack has 6 books, and that means he has 6 x 80 = 480 pages thick.
That means each book is 12 / 480 = 0.025 inches thick.
Thus, each book is 0.025 x 80 = 2 pages thick.
The answer is 2.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 429 — chosen sample 1 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen labels the 736 result as books published inside the country rather than outside.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: In the school's library, there are 2300 different books. 80% of all the books are in English, but only 60% of these books were published in the country. How many English-language books have been published outside the country?
Answer:
```

**Chosen:**

```text
80% of 2300 books published in English is 2300 * 80/100 = 1840 books
60% of 1840 English-language books are published in the country which is 1840 * 60/100 = 1104 books
1840 - 1104 = 736 books have been published in the country
The answer is 736.
```

**Rejected:**

```text
The number of books in English is 2300 * 80/100 = 1840.
The number of books published in English is 1840 * 60/100 = 1104.
The number of books published in English outside the country is 1104 - 1840 = 1184.
The answer is 1184.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 887 — chosen sample 0 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Kyle is 5 years older than Julian. Julian is 20 years younger than Frederick. Frederick is 2 times older than Tyson. If Tyson is 20, how old is Kyle?
Answer:
```

**Chosen:**

```text
Frederick is 2 * 20 = 40 years old.
Julian is 40 - 20 = 20 years old.
Kyle is 20 + 5 = 25 years old.
The answer is 25.
```

**Rejected:**

```text
Tyson is 20 years old, and Frederick is 2 times older than him, so Frederick is 2*20 = 40 years old.
Frederick is 20 years younger than Julian, so Julian is 40+20 = 60 years old.
Kyle is 5 years older than Julian, so Kyle is 60+5 = 65 years old.
The answer is 65.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1069 — chosen sample 0 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `QUALITY_HOLD_REJECTED`
- Old concern: Rejected response double-counts the gifted quarters and finishes with nonsensical arithmetic.
- New policy reason: Relaxed: chosen is arithmetically sound in existing review; messy/wrong reasoning occurs in the rejected response.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Maria has 4 dimes, 4 quarters, and 7 nickels in her piggy bank. Her mom gives her 5 quarters. How much money, in dollars, does Maria have now?
Answer:
```

**Chosen:**

```text
There are 4 + 5 = 9 quarters.
The dimes are worth 4 * 0.10 = $0.40.
The quarters are worth 9 * 0.25 = $2.25.
The nickels are worth 7 * 0.05 = $0.35.
In total, Maria has 0.40 + 2.25 + 0.35 = $3.00.
The answer is 3.
```

**Rejected:**

```text
The value of the dimes is 4 * $0.10 = $0.40
The value of the quarters is 5 * $0.25 = $1.25
The value of the nickels is 7 * $0.05 = $0.35
The value of the quarters Maria’s mom gave her is 5 * $0.25 = $1.25
The total amount of money Maria has now is $0.40 + $1.25 + $0.35 = $1.00
The answer is 1.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1287 — chosen sample 0 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: "Three times faster" could be read ambiguously; chosen follows GSM8K reference and the rejected output is numerically incorrect.
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Pete walks backwards three times faster than Susan walks forwards, and Tracy does one-handed cartwheels twice as fast as Susan walks forwards.  But Pete can walk on his hands only one quarter the speed that Tracy can do cartwheels.  If Pete walks on his hands at 2 miles per hour, how fast can Pete walk backwards, in miles per hour?
Answer:
```

**Chosen:**

```text
If Pete walks on his hands at 2 miles per hour, then Tracy can do cartwheels at 2*4 = 8 miles per hour.
Tracy does one-handed cartwheels twice as fast as Susan walks forwards, so Susan walks forwards at 8/2 = 4 miles per hour.
But Pete walks backwards three times faster than Susan walks forwards, so Pete can walk backwards at 3*4 = 12 miles per hour.
The answer is 12.
```

**Rejected:**

```text
If Pete can walk on his hands at 2 miles per hour, then Pete can walk backwards at 2*4=8 miles per hour
Tracy does one-handed cartwheels twice as fast as Susan walks forwards, so she can do 8/2=4 miles per hour
If Pete walks backwards 3 times faster than Susan walks forwards, then Pete can walk backwards at 4/3=1.33 miles per hour
The answer is 1.33.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1474 — chosen sample 0 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Evelyn’s family watched 10 hours of television last week. The week before, they watched 8 hours of television. If they watch 12 hours of television next week, what is the average number of hours of television that they watch per week?
Answer:
```

**Chosen:**

```text
Evelyn’s family watched a total of 10 + 8 = 18 hours of television last two weeks.
If they watch 12 hours of television next week, they will watch a total of 18 + 12 = 30 hours of television.
Therefore, the average number of hours of television that they watch per week is 30 / 3 = 10 hours.
The answer is 10.
```

**Rejected:**

```text
Last week, they watched 10 hours of television, so the week before they watched 8 + 10 = 18 hours.
Next week, they watch 12 hours of television.
In total, they watched 18 + 12 = 30 hours of television.
Next week, the average is 30 hours / 4 weeks = 7.5 hours of television.
The answer is 7.5.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1505 — chosen sample 2 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen says two newborn lambs had two babies instead of two of the original six lambs.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Mary had 6 lambs and 2 of the lambs had 2 babies each.  She traded 3 lambs for one goat.  One morning, she woke up and found an extra 7 lambs in the field.  How many lambs does Mary have?
Answer:
```

**Chosen:**

```text
The 2 lambs that were born had 2 babies so they had 2*2=4 babies
Mary had 6 lambs and 4 babies so she had 6+4=10 lambs
Mary traded 3 lambs for one goat so she had 10-3=7 lambs left
Mary found 7 extra lambs in the field so she now has 7+7=14 lambs
The answer is 14.
```

**Rejected:**

```text
Mary initially had 6 lambs and had 2 babies so she had 6+2=8 lambs
Mary traded 3 lambs for one goat so she had 8-3=5 lambs left
Mary found 7 more lambs in the field so she now has 5+7=12 lambs
The answer is 12.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1634 — chosen sample 0 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen calls $100 a profit even though $100 is the revenue needed for an $80 profit.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Alexa has a lemonade stand where she sells lemonade for $2 for one cup. If she spent $20 on ingredients, how many cups of lemonade does she need to sell to make a profit of $80?
Answer:
```

**Chosen:**

```text
She needs to earn a profit of $80 + $20 = $100.
She needs to sell $100/$2 = 50 cups of lemonade.
The answer is 50.
```

**Rejected:**

```text
Alexa needs to earn $180 because 80 + 20 = 180
She needs to sell 90 cups because 180 / 2 = 90
The answer is 90.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1699 — chosen sample 3 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen labels 30 as combined pink and purple rather than 30 of each color.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: A garden is filled with 105 flowers of various colors. There are twice as many red flowers as orange. There are five fewer yellow flowers than red. If there are 10 orange flowers, how many pink and purple flowers are there if they have the same amount and there are no other colors?
Answer:
```

**Chosen:**

```text
There are 10 * 2 = 20 red flowers.
There are 20 - 5 = 15 yellow flowers.
There are 10 + 20 + 15 = 45 flowers that are red, yellow, and orange.
There are 105 - 45 = 60 pink and purple flowers.
There are 60 / 2 = 30 pink and purple flowers.
The answer is 30.
```

**Rejected:**

```text
Since there are 10 orange flowers, there are 2*10=20 red flowers.
If there are 5 fewer yellow flowers than red, there are 20-5=15 yellow flowers.
In total, there are 20+15+10=45 flowers.
There are 105 flowers in total and 45 flowers are pink and purple, so there are 105-45=60 pink and purple flowers.
The answer is 60.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1731 — chosen sample 1 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen says Ricciana ran a total of 4 feet, which was her jump distance.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Ricciana and Margarita joined in their school's long jump event. Ricciana ran and jumped a total of 24 feet -  20 feet for running and 4 feet for jumping. Margarita ran for 18 feet and jumped 1 foot less than twice Ricciana's jump. How much farther did Margarita run and jump than Ricciana?
Answer:
```

**Chosen:**

```text
Ricciana's total run was 24 - 20 = 4 feet
Margarita's jump was 2 * 4 - 1 = 7 feet
Margarita's total run was 18 + 7 = 25 feet
Margarita ran and jumped 25 - 24 = 1 foot farther than Ricciana.
The answer is 1.
```

**Rejected:**

```text
Ricciana ran for 20 + 4 = 24 feet.
Margarita jumped 24 * 2 - 1 = 47 feet.
Margarita ran for 18 + 47 = 65 feet.
The difference between Margarita's and Ricciana's running is 65 - 24 = 41 feet.
The answer is 41.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1848 — chosen sample 0 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: A floral shop had a three day sale on rose bouquets. On Monday, they sold 12 bouquets. On Tuesday, they sold three times that many bouquets. On Wednesday it rained all day and they only sold a third of what they did the day before. How many bouquets did they sell during the three day sale?
Answer:
```

**Chosen:**

```text
On Monday they sold 12 bouquets.
On Tuesday they sold 3*12 = 36 bouquets.
On Wednesday they sold 36/3 = 12 bouquets.
In total they sold 12+36+12 = 60 bouquets.
The answer is 60.
```

**Rejected:**

```text
They sold 12 x 3 = 36 bouquets on Tuesday.
They only sold a third of 36, for a total of 36 / 3 = 12 bouquets on Wednesday.
Together, they sold 36 + 12 + 12 = 56 bouquets.
The answer is 56.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 2050 — chosen sample 2 / rejected sample 0

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen describes the five-day second protest as five more days without clear referent.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: John attends a protest for 4 days.  He then attends a second protest for 25% longer than the first.  How many days did he spend protesting?
Answer:
```

**Chosen:**

```text
For 25% longer, it is 4*0.25 = 1 more day
So it takes him 4+1 = 5 more days
So he spent protesting for a total of 4+5 = 9 days
The answer is 9.
```

**Rejected:**

```text
He was protesting for 4*2=8 days for the second protest
So he was protesting for a total of 8+4=12 days
The answer is 12.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 2192 — chosen sample 1 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `QUALITY_HOLD_REJECTED`
- Old concern: Rejected response repeatedly mislabels donation ordinals and totals; mistake is not well isolated.
- New policy reason: Relaxed: chosen is arithmetically sound in existing review; messy/wrong reasoning occurs in the rejected response.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Suzanne wants to raise money for charity by running a 5-kilometer race. Her parents have pledged to donate $10 for her first kilometer and double the donation for every successive kilometer. If Suzanne finishes the race, how much money will her parents donate?
Answer:
```

**Chosen:**

```text
Suzanne's first donation will be $10.
Her second donation will be $10 x 2 = $20.
Her third donation will be $20 x 2 = $40.
Her fourth donation will be $40 x 2 = $80.
Her fifth donation will be $80 x 2 = $160.
Thus, her parents will donate a total of $10 + $20 + $40 + $80 + $160 = $310.
The answer is 310.
```

**Rejected:**

```text
Suzanne's first donation is $10 because she runs the first kilometer.
Her first two donations are $10 * 2 = $20
Her second donation is $20 * 2 = $40
Her third donation is $40 * 2 = $80
Her fourth donation is $80 * 2 = $160
Her fifth donation is $160 * 2 = $320
Her parents will donate $320.
The answer is 320.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 3044 — chosen sample 1 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen replaces pounds of noodles with individual noodles and says 2 pounds per noodle.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Tom decides to make lasagna with all his beef.  It takes twice as many noodles as beef.  He has 10 pounds of beef.  He already has 4 pounds of lasagna noodles and the noodles come in 2-pound packages.  How many packages does he need to buy?
Answer:
```

**Chosen:**

```text
It takes 2*10=20 noodles
He has already got 4 noodles
He needs to buy 20-4=16 noodles
There are 2 pounds in 1 noodle so he needs to buy 16/2=8
The answer is 8.
```

**Rejected:**

```text
The noodles needed for the lasagna are 10*.5=5 pounds of noodles
He needs to buy 5-4=1 more package of noodles
The answer is 1.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 3424 — chosen sample 0 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen says $7 was given to the brother, though $5 was spent on lunch and only $2 given.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Larry spent $5 for lunch and gave his brother $2. How much did Larry have at the beginning if he has $15 now?
Answer:
```

**Chosen:**

```text
Larry spent $5 for lunch and $2 for his brother and gave $5+2=$7 to his brother.
Larry has $15 and he spent $7 so he had $15+7=$22 at the beginning.
The answer is 22.
```

**Rejected:**

```text
He gave his brother $2 and spent $5 for lunch, so he has spent $5 + $2 = $7.
Larry has $15 now and spent $7, so he had $15 - $7 = $8 at the beginning.
The answer is 8.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 3467 — chosen sample 1 / rejected sample 0

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen describes two spent $1 bills as $2 rather than as a number of special bills.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: George is about to celebrate his 25th birthday. Since his 15th birthday, he's been given a special $1 bill from his parents. They told him that on his 25th birthday, for every bill he still has, they will give him $1.5 in exchange. He spent 20% of his special bills. How much will he receive from his parents when he exchanges them?
Answer:
```

**Chosen:**

```text
He has already been given 25-15=10 special bills.
He has spent 10*20/100=$2.
So, he has 10-2=8 special bills left.
He gets 8*1.5=$12 when he exchanges them.
The answer is 12.
```

**Rejected:**

```text
George has already spent 25 - 15 = 10 bills
He has 25 - 10 = 15 bills left
He needs 15 - 10 = 5 bills for the exchange
He will receive $1.5 x 5 = $7.5
The answer is 75.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4017 — chosen sample 0 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Tom broke his leg and needed to go to the doctor.  The visit cost $300 and the cast cost $200.  If insurance covered 60% how much was Tom's out-of-pocket cost?
Answer:
```

**Chosen:**

```text
The total cost was $300+200=$500
Insurance covered 60% of the total cost so 60/100*500=$300
Tom's out of pocket cost was 500-300=$200
The answer is 200.
```

**Rejected:**

```text
Insurance covered $120 because 200*0.6=120
So the cost of the visit and cast was $420 because 300+200=420
So Tom's out-of-pocket cost was $240 because 420-120=240
The answer is 240.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4087 — chosen sample 3 / rejected sample 0

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen uses a currency sign for the 12-foot answer ($12 feet).
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Mitch has saved $20000 to finance his boating hobby. A new boat costs $1500 per foot in length. If Mitch needs to keep $500 for a license and registration, and three times that amount for docking fees, how many feet is the longest boat he can buy?
Answer:
```

**Chosen:**

```text
Mitch needs to keep $500 for a license and registration and 3*$500=$1500 for docking fees.
So, Mitch will keep a total of $500+$1500=$2000
The total cost of the boat is $20000-$2000=$18000
Thus, Mitch can buy 18000/$1500=$12 feet of the longest boat he can buy.
The answer is 12.
```

**Rejected:**

```text
Mitch needs $20000 - $500 = $19500 to buy the boat.
The docking fees cost Mitch $500 x 3 = $1500.
Mitch needs $19500 - $1500 - $1500 = $16500.
Thus, the longest boat he can buy is $16500 / $1500 = 11 feet.
The answer is 11.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4561 — chosen sample 1 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Eric, Ben, and Jack have some money. Eric has $10 less than Ben, and Ben has $9 less than Jack. If Jack has $26, how much money, in dollars, do all 3 of them have in total?
Answer:
```

**Chosen:**

```text
If Ben has $9 less than Jack, then Ben has $26 - $9 = $17.
If Eric has $10 less than Ben, then Eric has $17 - $10 = $7.
In total, all 3 of them have $26 + $17 + $7 = $50.
The answer is 50.
```

**Rejected:**

```text
If Ben has $9 less than Jack, Ben has $26 - $9 = $17.
If Eric has $10 less than Ben, Eric has $17 - $10 = $7.
In total, Eric, Ben, and Jack have $7 + $17 + $26 = $40.
The answer is 40.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4788 — chosen sample 2 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Fran's school just instituted a school uniform policy. Each student needs to buy five complete uniforms, each consisting of pants, shirt, tie and socks. The pants cost $20, the shirt costs twice as much as the pants, the tie costs 1/5 as much as the shirt and the socks cost $3/pair. How many dollars will each student need to spend?
Answer:
```

**Chosen:**

```text
The cost of the shirt is 20 x 2 = $40.
The cost of the tie is 40 / 5 = $8.
The total cost of one complete uniform is 20 + 40 + 8 + 3 = $71.
Therefore, each student will need to spend $71 x 5 = $355.
The answer is 355.
```

**Rejected:**

```text
The shirt costs 20 * 2 = $40
The tie costs 40 / 5 = $8
So the socks cost 3 * 5 = $15
Therefore the total cost is 20 + 40 + 8 + 15 = $83
The answer is 83.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4919 — chosen sample 0 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Mcdonald is planning to open up a farm that provides eggs to the community. In his local community, Saly needs 10 eggs, Ben needs 14 eggs, and Ked needs half of the number of eggs needed by Ben per week. In a month which has 4 weeks, how many eggs should Mcdonald's farm produce?
Answer:
```

**Chosen:**

```text
Saly needs 10 eggs per week.
Ben needs 14 eggs per week.
Ked needs 1/2*14 = 7 eggs per week.
In total, they need 10+14+7=31 eggs per week.
In a month, which has 4 weeks, they need 31*4 = 124 eggs.
The answer is 124.
```

**Rejected:**

```text
Ben needs 14 / 2 = 7 eggs a week.
Together, Saly and Ben need 10 + 7 = 17 eggs a week.
Together with Ked, they need 17 + 7 = 24 eggs a week.
In a month of 4 weeks, the farm needs to produce 24 x 4 = 96 eggs per month.
The answer is 96.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 5236 — chosen sample 0 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: John decides to buy a month's supply of dog treats.  He gives his dog 2 treats a day and they cost $.1 each.  How much does he spend on the treats if the month is 30 days long?
Answer:
```

**Chosen:**

```text
He gives his dog 2 treats a day so that’s 2*30=60 treats in a month
Each treat costs $.1 so that’s 60*.1=$6.00
The answer is 6.
```

**Rejected:**

```text
He gives his dog 2 treats a day for 30 days so he gets 2*30=60 treats
They cost $.1 each so he spends 60*.1=$0.60
The answer is 0.60.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 5428 — chosen sample 2 / rejected sample 1

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen describes the 100-meter school round trip as 100 meters to the market.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Andy walks 50 meters from his house to school. After school, he comes back to the house and goes to the market. If he walks 140 meters in total, how many meters is the distance between the house and the market?
Answer:
```

**Chosen:**

```text
Andy walked 50 + 50 = 100 meters to the market.
So, the distance between the house and the market is 140 - 100 = 40 meters.
The answer is 40.
```

**Rejected:**

```text
He walks 100 meters to the market because 50 + 100 = 150
The distance between the house and the market is 50 meters because 150 - 100 = 50
The answer is 50.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 5912 — chosen sample 0 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: Chosen leaves the last $2 juice charge unlabeled; the amount and sum are correct.
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: A school canteen sells a sandwich at $2, a hamburger at $2, one stick of hotdog at $1, and a can of fruit juice at $2 each can. Selene buys three sandwiches and a can of fruit juice. Tanya buys two hamburgers and two cans of fruit juice.  How much do Selene and Tanya spend together?
Answer:
```

**Chosen:**

```text
Selene spends 3 x 2 = $6 on sandwiches.
Tanya spends 2 x 2 = $4 on hamburgers.
Tanya spends 2 x 2 = $4 on fruit juice.
Together, Selene and Tanya spend 6 + 4 + 4 + 2 = $16.
The answer is 16.
```

**Rejected:**

```text
Selene spends 2*3=6 dollars on sandwiches.
Tanya spends 2*2=4 dollars on hamburgers.
Tanya also spends 2*2=4 dollars on fruit juice.
Together they spend 6+4+4=14 dollars.
The answer is 14.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 5917 — chosen sample 2 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Harly's animal shelter has 80 dogs. She adopts out 40% of them but then has to take back 5 because of personality conflicts with other dogs in their adopted homes. How many dogs does she have now?
Answer:
```

**Chosen:**

```text
If she adopts out 40% of the dogs, then 80*.40 = 32 dogs have been adopted.
So far, there are 80-32 = 48 dogs left.
So she has to take back 5 dogs, leaving 48+5= 53 dogs now.
The answer is 53.
```

**Rejected:**

```text
She adopts out 80*0.4= 32 dogs
She now has 80-32= 48 dogs
She takes back 5 so she is left with 48-5= 43 dogs
The answer is 43.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 6052 — chosen sample 1 / rejected sample 0

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: On his farm, Mr. Valentino has 200 chickens, twice as many ducks as chickens and three times as many turkeys as ducks. How many birds does Mr. Valentino have on the farm in total?
Answer:
```

**Chosen:**

```text
If Mr. Valentino has 200 chickens, then he has 200 x 2 = 400 ducks.
He also has 400 x 3 = 1200 turkeys.
In total, Mr. Valentino has 200 + 400 + 1200 = 1800 birds on the farm.
The answer is 1800.
```

**Rejected:**

```text
Mr. Valentino has 200 x 2 = 400 ducks.
Since he has 200 x 3 = 600 turkeys.
So, he has 200 + 400 + 600 = 1200 birds on the farm.
The answer is 1200.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 6262 — chosen sample 1 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `QUALITY_HOLD_REJECTED`
- Old concern: Rejected response switches between undefined algebraic variables and unsupported equations.
- New policy reason: Relaxed: chosen is arithmetically sound in existing review; messy/wrong reasoning occurs in the rejected response.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: The ratio of books to pens that Arlo has to buy for his school supplies is 7:3. If he bought a total of 400 stationery from the store, calculate the number of books he bought.
Answer:
```

**Chosen:**

```text
Since the ratio of books to pens that Arlo has to buy for his school supplies is 7:3, we can say that he bought a total of 7+3=10 parts in all.
If the total number of stationery that he bought is 400, then each part is equal to 400/10=40
Therefore, Arlo bought 40*7=280 books from the store.
The answer is 280.
```

**Rejected:**

```text
Let b be the number of books Arlo bought and p be the number of pens Arlo bought. Since the ratio of books to pens is 7:3, the total number of books and pens is 10 units.
Since the total number of stationery that Arlo bought is 400, each unit is 400/10=40.
The total number of books Arlo bought is b+p=40*1=40
The total number of pens that Arlo bought is p=40*3=120.
The answer is 40.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 6453 — chosen sample 0 / rejected sample 3

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Question says a batch serves about six people; exact batch requirement is not fully specified.
- New policy reason: Relaxed: prior language/referent/unit concern allowed; chosen arithmetic operations follow the GSM8K numeric reference, per existing first-pass review.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Allie's making guacamole for a party. Each batch requires 4 avocados and serves about 6 people. If 42 people are going to be at the party including her, how many avocados does she need?
Answer:
```

**Chosen:**

```text
Each batch serves about 6 people, so the number of batches needed is 42/6 = 7 batches.
Each batch requires 4 avocados, so she will need 4 x 7 = 28 avocados.
The answer is 28.
```

**Rejected:**

```text
She needs to make guacamole for 42-1 = 41 people
She needs to make guacamole for 41/6 = 6.83 avocados
She needs 7 avocados.
The answer is 7.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 6697 — chosen sample 3 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Renne earns $4000 per month and wants to save half of her monthly earnings to buy the vehicle of her dreams worth $16000. How many months of saving will it take her to buy the vehicle?
Answer:
```

**Chosen:**

```text
First find the amount of money Renne wants to save: $4000 / 2 = $2000
Then divide the cost of the vehicle by the amount Renne wants to save each month: $16000 / $2000 = 8 months
The answer is 8.
```

**Rejected:**

```text
If the vehicle is worth $16000, then half of that is $16000 / 2 = $8000
This means that it takes 16000 / 8000 = 2 months to save enough money to buy the vehicle.
The answer is 2.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 7129 — chosen sample 3 / rejected sample 2

- Current decision: `PROVISIONAL_ACCEPT_QC_REQUIRED`
- Previous review: `PROVISIONAL_QC_REQUIRED`
- Old concern: No obvious mathematical/semantic contradiction in first-pass assistant review of the selected response pair; not independently certified.
- New policy reason: Retained from prior provisional first-pass review under arithmetic-first policy.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Mary was working on a research paper and already had borrowed 5 books from the library.  3 books weren't helpful so she returned those and checked out 5 more books.  3 days later, she went back to the library and returned 2 of those books and checked out 7 more books.  How many books does Mary currently have checked out of the library?
Answer:
```

**Chosen:**

```text
She had 5 books originally and returned 3 so she has 5-3=2 books remaining
She then checked out 5 books so she now has 2+5=7 books
3 days later, she returned 2 books so she now has 7-2=5 books
She then checked out 7 books so now she has 5+7=12 books in total.
The answer is 12.
```

**Rejected:**

```text
She started out with 5 books and returned 3 so she has 5 - 3 = 2 books left
She borrowed 5 more books and returned 2 so she has 2 + 5 - 2 = 5 books left
She checked out 7 books and returned 2 so she has 5 + 7 - 2 = 10 books left
The answer is 10.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

