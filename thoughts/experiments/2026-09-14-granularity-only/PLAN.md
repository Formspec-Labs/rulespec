# Isolate the list-granularity instruction

Decision: is the granularity sentence itself a useful improvement to the current
separate-section extraction prompt? The user requested this test after the grouped
comparison. No production change, adoption or commit is part of this experiment.

Observed: a grouped drug-record request produced individually referenceable list
contents while its separate control bundled them. Grouping also combined an entire
aviation signal table. The current prompt and CUE schema already request independent
meanings; the additional sentence specifically emphasizes distinct list-child
actions. Its effect was previously bundled with shared context and task identities.

Hypothesis: that sentence alone consistently separates independent drug-record
contents while preserving their inherited scope and connected alternatives.
Alternative explanations: shared-section context/task framing caused the effect,
or ordinary generation variability explains the prior difference. If the sentence
alone succeeds, grouping is not necessary on these cases. Failure cannot distinguish
the other explanations. This is a targeted mechanism test on known cases, not a
new-document benchmark or a claim about hidden model reasoning.

Arms: A is the exact current one-section prompt. B inserts exactly this sentence
immediately before the passage catalog:

> Keep independently actionable duties as separate records, including list children that require distinct actions.

Everything else stays the same: source text, section index, focus/context ranges,
passage IDs/coordinates, current CUE schema, examples, parser, model settings and
output allowance. No task IDs, batching language, table-specific hint or other
new instruction is added. Actual requests must differ only by that one sentence
and its separator newline.

Cases, all reused unchanged from 2026-09-14-grouping-fresh:

- 21 CFR 211.188: primary known case; two repeats per arm. Check D1–D6 from the
  prior EXPECTATIONS.md. All thirteen content meanings must be independently
  referenceable with batch-record/significant-step framing. Check the automated-
  equipment/personnel alternative and no invented body for cited 211.68/211.134/
  211.192; 211.192's body is not supplied to this one-section request.
- 14 CFR 91.125: table counterexample; one repeat per arm. Check every A8 mapping
  and aircraft setting. One complete record per signal or per setting is acceptable;
  one omnibus table record does not meet the referenceability target. No table-
  specific improvement is presumed from an instruction about duties.
- 14 CFR 91.123: one repeat per arm. Check A1–A7 and their counterexamples: three
  deviation exceptions stay alternatives, cancellation stays permission, and the
  conditional 48-hour report does not absorb the separate prompt-notification rule.
- 45 CFR 164.312: one repeat per arm. Check H1 and H8–H14, keeping Required/
  Addressable, external 164.306 qualification, appropriate/as-needed limits,
  and AND/OR alternatives. No imported physical-safeguard conditions.
- CSBG 9914: one repeat per arm. Check C7–C16 and C18 in the earlier source checks:
  four monitoring duties remain separate; local evaluation/report meanings and
  timing survive; assistance is permission and the historical note is not a duty.

The full earlier expectations and C1–C14 source checks are retained by hash and
copied into the blind review packet. Only the selected section's checks apply.
Shared baseline defects remain visible; not every existing gap must be repaired.

Held constant: current installed runtime and authoritative CUE schema;
gemini-3.8-flash, low thinking, 16,384 generation tokens, provider-managed sampling
(no temperature/top_p/top_k); no retries or model audit/refinement. Alternate arm
order across six paired comparisons. At most twelve calls and twenty capture
minutes, retaining an in-flight request up to the existing five-minute timeout.
Repeated calls measure within-case variability, not source diversity. Report
provider tokens and latency without inferring dollar cost or missing thinking use.

Decision rule: a bounded benefit requires the intervention to produce all thirteen
independently usable drug-record contents on both repeats, improve on at least one
contemporaneous control, and introduce no new material omission, wrong modality,
broken alternative, lost governing scope or worse referenceability on the controls.
Show token costs alongside utility: this is not a cost-saving hypothesis, and extra
useful records can justify extra output. Flag repeated non-useful prose separately.
If both arms already succeed, there is no demonstrated incremental benefit. Mixed
repeat results or new meaning regressions mean keep current production and stop;
do not add another prompt patch or expand the call budget after seeing output.

Retain exact requests/responses, failures, native replay and actual-schema/Core
checks. Present randomized unlabeled sets for independent source-based review;
freeze the review before opening the assignment key. These are revisable labels,
not gold. Even a bounded positive result would not establish general adoption.
