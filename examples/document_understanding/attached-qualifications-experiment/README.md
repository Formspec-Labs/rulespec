# Attached qualifications and source references

The trial creates the desired previous-name exception link and preserves the
document-option list without asking the model to recopy it. However, it also
creates misleading relationships and loses important inherited conditions.
Keep it isolated; it is not a replacement for the current extractor.

## Scope and cost

Two new Gemini 3.8 Flash calls at temperature 0, compared with the saved current
controls from `../indexed-statements-experiment/runs/*-current`. No retries,
audits, or repair calls. Both use the exact same names and photos source text.
These are familiar development excerpts, not a held-out sample.

| Measure | Saved controls | New trial |
| --- | --- | --- |
| Names baseline statements | 13 | 10 |
| Photos baseline statements | 10 | 7 |
| Names qualification links | 0 | 6 |
| Photos qualification links | 0 | 5 |
| Reported total tokens, both documents | 21,542 | 16,301 |

The trial used about 24% fewer reported tokens. Its shorter prompt and grouped
statements contribute to that reduction. Lower token count and more links do not
establish better extraction. The final conversion accepts 16 names records and
12 photo records, including their generated qualifications; these are not counts
of independently verified rules.

## What changed

The experimental CUE schema reuses existing profile/Core field types. Statements
contain `qualifications`, each with a relation, statement, and source references.
Nesting identifies the intended target. Code creates ordinary Core condition or
exception records and their relationship assertions, keeping everything in draft
review state.

Main, scope, context, option and choice evidence select supplied passage IDs or
contiguous ranges. The catalog comes from `documents.source_passages`; code
recovers the exact source text and offsets. It does not infer legal scope from
structural parents. Other short quotation fields retain the existing format.

Each nested family compiles separately through existing Core functions before
building the combined graph. This preserves the specified parent when two
statements share a quotation. A later global quote-based relink would discard
that disambiguation; this experiment does not claim full review-store integration.

## Source-review findings

**Successful mechanics:** The previous-name exception now targets its prohibition.
The older-name-change suspension trigger and the replacement-photo trigger also
have appropriate targets. All selected passage references resolve. All six name
document options survive final acceptance with original list markers and line
breaks. Both graphs validate, and offline conversion reproduces exactly.

**Lost conditions:** The emergency permission says:

> If there is insufficient time to request that the applicant submit acceptable
> ID prior to urgent or emergency travel, a limited-validity passport may be
> issued in the requested name.

It omits the governing older-than-one-year name change, DS-11 application and
unchanged-ID case. Those limits are also absent from `scope_text` and the attached
trigger statement, although the referenced source paragraph still contains them.
The saved control retained those limits in its explicit meaning.

**Misleading relationships:** The trial attaches the hairstyle acceptance as an
exception to the whole photo recency/likeness recommendation. The source does
not waive six-month recency. It also turns the explanation that applicants
generally need their documents to change ID into scope for the notation duty,
and models a separate documentation duty as a prerequisite of the new-ID exemption.

The review in `assessment.json` considers 3 of 11 links supported, 6 misleading,
and 2 uncertain. Every judgment identifies its raw statement and qualification
index with a rationale. This is a small source-based review, not a population
accuracy estimate or a gold annotation set.

Both documents retain useful prose, including the certificate timing caution and
the generally-needed-documentation explanation, but some of that prose is given
the wrong relationship type. The model also merges distinct actions and modal
forces into single baselines. Valid evidence references do not establish correct
interpretation or make those merged records suitable for executable workflows.

**Confounding changes:** This trial shortened the prompt and changed evidence
field descriptions as well as output shape. Some original guidance about context
versus scope and separate actions was lost. These results do not show that nesting
itself causes the semantic regressions. They show that the tested combination
is not safe to promote.

## Conversion correction and verification

The initial experimental adapter mistakenly treated non-verbatim `logic_text` as
a fatal error. The normal parser permits it and Core records a review issue.
That mismatch initially refused the name-document rule, despite correct passage
references for its alternatives. The adapter now matches the existing hard quote
checks. No model response was modified or regenerated.

- `runs/*` preserves the original requests, raw responses and initial conversions.
- `corrected-conversion/*` contains the final rulebooks, mappings and graph checks.
- `amendment.json` records the adapter correction; both runner versions are frozen.
- `design.json` records the request budget, checks and runtime fingerprints.
- `replay.json` verifies final conversions against both original raw responses.
- `tests.txt` records seven passing tests: shared-quote parent binding, duplicate
  text positions, malformed references, missing-parent protection, exact lists,
  reversed ranges, and the existing nonfatal logic review behavior.

The initial manifest covers acquisition and initial processing. Later correction
and review artifacts are separate and retain links to that original capture.

Reproduce the final conversion without provider calls from the repository root:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/attached-qualifications-experiment/experiment.py replay
```

The next experiment should retain source references and explicit parent binding
while restoring full governing-scope and separate-action guidance. It also needs
to distinguish supporting explanations, related duties, and actual qualifications.
No such follow-up or default-extractor change is adopted here.
