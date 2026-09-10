# Explicit target enumeration did not repair the missing link

**No measured improvement; keep production unchanged.** Asking the relationship
pass to consider every existing qualification against every local candidate rule
produced the same seven primary links as the current prompt. Both still missed the
listed-refrigerant-substitutes exemption's link to the local service rule. The new
prompt used 23.1% more total tokens in this small comparison.

| Final applied primary links | Current A | Enumeration B |
| --- | ---: | ---: |
| Refrigerants | 2/3 | 2/3 |
| Seatbelts | 5/5 | 5/5 |
| Incorrect primary targets observed | 0 | 0 |
| Proposed / decoded / prepared / supported / applied edits | 5 / 5 / 5 / 5 / 5 | 5 / 5 / 5 / 5 / 5 |

Every proposed edit applied. The missing edge was never proposed, so a challenge
that verifies only proposed changes could not catch it. Exact passage references
resolved for all ten challenge judgments; quotation copying caused no loss in this trial.

The actual missed refrigerant relationship is C0001 → C0004. The exemption says
listed substitutes/end uses are exempt both from venting and from the requirements
of the subpart. Both outputs link it only to venting C0000. A calls C0004 already
represented; B offers no omission explanation despite the explicit candidate pair.
C0004 already says non-exempt substitutes, so the missing edge limits graph discovery;
it does not prove the existing service duty statement is inaccurate. Neither arm
incorrectly lets the de minimis-release exemption waive service practices/equipment
requirements or excuse knowing post-recovery release.

Both seatbelt outputs correctly connect the part121/125/135 exclusion to briefing,
notification and seating, retaining unless otherwise stated. Dock personnel and
§91.105 exclusions connect only to seating, leaving the two pilot duties binding.
Child-restraint provisions include potentially overriding notwithstanding language;
extra blanket links there were not required positives and were not emitted.

These are historical selected development sources: the exact refrigerant draft from
[evidence-catalog](../2026-09-10-evidence-catalog/README.md), plus the saved full
seatbelt extraction used by [relationship-audit](../2026-09-10-relationship-audit/README.md).
The seatbelt book was loaded through current ReviewStore in an isolated copy and
its packet rebuilt without an audit for both arms; the old book is also retained.
Earlier seatbelt failures are historical, and their improvement here cannot be
credited to B because the contemporaneous baseline already succeeds. No fresh
source or shared extraction was added.

## Intervention and costs

B appends a generic candidate matrix and instructions to check each candidate
pair, permit no supported link, support multiple targets, and preserve unrelated
duties. It receives no expected answers. Source data, original prompt, output
schema, current passage-reference challenge and ordinary decoder/preview/review
application remain the same. This deliberately tests an instruction-plus-matrix
bundle, not a new permanent schema. Actual requests verify the intended addition.

| Provider-reported tokens, four calls per arm | A | B |
| --- | ---: | ---: |
| Input | 55,482 | 56,204 |
| Answer | 5,086 | 5,048 |
| Thinking | 13,199 | 29,542 |
| Total | 73,767 | 90,794 |

Eight calls total, no retries or full audits. Both use gemini-3.8-flash, temperature0,
provider-default thinking and32768 output tokens. No usage fields are missing.
These are tokens, not a bill. One run per arm/case does not establish stable costs,
reliability or generalization. B's extra thinking does not prove more reasoning
improved understanding; there was no observed primary link gain.

All original meaning fields, complete quotations/evidence, identities and review
history survive. Existing component-evidence warnings remain; no new claims were
added. A's two refrigerant already-represented observations and B's two seatbelt
unresolved-reference observations remain recorded. One B observation describes
§91.105 as flight-crewmember rules despite that detail being absent from the supplied
source; it did not enter an applied claim. See the manual review for this limited
unsupported explanation. No observations are silently counted as API failures.

## Decision and reproducibility

The preregistered gate required at least one additional repaired edge, no losses or
false targets, preserved meaning and <=1.5x total tokens. The improvement condition
failed. Explicit candidate enumeration alone did not solve target discovery, and
the output schema did not make per-pair consideration observable. We cannot infer
that the model considered every pair simply because the instruction requested it.
This weakens the proposed prompt treatment; it does not test a separate structured
per-pair decision pass faithfully realized. Do not add another prompt patch or
mandatory production stage on these results.

[PLAN.md](PLAN.md) contains competing hypotheses and frozen criteria.
[REVIEW.md](REVIEW.md) records source/output assessment before arm disclosure,
followed by disclosure. This is partial blinding and revisable same-agent judgment,
not an independent benchmark. [assessment.json](assessment.json) contains exact
costs, final edges, issues and preservation checks. [design.json](design.json) pins
runtime sources, settings, input hashes and randomized cell order. Every raw
request/response is retained under cells/.

Replay matches prompts/schema, proposal decoding and challenge decoding without
provider calls. Separate assessment reconstructs the final snapshot from the
isolated baseline plus saved review events, reloads ReviewStore, checks discovery
export and confirms original semantic/evidence preservation. Those mechanical
checks do not establish semantic completeness.

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-parallel-targets/experiment.py replay
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-parallel-targets/assess.py
```

No production code, default prompt or schema was changed by this experiment.
