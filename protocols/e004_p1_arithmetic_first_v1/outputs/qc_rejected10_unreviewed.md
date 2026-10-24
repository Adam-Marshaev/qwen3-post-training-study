# E004-P1 relaxed arithmetic-first QC — 10 review rejects

- QC selection seed: `20261024`, Python `random.Random`.
- Sample from source-sorted decisions; excludes no source on correctness/baseline grounds.
- Rejected sample is intentionally STRATIFIED: all eight nonmechanical holds + two random mechanical rejects. Not representative of all rejects.
- This is an **unreviewed audit worksheet**. These are not signed or independently approved training pairs.
- Do not repair source responses. Review arithmetic validity and material relationships; minor wording slips are allowed.

---

## Source 630 — chosen sample 2 / rejected sample 0

- Current decision: `REJECT_MECHANICAL`
- Previous review: `MECHANICAL_REJECT`
- Old concern: Fails at least one deterministic arithmetic, format, eligibility, or length gate.
- New policy reason: No pair meets frozen arithmetic/eligibility/format/length checks.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: On her birthday, Avianna bought red candles and blue candles in the ratio of 5:3. If Avianna had 45 red candles on her birthday, how many blue candles did she have?
Answer:
```

**Chosen:**

```text
The ratio of red candles to blue candles is 5:3, which means that 5 parts represent red candles and 3 parts represent blue candles.
If Avianna had 45 red candles, and the red candles represent 5 parts, we can divide 45 by 5 to find out how many candles one part represents: 45/5 = 9
The blue candles represent 3 parts, so we can multiply the number of parts by the number of candles one part represents: 9 * 3 = 27
The answer is 27.
```

**Rejected:**

```text
If the red candles were 5 red candles for every blue candles, and Avianna had 45 red candles, then the blue candles were 45/5 = 9 blue candles.
The answer is 9.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 1344 — chosen sample 2 / rejected sample 0

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen repeatedly calls an increase in earnings a decrease.
- New policy reason: Chosen calls a positive earnings increase a decrease throughout; reverses the requested quantity.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Jame gets a raise to $20 per hour and works 40 hours a week.  His old job was $16 an hour for 25 hours per week.  How much more money does he make per year in his new job than the old job if he works 52 weeks a year?
Answer:
```

**Chosen:**

```text
His new job pays him 20*40=$800 per week
His old job pays him 16*25=$400 per week
His new job pays him 800-400=$400 less per week
If he works 52 weeks a year he makes 400*52=$20,800 less per year
The answer is 20800.
```

**Rejected:**

```text
He gets 40*20=$800 a week
He earns 52*800=$41600 a year at his new job
He works 52*25=$1300 a year in his old job
So he earns 41600-1300=$39300 less a year at his old job
The answer is 39300.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4483 — chosen sample 0 / rejected sample 3

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen confuses the buyers, half-collection arithmetic, and offer prices.
- New policy reason: Chosen invents/reshuffles record purchasers and wrong half-collection math; correct final absolute difference is coincidental.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Peggy is moving and is looking to get rid of her record collection. Sammy says that he will buy all of them for 4 dollars each. Bryan is only interested in half of the records but will offer 6 dollars each for the half that he is interested in and 1 dollar each for the remaining half that he is not interested in with the hopes that he can resell them in bulk later. If Peggy has 200 records, what is the difference in profit between Sammy versus Bryan's deal?
Answer:
```

**Chosen:**

```text
If Peggy has 200 records, then Sammy will buy them for 200*4 = $800.
If Peggy only has half the records, then the half she is interested in will be 200/2 = 100 records.
Sammy will buy the half of the records for 100*6 = $600.
Bryan will buy 100/2 = 50 records for 50*1 = $50.
Bryan will also buy 50 records for 50*6 = $300.
Bryan's total will be 600+300 = $900.
The difference in profit between Sammy versus Bryan's deal is 900-800 = $100
The answer is 100.
```

**Rejected:**

```text
Half of Peggy's records is 200/2 = 100 records.
With 100 records Sammy will buy, he will pay 4 dollars for each record, so he will pay 100*4 = $400 for all of the records.
With the 100 records, Bryan will buy half of them for 6 dollars each, so that will be 100*6 = $600.
Bryan will also buy the other half of the records for 1 dollar each, so he will pay 100*1 = $100 for those records.
Bryan's total will be 600 + 100 = $700
So Sammy will make 700 - 400 = $300 more than Bryan.
The answer is 300.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 4681 — chosen sample 2 / rejected sample 0

