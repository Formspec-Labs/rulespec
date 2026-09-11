# Independent end-to-end recommendations C

I would rebuild the product around an immutable source library and a small, optional interpretation layer. Retrieval should work before interpretation succeeds. Workflow preparation should be a separate operation that assembles and reviews the relevant source and interpretations for a particular proposed activity. I would stop treating the general extraction graph as an almost executable workflow model.

These recommendations follow my own raw-output inspection in `2026-09-10-blind-process-c.md`. I have not read other agents' recommendations. They are design proposals, not demonstrated improvements. No additional model calls or production changes were made.

## What the evidence changes

The current pipeline's best demonstrated capability is retaining useful meaning with traceable source locations: complicated refrigerant lists, label alternatives, dates, and separate permissions survive. Its largest demonstrated weakness is treating individually extracted statements as complete when consequential context is elsewhere. Exact evidence, multiple model passes, and a draft graph do not resolve that problem.

One earlier interpretation needs qualification. The child-restraint permission's “Notwithstanding any other requirement of this chapter” may interact with the section exclusion's “Unless otherwise stated.” I cannot conclude that every child-restraint duty must inherit that exclusion. The system should represent and escalate the interaction instead of assuming either blanket inheritance or blanket independence. The narrower defect is clear: isolated label statements lack their aircraft-use context and their relationship to the permission.

Evidence: `thoughts/experiments/2026-09-10-parallel-targets/inputs/seatbelts/packet.json`, C0006–C0016; cells 01/02 final output. Refrigerant C0000 also omits the de minimis exception from its default statement even though C0002 retains it separately. Actor controls in `thoughts/experiments/2026-09-10-parallel-copying` test source support for fixed labels; they do not establish automatic role identification.

## Proposed design

### 1. Preserve and index sources first

**Input:** original document bytes, source URL, retrieval date, edition or effective-date metadata when known, and the user's document collection.

**Process:** capture the original; parse text and its real hierarchy; preserve an explicit mapping between readable text and original locations. Keep headings, table cells, list lead-ins, and adjacent passages. Distinguish absent source structure from structure guessed from text. A parser may fix display whitespace while retaining the original bytes and offset mapping. Source identifiers must survive downstream model failures.

**Output:** versioned source documents, passages, structural parents, references as written, and a lexical plus embedding index. Index original passages and context-rich passages such as a child paragraph with its heading and lead-in. Do not concatenate an entire regulation into every vector. Evaluate retrieval sizes instead of assuming one chunk size.

**Check:** text coverage, citation resolution, source-location round trips, broken list/table boundaries, and original-to-readable mapping. The refrigerant sentence broken across artificial paragraphs is a concrete parser case worth fixing before asking a model to quote it again.

This gives automatic search a usable base without waiting for universal semantic extraction. Search results can show source text even when the interpretation layer is unavailable.

### 2. Extract a small interpretation bundle, not dozens of independent facts

**Input:** a coherent source section or local cluster, its explicit structural context, and any already resolved references needed for the intended use.

**Process:** one model pass proposes meaning units. A unit contains a readable interpretation, its kind and modal force, source passage references, any necessary contextual passages, and unresolved questions. Identify actors and defined terms when useful; do not populate them merely because a schema permits them. Models select source locations; application code retrieves exact text. Preserve raw responses and rejected components.

A unit can include several closely connected pieces. For example, the child-restraint permission, accompaniment requirement, label choices, and operator checks should remain discoverable together. They can have individually addressable children without becoming context-free duties. The refrigerant de minimis explanation should retain the “good faith” case, combined practices, machine-use condition, and alternative subpart in one readable unit.

**Output:** proposed meaning units with explicit context dependencies and status. A unit's short reading is an interpretation of the source, not a promise to restate every remote rule. If context is required to understand it, the default consumer view must include that context or plainly show the unresolved dependency.

**Check:** source IDs exist, locations match, modalities are internally consistent, and required context is present. Semantic checks ask what materially changes when a unit is read alone. They must permit “cannot determine from supplied text.” Do not turn every `except`, `may`, or colon into an automatic operator.

I would retain optional conditions and alternatives in natural language until a consumer needs a formal expression. When formal logic is needed, store the expression alongside its source and interpretation, not as a replacement for them.

