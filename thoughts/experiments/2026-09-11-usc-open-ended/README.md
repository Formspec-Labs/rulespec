# Keep the full open-ended citation; do not invent its ending

The upstream correction is committed locally as RefSpec `53c0f387`.

The native reader previously emitted `38 U.S.C. 4301` from the actual source
`38 U.S.C. 4301, et seq.`. The small upstream correction retains the full written
phrase with `usc_open_ended_reference_unresolved`. It neither invents an ending
section nor treats the first section as the entire target. The same rule covers
the existing grammar's `and following` and `ff.` forms.

The [raw paragraph](source.json) and [before/after data](raw-comparison.json)
preserve the failure and correction. The prior occurrence function stays copied
in RefSpec's tests. On the 31 earlier inputs and five variants each, the new and
prior occurrence outputs agree. The whole-field reader continues to agree with
its separate copied oracle on the earlier seven-variant battery. The three
open-ended spellings are deliberate, asserted occurrence differences.

Validation: 503 owner tests pass (14 slow tests deselected), 579 full application
tests pass from source and installed wheels, and 116 focused USC tests pass in
the final isolated environment. The [wheel receipt](wheel-inputs.json) identifies
the builds installed in `reference-integration-20260911-usc-open-ended` and
`document-poc-venv`. The previous delivery remains available in its own directory.

The [positive reference CLI checks](cli-positive-working/checks.json) confirm that
both commands retain the full phrase and its refusal. Their saved historical
model response does not fit today's unit schema; its failed processing status
and unchanged baseline refusals are recorded separately in
[processing-status-review.json](processing-status-review.json). Reference export
success is not an extraction-success claim. No legacy conversion was added.

No provider call, prompt change, Core schema change or target lookup was needed.
This fixes the observed qualification loss, not every possible USC reference.
