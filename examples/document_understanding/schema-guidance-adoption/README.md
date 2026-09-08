# Rich schema guidance adopted

The default extractor now uses the exact richer schema titles and descriptions
evaluated in [trial-01](../schema-order-experiment/README.md). The recovery and
relationship passes inherit the same unit descriptions through their existing
shared schema. Output fields, field order, prompts, examples, parsing, and Core
records retain their previous behavior.

The guidance covers complete inherited conditions, nested alternatives,
recommendations and descriptive possibilities, qualification targets, and
evidence supporting the actual actor or object. Concept IDs and the experimental
reference format remain deferred: they did not improve on descriptions alone.

The earlier experiment passed 9/16 selected cases in each repeat with richer
descriptions, versus 5/16 with the previous descriptions. This adoption verifies
the exact tested schema and compatibility; it does not claim a new quality score
or resolve the remaining semantic failures.

## Schema ownership and the CUE follow-up

Generated Core schemas already validate the stored graph. For example,
[`EvidenceBinding`](../../../constraints/core/evidence-binding.cue) links an
assertion to an identified source fragment, while the model returns quotations
from which Rulespec constructs those records. The Core schemas do not define the
document-understanding profile's `modality`, `scope_text`, or `alternative_quotes`.

There was avoidable repetition between the Python candidate schema and provider
schema. `provider_schema()` now reads field types and closed classifications from
[`CANDIDATE_SCHEMA`](../../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py).
It adds the model-specific field selection, required fields, empty-value behavior,
descriptions, and output order. The resulting provider JSON is identical to the
tested rich variant.

The candidate profile itself remains Python-authored. The fuller cleanup is a
CUE-owned document-understanding profile, a generated validation schema, and a
thin Gemini adapter. The existing CUE projector does not export field descriptions,
so that migration must preserve the richer guidance as well as the constraints.
It is not implemented by this adoption.

## Verification

- The full application and experiment adapter suite passed: **213 tests**.
- After consolidating type/enum lookup, the affected extraction and refinement
  suites passed again: **93 tests**.
- The active provider schema exactly matches the saved rich variant, including
  serialization order. Removing titles/descriptions yields the old structure.
- All **24** saved responses reproduce identical normalized records, mappings,
  and Core graphs under the current code. Graph validation passes for each.
- All **9,476** protected files retain their original hashes, including the prior
  extraction, review, and experiment artifacts.
- One live Gemini 3.8 Flash request accepted the richer refinement schema. This
  empty-source probe checks provider acceptance, not recovery quality. The first
  local probe setup used the extraction-only adapter and failed before any model
  call; its failure is retained. The successful probe uses the existing
  `refinement._call` path.

Evidence: [offline verification](verification.json),
[provider acceptance](refinement-probe-02/verification.json), and
[test/check record](delivery.json). Only `provider_schema()` changed in the runtime.

Repeat the compatibility check without provider calls, choosing a new output:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/schema-guidance-adoption/verify.py --output /tmp/rulespec-schema-adoption-check.json
```

Strict replay of a historical extraction or refinement run still reports the
deliberate runtime change. Keep its frozen runtime for exact historical replay,
or use `rulespec-understand reprocess` for an extraction run to create a separate
processing result under current code. Reprocessing preserves original model
responses; only a new extraction receives the richer guidance.
