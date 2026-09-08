# Native CUE assessment

**Follow-through:** the extraction application profile has now moved to native
CUE generation. Its model schema matches the evaluated rich schema exactly;
181 controls and saved-output replay pass. See
[the implementation and checks](../../examples/document_understanding/native-extraction-schema/README.md).
The remaining discussion of full Core migration still applies.

The settings recheck changes the recommendation: evaluate native CUE generation
for the extraction application schema before building another general source
reader. We missed a supported source migration and an exportable conditional
validator. Native CUE can handle the small cases correctly when authored and
migrated appropriately. That does not yet make it a compatible replacement for
the existing Core build.

Keep the production compiler stable while testing native generation with
Rulespec's conventions made explicit. Decide which custom output logic remains
from demonstrated gaps, rather than assuming every target needs our own CUE
interpreter. CUE's official parser remains the appropriate tool for any source
metadata or structure that an adapter needs.

The legacy Core parser replacement and its annotation fix are not implemented. The
unfinished annotation-parser patch was saved and removed from the active
compiler. All migrations below use separate copies; production definitions,
generated outputs, model captures, and review records remain unchanged.

## Settings recheck: what we missed

The original explicit-open test only added an experiment attribute. The correct
command is `cue fix --exp=explicitopen`, which also rewrites embedded definitions
such as `#Concept` to `#Concept...`. On the composition probe, this preserves
the CUE decisions and fixes native export: all four controls pass, including
rejection of an unknown field. The experiment needs language version v0.15.0
or later. A module pinned to v0.10.0 rejects the migration; v0.17.0 permits it.
The real repository has no `cue.mod/module.cue` and still pins the binary to
v0.10.0. Merely setting a newer module language version did not fix the probes.

We also missed `matchIf`, CUE's supported conditional validator. Importing a
small JSON Schema with `if`/`then`/`else` produces this form through CUE's own
importer. Exporting that CUE back to JSON Schema agrees with CUE on all eight
conditional controls: correct human/AI records, missing fields, invalid values,
lineage outside the AI branch, and unknown fields. This establishes support
for conditional validation; the earlier comprehension syntax is the failing
form. Removing its alias or migrating to `aliasv2` did not fix that form.

Several similarly named options are not substitutes:

| Option | Observed result in v0.17.1 |
|---|---|
| `cue fix --exp=explicitopen` | Fixes the simple composition case while preserving closure. |
| Go `GenerateConfig.ExplicitOpen: true` | Allows unknown fields that CUE rejects; unsuitable as a blanket fix. |
| CLI `jsonschema+strict`, `strictFeatures`, `strictKeywords`, `openOnlyWhenExplicit` | No change to the tested generated schemas. The CLI constructs the generator with default options; these settings configure import. |
| `-A`, `-s`, `--inline-imports` | No change to the tested JSON Schema outputs. |
| Go `Value.Eval()` before generation | Fixes simple composition but removes the working `matchIf` branch requirements in the tested imported schema. |
| Go `Value.Err()` preflight | Rejects the unresolved comprehension instead of emitting an empty schema. Useful protection for this case; not a completeness check. |
| OpenAPI `ExpandReferences` / `StrictFeatures`, including a 3.1 version request | Does not preserve the tested conditional rules. Some calls succeed with those rules missing. |

The CLI matrix contains 56 exports across eight flag settings and seven
source/shape combinations. The strictness and rendering options produced the
same schemas as their defaults. Native generation still supports doc comments
as descriptions; these settings do not add support for arbitrary `@title` and
`@description` attributes or preserve the tested source property order.

The subsequent application migration found an additional loading distinction:
the v0.17.1 Go loose-file loader does not attach `ModuleFile`, so its parsing does
not apply the module language version. The earlier `cue fix` tests did check
module version eligibility, but the export commands that named loose files were
not proof of module-version-aware export. The application build now loads the
package directory and records the actual module language version. Its full
profile checks pass through that path. The larger Core assessment should use
the same distinction when a coherent Core module migration is attempted.

## Wider replay after the proper migration

All 62 constraint files were copied. The official migration ran on the 58
files used by the existing comparison, leaving the four platform/semantics
files outside that test scope. CUE's validation decisions were unchanged on
all 296 adapted fixture cases. Native JSON Schema export still did not match
the current build:

- 43 of 45 fixture shapes exported; `ConceptScheme` and `ConfidenceRecord`
  hit stack overflows in the upstream exporter. The error traces are saved.
- 170 raw-fixture results differed from expectations or lacked an exported
  schema, including 168 of the 288 regular cases. This includes deliberate
  JSON-LD conventions, remaining lost constraints, and nine cases affected by
  the export crashes; it is not a count of independent exporter defects.
- On identical adapted data, native export accepted 128 cases CUE rejected
  and rejected one CUE accepted; nine cases lacked a schema. The automatic
  migration preserves source behavior but does not fix generation as a whole.

A separate `matchIf` rewrite attempt used the actual
`RelationshipAssertion` definitions and dependencies: 11 saved fixtures plus
10 focused controls. It recovers the local lineage/provenance conditionals,
but native export still loses inherited requirements. Five of 21 exported
verdicts differ from the source expectations. The rewrite itself also widens
closure in one control, so it is not an acceptable source migration. Moving
the validators outside explicitly closed structs in a further attempt fails
to compile; that attempt is saved rather than presented as a fix.

These results justify keeping the current Core build during a staged change.
They do not justify maintaining our own generator for a new application schema
without testing the native route first. The remaining question is how much of
Core can use exportable CUE forms while preserving composition and Rulespec's
consumer conventions; this recheck does not settle that for every definition.

## Earlier baseline: what was tested

The repository still pins CUE v0.10.0. A separate v0.17.1 binary was downloaded
from the official release and checked against its published SHA-256 digest.
The experiment also uses the upstream Go API pinned to v0.17.1.

| Check | Result | Meaning |
|---|---|---|
| Export the 45 shapes used by the fixture suite with native `cue def --out jsonschema -e '#Name'` | All commands succeed | Export success alone does not establish fidelity. |
| Compare the 288 regular fixture cases with expected outcomes | Existing compiler: 288 match; native export: 127 match, 161 differ | Native export is not compatible with current consumer behavior. |
| Inspect those 161 differences | Native accepts 56 expected failures and rejects 105 expected passes | Both lost restrictions and excessive restrictions need attention. |
| Include the eight adversarial fixture cases | 296 cases total; existing compiler differs on two, native export on 163 | The two existing differences are documented adversarial cases, not new failures. |
| Test seven small plain-JSON inputs against CUE itself and the native schema | Three differences | These isolate failures without JSON-LD conventions obscuring the result. |
| Read all 62 source files with the native parser | 948 field declarations, 287 with annotations, 83 `if` clauses | Upstream parsing retains the source information we need. These are syntax counts, not counts of unique rules or a proof of semantic completeness. |
| Read a rich-schema probe through the native parser | Descriptions, titles, field order, and fields inside a conditional survive | A source reader based on the upstream API is feasible. |

The 288 regular cases include Core, analysis, and profile cases; they are not
288 Core-only cases. They all match the existing compiler. The two existing
adversarial mismatches are `conditional-silent-pass-positive.jsonld` and
`nested-noevidencereason-positive.jsonld`, both rejected by the existing JSON
Schema target.

## What the differences mean

Some differences are deliberate Rulespec conventions. Resource schemas accept
JSON-LD `@id` fields and additional profile properties, and many list properties
accept one value without an array. The CUE source is often closed and requires
arrays. A native export cannot replace those conventions without an adapter.

The comparison also tests identical data against native CUE and native JSON
Schema after removing JSON-LD identifiers and expanding scalar list shorthand.
It leaves domain fields and CUE restrictions intact. Across those inputs,
110 cases differ: 72 native-schema acceptances where CUE rejects, and 38
native-schema rejections where CUE accepts. This diagnostic does not claim
that all fixture spellings have been converted to a canonical CUE authoring
format. The smaller probes below provide clearer evidence of specific losses.

The conditional probe has a required `kind` field and requires `lineage` when
`kind` is `ai`. CUE accepts a valid human record and a valid AI record, and
rejects an AI record without lineage or an empty record. Native JSON Schema
export produces only `$schema`, accepting both invalid inputs. The Go API
reproduces that result, including with `GenerateConfig.ExplicitOpen: true`.

