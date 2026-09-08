# Native CUE extraction schemas

The extraction application now loads candidate and model schemas generated from
[one CUE profile](../../../packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data/document-understanding.cue).
Shared field types, classifications, descriptions, titles, and model field order
live there. The independently authored Python schemas were removed. Refinement
continues to reuse the same model meaning fields.

Native CUE generates the validation rules. A small build adapter resolves local
model-schema references and preserves presentation metadata. Generated JSON and
a source/output manifest ship with the package; extraction and replay require
neither Go nor CUE. The existing Core compiler and its source files are unchanged.

## Verified behavior

| Check | Result |
|---|---|
| Model schema against the evaluated rich schema | Exact match, including descriptions, titles, property order, required order, and JSON serialization order |
| Old candidate schema, generated JSON Schema, and CUE | Agree on all 181 explicit controls across candidates and model responses |
| Application suite | 227 tests passed |
| Adapter guards, generated-schema tests, and saved experiment adapters | 34 tests passed; this overlaps the application suite and is not an additional 34 unique tests |
| Saved model responses | All 24 normalize to the same complete rulebooks, mappings, and Core graphs |
| Historical captures | All 9,476 protected files retain their hashes |
| Core source | All 62 CUE sources retain their hashes |
| Fresh installed wheels outside the checkout, with no Go/CUE on PATH | Candidate compilation, Core validation, and freezing all five schema inputs pass |
| Regeneration check | Generated files match the pinned native build |

The controls include mandatory fields, unknown fields, invalid classifications,
wrong types, empty evidence, duplicate evidence, permitted repeated target
quotes, Unicode text, and nullable/nonnegative offsets. They check structural
equivalence. This migration makes no new model call and claims no extraction
quality improvement.

The prompt and invented examples are unchanged. Strict historical replay still
detects changed implementation/schema inputs. Explicit reprocessing remains
the way to apply current code to saved responses while preserving the originals.

## CUE settings that mattered

- The native build uses CUE v0.17.1 and a module declaring language v0.17.0.
  It loads the package directory so that declaration actually governs parsing.
  The loose-file loading path does not attach module configuration in this
  CUE release. The manifest records the actual loaded language version and
  actual Go dependency version.
- `@experiment(explicitopen)` makes object closure explicit for export.
- Mandatory output fields use `!`, including list fields. Ordinary CUE fields
  can be inferred and may not become required JSON properties.
- Shared named field definitions feed both records. The candidate adds stricter
  evidence constraints without independently defining field meaning.
- The build preserves CUE's native validation output. It does not enable the
  Go API's globally permissive `ExplicitOpen` setting or call `Value.Eval()`
  before generation.

Earlier exploratory outputs remain in this directory, including the initial
loose-file trial. `package-loading-verification.json` is the final source and
runtime comparison using the proper module loading path.

## Reproduce

From the repository root:

```sh
python tools/build_extraction_schemas.py --check
.tools/document-poc-venv/bin/python -m pytest packages/rulespec-extrapolator/tests -q
.tools/document-poc-venv/bin/python -m pytest tools/test_extraction_schemas.py examples/document_understanding/schema-order-experiment/test_experiment.py -q
.tools/document-poc-venv/bin/python examples/document_understanding/native-extraction-schema/verify.py --cue .tools/cue-native-v0.17.1/cue --output /tmp/rulespec-native-profile-recheck.json --runtime
```

The verification script requires a new output filename. It never overwrites
saved responses or judgments. The full generation command and adapter limits
are documented in [the build tool README](../../../tools/cue_schema_export/README.md).
A dedicated CI workflow checks generation drift and the profile/adapter tests.
That workflow has been added locally; no remote CI run is claimed.

`before/` and `baseline.json` preserve the previous schemas and source hashes.
`application-tests.txt`, `affected-tests.txt`, `package-loading-verification.json`,
`wheel-install-log.json`, and `wheel-verification.json` record verification.
The wheel check creates a fresh environment outside the repository, installs
both built wheels, then runs `wheel_check.py` with an empty compiler search
path. `delivery.json` records the final local delivery boundary and file hashes.
