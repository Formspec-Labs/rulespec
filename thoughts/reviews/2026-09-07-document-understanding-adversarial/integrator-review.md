# Integrator verification and additional finding

The integrator had prior project context and is **not blind**. These checks are
separate from the three independent agents' reports. They use the copied code
packet and synthetic inputs, with no provider calls or production edits.

## I1 — A valid child-section assignment is replaced by its parent

**Severity: P2. Confidence: high; reproduced.**

At [`core.py:95`](../../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L95),
`_claim` finds the first section containing the quote's start. It checks that an
explicit candidate `section_id` also contains that start, but then overwrites
the supplied ID with the first section's ID.

The probe supplies overlapping parent and child sections for:

```text
Header.
Visitors must wear badges.
```

The candidate explicitly names `specific-paragraph`, covering `[8, 34)`. The
parent `whole-document` covers `[0, 34)` and appears first. Both sections pass
document validation. The accepted claim nevertheless names `whole-document`,
has no issues, and passes Core graph validation. Reversing only the section
array changes the result back to `specific-paragraph`.

This loses the caller's precise source-section assignment. It matters when
Rulespec records both a document's section hierarchy and the particular
paragraph associated with a rule.

**Counterargument and limit:** inferring the first containing section can be a
reasonable fallback when the candidate supplies none. Here the candidate
supplies a valid explicit ID, and document validation accepts overlapping
sections. No rule requiring flat, nonoverlapping sections is enforced. This is
a synthetic nested-section failure; the reviewed flat excerpt corpus does not
demonstrate this error in its recorded outputs. Exact quote coordinates remain
correct, so the finding does not claim source text or quotation corruption.

The regression should preserve a valid explicit assignment regardless of
section-array order, and separately define the fallback for an omitted ID.
Either support nested sections deliberately or reject unsupported overlap
explicitly; do not silently replace a valid selection.

Evidence: [executable probe](integrator_probes.py),
[observed results](integrator-probes.json).

## Confirmation of the workflow review

The integrator reran the workflow reviewer's numeric-overflow and total-omission
inputs against the sealed code copy. Both results reproduced. The overflow run
remained `running`, lacked its manifest, and failed the ordinary review,
replay, and reprocessing entry points. The omission report correctly failed
extraction quality but incorrectly marked the fully judged review incomplete.

This reuses the reviewer's inputs and confirms reproducibility; it is not a
second independent discovery. The original blind probe artifacts were not
overwritten. Evidence: [confirmation script](integrator-confirm-workflows.py),
[confirmation results](integrator-workflows-confirmed.json), and the full
[workflow review](workflows-review.md).
