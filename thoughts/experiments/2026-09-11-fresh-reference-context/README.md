# Fresh reference context: keep the selector experimental

**Decision: defer adoption.** Supplying already located reference text did not
recover the declared missing meaning in any of the three selected cases, in
either observation. Both expanded-context outputs for title 20 changed one
permission's modality from `may` to `must`. One expanded-context response was
incomplete. Production context, prompts, schemas and model defaults remain unchanged.

## What was compared

The [preregistered design](design.md) compared normal production context (A) with
the same context plus unique operative reference targets and short enclosing
sections (B). Both arms used the existing generated schema and instructions,
`gemini-3.8-flash`, low thinking, temperature 0, and a 16,384-token output limit.
Three previously untuned USLM chapter selections supplied one normal extraction
window each, with two observations per arm in balanced AB/BA order: twelve calls.

The [source selection](source-selection.json), [manual source review](source-review.md),
[labels](labels.json), exact prompts and runtime identities were frozen before
execution. These are selected context opportunities, not a random document sample.
The three windows are not complete chapter extractions. The combined intervention
does not distinguish the effects of referenced text from enclosing-section text.

| Case | Additional source characters in B | Declared missing meaning recovered |
| --- | ---: | --- |
| Title 29, chapter 4B | 4,533 | Neither arm expanded the State-agency definition beyond its reference to section 49c |
| Title 38, chapter 7 | 7,228 | Neither arm supplied the adopted senior-position definition from section 713(d) |
| Title 20, chapter 6A | 10,152 | Neither arm completed a declared vending-income, set-aside or training meaning |

All twelve calls completed within the declared time bound, with no retry or
within-experiment tuning. One B output ended with `MAX_TOKENS`; its prefix was
read for diagnosis only and was not accepted as a complete response.

## Acceptance and cost

| Preregistered check | Result |
| --- | --- |
| Complete missing meaning gained on at least two cases, in both observations | Fail: zero of three cases |
| No new critical actor/modality/scope/exception error | Fail: the same title-20 authorization became `must` in both B observations |
| Preserve exact source evidence | Replay/export checks pass; existing processing losses described below remain |
| Mean total reported tokens B at most 1.5 times A | Pass: 1.089 times A |

| Reported usage across six requests per arm | A | B |
| --- | ---: | ---: |
| Input tokens | 72,792 | 84,824 |
| Answer tokens | 56,112 | 55,578 |
| Total tokens | 128,904 | 140,402 |
| Cached input tokens reported | 16,102 | 33,254 |

B used 8.9% more total reported tokens. Separate thinking-token counts were not
reported; their absence does not establish zero thinking usage. No dollar cost
is inferred without a verified price snapshot. Usage includes the incomplete
response. The [live command receipt](live-command.json) records elapsed time and
machine load; this run does not establish comparative latency.

## More valuable follow-up: preserve correct generated output

The [raw review](raw-review.md) examined all eleven complete response arrays and
the incomplete response's complete prefix rows and remaining tail. It separated
generated meaning from parser, Core and export behavior. The subsequent
[saved-output verification](processing-checks.json) passed exact request checks,
candidate/refusal replay, Core replay, discovery equality, retained source records
and exported evidence verification. These checks establish reproducibility,
not semantic completeness.

That verification found three concrete follow-ups:

1. **Complete quotations cross inserted formatting.** Across these repeated
   outputs, 103 Core rejections have quotations exactly present at their saved
   prepared-text coordinates. Every one crosses inserted whitespace. Core's
   single-fragment evidence check refuses them as absent or ambiguous. Reuse
   discovery's source-map slicing and existing evidence records to investigate
   retaining a complete statement with separately verified source fragments.
   Do not turn inserted text into original-source evidence.
2. **Valid passage ranges cross numbering holes.** Nine refused rows across
   three completed title-38 responses span `F054`, `F076` or `F178`. Those omitted
   catalog entries contain only a newline. Catalog numbering skips empty text
   after assigning numbers, while range resolution requires every number.
   Compare the smallest correction against the saved responses and counterexamples
   for unseen non-whitespace, missing endpoints and invalid ranges.
3. **Capture new reader modules consistently.** This experiment snapshots six
   additional application/native modules because the general runtime freezer
   predates their integration. Assess extending the existing capture path without
   making optional readers mandatory for plain-text extraction or Core validation.

The 103 and nine figures count repeated output events, not distinct legal rules
or population accuracy. Seven other Core rejections concern kind/modality
contradictions and require a separate semantic assessment. No output contained
a literal `"null"` field string; ordinary null-valued optional fields remain.

These processing defects can be tested with saved outputs, without another model
call. They do not explain away B's lack of gain in the raw statements or its
modality regression. More context may help a different consumer or intervention;
this result does not justify adding this selector to production.

## Preserved evidence and next work

- [Raw review](raw-review.md), [processing checks](processing-checks.json),
  [verification log](verification-command.log) and [completed receipt](verification-command.json).
- [Pre-run pins](prerun-pins.json), [context controls](final-controls.json),
  [cell order](cells.json) and [run results](run-results.json).
- The original failed freeze command remains saved. It failed on a `uv` argument
  before model execution; the corrected freeze passed controls and a no-op mutation.
- The [comprehensive task list](../../plans/2026-09-10-reference-integration-task-list.md)
  prioritizes the deterministic retention fixes and keeps broader reference,
  discovery and operational-preparation work open.

This experiment changed no production code and made no release or deployment.
