# Larger source windows, generation allowance and fitting lists

The user clarified that larger context and generation limits are acceptable.
The small stress-test windows are application choices, not model limitations.
Google's long-context guidance supports providing more relevant information up
front; it does not establish complete extraction accuracy for our task:
https://ai.google.dev/gemini-api/docs/long-context

Implemented a 24,000-character default source window (previously 6,000), with the
existing explicit `--max-chars` override. Added a positive integer
`--max-output-tokens` option through acquisition, recording and replay; the
current generation default remains 16,384 while a 32,768 allowance is evaluated.
When splitting is necessary, the planner uses existing source parent relationships
to move a fitting list group intact into the next window. It preserves exact
character coverage and the configured hard limit. Oversized groups still split.

The fuller saved leave section exposed compound `(c)(1)` markers, which now start
a new group instead of allowing later `(2)`/`(3)` to inherit the preceding `(b)`.
Focused tests cover this, list boundaries, oversized groups, Unicode coverage and
recording/replay of a nondefault generation allowance. The package suite passes
317 tests; the final marker-boundary adjustment also passes all eleven context
tests.

The completed frozen experiment is saved in
`examples/document_understanding/context-budget-experiment`:

- Full 29 CFR 825.110, all paragraphs (a)-(e), 6,919 characters, sourced from the
  already saved official XML. This exceeds the previous application window but
  remains far below model capacity; do not call it a model-scale long-context test.
- Input limits 6,000 versus 24,000 and generation allowances 16,384 versus 32,768,
  each combination repeated twice with current schema and prompt unchanged.
- Four additional saved-case runs (baggage/display, two repeats each) test fitting
  list boundaries at their previous stress limits and 16,384 generation allowance.
- Twelve runs, twenty planned calls total. No retries or repair calls. Compare
  packing against saved old-boundary controls with that historical limitation.

All twenty calls completed, producing 191 accepted statements with no parsing
refusals or Core rejections. All twelve runs replay exactly; raw statement,
scope, kind and modality match compiled values. Total reported usage is 153,753
tokens including thinking. The package suite passes 317 tests; the final marker
boundary adjustment also passes all eleven context tests.

Larger intact leave input uses one request instead of two and fewer tokens in
these observations. More output allowance does not consistently improve meaning:
whole-input 32K runs lose schedule/example detail retained by smaller-focus runs,
and one combines many independent meanings. Both allowances retain recurring
proviso, scope and reference-topic gaps. This small study does not establish
model-scale lost-in-the-middle behavior or a generally optimal context size.

The list-boundary change recovers complete firearm and storm-condition statements
in both repeats at their original source/generation limits. All four new runs
complete versus one of four saved old-boundary controls. Historical controls
limit causal attribution; input completeness is independently verified. Scope
and logical-evidence problems still exist in the recovered records.

Decision: retain the 24,000-character configurable source default, fitting-list
boundaries and compound-marker correction. Keep generation default at 16,384 and
expose the tested 32,768 allowance through the new option. More room is available
without asserting that a larger cap fixes semantic omissions. No schema/prompt
change or new mandatory review stage is added.

The [experiment README](../../examples/document_understanding/context-budget-experiment/README.md)
links the full source, pinned comparisons, ten source-review findings, request
checks, replay results and usage. A next evaluation should use genuinely longer
documents with beginning/middle/end coverage checks. Original captures remain
unchanged; work is local and uncommitted. No commit was requested.
