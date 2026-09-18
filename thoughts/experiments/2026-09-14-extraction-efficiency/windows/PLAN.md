# Bounded section grouping

Decision: should a small contiguous-section grouping option advance to a broader quality test as a cheap alternative to one request per section? This experiment authorizes no production edits.

Observed: complete CSBG section mode made 27 calls versus 6 broad calls, captured 13/13 plan contents versus zero independently captured, and used 202,158 versus 129,185 recorded tokens. This does not isolate whether reduced competition or extra output capacity produced the gain. Tiny section requests still consume 3,000+ input tokens.

Hypothesis: grouping adjacent short sections can preserve their separately referenceable meanings while amortizing fixed prompt/schema/example/index cost. Contrary predictions: cross-section force or scope leaks; monitoring lists are compressed; timing and eligibility details disappear. A competing explanation is that more output budget per section drives accuracy; this experiment tests a bounded scheduling bundle, not hidden model reasoning.

Arms: A makes two fresh normal section requests for 42 USC 9913 and 9914. B makes one fresh request whose focus is their exact contiguous union. Both use current production prompt, generated schema, examples, catalog, decoding, and context assembly. All original section IDs and full chapter index remain supplied. The union changes window size and F labels, not the source contents or output shape. Process order A9913, B, A9914 is fixed before calls. No retry or best-of selection.

Cases and criteria, reviewed directly from the pinned source before calls:
1. 9913 reserved funds retain every listed activity, corrective-action/monitoring purpose, reporting/data collection, and distribution under (c).
2. 9913 grants/contracts/cooperative agreements remain permission and apply only to (a)(1)(A).
3. Training determination addresses eligible entity/program needs including financial-management quality, to maximum extent feasible.
4. Local-needs responsiveness retains ongoing input from national and State networks.
5. Distribution remains direct, retains 9903(b)(2)(A), recipient restriction, program-quality/financial-management, management-information/reporting, program-results, and local-needs purposes.
6. Recipient eligibility retains demonstrated training expertise and low-income families/communities.
7. Monitoring preserves full onsite review each 3-year period.
8. New entity review occurs immediately after its first funding year completes.
9. Followup retains prompt return visits and failed goals/standards/requirements.
10. Other reviews are as appropriate and include other grants terminated for cause, excluding this chapter's assistance.
11. State may request training/technical assistance as needed; no invented duty.
12. Secretary evaluations occur in several States each fiscal year, include investigations, preserve compliance focus including 9908(b).
13. Secretary report to each evaluated State preserves findings/recommendations and benefits to people in need; State response plan is triggered by receipt.
14. Annual congressional submission retains both recipients and section 9917(b)(2).
Counterexamples: permission must not become obligation; historical committee-name note must not become a fresh monitoring duty; requirements from 9913 must not inherit 9914's State actor or timing. Known difficult 9908 remains intact and alone in whole-document scheduling simulations; no claim that these calls repair its known omissions. These are selected development cases, not an independent benchmark.

Held constant: pinned full CSBG source, installed current runtime, gemini-3.8-flash, low thinking, provider-managed sampling (no temperature/top_p/top_k), 16,384 output tokens, no model audit/refinement. At most 3 calls, 5-minute provider timeout each, 15 minutes total. One observation per arm/case. Raw failures count. No billable-price inference from token counts.

Decision rule: advance bounded grouping only if it reduces calls/input tokens and preserves all critical details the contemporaneous separate control preserves, with no new material force/scope errors. Both arms failing a criterion is a remaining defect. Any semantic regression blocks adoption; lower cost alone is not a pass. Record native decode/refusals, raw response finish/usage/time, manual criterion judgments, exact replay, and coverage independently. Whole-document grouping is static simulation only.

Prior work consulted: 2026-09-13-csbg-retest PLAN/RESULTS, 2026-09-12-csbg-audit RESULTS, 2026-09-13-model-input-improvements plan, current planner/request code. Existing section mode deliberately forces every section start and retains preambles/notes; no existing adaptive grouping implementation was found in these entry points.
