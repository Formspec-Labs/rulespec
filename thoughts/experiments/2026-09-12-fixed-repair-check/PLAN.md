# Can the checker recognize a supplied repair?

Decision: distinguish failure to discover/propose a repair from failure to judge
a supplied repair. The preceding recovery comparison returned no proposals in
all four cells; these are historical observations, not a contemporaneous control.

Hypotheses: H1, selection/composition is the main obstacle on these cases: the
existing checker should accept supported fixed repairs and reject wrong ones.
H2, the checker also treats whole-book retention as enough and rejects the
supported changes as duplicates. H3, supplying plausible repairs leads to
indiscriminate approval. Verdicts and source-based rationales distinguish these
outcomes. Success does not reveal the model's internal cause or prove automatic
repair works.

Intervention: use the existing `CHECK`, `CHECK_SCHEMA`, `_challenge_prompt` and
`_decode_checks` without modification. Supply full original source/draft and ten
constructed edits. Keep rationale neutral and identical; do not provide expected
labels or suggested answers. No navigation change, extra audit or generation
call. Every proposal must receive supported/unsupported/unknown with source refs.

Cases and expected outcomes, fixed before requests:

| Case | Constructed edit to existing default statement | Expected |
|---|---|---|
| I1 | IEP C0004 retains its complete statement and adds that the parent's agreement under this attendance provision must be written | supported |
| I2 | IEP C0005 retains all excusal conditions and adds written parental consent, distinct from member input | supported |
| I3 | C0004 requires both parent and agency agreements to be written | unsupported: source singles out the parent |
| I4 | C0005 states the member's written input satisfies parental written consent | unsupported: distinct requirements |
| I5 | Team-composition C0003 adds written parental consent as a prerequisite for every member's participation | unsupported: wrong target and scope |
| I6 | Transition-invitation C0007 requires written parental consent before the invitation | unsupported: source requires parental request, not this writing prerequisite |
| T1 | Constructed request permission adds the required applicant name and reference number | supported |
| T2 | Request permission becomes conditional on the agency having published annual statistics | unsupported: independent agency duty |
| T3 | Inspection permission inherits electronic-request name/reference-number requirements | unsupported: wrong native branch |
| T4 | Request permission adds an applicant duty to publish annual request statistics | unsupported: wrong duty bearer |

IEP is the actual unchanged saved failing book. The request/inspection source is
the same constructed counterexample used previously, not a fresh real document
or provider extraction. All ten repairs are constructed; labels are source-based
engineering judgments under the declared standalone-statement criterion, not
absolute legal rulings. Unknown or disputed rationales remain visible. Other
unchanged IEP actor/detail disagreements are not silently labeled clean.

Each edit retains its original main quotation, kind, modality and other fields;
it adds the relevant full source sentence as `context_quotes`. Main source
positions and the original separate requirement remain intact. The evidence can
be exact while the added meaning is wrong. All proposals must decode and preview
through the existing mechanical checks before any provider call.

Held constant: gemini-3.8-flash, temperature 0, medium thinking, no numeric thinking
budget, 32,768 output cap. Two batches (six IEP and four constructed candidates),
each sent twice with the candidate order reversed. Randomized opaque proposal
IDs and request order; expected labels stay out of requests. Four calls maximum,
no retries, no new call after 900 elapsed seconds or 120,000 reported tokens.
This measures two presentations of ten candidates, not twenty independent cases.

Decision rule: all six supported-candidate judgments across the repeats must be
supported; all fourteen negative-candidate judgments must be unsupported, with
complete source-grounded output and no contradictory rationale. Unknown, missing
or ungrounded judgments fail the bounded gate and remain separately reported.
Inspect all raw verdicts/rationales. For positive writing findings, source refs
must include the writing clause and affected attendance provision. Explicitly
assess whether each rationale requires evidence absent from its selected refs.

No production edits or review actions. Save requests/responses, fixed proposal
labels, pre-call source/runtime pins, mechanical proof, costs and replay. If the
gate passes, recognition of these supplied repairs is supported; generation and
fresh-document quality remain unproven. Stop at the stated comparison without
patching prompts to make these ten candidates pass.
