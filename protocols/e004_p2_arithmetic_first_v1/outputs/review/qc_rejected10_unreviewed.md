# E004-P2 arithmetic-first QC — 10 rejects

- Fixed seed: `20261024`. Random accepted sample; rejected sample is STRATIFIED (all seven source-level material holds + three random mechanical rejects).
- This sample is NOT independently adjudicated. All selected pairs remain provisional; no training approved.
- Judge mathematical operations and quantity relationships; tolerate minor wording/units/referents.
- For mechanical rejects, the diagnostic comparison shown below does NOT satisfy all mechanical gates.

---

## Source 658 — chosen sample 3, rejected sample 2

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Question prices use USD and EUR without a conversion rate. Subtracting 893 dollars and 874 euros as equivalent currency is unjustified.
- Reference numeric answer: `19`
- Chosen/rejected token gap: `3`

**Question:**

```text
Question: Sara is checking out two different stores to buy a computer. The first store offers a device for $950 with a 6% discount. The second sells the same computer for €920 with a 5% discount. What is the difference in price between the two stores?
Answer:
```

**Chosen response:**

```text
The first store offers a discount of 950*6/100 = $57
The computer costs 950-57 = $893
The second store also offers a discount of 920*5/100 = $46
The computer costs 920-46 = $874
The difference in price between the two stores is 893-874 = $19
The answer is 19.
```

**Rejected response:**

```text
The first store offers $950 * 6/100 = $57 of discount.
The first store sells the computer for $950 - $57 = $893.
The second store also sells the computer for $920 - $920 * 5/100 = $876.
The second store sells the computer for $876.
The discount is $893 - $876 = $17.
The answer is 17.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 660 — chosen sample 3, rejected sample 1

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Duke should have 2 ants, not 6, and Abe is omitted from the final summation. The reported 20 is coincidental.
- Reference numeric answer: `20`
- Chosen/rejected token gap: `4`

**Question:**

```text
Question: Abe finds 4 ants on the sidewalk.  Beth sees 50% more ants than Abe.  CeCe watches twice as many ants as Abe.  Duke discovers half as many ants as Abe.  How many ants do the four children find together?
Answer:
```

**Chosen response:**

```text
Beth sees 4*0.5=2 more ants than Abe
So, Beth finds 4+2=6 ants
Duke finds 4/2=2 more ants than Abe
So, Duke finds 4+2=6 ants
CeCe finds 4*2=8 more ants than Abe
So, CeCe finds 4*2=8 ants
Together, the four children find 6+6+8=20 ants
The answer is 20.
```

**Rejected response:**

```text
Beth sees 4*1.5=6 more ants than Abe.
So Beth sees 4+6 = 10 ants on the sidewalk.
Duke finds 4/2=2 ants on the sidewalk.
So Duke finds 2+4 = 6 ants on the sidewalk.
Cecie finds 4*2 = 8 ants on the sidewalk.
The four children find a total of 10+4+6+8 = 28 ants on the sidewalk.
The answer is 28.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 979 — chosen sample 3, rejected sample 1

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Grant throws 20 yards and Kyle 40 yards; chosen computes twice the 4-yard increase instead, then adds 16+8 to obtain 24 accidentally.
- Reference numeric answer: `24`
- Chosen/rejected token gap: `15`

**Question:**

```text
Question: At football tryouts, the coach wanted to see who could throw the ball the farthest.  Parker threw the ball 16 yards.  Grant threw the ball 25 percent farther than Parker and Kyle threw the ball 2 times farther than Grant.  Compared to Parker, how much farther did Kyle throw the ball?
Answer:
```

**Chosen response:**

```text
Grant threw the ball 16*0.25 = 4 yards farther than Parker.
Kyle threw the ball 2*4 = 8 yards farther than Parker.
Kyle threw the ball 16+8 = 24 yards farther than Parker.
The answer is 24.
```

**Rejected response:**

