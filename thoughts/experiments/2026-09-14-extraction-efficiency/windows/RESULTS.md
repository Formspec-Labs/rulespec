# Fewer calls are possible; naive grouping changes the product

**Four native captured calls found a bounded token saving, but no change is ready for default adoption.** Grouping two small adjacent CSBG sections saved 34% total recorded tokens while merging independently referenceable requirements. Adding explicit section task identities and a short granularity instruction restored those records and retained 22% savings. A remaining antecedent regression limits standalone usability.

No production code, schemas, defaults, or commits changed. Calls used current installed Rulespec helpers, Gemini 3.8 Flash, low thinking, provider-managed sampling, a 16,384-token allowance, and no retries. No new model output structure or audit pass was introduced.

## What was tested

The [raw review packet](RAW-REVIEW.md) contains both complete source sections, every generated default statement, and its exact evidence coordinates.

The source is the retained 42 USC chapter 106, release 119-102. The selected same-coverage comparison contains all 4,911 source characters of sections 9913 (training/assistance) and 9914 (monitoring), including the historical committee-name note. This is selected development data. The known difficult application section 9908 was not rerun or fixed.

The original [plan](PLAN.md) specified a three-call comparison. The [fourth-call follow-up](FOLLOWUP-PLAN.md) was written after seeing naive grouping lose granularity, before collecting its result. It deliberately bundles task identities and a granularity instruction; attribution to either individually is unresolved.

| Measure | Separate sections A | Naive grouped B | Grouped with explicit tasks |
|---|---:|---:|---:|
| Calls | 2 | 1 | 1 |
| Source focus characters | 4,911 | 4,911 | 4,911 |
| Records | 17 | 12 | 17 |
| Input tokens | 6,569 | 4,162 | 4,297 |
| Candidate output tokens | 4,235 | 2,945 | 4,089 |
| Total recorded tokens | 10,804 | 7,107 | 8,386 |
| Sum of measured call seconds | 10.79 | 7.54 | 10.75 |
| Selected source-detail criteria retained | 14/14 | 14/14 | 14/14 |
| Monitoring duties individually represented | 4 | 1 composite | 4 |
| Training-process duties individually represented | 2 | 1 composite | 2 |
| Parser refusals / truncations | 0 / 0 | 0 / 0 | 0 / 0 |

The fourth call reduces input tokens 34.6%, candidate output 3.4%, and total recorded tokens 22.4% relative to the separate controls. There is **no measured latency improvement** for that arm. These are provider usage counts, not a billing calculation; thoughts-token usage was absent in all responses. Total experiment: 4 calls, 26,297 recorded tokens, 29.08 summed call seconds. Model request/response versions and actual settings are in the retained captures.

## Raw review: what the aggregate scores miss

All 14 predeclared detail criteria survive in the default statement(s) of every arm: reserved-fund uses; grants/contracts/agreement alternatives and permission; maximum feasibility; local network input; direct distribution and recipient expertise; 3-year reviews; first-year timing; prompt followup; as-appropriate reviews and terminated-grant exclusion; optional State requests; annual federal evaluations; report/response requirements; congressional recipients. The committee-name note remains factual rather than a fresh duty. State/Secretary actors and the two permissions do not leak into neighboring duties.

Naive grouping nevertheless combines four different monitoring duties into one long record:

> ...the State shall conduct the following reviews... (1) a full onsite review...; (2) an onsite review of each newly designated entity...; (3) followup reviews...; and (4) other reviews as appropriate...

The same source becomes four separate records in both A and the task-directed arm. This matters when another system needs one requirement per review type. Naive grouping also combines the two required training-process features and the separate allocation actions. Token saving partly comes from changing granularity, not purely removing waste.

