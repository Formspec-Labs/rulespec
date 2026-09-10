# Actors and defined terms: production integration

The current extractor asks for actors and a source-backed index of explicitly
defined terms. Existing drafts can use `enrich` to add this structure through
ordinary review edits, preserving their statement text and populated fields.
The schemas come from canonical CUE; the graph uses existing Core types.

These are two live integration checks, not a paired accuracy experiment. Both
used Gemini 3.8 Flash, low thinking, temperature 0 and a 16,384-token output cap.
The source was the already-used passport introduction. The earlier
[fresh-source comparison](../fresh-structure-check/README.md) supplies the transfer
experiment; this check verifies product behavior on the user's displayed draft.

| Result | Fresh extraction | Fixed enrichment of existing draft |
| --- | --- | --- |
| Statements | 15 | 14, all original wording preserved |
| Populated actors | 6 | 6 |
| Definitions | 2 | 2 |
| Parser/component refusals | 0 | 0 |
| Input tokens | 2,244 | 3,406 |
| Output tokens | 2,236 | 1,104 |
| Total reported tokens | 4,480 | 4,510 |

Both identified information request letters (IRLs) and information notices (INs),
and distinguished the acting passport agencies/centers from the approval office.
The actual evidence and model assignments remain in the capture. Location checks
do not prove the assignments correct or exhaustive.

The fixed pass added 14 review events, left all other candidate fields unchanged,
and left the original extraction files intact. The UI shows the actor in the
existing card, the name/aliases on each definition, and clickable uses. Both term
links were exercised in a real browser; they select the matching definition,
move keyboard focus to its card and highlight its evidence. The original in-app
browser was unavailable because the Mac was locked; a separate Playwright browser
provided rendered verification. The server remains at http://127.0.0.1:63694/.

## Remaining failure observed directly

The fresh extraction produced the standalone requirement:

> Posts must use the cleared language in the IRLs.

Its separate permission retains the authority to modify that language for local
requirements and concerns, but the requirement itself loses that qualification.
The enriched existing draft retains both in the same statement. This repeats the
known standalone-reading weakness; the integration does not solve it. Two optional
component quotations in the fresh run also remained unresolved (modal wording
and choice evidence). All source evidence and issues are preserved.

This supports enrichment as a way to improve structure without introducing a new
statement rewrite. It does not establish that the combined first pass improves
meaning accuracy, nor that either path finds every actor or term use. Definition
reconciliation across separate source windows/documents remains unimplemented.

## Reproduction and provenance

- `extract/` and `enrich/` contain original requests/responses, source, exact
  outputs, hashes and frozen runtime files. `enrich/` also retains before/after
  history and each proposed/applied action. Original manifests are unchanged.
- Both native replay commands passed against the captured runtime with zero
  additional provider calls, including all 14 enrichment edits.
- Final inspection corrected qualification-family classification in `core.py`
  for scope, prerequisite and trigger relationships. The capture predates that
  small fix. Strict original replay therefore requires its frozen runtime;
  `final-code-verification.json` pins the final runtime used to reproduce the
  enrichment proposals and full saved review snapshot without API calls.
- The final code also reprocessed the fresh extraction without a provider call.
  Its result is saved under `.tools/actor-term-production-20260909/final-code-reprocess`.
- The three preceding experiments retain all 162 manifest-indexed artifacts
  unchanged. They remain evidence from their own frozen configurations.

Final verification: **397 package and schema-generator tests passed**; native CUE
generation and `git diff --check` passed. Reprocessing retained every extracted
claim and assertion identity; its provenance identifies the newer runtime.

No additional prompt tuning followed the observed passport failure. Schema-valid
output, exact evidence and replay do not establish semantic completeness.
