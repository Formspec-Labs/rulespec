# Remaining citation ownership

The extraction workflow already uses the stronger RefSpec occurrence readers.
The older graph package still has live citation readers, so removing its whole
module would change output. This iteration removes seven unused definitions
for act-name and compilation-locator extraction, with their private constants.
RefSpec already owns those features. No new dependency, reader, schema or model
call was introduced.

Code is committed locally as `97a6e26a4597db98f5457919e3bc1ac2a8d1073d`.
Comparisons ran before that commit; their module hashes identify the tested
working-tree bytes while their Git fields retain the preceding commit.
Nothing was pushed or published.

## Verified callers and ownership

| Job | Current caller and owner | Decision |
|---|---|---|
| Source CFR and USC occurrences, evidence and inherited list context | Rulespec `references.scan_references` → RefSpec `find_cfr_citations` / `find_usc_citations` | Keep this route; fix source-reading gaps upstream. |
| Source named-act occurrences and optional resolution | Rulespec `references.scan_references` → RefSpec `find_act_relative_occurrences` / `act_resolution` | Already connected; delete the unused older act parser from `rulespec-projection`. |
| Compilation volume/page reading | RefSpec `parse_eo_compilation_locators`; old Rulespec helper had no caller | Delete the unused Rulespec helper and type. Preserve the separate compilation guard used by its live CFR parser. Extraction export of these locators remains R7 work. |
| Agenda graph citations | `rulespec_projection.projection.unified_agenda_facts` → local `parse_cfr_citation` / `parse_authority_citation` and IRI helpers | Live: `EMIT_PROFILE_EDGE_PROJECTIONS` is true. Keep until a migration handles input policy and semantic differences. |
| Graph identifiers from published rows | `_cfr_iri`, `_authority_iri`, docket/proceeding helpers in `projection.py` | These read existing fields and mint identifiers; they are not source occurrence readers. |
| SpicyRegs rule-target production | `transforms.build_rule_targets` → `ontology.citations.parse_cfr_citation` | Still live. Accepts Federal Register dictionary values as well as prose. Requires its own migration. |
| SpicyRegs metadata normalizers | `build_proceedings`, `build_regulatory_agenda`, `build_comment_periods` → `ontology.citations` | Live consumers; do not delete the module as an obsolete archive. |
| Search-query recognition | SpicySearch `identifiers` | Permissive query behavior is intentional. Source scanning uses the appropriate narrower readers. |
| Court/presidential source scans | SpicySearch `derived_topic_passes.court` and `.presidential` → `cfr_citations` | Separate source reader with an explicit strict mode. The comparison below does not change its callers. |

Caller searches covered Python under Rulespec packages/tools/src and the source
trees of RefSpec, SpicySearch, SpicyRegs, DocSpec and SpicyDocs. The removed
helpers were not in `rulespec_projection.__all__`. Unknown external direct
imports were not audited; no compatibility aliases were added.

The package graph does **not** currently contain a projection–RefSpec cycle:
RefSpec depends on `rulespec-conformance`, whose dependencies do not include
`rulespec-projection`. Adding RefSpec to projection would nevertheless replace
its deliberately empty dependency set with RefSpec's larger dependency set.
This experiment provides no reason to make that change. There is no new shared
grammar package.

## Reader comparison

Inputs are all 8,424 distinct title/part keys from the saved OFR index, rendered
as constructed strings, plus 25 selected controls. Counts below concern only
the complete part key, not prose accuracy, recall over documents, legal validity
or the existence of a provision today.

| Reader | Correct complete part | Wrong part | No accepted part |
|---|---:|---:|---:|
| Older Rulespec projection | 8,152 | 272 | 0 |
| RefSpec occurrence reader | 8,235 | 189 | 0 |
| SpicySearch strict reader | 8,225 | 0 | 199 |

Raw index rows distinguish `7 CFR 15` (Nondiscrimination) from `7 CFR 15a`
(Education programs or activities receiving or benefiting from Federal
financial assistance). They also name `41 CFR 60-1` as Obligations of
contractors and subcontractors. The headings show why dropping the suffix
changes the referenced subject. Source CSV path and hash are in each summary;
the publisher HTML captures were not located in the current corpus tree.
No grammar change was admitted on the strength of these constructed strings.

Manual review of all 25 control outputs found:

- RefSpec and strict SpicySearch preserve `7 CFR 15a`; the older reader returns
  part `15`. RefSpec therefore fixes the 83 lettered-part cases already covered
  by the extraction workflow's existing choice of reader.
- RefSpec and the older reader return part `101` for `41 CFR 101-1`.
  SpicySearch retains `101-1` and explicitly refuses to decide whether it is a
  compound or range. Neither is a complete compound-part solution.
- RefSpec preserves the three sections in `40 CFR §§ 82.155, 82.156, and
  82.157`, including title context. The older parser emits the first section
  plus a bare part; strict SpicySearch emits only the first section.
- The older reader borrows `15` from `17 CFR 240, 15 U.S.C. 78c` and borrows
  `12` from `40 CFR part 37, 12 people attended.` The source readers do not.
- `3 CFR 127 (1981 Comp.)` is refused as a compilation locator by SpicySearch;
  RefSpec and the older reader still emit a CFR part. This is a concrete R7
  upstream reuse candidate, not fixed by this cleanup.
- SpicySearch's additional ten index misses are five-digit parts in titles
  5 and 43; its strict token permits at most four digits.
- Dictionary input and `40-60.5` work in the older parser. RefSpec and
  SpicySearch prose readers do not accept those input formats. Their errors
  on dictionaries are retained; they are interface differences, not evidence
  that a string API is broken.

**Decision:** bounded cleanup adopted; wholesale reader substitution fails the
declared gate. No extraction accuracy improvement is claimed for deleting
unused code. The comparison leaves live parsing behavior unchanged.

## Verification and retained evidence

- All 30 surviving functions/types and 25 surviving simple constants retain
  their original syntax trees. Deleted definitions are unreachable from the
  graph module's citation imports. See `final/summary.json`.
- All 8,449 baseline/current CFR outputs agree exactly, including errors.
- Projection: 30 source tests and 30 tests against the isolated wheel pass,
  including the original producer's graph fixtures and import-boundary checks.
- Application: 579 tests pass, with the existing 10,971 rdflib warnings.
- Wheel files match the final source and isolated installation byte for byte.
  The isolated environment contains only `rulespec-projection`, with no
  dependencies or third-party imports. The rebuilt wheel is also installed in
  the working extraction environment. See `wheel-verification.json`.

`baseline`, `pruned` and `final` retain outputs before deletion, after deletion,
and after the explanatory comments and additional dependency checks. The inputs
and reader settings did not change. `raw.jsonl.gz` contains complete reader
outputs, including errors; `controls.json` provides the manually reviewed
subset. No model cost or performance measurements were taken.

Reproduce from the Rulespec root, using a new output-directory name:

```sh
.tools/document-poc-venv/bin/python \
  thoughts/experiments/2026-09-11-citation-ownership/compare.py new-comparison
```

## Next implementation decision

Fix complete CFR tokens, ranges and compilation context in RefSpec before
migrating the older graph callers. Use SpicySearch's retained token and
compilation evidence as existing starting points, not a second production scan
whose guesses overwrite RefSpec. Read original publisher prose around compound
parts and genuine ranges; test how section pinpoints and list context survive.
Keep dictionary/compact-key decoding at the structured-input boundary and
measure graph output against the saved producer fixtures. Five-digit strict
tokens belong in SpicySearch's next source-reader check. R8 remains open.
