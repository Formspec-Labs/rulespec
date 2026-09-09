# Compare explanation fields by the job they perform

Decision: identify whether a particular source-grounded explanation improves its
corresponding extraction decisions enough to warrant follow-up. Do not adopt any
field or production change during this experiment.

Observation: the previous scope_text/choice_text ordering test did not reliably
emit interpretations on the real documents and left the known notice qualification
miss unresolved. It did not test dedicated actor, modality or logic explanations.

Hypotheses: actor explanations may protect responsible-party attribution; modality
explanations may protect permission/prohibition/exemption/recommendation distinctions;
logic explanations may protect AND/OR, exception trees and temporal alternatives;
applicability explanations may protect parent-condition inheritance. Each predicts
a gain in its matching decisions, not a generic benefit from extra output. A field
that merely repeats the statement, is null on the actual difficulty, or adds wrong
interpretation weakens that field's hypothesis. Cross-field effects are secondary.

Five arms: current baseline; actor_explanation; modality_explanation;
logic_explanation; applicability_explanation. Each treatment adds only its one
field before statement, generated through the existing native CUE exporter from
an isolated copy of the canonical profile. The field is required but nullable:
null is appropriate when no interpretive issue exists. Nonempty notes explain a
source-supported decision in at most two concise sentences. Required-slot
adherence and substantive/non-null adherence are scored separately.

The current prompt is identical in all arms. Field-specific instructions live in
schema descriptions. Existing fields/types/order otherwise remain unchanged.
Changes in field name/description/required slot are a deliberate per-field bundle;
this test cannot credit name, length, requiredness or ordering alone. There is no
late-order arm and no common-field aggregate accuracy conclusion.

Cases: the same complete passport introduction, Ohio satellite-waste rule and
29 CFR 825.303 notice source used in saved experiments. Keep real surrounding
context. Baseline calls are fresh, not reused historical output. The historical
notice designated-number example is the actual known miss; nearby correct cases
are equally important controls.

Freeze a field-specific review rubric before calls. Check, at minimum:
- Actor: agencies/centers versus posts, literal you, employee versus employer,
  spokesperson substitution and source-specific generator categories.
- Modality: explicit must/must not/may/not required, factual definitions, the
  generally-should expectation and preserved uncertainty in may-not-be-required.
- Logic: both label components, nested venting exceptions, three-day alternatives
  and every removal destination, passport approval exceptions and no-response rule.
- Applicability: the notice example's unforeseeable-leave and unusual-circumstances
  limits, first-time/repeat notice settings, local adaptations versus other actors,
  and parent exemption/excess-accumulation conditions after splitting waste rules.

Held constant: gemini-3.8-flash, temperature 0, low thinking, 16384 output tokens,
one full source window per case, existing parser/Core checks. Fifteen calls:
one per arm per case, fixed randomized dispatch order, no retries/audit/repairs.
No new source text is fetched. These are reused development cases, not independent
evaluation. One call per cell does not measure repeatability.

Save the original explanation with its row and capture. Validate the trial schema
first, remove only that experimental field for the unchanged production parser,
then preserve both the full model output and deterministic Core result. A note
does not become source evidence or proof of the rule's completeness. No existing
Finding/Attestation record is misused as the extraction's explanation.

Review canonically ordered outputs under opaque randomized run IDs before reading
arm mappings/config/usage. Inspect statements first with explanation fields hidden;
then review notes and compare them to the same source. Explanation names/content
can reveal the treatment during that second review; report this blinding limit.
Labels are revisable Codex judgments, not independent human gold.

Decision rule: assess each field separately. A promising field repairs a reproduced
baseline error or omission on its intended dimension, keeps named controls intact,
and supplies a supported explanation. Count unchanged, regressed, non-adherent and
uncertain cases. A correct note with an incomplete statement is not a repair.
Compare actual input/output tokens per source; do not infer reasoning quality from
length or order compliance. If no relevant baseline error reproduces, report the
quality ceiling instead of claiming an improvement. Stop after fifteen calls;
retain all captures, review decisions and zero-provider replay evidence.
