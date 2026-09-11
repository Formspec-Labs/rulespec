# Context-bearing meanings: bounded improvement, incomplete selection

**Existing context helps when it actually includes the needed clause. It does not recover remote qualifications by itself.** Eight fresh comprehension calls compared four fixed statements alone with the same statements plus current deterministic source/evidence context. Nothing changed in production.

The added context resolved four questions that the isolated statement could not settle. It introduced no observed transfer of unrelated parent duties or categorical answer to the disputed aircraft applicability question. But neither arm could answer the actual refrigerant de-minimis questions: the selector never supplied the exception. A larger context-dependency trial is justified; the current bundle is not a demonstrated completeness solution.

## Results against the frozen questions

| Case | Isolated statement A | Statement + context B | Interpretation |
| --- | --- | --- | --- |
| Refrigerant default venting rule | Abstains on de-minimis criteria and separate service duties; preserves default actor/action | Same | Not solved: paragraph (a)(2) and paragraph (b) are absent from both inputs |
| Child-restraint dated labels | Cannot settle general manufacturing versus operational scope | Correctly identifies conditional child-restraint occupancy, rejects general manufacturing mandate | One useful scope clarification; still cannot establish aircraft context because outer aircraft clause was not selected |
| Child-restraint securing duty | Correct operator/action; cannot assess absent notwithstanding phrase; does not settle part 135 | Correct operator/action; explains that notwithstanding retains its own conditions; still does not settle part 135 | One useful qualification clarification; actual notwithstanding/exclusion interaction remains untested because exclusion is absent |
| Constructed visitor permission | Preserves no-permit permission; lacks log/closing details | Keeps staff duties off visitors; resolves log distinction and 18:00 closing time | Two useful answers, no mistaken parent inheritance on this hand-authored control |

These are **four additional source-grounded answers out of sixteen fixed questions**, not four repaired production defects or a general accuracy rate. The model safely abstained where evidence was absent. All 32 answer rows had the requested structure and referenced only supplied IDs. Safe abstention is assessed from the answer text: for example, “no, this material does not establish…” is not a substantive answer that the underlying rule prohibits or permits something.

The label case's specific aircraft question remains unresolved in B. The model explicitly states that the supplied material never mentions aircraft. This correctly avoids using the question's wording or memorized law as evidence. It is useful evidence of restraint, not successful recovery of the full aircraft-use context.

## Raw examples

- Label B: “S000–S002 frame the labeling requirement as a conditional rule ('provided that') for occupying an approved child restraint system.” It separately says aircraft cannot be confirmed from the supplied text. [Raw capture](cells/cell-03/attempt-0000.response.json)
- Refrigerant B: “The supplied material does not mention de-minimis releases or good-faith recovery compliance routes.” The exception exists in the pinned full document but is absent from the selected packet. [Raw capture](cells/cell-00/attempt-0000.response.json)
- Child B: notwithstanding is “expressly qualified by 'provided that', requiring compliance with the subsequent conditions.” It leaves part 135 applicability unknown. [Raw capture](cells/cell-04/attempt-0000.response.json)
- Constructed B: “Signing the laboratory entry log is a requirement imposed on staff, and visitor waiting-room permission is explicitly independent of staff entry conditions.” [Raw capture](cells/cell-07/attempt-0000.response.json)

## Cost and controls

| Reported tokens, four calls per arm | A | B |
| --- | ---: | ---: |
| Input |1,107|2,536|
| Answer |1,367|1,522|
| Thinking |12,478|7,706|
| Total |14,952|11,764|

B sent 2.29 times as many input tokens but reported 21.3% fewer total tokens because thinking tokens were lower. One sample per case, with provider-default thinking, cannot establish a repeatable cost saving or explain the difference causally. Total across all eight calls: 26,716 tokens. There were no retries, unanswered calls, or incomplete responses.

The model was `gemini-3.8-flash`, temperature 0, provider-default thinking, max 32768 output tokens, candidate count 1. Actual request bodies/configurations were captured and checked, not inferred from intended settings. Arm order alternated BA/AB across cases. The same questions, instructions and response schema were used in both arms. Current `refinement._call`, `documents.with_context(2400)`, `extraction.passage_catalog`, and `discovery.verified` were reused. Equal source ranges were shared; overlapping evidence remained visible, so this was not a compression experiment.

## Decision and limits

**Bounded improvement:** supplied context improves some conditional readings and adds available local facts without an observed scope regression on these cases. Proceed, if desired, to a separate dependency-selection experiment. **Not solved:** existing bounded context selection misses important remote clauses and sometimes even the outer actor/action setting. Context-bearing presentation cannot make an omitted clause appear.

This pilot does not justify a production redesign. It uses two repeatedly studied natural documents and one constructed source, one completion per arm/case, same-agent manual assessment, and comprehension questions as a proxy. It measures neither retrieval usefulness nor human review time. Reviewer interpretations remain revisable. In particular, it does not settle the child-restraint notwithstanding/exclusion interpretation and does not establish any new legal rule.

A useful next hypothesis is that source structure plus explicit local-reference dependencies can improve **which context is delivered**, with an observable accounting of unresolved dependencies. Test selection coverage before adding another interpretation pass. Reuse current passage IDs/evidence roles; keep proximity separate from governing scope, and preserve raw source retrieval when a needed dependency is not selected. Include remote siblings, missing outer setting, misleading parents, and unresolvable external references. Do not pad known cases with manually selected answer clauses.

## Reproduction

- [Frozen plan](PLAN.md), [cases and exact source bundles](cases.json), [design hashes](design.json)
- [Source review written before reading answers](SOURCE-REVIEW.md)
- [All answer text](readings.txt), [mechanical checks and token accounting](mechanical-assessment.json)
- [Replay receipt](replay.json): zero provider calls; hashes, actual requests and response decoding matched.

From repository root:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-design-context/experiment.py replay
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-design-context/assess.py
```

Original captures and production records remain unchanged. The experimental scripts and results are local and uncommitted.
