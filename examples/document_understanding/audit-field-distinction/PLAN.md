# Can the existing audit distinguish wording loss from retained logic?

Decision: Can current audit instructions reliably identify where the known notice
qualification survives, without falsely rejecting a complete constructed statement?

Hypothesis: the current audit will flag incomplete summaries in A and B, explain
that B retains all governing conditions in logic, identify A's missing
unforeseeability lead-in, and accept C's complete statement. If it gives the same
undifferentiated omission rationale to A/B, or rejects C without a source-backed
reason, the field distinction is not reliable on this case.

Arms are controlled draft inputs, not different prompts:
- A: original saved C0014, whose summary and scope lack the qualifications. Its
  logic and main quote include unusual circumstances/emergency exceptions but
  lack the unforeseeability lead-in. This is the actual historical failure.
- B: A with the main source selection and logic extended to exact F003:F004,
  including corresponding evidence offsets. Summary and scope stay unchanged.
  This deliberately changes a source-selection bundle, not only a string.
- C: B with only its summary replaced by a constructed full statement preserving
  unforeseeability, unusual circumstances, and the emergency exemption until
  stabilization AND access AND ability to use a phone. Scope remains empty; the
  audit already permits complete prose without redundant structured enrichment.

Use the entire saved source, all 18 draft claims and all 18 substantive inventory
units from comparison-passage-ids/fixture.json. Keep all other claim content fixed.
Inventory is a frozen fallible model observation, not gold. The constructed
statement expresses the prior standalone-use criterion; it is not legal authority.
The unchanged correct emergency exemption and first/subsequent-notice alternatives
are additional counterexamples against overcorrection. This is development data.

Store the original fixture unchanged. Experimental draft views contain document
and claim data only; give the changed target a distinct experimental identity,
and keep their provenance outside model-facing input. Do not fabricate provider
captures, mutate original Core graphs, write approval/history, or derive new Core
Findings for the constructed views. Reuse current comparison input generation,
provider capture, judgment parsing and evaluation accounting. Only the draft
target source-selection/wording varies; no runtime/schema/prompt patches.

Held constant: gemini-3.8-flash, temperature 0, medium thinking, no numeric thinking
budget or application output cap, one full-source window, same current CUE-derived
field guidance/schema and comparison prompt. Two repeats per arm, six comparison
calls maximum; no new inventory/extraction, retry, repair or tuning. Randomize cell
order before calls. Existing five-minute request timeout. Save actual request
bodies, raw responses, failures and all derived judgments. Replays make no calls.

Primary review criteria, fixed before calls:
1. A and B: summary verdict error with a substantive reason identifying missing
   governing qualifications; scope may be error in A, or correct/error with an
   explicit field-based explanation in B. Do not pre-judge that ambiguous dimension.
2. A rationale: distinguish missing unforeseeability from the unusual/emergency
   qualifications retained in logic; do not claim all qualifications are absent.
3. B rationale: explicitly identify complete qualifications retained in logic and
   incomplete summary/scope. Merely saying a quote contains them does not meet
   the instructed distinction between evidence and explicit logic_text.
4. C: summary correct and no invented omission of these qualifications; an actual
   source-backed error in the constructed wording counts against this criterion
   and triggers reconsideration of that label, not dismissal of the auditor.
5. Preserve the emergency exemption's three prerequisites and first/subsequent
   notice alternatives in the audit's treatment of unchanged claims C0007/8/15.

Mechanics: account separately for complete reciprocal judgments, valid exact
passage evidence, model semantic verdicts, rationale quality and global report
status. Other known ambiguous modality labels may make the global report fail;
do not treat that as failure of the target distinction. Review every target and
the unchanged controls, and inspect additional reported errors against source.

Decision rule: all primary criteria must hold in both repeats for bounded support
that the existing audit can make this distinction on this document. Mixed outcomes
mean unreliable or unresolved, not general success. Any result changes the next
decision about using existing audit signals; no automatic production change is
authorized. Mask/randomize raw audit outputs for initial self-review, then unmask
and compare to the exact inputs. The same agent knows the design, so describe the
masking limitation. Stop after six calls and save the decision; no prompt patching.
