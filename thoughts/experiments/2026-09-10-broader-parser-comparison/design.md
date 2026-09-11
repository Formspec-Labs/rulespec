# Broader reference-parser comparison — preregistration

Decision: Which existing parser family deserves the next Rulespec reference-discovery integration: current narrow scan, broader RefSpec readers, SpicySearch's query detector, or Rulespec's existing projection readers?

Observation: The current reference-tool experiment scans CFR and USC. Other callable parsers exist, but code inventory does not establish accurate prose extraction or usable source evidence.

Hypotheses:
- H1: Broader readers recover correctly typed references in additional families. Prediction: correct additions in at least three families absent from the baseline, without false identities on negative controls.
- H2: Some apparent gains are permissive or field-specific interpretations. Prediction: damaged/ambiguous controls produce misleading partial identities, or whole-value readers cannot supply the actual occurrence span.
- H3: Rulespec's existing projection parser already covers the useful gains. Prediction: it matches RefSpec's correct additional families without extra false matches; if so, duplication/consolidation matters more than adding a dependency.
H1 and H2 can both hold. No test here decides the best ownership boundary or downstream LLM accuracy.

Arms (one deterministic pass each):
A. Current experiment: RefSpec find_cfr_citations plus SpicySearch strict CFR/USC readers.
B. RefSpec bundle: parse_authority_citation, detect_identifier_shapes, parse_federal_register_citations, parse_eo_compilation_locators, find_act_relative_citations.
C. SpicySearch detect_identifiers, using its unchanged query defaults.
D. Rulespec projection readers: parse_cfr_citation, parse_authority_citation, find_act_relative_citations.
The bundles are assessed as bundles. Raw output is retained per function; no gains attributed causally to one bundled component.

Cases: Freeze a maximum of 36 cases before running any arm: actual saved source passages from the preceding experiment; original truncation failures; selected additional-family examples; malformed, ordinary-prose, ambiguous-number and unknown-name controls. Constructed examples are explicitly labeled and are not an independent corpus benchmark. Expected type/identity is a revisable manual label, not proof of legal validity. Act-name tests use the same small declared name set in both arms, not a production roster.

Held constant: Exact source strings, supplied act-name set, caller context, local checkout/package versions, and manual outcome criteria. No model/API/network calls. Temperature/thinking settings not applicable. One pass plus one exact replay; repeated calls establish replayability, not generalization. Stop after these cases or 25 minutes; no parser fixes or tuning in this iteration. Reuse the existing reference-tool capture style and installed environments; use direct imports only for the local Rulespec module when no installed copy is available, and log the actual import location.

Measures: Distinct expected references recovered, misleading/wrong references, duplicates, missed cases, supplied original occurrence spans (separate from full-input provenance), explicit refusal/partial status, and reference/context requirements. Manually read every case's raw outputs. A `partial` status alone is not a false positive: a complete reference inside prose can be partial at whole-input level. Repeated output for one identity is not extra recall. No latency or general accuracy rate claim.

Decision rule: Recommend a bounded next integration only if it adds correct references in at least three additional families, preserves baseline successes, introduces no false identities on the negative controls, and supplies exact verifiable occurrence spans for additions. If coverage improves but the safety/evidence gate fails, report a tradeoff and name the needed adapter or narrower follow-up; do not call the broader gate passed. If D matches useful B gains with no added errors, prioritize comparing/consolidating the existing implementations. No production adoption is authorized by this experiment.

## Execution correction before collecting parser outputs

The first invocation stopped before parser calls because the runner applied
SpicySearch's load threshold to this Rulespec experiment. That repository's
measurement policy was imported too broadly: this work lives in Rulespec and
measures deterministic recognition/evidence, with no timing claim. Remove the
load refusal and use an experiment-local exclusive lock; continue recording host
load. Inputs, labels, arms and decision thresholds are unchanged. The initial
refusal remains recorded in this note; no output observation was discarded.

## Assessment-writer correction

The initial assessment writer omitted appending completed rows, producing an
empty assessment and therefore empty counts. Both invalid files are retained
as `*.invalid-empty.json`. Add the missing append and require assessment case IDs
and expected labels to match every raw input before counting. No raw parser
output, expected label, or pre-unmasking manual judgment was changed. This is an
instrument correction, not an intervention result. The replay observations stay
unchanged.
