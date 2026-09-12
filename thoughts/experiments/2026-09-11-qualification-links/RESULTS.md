# Existing relationship generation missed the links we needed to test

**Decision: keep production unchanged. No measured detection improvement; the
broad gate failed.** The existing relationship pass produced valid links for
other exceptions but never proposed the missing equipment override, simulator
prerequisites, PPE scope connection, or payment-precedence connection. This exposes
a discovery/selection failure. It does **not** establish that correctly supplied
links cannot help the checker.

## What was compared

Three frozen development books and their expanded inventories, with the same full
source used in both arms. The unchanged relationship pass ran once per book.
Both checkers then received identical proposed meaning and evidence; only B
received `qualifies` target aliases. Generator rationales were omitted from both
comparison inputs. Proposals remained unapproved advisory data; all judgments
concerned the original, unchanged statements.

Actual requests confirm the intended single difference and the settings:
`gemini-3.8-flash`, temperature 0, medium thinking, 32,768 output allowance, no
thinking budget. Nine fresh calls, nine responses, no retries. All three sources
are now development data, with one observation per arm. This is not a general
accuracy estimate or a complete production refinement evaluation.

| Prelabelled defect | Needed association generated? | A: no target aliases | B: target aliases |
| --- | --- | --- | --- |
| Equipment E1: special-flight-permit override of C0000 | No; dismissed as already represented in C0013 | Missed | Missed |
| Flight F1: two missing simulator-permission prerequisites | Neither; only existing exemption links proposed | Both missed | Both missed |
| PPE P1: (g) limits the (d)/(f) duties | No; generator says limits are already incorporated | All nine affected statements flagged | All nine affected statements flagged |
| PPE P2: other-standard payment precedence affects C0015 | No; dismissed as already represented in C0025 | Missed | Missed |

The nine PPE findings represent one shared scope limitation. Both checkers already
received its expanded inventory and source. They do not show a benefit from the
additional target aliases. Source-only presence, inventory meaning, and complete
meaning in each original statement remain separate questions.

## The useful failure is in selection

The generator produced 14 mechanically accepted proposals containing 19 target
associations: ten existing-exemption links and four companion exceptions. All
nineteen proposed targets were supportable on manual review with their retained
qualification meaning. None supplied a missing primary association. No proposal
was refused, and none of the three requests reached the eight-proposal cap.

For equipment, it linked the already-retained (d) exception to C0000, but described
the (e) override as already represented in C0013 and not an independent exception.
For flight review, it linked five exemptions while emitting no simulator conditions.
For PPE, it linked payment exceptions but said the (g) limit was already incorporated
into relevant rules. The actual nine statements lack it; the inventory contains it.
That is consistent with confusing whole-book or inventory retention with current
claim completeness. The rationale is observable; the model's hidden cause is not.

H3, automatic association discovery/selection as a bottleneck, is supported on
these cases. H1, benefit from correctly supplied missing links, remains unresolved
because the necessary treatment was never generated. The comparison outputs repeat
the H2 necessary-condition-versus-sufficient-permission failure, but this run cannot
show H2 persists *despite correct primary links*: those links were absent.

## Counterexamples and mechanical checks

The ground-training exemption remained limited to one hour of ground training.
Simulator approval for landings did not cancel course or rating requirements.
The PPE (g) restriction was not applied to independent maintenance, design,
damaged-equipment or payment duties. Payment exceptions preserved off-site-wear
permission, employee-request conditions, voluntary ownership and intentional
damage. No confirmed false qualification inheritance was observed.

There was a separate regression in equipment B: three inventory rows returned
the wrong claim aliases despite naming the right claims in their rationales.
The existing evaluator caught all three as `inconsistent_coverage_judgment` and
returned `needs_review`, with `review_complete=false`. Source grounding and parser
acceptance alone did not catch the problem; the existing consistency check did.
Preserve this saved failure for any future alias-handling change.

Both PPE outputs added respiratory/electrical descriptions not established by the
supplied section-number passages. Their section-number scope findings remain
supported; the explanatory gloss goes beyond the supplied evidence. Several
outputs also mark unused dimensions correct while others use not_applicable.
Fine-grained scoring consistency was not established by this experiment.

All six comparisons returned 106 claim judgments and 142 inventory judgments,
with 453 grounded source-reference selections. There were no schema/grounding
refusals. All nine capture-processing results replay identically with zero model
calls. Original books and inventories, actual request bodies, pair differences,
runtime copies, and the pre-call hashes were checked. The same experimental
compound-evidence adapter was used in both arms; production audit's whitespace
inconsistency remains unchanged.

The six comparison outputs were reviewed in randomized anonymous order and the
review was hashed before opening the arm key or generated targets. All generated
proposals and targets were then reviewed separately. Labels remain revisable.

## Cost and stopping point

Recorded total: **305,743 tokens**: 88,119 relationship generation and 217,624
comparison. Capture operations took about 274 seconds, excluding preparation and
manual review. The ninth call began at 255,915 recorded tokens; its response took
the final total 5,743 above the 300,000 pre-call stopping threshold. No further
calls were made. All requests have response/usage receipts.

Comparison totals were A 113,848 and B 103,776 tokens (B about 0.91× A), with no
primary detection gain and a consistency failure in B. Reported cache use and
variable thinking affect these totals; they are not a stable billing estimate.
The shared generation cost is additional, and historical extraction/inventory
cost is excluded.

Stop this experiment here. Do not add another default relationship/audit pass
on this evidence. Keep the existing IDs, evidence, CUE schemas and review checks:
they can represent and validate these associations, and the consistency guard
proved useful. The missing work is deciding which qualifications still need to
be connected and preserving their effect in reusable statements.

The smallest remaining diagnostic, if pursued, is to supply a few manually
source-checked missing associations using the existing fields and repeat the
linked/unlinked comparison. That would be an explicitly constructed upper-bound
test of the checker, not evidence of automatic discovery. If even correct inputs
fail, another discovery pass is not the remedy. If they help, automatic selection
would still need a fresh-document evaluation before adoption. The full existing
recovery → relationships → challenge → apply workflow was not tested here and
must not be judged solely from this isolated relationship experiment.

Receipts: [plan](PLAN.md), [prelabels](PRELABELS.md), [anonymous review](BLIND-REVIEW.md),
[proposal review](PROPOSAL-REVIEW.md), [mechanics](mechanical-results.json),
[replay](replay.json), [usage](usage.json), [cost accounting](cost-summary.json).
Raw requests and responses are in `relationships/` and `comparison/`.

```sh
.tools/document-poc-venv/bin/python thoughts/experiments/2026-09-11-qualification-links/verify.py
```
