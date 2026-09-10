# Compression with source-reference challenges: cost gain, failed quality gate

**Do not integrate this candidate.** Shared quotations reduced aggregate input
tokens **38.90%** and total tokens **5.03%**, but applied one fewer supported
relationship in a fresh source. Both arms now apply all five railroad links,
including the earlier thin-space failure. The remaining loss is target selection
and all-or-nothing challenge acceptance, not evidence copying.

This compares current committed production A (`39f6c3f`) with the existing
lossless quotation-catalog experiment B. Both use the same current `source_refs`
challenge schema and resolver. No production files changed. There were nine live
calls: one shared extraction and four proposal/challenge pairs, without retries.
All original captures and refused changes remain saved.

| Four comparison calls per arm | A: production input | B: catalog input |
| --- | ---: | ---: |
| Input tokens | 59,912 | 36,604 |
| Answer tokens | 4,413 | 4,687 |
| Thinking tokens | 11,332 | 30,562 |
| Total tokens | 75,657 | 71,853 |
| Summed call duration, seconds | 44.17 | 105.48 |

The fresh shared extraction used 2,810 reported tokens; its thinking-token field
was absent. All nine calls used 150,320 reported tokens. These are token counts,
not dollars. One sample does not establish a stable latency or reasoning-cost rate.

| Case | A final supported links | B final supported links | A / B total tokens |
| --- | ---: | ---: | ---: |
| Saved railroad crossings | 5 | 5 | 62,473 / 43,912 |
| Fresh mobile-phone rule | 1 | 0 | 13,184 / 27,941 |

The aggregate savings hide a large fresh-case total-token increase. Its compact
proposal used 18,255 thinking tokens versus 4,543 in A. The captures establish the
cost difference; they do not explain the model's internal process.

## What survived and what failed

Both railroad outputs copied all original meaning and evidence exactly and changed
only the five exemptions' relationship targets. Both challenges selected source
passages containing the stopping rule, common exemption lead-in and relevant child
paragraph. Thin-space `§ 390.5` resolved to exact source text. Neither arm linked
exceptions to gear shifting, safe-crossing permission or sign-consent duties.
The existing external-reference warning and one existing actor warning remain;
no new component grounding issues appeared in either arm.

The fresh source was [49 CFR 392.82, official 2025 XML](https://www.govinfo.gov/content/pkg/CFR-2025-title49-vol5/xml/CFR-2025-title49-vol5-sec392-82.xml).
Recent experiment/review notes contained no match for this source/topic before
selection. Its shared extraction retained both driver and motor-carrier duties,
the definition of driving, temporary traffic stops, the safely parked exclusion,
and the necessity condition for calls to law enforcement OR other emergency
services. The saved text joins XML text nodes and collapses XML presentation
whitespace before extraction; the original XML is retained. This is not the
production quotation-fallback mechanism. The saved railroad source keeps its
original thin space.

A proposed a companion emergency exception targeting the driver prohibition only.
The challenge supported it and the ordinary review path applied it. B proposed a
single exception targeting both driver and carrier prohibitions. Its challenge
accepted that the source qualifies the driver prohibition, but rejected the whole
proposal because carrier applicability was not explicit. The certain driver edge
was therefore lost alongside the disputed carrier edge. See B's
[raw challenge](cells/cell-00/challenge/attempt-0000.response.json) and
[application result](cells/cell-00/result.json).

Carrier applicability was **preregistered uncertain**, so the result is not a
new claim that the carrier edge is legally wrong. The observable failure is that
one disputed target prevents a separately supported target from being applied.
No unsupported carrier link reached either final result. Neither arm changed any
original statement or condition. B's proposed addition repeated the emergency
phrase across logic/choice/alternative fields, but the rejected addition never
entered the accepted data. A's observation described carrier uncertainty correctly
but used the less precise `already_represented` label; this is not completeness.

## Decision and limits

The cost gate passed. The final-useful-output gate failed: A retained six expected
links and B five. Retain compression as an experimental candidate. An adoption
restricted to the railroad case or large packets would be a new decision, not a
passed version of this broader gate.

One sample per arm/case cannot establish that compression caused the target
selection difference. B's wrapper also changes challenge serialization order:
the identical passage catalog is inside the encoded bundle rather than in A's
source-first prefix. The actual tested intervention is that complete input-encoding
bundle. Exact recursive reconstruction proves unchanged information, not equivalent
model behavior. Review used shuffled arm-hidden outputs, with judgments saved
before revealing labels; it remains partial same-agent blinding, not independent
gold evaluation. No full audit or general completeness claim is included.

The concrete next hypothesis is to judge qualification targets independently,
using existing aliases and source references, so rejecting an uncertain edge does
not discard a supported edge. This is separate from compression and is not
implemented here. Link additions may still require companion exception records
because the production relationship pass correctly preserves existing permissions.

## Saved evidence and checks

- [Preregistered plan](PLAN.md), [alias expectations](expected.json), frozen
  [runtime/source design](design.json), and [paired inputs](cells-design.json).
- [Sixteen imported counterexamples](preflight.json): exact reconstruction,
  distinct positions/roles, overlaps, Unicode, AND/OR, and invalid references.
  Every B proposal and challenge round-tripped exactly during execution and replay.
- [Manual review before arm reveal](BLIND-REVIEW.md), [reading copies](blind-results.json),
  and [usage, preservation and grounding assessment](assessment.json).
- [Zero-call replay](replay-checks.json) reproduced proposal/check decoding and
  exact request prompts/schemas. Runtime fingerprints matched; request settings
  were verified as identical across arms. ReviewStore reloads and discovery exports
  matched saved outputs, and all original meaning/evidence fields remained equal.
  This replay does not independently reconstruct every applied review event.

All evidence is under this directory. The catalog is imported from the earlier
experiment without changes; prior captures and production code remain untouched.
