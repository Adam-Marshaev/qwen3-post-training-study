# E004-P1 Arithmetic-First Provisional Reclassification

Existing 135 mixed source groups from 250 frozen training questions, 4 draws/question. The **91** previously mechanically passing selected top pairs are the only pairs reconsidered. Source data, sampled outputs, old review rationales, and pair choices are unchanged.

## Summary

| Decision | Count |
|---|---:|
| Provisionally accepted (QC still required) | **83** |
| Rejected: invalid mathematical relationship, coincidental final answer, or material ambiguity | **7** |
| Rejected: negative too incoherent | **1** |
| Rejected: original mechanical gates | **44** |
| Independently verified/approved for DPO | **0** |

This reflects **relaxing subjective wording and messy-negative requirements**, not newly verifying the true reasoning quality of 83 examples.

Hard exclusions for material errors: **1344, 4483, 5588, 6411, 6786, 7019, 7305**. Negative too chaotic: **5932**. See `outputs/decisions_relaxed.jsonl` for explicit reasons and all original issues.

Prior 30-pair QC had eight holds. All eight are currently marked provisional under this **deliberately lenient** policy; their flags are *not erased*, and QC must test whether this tolerance is appropriate. In particular, source 25 has a wrong verb label despite valid missed-ball arithmetic, and source 6632 uses the prompt's stipulated yellow-to-red conversion even though it does not model actual soccer rules.

Potential downside: DPO may reinforce erroneous language when a chosen response has correct arithmetic but mislabeled quantities. The policy is a practical throughput-versus-purity tradeoff, not a claim that this risk disappears.

The frozen E002a baseline showed **51/135** mixed questions greedy-wrong. How many of the **83** provisional pairs are greedy-wrong can be measured by the optional immutable baseline join, rather than inferred from the earlier status-level totals.

## Next gate

Review the generated **30 accepted + 10 rejected** worksheets under the relaxed rule. Rejections from mechanical gates might include useful missed pairs; don't rescue them in this run. A fresh batch after policy freeze is needed to estimate out-of-sample acceptance. No training authorized.
