# Gemini 3.8 Flash with low thinking

Low thinking is promising for the inexpensive first pass: these four calls used **26,522 reported tokens, 82.3% fewer** than the four saved high-thinking controls, and took **8–12 seconds each**. The display rules held up well; leave extraction was less consistent. No default was changed.

## Test

Two repeats each on the full leave section and invented display policy. Same model (`gemini-3.8-flash`), temperature zero, intact 24,000-character windows, source, prompt, schema and runtime as the saved [high/provider-limit controls](../thinking-level-experiment/README.md). Actual captured requests differ only in thinking_level=low. No thinking_budget or max_output_tokens is sent. No retries, repairs or model audit calls. Controls were saved earlier, not rerun contemporaneously.

| Run | Pipeline outcome | Accepted | Rejected | Reported tokens | Request seconds |
|---|---|---:|---:|---:|---:|
| leave-full-low-1 | partial | 20 | 1 | 8,346 | 11.9 |
| display-low-1 | complete | 18 | 0 | 5,685 | 10.3 |
| leave-full-low-2 | complete | 12 | 0 | 6,946 | 9.3 |
| display-low-2 | complete | 18 | 0 | 5,545 | 8.0 |

All four provider responses ended STOP with valid JSON. Three pipelines completed; the first leave run is partial because Core rejected one candidate whose `statement` kind contradicts its `not_required` modality. All 69 raw rows remain accounted for: 68 accepted and one preserved rejection. This rejection removes the nonconsecutive-month meaning from the accepted graph even though its raw wording is present.

No separate thinking-token count was reported for low. That does not prove the model performed no internal reasoning. The matched high controls used 149,846 total tokens and took 51–133 seconds per request. Per-source reduction: about 75% for leave and 87.5% for display. These are token and latency comparisons, not measured dollar savings or an accuracy score.

## What the raw review found

- Both display repeats preserved the main duties and inherited context, all storm prerequisites, warning expiry, alternatives, recommendation force and investigation extension. They also avoided the duplicate broad baseline emitted by high. Paper-map non-prohibition still becomes a permission label, and complete storm component evidence varies between repeats.
- Leave repeat 1 retained teachers and the future-headcount example; repeat 2 omitted those topics from statement/scope, merged more clauses and placed leave-schedule variants only in scope. Saved high runs retained those details more consistently. A retained citation or source quote does not itself mean its topic is expressed in the statement.
- Both leave repeats preserved the main eligibility thresholds, USERRA/rehire alternatives and distinct timing rules. Standalone permissions still lose inherited conditions, while grouped records can combine distinct modal forces. More thinking did not eliminate those problems either.

Use the existing option:

```sh
.tools/document-poc-venv/bin/rulespec-understand extract source.json \
  --thinking-level low --max-output-tokens provider \
  --env-file /path/to/credentials.env --output /tmp/new-low-thinking-run
```

This supports testing low extraction plus a stronger audit next; that combination has **not** been evaluated here. Four calls on two familiar documents are insufficient to establish a production default.

## Saved evidence

`design.json` pins inputs, runtime and saved control hashes before calls. `runs/` contains exact requests, raw responses, candidates, Core results and frozen runtime. `source-review.json` records six findings with raw rows and accepted/rejected dispositions. `verification.json` verifies replay and request differences. Its coarse raw_meaning_preserved flag is false for the partial run because a row was rejected; `raw-dispositions.json` verifies every individual row and confirms all accepted meaning fields were preserved. `results.json` records usage and timing; `manifest.json` binds artifacts.

All four runs replayed identically without provider calls. No production code/schema/prompt changes were needed, so the unchanged package suite was not rerun. The saved 327-test gate from the preceding iteration covers the same runtime; this experiment adds real endpoint and replay evidence, not a new accuracy guarantee. Original high captures and review history remain unchanged. Work is local and uncommitted.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/low-thinking-experiment/verify.py \
  /tmp/new-low-thinking-replay-directory
```
