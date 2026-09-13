# Complete-reading checker diagnostic — preregistered

Decision: verify the API/input fixes M2/M3 and decide whether M4's shared task and
assessment of no-change decisions can serve the next repair experiment. Keep M4
experimental; this does not authorize a new default pass or establish accuracy
on fresh documents. No generation comparison in this diagnostic.

Hypotheses:
- Application identifiers were causing a spurious objection. With aliases, the
  saved cell 6 exemption's action/object error should still be rejected; a matched
  control clearing only those optional components should lose that objection.
- Repair/check task disagreement contributes to accepted enrichment and ignored
  omissions. A checker given TASK.txt and all selected decisions should accept
  needed complete readings and correct no-ops while rejecting incomplete no-ops,
  optional enrichment without repair, and wrong-target/wrong-meaning controls.
- Alternatively, the explicit task will not reliably overcome these mistakes.

Arms: A is the current production checker after M2/M3, examining edits only.
B uses the same source, aliases, fields and CUE-derived evidence/verdict schema,
with TASK.txt and explicit edit/no-change decisions. This deliberately tests the
M4 bundle; it cannot attribute improvement to task wording versus added coverage.
Unchanged targets in A are unassessed, not false positives or correct rejections.
Both arms use Gemini 3.8 Flash, medium thinking, 32768 output tokens, no sampling
parameters, no automatic retries. Two repetitions, randomized order and anonymous
cell labels. No claims of independent blinded human review.

Cases (development data, not fresh generalization evidence):
- Saved cell 1 pension repair, plus a constructed wrong-year variant.
- Saved cell 6 notice exemption with its real action/object error; a constructed
  complete exemption explaining advance notice and surviving at-filing duty;
  a wrong-target variant linking that exemption to the surviving duty; unchanged
  notice C0000 missing the incoming exception.
- Constructed complete electronic request meaning with required name/reference
  number, saved incomplete request enrichment, unchanged incomplete request,
  unchanged complete inspection, saved unnecessary inspection enrichment, and a
  wrong-actor variant assigning agency reporting to applicants.
- Separate M3 diagnostic: saved cell 6 P0001 and its component-cleared control,
  one fresh call each using the current checker. Raw originals stay unchanged.

Labels: complete means the default reading preserves the governing content
specified in TASK.txt, not merely that the document retains it elsewhere. The
permission/content and exemption/surviving-duty labels reflect this explicit
product criterion; the original isolated quotation is not thereby false.
Wrong-year, wrong-target and transferred-actor controls are clear substantive
errors. Optional inspection enrichment is source-faithful but unnecessary for
this task. Constructed answers are labeled as fixtures, never provider output.

Bounds: 12 M4 calls (3 groups x 2 arms x 2 repeats), 2 M3 calls, 1 extraction smoke;
15 calls total, 160000 recorded tokens, 1200 seconds summed call time. Stop on
exhaustion or a provider error; no retries. Freeze cases, actual prompts, schema,
labels and runtime digests before the first call. Save each request/response.

Decision rule: M3 passes if the real component defect is rejected without an
internal-ID objection and the component-cleared control has no such objection.
M4 is usable for a fresh repair comparison only if B correctly assesses every
case on both repeats with valid evidence, including every no-op and safety
control. Otherwise retain the diagnostic and do not use it as an adoption gate.
Report mechanical validity, task correctness, source fidelity and necessity
separately. A clean API smoke proves compatibility, not extraction completeness.

Reuse production capture, source catalog, decoder and preview APIs. Verify
provider-blocked replay and historical-capture reprocessing; preserve receipts.
