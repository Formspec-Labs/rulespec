# Independent pipeline recommendation B

I would build a source-centered discovery system with inexpensive automatic enrichment, then prepare selected material for human-reviewed workflows when someone actually needs it. Basic extraction already runs independently; audit and refinement are optional. I would keep that separation and replace the full inventory → comparison → recovery → relationship proposal → challenge → fresh inventory → comparison sequence inside the optional refinement route with targeted operations. I would not adopt that full route as a universal ingestion or quality gate.

The default product should help users find a provision, understand its conditions, and correct a suggestion. It should not spend most of its inference budget certifying its own interpretation before anyone searches it. Workflow preparation deserves a different depth of analysis because a wrong deadline or overbroad exception changes what someone does.

This recommendation is independent of other agents' recommendations. It uses the pinned captures reviewed in `thoughts/reviews/2026-09-10-blind-process-b.md`, not changing production code. I applied the architecture-review skill's evidence, user-value, and counterfactual checks. The parent review confirmed that audit/refine are optional and that the optional refinement function runs the full chain. I did not inspect repository-wide normative commitments or actual search/form consumers; compatibility with those remains an implementation discovery task, not an asserted fact.

## What supports this decision

**Observed:** The alcohol and rail initial extractions preserve the important meanings. Every original summary survives final refinement verbatim. Recovery produces nothing in either case. The substantive change is two alcohol exception nodes and five rail links. The eight-call process consumes 111,966 and 133,717 provider-reported tokens respectively, versus 5,577 and 6,563 for extraction. Exact quotations and evidence offsets remain sound. All final assertions are drafts, despite model comparison reports saying passed.

**Observed:** Rail exception links point to a grouped stop/look/listen/no-approaching-train rule, without identifying just the stop action. Vehicle-class applicability exists in prose across six statements but lacks explicit applicability links. Alcohol's accurate State reporting prose still needs branch and reference-event interpretation before it can become a deadline calculation.

**Interpretation:** The captured optional refinement process has built useful provenance and good reading aids, but its extra stages deliver relatively little demonstrated discovery value in these examples. They do not resolve the hardest workflow decisions.

**Hypothesis:** A single good extraction, deterministic checks, source-aware retrieval, and selective enrichment will provide comparable or better discovery value at much lower cost. Two short passages cannot establish this for a corpus. The experiments below are intended to overturn this hypothesis cheaply if it is wrong.

## Preferred stages and their exact jobs

| Stage | Input | Work | Output and check |
|---|---|---|---|
| 1. Capture source | Original document, source URL, edition/version metadata | Save immutable bytes; extract text and source structure; retain heading/list/paragraph parentage and a mapping to original locations | Versioned source, exact spans, source tree, parse warnings. Verify text/location consistency and detect missing or garbled sections. |
| 2. Make useful discovery records | A coherent source section or bounded focus with necessary surrounding source, existing topic vocabulary if supplied | One model call writes readable meanings, preserves qualifications and alternatives, identifies a few useful roles/terms/topics, and records uncertainty | Small records tied to spans and source version. Check schema, exact spans, valid local IDs, limits, and refusal/truncation. Do not call schema validity semantic correctness. |
| 3. Index and retrieve | Original source passages and discovery records | Index lexical text and embeddings; retain separate source and generated text; retrieve relevant passages/records and bring governing context with them | Ranked source-backed results with source links, excerpt, conditions, and related material. Evaluate on real queries and judged results. |
| 4. Enrich where it helps | A selected local group or candidate relation pair, exact surrounding source, existing record IDs | Optional automatic relation/tag refinement triggered by demand, recurring queries, or a known quality issue | Suggested topic associations, references, and typed relationships with explanation and affected text. Validate IDs/spans and compare benefit against un-enriched retrieval. |
| 5. Learn from use | User corrections, query judgments, unresolved interpretations, new source versions | Save narrow versioned feedback; distinguish factual correction, alternative reading, and personal preference; apply local fixes and inform sampled evaluation | Corrected records, reproducible revision history, regression cases, and selective reprocessing. Never treat a click alone as proof of legal interpretation. |
| 6. Prepare a workflow or form | User-selected provisions, intended task and population, source context, relevant exceptions/references, known local decisions | Produce a reviewable decision table and action list; identify unresolved inputs and branch consequences; resolve required references | Human-reviewed operational specification with source evidence and scenario tests. Generate workflow/form definitions only from decisions explicitly accepted for this use. |

Stages 1–3 are routine ingestion. Stage 4 can run automatically without human permission or a universal audit gate; it should be demand-driven or selectively precomputed. Stage 5 supports normal product use. Stage 6 is entered because a user wants an operational artifact, not because a search result exists.

### 1. Keep the source authoritative, including its awkwardness

The original text, its location, and its edition are the durable asset. Preserve repeated list entries, spelling, ambiguous names, and unresolved citations. A cleaned display version is useful, but should map back to the original rather than replace it.

