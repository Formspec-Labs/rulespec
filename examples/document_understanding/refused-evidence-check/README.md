# Four original audit refusals: evidence location isolated

All four original refusals reproduce. All four resolve when supplied with
reviewed substantive quotations through the existing parser, or reviewed passage
IDs through the saved prototype. Their model-written meanings and kinds remain
unchanged. No model calls or production repairs were made.

## What was checked

The [original full-section audit](../low-extract-medium-audit/README.md) proposed
26 inventory rows and refused four. This check verifies its saved manifest and
recreates its original inventory exactly, including the same four failures.

| Original row (zero-based) | Original scope reference | Exact occurrences | Reviewed passage |
|---|---|---:|---|
| 18: employer proof burden | `(c)(3)` | 0 | `F014` |
| 19: teacher example | `(c)(3)` | 0 | `F014` |
| 20: eligibility determination date | `(d)` | 2 | `F015` |
| 21: non-FMLA leave transition | `(d)` | 2 | `F015` |

All four main quotations already resolve. The problem is their additional scope
references. The source writes `(3)` inside section (c), not `(c)(3)`. The string
`(d)` occurs at offset 5302 inside the citation `§ 825.801(d)` and at offset 5370
as the next paragraph marker. Exact matching correctly refuses ambiguity.

`F014` is the complete employer-burden/teacher paragraph at `[4440, 5368)`;
`F015` is the complete eligibility-timing paragraph at `[5370, 5933)`. These are
existing catalog entries, selected by direct source review for this local test.
They are not new model predictions.

For each row, the check compares:

1. The original row: refused because its scope marker is absent or ambiguous.
2. The same row with its scope marker replaced by the substantive paragraph
   text: accepted by the existing quotation parser, preserving its main quote.
3. The unchanged meaning and kind with the reviewed whole-paragraph passage ID:
   accepted by the frozen passage-ID prototype. The original main quote is
   contained in that paragraph, whose text includes the relevant context.

Every repaired-reference fixture retains exactly the original meaning and kind.
The source captures and original audit report are untouched. Local parser inputs
are explicitly labeled `fixture_only` and `not_provider_output`; they are not
fabricated provider captures or applied extraction corrections.

## What this proves—and what it leaves open

The existing exact-match machinery is sufficient when given substantive,
unambiguous text. Passage references can reuse the existing catalog and resolver;
there is no need for fuzzy matching, a new resolver or another Core schema.
Both approaches pass the evidence-location check. This test does not establish
that a model reliably makes those selections, or that passage IDs outperform
quotations in fresh calls.

Three negative fixtures using an absent main ID, absent scope ID and invalid
range are refused. A fourth deliberately selects the unrelated headcount passage
`F016` for the teacher rule. It passes structural checks despite not supporting
that meaning. A valid location is not a semantic assessment.

The unchanged meanings illustrate the same boundary:

- Row 19 still omits the inaccurate-record condition from its teacher statement.
  Selecting the correct whole paragraph makes the condition available as evidence;
  it does not insert it into the meaning.
- Row 21 still classifies “may be on non-FMLA leave” as permission. Whether this
  describes a possibility instead remains a separate interpretation question.
- Row 20 names 1,250 hours, while its selected paragraph says “hours of service
  requirement.” The number occurs elsewhere in the full source. Selecting the
  right paragraph for the original quotation does not prove that it alone
  substantiates every component of the model's meaning.

`source-review.json` records these revisable observations. The original report
remains `needs_review`, `review_complete=false`, and semantic completeness
`not_established`. No coverage verdicts were recomputed or upgraded.

## Decision and next step

The deterministic location check passes. Keep exact matching and retain the
passage-ID prototype as an evidence-selection candidate. Its fresh-model behavior
and remaining semantic issues still need evaluation; do not describe these four
reviewed selections as a production fix.

The next useful comparison is fresh quotation-based versus passage-ID inventory
on the original full-section window, with the adopted example guidance retained.
Report reference failures separately from conditions, classifications and other
meaning defects. This is a proposed next step, not executed here.

## Replay and provenance

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/refused-evidence-check/check.py replay
```

`design.json` pins the original capture manifest, frozen prototype manifest,
runtime, source fixture, selections, criteria and check script. The script invokes
both saved inventory parsers and the existing passage resolver. `results.json`
retains the original failures, corrected-reference outputs and negative controls.
The outer manifest covers all local artifacts.

No credentials, provider requests, extraction calls or comparison audits are
needed. No implementation or defaults changed. Existing uncommitted production
guidance changes remain intact; only the active handoff and operating guide were
updated afterward. All research remains local and uncommitted.
