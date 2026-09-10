# Actors and definition links: useful structure, failed overall adoption gate

**The model can supply the missing actors and definition links. Adding them to
the first pass also coincided with a material statement regression. Keep these
changes experimental.** Six fresh calls compared current extraction, explicit
actors, and actors plus a definition index on the exact passport source and a
constructed counterexample document. No production schemas, UI data or review
history changed. No more calls are pending.

## What improved

Both enriched arms supplied the ten checked actor assignments across the two
documents (twenty assignments across both arms). These include Passport
agencies/centers, Posts, literal you, Applicants, Reviewers and Clerks. One of the
ten uses passive IN wording at agencies/centers and is less explicit than the
active IRL restriction; nine directly expressed assignments also pass on their
own. Definitions, an unexplained code, impersonal retention and descriptive
storage availability retained null actors. Approvers were not substituted for
the principal actors. All twenty populated actors have accepted Core evidence.
This checks selected roles, not exhaustive actor coverage: the combined IN
response/personalization exemption still does not separately model its recipient.

The index arm produced exactly the two defined terms on each document:

| Defined term | Source alias | Examples of correctly linked uses |
|---|---|---|
| information request letters | IRLs | Alteration restriction, Posts language rules, consultation |
| information notices | INs | Alteration restriction, response exemption, consultation |
| Review notice | RN | Return deadline, receipt-triggered action |
| Service receipt | SR | Issue receipt, keep a copy |

Each term links to the correct defining unit; name/alias support resolves to
source passages. Consultation links both IRLs and INs. No terms were invented
for XYZ, supervisor, files or storage. IDs are unique with no dangling references.
The RN link on deadline extension correctly follows its antecedent; that is
separate from the directly mentioned links. These links are experimental data,
not yet compiled into Core relationships or exposed in the UI.

## What worsened

The baseline kept this governing qualification in its independent statement:

> Posts must use the cleared language in the IRLs, but are authorized to modify
> the language to suit local logistical requirements and other local concerns
> such as available documentation.

Both enriched arms instead emitted:

> Posts must use the cleared language in the IRLs.

They also emitted the qualified modification permission as a separate row. A
consumer reading both rows together could recover the meaning, but the declared
standalone-statement check fails: an independent mandatory statement now lacks
its qualification. One call per cell cannot establish that adding fields caused
this behavior or that it will repeat.

Blinded statement judgments were saved before inspecting treatment labels and
actor/index output:

| Source and named checks | Current | Actors | Actors + index |
|---|---:|---:|---:|
| Passport, 8 | 8 | 7 | 7 |
| Constructed controls, 8 | 7 | 8 | 8 |

The controls baseline labeled the expressly unexplained XYZ code as a definition;
both enriched arms labeled it a statement. That classification is debatable: the
source does describe its category, and the text preserves uncertainty. If that
judgment is excluded, all arms pass the remaining seven control checks. It does
not remove the passport regression. All other named statement conditions and
alternatives survived. Actor-only controls also said “the deadline” without naming
RN return; the five-day limit and approval condition survived, but standalone
context is weaker than the other arms. No general accuracy percentage follows.

## Cost and mechanical checks

| Source | Current output tokens | Actors | Actors + index |
|---|---:|---:|---:|
| Passport | 1,418 | 2,613 | 3,284 |
| Constructed controls | 724 | 908 | 1,989 |
| Total | 2,142 | 3,521 | 5,273 |

Actor output grew 64% across these calls; the index bundle added another 50%
over actors. These are complete response token counts, including changes in
other optional fields and statement wording, not the isolated cost of new keys.
Provider-reported total tokens were 6,272 / 7,651 / 9,403; all six calls totaled
23,326. No dollar estimate or invoice claim is made. Summed request durations
were 6.43 / 8.77 / 12.40 seconds; one sample per cell is not a latency benchmark.

All six responses passed their native CUE-generated JSON schemas. All 74 records
were accepted and their Core graphs passed validation; no response, parsing or
link-integrity errors occurred. These mechanical checks did not detect the
statement issue. A deterministic offline replay verified all six requests and
processing results without provider calls.

Settings: `gemini-3.8-flash`, temperature 0, low thinking, maximum 16,384 output
tokens. One randomized fresh call per arm/case; no retries, audits or repairs.
Actual captured requests have identical prompts/settings per source, and the
expected schemas. Actor fields reuse existing CUE `#Actor` and `#ActorQuote`.
The actor arm keeps statement first. The index arm puts its registry before
extractions and per-unit link fields before the statement; this ordering is part
of the index bundle, not an independently tested factor.

## Decision and next boundary

- **Bounded improvement:** explicit actor and definition navigation data are
  useful and correct on the checked examples. The index adds correct links without
  another observed statement regression versus the actor arm.
- **Tradeoff / broader gate failed:** neither enriched first pass meets the
  no-regression condition against current extraction. The relative index result
  does not make the complete bundle an adoption pass.
- **Next hypothesis, not implemented:** enrich saved statements in a separate
  bounded step, so actor/term additions cannot rewrite their wording. That protects
  the original capture by construction; it does not prove the added roles/links
  are accurate or that an extra call is worth its cost. Compare its marginal cost,
  omissions and unsupported links before adopting it. Do not patch these source
  prompts to chase the observed split.

The old explanation experiments do not settle this question: these fields carry
roles and referenceable identities, rather than explanatory prose. Conversely,
correct new fields do not compensate for missing qualifications in statements.

## Evidence and replay

[Plan](PLAN.md), [pre-call checks](REVIEW.md), [source inputs](sources),
[schemas](schemas), [actual requests and raw responses](runs),
[blinded statement views](blind), [statement judgments](statement-review.json),
[structure judgments](structure-review.json), [metrics](metrics.json),
and [manifest](manifest.json) preserve the result. Labels are revisable judgments
by one model reviewer, not gold. Passport is development data; the counterexamples
are authored controls, not an independent benchmark. The previously frozen fresh
regulatory sections were not reused or changed.

Run from the repository with the pinned runtime at base commit `e43f4b2` and the
recorded dependencies. The runner verifies runtime and input digests; it does
not silently update them when the repository changes.

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python \
  examples/document_understanding/actor-definition-check/run.py replay
```

The index adds a small model-facing structure because no first-pass definition
link exists. A later integration should reuse Core `LocalConcept`, SKOS labels
and aliases, source evidence and explicit relationship assertions. Existing
topical `ConceptTag` assignments must not be substituted for definition identity.
