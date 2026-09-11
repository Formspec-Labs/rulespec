# Parallel pipeline design pilots

The useful direction is to improve which evidence reaches a consumer and how individual review decisions are recorded. These pilots do not justify a larger extraction prompt or a wholesale pipeline replacement. None of the experimental changes was adopted into production.

Three agents ran the comparisons in parallel against frozen plans. The parent independently reviewed the context answers, target verdicts and rationales, retrieval regressions, and actual request/response accounting. These judgments remain revisable; they are not human gold labels.

| Pilot | Observed result | Decision |
| --- | --- | --- |
| [Retrieval representations](../2026-09-10-design-retrieval/README.md) | Relevant source fragment at top 3: source 14/16, statements 14/16, combined 13/16. Combined loses two source successes and gains one. | Regression against the no-loss gate. Do not adopt concatenation before ranking. |
| [Statement plus context](../2026-09-10-design-context/README.md) | Four additional grounded answers across 16 fixed questions; no observed transfer of unrelated parent duties. Remote exceptions and some outer scope remain absent. | Bounded improvement in supplied local context; required-context selection remains unsolved. |
| [Independent target decisions](../2026-09-10-design-targeted/README.md) | Expected positive links recommended: 2/5 to 4/5; both accept 0/3 negative links. Experimental arm loses the expected service link and adds overbroad prose. | Tradeoff; the broader gate failed. Investigate smaller decisions separately from additional descriptions. |

## What the raw examples tell us

**The current checker often sees the distinction already.** Its phone rationale explicitly recognizes the driver emergency exception, then rejects the proposal because it also targets the disputed carrier duty. The same pattern appears in the railroad and de-minimis bundles. Separate target verdicts retain useful recommendations that the existing all-or-nothing verdict discards. This is evidence for finer decision granularity, not evidence that the model reads better. No partial addition or review graph change was applied in this pilot.

The targeted arm also reveals a modeling ambiguity. It rejects the exempt-substitute → service relationship because the service provision already says “non-exempt substitute refrigerant.” The baseline accepts the same edge as explicit applicability information. The frozen expected-positive label and failed gate remain intact, but this disagreement need not imply different substantive interpretations of applicability. We need to define whether that relationship records a dependency that explains scope or only a change to otherwise applicable scope. Both arms remain too categorical about the previously disputed carrier interpretation.

**More generated explanation creates another place to lose conditions.** The target arm correctly distinguishes de-minimis venting from independent service duties, then writes “All other releases remain prohibited.” That sentence overlooks the separate listed-substitute exemption. A well-grounded edge verdict does not establish that its generated description is complete. The experiment bundled target decisions with affected-action descriptions, so it cannot establish which component caused the gains.

**Useful context must actually arrive.** Added child-restraint context shows that a dated labeling requirement is conditional on restraint occupancy, rather than establishing a general manufacturing mandate. But its selected text lacks the outer aircraft setting, and the model correctly refuses to infer it from the question. The refrigerant packet similarly never includes the de-minimis paragraph. Both arms abstain on that omission. This is a selection failure, not evidence that the model cannot interpret the missing passage.

**Repeated context can harm search before anyone reads it.** Appending the same long classification statement to multiple source items pushes the required any-quantity chlorine provision from rank 1 to rank 20. A service-equipment provision moves from rank 2 to rank 4, outside the fixed top three. Combined indexing grows from 15,928 to 99,415 characters. Across 16 queries its returned evidence contains 24,029 unique characters plus 57,276 repeated characters. These are payload measurements, not billed token counts.

Source-only and statement-only retrieval have complementary failures: source retrieves an actual nonconsecutive-employment provision absent from this extraction, while a grouped statement supplies the connection between beer and a shipment exception that a short source list item does not express. Preserve source retrieval even when extraction succeeds mechanically.

## What to test next, in priority order

1. **Test selection before another interpretation pass.** Reuse passage IDs, source structure, references, and existing evidence roles to deliver outer scope and remote dependencies. Measure whether required passages arrive, unrelated context volume, and unresolved references. Proximity must not silently become governing scope. Include fresh documents and misleading parents; do not manually supply the answer clauses from these development cases.
2. **Test one decision per proposed target, without the new affected-action prose.** First document the intended existing relationship semantics. Preserve unknown and rejected readings, and test safe partial handling of additions separately. Reuse the current decoder, evidence resolver, and review history. The present pilot only selects among supplied candidates; it does not discover missing targets or replace the full refinement chain.
3. **Use the existing search alternatives before inventing another index format.** Compare source ranking followed by the existing `discovery_trial` packets evidence expansion, and a separate source/statement result combination. Deduplicate returned evidence by source positions while preserving roles. Freeze fuller support labels and a meaningful output budget before scoring. This is a new comparison, not an implemented recommendation.

Human workflow review time, embeddings, cross-document knowledge-graph usefulness, and end-to-end replacement of refinement remain unmeasured. There is no reason from these results alone to change the one-pass extraction default.

## Cost, verification, and stopping point

There were **14 fresh model calls**, no retries, and **123,125 total reported tokens**: 80,105 input, 5,753 answer, and 37,267 thinking. Retrieval used zero API calls. All live requests used `gemini-3.8-flash`, temperature 0, provider-default thinking, a 32,768 output-token limit, and one candidate. The parent counted the actual attempt files and checked those settings and returned usage; see [usage.json](usage.json). Historical extraction costs are excluded.

Context used 26,716 total tokens. Target challenges used 96,409; the experimental target arm cost 4.0% more than its control. The context arm's lower total despite higher input reflects single-sample thinking variation and does not establish repeatable savings. These are stage-specific measurements, not a document-cost estimate.

All three pilots saved zero-provider-call replay receipts. Response structures, exact reference resolution, and captured requests passed their mechanical checks. That does not establish semantic completeness. The retrieval fragment labels under-specify the de-minimis compliance routes, and its 6,000-character cap never binds; its selected-fragment scores must not be described as complete-answer accuracy.

The cases are selected historical development documents, newly authored questions, and labeled constructed controls. They are not an independent benchmark. Each live case has one observation per arm. The comparisons stopped at their declared bounds without tuning. Existing uncommitted compact-link implementation work was preserved; this round added only experiment artifacts. Nothing was committed, deployed, or added to production by these pilots.

See the [aggregate pre-run plan](PLAN.md) and each pilot's frozen plan, raw captures, assessment, and manual review for the evidence behind these conclusions.
