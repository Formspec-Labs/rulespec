# RefSpec CFR occurrences connected and installed

The optional application reference scan now reuses RefSpec's CFR occurrence
reader alongside the five previously connected SpicySearch families. Both
`references` and `discovery-export --references` retain CFR list members,
subsection labels, native flags and exact title-bearing context. No model or Core
schema changes were needed.

## Decision and evidence

Adopt this bounded integration. It supplies explicit CFR occurrences previously
absent from the scan while preserving all 16 five-family occurrences, including
their IDs, across the nine frozen source cases. The three added CFR occurrences
match RefSpec's native readings. These cases are development/regression inputs,
not a fresh citation-completeness benchmark.

- **470 extractor tests passed** in 38.19 seconds; see [tests.log](tests.log).
  Tests cover exact quotations, Unicode, repeated occurrences, spaced labels,
  list title context, inserted source-map text, native refusal flags, historical
  title 35, both CLI paths and unchanged accepted statements.
- A new export check initially failed because rejected readings retained their
  own quotation blocks. The existing shared-evidence path now handles them too;
  the failure remains in [source-check-before-export-fix.log](source-check-before-export-fix.log).
  The earlier pre-integration failures remain in [red.log](red.log).
- All nine complete scans match between source imports and the freshly installed
  package. A separate installed five-family control confirms unchanged old
  candidates. [verification.json](verification.json) records these comparisons
  and the exact six wheel hashes.
- Both installed commands ran from `/tmp`. The constructed CLI fixture retains
  two CFR list members, their shared title context, one public law and one
  refused CFR reading. Statements and default discovery records remain identical.
  This manually compiled fixture is a packaging/control test, not a model run.
- `uv pip check` passes for the isolated environment and the updated
  `.tools/document-poc-venv`. The latter now uses the same built extractor.
  [Installed requirements](installed-requirements.txt) record the isolated environment.

No provider calls, source downloads, commit, publication or deployment occurred.
The larger reuse objective remains active.

## Field mapping and remaining uncertainty

| Native information | Application output | Existing Rulespec representation/check | What it does not establish |
| --- | --- | --- | --- |
| Written occurrence and offsets | `evidence`, or shared `evidence_refs` in discovery | `_evidence`, `SourceFragment` identity, exact source verification | Complete interpretation of every qualifier |
| Title/part/section and attached labels | `reading` plus one normalized display `value` | Native fields retained; frozen parity assertions | Existence of a subsection in any edition |
| Written title for an abbreviated list member | Evidence role `reference_context` | Same verified fragment/evidence table as other source support | Inferred title from an unstated document context |
| Impossible title / implausible part | `rejected`, native `reading` flags and code | Exact source evidence retained when available | Current or historical legal validity from syntax alone |
| Reader implementation | `parsers` with version and module hash | Recorded per scan; source/wheel comparison | A new interpretation's approval |
| Mention location within a document | Stable candidate ID and `record_ids` | Existing fragment and passage IDs | A located external target or an applicability link |

The application shape is `document-references/2`. These are deterministic
candidate observations, so they do not add model response fields or a second
handwritten schema. No `Artifact`, relationship assertion or `ClosureClaim` is
created merely because a name parses. Captured parser identity distinguishes
readings made by different implementations without changing the source occurrence.

The source example `49 CFR Part 172 subpart E (labeling) or subpart F (placarding)`
still yields a part-level occurrence. It does not yet retain either subpart or
their choice. This is a demonstrated upstream qualifier gap, not hidden by the
passing package tests. USC, omitted-title references, paragraph ranges, edition
lookup and deciding governing conditions remain separate tasks.

## Reproduce the checked installation

From the Rulespec root, use a new environment path and verify the selected wheel
bytes against `verification.json`:

```sh
uv venv --python 3.12 .tools/reference-integration-20260911
uv pip install --python .tools/reference-integration-20260911/bin/python \
  --find-links ../spicysearch/vendor \
  dist/production-20260910/rulespec_artifacts-1.0.11-py3-none-any.whl \
  dist/production-20260910/rulespec_conformance-0.2.0rc18-py3-none-any.whl \
  dist/production-20260910/rulespec_projection-0.1.0-py3-none-any.whl \
  dist/reference-tools-20260910-parenthetical/spicysearch-0.1.4-py3-none-any.whl \
  dist/reference-tools-20260910/refspec-0.1.0.dev0-py3-none-any.whl \
  dist/reference-integration-20260911/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl
uv pip check --python .tools/reference-integration-20260911/bin/python
```

[check.py](check.py) captures the source/installed comparison and refuses to
overwrite its output. Its `--cli` mode creates a fresh fixture directory and
three outputs; preserve the original run and choose a separate capture directory
for another CLI run. Raw evidence is in [source-final.json](source-final.json),
[installed-control.json](installed-control.json), [wheel-final.json](wheel-final.json),
[cli-references.json](cli-references.json) and [cli-discovery.json](cli-discovery.json).
