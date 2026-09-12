# Linked evidence helped; audit missed the preselected gaps

**Decision:** retain extraction plus source-preserving discovery, including its
existing linked-evidence capability, as the main documented path. Linked evidence
showed a bounded improvement; its broader value remains uncertain in this small
sample. Keep audit optional. No prompt, model setting, schema, ranking or
automatic refinement change was adopted. The documentation/CLI cleanup is a
separate delivered usability change, not a measured extraction improvement.

The [plan](PLAN.md), twelve [questions and expectations](questions.json),
[pre-audit review](PRE-AUDIT-REVIEW.md) and its hash were saved before their
respective model calls. All seven requests returned complete JSON responses;
there were no provider retries or incomplete responses. Raw sources, actual
requests/responses, refusals and frozen runtimes remain available.

## Fresh extraction

| Source selection | Accepted statements | Recorded extraction tokens | Capture time |
|---|---:|---:|---:|
| Complete 7 FAM 1453 | 8 | 4,456 | 6.9 s |
| Complete annual 40 CFR 262.15, 2025 edition | 13 | 8,247 | 12.0 s |
| Complete 5 USC 6323 with notes, release 119-102 | 13 | 16,455 | 13.3 s |
| Total | 34 | 29,158 | 32.1 s |

Each selection fit one normal 24,000-character window. Actual requests used the
unchanged low-thinking, temperature-zero extraction configuration and 16,384-token
output cap; no numeric thinking budget was sent. Counts include prompt and
provider-reported generated tokens. Missing individual usage categories remain
unreported, not assumed zero. These are token receipts, not a price estimate.

Manual review of all raw responses found good retention of the manual's historical
versus current powers, and the regulation's thresholds, exceptions, alternatives
and continuing duties. The statutory output retained the operative rules but
left the named standalone-accrual and cautionary-reference gaps described below.
One actor component was withheld for a non-exact capitalized quotation, so the
USLM run is `partial`; the statement survives. Core additionally records four
component-evidence issues for the annual source and three for USLM, separate from
capture refusals. Accepted statements are not a complete-grounding or accuracy score.

The manual and annual sources use separately retained visible-text renditions
created with the existing DocSpec acquisition tools. Annual XML is still unsupported
by the native reader; no production dependency/parser was added. USLM uses the
native source map. [Source receipts](source-receipts.json) distinguish source bytes,
renditions, selected ranges and serialized native XML.

## Discovery: a bounded improvement on a small sample

The existing BM25 diagnostic uses the same top-three source rankings in both arms.
It measures retrieval of all preselected exact source passages, not answer
correctness or a production search service's quality.

| Evidence returned | Fully supported questions | Returned-evidence characters, summed across questions |
|---|---:|---:|
| A: source passages alone | 7/12 | 12,963 |
| B: same hits plus linked statement/scope evidence | 8/12 | 54,884 |
| Summaries-only diagnostic, separate comparison | 7/12 | 17,523 |

All source hit IDs, order and scores match between A and B. B recovers both
purposes limiting temporary container venting (A2), which A's top-three snippets
missed. A4 improves from one to six of seven required passages, but still misses
the continuing compliance/date-label paragraph. M1 misses the current consular
role; U3 misses the definition warning; U4 retrieves historical material without
the current accrual paragraph. Original [hits and evidence](retrieval.json) remain.

**Bounded improvement; predeclared two-gain threshold not met:** one full gain,
one substantial partial gain, no losses. Twelve questions across three selected
sources cannot establish the frequency or size of the benefit on other documents.
The threshold was a rule for a stronger recommendation, not evidence that the
observed gain has no value. Keep the existing linked evidence; do not infer a reason
to remove it from a small sample that showed improvement.

The roughly
4.23× evidence-character total includes repeated evidence/roles across hits; it is
not unique source coverage, a measured latency increase, or billed output tokens.
That payload increase is a tradeoff to measure in a real consumer, not proof that
it outweighs the recovered support. No consumer latency or answer-generation cost
was measured, and no new ranking behavior was introduced.

