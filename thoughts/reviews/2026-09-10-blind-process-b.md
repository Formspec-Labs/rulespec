# Independent end-to-end review B

These two captures are useful automatic search enrichment. Their readable statements retain the important source meaning, and refinement adds useful exception navigation without destroying the baseline text. I would use them in a search or graph discovery product that shows source text and accepts corrections. I would require targeted review before using their relationships and deadlines to drive a workflow. The largest concern is the cost and implied assurance of the process, rather than widespread bad extraction.

## Scope and independence

I manually read the two source texts, every initial extraction statement, source inventories and comparison judgments, recovery outputs, all relationship proposals and challenges, final statements, history, and Core assertions. I inspected the stage requests to understand what each model received. This review concerns the pinned files under `thoughts/experiments/2026-09-10-exemption-end-to-end/`; paths below are relative to that directory. I made no provider calls and did not inspect changing production code, README conclusions, prior review reports, or experiment assessment narratives.

I saved my source-to-extraction observations first in `thoughts/reviews/2026-09-10-blind-process-b-initial.md`, before reading model audit judgments. A required memory search exposed generic historical caution about evidence versus meaning; it provided no conclusions about these captures. This is an independent artifact review, not a blind experiment with a statistically independent population of reviewers.

## What the actual words get right

**Alcohol is strong.** In `cases/alcohol/extraction/attempt-0000.response.json`, the 13 original statements preserve the four-hour pre-duty restriction, alcohol presence while on duty, qualifying wine threshold, both shipment and bus-passenger exceptions, motor-carrier responsibility, immediate 24-hour out-of-service period, issuance as its start, employer reporting within 24 hours, both State reporting routes, the written petition within ten days, and the distinct review authorities. The complex State reporting statement keeps the alternative thirty-day clock after affirmation. It does not silently substitute a fixed deadline for that conditional route.

The passive out-of-service duty does not invent who issues the order. The extraction treats affirm/reverse as authority, and preserves the source's different names for Division Administrator, State Director, and Regional Director of Motor Carriers. That restraint matters: these names should not become presumed synonyms or a guessed workflow organization chart. Remote definitions and references remain unresolved rather than fabricated. Empty locally defined-term arrays are appropriate here.

**Rail crossings is also strong as readable text.** In `cases/rail-crossings/extraction/attempt-0000.response.json`, all 18 placard list entries survive, including the Division 1.2/1.3 alternative and the repeated Division 5.1 found in the source. Loaded-or-empty limits and the at-loading flashpoint condition survive. The five exemptions retain the business-district qualification, police officer or flagman alternative, functioning green signal plus local-law qualification, abandonment sign, and Exempt sign. The separate sign-erection duty survives. The extraction separates permission to cross in a suitable gear from the prohibition on shifting.

The repeated Division 5.1 is source duplication, not an extraction mistake. Retain it in provenance; avoid counting it as two independent applicability reasons in a user interface.

**Refinement does not recover missing substantive text in these examples.** Both `cases/*/refinement/recovery/window-0000/proposal/attempt-0000.response.json` files return empty proposals and observations. Alcohol's relationship pass adds two exception nodes already present in the prohibition's prose. Rail's pass edits five existing exemptions to add exception links, preserving `kind=exemption` and `modality=not_required`. Every original summary appears verbatim in the final export. This is a useful structural enhancement, not evidence that refinement repaired an inaccurate initial extraction.

## Where I would limit trust

**The rail exception links identify a relevant rule, but do not precisely identify the part waived.** The target `C0000` contains stopping, listening, looking, and ascertaining that no train approaches. All five exemptions say that a stop need not be made. The final `rkaf:RelationshipAssertion` records point to the entire target revision ending `ebe79c8702bbd1a76b33f0145c50b80ac49d8b4c008ec4c0597540bdaba85e4a`; they have no field selecting only stopping.

The challenge in `cases/rail-crossings/refinement/relationships/window-0000/challenge/attempt-0000.response.json` calls each link supported and quotes the target only through its stopping-distance clause. It does not discuss the rest of that target. I regard the links as reasonable navigation, with an unresolved consumer interpretation. A consumer that treats an exception edge as disabling the whole node could infer too much. This is not a finding that a current consumer already makes that error. For reviewed workflows, identify the affected action explicitly or review a more precise split before treating the edge as executable applicability logic.

**Local references are not complete graph applicability.** Rail's baseline points to paragraphs (a)(1) through (6); six separate statements contain those vehicle classes. Those statements are not linked as explicit applicability alternatives to the baseline in the final graph. The substantive meaning is present across records, but traversing just qualification edges does not provide all vehicle applicability. Show related source context during discovery. Treat the prompt's promise of a completely self-contained statement as an aspiration these local-reference statements only partly meet.

