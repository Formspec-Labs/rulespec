# Integrated context: useful answers, failed promotion gate

The delivered reference/source work helps a fixed-question task recover meaning that its small context cannot supply. Three of four natural cases gained complete, source-grounded additional answers. The broader promotion gate **failed**: the seatbelt answer introduced an unsupported actor restriction, and integrated requests used 2.145× baseline reported tokens against the 2× limit. No automatic context-check pass or meaning correction is adopted.

## What was tested

Twelve contemporaneous requests: six fixed cases × current context (A) or integrated context (B), alternating AB/BA. Gemini `gemini-3.8-flash`, temperature 0, low thinking, no thinking budget, maximum output 32,768, one candidate. The exact requests verified these settings. All calls returned complete responses; none were retried. This measures a selected question-answer task, not extraction accuracy or fresh-document generalization. Questions often name the missing concept; it does not show automatic omission discovery.

The bundle adds short enclosing sections, one-hop located references, existing source metadata and relevant recorded feedback. Its result cannot distinguish the contribution of those components or larger input size. Each source uses its own passage catalog and existing resolver.

## Manual source review

| Case | A | B | Assessment |
| --- | --- | --- | --- |
| Refrigerant | Abstains on de-minimis routes and independent servicing duties; retains substitute exemption | States both compliance routes, applicable components, exempt-substitute qualification, and separate servicing/equipment requirements | Additional grounded meaning on questions 1 and 2 |
| Seatbelt | Recognizes use rather than manufacturing and does not invent a manufacturer; two selected ranges cross unsupplied text, so the cell is refused | Adds aircraft/use/operator context, but question 3 calls the accompanying person an **“authorized adult”** | Partial benefit with actor regression: source permits parent, guardian, or designated attendant without stating adulthood; question 1 also describes the §91.105 exclusion too broadly as the whole section rather than paragraph (a)(3) |
| State agency | Knows the definition points to §49c but cannot supply designation authority or powers | Supplies Governor designation/authorization, State-statute condition, cooperation powers, and retains §49l–2 exception | Additional grounded meaning on question 1; no duty transferred to local offices |
| External good cause | Abstains because target text is unavailable | Supplies good-cause finding, incorporation of finding and brief reasons, all three alternative grounds, and separate-statute limitation | Additional grounded meaning on questions 1 and 2; governing edition remains unestablished |
| Constructed visitor/staff | No transferred staff duties; laboratory permission unknown; closing time retained | Same results | No semantic gain expected; noninheritance control passes |
| Constructed competing editions/feedback | Abstains from selecting a version but sometimes answers about the 2020 rule rather than the statutory target | Correctly identifies ambiguous statutory targets, declines blanket-waiver feedback, and acknowledges unavailable body | Control passes; clearly labeled adversarial feedback makes this an easy control, not evidence against arbitrary injection |

These are revisable, unblinded assistant judgments against preregistered source labels. This is a limitation relative to blinded comparative scoring. The assessment reads the raw answers, including the refused A seatbelt payload; it does not credit a valid JSON shape or a citation by itself as faithful meaning. The natural external case uses a real primary document and a declared constructed target wrapper. Controls are constructed.

All source references in B resolve. A seatbelt fails because its range would include unsupplied intervening content, demonstrating an evidence-boundary refusal rather than permission to widen the resolver. The saved `decoded.json` retains that raw payload. No response was silently repaired. “Unknown” about absent context is an appropriate abstention, not an extraction defect.

## Usage and gate

| Arm | Input tokens | Answer tokens | Reported total | Mean total per case |
| --- | ---: | ---: | ---: | ---: |
| A | 12,854 | 1,963 | 14,817 | 2,469.5 |
| B | 29,194 | 2,590 | 31,784 | 5,297.3 |

Total experiment: 46,601 reported tokens over 12 calls. All responses contain usage; none reports a separate thinking count, so none is inferred. The B/A total ratio is 2.1451 (+114.5%). These are stage costs, not whole-document costs or dollar invoices.

The ≥2 natural-case gain gate passes (3/4); the source-resolution and negative-control gates pass for B. The no-critical-regression gate fails on actor/scope specificity, and the cost gate fails. The overall gate fails. Previous broad-extraction failures remain unchanged.

## Implementation decision

Connect the deterministic **evidence assembly/export** to the application as navigation and caller-supplied context. This is a separate, narrower delivery decision, justified by 170 grounded input passages, source isolation, duplicate-target accounting, source/installed parity, recorded budget/refusal states and feedback reload checks. It does not promote the failed model workflow or claim better production extraction.

Keep the live fixed-question check, questions, response schema and judgments experimental. Existing review observations and preview/revision-checked meaning edits remain the route for a future demonstrated correction; no existing claim, approval or review history is changed here. Per-target subset application (R25) remains a separate experiment.

The next unresolved question is whether an explicit review task can preserve exact actor/scope limits without paying for unrelated notes and duplicated provenance descriptions. Do not infer that simply stripping metadata or narrowing sections preserves these results: no such follow-up was run. No more provider calls or prompt tuning are needed to decide this comparison.

## Reproduction

`design.json` pins cases, labels, adapter, harness, schema, prompts and runtime bytes. `inputs/` and `cells/` retain source catalogs, scans, exact requests, responses and refusals. `preflight.json` records mechanical checks. `replay.json` confirms all twelve decoded results matched with zero provider calls before production changes. `preflight-01/` retains the mistaken TOC selection; `preflight-02/` retains capture bookkeeping fixes and the corrected assumption that changing visible publication metadata preserves prepared offsets. Neither preflight made a provider call.

Run the experimental harness with its recorded runtime; it deliberately refuses drift. Production evidence export has its own parity and integration tests; those do not replace this saved experiment or its failed gate.
