# Qualified USC comparison: extend the existing RefSpec reader

Neither tested API passes the complete integration gate unchanged. The comparison
ran all 29 frozen inputs with identical replay and no reader exceptions. Raw
source review identifies missing qualifications, missing occurrence positions,
collapsed repetitions, and a field-reader policy that can mistake prose counts
for listed sections. These are selected diagnostics, not an accuracy benchmark.

Use RefSpec's existing matcher to retain qualified readings and original positions
together, then connect the passing result to Rulespec's existing reference adapter.
SpicySearch's permissive query defaults stay unchanged. No production parser or
installed package changed during this comparison.

- [Manual review of every case](review.md), with the decision and owning-code trace.
- [Frozen input strings and expectations](cases.json).
- [Native output](attempt-02/raw.json), [exact replay](attempt-02/replay.json),
  [runtime/source identities](attempt-02/run.json), and
  [mechanical checks](attempt-02/mechanical-checks.json).
- [Preregistered design and execution-scope clarification](design.md).

The three first-matching publisher paragraphs were read with their surrounding
source before labeling:

| Source | Written target that needs preserving |
| --- | --- |
| 5 CFR 6.8(d) | Both `5 U.S.C. 3105` and `5 U.S.C. 5372(b)`; appointment dates are not additional sections |
| 5 CFR 302.303(b)(3) | `5 U.S.C. chapter 81, subchapter I`, without broadening it to the whole chapter |
| 5 CFR 315.608 | `50 U.S.C. 403j` and the note under `50 U.S.C. 402`; neighboring employment categories are separate context |

[Selected sources](selected-sources.json) pin the original file, source byte
bounds, saved surrounding XML and exact paragraph text. The other 26 cases are
constructed development diagnostics, including eight unchanged earlier cases.

The first attempt incorrectly inherited SpicySearch's repository-specific load
gate and stopped before calling either parser. Its [refusal](not-run.json),
[original design](design-before-execution-scope-clarification.md) and
[original runner](run-before-execution-scope-clarification.py) remain unchanged.
The documented correction used an exclusive Rulespec output directory and recorded
host load without making a performance claim. Input, label and loaded-reader
hashes match the first attempt. This is a new completed attempt, not a passed
original one.

The recognition comparison is complete. R6's [native upstream implementation](native-review.md)
passes 468 tests, with 14 slow tests deselected. Application
connection and wheel verification remain open on the
[task list](../../plans/2026-09-10-reference-integration-task-list.md).
