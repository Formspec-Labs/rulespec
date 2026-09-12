# Section focus integrated; the existing audit misses the smaller gaps

**Decision: keep section focus available explicitly; do not make the current
audit a completeness gate.** Nine fresh audit calls identified the broad draft's
missing State-plan contents, but detected **zero of the three** previously
identified detail-gap groups in the focused draft. The independent inventory
had omitted the same details before seeing that draft.

## What changed in the extractor

`extract --section-windows` now bounds requests at the document's existing section
starts, retaining the original source, character cap, line/list handling and
bounded parent/neighbor context. It records the option in run metadata and supports
ordinary replay and reprocessing. No prompt, schema, model default, citation
fetch, audit, refinement or UI behavior changed.

This is the narrower integration authorized after the
[focus experiment](../2026-09-12-csbg-focus/RESULTS.md), whose full-completeness
gate failed. The option defaults off. The full CSBG chapter would use 27 requests
instead of six; all text remains present once as focus. All three compared sections
remain intact in the new plan, with separator whitespace appended. The complete
27-request extraction has not been run or evaluated. See
[integration checks](integration-checks.json) and the
[operating instructions](../../../packages/rulespec-extrapolator/OPERATIONS.md#section-focused-extraction).

The 698-test suite passed; 133 focused tests passed again after the final replay
metadata guard. The wheel was built and installed, and all 92 installed packages
remain compatible. From outside the repository, the installed package reprocessed
the original full CSBG capture and replayed the result identically without provider
calls: 208 accepted, one rejected, unchanged candidate data. The original partial
status remains. See [installed check](installed-check.json).

## The bounded diagnostic test

The [plan](PLAN.md), source/runtime/config pins and randomized comparison order
were saved before calls. Existing production audit functions made three independent
source inventories, then six comparisons: historical broad and focused drafts for
9908, 9910 and 9915. Each pair shared the same fresh inventory and exact focus
window. The audit used `gemini-3.8-flash`, medium thinking, temperature zero and
32,768 output tokens, with no numeric thinking budget or retries.

These are custom selected-window observations. They are not a full-chapter audit,
fresh extraction, new audit algorithm, or independent-document benchmark. No
whole-document assessment/accounting was manufactured for the partial selection.

The [manual review](BLIND-REVIEW.md) was hashed before opening the arm key.
Record shapes reveal likely arms, so masking is partial. Labels remain revisable
assistant judgments against the original source, not absolute answers.

| Predeclared measure | Observation |
| --- | --- |
| Broad plan's thirteen missing content meanings | All thirteen flagged through fifteen partial inventory units and a claim-summary error |
| Focused plan (b)(1) emergency-need and replication details | Missed; inventory also omits them |
| Focused plan (b)(3) gap-filling methods | Missed; inventory also omits them |
| Focused plan (b)(5) low-income recipients | Missed; inventory also omits them |
| Private-board scope in optional field versus default statement | Whole record accepted; default-statement concern not diagnosed |
| Standalone 'must, at its discretion' | Accepted without noting the modal-field tension |
| Named faithful alternatives, qualifications and timing controls | Credited; no false alarm on these selected substantive controls |

The focused plan receives 28 all-correct claim judgments and 29 covered inventory
units, despite the three known gaps. For example, the original (b)(3)(B) names
information, referrals, case management and followup consultations. Both draft
and inventory reduce this to developing linkages to fill service gaps. The
comparison calls the unit covered. Raw quotations contain the methods, but their
presence never becomes an explicit meaning or a missing-detail observation.

Two other results constrain confidence:

- The audit flags the broad board-composition record for missing the explicit
  private/nonprofit eligibility condition. Requiring self-contained wording is
  reasonable, but its rationale overstates the defect as an unconditional mandate:
  the statement still explicitly identifies the board in 9910(a)(1). This is one
  debatable scope diagnosis affecting six inventory units, not six proven errors.
- It accepts the broad standalone 90-day finality statement even though the
  documentation-receipt trigger remains only in the neighboring statement. Its
  inventory similarly separates the deadline trigger from finality. The focused
  statement correctly retains that trigger.

The broad plan's extra FY2000 transition finding concerns text outside that
historical capture's focus. It is excluded from the primary omission comparison.

## Consumption and verification

All nine responses ended `STOP`, with no incomplete responses or retries. They
used **159,427 recorded tokens**: 98,337 input, 28,922 candidate output and 32,168
thinking tokens. Capture took **157.4 seconds**. This is the cost of the whole
diagnostic comparison, not a per-document extraction estimate or invoice.

The three inventories produced 54 units, including three background units. The
six comparisons assessed all 62 supplied claims and 102 substantive unit appearances
across the pairs. Parsing/source checks recorded no issues; reciprocal judgment
links were consistent. These mechanical results do not resolve the missed meaning.

All nine complete actual requests match the production adapter's configuration,
and their inventories/judgments reproduce with provider setup disabled. The first
local verifier had omitted the SDK's JSON MIME-type field from its expectation;
the [correction](VERIFICATION-NOTE.md) is retained separately from the pinned
harness. See [verification](verification.json), [raw captures](captures/) and
[masked review inputs](review/). Original experiments and captures remain intact.

## Next useful decision

The existing audit has value for gross missing content, but it did not provide a
more detailed account of these compressed clauses. This does not establish why
the model omitted them internally, nor prove that other settings or cases behave
the same way. It does identify an observed failure at the source-inventory stage,
followed by missed detection during comparison.

The next bounded test should reuse the existing publisher/source passage index
to check subordinate items explicitly against extracted meaning, preserving the
governing lead-in. Compare that checklist with the unchanged audit on saved
failures and untouched documents. Count both uncaptured components and false
alarms on descriptive examples/alternatives. This is proposed work, not an added
production pass or schema. Keep structural processing coverage distinct from
semantic completeness; no node count or model agreement establishes the latter.

Stop this comparison at its nine-call bound. Do not keep shrinking the same
documents or accumulating prompt patches. The
[task list](../../plans/2026-09-10-reference-integration-task-list.md) records the
capture work separately from genuinely missing-reference-context integration.
