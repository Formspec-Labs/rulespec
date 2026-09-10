# Does exemption linking transfer to fresh source sections?

Decision: whether the minimal exemption-link instruction/schema change merits a
larger live evaluation. This is not authorization to add an automatic model pass.

Hypotheses: (1) the old proposal rules prevent a model from expressing otherwise
correct links; updated rules should yield accepted, meaning-preserving exemption
edits. (2) The model treats prose coverage as sufficient and will still omit edges.
(3) Explicit reuse may reduce duplicate companion statements without improving
target discovery. Raw proposals, decoder results, and omissions distinguish these.

Arms: A uses the HEAD version of relationship instructions, meaning schema and
decoder; B uses the locally updated versions. This deliberate bundle tests the
proposed workflow, not one sentence in isolation. Both use identical current
Core behavior for structural validation; its schema shape is unchanged. Also
decode each capture with both decoders to distinguish output from acceptance.

Cases: two freshly selected official 2025 CFR sections, plus the saved extinguisher
development case. Draft records are constructed and labeled as such, not fresh
extractions. Full 1904.1 tests partial industry exemption versus mandatory incident
reporting and the non-overlapping small-company exemption. A contiguous 1910.119
excerpt through employee participation tests section-wide exclusions over three
duties, with definitions as non-targets. Preserve original XML and selected text.
Extinguishers tests both saved exemptions against distribution versus maintenance.

Expected targets, forbidden targets and their explanations are saved before calls.
They are engineering judgments open to correction, not authoritative legal labels.
Other proposals are reviewed separately; a correct companion condition is not an
error merely because it falls outside the target-exemption score.

Held constant: gemini-3.8-flash, temperature 0, medium thinking, 32768 maximum
output tokens, one sample per arm/case, no audit hints, no retries or tuning.
Randomize six calls using seed 20260912. Stop after six calls or 1200 seconds;
an in-flight request may finish after the time bound. Record actual requests,
usage, refusals, observations and failures. No user extraction or review changes.

Measures: raw correct and wrong target edges; exact target-set recovery per
exemption; accepted meaning-preserving edits; additions duplicating an existing
exemption; refusals; source-supported new qualifications; reported tokens/time.
Review all raw outputs manually against the frozen expectations. Single selected
examples diagnose mechanisms, not general accuracy. They become development data.

Decision rule: investigate further only if B recovers both fresh-case target sets
without incorrect targets and preserves exemption meaning, with more usable links
or less duplication than A. Any wrong link is a failed gate. Partial correct gains
are bounded improvement, not success on the full gate. If B still misses a fresh
case, stop tuning and record whether discovery or expression remains the obstacle.

No model-based outcome judge or subagents are used. Decode replay must match.
Production changes this turn: none; previous exemption-link changes remain local.
