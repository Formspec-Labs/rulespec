# Higher thinking effort, with no application token cap

High thinking recovered useful leave-document details and separated more meanings. It needed enough room to finish: two of four high runs failed at a 32,768-token generation cap; all four follow-up high runs completed with that cap omitted. This is a small source-reviewed experiment, not a general accuracy benchmark.

Use the normal extractor:

```sh
.tools/document-poc-venv/bin/rulespec-understand extract source.json \
  --thinking-level high --max-output-tokens provider \
  --env-file /path/to/credentials.env --output /tmp/new-high-thinking-run
```

`thinking_budget` and `max_output_tokens` are absent from these requests. Gemini retains its own limits; a live model metadata lookup reported 1,048,576 input and 65,536 output tokens for `gemini-3.8-flash`. This is not unlimited generation. The request timeout is five minutes; retries remain disabled. Normal defaults remain provider-selected thinking and a 16,384-token total generation allowance.

## What changed

The previous extractor did not send a thinking budget or level. [Google's current guidance](https://ai.google.dev/gemini-api/docs/thinking) lists medium as the default for Gemini 3.8 Flash. The installed LangExtract 1.6 adapter filters `thinking_config` out of both constructor and inference arguments. The existing SDK request-recording function now sets the explicit level before recording and sending the exact request. No schema or prompt changes were needed.

`--thinking-level` accepts low, medium or high. `--max-output-tokens provider` omits the application cap. Run records preserve both choices; replay and reprocessing verify the actual requests. Existing Core evidence, provenance and refusal handling remain in use.

## Comparison

Initial stage: eight fresh requests comparing explicit medium/high, at temperature zero, with a 32,768-token total generation cap. Each document fits in one 24,000-character window. Leave has two repeats per level; baggage and display have one. Only thinking level differs in paired request contents/configuration.

Follow-up: four declared high requests, two repeats each of leave and display, with the application generation cap omitted. Exact captured requests match the capped high requests after removing that one field. Timeout increased from 120 to 300 seconds to accommodate greater output; one successful follow-up took 133 seconds. The earlier failures returned MAX_TOKENS rather than timing out. The follow-up did not rerun medium controls, so it is sequential evidence, not a second complete factorial comparison.

| Run | Outcome | Accepted meanings | Reported tokens | Request seconds |
|---|---|---:|---:|---:|
| leave-full-medium-1 | complete | 11 | 10, 100 | 15.6 |
| leave-full-high-1 | complete | 23 | 33,756 | 69.1 |
| baggage-high-1 | complete | 7 | 17,347 | 34.9 |
| baggage-medium-1 | complete | 6 | 4,801 | 6.5 |
| display-medium-1 | complete | 20 | 19,737 | 40.2 |
| display-high-1 | failed | 0 | 34,975 | 82.0 |
| leave-full-high-2 | failed | 0 | 36,154 | 73.7 |
| leave-full-medium-2 | complete | 11 | 7,481 | 11.3 |
| provider-limit/leave-full-high-1 | complete | 23 | 33,459 | 66.2 |
| provider-limit/display-high-1 | complete | 17 | 52,219 | 133.3 |
| provider-limit/leave-full-high-2 | complete | 20 | 26,694 | 51.3 |
| provider-limit/display-high-2 | complete | 18 | 37,474 | 84.3 |

Across both stages: **12 model calls, 314,197 reported tokens, 156 accepted meanings, 12 identical replays**. Two failed captures remain preserved with MAX_TOKENS/malformed-JSON refusals and zero accepted meanings. Token totals include thinking. A count of accepted meanings is not an accuracy score.

## Source-review findings

- **Leave: repeatable topic recovery.** Both uncapped high runs retained the teacher example and its inaccurate-record context, flight-crew/outside-US references, intermittent/reduced schedules, the qualified August/December headcount example, and distinct eligibility timing. The medium runs omitted teachers and schedule variants from their statements. High also separated payroll/52-week definitions and permission/uniform-treatment duty. It produced 23/20 meanings versus 11/11 at medium; some gains are finer splitting rather than recovered omissions.
- **Baggage: a useful one-run gain.** At 32K, high preserved who receives the firearm declaration and what must be declared. Medium omitted those details. Both still misclassified the weapons exception and ammunition non-prohibition as `not_required`. No uncapped baggage follow-up was necessary to investigate truncation.
- **Display: completion improved, semantic gains were mixed.** Medium and both uncapped high runs retained the principal rules, alternatives, storm prerequisites, warning expiry, recommendation and investigation extension. High used complete storm component evidence in one repeat and only the lead-in in the other. One high repeat merged paper-map non-prohibition with possible outside restrictions under `possible`; the other kept them separate.
- **Splitting still loses context.** Standalone old-service permission omits its uniform-treatment condition. Accurate-accounting permission omits inherited exception context. The full source evidence remains available, but not every extracted statement or scope is independently complete. Broad display baselines still duplicate individual duties.

The uncapped high leave runs averaged about **3.4 times** the reported tokens of medium; display averaged about **2.3 times** its single medium control. Higher effort is promising for richer extraction, with greater token use and latency. Keep it available explicitly; this experiment does not justify changing the cheap default everywhere.

## Evidence and verification

- `design.json` and `provider-limit/design.json`: settings, frozen runtime hashes, exact input/script hashes, declared calls before acquisition.
- `criteria.json`: existing, revisable source-review criteria reused without changing the rubric after results.
- `runs/` and `provider-limit/runs/`: full source, prompts, schemas, SDK requests, raw responses, frozen runtime, accepted/rejected results and refusal history.
- `source-review.json`: nine findings with exact raw rows, accepted IDs and response hashes.
- `verification.json`, `provider-limit/verification.json`, and `provider-limit/cross-stage-verification.json`: replay, raw-to-accepted meaning checks and controlled request differences.
- `results.json`, `model-limits.json`, `test-verification.json`, and `manifest.json`: run totals, live limits, tests and artifact hashes.

All 327 package tests passed after the final runtime change, including the real LangExtract adapter path, omitted token caps, replay/reprocessing and tampering checks. All 12 runs replayed without provider calls. The first eight replayed before adding provider-limit support; the final four replayed under the final runtime. Original frozen runtimes remain available, and strict replay refuses a mismatched installed runtime. Structural validity and repeatability do not establish semantic completeness.

To verify the final four under their pinned runtime:

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/thinking-level-experiment/provider-limit/verify.py \
  /tmp/new-thinking-replay-directory
```

No original captures or review history were replaced. No UI changes. Work remains local and uncommitted.