- Current decision: `REJECT_MECHANICAL`
- Previous review: `MECHANICAL_REJECT`
- Old concern: Fails at least one deterministic arithmetic, format, eligibility, or length gate.
- New policy reason: No pair meets frozen arithmetic/eligibility/format/length checks.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Coby went on a road trip. He is traveling from Washington to Nevada but he needs to stop in Idaho which is 640 miles away from Washington and 550 miles away from Nevada to pick up some friends.  If Coby is traveling at a speed of 80 miles per hour going to Idaho and at a speed of 50 miles per hour from Idaho to Nevada, how many hours did it take for him to arrive at the destination?
Answer:
```

**Chosen:**

```text
Idaho is 640 miles away from Washington so that takes 640/80 = 8 hours
Idaho is 550 miles away from Nevada so that takes 550/50 = 11 hours
In total, it took him 8+11 = 19 hours to arrive at the destination.
The answer is 19.
```

**Rejected:**

```text
First find the total distance to Idaho: 640 miles + 550 miles = 1190 miles
Then divide the total distance to Idaho by the speed to find the time it took: 1190 miles / 80 miles/hour = 14.875 hours
Then divide the distance from Idaho to Nevada by the speed to find the time it took: 550 miles / 50 miles/hour = 11 hours
Then add the two times to find the total time: 11 hours + 14.875 hours = 25.875 hours
The answer is 25.875.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 5588 — chosen sample 1 / rejected sample 0

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen reverses 20% bringing vests into 80% bringing vests; gets correct number via wrong account.
- New policy reason: Chosen reverses who brings life vests and then uses that mislabeled group as unmet demand; material contradiction in population account.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Alice's white water rafting class is composed of 40 students and 10 instructors, including herself.  She has 20 life vests on hand.  20% of her students are bringing life vests.  How many more life vests will Alice need to get so that entire class has one?
Answer:
```

**Chosen:**

```text
There are 100% - 20% = 80% of students that are bringing life vests.
There are .8*40 = 32 students bringing life vests.
So she needs 32 + 10 = 42 life vests to have one for the entire class.
That means she needs to get 42 - 20 = 22 more life vests.
The answer is 22.
```

**Rejected:**

```text
The students are bringing life vests 20/100*40 = 8 life vests.
So, the total number of life vests that the class has is 40+10+8 = 58 life vests.
Therefore, Alice needs 58-20 = 38 life vests more.
The answer is 38.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 5932 — chosen sample 1 / rejected sample 2

