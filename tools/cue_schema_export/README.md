# Native CUE schema export

This build tool calls `cuelang.org/go/encoding/jsonschema.Generate` to generate
validation rules. CUE parses and evaluates the source. The tool separately
reads field order and metadata through CUE's APIs; it contains no CUE expression
parser or validation-rule translator.

The extraction profile uses CUE v0.17.1 and explicitly declares language
v0.17.0 with the `explicitopen` experiment. `go.mod`, `go.sum`, and the profile's
`cue.mod/module.cue` pin those inputs. This leaves the existing Core compiler's
CUE pin unchanged. The application imports existing Core definitions through
`rulespec.invalid/core:rkaf`. The Python build stages `constraints/core` unchanged
inside a temporary CUE module's `cue.mod/pkg` directory; there is no checked-in
copy or generated enum inventory. The manifest fingerprints every Core source,
and `--check` detects upstream changes requiring regeneration.

The exporter loads the CUE package directory, rather than individual files.
Upstream's loose-file loader does not attach the module configuration. Package
loading lets the declared language version govern compilation; the manifest
records that version and the actual CUE dependency from Go build information.

From the repository root, with Go 1.25 or newer and Python 3.12 available:

```sh
python tools/build_extraction_schemas.py
python tools/build_extraction_schemas.py --check
```

Edit
`packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data/document-understanding.cue`.
Generated `candidate.schema.json`, `provider.schema.json`, and `manifest.json`
live beside it and ship with the application. The application needs neither Go
nor CUE at runtime. Its loader verifies source/output hashes, and extraction
runs freeze the schema files and build manifest with their other inputs.

The Python build adapter resolves local model-schema references, restores field
order and `@title` metadata, and sorts enum presentation only when CUE declares
`@sortEnum()`. It makes string-only enums' implied type explicit and keeps the
existing request's serialization order. These changes preserve validation.
Recursive references, unsupported reference siblings, and disagreement between
native fields and metadata raise errors. Candidate validation keeps native
references and constraints; only its top-level field order is restored.

Use explicit `!` required markers where the output must contain a field.
An ordinary CUE field can be inferred, including an empty list; it does not
always translate to a required JSON property. Shared named field definitions
let candidates narrow model fields without referring to a required field that
does not exist as a regular CUE value.

This is a bounded application-schema path. The saved Core assessment still
contains native-export losses and crashes. Successful generation is not proof
that arbitrary CUE expressions can be represented without loss, nor that an
extracted document meaning is correct or complete.

References: [CUE JSON Schema guidance](https://cuelang.org/docs/concept/how-cue-works-with-json-schema/)
and [CUE Go API](https://pkg.go.dev/cuelang.org/go@v0.17.1/cue).
