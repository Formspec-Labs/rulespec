# Test rich schema guidance and definition order

The user asked to test moving more meaning into schema descriptions and creating
local identifiers before emitting records that reference them. This is a bounded
extraction experiment, not a replacement of the current workflow.

## Comparisons fixed before provider calls

Use Gemini 3.8 Flash, temperature 0, a common 32,768 output-token allowance, the
same exact source windows, and the existing invented semantic examples. Run each
variant twice on the saved names, photographs, and names-excerpts documents.
These are known development cases, not blind holdouts. Do not send reference
answers or historical output to the extraction model.

1. **Current:** current provider schema and extraction instructions.
2. **Rich descriptions:** the same output fields, constraints, order, and prompt;
   add detailed titles and descriptions. This isolates added schema guidance.
3. **Definitions first:** rich semantic fields plus local concepts, unit IDs,
   explicit qualification references, and unresolved references. Emit concepts,
   units, then relationships. Preserve all existing meaning/evidence fields.
4. **References first:** the identical schema and prompt as variant 3, changing
   only top-level property order to relationships, units, then concepts. This
   isolates output order within the new representation.

The current-versus-rich comparison tests extra descriptions; rich-versus-local-ID
comparisons also change representation and cannot attribute all effects to IDs.
The two local-ID variants differ only in output order. A short request-acceptance
probe may precede the matrix; retain any rejection and its exact schema.

## Reuse and implementation

Reuse the current LangExtract native Gemini schema adapter, credential loader,
request/response capture, source-window planning, exact-evidence parser, Core
candidate compiler, and graph checks. Keep the experiment runner separate from
the production CLI. Preserve original captures, decisions, and review history.

Build an experiment-only adapter for local references. Check unique local IDs,
target existence and type, concept evidence, and rule-reference mappings. Keep
model references and their mapping to deterministic Core identifiers as explicit
artifacts. Never silently resolve an ambiguous quotation or invent a missing
target. Reference consistency and semantic correctness are separate measurements.

Record model version, temperature, token allowance, raw requests/responses,
instruction/schema hashes (including serialization order), dependency versions,
latency, usage, and failures. Freeze source files and experiment code so the
normalization and checks can be replayed without provider calls.

## Assessment and stopping point

Freeze the existing named omission, inherited-condition, modal-force, alternative,
and exception-target expectations before extraction. Inspect the raw output and
normalized records against those expectations; make each reference judgment
traceable to exact source and output records. Evaluate all four variants under
the same criteria, including any baseline successes lost. Assess concept reuse
and new relation-target errors as well as JSON validity and exact grounding.

Report each repeat separately, the observed output order, cost, and any refusal.
These small, overlapping development cases do not establish general document
accuracy or a causal explanation of the model's reasoning. Stop after the
comparison, save the recommendation, and leave the default workflow unchanged
unless the user subsequently requests adoption.

## Guidance checked

Google documents descriptions/titles as model guidance and schema key order as
the output order for the Generate Content structured-output path. The installed
SDK continues to use the already tested native `response_json_schema` adapter.
[Google structured-output guidance](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en).

## Progress

- Located the existing runtime at `.tools/document-poc-venv/` and confirmed the
  current provider schema imports.
- The three saved source documents are 2,651, 4,982, and 5,874 characters, so each
  fits one common 6,000-character focus window.
- Original workflow and captures remain unchanged.
- Implemented the isolated runner and seven passing offline adapter checks in
  `examples/document_understanding/schema-order-experiment/`.
- Froze sixteen selected existing cases and all three sources in `trial-01/`.
  All reference source coordinates resolve exactly. Added guidance is generic;
  source-specific reference answers never enter the prompts.
- All four request-acceptance probes succeeded, including the 1,496-word
  description variants. Recorded outputs follow the requested property order.
- Completed all 24 fresh extraction requests. The case results across the two
  repeats are Current 5/16 and 5/16; Rich 9/16 and 9/16; Definitions-first 9/16
  and 8/16; References-first 7/16 and 6/16. Four ambiguous damage readings remain
  unknown and receive no passing credit. These extraction-only results are not
  comparable with the earlier multi-pass 25/29 measurement.
- Detailed source adjudication and five concept-role counterexamples are saved in
  `examples/document_understanding/schema-order-experiment/REVIEW-NOTES.md` and
  `trial-01/assessment/results.json`. All 343 concept references resolve, but some
  point to a related topic rather than the actor/object named in the unit.
- All 24 provider schemas and Core graphs validate; all 24 normalizations replay
  without calls; all 9,102 protected original files are unchanged. Estimated API
  cost for the 24 extractions and four probes is $0.979929.
- Recommendation: retain richer descriptions; test clearer actor/object versus
  topical references and a separate qualification conversion before adopting IDs.
  No production defaults, UI, commits or external publication changed.
