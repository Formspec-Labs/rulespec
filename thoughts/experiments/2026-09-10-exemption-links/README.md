# Exemptions can retain their meaning and gain explicit links

Implemented locally: existing `exemption` records may use `relation=exception`
and `applies_to` to identify affected rules while retaining `not_required` force.
The relationship pass can change only their relation and targets; it must preserve
all other meaning fields and the exact main quote. Standalone exemptions remain
valid. This reuses the existing proposal, edit/revision, Core relationship and
evidence-binding machinery. No new schema family or duplicate statement.

## Verification

- 417 extraction and schema tests passed; generated schemas match native CUE.
- Nine new test cases cover preservation, evidence-backed Core relationships,
  preview, revision history, reload, discovery export, changed/rejected targets,
  reclassification, rewritten meaning/evidence, invalid relations and self-links.
- All three saved raw reclassification proposals remain refused.
- All three **constructed link-only adaptations** apply, preserve original
  meaning/evidence and logical identity, create new revisions, and reload/export.
- Zero provider calls. This demonstrates supported operations, not new model
  behavior or improved extraction accuracy.

The saved cases connect the outside-building extinguisher exemption to the
distribution rule, and the dock-personnel and section 91.105 exemptions to the
seatbelt/seating rule. See [results](run-03/results.json) and each case's adaptation,
reviewed records and discovery output under `run-03/`.

The seatbelt cases copy and verify the original extraction manifest and all its
artifacts into isolated review workspaces. Original captures and review files
remain untouched. `run-01` and `run-02` are incomplete harness attempts: the
seatbelt workspace initially omitted the extraction manifest referenced by its
run metadata. ReviewStore correctly refused it. The runner now copies the full
verified extraction artifacts; no integrity check was relaxed. An initial suite
command also named a nonexistent test file and ran no tests; the corrected command
below completed successfully.

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python -m pytest packages/rulespec-extrapolator/tests tools/test_extraction_schemas.py -q --disable-warnings
.tools/document-poc-venv/bin/python tools/build_extraction_schemas.py --check
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-exemption-links/replay.py --output /tmp/rulespec-exemption-links-new-run
```

## Remaining boundary

No automatic section-wide applicability propagation, no repair of incomplete
default statements, and no proof that the model follows the amended instruction
or chooses every correct target. The earlier relationship prepass still showed
no audit accuracy gain and remains an experimental result. Do not promote that
extra pass on the strength of these deterministic tests.

The next model experiment, if pursued, should measure link discovery on fresh
documents with section-level exclusions and neighboring rules that must remain
unaffected. Freeze expected target sets before calls, then compare the existing
relationship pass with this minimal instruction/schema change. Keep API success,
accepted edits and semantic target accuracy separate.

Changes are uncommitted. UI and saved original extraction results were not changed.
