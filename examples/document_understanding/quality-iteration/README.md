# Extraction quality iteration

Rulespec now preserves more of a rule's complete meaning and can expose missing
content through a separate source-first check. The saved examples demonstrate
inherited conditions, modal distinctions, alternatives, exact evidence and
corrections that preserve history. Automatic extraction still misses guidance
and explicit exception relationships. This is a usable extraction and assessment
workflow, with specific quality work remaining.

Temperature `0.2` recovered some name-related content but increased photo
omissions. Keep the default at `0` for now. The
[matched-request receipt](temperature-comparison-controls.json) confirms that
each of the three source pairs differs only in temperature. One sample per
source and setting does not establish a general winner.

## What goes in, what happens, and what comes out

1. **Input:** exact document text with its section coordinates and source map.
   This example uses saved passport-manual passages about names, photographs
   and adjudicative responsibilities. Original captures remain unchanged.
2. **Extraction:** Rulespec selects a focused passage and bounded surrounding
   context. Gemini returns a small application record containing meaning,
   modality, governing scope, alternatives and source quotations. Rulespec
   checks the quotations and deterministically creates Core records.
3. **Output:** individually referenceable draft meanings, a Core JSON-LD graph,
   component evidence, unresolved references, refused candidates, original
   requests/responses and processing records. The output supports discovery and
   later feedback, or closer review before workflow/form construction.
4. **Checking:** a separate request inventories source meanings before seeing
   the draft. Another compares that inventory and the complete draft fields.
   Saved reference judgments assess the results. Corrections create new
   revisions and preserve prior evidence and decisions.

Processing completeness, semantic coverage and review completeness are separate
results. Exact quotations and valid schemas do not establish complete meaning.
No `ClosureClaim` is emitted, and discovery does not require upfront human review.

## What changed

The [capability assessment](../../../thoughts/reviews/2026-09-07-extraction-capability-assessment.md)
maps meaning to application fields, existing Core records, checks and remaining
uncertainty. Core schemas themselves did not change.

| Capability | Implementation |
| --- | --- |
| Must, should, may, must not, not required, possible and unstated force | Explicit `modality` in application profile `document-understanding/2`; incompatible normative kinds are refused visibly |
| Complete rule meaning | Existing `ValueAssertion` stores the full meaning, including scope; a scope change creates a different proposition |
| Conditions and surrounding context | Existing `EvidenceBinding` roles `definesScope` and `providesContext`; `qualifies` remains available for linked modifiers |
| Applicability | Existing `ApplicabilityScope` and `hasApplicability` when supported jurisdiction is supplied; otherwise retain scope in meaning and evidence |
| Alternatives and thresholds | Source-supported choice wording, alternative quotations and uninterpreted logic; no automatic conversion into executable policy |
| Context selection | Exact paragraph/list indexing and bounded parent/neighbor context, separate from the focused passage |
| Gap discovery | Source-first inventory, separate claim comparison and the existing evaluator's missing/partial/unknown states |
| Recoverability | Overflow refusals remain serializable; fully judged total omissions fail quality without implying unfinished review; explicit section IDs survive array ordering |

The [Gemini schema investigation](../../../thoughts/reviews/2026-09-07-gemini-schema-guidance.md)
records official guidance and four controlled probes. Repeated per-kind schema
shapes failed through both transports; a shared record shape succeeded. The final
explicit native JSON Schema retains every semantic field, required properties,
closed enums and descriptions. Prompt examples describe semantics without
duplicating JSON output examples. Schema acceptance is separate from extraction
quality.

## Results against the saved cases

The [30-case reference assessment](reference-assessment/RESULTS.md) contains the
final source-adjudicated decisions. Its
[reference set](reference-assessment/reference-cases.json) preserves expected
invariants, source evidence and negative controls. The
[results](reference-assessment/results.json) pin every assessed rulebook and
include claim IDs and rationale. These are the project's gold reference answers
for these cases, attributed to Codex and open to evidence-backed revision.

Across the 29 automatic-extraction cases, temperature `0` passes 17 and fails 12;
temperature `0.2` passes 16 and fails 13. The thirtieth case independently passes
the correction-history demonstration. Cases overlap and include strict checks
for explicit relationships; these counts are not a general accuracy estimate.

| Input | Temperature 0 accepted / refused | Temperature 0.2 accepted / refused |
| --- | --- | --- |
| Contiguous name-change section | [11 / 0](runs/names-05/rulebook.json) | [13 / 0](runs/names-t02/rulebook.json) |
| Photograph passages | [33 / 0](runs/photos-03/rulebook.json) | [28 / 0](runs/photos-t02/rulebook.json) |
| Selected name passages | [24 / 1](runs/names-excerpts-03/rulebook.json) | [25 / 1](runs/names-excerpts-t02/rulebook.json) |

`Accepted` means the candidate passed compiler checks. It does not mean the
meaning is correct. Both selected-name refusals concern the acceptable-document
list's component quotation outside the supplied request; the contiguous runs
retain the whole list correctly.

