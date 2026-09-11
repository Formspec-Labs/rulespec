# Capture the reader implementation used by a saved run

Decision: extend the existing runtime capture rather than create another replay
format or reader registry. The preceding retention delivery is complete and sealed.

Observed gap: the application freezer omits `references.py` and `uslm.py`, RefSpec
and SpicySearch versions, and their reference-reader source modules. The earlier
context experiment had to pin six extra modules manually. Reader exports already
record direct parser hashes and index digests, but those do not complete a saved
extraction/audit/refinement runtime snapshot.

Hypothesis: adding the relevant source modules and optional package versions to
the existing capture makes reader changes detectable by its existing replay checks,
without changing candidates, schemas, prompts or normal extraction dependencies.

Arms: installed retention baseline versus the small capture extension. Hold saved
documents/provider responses and reader implementations fixed. Use constructed
offline runs to exercise the actual freeze/replay path; make no provider calls.

Cases and controls:

- Capture both application adapters and installed native reader/helper sources.
  Include the six known missing modules and traced normalization/act helpers.
- Mutate a captured reader source: strict replay must refuse drift. Restore it:
  replay must succeed. A missing optional package must not break plain extraction.
- Record optional package versions when available. Do not turn an unrelated
  missing transitive dependency into an invented absent-package result.
- Reprocess the normal saved capture under the new runtime and compare meaningful
  candidates, graph and exports; retain original captures and review history.
- Test direct source, build the changed extractor wheel, then execute from the
  installed package outside the checkout. Preserve the previous wheel and receipts.

Decision rule: deliver only if coverage and negative controls pass, unchanged
meaning/output checks pass, and plain extraction/Core validation remain usable
without optional reference packages. This conservatively records supported readers
that are installed; it does not claim an exact per-function execution trace. A
changed captured optional reader can therefore cause strict runtime drift even on
a plain-text run. Existing reprocessing remains the explicit way to use new code.

Stop at that bounded result. This changes capture completeness, not extraction
accuracy, citation coverage or context selection. Qualified USC and the remaining
reuse/consumer tasks stay on the canonical backlog.

Comparison clarification after the first installed check: raw graph byte equality
failed because `AILineage` identity is a digest of the complete run, including its
new runtime record and reprocessing metadata. The only observed graph differences
were that ID and references to it. Preserve the first failed verifier/log. Verify
each old/new ID against its own run, substitute only that ID and its lineage links
for comparison, and require all other fields to match. Add controls showing changed
model provenance and fabricated source text still fail. This corrects the comparison
instrument; it is not a production graph change or a claim of raw graph equality.
