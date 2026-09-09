# Passage-ID inventory experiment

**Decision: revise the experiment; do not adopt the prototype yet.** Passage IDs
resolved correctly, but one treatment meaning lost an inherited condition and
another changed a counting exemption's classification. The narrow controls also
had no evidence failures, so they did not reproduce the original full-document
problem. The predeclared gate failed; no full-document audit was run.

Production code and generated schemas were restored to the baseline. The tested
prototype, tests, generated schema, frozen runtime and raw captures remain here.
No existing captures were edited and no commit was made for this experiment.

## What was reused

| Capability | Status before experiment | Prototype change |
|---|---|---|
| `passage_catalog` and `resolve_passage` | Implemented for extraction | Connected to source inventory |
| CUE source-reference type and focus-reference restriction | Available in extraction | Shared by a new inventory request view |
| Audit source-span records, labels and comparison | Implemented | Output shape retained; evidence resolved from IDs |
| Rejection of inserted/non-source text | Implemented | Shared between quote and passage-based audit evidence |
| CUE-generated inventory request | Missing | Added a small `InventoryResponse` definition and generated view |

The prototype uses `quote_ref` for a focus passage/range and `scope_refs` for
substantive governing passages. It resolves these to the existing exact source
spans and normalizes the meaning/kind record before deriving its identity. It
preserves refused raw responses. It does not guess section labels, silently
repair quotations, or treat an evidence selection as proof of correct meaning.

The inventory classification set stays the same. Shared CUE kind values avoid
copying the overlapping extraction enum. Extraction's provider and full meaning
schemas remain byte-identical; the candidate enum has the same allowed values in
a different order. The schema generator gains an export, not new CUE compilation
semantics. Prototype audit format is version 3; production remains version 2.

## Paired results

Six medium-thinking Gemini `gemini-3.8-flash` inventory calls used temperature
zero, no numeric thinking budget, no application output cap and no retries. Each
pair received the same source focus and bounded context. Controls used the frozen
quotation-based inventory implementation. Comparison instructions were unchanged;
no extraction, comparison or repair calls were made.

| Excerpt | Control units / refusals | Passage-ID units / refusals | Control tokens | Passage-ID tokens |
|---|---|---|---:|---:|
| Employer burden and teachers | 3 / 0 | 4 / 0 | 3,378 | 3,477 |
| Eligibility timing and transition | 4 / 0 | 4 / 0 | 2,703 | 2,539 |
| Service and rehire exceptions | 6 / 0 | 6 / 0 | 4,923 | 3,499 |
| Total | 13 / 0 | 14 / 0 | **11,004** | **9,515** |

All six responses ended STOP and their inventories replay identically. Total
usage was 20,519 reported tokens. Counts include background entries and different
splitting choices; more units do not establish better coverage. One observation
per cell cannot establish stability or attribute meaning differences causally to
the new evidence format.

## Why the quality gate failed

The control teacher requirement begins “When accurate hours-worked records are
not maintained.” The treatment retains that condition in a different employer
burden statement, but its separate teacher requirement says only that the employer
must demonstrate the hours threshold to claim ineligibility. It does not carry
the governing condition into that meaning. Both cite the original paragraph;
valid evidence does not restore the missing condition in the split statement.

The treatment also labels the seven-years-or-more counting exemption `permission`
rather than `exemption`, although its meaning still says “need not.” Both service
routes, their seven-year thresholds, service credit, written agreement and USERRA
entitlement limit survive. Both timing arms preserve the conditional leave
transition, while retaining the known permission-versus-description uncertainty.

Most importantly for the experiment's original purpose, none of the quotation
controls emitted an invalid section marker on these smaller excerpts. Therefore
there is no observed improvement in refused inventory entries in the paired
results. The mechanism works, but this run does not establish its practical
benefit on the original failing input.

`source-review.json` preserves the raw and normalized units for both arms and
revisable interpretations. `gate.json` records the stop decision before any full
audit. These reviews are not independent or unquestionable gold labels.

## Verification and reproduction

The prototype passed 347 tests (package plus generator), including 61 focused
checks. New cases cover repeated exact wording with distinct offsets, duplicate
support references, unavailable or out-of-focus references, ranges crossing
unsupplied text, and inserted text. Native CUE generation passed. These establish
processing behavior, not semantic correctness.

`design.json` pins the fixtures, acquisition script, old audit code, expected
meanings and runtime before the calls. Per-run manifests bind every response and
normalized result. `prototype.patch` and `prototype-files.json` preserve the tested
implementation and tests relative to the recorded base commit. The frozen runtime
lets replay run without replacing the production package:

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/audit-grounding-experiment/replay_frozen.py
```

This changes only that Python process's package search path. The runner verifies
all recorded runtime hashes and replays the six inventories without credentials
or provider calls; shared dependency versions must still match. Use an isolated
checkout at the recorded base commit to apply `prototype.patch` for development.

## Next bounded step

Build a deterministic comparison from the original four refused inventory rows,
with explicit, source-reviewed passage selections and unchanged meaning text.
That can verify the evidence conversion against the actual failure without new
model calls or pretending automatic label repair is safe. Separately probe the
teacher condition with complete and deliberately weakened meanings. Only then
consider repeating the model experiment or combining the two changes.
