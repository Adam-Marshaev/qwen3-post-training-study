# E003 — 124-Pair Second-Pass Advisory Review

- Uploaded review document SHA256: `af257bd6315a5645dde5574394b40309f6c9fb5ca0d046ef0022d3fa321e6fbf`
- Declared original candidate dataset SHA256: `83216697cf1d4293e735de6ca2832a21b2dc13e06fc07eeb87fb583e3fbe1a42`
- Review basis: **rendered review document only**; frozen host dataset was previously audited but not available here.
- No new independent human signoff, dataset approval, or DPO training authorization.

## Recommendation tally

| Status | Pair count |
|---|---:|
| RECOMMEND_FOR_INDEPENDENT_SIGNOFF | 108 |
| RE_REVIEW_REQUIRED | 4 |
| EXCLUDE_INITIAL_LENGTH_THRESHOLD | 11 |
| PREEXISTING_PAIR_APPROVAL | 1 |

## High-priority source decisions

### Source 2738: RE-REVIEW REQUIRED

Chosen says "$4.50 in total in her wallet" despite bills also present; arithmetic $40+$15+$4.50-$17.50=$42 is correct. Clarify whether this is an innocuous reference to coins or a contradictory statement.

### Source 4320: RE-REVIEW REQUIRED

Chosen states 6*3=18 "m*square meter", an invalid area unit; ensuing area/paint/labor arithmetic gives $192. Decide whether unit-expression error invalidates chosen reasoning.

### Source 5819: RE-REVIEW REQUIRED

Chosen explicitly says "Each corn plant needs 15 x 0.5 = 7.5 gallons". That is false per plant; 7.5 gallons is the demand of 15 plants in one row. Later total and time are correct (75 gallons, 25 min).

### Source 6288: RE-REVIEW REQUIRED

Chosen says "When she added 83 plates" even though 83 is the total at collapse; then computes 83-(27+37)=19. Decide whether the statement is a material total-versus-increment contradiction.

## Non-blocking wording warnings

- **528:** Chosen calls the 7 purchased bikes/off-road vehicles "7 trucks". Vehicle count and monetary arithmetic are correct; lexical category slip should be noticed.
- **3012:** Chosen calls the three slices Amber eats part of the slices "to give away"; the combined 19 consumed slices and final 5 remaining are arithmetically correct.
- **5903:** Question has awkward wording ("four times the number of lattes as it did teas"); chosen follows intended four-times-teas-plus-eight interpretation.
- **6515:** Chosen counts 3 people x 3 nights = 9 person-nights but loosely calls them "9 nights". Multiplication and $360 cost are correct.

## Sources excluded by proposed length threshold

1870, 3419, 3869, 4200, 4457, 5828, 5885, 6190, 6576, 7217, 7284

This exclusion is a proposed policy for an initial bounded run; it is not a reason to relabel the frozen data. Absolute gap alone cannot establish signed length bias.

## Full pair-by-pair decision index

