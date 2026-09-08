# CUE compiler comparison

These are diagnostic outputs and replay tools. They do not replace generated
Rulespec artifacts. The findings and implementation sequence are in
[the assessment](../../../thoughts/reviews/2026-09-07-native-cue-assessment.md).

`before/` holds schemas generated with `compiler-before.py` before the
unfinished annotation patch. `baseline.json` records source hashes.
`unfinished-annotation-parser.patch` and `compiler-with-unfinished-annotations.py`
preserve that patch; `parser-patch-checkpoint.json` records its restoration.

The separately installed binary is `.tools/cue-native-v0.17.1/cue`.
`native-export/current-install.json` records its release URL and checksums.
The repository's normal `.tools/cue` and version pin remain v0.10.0.

From the repository root, reproduce the fixture comparison:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/cue-projector-verification/compare_native.py --cue .tools/cue-native-v0.17.1/cue
```

Build the native source/API probe:

```sh
cd examples/document_understanding/cue-projector-verification/native-source
go build -o ../../../../.tools/cue-native-v0.17.1/source-probe .
```

Then, from the repository root:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/cue-projector-verification/verify_native_probes.py --cue .tools/cue-native-v0.17.1/cue --source-probe .tools/cue-native-v0.17.1/source-probe
.tools/cue-native-v0.17.1/source-probe constraints/core/assertion.cue
.tools/cue-native-v0.17.1/source-probe -schema '#Conditional' -explicit-open examples/document_understanding/cue-projector-verification/native-export/probes/ordinary.cue
```

The parser probe reads source syntax and annotations using CUE's Go packages.
It does not evaluate inheritance or certify that extracted rule meaning is
complete. The `-schema` mode uses the native generation API and correctly
serializes its result as JSON; it does not serialize Go AST structs directly.

Fixture comparison records raw JSON-LD compatibility separately from a second
check using identical adapted data with CUE and native JSON Schema. That second
check removes JSON-LD identifiers and expands admitted scalar list shorthand;
it preserves other differences for inspection. Never interpret a successful
export, a matching fixture, or a syntax count as a completeness claim.

The follow-up [settings recheck](native-export/settings-check/README.md) tests
official source migrations, conditional validators, module versions, CLI
options, and Go API options. It preserves the earlier captures and records
both small successes and remaining failures in the full fixture replay.