### 3. Build a modest graph from interpretations and source structure

**Input:** source references, meaning units, explicit defined terms, candidate entity matches, and targeted relationship proposals.

**Process:** separate documentary relationships from semantic interpretations. “This paragraph is inside that section” and “this text cites that section” are different from “this exception changes that permission.” No automatic semantic inheritance should follow from paragraph nesting. A precedence interaction should be recorded as unresolved when the evidence does not settle it.

**Output:** nodes for sources, passages, meaning units, and useful entities; typed relationships with source evidence, draft/review status, and revision history. Common initial relations might be `cites`, `defines`, `mentions`, `condition_of`, `exception_to`, and `alternative_to`. Add a type because a real consumer asks a question that needs it, not because the ontology can express it.

Entity matches and topical tags are suggestions with provenance. A refrigerant name can support discovery without proving that two legal terms are interchangeable. Dates mentioned in a list must not automatically become the effective date of the entire rule.

**Check:** unsupported references, ambiguous targets, stale versions, contradictory interpretations, and relationship direction. Do not hide absent edges by treating an empty target list as evidence that a rule is unconditional.

I would initially keep this in ordinary application records and a relation table. The observed 17 seatbelt claims becoming 81 value assertions and 138 evidence bindings are justifiable for field-level attestation, but that cost has not been shown necessary for search or review. Generate RDF or another graph format at the boundary when a consumer demonstrably needs it. Retain stable IDs and provenance so this simplification does not discard auditability.

### 4. Retrieve sources and interpretations together

**Input:** user query, collection, optional facets, and usage context.

**Process:** combine lexical and vector candidates from source passages and meaning units; merge repeated source hits; expand necessary context; then rank. Keep source and interpreted fields separable so retrieval can fall back when a model omitted an actor or misunderstood scope. A qualifier graph should enrich a result, not silently remove it from consideration because one edge is missing.

**Output:** source-backed hits with a readable excerpt, a proposed interpretation where available, relevant conditions and exceptions, and a small number of actionable uncertainty labels. Tagging and graph enrichment may operate automatically, but should remain distinguishable from reviewed interpretations.

**Check:** measured query relevance and source coverage. Display-level checks should verify that an excerpt about a duty does not hide an attached exception. Embeddings, tags, and summaries should carry the source version so they can be rebuilt when the text changes.

### 5. Compile preliminary workflows and forms for a named activity

**Input:** a concrete proposed activity, the user's operational facts, retrieved source bundles, and explicitly selected interpretations. For example, inspect child-restraint eligibility for a described aircraft operation, not generate every possible aviation workflow.

**Process:** assemble relevant evidence; resolve necessary references; identify applicable decisions, actions, actors, timing, exceptions, and missing facts. Ask for operational facts when they determine applicability. Produce a preliminary decision path and form fields that answer those decisions. Do not convert every extracted noun into a form field or every `must` into a task. An action sequence inferred for convenience must be labeled as a proposed implementation sequence.

**Output:** a draft workflow/form plus a review table: decision or field, proposed behavior, supporting source, interpretation, unanswered applicability questions, and human approval state. Any unresolved prerequisite can produce a review branch instead of an invented Boolean answer. Fields should record facts needed to decide applicability, not imply legal conclusions the user has not established.

**Check:** walk representative cases through the draft with a human reviewer. Confirm who acts, when, under which conditions, and what evidence would show completion. Distinguish confirming a source interpretation from approving a particular organization's implementation. Only an explicitly approved version should become an operational workflow.

## Keep, remove, and replace

Keep original source capture, hashes, stable locations, raw model outputs, selective component refusal, revision history, draft status, and separate human approval. Keep grouping that preserves alternatives. Keep replayable transformations, but provide a compact reading view over the detailed archive.

Current base extraction is already single-pass; audit and refinement are optional. Within the optional `refine_run` route, the full initial-audit/recovery/relationships/final-audit chain is mandatory. I would offer selective entry points within that route and keep the full chain from becoming a prerequisite for discovery. Remove the expectation that every useful passage must become a formal rule. Remove scalar confidence presented as semantic correctness, if introduced later; the inspected outputs wisely do not establish completeness that way. Remove compulsory recopying of unchanged statements just to attach a relationship.