Alcohol has a similar product boundary: its combined State reporting statement is accurate enough to find and explain the obligation, but a workflow builder must identify request-for-review, affirmation, recipient, and deadline reference event. More RDF nodes alone do not resolve those decisions.

**Actor/evidence issues are noisy, not proof of bad meaning.** Alcohol's first final statement has an unresolved actor and modality evidence issue even though the source's immediate lead-in says `No driver shall`. Actor `driver` repeats in the document; it is semantically straightforward but difficult to align from that short component quote. See `cases/alcohol/refinement/after.json`, first accepted record and its `issues`. Rail's shorter `the driver` also triggers an actor issue in its crossing permission. These are reasons to improve localization or show the inherited lead-in, not reasons to withhold useful search results indefinitely.

## Does validation match the quality?

The provenance mechanics are good. My read-only checks found no incorrect main-quote offsets or evidence offsets in either final export, no lost original summary, no dangling qualification target, and exact equality between final accepted records and the final-audit rulebook. The final history records two AI additions for alcohol and five AI edits for rail. Neither history contains human attestations.

All 66 alcohol and 56 rail Core assertions retain `rkaf:reviewQueueOnly` and `rkaf:draft`. That accurately represents their status for operational use. The report also explicitly retains `semantic_completeness=not_established`.

The other labels communicate more assurance than I would take from this run. Both initial and final audit reports say `passed` and `review_complete=true`, with every dimension correct. Final exported review summaries nevertheless say `needs_review`, 15 pending records apiece, and 12 alcohol / seven rail records with issues. Those statements have different meanings and are not inherently contradictory, but a product must explain which review is complete. “Model comparison completed; human review pending” is clearer than a prominent passed badge.

Every dimension is scored correct even for absent concepts, source attribution, effectivity, and optional action/object structure. The audit prompt permits empty structure when prose retains the meaning; that is sensible. Reporting the resulting score as universal correctness is not informative about what structured capabilities exist. Use not-applicable or explicitly distinguish prose completeness from populated-field accuracy.

Inventory granularity also changes independently of source quality. Alcohol's expected substantive units increase from 13 initially to 16 finally on the unchanged source, partly by splitting the review process and reporting branches. The first inventory calls the out-of-service commencement rule a requirement; the final inventory calls it a statement. Both comparisons are all-correct. This does not invalidate the good extraction, but it makes percentage coverage an unstable denominator and shows that the model inventory is not a fixed reference answer.

## Process cost and unnecessary ceremony

Summing the actual `usage_metadata.total_token_count` fields, excluding copied workspace/base-run responses, gives:

| Case | Source characters | Initial extraction tokens | Entire captured process tokens | Provider calls |
|---|---:|---:|---:|---:|
| Alcohol | 2,763 | 5,577 | 111,966 | 8 |
| Rail crossings | 2,907 | 6,563 | 133,717 | 8 |
| Total | 5,670 | 12,140 | 245,683 | 16 |

These are provider-reported token counts including reported thinking, not dollar estimates. The full process uses about twenty times the initial extraction tokens. Both empty recovery calls together use 41,635 tokens. Repeating the source-only inventory after changes reinterprets unchanged source while changing the coverage denominator.

The relationship packets repeatedly carry the whole source, full claim fields, evidence, inventory, and both audit judgment collections. In rail's `relationships/window-0000/packet.json`, serialized claim data alone is about 65,000 characters for a 2,907-character source. The model then returns complete replacement fields to change two relationship fields on each exemption. This is expensive copying with additional opportunities to erase otherwise correct fields.

My practical priorities are:

1. Keep the faithful initial extraction as the default search artifact; measure actual search retrieval and user corrections before making all eight calls mandatory.
2. Run recovery when there is a concrete suspected omission, or on a sampled quality-check population. These two empty calls do not justify an always-on pass by themselves.
3. Reuse the unchanged source inventory for the final comparison. Deliberate re-inventory can be a separate robustness experiment.
4. Send compact records and source references into relationship work, and make relationship-only edits narrow data changes. Preserve full provenance in storage without repeating it all in every prompt.
5. Spend review attention on affected-action scope, conditional deadlines, and unresolved applicability before adding more universal correctness scores.

For automatic discovery, perfection is unnecessary and these captures are already useful. The best next evidence is whether people find the right provision faster, see its qualifications, and can correct a misleading suggestion. For reviewed workflow-building, the preserved source and change history are a sound starting point; they do not replace decisions about actors, branch conditions, and the exact action an exception changes.
