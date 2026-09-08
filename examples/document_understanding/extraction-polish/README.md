# Temperature-zero extraction polish

The retained change clarifies CUE field guidance without changing fields, constraints,
Core mappings, or the one-request-per-window extraction process. Temperature already
defaulted to 0; all twelve new requests explicitly use 0. The README now makes this
default clear. These trials do not demonstrate a net accuracy improvement.

The guidance asks for source-supported actors and attribution, exact typed-value
descriptors and exception targets, faithful modality evidence, and substantive
descriptive cautions. It adds no processing layer or provider calls. Generated
schemas come from CUE. Existing concept guidance and few-shot examples are retained.

## Experiment and decisions

Two short source excerpts were used: the unchanged 2,651-character name-change
section and a contiguous photo-section prefix. `selection.json` records the photo
selection; each run freezes its source, request, response, schemas, and runtime.
`checks.json` was written before the requests. Each run made one Gemini 3.8 Flash
request, without audit or refinement. `assessment.json` records usage, timing,
candidate counts, validation, and qualitative source-review findings.

| Captures | Change tested | Decision |
| --- | --- | --- |
| `baseline-*` | Unchanged schema and examples at temperature 0 | Comparison baseline |
| `polished-*` | Initial guidance, including narrower concept-tag instructions | Reject tag restriction: one photo run produced no tags |
| `final-*` | Restore concept guidance; clarify literal actors and typed descriptors | Retained source configuration; two repeats per excerpt |
| `selected-*` | Additionally retain the full exception clause in the badge example | Reject example change: no link gain; names run invented 12 issuer attributions |

Directory names identify experiment stages, not quality rankings. The `selected-*`
stage was rejected. Its poor result does not prove the example edit caused the
regression; it gives no evidence for keeping that edit. Original captures remain
intact, including rejected experiments.

## What the output supports

Both retained photo runs preserved the six selected checks: infant accommodations,
parent-face prohibition, recommendation strength, appearance acceptance condition,
the certificate-date caution, and absence of invented attribution. One run still
had unresolved evidence for an alternative component.

Both retained names runs preserved the six documentary alternatives and the tested
inherited conditions. Neither produced a separate previous-name exception link,
although the baseline retained the exception's meaning. One run retained the
generally-needed-documentation statement only as context of the notation duty,
making it less independently discoverable. Both retained runs left claimants empty.

The rejected final example trial supplied “Department of State” as issuer for all
12 name-change candidates, supported only by an ambiguous section-label quote.
Evidence checks withheld eleven Core claimant records. One unsupported claimant
reached the graph using the section-reference prefix at offsets 712:725, which
resolved inside that claim's quotation. All twelve application candidates contain
the incorrect attribution. The blind review caught this correction to the initial
assessment. Structural acceptance does not establish semantic correctness.

The narrower concept trial produced correct explicit exception links in both names
runs, while reducing topic coverage. That mixed outcome is why it was not adopted.
Temperature 0 still produced different outputs across repeated requests. This small
sample cannot separate temperature effects, prompt effects, and sampling variation,
or establish a general accuracy rate.

## Verification and stopping point

Native CUE generation checks pass, and `schema-comparison.json` records unchanged
constraints and field order. `retained-tests.txt` records the tests against the final
retained source. `replay-names/replay.json` and `replay-photos/replay.json` verify
identical parsing and candidate compilation from the retained first-repeat captures,
with zero provider calls. Earlier test logs belong to their experiment stages.

Stop here for this polish. The next useful quality target is consistent extraction
of separately referenceable exceptions and descriptive statements, measured on
saved cases. More wording alone has not reliably solved it. Preserve the cheap path
and treat semantic completeness as a separate assessment.
