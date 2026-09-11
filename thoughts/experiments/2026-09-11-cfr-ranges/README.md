# Complete CFR ranges survive the reader and its consumers

The coordinated change is installed locally. RefSpec preserves complete compound
parts and explicit range endpoints; Rulespec retains the original wording,
endpoint labels and source evidence. Consumers that only understand one part
decline a range lookup instead of silently selecting its first endpoint.

The parser change belongs upstream. Rulespec removes its duplicate CFR display
formatter and uses the native occurrence text. No model-response field, Core
schema, dependency, range enumeration or per-match catalog lookup was added.
The new item scan advances through adjacent tokens. Its standard occurrence scan
uses a constant-time overlap check; alternate spellings retain the preexisting
overlap scan. This is not a claim that the entire parser is linear.

## Measured result

The [design](design.md) and [final direct comparison](run-04/summary.json) preserve
the adoption criteria and results. Original publisher XML is in the preceding
whole-token experiment; this comparison reuses its frozen baseline.

| Check | Before | After |
| --- | ---: | ---: |
| Complete supported part keys, 8,424 constructed OFR index strings | 8,235 | 8,424 |
| Source expectations across eight paragraphs and five variants each | 5/40 | 40/40 |
| Fresh reviewer checks across six additional publisher paragraphs | 2/6 | 6/6 |

The 189 changed index readings are title-41 compound parts. Other index readings
are unchanged. The 40 cases include full paragraph text and formatting/neighbor
variants; they are not 40 independent documents. The [fresh review](fresh-review/README.md)
froze expectations before execution. Its six results are unchanged in the final
installed grammar, verified in [fresh-installed-replay.json](fresh-installed-replay.json).
These selected checks establish bounded representation improvements, not general
extraction accuracy, target existence or legal applicability.

Examples now retained completely include `41 CFR 101-19.600 to 101-19.607`,
`40 CFR parts 1500 through 1508`, and the two parts in
`41 CFR parts 102-193 and 102-194`. Mixed lists and cross-part section ranges
retain both endpoint pinpoints and following members. Incomplete endings,
unsupported hyphen forms and repeated range connectors remain explicit refusals.
A refused ending cannot swallow the title of a following explicit citation.

## Downstream tradeoff

Both Unified Agenda Arrow tables, identity comparisons and joined copies retain
endpoints and refusals. The shared reader can keep one coordinate occurrence
while consuming its qualifiers, so the table needs no deduplication heuristic.
Repeated explicitly written citations stay separate.

The [three-arm authority-note comparison](consumer-delta/summary.json) examined
all 8,240 pinned notes. Compared with the new grammar and old consumer, the new
consumer withholds 170 single-part comparisons: 29 part ranges, 58 section
ranges, 81 unsupported hyphenated-section forms and two ambiguous hyphen forms.
All changed records and their source context are retained. U.S. Code, public-law
and named-act identities are unchanged. The old USC test also had an inherited
one-row drift in its unrelated all-family total; it now pins the intended USC
population, while separate fixtures pin all changed CFR notes.

Flat authority/table rows lack fields for endpoint pinpoints. They retain the
coordinates and raw text with `range_pinpoints_not_represented`, rather than
presenting qualified ranges as complete sections. Native occurrences and the
Rulespec export preserve those labels. Single-part note comparisons retain their
existing coarser interpretation.

## Delivery and limits

- **595 extractor tests pass from source and the installed wheel.**
- **258 focused RefSpec tests pass from the installed wheel.** The upstream
  implementation also passed its source grammar/consumer checks and lint.
- All **406 Python files** in the seven pinned wheels match both installations;
  changed package bytes also match source. Normal CLI reference output and
  discovery data agree across source, isolated and working installations.
- The CLI checks use derived text from the publisher paragraphs and an actual
  supported USLM XML input. This adds no generic eCFR XML ingestion claim.
- Dependency checks pass. **Zero model calls** were made. Nothing was published.

[Wheel inputs](wheel-inputs.json), [isolated checks](delivery-isolated/checks.json)
and [working checks](delivery-working/checks.json) identify the local delivery.
Earlier failed runs remain saved: the first callback refactor had a stale variable;
two source-suite runs detected file drift during concurrent edits; and the first
isolated test invocation lacked the test runner. The final frozen-source run and
installed tests pass. No production assertion was weakened to bypass those failures.

This closes the selected complete-reading gate. The minter still refuses compound
identifiers, and separate graph readers have not been migrated. Unsupported forms
such as `48 CFR 1.301-1.304` remain complete observations with refusal. General
reference resolution and supplying useful target text to extraction remain open.
Prioritize a concrete discovery or workflow consumer before adding more syntax.
