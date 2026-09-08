# Adopt the successful schema guidance

The user authorized implementing the successful takeaways from the saved
schema-order experiment. Promote the exact `rich` schema annotations into
`rulespec_extrapolator.extraction.provider_schema()`. Preserve its field order,
constraints, prompt, examples, parser, and Core representation. The existing
refinement proposal schema reuses these attributes and should receive the same
guidance through that existing connection.

The experiment supports richer descriptions: 9/16 selected cases passed in both
repeats, compared with 5/16 for the previous descriptions. The concept-ID variants
did not improve on that result. Local concept IDs, new relationship fields, and
semantic role reconciliation remain experimental.

## Verification

1. Check the installed provider schema against the exact saved `rich` schema,
   including serialization order, and prove that removing annotations leaves
   the previous structure unchanged.
2. Run the application tests and the experiment's reference-adapter tests.
3. Reprocess the saved experiment responses with current code, in memory, and
   compare their complete normalized records and Core graphs. This checks
   compatibility; it does not generate a new semantic quality score.
4. Check that refinement retains the richer field annotations and make a small
   recorded provider acceptance probe for that nested schema.
5. Preserve all previous source captures, outputs, judgments, and review history.
   Save verification separately. Strict replay of historical runs should still
   detect the deliberate provider-schema/runtime change; do not bypass it.

Stop after local implementation and verification. No UI work or new quality
matrix is needed for this adoption.

## User clarification: CUE ownership

The user flagged handwritten schemas as potential duplication. Inspection
confirmed that generated Core schemas already validate the stored graph, while
the document-understanding candidate profile is defined in Python and the
provider view repeated its types and classifications. This adoption now derives
those shared definitions from `CANDIDATE_SCHEMA` without changing the evaluated
provider output. A CUE-owned candidate profile remains the fuller cleanup.
The current CUE projector also needs support for preserving field descriptions
before it can generate the tested guidance. Do not claim that migration is done.

## Completion

Implemented locally in `provider_schema()`. The active ordered schema exactly
matches the saved rich variant; prompt, examples, output format, and normalization
remain unchanged. The full 213-test suite passed, followed by 93 affected tests
after consolidating schema definitions. All 24 saved outputs reproduce exactly,
all 9,476 protected files retain their hashes, and the actual refinement provider
path accepts the richer nested schema. Verification is saved in
`examples/document_understanding/schema-guidance-adoption/`.
