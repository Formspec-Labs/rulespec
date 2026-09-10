# Fixed-statement enrichment: structure added without rewriting

**The separate step passed the bounded actor/link and no-rewrite checks. It did
not demonstrate higher overall extraction accuracy.** Six fresh calls compared
current extraction (B), a combined actor/index first pass (I), and enrichment of
B's fixed statements (E). Each strategy saw the complete source: the passport
document and a new constructed document with two different meanings of RN.

No production code, schemas, UI run or review history changed. All six calls are
complete; there were no retries, audits or repairs.

## Meaning and structure

E correctly added all ten directly checked actors across the two documents,
with accepted Core evidence, and kept the checked unstated actors null. It
supplied both passport terms and both scoped RN senses, with supported names,
aliases, defining claims and usage links. The application RN and inspection RN
share the name “review notice” and acronym “RN”; they received distinct IDs and
the right local uses. No defined term was invented for the unexplained ZX code.

I also passed the directly checked actor and term-link checks. It assigned an
actor to the passive IN alteration restriction; E left that actor null. This
less explicit role was declared separately from the ten directly checked actors.
That difference prevents claiming identical or exhaustive actor coverage.

All 23 B rows retained every original field when E was applied, including
statement wording, kind, modality, source selection and prior enrichment. The
model response has no statement field; a deterministic merge accepts only the
four added fields for existing claim IDs. Original B captures and Core records
remain separate from derived enriched records. Identity changes caused by added
meaning are not an in-place review-history migration.

Blinded statement review found:

| Source, 8 named checks each | B | I | B + E |
|---|---:|---:|---:|
| Passport | 8 | 8 | 8, inherited unchanged |
| Scoped controls | 7 | 8 | 7, inherited unchanged |

The earlier Posts qualification failure did **not** recur in this fresh I call:
both B and I retained local modifications in the independent requirement. This
weakens any claim that adding actor/index fields reliably causes that failure.

The scoped B output added a condition to this source sentence:

> You must retain a copy of the approval email.

Its extracted statement was:

> Within equipment inspections, where an RN is archived with manager approval,
> you must retain a copy of the approval email.

The source establishes which approval email is meant, but does not explicitly
condition retaining it on actually archiving the RN. Approval could arrive even
if archival never occurs. E preserves this added condition because it cannot
rewrite statements; I avoided it. The judgment is interpretation-sensitive: if
the added phrase is read as background rather than a condition, the remaining
seven scoped checks pass in every strategy. Under neither reading does E show
a measured overall accuracy gain.

E linked that email statement to equipment RN through context. The plan explicitly
allowed this supported contextual reading while assessing direct mentions
separately. A link does not repair or justify an added statement condition.

## Cost of the complete strategies

| Source | I reported total tokens | B + E total tokens | Increase |
|---|---:|---:|---:|
| Passport | 5,591 | 6,641 | 18.8% |
| Scoped controls | 4,025 | 5,118 | 27.2% |
| Total | 9,616 | 11,759 | 22.3% |

B + E used 4,147 output tokens versus I's 5,427: **23.6% less output**. Its input
grew from 4,189 to 7,612 tokens because the extra call reads the source and fixed
claims. E alone used 3,423 input and 1,742 output tokens across the two documents.
The experiment's predeclared budget gate was at most twice I's reported total
tokens; both cases passed. Token totals are not dollar costs: input/output prices
can differ, and no pricing or invoice claim is made.

Summed request durations for B + E were 7.77 seconds for passport and 8.07 for
scoped controls, versus I's 6.93 and 5.44 seconds. These exclude local processing
and are one sample per cell, not a latency benchmark. All six calls used
`gemini-3.8-flash`, temperature 0, low thinking and 16,384 maximum output tokens.

## What the result supports

- **Bounded improvement:** missing structure can be added to already extracted
  statements with an enforced no-rewrite boundary. The two-sense RN test worked.
- **No measured overall accuracy improvement:** B + E inherited a B error that
  the fresh I output avoided. The previous I regression did not repeat.
- **Bounded cost tradeoff:** less output, an extra source-reading call, and 22.3%
  more reported total tokens here. This passes the chosen experimental budget.

Retain E as a candidate enrichment step for existing or reviewed extracts.
These results do not justify a default pipeline switch or a claim that separate
passes are generally more accurate. Enrichment and correction remain separate
decisions: preserving a statement protects both its correct meaning and any
existing mistakes. Do not add source-specific prompt patches to chase either
observed qualification issue. The next adoption decision needs representative
actor/link coverage and the intended use of already reviewed records.

## Verification and reconstruction

All six actual requests matched their expected native CUE-generated schemas,
prompts and settings. Four extraction responses yielded 47 accepted records;
the two enrichment responses produced 23 enriched versions, not 23 additional
source meanings. All six Core checks passed. Claim IDs matched exactly once;
term IDs, aliases, source references and definition/usage links passed integrity
checks. No model call was made by parsing or replay.

Constructed pre-call merge checks verified unchanged fields and rejected missing,
duplicate and unknown claim IDs, plus a forbidden statement field. Offline replay
verified all six exact requests and processing results and the no-rewrite
invariants. Mechanical checks do not establish source meaning or completeness.

[Plan](PLAN.md), [criteria](REVIEW.md), [sources](sources), [schemas](schemas),
[captured requests/responses](runs), [opaque statement views](blind),
[blinded judgments](statement-review.json), [actor/link judgments](structure-review.json),
[metrics](metrics.json) and [manifest](manifest.json) retain the evidence.
Review judgments come from one model reviewer and are revisable. Passport is
development data; the new scoped document is constructed, not an independent
benchmark. One call per cell cannot establish rates or causation.

The runner reuses the preceding experiment's pinned helper, existing capture,
parser, evidence resolver and Core compiler. Actor types come from canonical
CUE; the term index reuses the preceding experimental definition unchanged.
Existing refinement permits complete record edits, so it does not supply this
fixed-field boundary. Term links remain experimental data, not new Core types
or production relationships. A later implementation should use existing Core
concepts, labels, aliases, evidence and explicit relationship assertions.

Use base commit `e43f4b2` with the saved actor-definition helper and both experiment
directories. Runtime, helper and input hashes are checked rather than silently
updated:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python \
  examples/document_understanding/fixed-enrichment-check/run.py replay
```
