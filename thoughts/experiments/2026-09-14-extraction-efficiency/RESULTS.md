# Extraction efficiency: useful savings, no production switch yet

The strongest token-saving candidate is to put several small sections in one
request while explicitly preserving each section as its own extraction task.
The pilot halved requests and saved 22.4% of total tokens without losing an
operative duty. Reference clarity improved in some records and weakened in
others. That warrants a broader comparison, not immediate adoption.

More aggressive output reduction saved more tokens by losing useful meaning.
Keep the current extraction behavior while testing a smaller input presentation
and, if waiting time matters, two concurrent unchanged requests. Neither needs a
planner model, mandatory audit, parallel schema system, or new extraction stage.

## What was tested

Three investigators ran four fresh provider calls each. A fourth agent manually
reviewed anonymized outputs against complete source, without the experiment
conclusions or additional provider calls. The root independently checked every
captured request's settings, response schema, finish reason and usage.

| Comparison | Measured saving | What happened to the result | Decision |
|---|---|---|---|
| Instruct omission; prohibit empty optional values when present | CSBG: 39.8% total tokens; benefits: 19.7% | CSBG's 13 plan contents became a generic pointer. Benefits lost useful term links and a supported actor. | Reject this change. |
| Combine two sections without explicit separate tasks | 2 calls to 1; 34.2% total tokens | 17 records became 12; several distinct duties were combined. | Reject naive grouping for independently usable requirements. |
| Combine the same sections with explicit section tasks | 2 calls to 1; 22.4% total tokens | All 17 records and operative duties survived. Some governing references improved; some report/evaluation references became ambiguous. | Best candidate for broader testing. |
| Select source clauses and assemble their exact text instead of generating statements | 35.9% total tokens across two sections | Preserved a difficult detail, but broke an OR into apparent separate duties and omitted governing scope. Default readings were 68.7% longer. | Reject as the default extraction path. |

These are single observations per source and arm on known development sources:
CSBG sections 9908, 9910, 9913 and 9914, plus the previously studied benefits
section 29 USC 1025(a). They are not an unseen-document benchmark or a whole-
chapter optimized run. The task-grouping follow-up changes both task boundaries
and granularity instructions; source assembly changes both prompt and response
shape. Their individual causal contributions are not isolated.

All twelve responses finished normally and validated against their actual request
schemas. Native decoding matched the output/window replay checks; source assembly
used a separately documented adaptation into Core, which rejected two invalid
kind/modality combinations. Passing JSON validation did not establish faithful
extraction. No live call used retries or an automatic audit.

## What the blind review adds

The independent reviewer received two unnamed sets containing all 17 records and
the complete 9913/9914 source. It found every operative duty, qualification,
alternative and modality preserved in both. Missing optional choice fields did
not imply lost alternatives when the statements still contained them.

After the review was saved and hashed, the key identified Set 1 as grouped tasks
and Set 2 as separate calls. Grouping identified 9913(c) and 9914 more clearly in
three records. Separate calls identified the evaluations and report more clearly
in three others. Both left some local references unresolved.

For example, the separate call says "On receiving the report of evaluations
conducted by the Secretary under 42 U.S.C. 9914(c)"; grouping says "On receiving
the report." The receipt trigger survives. The loss is identification of which
report, not omission of the trigger. Conversely, grouping resolves "this section"
to 9914 in the assistance permission, where the separate call does not.

This is mixed quality evidence. Neither version consistently supplies a statement
that can stand alone. Equal record counts and the investigator's 14 selected
detail checks would have missed these differences. The review is another
judgment on the same outputs, not an independent sample or expert-approved label.

## Where waste actually comes from

The committed complete CSBG run sent the same 135,797 focus characters through
27 section requests rather than six broader windows. It spent 121,039 input
tokens rather than 70,772. Section extraction also captured substantially more
meaning, so the cheaper broad run is not an equivalent-quality baseline.