- Current decision: `REJECT_UNSUITABLE_NEGATIVE`
- Previous review: `QUALITY_HOLD_REJECTED`
- Old concern: Rejected response consists of multiple unrelated unsupported quantity changes.
- New policy reason: Rejected response has several disconnected false quantities and inconsistent conclusions; unsuitable style-confounded preference negative.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Jenine can sharpen a pencil 5 times before it runs out. She needs to sharpen a pencil for every 1.5 hours of use. She already has ten pencils and needs to write for 105 hours. A new pencil costs $2. How much does she need to spend on more pencils to be able to write for 105 hours?
Answer:
```

**Chosen:**

```text
Jenine can sharpen a pencil for 5 * 1.5 = 7.5 hours
Jenine needs to sharpen a pencil for 105 / 7.5 = 14 pencils
Jenine already has 10 pencils
She needs to purchase 14 - 10 = 4 more pencils
A new pencil costs $2.
Jenine needs to spend 2 * 4 = $8 on more pencils
The answer is 8.
```

**Rejected:**

```text
She has 10 pencils because 10 x 1.5 = 15
She already has 10 pencils because 15 / 1.5 = 10
She needs to write for 100 more hours because 105 - 55 = 50
She needs 12 more pencils because 12 x 5 = 60
She needs to spend $6 on more pencils because 6 x 2 = 12
The answer is 12.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 6411 — chosen sample 2 / rejected sample 0

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen adds magnets, buttons, and gemstones and then calls all components gemstones.
- New policy reason: Chosen adds magnets and buttons to gemstones instead of calculating gems for two earrings; reaches 24 by coincidence.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: Rebecca makes her own earrings out of buttons, magnets, and gemstones.  For every earring, she uses two magnets, half as many buttons as magnets, and three times as many gemstones as buttons.  If Rebecca wants to make 4 sets of earrings, how many gemstones will she need?
Answer:
```

**Chosen:**

```text
For one set of earrings, Rebecca uses 2 magnets and 2/2=1 button
So she uses 1*3=3 gemstones
Thus for one set of earrings, she uses 3+1+2=6 gemstones
For 4 sets of earrings, she will need 6*4=24 gemstones
The answer is 24.
```

**Rejected:**

```text
For 1 earring, she uses 2*0.5 = 1 button.
She uses 3*1 = 3 gemstones.
Thus for 1 earring, she uses 1+3 = 4 gemstones.
She will need 4*4 = 16 gemstones.
The answer is 16.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 6786 — chosen sample 2 / rejected sample 1

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen treats the initial 2-inch nail length as months to grow 26 inches, then treats months as years.
- New policy reason: Chosen treats 20 months of growth as 20 years of aging; required time is (26-2)/0.1=240 months=20 years.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: The world record for longest fingernails is 26 inches. Sandy, who just turned 12 this month, has a goal for tying the record. Her fingernails are 2 inches long. Her fingernails grow at a rate of one-tenth of an inch per month. How old will she be when she achieves the world record?
Answer:
```

**Chosen:**

```text
Sandy's fingernails are 2 inches long and it takes 1/10 of an inch per month to grow her fingernails. This means it will take 2 * 10 = 20 months to reach the world record.
Since Sandy has just turned 12, she will be 12 + 20 = 32 years old when she achieves the world record.
The answer is 32.
```

**Rejected:**

```text
Sandy's fingernails will grow 1/10 x 12 months = 1.2 inches in 12 months.
Sandy's fingernails will be 2 inches + 1.2 inches = 3.2 inches long in 12 months.
Sandy will be 12 + 12 = 24 years old when she ties the world record.
The answer is 24.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 7019 — chosen sample 2 / rejected sample 0

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Original question's phrase "one and a half increase" is ambiguous enough to warrant exclusion.
- New policy reason: Question wording about a one-and-a-half increase is materially ambiguous; a rejected different interpretation may be defensible.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: One and a half increase in the productivity in Tutuwanas saw-mill this year was due to the Albaszu machine's being finally repaired. If the Albaszu machine was cutting 10 trees daily, how many trees is it cutting now after its improvement?
Answer:
```

**Chosen:**

```text
The machine has increased in productivity by 1.5 times its previous productivity of 10 trees, which is 1.5 * 10 = 15 trees.
So, it is now cutting 15 + 10 = 25 trees daily.
The answer is 25.
```

**Rejected:**

```text
The Albaszu machine was cutting 10 trees per day and one and a half increase means it will be cutting 10 + (1/2*10) = 10 + 5 = 15 trees per day after improvement.
The answer is 15.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

## Source 7305 — chosen sample 1 / rejected sample 3

- Current decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Previous review: `SEMANTIC_HOLD_CHOSEN`
- Old concern: Chosen invents a change in the number of cats that the question never states.
- New policy reason: Chosen assumes an unstated change in number of cats; conclusion requires unsupported population relation.
- Previous QC flag: none
- **Note:** for mechanical rejects, the shown pair is diagnostic only, NOT a mechanically passing pair.

**Question:**

```text
Question: If the number of dogs in the neighborhood was originally half the number of cats in the neighborhood before twenty new dogs were born, and now there are twice as many dogs as cats, how many cats were in the neighborhood, to begin with, if there are 20 cats now?
Answer:
```

**Chosen:**

```text
After twenty new dogs were born, the number of dogs in the neighborhood increased to 20+20 = 40
If there are now twice as many dogs as cats in the neighborhood, and there are 40 dogs, the number of cats in the neighborhood is 40/2 = 20 cats.
If there are 20 cats now, and the number of cats had originally been half the number of cats in the neighborhood, the number of cats in the neighborhood was 20*2 = 40 cats.
The answer is 40.
```

**Rejected:**

```text
Twenty new dogs were born, so there are 20+20=40 dogs now.
The number of dogs in the neighborhood is now twice as many as cats, meaning there are 40/2=20 cats in the neighborhood.
Twenty new dogs were born, so there were 20-20=0 new dogs in the neighborhood.
As the number of dogs has decreased, the number of cats must have increased, so the number of cats in the neighborhood was 20+0=20.
The answer is 20.
```

**Your QC decision:** [ ] accept under arithmetic-first rule  [ ] reject material mathematical error  [ ] uncertain

**Reason:**

---