Structural parentage is evidence about layout, not proof that a parent condition governs every child. Store it so retrieval and reviewers can inspect it; let semantic claims about scope remain claims. For very long sections, split at source boundaries, retain list lead-ins and continuations, and expose omitted-context warnings. Do not silently truncate a qualification to meet a character budget.

Version source passages independently of model-generated wording. A rerun should not erase the identity of the source a correction concerned. New source versions should invalidate affected derivatives visibly, without discarding earlier review evidence.

### 2. Use a small discovery representation

My starting record would have:

- Source version, exact span IDs, and source heading path.
- A readable statement or coherent grouped meaning.
- A broad type such as duty, permission, prohibition, exemption, definition, or explanatory statement, when useful.
- Optional actor text, locally defined term, source references, and a few topic suggestions.
- Optional named uncertainties, such as unresolved scope or missing referenced text.

I would not require action/object decomposition, typed thresholds, jurisdiction, effective periods, formal logic, per-component assertions, or a full fourteen-dimension assessment at ingestion. Add structure only when a consumer can name what it does with it. A null field should not manufacture a review task when the readable statement already retains the meaning.

Group options and mutually dependent steps when that makes a better search result. Separate independently useful actions or different modal forces. Do not force one node per sentence or one node per atomic proposition. Rail's list of placard classes should remain a readable list; workflow preparation can turn it into explicit OR conditions if needed.

Prefer complete statements, but do not make every short record reproduce an entire multi-page applicability schedule. Explicitly tie such a record to the relevant source section and ensure retrieval delivers that context. A short statement that admits incompleteness is more honest and maintainable than thousands of repeated words advertised as self-contained.

### 3. Treat tags and embeddings as retrieval aids

Tags should answer actual discovery needs: subject, regulated activity, actor role, material/asset, or document family. Keep topic suggestions distinct from actors and from terms explicitly defined by the source. If a maintained vocabulary exists, suggest its IDs and preserve unmatched labels; do not create an elaborate concept release for each generated phrase by default.

I would index original passages and generated readings separately first. A result can benefit from a plain-English paraphrase without replacing the wording containing a qualification. If only one embedding per passage is affordable, use source text plus heading context as the starting baseline and test generated-text augmentation. Neither choice is established by the two captures.

At retrieval time, show the matched record with relevant preceding lead-in, associated list items, and exceptions. Fetch from the source structure and explicit known links; do not silently turn a guessed relationship into a restrictive filter. Keep an ordinary source-text search path so a missed extraction does not make a provision undiscoverable.

### 4. Make graph relationships useful before making them executable

Build the inexpensive graph automatically: document/section membership, citation references, explicit local term use where supported, and suggested topic associations. Distinguish those relationship types; sharing a topic is not equivalent to an exception.

For inferred legal relationships, use compact local requests. Return the source record, target record, relationship type, affected phrase or action, and a short explanation. Do not resend complete records and all previous judgments merely to ask for a link. Do not ask the model to copy unchanged fields back into a full replacement.

For rail, a useful output is: “This exemption changes the stop step in this crossing procedure.” A plain edge to the whole grouped rule is acceptable for navigation if displayed as a suggestion; it must not mean the whole procedure disappears. If affected scope is unclear, save that uncertainty and keep the source available.

I would test whether producing a few explicit local links in the initial extraction is cheaper and equally accurate. I would not make it the default before that experiment: expanding every extraction request to solve graph semantics could degrade the readable result or recreate the existing complexity.

### 5. Put corrections close to the task

Allow a user to flag a missing qualification, wrong target, wrong actor, misleading tag, or duplicate result directly beside the source. Preserve the disputed model output and the proposed correction. A reviewer may confirm one statement without approving the whole section.

Feedback should be scoped. A personal tag or query preference is not a correction to the regulatory source; an expert interpretation may coexist with another plausible interpretation. Record the contributor, source version, reason, and intended use. Apply factual corrections immediately to the appropriate reviewed view, and use accumulated examples to improve prompts or evaluation after deliberate review. Avoid automatic global prompt changes from isolated feedback.

### 6. Prepare operational decisions on demand

For workflow/form building, start with the intended user task: who is acting, what event starts the process, what cases matter, and what the artifact should produce. Retrieve the relevant rules and inspect the surrounding source and references. Then create a decision table with actor, trigger, conditions, required/permitted action, recipient, deadline, exceptions, and evidence. Fields can remain unresolved rather than forcing invented answers.

For alcohol reporting, the draft should explicitly separate the employer-reporting clock, ordinary State-reporting clock, and review/affirmation route. For rail, it should separate vehicle applicability, the stop step, remaining crossing checks, and sign authorization. Human review should focus on those choices and concrete cases, not require approval of dozens of evidence records.

Only this selected operational specification needs semantic sign-off before driving behavior. Test cases should include both admitted and excluded situations, clock-start events, absent facts, and competing branches. A second model can challenge this compact specification when useful, but its agreement is supporting review evidence rather than approval.

## Keep, remove, replace

