# XPath payload validation

Decision: Fix the missing XPath string check in its owning schema/generator,
without changing the standard selector payload or adding an application validator.

Observed: The new CUE shape declares required string `rdf:value`. Its generated
SHACL checks presence/cardinality but the focused test expects a string datatype
and fails. JSON Schema rejects the numeric fixture. No runtime SHACL verdict on
that fixture has yet been recorded for this comparison.

Hypotheses: (1) SHACL generation drops the literal type, so the numeric fixture
passes RDF validation. (2) JSON-LD coercion already makes this field a string,
so the test's expectation does not establish a runtime gap. Actual RDF terms and
separate JSON Schema/SHACL verdicts distinguish these explanations. CUE `string`
alone cannot distinguish literal text from an IRI after JSON-LD expansion.

Arms: A is the existing generated output. If A confirms the gap, B derives plain
string-literal validation from the CUE field and the existing JSON-LD context,
preserving explicit IRI/language/typed-literal mappings. Inspect the generated
scope before adoption; do not add a term-specific repair or duplicate wire schema.

Cases: The exact new XPath positive/missing/nonstring fixtures; existing source
fragment/selector parity fixtures; focused controls for string literals versus
IRI-valued fields and existing typed/language literals. Inspect a numeric literal
through the real RDF loader. Full compiler/parity tests bound collateral effects.

Held constant: Same CUE definitions, context, source XML captures, fixture bytes
and model settings (no model calls). One deterministic baseline and changed run.
Retain baseline outputs and failures. Regenerated artifacts remain canonical.

Decision rule: Adopt only if the numeric XPath payload fails in both validators,
valid payloads remain valid, and affected compiler/parity checks pass. Preserve
separate exact-XPath source verification; datatype validity proves no target
exists. Record any broader pre-existing mismatch without silently weakening tests.

Stop bound: This validation discrepancy and its affected regression checks, then
return to application export review and source/wheel delivery. No generic XML
schema framework or new model output is part of this change.

Result: Hypothesis 1 is confirmed. The actual numeric payload expands to an RDF
integer and passes baseline SHACL while failing JSON Schema. `xpath-baseline.json`
retains that discrepancy. The generator now uses the existing shipped JSON-LD
context to distinguish plain string literals from identifier/typed/language values.
It emits the string check for ordinary and conditional plain-string fields; the
standard selector wire payload stays unchanged. No term-specific repair was added.

`xpath-changed.json` records agreement on all 16 source-fragment cases. All 146
compiler tests and 47 Rust tests pass. The 299-case parity run reports zero Core
divergences and two separately classified adversarial findings. The reference
corpus and 508 application tests pass. The added nested-refusal application control
passes with the other USLM tests (12 total). Only the extraction schema manifest
needed regeneration; its model-facing JSON schemas are byte-identical. The original
failed selector test and manifest-drift log remain saved.

Decision: Adopt this bounded upstream generator correction. Datatype validation
does not check XPath syntax or what it selects; the native and independent source
location checks remain necessary. The relevant standards are the
[Web Annotation XPath selector](https://www.w3.org/TR/annotation-model/#xpath-selector)
and [JSON-LD type coercion](https://www.w3.org/TR/json-ld11/#type-coercion).
