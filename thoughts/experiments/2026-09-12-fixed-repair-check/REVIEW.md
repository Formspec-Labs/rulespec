# Manual source and response review

The reviewer read all twenty verdicts, rationales and resolved quotations against
the original source and the ten fixed edits. Expected labels were preregistered
and withheld from the provider. This is an informed review, not a blind human
assessment; the reviewer knew the cases. Labels remain revisable engineering
judgments about the stated product criterion.

## Results by candidate

Each entry below represents two presentations of the same candidate. Forward and
reverse verdicts agree in every case. Reversal changes proposal presentation,
not source order or IDs; cell 4 returned IDs in numerical order despite receiving
them reversed. This is presentation robustness on these requests, not proof of
determinism or independent case coverage.

| Case | Source-based expected outcome | Both observed verdicts | Manual assessment |
|---|---|---|---|
| I1 | Add the parent's written agreement to the existing attendance exemption | supported | Correct. Both cite the attendance provision F046 and writing rule F053. Main conditions remain intact. |
| I2 | Add written parental consent to excusal, retaining the member's separate written input | supported | Correct. Both cite F048:F050 and F053, covering the excusal conditions and separate writing rule. |
| I3 | Reject extending writing to the agency's agreement | unsupported | Correct. Both explicitly distinguish the parent's writing duty from the agency's agreement. |
| I4 | Reject treating the member's written input as parental written consent | unsupported | Correct verdict in both; the reverse-order explanation adds an unsupported agency-writing obligation. See below. |
| I5 | Reject written consent as a prerequisite for every team member's participation | unsupported | Correct. Both distinguish team composition, F032:F043, from the attendance writing rule, F053. |
| I6 | Reject written consent as a prerequisite to a transition invitation | unsupported | Correct. F056 requires a parent's request; F053 does not impose the proposed writing prerequisite on that invitation. |
| T1 | Include the electronic request's name/reference-number requirement in its independently usable default reading | unsupported | Both acknowledge the source requirement but reject incorporation as duplication of C0001. F000/F001 are relevant and complete. This fails the declared criterion; it is not a claim that the source lacks the requirement. |
| T2 | Reject prior agency publication as a prerequisite to submitting a request | unsupported | Correct. Both cite the request permission and agency reporting duty, F000/F002. |
| T3 | Reject electronic-request content requirements applied to inspection | unsupported | Correct. F001/F003 distinguish requests from inspections. Cell 4 also discusses F000 but omits it from selected refs. |
| T4 | Reject assigning agency reporting to applicants | unsupported | Correct. F000/F002 identify the different duty bearer. |

## A correct verdict can carry a wrong explanation

Cell 2, I4 (`P0005`), says:

> the parent and the local educational agency consenting in writing to excusal

The source requires the parent and agency to consent, but the adjacent writing
rule explicitly specifies the parent's consent. This explanation extends writing
to the agency without source support. The same response correctly rejects that
extension for the attendance-agreement candidate I3; those are different branches,
but both are governed by the same parent-specific writing sentence. Cell 3's I4
explanation preserves the distinction:

> the written consent of the parent (and consent of the agency)

The I4 repair is rightly rejected in both presentations because the member's
input cannot substitute for parental consent. A correct rejection therefore
does not make its whole rationale suitable for reuse as extracted meaning.

## Evidence completeness and task boundaries

All twenty decisions include nonempty, resolvable exact source references; none
was omitted, unknown or rejected by the decoder. All four supported IEP decisions
cite both the affected provision and writing rule, meeting the specific evidence
gate. Negative verdicts have the relevant source provisions for the proposed
change. Exact resolution does not catch the I4 explanatory overstatement.

Cell 4's T3 explanation names F000 while selecting only F001/F003. Those selected
passages support rejecting the inspection prerequisite, but they do not include
every passage the explanation invokes. Record this as incomplete citation of
the rationale, without relabeling the substantively correct rejection.

The constructed source has native branches in the saved document, but the
unchanged checker prompt displays passage text without those native parent IDs.
References to a first or subsequent section in its explanations are inferred
from text order and subject matter. This experiment tests rejection of the wrong
subject's requirement, not the checker performing native-identifier resolution.

The T1 disagreement is partly about record boundaries. The original permission
and content requirement are both faithful, separately retained source meanings.
The declared goal requires the default permission reading to carry its request
content requirement. The checker instead treats those as separate provisions;
cell 4 additionally objects to mixing their modal forces. Preserve this
disagreement rather than calling a source-supported sentence a hallucination or
quietly changing the expected label. Actual IEP repairs also combine different
modal forces and were accepted, so the mere presence of two modalities does not
explain the difference by itself.

No new default behavior, source edit or review action follows from these labels.
These are constructed candidate edits to one saved real extraction and one
constructed source; neither population is a fresh generalization benchmark.
