# Comparison passage references integrated

Comparison now selects `source_refs` using the existing CUE-generated source
reference definition and passage resolver, preserving full selected text and
original prepared-source offsets. Invalid selections refuse the judgment. No
fuzzy matching or quotation narrowing is added. The exact-quote helper remains
in use by the separate refinement workflow.

This is the user-authorized, narrowly scoped citation-reliability change proposed
after the comparison experiment. It does not mean the experiment's broader semantic
quality gate passed. The unresolved field-specific logic and modality findings
remain recorded in the original experiment.

Verification: 356 package/schema-generator tests pass, including repeated source
text, separate governing context, unavailable/invalid/empty references, unseen gaps,
inserted text and valid-but-unrelated references. Native CUE drift check passes.
The check below reproduces both saved ID prompts/schemas and all 36 judgments per
run, including the original reports, without another provider call:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/passage-id-integration/check.py
```

Audit captures now identify version `document-understanding-audit/4`. Original
experiments/captures remain unchanged; the complete pre-integration research and
runtime checkpoint is commit `68de277`. Replay old quote-era experiments using
that checkout or their recorded runtime, rather than silently reinterpreting them
with the new schema. No legacy quote response path is added to comparison.
