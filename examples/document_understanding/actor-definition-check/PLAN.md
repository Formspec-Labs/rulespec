# Explicit actors and definition links

Decision: Is adding source-supported actor fields worthwhile, and does a small
document-local definition index add navigable meaning beyond actors alone?
This authorizes an experiment, not production adoption.

Observation: Current first-pass CUE does not request actors or definition
subjects. Its parser sets actor to an empty string. The saved passport UI has
complete actor wording in several statements but no actor fields or term links.

Hypotheses and alternatives:
- A: Explicit actor slots restore faithful actor data with no material loss of
  statement meaning. Weakened by missed actors, invented duty bearers or confusing
  an approving authority with the party acting.
- B: A definition index and per-unit references identify definitions and connect
  uses without making topical mentions into definitions. Weakened by missing
  definitions, dangling/wrong links, unsupported aliases or increased omissions.
- Missing fields in the baseline are a known schema limitation, not evidence
  of a model's inability to identify actors. Comparing A with B isolates the
  incremental index bundle, not effects of its individual fields or ordering.

Arms: current schema; current plus actor/actor_quote; actor schema plus an early
terms index and defines_term/term_refs per unit. Same prompt in all arms; only
native CUE-generated schema differences. Reuse #Actor and #ActorQuote directly.
Actor fields are required-nullable to distinguish assessed absence from not
requested. This trial does not compare nullable with omission-only policy.

Cases: the exact complete passport source shown in the UI, plus a newly authored
counterexample document. Passport is development data. Constructed controls are
not an independent benchmark. Do not touch the frozen oxygen/alarm/procurement
evaluation sources. Pre-call checks are in REVIEW.md.

Held constant: model default Gemini 3.8 Flash, temperature 0, low thinking,
16,384 maximum output tokens, same complete source window and prompt per case.
One call per arm/case, randomized order: six calls maximum, no repair or retries.
Stop after six calls or twenty minutes of provider work; retain failed calls.
No rate/generalization estimate from two selected inputs or one repeat per cell.

Decision rule: investigate actor adoption only if every explicitly checked actor
is correct, null counterexamples hold, evidence survives Core, and statements
lose no checked qualifications versus baseline. Investigate the index only if
both passport definitions and both constructed definitions have supported names,
aliases, definition targets and the checked usage links, with no invented terms,
dangling/wrong links or material checked statement regression versus actor-only.
A failed broader gate remains failed even if individual fields improve. Report
tokens and latency separately. Passing is bounded evidence for a later integration
decision, not authority to change production now.

Reuse assessment: actor/evidence fields, native CUE generation, passage IDs,
capture, candidate parsing, Core compilation and conformance are callable today.
Core LocalConcept/ConceptScheme support local identities and SKOS labels/aliases;
RelationshipAssertion can express explicit links with profile predicates.
Existing ConceptTag is topical association, explicitly not entity identity or a
defines relationship. No first-pass defined-term index/link is connected. Build
only the small model-facing index for this trial; retain it as experimental data.
Do not mislabel a topic assignment as a definition link or claim Core term-link
integration was tested. A production integration would reuse those Core records
and add explicit profile predicates, with source evidence and scope retained.

Assessment: review randomized, opaque statement views before looking at arm names
or enrichment. Then assess actors and term links separately against raw source;
new fields necessarily reveal treatment during that second review. Record
mechanical validity, adherence, semantics, user benefit and cost separately.
Judgments remain revisable, not gold. Freeze plan, checks, sources, schemas and
actual prompt before calls. Pin base commit and runtime digests rather than copy
the entire repository into another experiment. Keep every original capture.