```text
Grant threw the ball 25/100 * 16 = 4 yards farther than Parker.
Kyle threw the ball 2 * 4 = 8 yards farther than Parker.
The answer is 8.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 1115 — chosen sample 2, rejected sample 3

- Decision: `REJECT_MECHANICAL`
- Reviewer note: No pair passed exact frozen arithmetic, eligibility, terminal-answer, and length-gap gates.
- Reference numeric answer: `48`
- Chosen/rejected token gap: `6`

**Question:**

```text
Question: 8 jumbo scallops weigh one pound and cost $24.00 a pound.  Nate is pairing 2 scallops with a corn bisque as a light summer dinner.  He’s cooking for 8 people.  How much will the scallops cost?
Answer:
```

**Chosen response:**

```text
Each scallop weighs 8/2=4 pounds
So each scallop cost $24.00/4=6 dollars
And 8 scallops cost 6*8=$48.00
The answer is 48.
```

**Rejected response:**

```text
Nate needs 1 pound per 2 scallops
So 8 people need 4 pounds of scallops
That means 4 pounds * $24/1 pound = $96
The answer is 96.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 1434 — chosen sample 1, rejected sample 3

- Decision: `REJECT_MECHANICAL`
- Reviewer note: No pair passed exact frozen arithmetic, eligibility, terminal-answer, and length-gap gates.
- Reference numeric answer: `225`
- Chosen/rejected token gap: `8`

**Question:**

```text
Question: A typical tournament of tennis has 4 rounds. There are 8 games in the first round, 4 in the second round, 2 in the third round and 1 during the finals. If each game requires new tennis balls, and on average each game uses 5 cans of tennis balls, how many tennis balls in total are used at the end of the tournament if each can has 3 tennis balls?
Answer:
```

**Chosen response:**

```text
8 games x 5 cans/gam 40 cans
4 games x 5 cans/gam 20 cans
2 games x 5 cans/gam 10 cans
1 game x 5 cans/gam 5 cans
40 + 20 + 10 + 5 = 75 cans of tennis balls
75 cans x 3 tennis balls/can = 225 tennis balls
The answer is 225.
```

**Rejected response:**

```text
First find the total number of games in the tournament: 4 rounds * 8 games/round = 32 games
Then find the total number of cans of tennis balls used: 32 games * 5 cans/game = 160 cans
Then find the total number of tennis balls used: 160 cans * 3 tennis balls/can = 480 tennis balls
The answer is 480.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 2760 — chosen sample 2, rejected sample 1

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Chosen doubles the father’s current age and subtracts the son’s current age as though the father must first reach 64. The age relationship is invalid; 27 arises by coincidence.
- Reference numeric answer: `27`
- Chosen/rejected token gap: `20`

**Question:**

```text
Question: Joel is 5 years old and his dad is 32 years old.  How old will Joel be when his dad is twice as old as him?
Answer:
```

**Chosen response:**

```text
Joel's dad will be 32*2=64 years old.
Joel will be 64-32=32 years old when his dad is twice as old as him.
Joel will be 32-5=27 years old when his dad is twice as old as him.
The answer is 27.
```

**Rejected response:**

```text
Joel is currently 5 years old and his dad is 32 years old.
Joel's dad will be twice as old as him when he is 32/2 = 16 years old.
Joel's dad will be 32 years old - 16 years = 16 years later.
Joel will be 5 years + 16 years = 21 years old.
The answer is 21.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 4844 — chosen sample 2, rejected sample 1

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Chosen summation omits Kit-Kats and fails to subtract the 5 gifted lollipops; those errors cancel and the numeric total is coincidental.
- Reference numeric answer: `49`
- Chosen/rejected token gap: `10`

**Question:**

```text
Question: After trick-or-treating, Brent dumped his candy on the table.  He had received 5 Kit-Kat bars, three times that amount in Hershey kisses, 8 boxes of Nerds,  and 11 lollipops.  He also had 10 Baby Ruths and half that amount in Reese Peanut butter cups.  After giving his little sister 5 lollipops, how many pieces of candy did Brent have left?
Answer:
```

**Chosen response:**

```text
He had received 3*5=15 Hershey kisses.
After giving 5 lollipops, he has 8+11+15+10+5=49 pieces of candy.
The answer is 49.
```

**Rejected response:**

