# Full-section inventory: passage IDs avoid six fresh quotation failures

The passage-ID inventory resolved all 20 proposed observations. The fresh
quotation-based inventory refused six of its 22 observations. Both retained the
teacher example's inaccurate-record condition, but both still omitted details
and had classification or standalone-scope weaknesses. This supports the evidence
selection change; it does not establish complete interpretation.

## What ran

Two fresh Gemini `gemini-3.8-flash` calls inventoried the same saved 6,919-character
leave-eligibility section and original full-section window. This is development
data already used in earlier experiments, not an unseen evaluation document.

- Quote: the current production inventory prompt and schema, including the
  newly adopted complete-meaning/example guidance from CUE.
- Passage: the frozen CUE-generated passage-ID inventory schema and its associated
  evidence instructions, with that exact same current CUE guidance appended.

Both used medium thinking, temperature zero, no numeric thinking budget and no
application output cap. There were no retries, extraction calls, draft comparisons
or repairs. Shared capture/resolver and quotation-parser function bodies were
checked against current production before setup; the experiment runs using pinned
frozen helpers without changing the installed implementation.

This compares two implementation variants. Schema constraints, descriptions, enum
order and evidence-selection wording differ. It is not a pure causal test of ID
syntax alone. The current guidance and generation settings are equal across arms.

## Results

| Measure | Quote | Passage IDs |
|---|---:|---:|
| Raw observations | 22 | 20 |
| Accepted observations, including one background entry | 16 | 20 |
| Accepted substantive observations | 15 | 19 |
| Refused observations | 6 | 0 |
| Reported tokens | 8,424 | 5,593 |
| Request seconds | 13.83 | 9.57 |

Both responses ended STOP. Combined tokens: **14,017**. Different segmentation
means accepted-row counts are not source recall. These are single observations,
not stable latency, accuracy or cost estimates.

The quotation failures are concrete:

- The cumulative eligibility definition changes source newlines in its quotation.
- The written-rehire alternative splices its parent lead-in and later list item,
  omitting intervening text, so the quotation is not contiguous.
- The 52-week equivalence cites ambiguous `(3)` scope.
- USERRA service credit and schedule calculation each cite ambiguous `(2)` scope.
- Non-FMLA leave transition cites ambiguous `(d)` scope.

The existing parser correctly refuses these references. Exact substantive
meanings remain in raw responses but cannot all enter accepted inventory. The
passage arm selects supplied passages/ranges for these topics without rewriting
source text. Direct inspection found its selections relevant to their topics;
whole passages can include additional material and do not themselves prove every
interpretive component.

## Meaning review

The initial meaning-only packet used shuffled A/B labels and hid evidence-format
fields. Its assessment was saved before revealing the key: A was passage, B was
quote. Complete raw evidence was inspected afterward. This reduces arm-label bias;
it is still a same-agent review, not independent adjudication or gold labels.

Both retain the principal topics in their raw meanings: eligibility requirements,
both service/rehire alternatives, service-credit limits, payroll-week and 52-week
rules, uniformity duty, accounting rules, teacher proof, eligibility timing and
headcount examples. The passage arm keeps all four formerly refused topics in
accepted observations, grouping the burden and teacher example together. The
quote arm again refuses the non-FMLA transition; its other three targeted topics
resolve in this fresh call.

The passage arm keeps accounting exceptions within its combined accounting rule.
The quote arm retains those exceptions in the main calculation rule but omits
them from a separate accurate-accounting permission. Both now retain the teacher
example's inaccurate-record condition.

Remaining defects prevent a clean semantic result:

- Both compress teacher details and omit outside-classroom/home work and the
  teacher-definition reference from explicit meaning.
- Both omit the eligibility-notice reference and its topic from explicit meaning.
- Both leave uniformity outside the separately stated older-service option.
- Both classify no-obligation language as permission in at least one place.
- Passage classifies the uniformity must-duty as a condition; quote classifies
  generally usable schedules as a recommendation despite permissive/descriptive
  wording. Non-FMLA permission versus possibility also remains a concern.

The initial assessments and subsequent evidence review are preserved separately
in `blind-source-review.json`, `review-key.json`, `source-review.json` and
`evidence-diagnostics.json`. These judgments remain revisable.

## Decision

Evidence selection shows a bounded improvement. The broader clean-meaning
criterion is not established. Proceed next with a narrow integration of the
CUE-generated passage-ID inventory and existing resolver, preserving current
example guidance, raw refusals and provenance. This is a proposed engineering
adoption of the evidence improvement, not a declaration that semantic gates passed.

The existing [deterministic check](../refused-evidence-check/README.md) showed that
reviewed IDs can resolve the original failures; this call adds evidence that the
model can select valid IDs on the original full-section window. One call is still
insufficient to establish stable selection behavior or generalization.

No production integration was performed in this experiment. Keep known meaning
failures visible and assess them separately. No new Core schema, grouping prompt,
automatic repair or higher-thinking pass is justified by this comparison.

## Preservation and replay

`design.json` pins the input document/window, criteria, runner, current prompt and
schema configuration, production source snapshots, and original/frozen manifests.
`runs/` retains actual requests, responses, attempts, inventories and per-run
manifests. `verification.json` records setup parity, settings, counts and replay.
The outer manifest covers all experiment artifacts except bytecode caches.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/full-inventory-evidence-comparison/experiment.py replay
```

Both inventories, aggregate results and the randomized review packet replay
identically without provider calls. The operating guide and active handoff were
updated; no implementation changed, so production tests were not rerun. Existing
uncommitted example-guidance changes and all earlier captures remain intact.
