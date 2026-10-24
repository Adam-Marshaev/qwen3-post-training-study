# E004-P2 arithmetic-first advisory review v1

**Status:** screening completed; **0 training-approved pairs**. No model training or additional GPU inference. Original P2 run unchanged.

## Frozen evidence

- P2 250-question source pool Git revision: `f543aa41ff917d96b8f26b38df9c6c00f91b1619`.
- P2 original 1,000-candidate JSONL SHA256 (verified on user GPU host): `568b15094c755f73f240a0fcd91deb601ba48c1914d4e9fb2d7647573ce6bf79`.
- Uploaded P2 137-group compact JSONL SHA256 (verified locally): `fe4c4f034417b73be7862975889e102882be6d9f67352d62b9a568eaeb66faf9`.
- The P2 screen forks the frozen E004-P1 mechanical screen only by changing P2-specific SHA256 pins, group count 135→137, report schema name, and version label; tests assert byte-exact transformation.

## E004-P2 outcomes

| Stage | Source groups |
|---|---:|
| Pilot training questions | 250 |
| Mixed groups with eligible correct and incorrect outputs | 137 |
| Mixed groups having any chosen/rejected token gap ≤40 | 130 |
| Passing the **full** frozen mechanical screen | 87 |
| Rejected by frozen mechanical gates | 50 |
| Manual material-relation or question-ambiguity holds among the 87 | 7 |
| **Arithmetic-first provisional pairs** | **80** |
| **Independently certified / authorized training pairs** | **0** |

**P2 provisional yield:** 80/250 = **32.0%** of generated questions; 80/137 = **58.39%** of mixed groups. P1 reference: 83/250 = **33.2%**, using its own source-specific assistant review. Combined P1+P2: **163 provisional, 0 independently certified**. These are training-partition data, not held-out generalization metrics.

## Advisory holds with materially wrong mathematical relationships

These **seven P2 source-specific judgment calls are not automatic rules** and must not be transferred to P3 by source ID.

| Source | Substantive concern |
|---|---|
| **658** | Two store prices denominated in USD and EUR are subtracted without an exchange rate. |
| **660** | Duke's half-as-many count is changed from 2 to 6; Abe is omitted in the final sum. The number happens to match. |
| **979** | Kyle's distance increase is calculated from Grant's *increment* rather than Grant's total distance, accidentally yielding the required difference. |
| **2760** | The chosen age solution sets the father's later age to double his current age, which does not solve the given father/son relationship; 27 occurs coincidentally. |
| **4844** | The final candy summation omits the Kit-Kats but also fails to subtract the gifted lollipops; errors cancel. |
| **5745** | A 10-minute activity and 5-minute rest are each described as lasting 60 minutes; the response labels a 15-minute cycle entirely as handstanding. |
| **7443** | The solution first derives the mother's current age as 74−50=24, an invalid relationship, before later obtaining her actual age 72 and the reference final answer. |

Examples **retained** under the relaxed policy despite awkward/mislabeled explanatory prose include sources **3230** (giraffe/elephant revenue label), **3804** (shortage sign wording), **3945** (people called pizzas), **4392** (neighborhoods called streets), **4507** (weeks called days), and **6977** (boys total mislabeled present students). In these cases the quantitative operations still lead to the intended numeric answer. No attempt was made to rewrite any response.

## QC sample: reproducible, NOT independently adjudicated

The immutable seed is `20261024` with Python `random.Random`, sampling from source-index-sorted decisions. The accepted worksheet contains **30 random provisional accepts**. The rejected worksheet deliberately includes **all seven material holds and three random mechanical rejects**; it is **not a representative random sample of rejected groups**. Both worksheets contain the complete question, chosen and rejected responses, frozen decision, and empty independent-QC fields. They are unreviewed sign-off worksheets.

Assistant screening of the candidate pool and a follow-up check of selected examples did not reveal another clear *material* arithmetic failure in the 30 provisional accepts, but **this is the same assistant, not independent QC**, and does not establish the critical-error rate. A human or independent reviewer should classify each sampled example as acceptable, material error, or uncertain. No examples are training-approved until the user explicitly signs off.

## Limitations and next gate

- A correct terminal number, two verified equations, and an EOS stop **do not prove correct reasoning**.
- The 80 provisional pairs are chosen from different source questions than P1's 83. Baseline greedy results for P2 were **not** evaluated; do not assert P2 greedy-error coverage.
- Frozen P1 source-specific exclusion decisions were never applied to P2.
- No official GSM8K test set was used; P2 questions come from the frozen training partition.
- After independent 30+10 QC and explicit approval of a scaling plan, P3 generation may be considered. **No DPO or GRPO training has been authorized.**
