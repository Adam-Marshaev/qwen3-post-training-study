# E003 M3.9 — Independent Decisions on Three Disputed Groups (v1)

**Status:** append-only human-adjudication overlay; **not training authorization**.  
**Decision date:** 2026-10-22.  
**Basis:** explicit decisions supplied by the project owner in the current conversation.  
**Frozen parent advisory manifest:** `configs/preference/e003_scale256_reasoning_screen24_advisory_v1.json` (unchanged).

## Decisions

| GSM8K training source index | Earlier assistant advisory | Explicit reviewer decision | Current effective status | Rationale / conditions |
| --- | --- | --- | --- | --- |
| **744** | HOLD | **HOLD** | HOLD | Correct numeral, inadequate relative-closing-speed reasoning; no pair selection. |
| **2320** | HOLD | **APPROVE** | PROVISIONAL_APPROVE_WITH_DOCUMENTED_EXCEPTION | Sample 1 is a valid chosen *candidate* for group screening despite one wording slip (says “2 toppings” but uses 2 pizzas × 3 toppings). Reviewer accepts the coherent $50 arithmetic. Rejected sample and final pair remain unselected. |
| **5436** | EXCLUDE | **HOLD pending reference correction; otherwise EXCLUDE** | HOLD_REFERENCE_CONFLICT | Original reference is 55. Literal “between five products” gives four waits, 4×5+30=50. Do not use the group until a separately versioned reference erratum is explicitly authorized, independently reviewed, and regraded. If no such erratum is permitted, EXCLUDE. |

## Working tally over the 24 sampled mixed groups

- **22 provisionally usable:** 21 remain assistant-only advisory approvals; one (2320) has a recorded independent reviewer decision, with a wording exception.
- **2 held:** sources 744 and 5436.
- **0 currently excluded** because 5436 is conditionally held; **5436 must be excluded if reference correction cannot be permitted**.
- A recorded group decision is **not** an approved selected pair, full sample review, or approved DPO training dataset.

## Frozen-data policy for source 5436

The source GSM8K training JSONL, frozen GSM8K split manifest, original 1,024 generated completions, and previous review artifacts must remain byte-for-byte unchanged. The training reference value must **not** be silently edited in place to force agreement. If a correction is justified, create a new **derived, versioned training-only erratum** with its own checksum, independent review, and explicit scope. Regenerate *derived* correctness labels from the original unmodified completions, and audit any resulting preference pair independently. Leave the official test untouched. If the experiment protocol does not permit corrected training labels, mark group 5436 EXCLUDED in the subsequent overlay; do not pretend the original GSM8K data were corrected.

## Approval gates

- 744 remains HOLD.
- 2320 is approved at **group screening** level with a documented exception, *not* as a final preference pair.
- 5436 remains HOLD and is ineligible for pairing pending documented erratum resolution; otherwise EXCLUDE.
- Previous assistant-only judgments on the other 21 groups have **not** been independently signed off.
- No DPO preference dataset has been newly constructed or approved; no training performed; official GSM8K test untouched.

## Provenance

The companion JSON records the SHA256 hashes of the earlier advisory manifest, its report, original selection manifest, review report, and candidate dataset. It contains the reviewer decisions and derived 24-group working statuses. Treat the original review and advisory files as immutable historical artifacts, even when later adjudication differs.
