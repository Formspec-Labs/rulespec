# Rich schema and reference-order experiment

**Richer descriptions improved the selected case results in both repeats. Adding
concept and unit IDs did not improve the score beyond descriptions alone.**
Definitions before references worked better than the reverse in this small test,
but the new references still need clearer semantic roles before adoption.

This experiment originally left the normal extraction workflow unchanged.
The user subsequently authorized [adopting the richer descriptions](../schema-guidance-adoption/README.md).
The recorded comparison, raw captures, normalization, and source review remain
unchanged; `Current` below means the baseline at the time of the experiment.

## What was tested

Gemini 3.8 Flash processed the same three saved source documents twice under each
of four variants: 24 extraction requests after four empty-source acceptance
probes. Every extraction used temperature 0, one complete source window, the same
invented semantic examples, and a 32,768 output-token allowance. Model responses
reported `gemini-3.8-flash`. No response exhausted that allowance.

| Variant | Schema descriptions | Output structure |
| --- | --- | --- |
| Current | 23 descriptions, 249 words; no titles | Existing semantic units and quotation-based targets |
| Rich descriptions | 26 descriptions, 1,079 words; 26 titles | Exactly the same fields, constraints, order and prompt as Current |
| Definitions first | 46 descriptions, 1,496 words; 44 titles | Concepts → units with IDs → relationships → unresolved references |
| References first | Identical to Definitions first | Relationships → units with IDs → concepts → unresolved references |

The two reference variants have identical schema content and prompts; only the
top-level property order differs. Current versus Rich isolates the added schema
annotations. Rich versus Definitions first changes representation and reference
instructions as well as adding identifiers, so it cannot isolate an ID-only effect.

Schemas, exact requests and output order are retained in [trial-01](trial-01/).
Google documents titles/descriptions as model guidance and schema key ordering
for structured output. All four probes succeeded, and all 24 extraction responses
followed their requested top-level order.
[Google guidance](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en).

## Results

Sixteen previously saved development cases were fixed before extraction: four
from name changes, six from photographs, and six from the longer name excerpts.
They check omissions, inherited conditions, alternatives, modal force and explicit
exception relationships. Codex reviewed source meaning and raw/accepted output;
the [adjudication script](adjudicate.py) serializes those authored decisions and
checks their evidence references. It is not an automatic semantic scorer.

| Variant | Repeat 1: passed / 16 | Repeat 2: passed / 16 | Unknown across both repeats | Mean extraction cost per source |
| --- | ---: | ---: | ---: | ---: |
| Current | 5 | 5 | 0 | $0.0329 |
| Rich descriptions | 9 | 9 | 1 | $0.0424 |
| Definitions first | 9 | 8 | 2 | $0.0459 |
| References first | 7 | 6 | 1 | $0.0419 |

Unknown cases concern ambiguous damage-category grouping and receive no passing
credit. Most cases are composite: losing one required element fails the case even
when its other meanings remain correct. These are selected development checks,
not overall extraction accuracy. The previous 25/29 result included multiple
audit/refinement passes; this experiment tests initial extraction only.

The clearest improvement was retaining the longer excerpt's finality, spacing,
rewrite guidance and definitions. Both Rich runs preserved substantially more of
that material than Current. The gain was uneven: Rich still omitted the short
source's generally-needed-documentation statement in both repeats. No variant
recovered the photograph certificate timing caution or completed the hardest
infant/disability/glasses relationship cases.

Source decisions, exact evidence, inspected record IDs, raw-output hashes and
case-by-case rationales are in [results.json](trial-01/assessment/results.json).
[REVIEW-NOTES.md](REVIEW-NOTES.md) records the detailed review and limitations.

## What the ID test established

Local references work mechanically: all 343 concept references name existing
concepts, and their supplied concept quotations occur in the source. Definitions
first produced 55 concepts and 225 references; References first produced 30 and
118. Repetition does not establish that the concepts or roles are correct.

A targeted review found that some references functioned as broad topic tags while
their fields claimed actor/object identity. For example, Names/Definitions-first/2
u15 correctly describes submitting name-change documentation, but its sole
`object_refs` target is Form DS-11. Photos/Definitions-first/2 u15 names the returned
passport application as its object but references New photograph request, the
purpose of returning it. Five counterexamples are retained in results.json.
No overall semantic error rate for concept bindings is claimed.

Definitions first emitted seven relationship records: two structurally invalid,
one targeting a refused record, and four accepted. References first emitted
twenty-three: thirteen structurally invalid, two targeting refused records, and
eight accepted. Its larger number of attempted links matters when comparing
counts. One raw disability exception pointed to the endorsement-46 recommendation
instead of the natural-expression recommendation. All eighteen accepted edges
across all four variants were source-reviewed and target appropriate baselines.

A recurring failure is combining a requirement or permission with `relation:
exception` or `prerequisite`. The current application profile reserves those
relationships for separate condition/exception units, so Core refuses the mixed
record. This is a mismatch between the model's representation and the application
profile, not evidence that the underlying statement should disappear.

## Recommended next change

Carry forward the richer descriptions. Keep definition-before-reference order
for a subsequent reference experiment. Before adopting its format:

1. Distinguish broad concept associations from the specific actor and object of
   an action, and check agreement with their supporting text.
2. Give a statement's meaning and its qualification relationships separate fields
   without requiring the model to duplicate a duty as a modifier. Test a
   deterministic conversion into existing Core condition/exception records.
3. Re-run the saved grounding and exception counterexamples, including the raw
   meanings currently refused, before changing the default extractor.

The richer descriptions have since been adopted. The reference-format changes
remain proposals; this experiment does not implement a new production profile or
global concept reconciliation. Concept mappings remain explicit experimental
sidecar records. Existing Rulespec code still supplies canonical rule identities,
evidence, and Core graphs.

## Verification and cost

- Seven offline adapter tests pass, including duplicate identifiers, missing and
  wrong-type targets, refused target records, and two meanings sharing one quote.
- All 24 responses pass their provider JSON Schema. All 24 normalized Core graphs
  pass existing JSON Schema and SHACL graph checks. Semantic failures above remain.
- All 24 normalizations replay without provider calls. All 9,102 protected prior
  files retain their original hashes.
- Total estimated paid-tier API cost, including four probes: **$0.979929**. The
  estimate uses reported input, cached-input, output and thinking tokens at the
  standard prices verified September 7, 2026. It is not an invoice. These sources
  contain 421–944 words; whole-document and audit/refinement costs are separate.
  [Official pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.8-flash).

The original strict verification commands require the recorded runtime. The
current extractor deliberately differs after schema adoption, so
`verify_delivery.py` will report that drift. To check saved-output compatibility
under the adopted code without changing any original files:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/schema-guidance-adoption/verify.py --output /tmp/rulespec-schema-adoption-check.json
```

With the original frozen runtime restored, the original commands are:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/schema-order-experiment/experiment.py replay
.tools/document-poc-venv/bin/python -m pytest examples/document_understanding/schema-order-experiment/test_experiment.py -q
.tools/document-poc-venv/bin/python examples/document_understanding/schema-order-experiment/verify_delivery.py
```

To repeat this comparison live, restore the original runtime first: the runner
derives its variants from `provider_schema()`, whose default has now changed.
Then use a new output directory with `experiment.py prepare --output PATH`,
followed by `probe` and `run` with the same `--output PATH` and an explicitly
selected `--env-file`. Existing run directories are never overwritten. Source
adjudication and its report paths are deliberately tied to trial-01; new live
outputs require a new review, not a copied score.