The final matched runs retain the older-name-change emergency permission's full
parent condition, the recent-change ID exemption and separate documentation
duty, DS-11 photo re-execution scope, and recommendations as `should`. The
contiguous names runs retain all six document options and their nested grouping.
Temperature `0.2` adds qualified name guidance and the applicant definition but
loses photo tilt, appearance-change acceptance, immaterial-damage acceptance,
printing-defect return and the open-eyes recommendation.

### What the checker demonstrated

- [Names audit](audits/names-03/report.json): detects the lost parent condition
  in the preserved `names-04` output and omitted generally-needs-documentation
  guidance. The first checker missed that same scope defect; its captures remain.
- [Omitted-option control](negative-controls-02/omitted-alternative/report.json):
  detects missing customary-usage documentation even though the full quotation
  includes it. Other unit judgments remain unknown; the detected omission is
  still a definite finding.
- [Wrong-target control](negative-controls-02/wrong-exception-target/report.json):
  detects an exception wrongly attached to pending-name clearance. The quote is
  exact and the target exists, demonstrating why those checks alone are
  insufficient.

The first control run exposed a handoff defect: comparison requests omitted
existing citations and component anchors. The final code passes them through;
a failing regression now passes, and the follow-up recognizes the retained
citations while still detecting both intended defects. Earlier observations and
the preparation failure remain saved under `negative-controls/` and
`negative-controls-preflight-01/`.

The [fresh responsibilities assessment](fresh-assessment/summary.json) used
expectations frozen before the first extraction. That extraction retained the
expected content but classified factual statements as possibilities; its
automatic checker missed this. The informed `fresh-02` follow-up preserves all
seven expected meanings with the correct modal distinction. Exact component
anchoring remains unresolved for three units, so the evaluator reports four
covered and three unknown. This follow-up is development evidence, not a second
blind holdout.

### Corrections and preserved history

The [historical correction demonstration](review-demo/verification.json) replays
all three original actions with unchanged attribution, prior graph nodes,
current targets and reopen behavior. The missing weaker statements remain
disclosed. The [confidential-name correction](review-demo/confidential-exception/verification.json)
adds the exception to the correct court-document baseline while retaining all
25 existing records, including application-name disclosure and additional
evidence permission. This is a saved AI review action, separate from automatic
extraction success.

## Run the workflow

From the repository root, with the
[application environment installed](../../../packages/rulespec-extrapolator/README.md):

```sh
# Apply today's parser/compiler to retained model responses; no provider call.
.tools/document-poc-venv/bin/rulespec-understand reprocess \
  examples/document_understanding/quality-iteration/runs/names-t02 \
  --output .tools/my-quality-run
.tools/document-poc-venv/bin/rulespec-understand replay \
  .tools/my-quality-run --output .tools/my-quality-replay

# A fresh extraction and independent audit make provider calls.
.tools/document-poc-venv/bin/rulespec-understand extract \
  examples/document_understanding/quality-iteration/source/fresh-responsibilities.json \
  --temperature 0.2 --env-file /path/to/local.env --output .tools/my-new-run
.tools/document-poc-venv/bin/rulespec-understand audit \
  .tools/my-new-run/rulebook.json --env-file /path/to/local.env \
  --output .tools/my-new-audit
.tools/document-poc-venv/bin/rulespec-understand audit-replay \
  .tools/my-new-audit --output .tools/my-new-audit-replay
```

Use new output directories. Strict replay intentionally rejects a different
runtime. Extraction reprocessing records that change; historical audit replay
uses each verified frozen application, as demonstrated by
[verify_runtime.py](verify_runtime.py). Experiment helper scripts retain the
local credential path used during this authorized run; the CLI accepts another
explicit env file.

## Verification and remaining work

The extraction and projection suites pass 223 tests and 101 subtests. The
[compatibility receipt](compatibility-verification.json) verifies all five
historical v1 runs without adding v2 meaning they never supplied. The
[runtime receipt](runtime-verification.json) records final extraction/audit
replay, wheel smoke checks and preservation hashes. All 1,406 protected original
files remain unchanged. Existing dependency deprecation warnings remain.

The next iteration should concentrate on:

1. **Omitted qualified statements:** certificate guidance, spacing/suffix rewrite
   caveats, Sr./Señor context and other content without a strong modal verb.
2. **Explicit exception targets:** turn correctly retained caveats into supported
   relationships, particularly confidential names and photo qualifications.
3. **Complete checker inputs and calibrated judgments:** preserve reference and
   component evidence, challenge false passes, and split oversized assessment
   batches. Two temperature names-assessment batches exhausted their output
   budget; their automatic verdicts remain unknown alongside the adjudication.
4. **Component evidence and logical grouping:** resolve repeated quotations and
   prevent ambiguous category wording such as a list rendered as uppercase AND.

The current work is local and uncommitted. Rulespec owns the entire data process;
RefSpec remains the optional vocabulary integration. No UI work is required for
the demonstrated extraction, checking, correction or replay steps.

Implementation is paused after this verified iteration at the user's request.
The [effort/value assessment](../../../thoughts/reviews/2026-09-07-extraction-effort-assessment.md)
weighs the next work against current usefulness and recommends a bounded content
and relationship improvement before broader expansion.
