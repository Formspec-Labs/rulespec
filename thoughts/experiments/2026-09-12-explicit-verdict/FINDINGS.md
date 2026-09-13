# Explicit definitions and quote boundaries did not improve detection

Four fresh calls compared the preceding composed narrative with the saved
explicit definitions and `###` / `"""` layout. Both arms returned exactly the
same 21 boolean verdicts. The predeclared gate for fresh-document evaluation
failed. Production remains unchanged.

| Measure | A: preceding narrative | B: explicit definitions and layout |
|---|---:|---:|
| Clear omissions detected | 0/3 | 0/3 |
| False alarms on previously faithful items | 0/17 | 0/17 |
| Previously uncertain items flagged | 1/1 | 1/1 |
| Valid decisions | 21/21 | 21/21 |
| Input tokens | 37,702 | 49,068 |
| Output tokens | 152 | 167 |
| Total tokens | 37,854 | 49,235 |

B used 30.15% more input tokens. The four calls used 87,089 reported tokens and
7.60 seconds, with no retries. The final call crossed the 75,000-token bound as
permitted by the predeclared check-before-each-call rule. All calls finished
with STOP; there were no decode issues or discarded responses.

## What was actually tested

A's prompt exactly matches the saved previous composed request for each source.
B adds the specification's complete instruction block and renders literal item
headings, real line breaks, standalone triple-double-quote delimiters, and
explicitly named actor/kind/modality values. Every item's full supplied source,
unchanged statement, populated fields, and proposed terms remain represented.
The worked example and its expected answer are excluded from requests.

This tests definitions, task clarification, and formatting as a bundle. It does
not isolate delimiter choice from other changes, test automatic selection of
governing snippets, or establish a benefit from repeating full source.

Actual requests: B [LEA](prompts/cell-00.txt) and [IEP](prompts/cell-01.txt);
A [LEA](prompts/cell-02.txt) and [IEP](prompts/cell-03.txt).
Raw SDK requests, responses and readable answers are under `captures/`.

## Raw review

I read every returned verdict and both negative explanations, and rechecked the
known omissions against the source and unchanged extracted statements.

- Both arms approve IEP R000, whose long definition omits the explicit
  “including courses of study” detail in F025.
- Both approve IEP R004 without the requirement for the parent's agreement to be
  in writing. F053 supplies that requirement and appears inside the same item
  narrative as F045/F046. Availability and explicit completeness instructions
  did not make the checker catch the omission.
- Both approve IEP R005 without written parental consent. Its retained member's
  written input is a separate requirement. The source supplies both, but the
  statement preserves only the latter writing requirement.
- Both reject IEP R006's assignment of “parent” as actor. B says the requirement
  impersonally governs the agreement's form instead of imposing an action solely
  on the parent. This remains a disputed component interpretation. It is not
  detection of the original unresolved-clause-reference concern, and it does not
  count as detecting any of the three clear omissions. The original uncertain
  label is preserved rather than revised to reward the checker.
- Both approve all 13 previously faithful LEA items and the four faithful IEP
  controls. These controls catch overcorrection; their approval does not establish
  that this pass can discover missing content.

The revised actor explanation is more semantic than the prior grammatical-subject
objection, but that wording change did not improve the measured decisions.

## Verification and decision

Preparation checked exact quotations, standalone delimiters, heading spacing,
preservation of supplied source and populated fields, and exact control equality.
After capture, actual SDK contents/config matched the prepared requests and the
42 decisions replayed with provider creation blocked. `precall-pins.json` retains
hashes of the exact specification, adapter, reused harnesses, runtime, source,
fixed records and labels. `assessment.json` records individual verdicts and the
failed decision gate.

No measured quality improvement on these selected development cases. This weakens
the hypothesis that undefined field terminology or ambiguous quotation boundaries
alone explain the failures. It does not prove the model's internal cause or that
explicit formatting is useless elsewhere. One call per arm/document does not
measure within-case variability or generalization.

Stop this prompt iteration. Do not add the longer instructions to production as
an accuracy improvement. The remaining problem is detecting omitted meaning;
another formatting change needs a distinct, observable hypothesis rather than
being treated as an established fix.
