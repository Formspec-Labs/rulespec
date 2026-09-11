# Named-act resolution: preserve multiplicity and require complete page evidence

Implemented upstream in RefSpec and installed in Rulespec on 2026-09-11. A
single Table III classification no longer wins over multiple source-credit
targets. A single known page outside a named division is excluded, while unknown
or shortened page spellings cannot establish that exclusion. Existing lookup
results retain their source and uncertainty; no model prompt or Core schema changed.

## Why these changes earned adoption

The [preregistered comparison](design.md) separated the page rule from the
multiplicity rule. [Baseline data](baseline.json) contains 8,174 distinct native
act-name/section lookups: all 6,569 reachable source-credit pairs, the first 1,000
of 562,243 eligible single-row/outside pairs, and all 608 publication-derived
pairs, with overlap removed. These are diagnostic index questions, not 8,174
observed citations, documents or independent accuracy labels.

The baseline selected a unique identifier despite multiple source-credit targets
in 29 act-name/section lookups, representing **7 distinct law/division/section
keys**. Inspecting only the earlier 608 publication pairs had found none of these.
The wider population also exposed 58 conflicting source answers. The previous
zero-conflict observation remains true of its narrower population.

| Arm | Changed lookup results | Selected answers with multiple credit targets |
| --- | ---: | ---: |
| Baseline | — | 29 |
| Complete-page exclusion only | 1,085 | 7 |
| Multiplicity refusal only | 29 | 0 |
| Both changes | 1,092 | 0 |

The [comparison](comparison.json) retains every changed before/after result and
all combined results. Changes passed the declared predicates; their count is not
a count of independently reviewed legal errors. Across the 608 published authority
pairs, **no selected identifier changed**. SECURE section 127's refusal changed
from an unexpressible USC note to a classification outside the named division.
All 8,174 existing source-credit target lists remain unchanged.

## Raw source checks

- **PL 104-201, section 1416:** the [Table III XML](raw-104-201-0.xml) names
  USC 50:2316 for the section and child-section classifications in other titles.
  The pinned USLM credits name section 1416(a)(1) for [USC 10:282](uslm-t10-s282.xml)
  and section 1416(c)(1)(A) for [USC 18:175a](uslm-t18-s175a.xml). The direct
  classification is real, but it is not a unique section-level answer.
- **Energy Act section 8004:** [Table III](raw-116-260-1.xml) gives page 1816,
  outside its named division's conservative bounds of 2418–2615. Source credits
  retain two USC 42 targets. The resolver now declines to select the unrelated
  table classification.
- **SECURE section 127:** [Table III](raw-117-328-2.xml) gives page 4660, outside
  division T beginning at 5275. The four source-credit candidates remain visible.
- The producer already retained shortened page spellings in `quarantine.parquet`.
  The selected population intersects 33 such rows, including lists and compound
  numbers such as `3009-454`. The fix consumes that evidence instead of assuming
  the stored first integer represents the entire page designation.

[Index context](raw-index-context.json) records neighboring Table III rows.
[Credit context](raw-credit-context.json) records the source-credit text and pinned
archive/member identities. The USLM section files are explicitly labeled XML
serializations; the original archive remains pinned. Its location under an
annual-source directory does not make release point 119-102 an annual edition.

## Small production changes

- RefSpec's existing `ActIndex` reads the sealed quarantine table and records
  which act/section page values were shortened. Classifications and quarantine
  must belong to the same admitted artifact. Missing or mixed files fail loading.
- The existing Table III check applies exclusion independent of row count, only
  when all relevant pages are complete and outside the conservative bounds.
  Surviving in-range rows are not used to choose among multiple classifications.
- The existing source-composition function returns `act_section_ambiguous` when
  a single Table III candidate meets multiple credit targets. Its identifier is
  retained as optional `table3_candidate_iri`; the credit target records already
  existed. Ordinary results gain no populated extra field.
- Rulespec's adapter adds the newly consumed quarantine file to its input hashes.
  Existing sparse serialization carries the candidate automatically. Source
  fragments, passage IDs, statements, review history and model schemas are reused.

The two exported policy identifiers moved to version 2 because behavior changed.
Input artifacts were not rebuilt or rewritten. Copied prior resolver code remains
the test-only oracle; the comparison checks prior-field parity before applying
each intervention and enumerates deliberate differences. No new citation parser,
page grammar, registry service or mandatory model stage was introduced.

## Verification and delivery

- [391 upstream tests](owner-final.log) and [42 selected caller tests](caller-tests.log)
  passed. New controls cover one/many rows, unknown and shortened pages, inclusive
  boundaries, absent bounds, duplicate targets, agreement/disagreement, and mixed
  artifacts. The earlier evidence-only test now explicitly records the intended
  multiplicity change instead of silently dropping its old control.
- [496 source application tests](application-source.log) and
  [496 working installed tests](application-current.log) passed.
- The [wheel comparison](comparison-wheel.json) equals the direct-source comparison
  for all 8,174 lookups. Seven policy CLI fixture/output files agree exactly between
  source and wheel. Six commands passed outside the checkout in the isolated wheel
  environment, and three more passed in the working environment.
- Earlier 7 qualifier, 9 general-family and 6 named-act cases retain their data.
  Regression comparison excludes only expected parser module hashes and the newly
  recorded quarantine-file digest. All other fields are compared exactly.
- [Package receipts](verification.json) pin six wheels. Both dependency checks
  pass. The working environment is `.tools/document-poc-venv`; the isolated check
  environment is `.tools/reference-integration-20260911-policy`.
- The later [working installation receipt](current-verification.json) rechecks
  six installed modules against source and wheel hashes and compares seven saved
  CLI artifacts with the isolated wheel results. It confirms the saved 496-test
  result and three successful working commands without rerunning those suites.

No model calls, downloads or corpus rebuilds were needed. Original failures and
earlier experiment captures remain intact. Changes are local, uncommitted and
unpublished. This settles the two tested policy questions; broader named-act
ambiguity, qualified references, local context and fresh-document quality work
remain in the [canonical task list](../../plans/2026-09-10-reference-integration-task-list.md).
