# Core schema reuse: completed integration and stopping point

The extractor now uses existing Rulespec records for local concept discovery,
source attribution, typed values and explicit effectivity. The document profile
imports Core CUE definitions directly. Shared Core data, release digest code and
concept assignment construction replace application copies.

This is a completed local implementation milestone. Semantic extraction remains
fallible; the examples below demonstrate both useful output and surfaced errors.
No further quality iteration is running.

## What was checked

- `regression-tests.txt`: 301 tests and 101 subtests passed across extraction,
  review, refinement, schema generation adapters and the shared producer.
- `added-tests.txt`: 45 focused tests passed, including two later additions for
  shared Core enum equality and nested fields in refinement. Total: 303 distinct
  tests plus 101 subtests. Source evidence, invalid typed values, period boundaries,
  all four assignment roles, membership, release digests and review history are covered.
- `native-check.txt`: generated schemas match native CUE and imported Core sources.
- `wheel-check.json`: installed wheels work outside the checkout without Go or
  CUE, read Core data from the shared conformance package, validate all new record
  types and freeze runtime inputs. `check_wheel.py` reproduces the check using
  `control-document.json` and `control-candidate.json`.

## Fresh Gemini extraction

Both runs used `gemini-3.8-flash` at temperature 0.2 and completed with no parser
or compiler refusals. Raw requests, responses, source, schemas and runtime files
are retained inside each run.

| Run | Source | Accepted units | Core validation | Replay |
| --- | --- | ---: | --- | --- |
| `live-names-01` | 2,651-character passport-manual excerpt | 12 | Passed | `live-names-replay-01`, exact match, no provider calls |
| `live-invented-01` | `invented-source.txt`, an explicitly invented permit policy | 6 | Passed | `live-invented-replay-01`, exact match, no provider calls |

The passport output retains all six documentary options, the married-name
exception reference, the previous-name prohibition's exception wording, and the
inherited >1-year/DS-11/unchanged-ID conditions on the limited-validity permission.
It preserves generally/might/no-obligation distinctions and uses typed `P1Y`
values with source comparators and application-date anchors. No effective period
was inferred from the manual's update date.

The invented policy produces typed ages and relative deadlines, retains the
recommendation and fee exemption, and links five meanings to one explicit
in-force period. It keeps the document definition as a separate local concept.
A duration such as `P18Y` is one representation of age; downstream consumers
still need a deliberate interpretation rather than assuming every duration is
a filing deadline.

## Source audit and correction

Raw review identified overextended source attribution: “Department guidance” in
paragraph d was used to attribute the earlier definition, and a guidance reference
was treated as the asserting claimant. Exact quotation alone did not establish
those roles. The initial independent audit (`live-names-audit-01`) flagged both
errors. Its calls completed, while its semantic assessment failed: 17 covered
inventory units and 2 unknown because those claims were not fully correct.
The audit replays in `live-names-audit-replay-01` with no provider calls.

`live-names-refined-02` runs the existing refinement workflow in the copied
`names-review-workspace`. It obtains an audit of the exact review snapshot,
proposes corrections, checks each proposal against the source, applies review
events, and performs a final source audit. It:

1. Removes both unsupported claimant attributions.
2. Adds an explicit exception linked to the previous-name prohibition.
3. Preserves the original extraction and records three correction events.

The run remains **partial** because one proposal was refused during validation
and another was not applied after its source challenge. It does not hide those
outcomes. The final audit completed and passed its assessed 18 inventory units,
with no reported errors. This is evidence of successful correction on this
excerpt, not a proof of complete or universally accurate extraction. The audit
inventories themselves vary between runs.

`live-names-refined-replay-02` verifies all three applied actions without provider
calls. The refinement used 8 requests, with 114,784 prompt, 19,433 response and
57,564 thought tokens (191,781 total). Stopping here avoids another open-ended
round of prompt tuning.

The earlier `live-names-refined-01.log` records an expected stale-audit refusal:
an audit of the raw rulebook cannot be reused as an audit of the augmented review
snapshot. It made no provider call. Use `export` to obtain that snapshot before
an external audit, or let `refine` obtain its own initial audit.

## Remaining work when development resumes

- Improve concept reuse and granularity. Current labels often describe an entire
  rule; identical labels with different definitions deliberately remain distinct.
  Cross-document identity needs supported RefSpec resolution, not label matching.
- Improve source-attribution precision and measure it over a larger source set.
- Keep complete conditions and exception targets under adversarial evaluation.
  Typed lexical validity does not establish correct interpretation or normalization.
- Decide how consumers interpret typed value descriptors and date-only effectivity.
  No forms, workflow generation, RefSpec registration or authority chain was added.

See the [active schema checklist](../../../thoughts/reviews/2026-09-07-document-understanding-schema-usage.md)
and [implementation record](../../../thoughts/plans/2026-09-08-finish-schema-reuse.md).