| Current element | Decision | Reason |
|---|---|---|
| Exact source spans, immutable captures, versioned history | Keep | They make correction and review reproducible. |
| Faithful baseline extraction | Keep and simplify | It supplied most demonstrated value in both examples. |
| Source inventory and comparison inside the optional refinement chain | Separate from refinement; retain as sampled evaluation or targeted investigation | Model inventories change granularity and are not fixed ground truth. |
| Recovery on every invocation of the full refinement route | Make conditional | Both observed calls were empty; invoke when omission evidence justifies it. |
| Full-record relationship edits | Replace with narrow link operations | Copying unrelated fields costs tokens and risks erasure. |
| Challenge every relationship batch | Replace with selective checks and sampled adversarial review | No evidence here that universal repeated agreement resolves affected-action ambiguity. |
| Re-inventory unchanged source after edits | Remove | Reuse source assessment; deliberate independent inventories belong in robustness experiments. |
| Per-field Core assertions for every discovery record | Defer or derive at export | Keep the working store small; produce required Core data when a real consumer needs it. Existing consumer obligations must be checked before migration. |
| Passed/review-complete as general assurance | Replace with explicit states | Distinguish parsing, automatic checks, model assessment, unresolved interpretation, and human approval for a named use. |

These are product and cost recommendations, not findings that all current layers are unnecessary for every consumer. Core export may be valuable interoperability infrastructure; it should not determine how much text the model repeatedly receives.

## Alternatives and ways my preference could be wrong

**Source-only retrieval with no extraction:** This is the essential cheap comparator. If it performs equally well on real discovery queries and source navigation, defer much more extraction. It may struggle with implicit roles or plain-language queries; that is a hypothesis to test.

**One comprehensive extraction plus cheap checks:** This is my preferred default. It may miss long-range conditions more often than a multi-pass approach on difficult documents. If that happens, route those document shapes to additional analysis rather than imposing the cost universally.

**Always-on rich extraction and audit:** Keep this alternative if controlled tests show a material gain in important omissions or graph-target precision large enough to justify cost and latency. The present two cases do not show such a gain. A richer default may also be justified if most users immediately build workflows, rather than search.

**Fully atomic rule graph first:** This could help an existing execution engine, but only if its exact semantics and users justify the decomposition. Otherwise it creates many objects to review before showing a helpful result. The kill criterion for my grouped design is inability to prepare accurate selected workflows without repeatedly redoing all extraction.

## Smallest decisive experiments

1. **Discovery comparison:** Use roughly 30 varied source excerpts, including difficult lists, weak guidance, external exceptions, and at least several multi-window sections. Freeze source versions and create realistic queries before generating outputs. Compare source-only retrieval, source plus one-pass readings, and the current full pipeline under the same retrieval setup. Judge top results blind for relevance, missing qualifications, and time to locate the decisive source. Record total cost, latency, and index size. Do not decide from schema pass rates or similarity scores.
2. **Graph scope comparison:** Choose about 20 source-grounded relation questions, including the rail stop case, unrelated neighboring duties, and exceptions with unresolved targets. Compare compact first-pass/local relation output against current proposal/challenge output. A reviewer checks target, direction, and affected action. Include wrong candidate targets deliberately. Retain the cheapest approach whose navigation quality is comparable; require stricter review for executable use.
3. **Workflow preparation trial:** Ask two or three intended users to build a small form or workflow from selected provisions using source-only material, discovery records, and the full pipeline output. Count unresolved substantive decisions, harmful branch/deadline errors, and reviewer time. If rich ingestion does not reduce those decisions or review time, do not fund it as workflow preparation.
4. **Feedback replay:** Apply a few realistic corrections and one changed source paragraph. Verify that only affected outputs change, old evidence survives, and the correction appears in search without silently granting operational approval.

These sample sizes are small decision aids, not corpus-wide safety claims. Predeclare what improvement matters to the product owner before running them. Inspect failures, not just averages; an omitted prerequisite may matter more than several extra relevant hits.

## Implementation sequence and decision boundaries

First establish the discovery comparison and expose separate source/generated fields, source context, and clear suggestion status. Reuse the existing extractor and retained captures; no new platform is needed to test the thesis.

Next make the expensive stages independently selectable within the already optional refinement route, replace relationship replacements with narrow edits, and stop re-inventorying unchanged source. Keep existing outputs replayable so the lighter route can be compared on identical inputs.

Then add corrections beside source results and the compact relation path for demonstrated graph needs. Measure whether people use those links before expanding the relationship taxonomy.

Finally build the selected-rule decision-table review experience for one real workflow/form task. Add typed deadlines, explicit alternatives, or Core exports only as that task demonstrates their necessity. Check current consumers and normative schemas before retiring stored representations; preserve supported exports while simplifying the internal model requests.

**Verdict: keep extraction independent and reshape optional refinement.** Preserve source fidelity and revision history; make automatic discovery cheap and immediately useful; spend expensive semantic analysis on detected failures and selected operational work. Confidence is high about redundant copying and repeated unchanged-source inventories, moderate about the proposed ingestion default, and low about comparative retrieval or workflow outcomes until the controlled trials run.
