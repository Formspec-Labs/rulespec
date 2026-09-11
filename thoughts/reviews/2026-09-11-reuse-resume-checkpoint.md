# Resume Rulespec sibling reuse

Saved 2026-09-11 at the user's request. Start here, then use the
[canonical R1–R26 task list](../plans/2026-09-10-reference-integration-task-list.md)
for the detailed backlog and prior evidence. This checkpoint does not replace
that list or declare the goal complete.

## Objective and working rules

Continue hypothesis-driven reuse of useful capabilities from RefSpec, SpicySearch,
Spicy Regs, DocSpec, SpicyDocs and the local corpus. Keep code small, reuse the
owning schemas/readers, and fix shared defects upstream. The populated corpus
root is `/Users/mikewolfd/Work/corpora`; `~/corpora` was absent at inspection.

Focus on data and extraction/discovery outcomes. Prefer supported publisher XML.
Preserve original text, source identity, candidate readings, ambiguity, refusals,
review history and edition distinctions. Processing/schema validity is not proof
of complete meaning. Do not generate repeated explanations or add new model calls
without a bounded experiment that can change a decision.

The user has authorized local coherent commits and useful integrations. This work
has not pushed or deployed changes. Do not silently upgrade sibling wheels: other
sessions are actively editing those repositories.

## What is already delivered

The latest application delivery is the
[reference-feedback checkpoint](../experiments/2026-09-11-reference-feedback/README.md).
It records 662 passing source and isolated-installed application tests, 17 focused
checks, wheel/source parity and normal command checks. Those are the saved
delivery results, not a suite rerun for this documentation checkpoint.

- Existing reference readers run through the application, with exact source
  evidence, qualified CFR/USC readings, complete compound/range representation and
  explicit unsupported-scope refusals. Selected parser fixes went upstream.
- RefSpec supplies named-act/source-credit lookup, compilation occurrences,
  USLM/eCFR text and selected exact publisher target lookup. Source addresses and
  target bodies remain pinned; broader paragraph/edition correspondence is open.
- Saved-run reference feedback reuses Rulespec review history and Core findings.
  It retains the selected reading, rejected/accepted status, scan digest,
  source/reader pins and supplied-source diagnostics. It does not approve claims
  or automatically resolve parser defects.
- Proven unused citation copies were removed. Remaining graph consumers still
  require their own migration/behavior checks when selected for use.

The working application environment is `.tools/document-poc-venv`. Its last
delivered extrapolator wheel is under
`dist/reference-feedback-20260911-source-issues/`. The exact seven dependency
inputs and hashes are in
[wheel-inputs.json](../experiments/2026-09-11-reference-feedback/wheel-inputs.json).
Use that record instead of installing whatever a sibling checkout builds today.

Recent local commits before this checkpoint:

| Commit | Saved work |
| --- | --- |
| `02c482b` | Reference feedback and source diagnostics |
| `9976c4c` | Remaining reuse priorities and independent surveys |
| `fd59851` | Shared-library TODO work from another session; preserve it |
| `25ea300` | Fixed-ranking discovery evidence experiment |

## Recent decisions to preserve

The [fixed-ranking discovery experiment](../experiments/2026-09-11-discovery-evidence-budget/README.md)
is complete. With a 1,500-character evidence cap, support rose from 6/8 to 7/8 new
questions, below the preregistered two-gain gate. Existing uncapped packets reached
8/8. Giving direct hits priority avoided losing their evidence but did not improve
the selected support result further. Production stayed unchanged. These are
selected agent-authored cases, not an independent accuracy benchmark.

Earlier native-title defaults and CFR range/prose shortcuts also failed their
adoption gates. Do not reintroduce them as harmless defaults. The reverse explicit
CFR title form was separately demonstrated and delivered. Original captures and
failed controls remain in their experiment directories.

Three recent independent reviews are complete, with recommendations recorded:

- [Source evidence and feedback](2026-09-11-source-feedback-cross-relevance.md)
- [Consumer experiments](2026-09-11-consumer-experiment-cross-relevance.md)
- [Sibling ownership](2026-09-11-sibling-owner-cross-relevance.md)

Their advice supports testing one actual consumer, keeping workflow preparation
separate from discovery, and using public owner APIs. Recommendations are not
completed integrations.

## Current experiment and precise stopping point

The [publication metadata experiment](../experiments/2026-09-11-publication-metadata/README.md)
is in progress under R20/R21. Its plan, runnable reader probe, raw first row,
93-row inventory, admission report, body lookup and repository snapshot are saved.

DocSpec's existing public reader fully verified the selected 93-row Federal
Register catalog. The data already has useful dates, docket/RIN fields, native
facts and normalization/source-path evidence. No replacement normalizer was built.

The six proposed example document numbers were absent from the 8,284-row
`DocSpec/output/document-release-10k-v3/data/documents.jsonl` member inspected for
capture discovery. That release was not admitted and no bodies were read. This
does not establish absence elsewhere. The catalog's rendition URLs alone cannot
prove which captured bodies they describe.

**Resume by locating compatible captured bodies and freezing cases/controls.**
Then compare the actual discovery consumer with and without upstream metadata.
The comparison, adversarial controls, SpicySearch metadata-preparation execution,
production connection and wheel verification are not done. No model/network call
is needed for the next check. The experiment has no live process to poll.

DocSpec moved from its recorded probe HEAD while work was underway; DocSpec and
SpicyDocs have unrelated concurrent edits. Recheck their live state and preserve
those edits. The probe records actual imported module hashes. SpicySearch's old
private DocSpec catalog import remains a separate compatibility concern; public
owner-reader work is tracked as DocSpec D09 / SpicySearch SC01, with Rulespec's
shared-library follow-through also recorded in `TODO.md`.

## What remains across the full effort

The canonical list still has **19 open or partly complete workstreams**, six
delivered workstreams (R1, R2, R4, R5, R6, R14), and R15 closed as deferred after
its failed experiment. This count describes backlog states, not 19 equally sized
changes or prerequisites for a useful release.

| Group | Remaining work |
| --- | --- |
| Reference fidelity — R3, R7–R13 | Richer overlapping readings, additional families, remaining graph consumers, grounded missing titles, paragraphs/ranges, edition correspondence and unresolved act scope |
| Product evidence — R16–R19 | Meaningful comprehension gain, demonstrated discovery value, source-only/missed-mention feedback and resolution, one reviewed workflow/forms preparation example |
| Shared data — R20–R23 | Finish selected input/API checks; publication metadata; vocabulary/agency identities; meaningful layout and source-reading-order defects |
| Evaluation and simplification — R24–R26 | Broader fresh-document/product-value report; isolated per-target relationship verdict experiment; cheaper checks/removal of demonstrated duplication |

Continue one bounded decision at a time. Do not mark a workstream complete because
an import works, a fixture passes, or a useful subset ships. The task list gives
the explicit acceptance criteria and the experiment notes preserve unresolved
conditions. The overall goal remains active.
