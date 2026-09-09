# Meaning-first adoption — implementation record

The normal extractor now selects complete meanings from the existing CUE profile.
Full Core/refinement fields remain independently generated from `#UnitMeaning`;
first-pass field selection no longer controls Core defaults or refinement shape.
`statement` maps to existing `summary`, with exact source evidence and unchanged
Core review/provenance machinery. No automatic relationship or enrichment pass.

Implemented source passage IDs scoped to each actual request: F for focus, C for
supplied context. Ranges cannot cross unseen content, reverse, mix series or use
context as the main source. Repeated quotations resolve through exact offsets.
Bad optional selections are retained in refusal records while a valid grounded
statement survives. Main evidence, schema and kind/modality checks remain strict.

Moved the discovery diagnostic's source/context record builder into the package.
`discovery-export` emits every source passage, linked draft statements, review
status and separate processing accounting. Evidence overlap is not proof that
all meanings were found. No new embeddings, search engine, legal links or UI.

## Initial live check and bounded follow-up

Exactly four initial Gemini 3.8 Flash calls at temperature 0 were made through
the normal command; each used one request, no retry. Raw captures and frozen
runtimes are saved in `examples/document_understanding/meaning-first-adoption/initial`.
Names: 12 accepted; leave: 10; photos: 11; baggage: 4. Names and leave retained
statements despite malformed optional logical text. Baggage lost two whole rows
because the model supplied comma-separated, noncontiguous main references.

This identified two small implementation improvements: main-reference syntax is
now constrained in CUE, with guidance to put disconnected lead-ins in scope;
logical evidence now uses a passage selection (`logic_quote`) converted exactly
into Core `logic_text`. The model no longer rewrites this quotation. Optional
reference strings remain semantically checked per component so malformed support
can be withheld without refusing a valid statement. Whole-row type/required-field
failures still refuse a row. Proviso guidance now explicitly includes `provided`
and introductory statements whose following list supplies their limits.

The bounded follow-up uses the same four sources, four calls, temperature 0 and
no retries. Results and review are saved beside the initial captures. This
is a small development comparison, not a semantic accuracy benchmark.

## Existing checks and limits

Focused tests cover the three saved all-fields failures (emergency passport
permission, leave eligibility, prior-service alternatives), exact Unicode/CRLF
ranges, unseen context, repeated text, bad optional references, and discovery
retention of unlinked source. Refinement/replay tests pass with the full generated
meaning schema. The full suite now passes: 304 package tests plus six schema-builder tests.
Native CUE regeneration passes. All four final runs replay identically, and
`discovery-export` retained all source characters through the real CLI.

Gemini guidance was checked at https://ai.google.dev/gemini-api/docs/structured-output .
It documents descriptions, validation and `anyOf`, while warning about schema
complexity. A trial of a shared CUE kind/modality disjunction failed native export
with a non-concrete struct error. It was not adopted; the existing Core semantic
consistency check remains. No compiler workaround or silent reclassification was
introduced. Source references and exact evidence do not establish correct scope,
modal force, relationship targets or complete extraction.

## Completed outcome

The final four calls produced 35 accepted statements with no parse or compilation
refusals, using 24,596 total reported tokens. All graphs validated. The source
review remains mixed: emergency scope, alternatives and recommendation force
survive; the nonconsecutive-months proviso is now explicit in the statement.
Some independent meanings remain grouped and some scope fields remain incomplete.
The ammunition row misclassifies not prohibited as not required despite faithful
prose. This is saved as a semantic failure, not masked by validation success.

The retrieval diagnostic retains 9/10 answerable source-support hits with linked
context (8/10 for statement text alone). Two unknown questions remain separate.
No further model calls are planned in this iteration. The next useful quality
work is targeted modal distinctions and statement/scope consistency, using the
saved cases and existing audit/refinement paths rather than a routine extra pass.

All captures, source review and commands are in
[meaning-first-adoption](../../examples/document_understanding/meaning-first-adoption/README.md).
Work is local and uncommitted at this stopping point.