A portability regression remains even after restoring record counts. Compare the [complete source](RAW-REVIEW.md#source-9914), [fresh separate record 7](RAW-REVIEW.md#a9914-record-7), and [task-directed record 14](RAW-REVIEW.md#btasks-record-14). The fresh separate control says:

> On receiving the report of evaluations conducted by the Secretary under 42 U.S.C. 9914(c), the State must submit to the Secretary a plan of action in response to the recommendations contained in the report.

The task-directed arm says:

> On receiving the report, the State shall submit to the Secretary a plan of action in response to the recommendations contained in the report.

The latter retains the receipt trigger (so it passes the narrower criterion) but leaves **which report** in another record/source context. That is weaker for independent downstream use. Other local pointers, such as paragraph(1)(A), also remain in both arms. A source location or adjacent record does not turn these into complete independent meanings. The selected 14 checks therefore do not establish semantic completeness or a no-regression production gate.

## Where the input cost actually goes

The historical full section run makes 27 requests for 135,797 focus characters. Actual prompt strings contain 417,533 characters in aggregate; the serialized schema adds 308,826 characters. These are separate exact serialized-character measurements, not tokenizer estimates.

- The identical 7,120-character instruction/example prefix is repeated 27 times: 192,240 characters.
- The full 26-section label/start/end index repeats 27 times: 41,121 characters.
- Actual extra context is only 913 source characters across the full run. Parent/neighbor context is **not** the main duplicated-text cost here.
- Every request receives the same 11,438-character compact-serialized provider schema.
- The historical preamble request is not empty: it extracts an Act codification/history statement. Calling it a no-op and deleting it would silently change source coverage or desired content, despite being unhelpful for a narrow application-only product.
- Actual historic cache use was 4,600 input tokens out of 121,039. No new explicit cache experiment or external cache/billing assertion was made.

The evidence supports amortizing repeated instructions/schema across bounded independent tasks, not stripping source conditions or replacing the authoritative CUE schema with a parallel shape. Removing provider-unneeded location metadata is another simple candidate; this task did not test it.

## Whole-document scheduling simulations (not model results)

A greedy merge only combines adjacent complete existing windows while their union fits a limit. Large sections remain alone. All 135,797 focus characters and all source section identities remain; the difficult 14,756-character 9908 window is unchanged at every limit.

| Maximum grouped characters | Simulated calls | Prompt characters | Repeated schema characters |
|---|---:|---:|---:|
| Current section mode | 27 | 417,533 | 308,826 |
| 4,000 | 25 | 399,361 | 285,950 |
| 6,000 | 21 | 363,017 | 240,198 |
| 8,000 | 18 | 335,757 | 205,884 |
| 10,000 | 17 | 326,671 | 194,446 |

These simulations omit the small explicit-task directive and do not predict token counts, truncation, or semantic quality. The tested pair is grouped by the 6,000-character schedule.8,000 and 10,000 are untested configurations, not recommendations.

Current extraction loops serially. If each saved provider duration stayed fixed, scheduling the same 27 requests on two workers would change provider critical-path time from 192 seconds to 97 seconds; four workers gives 53 seconds. This is simulation only: no contention, rate limits, scheduling overhead, or provider variability modeled. Concurrency should change latency rather than token/call counts. `_record_window` temporarily replaces `model._client`, so a safe implementation needs an independent model/client per worker and deterministic serialized result aggregation; sharing the current mutable model would be unsafe.

## Recommended smallest next moves

1. **For speed with minimal meaning risk:** evaluate bounded concurrency 2 over the exact existing requests. Keep per-window captures, no implicit retry, one terminal result per window, and deterministic aggregation. This does not reduce tokens or calls.
2. **For actual call/token savings:** run one preregistered broader comparison of separate sections versus bounded task-directed grouping at 6,000 characters. Keep dense long sections unchanged; include independent-reading checks for report/list antecedents. Stop rather than tune this selected pair again. The current small result justifies investigation, not adoption.
3. **For simple input hygiene:** test omitting redundant numeric positions from the model-facing passage/index presentation while preserving them in local resolution/capture. Let the parent investigation combine this with its own measurements; do not discard necessary source text.
4. **Avoid a planner model or universal extra audit:** neither is needed to choose adjacent structural windows or parallelize unchanged calls. Keeping task identities in the input and a flat CUE response is simpler than a second model/schema/stage.

## Reproduction and limits

[run.py](run.py) prepared and made the three original calls through `_record_window`, `_attempt_result`, and current schema generation; [followup.py](followup.py) captured the fourth. [setup.json](setup.json), [pins.json](pins.json), and [frozen/](frozen/) retain the source/runtime/settings evidence. The original full source is pinned at the already committed retest path.

[analyze.py](analyze.py) recomputes static schedules and reruns native raw-response parsing. [replay.json](replay.json) verifies identical parse output for all 4 captures; this is extraction-stage replay, not a claim that the standalone research directories are full public-CLI run manifests or that Core graph/export has been qualified for a new batching implementation. No production implementation exists yet.

Manual judgments are revisable assistant assessments. There is one observation per arm; repeatability, new-document generalization, dense-section quality, real concurrency, explicit caching, and monetary cost remain untested. Raw failures would have counted; none occurred. The broader independent-usability gate remains unmet.