Each current request repeats roughly 7,116 instruction characters, a 1,465-
character compact section index and an 11,438-character compact schema. Eight
section requests have fewer than 2,400 focus characters. This makes amortizing
request setup a credible target. Preserve meaningful schema guidance; the failed
omission study shows that apparently cosmetic constraints can change segmentation.

Some model-visible source metadata is also redundant: the model selects passage
IDs while local code already retains their coordinates. Showing ID-to-text values
instead of ID-to-start/end/text values removes 29,182 characters across the saved
chapter inputs, about 7% of prompt-content characters. This is an offline size
estimate, not measured token savings or evidence that accuracy stays unchanged.

Output placeholders are real overhead: the saved 282-record run contains 2,288
empty optional values, excluding required actor assessments. Removing only those
after capture shrinks compact response JSON 19.9% and preserves native decoded
candidates across all 27 responses. It does not refund provider output tokens.
The live omission intervention's quality loss prevents treating that offline
result as permission to change model instructions.

Finally, a large rulebook file is not all generated text. It contains retained
source, repeated evidence and graph records. Existing `discovery.export_discovery`
already provides shared source/evidence tables. Consumer prompts and embeddings
should select the needed records instead of repeatedly expanding whole graphs.
That can reduce downstream work without asking extraction to capture less meaning.

## Smallest practical next steps

1. **For faster interactive runs, qualify two concurrent unchanged requests.**
   Saved-duration scheduling suggests roughly halving provider time, but this is
   a simulation, not a live result. Token and request counts stay the same. Use
   independent model/client instances because capture temporarily swaps a client;
   preserve source ordering and partial failure receipts. No scheduler service.
2. **For a small input simplification, test omission of numeric passage coordinates
   from the model-facing catalog.** Preserve every source word, passage ID,
   meaningful section identity and CUE description. Test on new documents with
   governing-context and local-reference counterexamples.
3. **For fewer calls and tokens, broaden explicit small-section grouping tests.**
   Keep dense sections alone. Check complete independent meanings, not just topic
   or record counts. The pilot had essentially unchanged measured provider time
   (10.79 seconds separate versus 10.75 grouped), so promise neither speed nor a
   chapter-wide 22% saving.
4. **At the next actual consumer, reuse the shared source/evidence export.**
   Avoid another exporter or ontology until a caller demonstrates a concrete gap.
   A source-first search view already fits the platform. Generating complete prose
   only for selected workflow items remains an untested, more substantial product
   choice; the source-assembly experiment does not qualify it.

For non-urgent bulk work, the provider's Batch API is a separate billing option:
Google documents 50% of standard cost with a target turnaround of 24 hours. It
preserves independent model requests and needs asynchronous result/error handling;
we did not test an integration. Existing implicit caching is also preferable to
adding speculative cache infrastructure. See [provider notes](PROFILE.md) and
[official Batch API guidance](https://ai.google.dev/gemini-api/docs/batch-api).

These are alternatives selected by the actual bottleneck. Do not implement all
of them as a new multi-stage pipeline. The ordered, actionable checklist is
[saved here](../../plans/2026-09-14-extraction-efficiency.md).

## Receipts and stopping point

The twelve captured generation calls used **61,532 input tokens and 49,971 answer
tokens: 111,503 total**. Thinking tokens were not separately reported. These
counts exclude investigator reasoning and tool turns. No dollar cost was inferred
without a verified billing rate or receipt. Every request used `gemini-3.8-flash`,
low thinking, a 16,384 generation-token cap and omitted sampling controls.

The investigation is complete at its twelve-call limit. Research and the next-
decision checklist are saved; no production behavior was changed and no commit
was made. Nothing here needs an immediate production merge.

- [Actual request/response verification and usage](verification.json)
- [Request overhead profile](PROFILE.md)
- [Optional-field experiment](output/RESULTS.md)
- [Window/task-grouping experiment](windows/RESULTS.md)
- [Source-assembly experiment](process/README.md)
- [Independent manual source review](independent-review/REVIEW.md)
- [Original investigation plan](PLAN.md)
