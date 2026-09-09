# Extraction handoff — September 9, 2026

The [operating guide](../../packages/rulespec-extrapolator/README.md) describes the
current workflow. Use low-thinking extraction with an optional medium-thinking
audit. Retain full source passages for discovery and human review before deriving
executable workflows. Default settings have not changed.

## Integrated

- Audit inventory selects passage IDs through a CUE-generated schema and resolves
  them through the existing source resolver. Missing, out-of-focus and inserted
  evidence remains refused. Exact source text, offsets, raw responses, rejected
  observations and provenance remain available. Comparison judgments still use
  exact quotations and produce existing Core `Finding` records.
- The successful example-inheritance wording lives in CUE `#Summary`. Extraction,
  refinement and audit share it. Native CUE now generates four schema views,
  including `inventory.schema.json`; Python has no competing inventory definition.
- Audit version 3 records the changed response shape. Historical version 2
  experiments retain their original captures and frozen runtimes. Their manifests
  were not rewritten. No legacy response conversion was added.

## Evidence and verification

The [fresh full-section inventory comparison](../../examples/document_understanding/full-inventory-evidence-comparison/README.md)
used the same 6,919-character source and current example guidance in both arms.
Quotation-based inventory refused 6 of 22 observations; passage-ID inventory
accepted all 20. Both retained the teacher example's governing condition. Both
still omitted details and produced imperfect classifications. This is one call
per arm on development data, with agent-authored, revisable meaning judgments.
The changed schema and instructions form a bundle; the comparison does not
isolate identifier syntax as the cause or establish general semantic accuracy.

Integration verification:

- All 347 package and schema-generator tests pass; native CUE drift check passes.
- The integrated provider request exactly equals the saved successful passage-ID
  request. The current parser reproduces all 20 saved inventory records unchanged.
- All eight newly saved experiment/check directories replay with their frozen
  inputs and runtimes; all 547 artifacts pinned by their outer manifests retain
  their recorded hashes.
- No fresh provider calls were made during integration. A new complete
  extraction-plus-comparison run under this runtime remains unmeasured.

The [earlier end-to-end run](../../examples/document_understanding/low-extract-medium-audit/README.md)
produced 19 accepted extraction statements, but four inventory refusals made its
review incomplete. Its three calls used 64,117 tokens and 48.24 seconds. Those
counts predate the integrated evidence and guidance changes. The
[deterministic evidence check](../../examples/document_understanding/refused-evidence-check/README.md)
reproduces all four refusals and resolves them using reviewed substantive quotes
or passage IDs without changing meaning. An unrelated valid ID still passes the
mechanical check: source existence does not prove interpretation.

## Remaining focused work

1. Test whether audit distinguishes complete standalone wording, qualifications
   retained only in `logic_text`, and qualifications absent everywhere. Existing
   instructions ask for this distinction, but the earlier audit missed it.
2. Check exemption/permission classification and duty-bearer wording against saved
   failures. Existing schemas express these distinctions; no new Core type is
   needed.
3. If revisiting dependent deadlines, measure segmentation-instruction adherence
   separately from meaning preservation. The
   [grouping experiment](../../examples/document_understanding/deadline-grouping-experiment/README.md)
   followed the grouping instruction in only one of two same-scope runs. No
   grouping instruction is adopted; existing fields support the successful form.
4. Before claiming broader improvement, repeat a complete workflow and evaluate
   new source material with independent, revisable judgments. Neither schema
   validity, accepted evidence nor replay establishes complete source coverage.

The [example-inheritance experiment](../../examples/document_understanding/example-inheritance-experiment/README.md)
and [transfer cases](../../examples/document_understanding/example-inheritance-transfer-experiment/README.md)
support the adopted wording narrowly. Detailed historical reports preserve their
original adoption decisions and settings; this handoff states what is integrated.

Implementation and research are committed separately. No push, deployment, release
or global memory change is part of this work.
