# Meaning first, with optional relationship extraction

The meaning-first pass is the strongest next candidate for discovery in this
small trial. It retained more usable content and used fewer tokens. Running a
second relationship pass across every document was expensive and added only
three explicit links. Production defaults remain unchanged.

## Experiment

We made exactly 12 Gemini 3.8 Flash calls at temperature 0: one all-fields call,
one meaning-first call, and one relationship call for each of four excerpts.
There were no retries, repairs, or additional model reviews. Output budgets and
model configuration were held fixed; schema and instructions differed by stage.

The all-fields control uses the prior restored-guidance prompt and attached
qualification schema unchanged. The meaning-first schema selects existing CUE
field definitions for complete statements, kind, modality, scope, context,
alternatives, logical wording, citations, and passage references. Its statements
must already preserve conditions and exceptions. It omits separate concepts,
claimants, normalized values, effective dates, and actor/action/object fields.

The relationship pass receives the original source catalog and accepted first-pass
statements with `B000`-style aliases mapped to existing Core record identifiers.
It can add qualifications but cannot rewrite or replace baseline statements.
Dates and claimant enrichment are outside that pass's scope.

The names and photos excerpts are the familiar development cases. The two new
excerpts were selected before requests and were not used to tailor the prompts:

- [29 CFR 825.110, 2025 edition](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol3/xml/CFR-2025-title29-vol3-sec825-110.xml),
  paragraphs (a)-(b), tests cumulative eligibility conditions, employment breaks,
  exceptions, and counting rules.
- [49 CFR 1540.111, 2025 edition](https://www.govinfo.gov/content/pkg/CFR-2025-title49-vol9/xml/CFR-2025-title49-vol9-sec1540-111.xml),
  tests restrictions with different scopes, local exceptions, and cumulative
  checked-baggage conditions.

The original government XML, selection rules, whitespace transformation, URLs,
and hashes are saved in `source/`. The first-pass meaning checks were frozen in
`review-cases.json` before responses. These are new excerpts for this iteration,
not a claim that their text was absent from model training.

## Results

| Measure | All fields | Meaning first | Meaning plus relationships |
| --- | ---: | ---: | ---: |
| Calls | 4 | 4 | 8 |
| Reported total tokens | 56,476 | 31,913 | 102,097 |
| Documents producing usable records | 3/4 | 4/4 | 4/4 |
| Retained baseline statements | 29 | 38 | Same 38 |
| Explicit qualification links | 13 | 0 | 3 |

Meaning-first used **43.5% fewer tokens** across all four calls, including the
failed all-fields call. On the three documents where both responses were complete,
the reduction was **32.6%**. Record counts are not semantic recall scores, and the
smaller output does not provide all the optional structure of the control.

The relationship calls alone used 70,184 tokens, including 43,927 reported thought
tokens. The combined path cost **80.8% more tokens than all fields**, or about
3.2 times meaning-first alone. These are reported tokens, not dollar estimates.

| Excerpt | All fields | Meaning first | Added relationship pass |
| --- | ---: | ---: | ---: |
| Names | 11,870 | 8,367 | 17,620 |
| Photos | 12,208 | 10,412 | 7,655 |
| Leave eligibility | 12,222 | 5,699 | 21,904 |
| Baggage | 20,176; incomplete | 7,435 | 23,005 |

## What the raw review shows

The smaller pass preserves the emergency permission's inherited limits, all six
name-document alternatives, separate recent-change duties, photo recommendations,
and the certificate timing caution. On the new excerpts, it retains the cumulative
eligibility conditions, the two seven-year comparisons as written, the alternative
service-counting cases, and the checked-baggage conditions and exception boundaries.

Three otherwise useful all-fields baselines were lost during conversion:

- The emergency permission had faithful prose, but its separate `object_quote`
  spliced text across intervening words. The whole baseline and its link were refused.
- The leave eligibility definition's concept quotation flattened multiple source
  paragraphs. The whole definition was refused.
- The prior-service counting duty's concept quotation inserted an ellipsis and
  joined separate passages. The whole duty and its link were refused.

The all-fields baggage response exhausted its output budget and returned incomplete
JSON: 15,730 reported thought tokens and 640 candidate tokens. It was retained as a
failed response without partial recovery. Removing optional fields improved the
usable result here, but a single call does not establish a repeatable failure rate.

Meaning-first also failed once: it used `statement / not_required` for the
nonconsecutive-months statement, violating the existing kind/modality rules. That
statement remains in raw output and refusals but is absent from the accepted graph.
Its standalone prose also omits the source's opening proviso tying it to the counting
rules. Both variants still combine the identity fact with a descriptive possibility.
Fewer fields do not eliminate semantic or classification errors.

The source review judged nine retained all-fields links supported, two misleading,
and two uncertain. The misleading links concern a notation deadline represented as
a prerequisite of itself and a service-counting exception missing its actual limits.
Two further supported raw links were discarded along with their parent baselines.

The separate relationship pass adds three links judged supported: the previous-name
exception, the service-counting exception with both alternatives, and the three
accessible-property weapon exceptions attached to the proper prohibition. It adds
no photo links and no explicit unloaded-firearm qualification. This does not mean
those conditions disappeared: first-pass statements, `ApplicabilityScope`, and
`EvidenceBinding` records already preserve much of that meaning. Three supported
links do not establish complete relationship coverage.

`assessment.json` records every frozen case judgment and every generated qualification
review with raw row indices. Its cases overlap and contain multiple requirements;
their counts must not be presented as an accuracy percentage. These are revisable
source reviews by the implementing agent, without an independent reviewer or
repeatability study.

## Decision and next work

Use the meaning-first result as the next candidate to consolidate. Address the
kind/modality rejection and prevent a bad optional component from discarding a
faithful baseline. Preserve unsupported candidates and the reasons they were withheld.
Verify another small batch before changing defaults.

Reuse existing scope and evidence records where they already express the needed
conditions. Keep relationship requests targeted to a consumer's specific unresolved
connection. This trial does not justify a document-wide second pass as the default.
It also does not isolate whether prompt wording, field count, or reasoning behavior
caused each difference; those are separate experiments if they become necessary.

## Verification and preserved history

Ten tests pass, covering the reused adapter plus composition: first-pass identity,
content and lineage retention, shared-quotation target selection, unknown/duplicate
target refusal, and malformed added evidence. All 11 successful conversions validate
as Core graphs. Offline replay reproduces those conversions and the one failed
response exactly, with no provider calls.

All 38 accepted first-pass aliases were returned once by the relationship stage;
this is processing accounting, not semantic completeness. First-pass records and
graph nodes remain unchanged in the combined result. New qualification assertions
receive second-pass lineage. Raw requests, responses, target tables, mappings,
refusals, prompts, source catalogs, schemas, and runtime snapshots are preserved.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/composed-extraction-experiment/experiment.py replay
```

The two smaller schemas were generated by the pinned native CUE exporter using
the existing profile and attached-trial definitions. `build/` retains the inputs.
The acquisition manifest and frozen runner precede the review. `amendment.json`
records a replay-only change to verify failed responses as well as conversions;
it changed no model call, prompt, schema, or conversion. Both runner versions remain
in `frozen/`. Review artifacts do not alter the original capture history.

Some acquisition manifests also recorded local Python bytecode caches. Those
caches remain untracked; the replay command verifies the frozen source/schema
hashes and recorded outcomes, rather than requiring those machine-specific files.
