# Explicit applicability contrast in the existing audit rationale

Decision: whether a requirement to state an applicability counterexample improves
audit defect detection enough to justify a broader trial. No production adoption.

Hypothesis: the broad audit instruction already mentions counterexamples, but
requiring an observable contrast in each rationale will catch additional lost
conditions. A tie, false alarms, missing contrasts, or other-dimension regression
weakens the case. Alternative explanations: the existing instruction already
suffices; the inventory omits dependencies; requiring contrasts encourages
invented restrictions. This test compares observable output, not hidden reasoning.

Arms: A = current audit._comparison_request. B = identical request, with an extra
instruction to start the existing rationale with an explicit source-versus-draft
applicability contrast, or say no supported contrast was found. No new field,
schema change, source change, reduced dimension set or repair pass.

Sources: official govinfo 2025 XML snapshots of 29 CFR 1910.38 (full section),
29 CFR 1910.157 (contiguous subsection (a) through (d) excerpt), and the exact saved
14 CFR 91.107 seatbelt capture. Raw XML, extracted full text, selected text, URLs
and hashes are retained. XML P/SECTNO/SUBJECT elements use itertext; paragraphs
are joined with blank lines. No editorial corrections to government wording.
The extinguisher excerpt excludes (e) onward; outside references stay unresolved.
Search of saved thoughts/example Markdown and source text found no previous use
of 1910.38 or 1910.157. They are fresh to this experiment history, not an independent
benchmark. 91.211 was considered and rejected because earlier experiments used it.

Fresh-source claims are four hand-authored diagnostic claims per source, compiled
through existing Core code, not provider extractions. Preserve both faithful
source readings and planted edits. Labels below are revisable agent judgments:

Emergency plan:
- E0 error: "An employer must have an emergency action plan" drops the trigger
  that an OSHA standard in this part requires one.
- E1 error: a universal written-plan duty loses the <=10-employee oral option.
- E2 valid: the <=10-employee oral permission retains the section's required-plan
  scope. This exception must not spread to alarm/training requirements.
- E3 valid: under the required-plan scope, employer designates and trains employees
  to assist evacuation. The <=10 oral-plan exception does not remove this duty.

Extinguishers:
- F0 error: Class A distribution <=75 feet drops the (a)/(b) limits on paragraph
  (d), including outside extinguishers and designated-user evacuation plans.
- F1 error: placement/operability duty says at all times and omits except during
  use. This claim retains a scope clause excluding the (a)/(b)(1) exemptions.
- F2 valid: (b)(2) exemption retains all plan/designated-user/evacuation conditions
  and exempts only distribution (d). It must not remove general requirements (c).
- F3 valid: (a)'s outside-building exemption applies only to paragraph (d), not
  every requirement in the section. Treat as an exemption statement.

Seatbelts: unchanged full paragraph-catalog rulebook, all 17 claims. Primary known
failure is the initial pilot takeoff duty omitting remote part 121/125/135
exclusions. Manually inspect other verdict differences rather than presume all
remaining claims are correct. This is development evidence, separately reported.

Protocol: build one source-first inventory per document through existing capture
code before any comparison sees the draft. Freeze it and use the same inventory
in both arms, retaining omissions/refusals. Freeze all claims before calls. Both
arms see the same whole selected document and all inventory units. Inventory
coverage can exceed the intentionally partial constructed drafts; missing units
are not counted as audit false alarms on the four selected claims.

Settings: gemini-3.8-flash, medium thinking, temperature 0, 32768 output tokens,
24000-character single window, one call per cell. Nine calls maximum: three
inventories plus six comparisons. Randomized comparison order, seed 20260910.
No retries; stop after nine calls or 20 minutes elapsed provider-stage work.
Check bound before each call, retain any in-flight completion. Record actual
request bodies, model versions and settings. One run per cell does not establish
stability. Credential setup uses the previously authorized spicy-regs environment
file through the existing credential helper; never retain credentials.

Assess separately: processing/schema/grounding; adherence to explicit contrast;
scope/summary detection with correct reason; false-positive controls; other-field
regressions; output/input/total tokens, elapsed time and missing usage. A generic
error verdict with the wrong reason does not count as detecting the planted error.
Do not count coverage failure caused by a partial constructed draft as a failed
audit execution. Review every raw comparison judgment and its selected evidence.
Randomize opaque cell order for first review before reading the arm map, while
acknowledging that the contrast format can reveal the arm. Agent labels are not gold.

Decision rule retained from the proposal: advance only if B complies and catches
at least one additional confirmed scope/summary defect on EACH fresh document,
with no new material false positives or other-dimension regressions. Otherwise
retain A and report tie/tradeoff/regression/unresolved as appropriate. A familiar
seatbelt improvement cannot rescue a failed fresh-source gate. Report all cells,
including failures, and do not patch the prompt after seeing results.

Stop after manual review and replay; production remains unchanged.

Source acquisition: web reader could not open govinfo XML; direct HTTPS download
of the same government URLs succeeded. No provider request occurred during setup.
