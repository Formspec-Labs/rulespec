# New-source check after passage-ID comparison integration

The integrated workflow completed on two previously untested local evaluation
sources. All 66 comparison judgments resolved to original prepared-source text,
with no inventory or comparison refusals. Direct review found useful preservation
of conditions and alternatives, especially in the nested waste rule. The passport
case still exposes a standalone qualification risk and one withheld component quote.
These are two selected runs, not a general accuracy estimate.

| Result | Passport correspondence | Waste accumulation |
|---|---:|---:|
| Prepared characters | 2,536 | 5,927 |
| Accepted / rejected claims | 16 / 0 | 14 / 0 |
| Inventory observations / substantive units | 16 / 15 | 24 / 21 |
| Accepted comparison judgments | 31 / 31 | 35 / 35 |
| Extraction status | Partial: one component withheld | Complete |
| Component-evidence warnings | 2 | 3 |
| Automated audit | Passed, review complete | Passed, review complete |
| Total reported tokens, all three stages | 32,947 | 71,962 |

Six fresh `gemini-3.8-flash` calls total: low-thinking extraction, medium-thinking
inventory, medium-thinking comparison for each source; temperature zero, no numeric
thinking budget or application output cap, no retries or repairs. The total is
104,909 reported tokens. There is no fresh quote-based control or repeated run per
source, so these results do not establish comparative cost/quality improvement.

## What the raw review found

- Passport approval authorities, extenuating-circumstances exceptions, adjudication
  sequence and both no-response/no-personalization exemptions survive.
- The passport duty to use cleared wording and permission to adapt it are separate
  claims. The complete collection preserves both; the duty alone lacks the
  qualification. The audit accepts the split. This is a standalone-use risk,
  rather than demonstrated loss everywhere or an explicit false prohibition.
- Waste closure exceptions, necessary venting with both reasons, both required
  label components, three-day timing and every disposal destination survive in
  complete statements. Comparison cites the relevant governing passages as well
  as individual branches.
- A passport modality quote `no ... may be made` is correctly withheld because it
  is not contiguous source text. Repeated short modality quotations cause other
  component warnings. Passing comparison does not clear those extraction issues.
- Cross-references remain textually preserved. Three local citation records in the
  waste case still lack resolved graph targets, alongside references to outside
  rules. Typed actors/thresholds remain in prose on this lean path, so this is not
  an executable decision model.

See the complete [source review](source-review.md), the frozen [plan](PLAN.md),
actual [metrics](metrics.json), and the
[next condition-preservation task](../../../thoughts/plans/2026-09-09-preserve-standalone-qualifications.md).
No transfer case was repaired or used to tune the runtime during this check.

## Sources and preparation

The passport source is the complete introduction section of
[8 FAM 801.2](https://fam.state.gov/fam/08fam/08fam080102.html), concerning information
request letters and information notices. It is not the entire subchapter. The
second source is the complete
[Ohio rule 3745-52-15](https://codes.ohio.gov/ohio-administrative-code/rule-3745-52-15).
Original HTML is retained. `prepare.py` deterministically selects the declared
section/rule, extracts paragraphs, collapses layout whitespace within paragraphs,
and preserves list markers/order. All evidence offsets address the resulting
pinned text, not HTML byte positions. Raw and prepared hashes are in `design.json`.
An earlier GovInfo request returned an HTML error page; it is retained separately
and was never supplied to a model. Newness was checked against saved source/document
experiment files, not every past conversation or model training data.

## Verification and reproduction

Both complete extraction/audit workflows replay identically from saved captures,
including discovery export. Each selected evidence span exactly equals its pinned
source slice. The integration passed 356 package/schema tests and native CUE drift
verification before these calls. All raw responses ended with STOP; no retries or
additional provider calls were needed for replay.

From repository root (each replay output must be new and outside the input):

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/passage-id-transfer/run.py passport replay --output /tmp/rulespec-passport-replay
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/passage-id-transfer/run.py waste replay --output /tmp/rulespec-waste-replay
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/passage-id-transfer/measure.py replay
```

Production integration is commit `83caace`; pre-integration research/runtime is
`68de277`. The experiment freezes its inputs and runtime and refuses drift. Source
coverage and model judgments remain distinct: `passed` does not mean every meaning
was independently verified. No additional matcher, profile tuning, workflow repair,
UI work or deployment was introduced by this transfer evaluation.
