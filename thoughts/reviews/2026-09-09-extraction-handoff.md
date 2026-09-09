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

## Subsequent small improvements

Discovery now exports existing `logic_text` alongside short statements. Fourteen
focused tests pass; the field preserves qualifications in both the saved accounting
case and a fresh notice-procedure case. Full source passage records remain intact.

The [two controlled comparisons](../../examples/document_understanding/minor-audit-improvements/README.md)
used 16 calls. Added CUE classification guidance improved labels but lost teacher
scope in one result; no adoption. Unit judgment order passed the primary verdict
checks 6/6 in both arms; no measured improvement and no adoption.

A reserved 29 CFR 825.303 section then produced 18 accepted extraction statements
and 19 accepted inventory observations. Comparison refused three claim/unit pairs
because copied quotations changed whitespace, leaving review incomplete. The raw
audit caught one overbroad permission but could not admit its evidence. Detailed
source reviews, refusals and identical replay are saved in the linked experiment.
The next candidate is comparison-stage passage references, not more prompt tuning.
These subsequent changes are local and uncommitted.

## Whitespace fallback tested, not adopted

The [follow-up experiment](../../examples/document_understanding/whitespace-evidence-experiment/README.md)
reprocessed the saved comparison with a whitespace-only fallback. All six refused
judgments recovered with original source offsets and unchanged raw verdicts;
accounting became complete, while the audit correctly remained failed. Of 17
expected-refusal controls, 15 remained refused, but two constructed table/list
joins were accepted. This fails the broad acceptance gate. No production matcher
change or provider calls; preserved artifacts include all 23 controls. General
whitespace matching and its superiority to passage IDs are not established.

## Known-library fuzzy comparison

The [library comparison](../../examples/document_understanding/library-fuzzy-evidence-experiment/README.md)
tests fuzzysearch 0.8.1 and installed LangExtract 1.6.0 across nine configurations
and 29 controls. Strict LangExtract (token coverage/density 1.0/1.0) recovers all six
judgments while rejecting seven content-change counterexamples; three ambiguity
and two layout cases remain accepted. Disabling fuzzy alignment produces identical
controls and audit, proving token-exact alignment suffices for these recoveries.
Reuse of that existing aligner is a concrete next candidate, with explicit
uniqueness/layout policy; no production alignment change was adopted.

The full-grid replay has stable printed outcome counts but fails exact equality.
A short-control diagnostic finds the asymmetric fuzzysearch configuration choose
a different occurrence of repeated text. The token-exact follow-up replays exactly.
All observations and counterexamples are saved; no model calls were made.

## Comparison passage-ID experiment executed

The [four-call comparison](../../examples/document_understanding/comparison-passage-ids/README.md)
kept the saved full source, draft and inventory fixed. Current exact matching accepted
32/36 then 36/36 judgments; token alignment accepted 36/36 in both; passage IDs
accepted 36/36 in both. Both ID runs cite the governing phone-call lead-in that the
second quote run leaves out of its selected evidence. All four detect the known
scope defect, but none explicitly identifies qualifications retained in logic_text.
The strict adoption gate is unmet; no production matcher or comparison change.

IDs used 22.6% fewer mean output tokens, but only 3.0% fewer total tokens because
input repetition remained fixed. All four calls used 254,201 reported tokens.
Local controls show cross-passage disambiguation but unresolved within-passage
ambiguity, layout joins and loss of separately selected conditions when narrowing.
Passage-only comparison is the simpler candidate for a separately narrowed
reliability decision; no evidence supports adding a fuzzy layer. Stop this bounded
experiment here. Captures, masked/unmasked review and identical replay are saved.

Source correction: C0014.logic_text starts mid-sentence at F004. It retains unusual-
circumstances/emergency qualifications but lacks F003's unforeseeable-leave lead-in;
it is not the complete original paragraph. Preserve that distinction in later
field-specific quality work. These results remain local and uncommitted.
