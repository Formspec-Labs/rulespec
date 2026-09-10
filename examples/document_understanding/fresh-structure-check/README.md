# Fresh actor/definition check and integration decision

Both strategies retained all 15 named meaning checks across two fresh official
eCFR section bundles: 21 CFR 11.3/11.10 and 14 CFR 107.3/107.19. Both indexed all
16 explicit definitions, supplied supported aliases and checked operational links,
and identified 17 actors (13 electronic-record controls and four pilot roles).
No invented terms, swapped aircraft/system senses or approver substitutions were
observed. The unnamed designation actor stayed null.

Neither establishes complete actor/link coverage. Both leave the actor empty
for the passive non-obscuring-record-change and audit-retention clauses despite
the broader regulated-person lead-in. The combined pass also omits a closed-system
term link on the non-obscuring rule, while retaining its electronic-record link.
This is narrower evidence than the full actor/link completeness gate: preserve
uncertainty and do not advertise complete actor or semantic extraction.

| Strategy, both bundles | Input tokens | Output tokens | Total tokens |
|---|---:|---:|---:|
| Combined first pass | 5,482 | 10,557 | 16,039 |
| Baseline + fixed enrichment | 13,748 | 11,181 | 24,929 |

Separate enrichment used 55.4% more reported total tokens here. It preserved all
38 baseline rows exactly; this protects existing content without establishing
that it is correct. All six response/Core checks passed and all six requests and
processing results replayed without provider calls. One call per cell does not
measure a population rate or guarantee that the earlier qualification failure
will not recur. There were no retries or prompt changes after the results.

**Decision:** use combined actor/definition extraction for new drafts, and provide
fixed enrichment for existing/reviewed material. This is a conservative product
decision about useful, source-backed structure and cost, not a claim that the
broader completeness gate passed. Keep unsupported and unavailable components
explicitly unresolved. The application must validate and store source evidence,
use existing Core concepts and relationships, and retain original review history.

Source bodies came from the official rendered eCFR pages, displayed as of
September 4, 2026. XML fetching returned HTTP 406; no XML source was silently
substituted. [Raw web capture](sources/web-capture.txt) and
[normalization notes](sources/retrieval.json) preserve that limitation. The full
selected section bodies were retained; these are not complete regulatory parts.

[Plan](PLAN.md), [pre-call checks](REVIEW.md), [blinded statement judgments](statement-review.json),
[actor/link judgments](structure-review.json), [metrics](metrics.json),
[requests and outputs](runs), and [manifest](manifest.json) preserve the evidence.
The runner reuses the exact preceding experiment's schemas, prompts and processing.
Use base commit `e43f4b2` with the saved actor-definition and fixed-enrichment
helpers for replay; their hashes and the original runtime are checked.

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python \
  examples/document_understanding/fresh-structure-check/run.py replay
```
