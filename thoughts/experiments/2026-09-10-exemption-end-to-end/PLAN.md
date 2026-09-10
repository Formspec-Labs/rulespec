# Fresh extraction through refinement and review

Decision: does the current full workflow deliver useful, source-faithful links on
fresh model-extracted drafts, enough to justify broader evaluation?

Comparison: each original low-thinking extraction versus that same draft after
the existing `refine_run` workflow (initial audit, recovery/challenge,
relationships/challenge, review edits and final audit). This is a before/after
workflow comparison, not a causal isolation of the exemption-link change.
No constructed claims or hand repairs are fed to any model.

Hypothesis: existing extraction finds enough exemption meaning for relationship
proposals to connect it correctly; challenge and review retain those links without
changing modal force, scope or independent duties. Alternatives: exemptions are
missing upstream; grouped meanings make the relationship unnecessary or ambiguous;
proposal guidance still misses links; challenge rejects good links or approves bad
ones; later edits invalidate a previously correct target.

Sources: full official 2025 CFR 49 sections 392.5 (alcohol) and 392.10 (railroad
crossings), previously unused in this sequence. These transport regulations differ
from the OSHA development cases. XML, extracted text and URL are preserved. All
source expectations below are frozen before extraction and are revisable engineering
judgments, not authoritative legal advice.

Expected source scenarios:

1. Manifested alcohol shipments are excluded from the possession prohibition.
2. Alcohol possessed or used by bus passengers has the same limited exclusion.
3. Requesting review changes the State-report deadline to 30 days after affirmation;
   it does not remove reporting or change the separate 24-hour employer-report duty.
4. The five no-stop situations in 392.10(b) must be retained: business-district
   streetcar/industrial-switching crossings; police/flagman direction; locally
   permitted green signal; marked abandoned crossing; marked exempt spur/industrial
   crossing. Each modifies the stop requirement, with its complete conditions.

Counterexamples and completeness checks: possession exclusions do not permit the
driver to drink or operate under influence; review does not excuse the employer
report; stopping exclusions do not authorize gear shifts or remove consent for
Exempt signs. Preserve four-hour/24-hour/30-day/10-day distinctions, 15–50 foot
stopping distance, vehicle scope and independently sufficient categories. Do not
treat a link to a grouped baseline as cancellation of every component. An exact
target may legitimately be grouped if modifier wording restricts its effect.

Primary measures: manually assessed source-faithful statement meaning before/after;
explicit correct links for separately represented qualifications; missed scenarios;
wrong targets or scope; preservation through challenge and review. A faithful
grouped statement may be a semantic success without an explicit edge. Absence of a
separate exemption is not automatically an error if complete meaning is retained.
Count API/schema/evidence failures, rejected proposals, stale links and duplication
separately. Read source, raw extraction, proposal, challenge and final consumer
output; do not accept the model audit as reference truth.

Held constant: current local runtime and canonical CUE-derived schemas; Gemini
3.8 Flash, temperature 0, one run per document, one source window. Use normal
settings: extraction low thinking / 16384 output tokens, audit medium / 32768,
refinement and challenge provider-default thinking / 32768. This differs from the
prior experiment's explicit medium relationship setting; do not attribute a change
in results to that setting. No retries, prompt tuning or automatic deployment.

Bound: at most 18 provider attempts (nine per full path), 1800 seconds before
starting any next call. Optional challenges may reduce the count. An in-flight
call may finish after the bound. Original extraction stays immutable; review edits
occur only in copies under this experiment. Replay must reconstruct the captures
without provider calls. No user workspace or production code changes.

Decision rule: bounded success only if every expected scenario remains faithfully
represented, no unsupported relaxation is introduced, and any proposed correct
links survive application without semantic regression. Report link-only gains
separately from improved default statements. If an expected scenario fails, record
the exact responsible layer and stop; do not patch or rerun the document. Any
remaining partial result fails the broad gate despite narrower gains. These two
selected documents cannot establish a general accuracy rate.