Replace full-record model edits with typed changes against a specific revision: add a meaning, revise its reading, add a proposed relation, or attach evidence. Replace duplicate summary/scope/choice prose with one primary reading and genuinely useful complementary structure. Replace blanket second-model approval with targeted semantic review selected by consequence, uncertainty, and measured error patterns. Preserve a full challenger option for difficult or consequential cases, but demonstrate that it catches errors before paying for it everywhere.

## Feedback that improves the product without rewriting truth

Collect distinct feedback signals: search relevance, incorrect tag/entity match, missing source passage, wrong interpretation, and workflow usability. A saved search result is a relevance signal, not confirmation of its legal meaning. A user's successful workflow does not prove that the source interpretation is universally correct.

Tie corrections to the exact source and interpretation version. Keep proposed, accepted, and disputed readings separate. Source revisions should invalidate affected interpretations for reassessment; they should not silently overwrite reviewed content. Use feedback first to improve ranking, context expansion, and the review queue. Update extraction prompts or models only after replaying a held-out evaluation, since a change that repairs one example can damage another.

## Strong alternatives and tradeoffs

| Design | Strength | Main cost or risk |
| --- | --- | --- |
| Source-only retrieval with interpretation on demand | Fastest delivery; few persistent model errors; a strong baseline | Repeats interpretation work; limited reusable semantic filtering |
| Source plus cached meaning bundles and a small graph — my preference | Useful automatic discovery with traceable interpretations; supports later human workflow review | Cache/version handling and unresolved scope still need careful design |
| Exhaustive semantic graph before serving | Rich queries and component review when extraction is accurate | Expensive, brittle completeness assumptions; current outputs do not justify it as a prerequisite |
| Human-curated models for selected high-value domains | Better scope and operational confidence for narrow workflows | Slower corpus expansion and explicit maintenance effort |

The best product may combine automatic discovery over the whole collection with human-curated workflow models for only the domains users actually need. That avoids demanding one representation satisfy two different quality bars.

## Smallest informative experiments

1. **Does interpretation improve discovery?** Compare source-only retrieval, one-pass meaning bundles, and the current pipeline on the same held-out documents and real user queries. Use blinded relevance judgments, answer-support coverage, missing-exception rate, latency, and cost. Split by source document, not by passages from the same document. Start with a small pilot to reveal obvious failure modes; do not call it production validation.
2. **Does context packaging fix the observed failure?** Show reviewers isolated statements versus bundled statements with governing text. Test refrigerant de minimis, child-restraint aircraft-use context, and fresh examples with nested permissions/exceptions. Measure correct interpretation and review time. Include the notwithstanding interaction as an ambiguity case, not an answer key asserting blanket inheritance.
3. **Does a challenge pass earn its cost?** Seed realistic scope omissions, wrong target edges, and actor/approver confusions. Compare one-pass checks, targeted challenge, and full challenge. Count new errors introduced as well as defects caught. Test unseen cases after prompt tuning.
4. **Do preliminary workflows save human work?** Have reviewers complete a few bounded activities using source-only evidence versus generated drafts. Record time, corrections, missing applicability questions, and unsupported fields/actions. The win is less effort at equal or better correctness, not a larger generated workflow.

## Implementation sequence

First, deliver the source index and context-bearing result view using existing captured documents. Preserve the current pipeline as a comparison rather than immediately rewriting it.

Second, introduce the small meaning-unit representation and typed edits behind one consumer interface. Adapt existing extraction and discovery outputs into it. Run the retrieval and context-packaging comparisons before replacing stages.

Third, add the feedback categories, version invalidation, and targeted review queue. Add graph relations only for demonstrated search or review needs. Repair source parsing and quote-location defects independently of semantic interpretation.

Fourth, build one bounded workflow/form preparation experience and evaluate it with actual human review. Expand only after it saves reviewer effort without hiding unanswered applicability questions.

My strongest recommendation is to make uncertainty and contextual dependence usable product data. The current pipeline records extensive evidence; its next major gain should come from showing users the right connected evidence at the right decision, rather than producing more assertions from the same passages.