| Source | Pair (chosen > rejected) | Absolute token gap | Chosen answer | Rejected answer | Advisory status |
|---:|:---:|---:|---:|---:|---|
| 5 | 3 > 2 | 21 | 35 | 32.5 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 81 | 2 > 1 | 28 | 14 | 11 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 144 | 1 > 3 | 5 | 8 | 68 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 158 | 2 > 1 | 7 | 6 | 18 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 376 | 1 > 3 | 14 | 7 | 27 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 434 | 0 > 1 | 10 | 80% | 125 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 468 | 1 > 0 | 8 | 504 | 1202 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 485 | 3 > 0 | 4 | 63 | 9 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 528 | 1 > 2 | 6 | 1825 | 1750 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 552 | 1 > 0 | 28 | 16000 | 1600000 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 557 | 0 > 2 | 7 | 42 | 21 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 755 | 2 > 0 | 9 | 12 | 24 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 780 | 0 > 3 | 37 | 72 | 36 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 784 | 1 > 3 | 11 | 81 | 54 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 815 | 2 > 3 | 6 | 6 | 10/3 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 853 | 3 > 1 | 5 | 6 | 36 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1035 | 1 > 2 | 7 | 960 | 480 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1150 | 0 > 3 | 23 | 1140 | 1330 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1219 | 1 > 0 | 3 | 37 | 34 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1357 | 2 > 1 | 4 | 140 | 0 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1429 | 3 > 2 | 7 | 20 | 1150 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1438 | 2 > 3 | 31 | 5 | 80 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1520 | 1 > 0 | 13 | 8 | 0 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1576 | 0 > 1 | 16 | 27000 | 42000 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1767 | 2 > 0 | 2 | 150 | 195 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1859 | 3 > 2 | 3 | 2100 | 1100 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1870 | 0 > 2 | 50 | 80 | 120 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 1889 | 0 > 1 | 11 | 680 | 740 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1920 | 2 > 3 | 18 | 2 | 4 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 1927 | 1 > 2 | 22 | 9400 | 8250 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2125 | 2 > 0 | 18 | 18 | 21 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2277 | 3 > 2 | 4 | 11 | 9 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2477 | 0 > 1 | 19 | 52 | 108 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2491 | 3 > 1 | 7 | 212 | 182 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2717 | 3 > 1 | 6 | 1591 | 1691 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2731 | 0 > 3 | 9 | 56 | 68 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2738 | 3 > 2 | 6 | 42 | 41 | RE_REVIEW_REQUIRED |
| 2786 | 3 > 1 | 29 | 80 | 120 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2860 | 0 > 1 | 12 | 9 | 1.5 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 2909 | 0 > 1 | 2 | 88 | 98 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3012 | 2 > 3 | 39 | 5 | 24 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3027 | 3 > 1 | 14 | 81 | 75 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3087 | 3 > 2 | 9 | 2 | 12 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3181 | 3 > 1 | 0 | 20 | 2 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3287 | 0 > 2 | 8 | 650 | 850 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3419 | 3 > 1 | 53 | 5 | 2 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 3530 | 0 > 1 | 34 | 75 | 15 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3612 | 1 > 0 | 14 | 108 | 36 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3674 | 1 > 3 | 8 | 62 | 64 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3676 | 1 > 0 | 17 | 48 | 32 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3785 | 0 > 1 | 14 | 95 | 90 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3869 | 2 > 0 | 66 | 19 | 21 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 3912 | 3 > 1 | 1 | 20000 | 13640 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3948 | 3 > 2 | 0 | 250 | 290 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 3992 | 1 > 0 | 11 | 480 | 640 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4067 | 1 > 2 | 8 | 110 | 34 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4156 | 2 > 3 | 11 | 18 | 14 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4168 | 1 > 3 | 6 | 72 | 122 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4200 | 1 > 0 | 41 | 75 | 135 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 4275 | 1 > 2 | 3 | 600 | 0 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4317 | 3 > 1 | 6 | 12 | 16 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4320 | 0 > 2 | 2 | 192 | 168 | RE_REVIEW_REQUIRED |
| 4324 | 3 > 0 | 5 | 1 | 2 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4446 | 2 > 1 | 1 | 52 | 50 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4457 | 0 > 3 | 48 | 105 | 10 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 4499 | 0 > 3 | 29 | 15 | 50 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4500 | 1 > 3 | 3 | 13 | 15 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4503 | 0 > 2 | 9 | 32 | 8 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4674 | 1 > 2 | 2 | 72 | 78 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4775 | 0 > 2 | 25 | 8 | 1 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4821 | 0 > 2 | 3 | 482 | 582 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4830 | 1 > 0 | 11 | 100 | 90 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4847 | 2 > 3 | 6 | 3 | 12 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 4997 | 2 > 3 | 12 | 20 | 5 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5008 | 3 > 1 | 2 | 56 | 48 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5200 | 2 > 1 | 6 | 250 | 500 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5341 | 2 > 3 | 2 | 10 | 4 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5436 | 2 > 0 | 28 | 50 | 55 | PREEXISTING_PAIR_APPROVAL |
| 5509 | 3 > 2 | 8 | 36 | 32 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5611 | 0 > 2 | 2 | 58 | 64 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5625 | 1 > 2 | 1 | 30 | 25 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5679 | 1 > 0 | 2 | 2 | 0.4 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5721 | 2 > 1 | 17 | 7 | 9 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5727 | 0 > 1 | 29 | 273 | 78 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5741 | 1 > 2 | 29 | 96 | 144 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5819 | 3 > 2 | 4 | 25 | 135 | RE_REVIEW_REQUIRED |
| 5828 | 0 > 2 | 47 | 94 | 294.0625 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 5885 | 1 > 3 | 57 | 15 | 1080 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 5903 | 2 > 1 | 7 | 32 | 28 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 5980 | 1 > 2 | 15 | 120 | 240 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6000 | 2 > 0 | 3 | 4 | 16 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6006 | 3 > 2 | 7 | 90 | 210 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6015 | 3 > 1 | 1 | 65 | 5 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6030 | 0 > 1 | 1 | 135 | 1440 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6047 | 0 > 2 | 33 | 99 | 103 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6103 | 3 > 0 | 8 | 24 | 8 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6117 | 2 > 0 | 20 | 24 | 40 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6159 | 2 > 1 | 2 | 210 | 150 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6190 | 0 > 2 | 54 | 62 | 2 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 6194 | 0 > 3 | 16 | 67 | 50 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6204 | 1 > 3 | 0 | 38 | 50 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6208 | 0 > 3 | 1 | 44 | 96 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6239 | 1 > 0 | 20 | 41 | 48 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6288 | 0 > 1 | 0 | 19 | 147 | RE_REVIEW_REQUIRED |
| 6297 | 2 > 1 | 3 | 222 | 192 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6354 | 1 > 2 | 3 | 21 | 5 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6389 | 3 > 2 | 14 | 34 | 2 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6404 | 2 > 3 | 1 | 10 | 1 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6485 | 3 > 0 | 4 | 35 | 44 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6515 | 0 > 2 | 5 | 360 | 480 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6525 | 3 > 2 | 4 | 16 | 20 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6576 | 3 > 1 | 66 | 13 | 12 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 6655 | 1 > 2 | 2 | 20 | 5 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6726 | 0 > 1 | 16 | 22 | 21 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6771 | 2 > 0 | 1 | 70 | 350 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6804 | 1 > 2 | 14 | 24 | 22 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 6959 | 0 > 1 | 4 | 3 | 2 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 7189 | 2 > 3 | 39 | 52 | 56 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 7207 | 1 > 3 | 29 | 95 | 105 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 7210 | 0 > 3 | 17 | 4 | 2 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 7217 | 3 > 2 | 112 | 9800 | 14000 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |
| 7251 | 0 > 1 | 39 | 1800 | 1200 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 7259 | 3 > 1 | 7 | 46 | 100 | RECOMMEND_FOR_INDEPENDENT_SIGNOFF |
| 7284 | 3 > 1 | 57 | 16 | 21 | EXCLUDE_INITIAL_LENGTH_THRESHOLD |

## Authorization boundary

- `RECOMMEND_FOR_INDEPENDENT_SIGNOFF` is an assistant advisory recommendation, **not** human approval.
- The four `RE_REVIEW_REQUIRED` records are new second-pass warnings, **not** edits to prior advisory manifests.
- Source 5436 had separate prior human approval, but the uploaded generic review template says `PENDING` under each pair. That placeholder does **not** supersede its versioned approval.
- The source document omits complete per-response token counts and eligibility/EOS fields; those remain dependent on the earlier host-side audit.
- Do not construct a training-ready dataset or start DPO/GRPO without independently documented signoff and training authorization.
