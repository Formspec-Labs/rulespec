# Same-passage scope instruction experiment

**Result: inconclusive.** Both the current and revised schema descriptions preserve
the governing condition in every required duty on these short cases. Neither
invents a prerequisite in the unconditional control. The extra instruction shows
no measured benefit here, and the earlier teacher-rule failure was not reproduced.
Production code, prompts, schemas and defaults remain unchanged.

## Exact test

The invented policy requires an employer to document how employee service hours
were calculated and keep the calculation for three years. In two variants these
duties apply when accurate records of working hours are unavailable:

- Same paragraph: the condition and both duties share one passage ID.
- Separate parent: the identical condition is a preceding passage.
- Unconditional: the same duties appear without that governing condition.

Each case received control and treatment requests twice: 12 calls total. Calls
used Gemini `gemini-3.8-flash`, medium thinking, temperature zero, no numeric
thinking budget and no application output cap. There were no retries, repairs,
new extractions, comparison audits or full-document calls.

Only the meaning-field description in a copy of the existing CUE-generated
inventory schema changed. The treatment appends:

> Include every governing condition in meaning, even when it appears inside the selected main passage. Empty scope_refs means no additional evidence passage is needed—not that the rule is unconditional.

Whole-request comparisons confirm this is the only difference within each pair.
Prompt, field order, enum order, validation constraints, source catalog and
settings are identical. The experiment uses the preserved passage-ID prototype
within its Python process; it does not edit the installed production package.

## Results

| Case | Control success | Revised-description success |
|---|---:|---:|
| Same-paragraph condition | 2/2 | 2/2 |
| Separate-parent condition | 2/2 | 2/2 |
| Unconditional duties | 2/2 | 2/2 |

Success here means both duty meanings, the three-year retention duration and
applicable governing condition survive, with no invented condition. Every
conditional duty repeats the unavailable-record condition in its own meaning;
we did not credit a separate condition record or raw evidence as a substitute.

For example, both versions produce meanings equivalent to: “When accurate records
of working hours are unavailable, the employer must keep the calculation documenting
how it calculated the employee's hours of service for three years.” Both remove
that condition in the unconditional case, as the source requires.

Some calls add a separate condition or retention-threshold record. One treatment
classifies the parent introduction as background while preserving its condition
in both duties. These are representation/classification differences, not missing
duties under this test's predeclared criteria. Independent condition classification
consistency was not established.

All 12 responses ended STOP, all inventory evidence resolved, and all 12 captures
replay identically without provider calls. Reported tokens totaled **21,393**:
9,159 control and 12,234 treatment. One treatment repeat spent substantially more
thinking tokens; this small sample does not establish a causal cost effect. The
provider reported equal input-token counts within each pair despite the changed
schema description; that observation alone cannot establish whether the description
was ignored or omitted from the reported token accounting.

## What this tells us

Selecting an entire paragraph can coexist with faithful scope propagation. The
simple claim that an empty scope_refs list necessarily causes condition loss is
not supported by these outputs. The wording hypothesis remains unproven rather
than disproved for the earlier, more complex teacher paragraph.

These examples explicitly say “the following requirements apply.” That makes the
condition-to-duty relationship clearer than the original teacher paragraph, which
mixes a general burden, an example and cross-references. The test removed that
complexity, so it cannot establish why the earlier failure occurred. No production
change is justified by this result alone.

The next informative comparison would use the exact original failing teacher
paragraph and context, keeping this same one-description intervention and repeated
controls. That follow-up is suggested, not executed.

## Saved evidence and replay

`criteria.json` and `design.json` pin the hypothesis, required meanings, unsupported
additions, source fixtures and exact schemas before calls. The design also pins
the prior prototype manifest and runtime. `runs/` preserves requests, responses,
normalized inventories and manifests. `source-review.json` contains all raw unit
meanings and revisable per-call assessments; `verification.json` and `decision.json`
record the checks and inconclusive decision. These are agent assessments, not
independent gold labels or a general accuracy estimate.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/same-passage-scope-experiment/experiment.py replay
```

The runner verifies pinned artifacts and dependencies, loads the preserved
prototype in its process and replays without credentials or provider calls.
No production tests were rerun because no production implementation changed.
The experiment and findings remain local and uncommitted.
