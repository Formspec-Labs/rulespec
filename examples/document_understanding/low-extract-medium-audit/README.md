# Final low extraction → medium audit check

The pipeline produces useful source-linked drafts and preserves incomplete audit
work honestly. This full-section run supports the current low-extraction,
optional-medium-audit recipe, with remaining scope and inventory weaknesses.
It does not establish complete legal interpretation or automatic approval.

## Run and measurements

Input: the saved 6,919-character text of 29 CFR 825.110, covering employment,
hours, break-in-service exceptions, eligibility timing and headcount examples.
This is a pinned test document, not a refreshed statement of current law.

The production extractor used Gemini `gemini-3.8-flash` with low thinking. The
production audit used medium thinking for both its source-first inventory and
its comparison. All stages used temperature zero, a 24,000-character focus and
the provider output limit, without a numeric thinking budget. Three calls total;
no retries, repairs or prompt changes after reviewing the results.

| Stage | Reported tokens | Request seconds | Result |
|---|---:|---:|---|
| Low extraction | 8,530 | 12.20 | 19 accepted, 0 rejected, 0 extraction refusals |
| Medium inventory | 7,454 | 12.25 | 26 proposed entries; 4 refused |
| Medium comparison | 48,133 | 23.79 | 19 claims assessed; 20 accepted substantive units marked covered |
| Total | **64,117** | **48.24** | **Review incomplete** |

Every provider response ended STOP with complete JSON. The inventory contained
two background entries; after four substantive refusals, 20 substantive units
remained for coverage assessment. The comparison marked all 20 covered, but
`report.json` correctly says `needs_review`, `review_complete=false` and
`semantic_completeness=not_established`. This is not 100% source coverage.

One run does not measure typical cost, stability or accuracy. Request time omits
local setup and validation. Token totals are not dollar estimates.

## Direct source review

The raw extraction preserves the principal eligibility thresholds, both service
and written-rehire exceptions, USERRA service credit and entitlement limitation,
the payroll-week condition, 52-week equivalence, employer uniformity duty,
employer proof burden and teacher example, eligibility timing, non-FMLA
transition, and future-headcount example. The nonconsecutive-month rule passes
Core validation in this run, unlike one earlier low-thinking capture.

Remaining issues are specific:

- The accounting permission's summary and scope omit the governing USERRA and
  airline-flight-crew exceptions. Its `logic_text` retains them. The audit calls
  the claim correct without acknowledging that standalone wording weakness.
- The nonconsecutive-month statement omits its proviso; the scope records part
  of that context. The older-service permission similarly keeps uniformity in
  `logic_text` and a companion duty, rather than its standalone statement.
- Teacher details about other educational establishments and work outside the
  classroom remain in `logic_text` but are compressed from the statement.
- “Nothing prevents” is classified as permission, and the inventory calls a
  generally-qualified calculation statement permission where the extraction
  uses descriptive possibility. Such classifications are fallible observations.
- Two accepted claims retain unresolved modality evidence; repeated short
  supporting text is ambiguous. Logical grouping remains explicitly unexecuted.
- Explicit exception links are not emitted by normal extraction. Their absence
  does not establish link accuracy; relationship refinement was not tested here.

The audit inventory's four refusals are reproducible: two entries use the absent
marker `(c)(3)` even though the source uses `(3)` within section (c), and two use
the ambiguous marker `(d)`. Exact main quotations survive in the raw capture,
but those inventory entries are withheld. Other entries use bare `(e)` context;
its unique occurrence resolves mechanically without establishing substantive
scope. These are model/evidence limitations, not a reason to relax exact matching.

`source-review.json` preserves eleven revisable checks, selected statement,
scope and logic fields, raw audit judgments, and the four refused inventory
entries. It is an agent assessment of saved source, not independent gold labels.
No automatic corrections or review approvals were applied.

## Verification and discovery

All 333 package tests and six schema-generator tests pass. Native CUE generation
matches committed outputs. Production extraction and audit replay reproduce the
original rulebook and report exactly without provider calls. Discovery export
also reproduces identically and retains all 17 source passages, linked statements
and pending review status. Zero unlinked passages does not establish semantic
completeness.

Inputs, criteria and runtime were pinned before acquisition in `design.json`.
`extraction/` and `audit/` retain raw requests/responses, refused content, reports,
Core graphs and frozen runtimes with manifests. `verification.json` records the
checks and timings; `discovery.json` is the source-preserving consumer output.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/low-extract-medium-audit/experiment.py replay \
  --output /tmp/new-low-medium-replay
```

Replay needs the pinned runtime and a new directory. It never calls the model.
Use the [current operating guide](../../../packages/rulespec-extrapolator/README.md)
for fresh extraction, optional audit and downstream export.

## Stopping point

Retain low extraction for inexpensive drafts and medium audit as optional
feedback. Keep source, qualifications and review history available to consumers.
When development resumes, prioritize substantive inventory evidence and faithful
standalone scope. Do not add more reasoning or automatic repair loops before
those cases have an independent evaluation. No full-document high comparison or
additional tuning was run in this iteration.
