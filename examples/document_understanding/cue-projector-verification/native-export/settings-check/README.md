# CUE settings recheck

This follow-up checks whether the earlier native-export failures are resolved
by supported configuration or source migration. Original captures under
`comparison/` and `probes/` remain the baseline. Production constraints,
compiler, generated outputs, and the v0.10.0 tool pin remain unchanged.

Questions under test:

1. Does `cue fix --exp=explicitopen` preserve source behavior and fix composed
   schemas? Also test the official `aliasv2` migration, rather than simply
   adding an experiment attribute.
2. Can CUE's `matchIf` validator express and export the conditional requirement
   that the earlier comprehension-based example lost? Check presence, branch
   selection, field types, and additional properties independently.
3. Do CLI strictness/rendering flags, module language versions, Go API
   `ExplicitOpen`, or evaluation before generation change these results?
4. Does an export-compatible spelling work on a real Rulespec schema with
   relevant saved fixtures? Separate source equivalence from compatibility
   with Rulespec's JSON-LD conventions.

The v0.17.1 upstream source exposes `GenerateConfig.ExplicitOpen` and reference
naming options for JSON Schema generation. It explicitly handles `matchIf`.
CLI `jsonschema+strict` settings appear in the import configuration; their
effect on export must be checked rather than assumed. `cue fix --exp` is the
official way to migrate source syntax for per-file experiments.

The recheck is complete. The official explicit-open source migration fixes
the small composition example, including its closed-object boundary. An
imported `matchIf` schema matches all eight conditional controls. These were
missing from the earlier assessment.

The full copied-source migration preserves CUE verdicts on all 296 adapted
fixture cases but does not fix the complete build: 43 of 45 shapes export,
with stack overflows for `ConceptScheme` and `ConfidenceRecord`. Raw consumer
compatibility and inherited constraints still differ. The real assertion
rewrite also changes closure in one control, so it is not an accepted fix.

The revised recommendation is to test native generation for the extraction
application schema first, while preserving the production Core compiler until
each migrated group passes its existing checks. See the parent assessment for
the evidence and limits.

## Reproduction

From `examples/document_understanding/cue-projector-verification/native-source`:

```sh
go build -o ../../../../.tools/cue-native-v0.17.1/settings-probe ./settings_probe
```

From the repository root:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/cue-projector-verification/check_native_settings.py --cue .tools/cue-native-v0.17.1/cue --settings-probe .tools/cue-native-v0.17.1/settings-probe
.tools/document-poc-venv/bin/python examples/document_understanding/cue-projector-verification/compare_native.py --cue .tools/cue-native-v0.17.1/cue --source-root examples/document_understanding/cue-projector-verification/native-export/settings-check/migrated-constraints --out examples/document_understanding/cue-projector-verification/native-export/settings-check/migrated-comparison
.tools/document-poc-venv/bin/python examples/document_understanding/cue-projector-verification/check_native_relationship.py --cue .tools/cue-native-v0.17.1/cue
```

The first script recreates its small copies and imports the saved conditional
JSON Schema. `full-migration.json` records the command that migrated the copied
repository constraints. The second command intentionally targets that saved
copy and a separate output directory. It must not use the earlier comparison
directory for migrated results. The third script recreates the assertion
experiment from original and migrated copies.

## Captures

- `report.json`: 56 CLI settings checks, Go API options, OpenAPI options,
  source migrations, module language versions, and plain-JSON controls.
- `conditional-strict-input.json` and `imported-strict-conditional.cue`:
  conditional schema and CUE's own imported spelling, including the false
  branch and unknown-field restriction.
- `full-migration.json`, `migrated-constraints/`, and
  `migrated-comparison/report.json`: the official migration and full replay.
- `migration-source-behavior.json`: unchanged CUE decisions across the full
  replay, represented by an empty differences list.
- `relationship/report.json`: 11 saved fixtures and 10 focused controls for
  the actual assertion sources. The eligibility control uses
  `rkaf:localOperationalUse`, a valid general eligibility value that the AI
  branch must forbid. `initial-report.json` preserves the earlier run whose
  corresponding control instead used a value outside the general enum.
- `relationship/external-matchIf/` and
  `relationship/external-matchIf-export.json`: a further source arrangement
  that fails to compile. This is an unsuccessful exploratory capture.
- `verification.json`: final production/source preservation checks.

The Go API preflight experiment explicitly checks `Value.Err()`. Its rejection
of an unresolved comprehension is distinct from the default generator's
successful empty output. None of the diagnostic scripts treats successful
export as proof of complete constraint preservation.