Interpretation clarification after user review: the original two-gain criterion
remains unchanged and unmet. The result is explicitly a bounded improvement with
uncertain generality, not "no value." The audit result below is a separate question.

## Audit: targeted gaps missed; one different omission found

One failed source (USLM) and one faithful control (annual regulation) received the
existing medium audit with the predeclared 24,000-character window override and
32,768-token output cap. The manual did not need another confirmation pass.
Neither audit changed the draft.

| Preselected check | Observed result |
|---|---|
| U-SCOPE: standalone 20-day accrual lacks the part-time limitation | Missed. C0001 receives `scope: correct`; the checker separately accepts the proration record. |
| U-REFERENCE: 44-day technician rule lacks the supplied caution about section 8401(30) | Missed. The operative claim is accepted without that context. |
| Annual regulation: preserve faithful venting, alternatives, labels and continuing duties | Preserved; no confirmed false alarm. |

The source inventory repeats the same unqualified standalone accrual wording.
This supports an observable shared omission across stages; it does not reveal the
model's hidden cause. The missing proration is a per-statement completeness issue:
the whole book still contains the formula. The missing definition caution is a
workflow-preparation/context issue, not proof the quoted entitlement is invalid.

Audit did identify an additional real omission: the old statutory definition of
officers/employees and substitute postal-worker leave is absent from the draft.
Its inventory names the 1947 act and specified prior provisions. Count this as an
archival source-coverage finding, not a newly verified modern 80-hour entitlement.
Its practical importance is unresolved and it does not satisfy the targeted
consequential-error gate. USLM's audit `failed` status comes from this different
missing unit; it does not mean the intended defects were detected.

Annual audit is `passed`; USLM is `failed`; both have completed their judgment
accounting and retain `semantic_completeness=not_established`. All 26 claim and
29 substantive-unit judgments and both full raw inventories were reviewed.

**No measured improvement on the targeted audit checks.** Added consumption:

| Audit | Additional recorded tokens | Capture time |
|---|---:|---:|
| USLM | 43,478 | 32.2 s |
| Annual regulation | 25,821 | 26.7 s |
| Total | 69,299 | 58.9 s |

The complete batch used **98,457 recorded tokens, seven model requests and about
91 seconds of capture time**, excluding source preparation and manual review.
No stopping bound was exceeded. This selected set has one observation per source;
it does not establish reproducibility or a general error/detection rate.

## Review, bloat and verification

The [reviewed preparation outline](REVIEWED-OUTLINE.md) reuses the accrual and
proration records, attaching the part-time branch before presenting a usable
calculation. One substantive assembly correction is required for that narrow
outline; referenced eligibility definitions and administrative roles still need
resolution. No executable workflow or human time-saving result is claimed.

Raw extraction still emits 294 null-valued attribute fields out of 544 attributes
across the 34 rows, and some scope/choice prose repeats statement content. Counts
are fields, not a measured token-saving estimate. This is a possible future cost
test, not permission to remove evidence, require new explanation fields, or start
another tuning cycle in this batch.

[Verification](verification.json) reproduces all three extractions and both audits
with provider setup disabled, from the installed wheel outside the checkout.
The original raw-book exports and current-workspace exports retain identical
retrieval rows and meaning/evidence. The workspace adds the known unresolved-
reference observations; its CLI export matches the same snapshot's direct export.
Every source passage survives, and the frozen retrieval diagnostic reproduces its
saved results exactly. The initial verifier's overly broad equality/field-name
assumptions and their corrections remain in [verification attempts](verification-attempts.json).

Keep the historical qualification regressions as development controls. This batch
has now also become development evidence; future generalization tests need fresh
sources. Stop here with the simpler guide, preserved evidence and explicit gaps.
