# Post-evaluation AI correction demonstration

Three saved review actions restore omitted document alternatives and scope in a
separate copy of `reprocessed/section-01`. The resulting export has 12 current
claims and 17 retained revisions, including all 14 original revisions and all
66 original assertions. Every current claim remains pending review.

This is an **AI-authored correction demonstration after evaluation**. The author
read the [saved findings](../../../../packages/rulespec-extrapolator/evaluation/results/FINDINGS.md),
the relevant labels, and the pinned source before making these corrections.
It is not a blind extraction, human gold, or an independent assessment of the
corrections. No score, approval, or provider call was produced.

## Changes and exact evidence

| Action | Correction | Pinned source span |
| --- | --- | --- |
| [01: edit documentation requirement](actions/01-document-alternatives.json) | Restore the five listed alternatives, including name change orders or divorce decrees within the court-order/decree option. Preserve “one or more” and the married-name exception reference. | `[413, 1075)` |
| [02: merge permission and trigger](actions/02-urgent-travel-scope.json) | Carry the more-than-one-year, DS-11, and unchanged-ID branch into the urgent/emergency travel permission. Keep the separate suspension duty. | `[1676, 2103)` |
| [03: merge documentation duty and trigger](actions/03-unchanged-id-scope.json) | Carry the within-one-year and DS-11 branch into the unchanged-ID documentation duty. Keep the separate new-name ID waiver. | `[2424, 2651)` |

Offsets count Unicode code points in the copied [document](section-01/document.json).
Each action records its rationale, original target IDs, expected revision, and
`actor_kind: "aiAgent"`. The merges replace two current claims with one scoped
claim while keeping both original revisions and their assertions in history.

## Saved result and checks

- [Reviewed rulebook](reviewed-rulebook.json): current claims, every revision,
  source evidence, history, graph, and validation.
- [Review history](review-history.json): the three actual saved events and their
  generated identities and timestamps.
- [Reviewed Core graph](reviewed-graph.jsonld) and
  [validation](reviewed-validation.json): 241 nodes; JSON Schema validation and
  SHACL conformance passed.
- [Verification receipt](verification.json): all 123 manifest-declared source
  artifacts stayed byte-identical; all 206 original graph nodes remained
  unchanged; every retained evidence span matched the source. Reopening the
  saved database reproduced the export exactly.
- [Provenance](provenance.json): original manifest, action files, and consulted
  evaluation materials bound by SHA-256 digests.

The original captures and extraction outputs remain intact in `section-01/`;
review state lives in its separate SQLite database. Strict replay creates this
copy using only manifest-declared files, adds a replay receipt, and writes a new
manifest. The exact input manifest is retained as
[source-manifest.json](source-manifest.json). The source run in
`../reprocessed/section-01/` was not reviewed or changed. The database is local
state excluded from Git; the JSON actions and exported history preserve the
portable record. The preceding demo remains archived locally at the path named
in `provenance.json`; all three action files are byte-identical to that demo.

## Recreate the corrections

Run from the repository root with the package installed in the local virtual
environment. This verifies and replays the frozen extraction into a fresh copy,
then applies the three JSON actions in order through the CLI. Existing local
review databases and other files outside the extraction manifest are not copied.
The same sequence was executed successfully during verification.

```sh
demo_dir=examples/document_understanding/manual-slice/review-demo
review_copy_root=$(mktemp -d "${TMPDIR:-/tmp}/rulespec-review-demo.XXXXXX")
.tools/document-poc-venv/bin/rulespec-understand replay \
  examples/document_understanding/manual-slice/reprocessed/section-01 \
  --output "$review_copy_root/section-01"

for action in "$demo_dir"/actions/*.json; do
  .tools/document-poc-venv/bin/rulespec-understand review \
    "$review_copy_root/section-01" --action "$action" >/dev/null
done

.tools/document-poc-venv/bin/rulespec-understand export \
  "$review_copy_root/section-01" \
  --output "$review_copy_root/reviewed-rulebook.json"
```

A fresh application creates new review event, revision, occurrence, and merged
rule IDs and timestamps. Verification compared the resulting candidate fields,
exact evidence, issues, pending review state, and qualification targets; those
matched the saved demonstration. Reopening an existing database preserves its
exact saved identities.

Strict extraction replay is a separate check. It reparses the original raw
response and reproduces the original 14 claims, while the JSON review actions
recreate the corrections. Strict replay of this demo's copied extraction also
passed without changing its saved artifacts.

## Remaining limits

The flat candidate format retains alternatives and both branch conditions as
verbatim `logic_text`. It does not create executable alternatives, calculate
the one-year boundary, set a passport validity duration, or encode the urgent
permission's relation to suspension as executable logic. Read the current
claims for the effective review state; the graph deliberately retains old
assertions as historical evidence.

The married-name exception remains an unresolved reference. The documentation
requirement's acting party and the urgent-passport issuer remain unspecified.
Other extraction issues, including existing DS-11 form identifiers treated as
section references, remain outside this bounded pass. Structural validation and
exact quotations do not establish semantic completeness or human approval.