```text
Brent had 5 x 3 = 15 Hershey kisses.
So he had 15 + 8 + 10 = 33 pieces of candy.
This means he had 33 - 5 = 28 pieces of candy left.
The answer is 28.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 4846 — chosen sample 3, rejected sample 0

- Decision: `REJECT_MECHANICAL`
- Reviewer note: No pair passed exact frozen arithmetic, eligibility, terminal-answer, and length-gap gates.
- Reference numeric answer: `4096`
- Chosen/rejected token gap: `14`

**Question:**

```text
Question: Under standard growth conditions, the bacterial strain, E.coli, has a doubling time of 20 minutes.   If 1 single bacterial cell is used to start a culture grown under standard growth conditions, how many bacterial cells will there be after the culture is grown for 4 hours?
Answer:
```

**Chosen response:**

```text
First, we have to convert the 4 hours to minutes.
4 hours * 60 minutes/hour = 240 minutes
We divide 240 minutes by the doubling time of 20 minutes to get the number of doubling cycles in 4 hours.
240 / 20 = 12 cycles
This means that the number of bacterial cells is 2 to the 12th power, which equals 4,096.
The answer is 4096.
```

**Rejected response:**

```text
First calculate how many minutes are in 4 hours: 4 hours x 60 minutes/hour = 240 minutes
Now divide that time by the doubling time: 240 minutes / 20 minutes = 12
This means that there will be 12 doubling times to go before there is a full doubling. Each doubling means there is a double amount of bacteria, so we multiply the number of doubling times by 2: 12 doubling times x 2 bacteria/doubling time = 24 bacteria
The answer is 24.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 5745 — chosen sample 0, rejected sample 1

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Response claims a 10-minute handstand and a 5-minute rest each contain 60 minutes, then treats the 15-minute cycle entirely as handstanding. Material temporal explanations contradict the problem.
- Reference numeric answer: `8`
- Chosen/rejected token gap: `7`

**Question:**

```text
Question: Barry stands on his head for 10 minutes at a time, but then he must sit for 5 minutes before he can take another turn standing on his head.  How many turns can Barry take standing on his head during a single 2-hour period?
Answer:
```

**Chosen response:**

```text
There are 120 minutes in a 2-hour period.
There are 60 minutes in a 10-minute stand on his head.
There are 60 minutes in a 5-minute sit.
Barry stands on his head for 10 minutes at a time and then sits for 5 minutes.
That means he stands on his head for a total of 10 + 5 = 15 minutes of standing on his head.
In a 2-hour period, there are 15 minutes standing on his head per turn.
So, he can stand on his head for 120 / 15 = 8 turns.
The answer is 8.
```

**Rejected response:**

```text
There are 60 minutes in an hour, so a 2-hour period is 2*60=120 minutes.
If Barry stands on his head for 10 minutes at a time, he stands on his head 120/10=12 times.
Each time he stands on his head, he sits 5 minutes before taking another turn standing on his head, so after standing on his head 12 times, he has a total of 12*5=60 minutes sitting.
Therefore, he can stand on his head 12-60=12 times.
The answer is 12.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

## Source 7443 — chosen sample 3, rejected sample 1

- Decision: `REJECT_MATH_OR_MATERIAL_RELATION`
- Reviewer note: Response initially claims mother is 74-50=24 years old, confusing parent-child age gap with mother’s present age. Later self-correction gives 72 and final 22, but prior relationship is materially false.
- Reference numeric answer: `22`
- Chosen/rejected token gap: `34`

**Question:**

```text
Question: Harry is 50 years old. His father is currently 24 years older than he is. How old was his mother when she gave birth to him if she is younger than his father by 1/25 of Harry's current age?
Answer:
```

**Chosen response:**

```text
His father is 50 + 24 = 74 years old.
His mother is 74 - 50 = 24 years old.
If his mother is younger than his father by 1/25 of Harry's current age, his mother is 1/25 * 50 = 2 years younger than his father.
His mother is 74 - 2 = 72 years old.
His mother was 72 - 50 = 22 years old when she gave birth to him.
The answer is 22.
```

**Rejected response:**

```text
Harry's father is 50+24 = 74 years old.
His mother is 74-24 = 50 years younger than his father.
The mother is 50-50/25 = 20 years younger than Harry.
So the mother was 50+20 = 70 years old when she gave birth to Harry.
The answer is 70.
```

**Independent QC:** [ ] arithmetic/relation acceptable  [ ] material flaw  [ ] uncertain

**QC notes:**

---