The composition probe embeds a two-field definition and adds a third field.
CUE accepts a record containing all three. Default native export closes both
parts separately, so each rejects the other's fields. The Go API's
`ExplicitOpen` setting fixes this example. Enabling the per-file
`@experiment(explicitopen)` attribute instead changes the language's embedding
rules and rejects the original composition syntax. It is not a substitute for
testing a source migration.

Native JSON Schema export retains documentation comments but alphabetizes
properties in the tested example. It also ignores our proposed
`@title`/`@description` attributes. Those attributes are valid generic CUE
metadata, not upstream JSON Schema exporter features. The native parser gives
us their actual parsed text and preserves declaration order; a Rulespec
annotation adapter can use that information without another lexer.

## Revised implementation sequence

1. Test the extraction application schema through native CUE generation in
   isolation. Use rich documentation comments, explicit open/closed objects,
   and exportable validator forms where needed. Pin the tested binary and
   language version for this path. Check the full existing application schema,
   not just the small probes, before selecting it for production.
2. Keep a small, explicit adapter for Gemini's accepted schema features,
   metadata, and property order. Use upstream CUE parsing for source metadata
   when necessary. Do not silently relax validation to satisfy the model API.
   Once verified, generate from CUE and remove the independently authored
   Python schema rather than maintaining both.
3. Migrate existing Core shapes in bounded groups. Preserve conditional
   inheritance, closed typed literals, open JSON-LD resources, scalar/list
   shorthand, reference handling, and cross-field checks. Treat the remaining
   exporter failures and upstream crashes as explicit unresolved cases.
4. Run compiler regressions, the 288 regular fixture cases, saved adversarial
   cases, and focused source-versus-export controls for each changed group.
   Compare non-JSON targets when their inputs change. Preserve original
   captures and review history. Export success and schema validity do not
   establish semantic completeness.
5. For behavior that still needs a custom generator, replace its text parsing
   with upstream APIs and retain only justified target-specific logic. This is
   a fallback for demonstrated gaps, not a prerequisite for testing the native
   application-schema path.

## Evidence and reproduction

Evidence lives under
`examples/document_understanding/cue-projector-verification/`. Its README
contains reproduction commands. Key files are:

- `native-export/current-install.json`: binary URL, version, and checksums.
- `native-export/comparison/report.json`: per-fixture results, source and fixture
  hashes, export failures, and the data-adaptation explanation.
- `native-export/probes/verification.json`: seven independently checked cases
  and the source/export property orders.
- `native-export/probes/go-api-verification.json`: explicit-open Go API checks.
- `native-export/source-structure.jsonl`: parsed declarations and conditions
  from all 62 sources.
- `native-source/`: the bounded upstream parser/API proof of concept.
- `unfinished-annotation-parser.patch`: the suspended custom-parser change.
- `before/`: schemas produced before that patch, used as the comparison baseline.
- `native-export/settings-check/report.json`: per-setting commands, outputs,
  language experiments, and independent validation controls.
- `native-export/settings-check/migrated-comparison/report.json`: full replay
  after the official explicit-open migration on copied sources.
- `native-export/settings-check/migration-source-behavior.json`: empty list,
  confirming unchanged CUE verdicts across those 296 fixture cases.
- `native-export/settings-check/relationship/report.json`: the real-schema
  `matchIf` attempt, including its remaining source and export differences.
- `check_native_settings.py`, `check_native_relationship.py`, and
  `native-source/settings_probe/`: replayable settings and real-schema probes.

Upstream references: [CUE JSON Schema guidance](https://cuelang.org/docs/concept/how-cue-works-with-json-schema/),
[CUE v0.17.1 release](https://github.com/cue-lang/cue/releases/tag/v0.17.1),
and [`GenerateConfig` / `Generate`](https://pkg.go.dev/cuelang.org/go@v0.17.1/encoding/jsonschema#Generate).
Conditional semantics are documented in the [CUE specification](https://cuelang.org/docs/reference/spec/#matchif).
The generation API describes itself as experimental. These results concern
the tested v0.17.1 release and current Rulespec source spellings.
