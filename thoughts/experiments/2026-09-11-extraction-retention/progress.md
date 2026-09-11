# Retention implementation checkpoint

Both fixes are implemented and locally delivered. No model call, model-schema
change, commit, push or deployment occurred. The final result and installation
checks are linked in [README.md](README.md).

| Saved-output arm | Parsed candidates | Accepted statements | Passage-range refusals |
| --- | ---: | ---: | ---: |
| Baseline | 334 | 224 | 9 |
| Range correction only | 343 | 224 | 0 |
| Compound evidence only | 334 | 327 | 9 |
| Both | 343 | 336 | 0 |

These totals cover twelve saved cells, including one incomplete provider output.
They count repeated output events. The seven remaining Core rejections are the
existing kind/modality contradictions. The source and model statements remain
unchanged; this does not recover missing meaning from the failed context experiment.

Source changes:

- `extraction.resolve_passage` selects supplied endpoints/entries and retains the
  existing non-whitespace gap check. Catalog text and stable document passage IDs
  remain unchanged. Large numeric holes do not allocate a numeric range.
- `documents.source_slicer` shares discovery's indexed original-source slicing.
- `core.evidence_parts` retains complete quotation coordinates and emits existing
  evidence records for original-source pieces. Atomic `_evidence` stays strict.
- Core fallback/qualification bindings, terms, structured values/claimants and
  review validation retain complete evidence groups. Concept assignments still
  target the whole prepared region; their support excludes inserted formatting.
- Existing CUE/Core schemas suffice. No new persistent evidence shape or model pass.

Recorded checks: 118 extraction tests pass for the range snapshot; 105 selected
compound/review/enrichment/term/discovery tests pass; the full combined source
snapshot passes 552 tests with no skips. The per-command logs/receipts include
start/end load and serialized measurement ownership. Warnings are retained.

Preserved harness failures:

- The first compound test command named nonexistent `test_structure.py` and ran
  no tests. The corrected command uses existing files.
- Initial constructed candidates omitted required `actor`; their original source
  is saved under `control-history`. Adding an empty actor makes the controls valid
  without changing production code or the intended assertions.
- Fresh-context cells share their frozen runtime at the experiment root and are
  not standalone production review directories. Their own pins and original Core
  graphs are checked; the generic production manifest verifier correctly refuses
  them when treated as standalone runs.
- Matching statements by prose alone conflated identical appeal provisions at
  two source positions. The checker now includes exact occurrence coordinates.
- The older `actor-term-integration/extract` review example has an assertion-ID
  incompatibility in both the unchanged and new runtime. This is not introduced
  here. The latest normal saved extraction, from `2026-09-10-parallel-compression`,
  reloads with the same snapshot digest in both runtimes. Both results are saved.

All twelve combined cells passed the source, Core graph and original-graph checks
in `verification-retry2-command.log` before the older-example check failed. The
final verifier reused the completed baseline/current review probes, recorded
reprocessing identity changes separately and wrote the complete checks artifact.
The final verification and build completed successfully; the former session 95331
is terminal. The final wheel was rebuilt after the README update and installed in
a fresh environment with the six other pinned wheels. Earlier build artifacts and
the initial installation receipts remain saved.

The preceding 2026-09-11 task-list refresh checked those receipts and package bytes.
All 32 extractor wheel files match the isolated installation; its 30 source package
files also match. The working installation differs in eight changed modules.
Installed-suite execution and the normal CLI reprocess/export/reload checks remain
open. The saved comparison also records 52 changed revision IDs on reprocessing,
including 48 changed rule IDs. Original captures remain intact; verify reviewed
claims at the installed reprocessing boundary before delivery.

Subsequent execution completed the isolated suite (552 pass, no skips), two
constructed review-history controls and normal CLI reprocess/replay/scanning/
export checks. The first new control incorrectly assumed a single newline created
two passages; its failure and original fixture remain saved. The corrected test
asserts the actual catalog and passes without production changes. Both changed-ID
and unchanged-ID cases retain original reviews and leave new output pending.

The working environment received the same wheel and its command outputs match the
isolated installation. `verify_delivery.py` checks seven pinned wheels, source
files, original comparison snapshots and captures, and the command results. The
new review controls were copied into the package tests after their successful
installed run. No additional provider calls or full-suite result is implied.

Next: follow the [current task list](../../plans/2026-09-10-reference-integration-task-list.md)
for optional-reader runtime capture and the remaining reuse candidates. This
retention delivery is complete; the broad reuse goal remains open.
