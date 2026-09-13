# Focused checker integration: working implementation, failed quality gate

The standalone selected-statement check is **not adopted**. Its implementation
passes 729 extractor tests and complete recorded replay, but the live bridge gets
**7/8 unchanged-reading judgments correct versus 8/8 with the previous comparison
input**. It falsely flags one complete leave-notice reading. Production code has
been restored; the complete implementation and tests are retained in
[candidate-implementation.patch](candidate-implementation.patch).

## What was implemented and tested

The candidate `check --claim ID` command reused the refinement runner, CUE-derived
meaning fields, source passage resolver, checker result schema, capture system and
review observations. It selected up to eight exact current claim revisions and
constructed unchanged candidates deterministically. It ran no inventory or repair
generation, changed no statement fields, and preserved approval and evidence
warnings. Its internal candidate builder could also combine selected edited
alternatives with the unchanged reading for future generation work.

The [plan](PLAN.md) deliberately narrowed the earlier M9 integration proposal to
a usable evaluator before changing generation. It compared actual command inputs
against newly sent copies of the successful previous request, rather than assuming
that the standalone form behaved identically. The exact policy, independent-
candidate instruction, reference navigation and medium-thinking settings were
retained. This tested no new wording.

Both arms used the same source and extracted meanings. The input check identified
one additional difference before calls: ReviewStore populates current `link_issues`
where the previous raw-book input had null. B retained those accurate statuses.
All other packet fields matched. See [packet differences](packet-differences.json)
and [preflight notes](PREFLIGHT.md). This is a bundle comparison; it cannot isolate
candidate removal from the visibility of current link status.

## Live results

Four known regression sources, two repetitions per arm. These are not eight
independent documents or a general accuracy estimate. Labels came unchanged from
the earlier source review; requests and criteria were frozen before calls.

| Shared unchanged-reading decision | A: previous comparison input | B: standalone check |
|---|---:|---:|
| Leave: complete notice rule | 2/2 | 1/2 |
| Hazard: complete reporting rule | 2/2 | 2/2 |
| Billing: missing supplied alternative meaning | 2/2 | 2/2 |
| Offset: missing four supplied prerequisites | 2/2 | 2/2 |
| Total correct | **8/8** | **7/8** |

B catches all four real-omission opportunities. It preserves three of four
complete controls, with one false alarm. A also gets all twenty additional edited
candidate decisions correct, including redundant fields, cosmetic changes,
complete repairs and wrong-meaning controls. Those extra decisions are not in the
shared no-change denominator. All 36 judgments have valid source selections.

The unchanged leave statement already says the employee must provide at least
30 days' notice for foreseeable planned-medical-treatment leave, with practicable
notice when treatment must begin sooner. Cell 07 rejects it because the prose
does not announce unavailable external references and because actor/modality
evidence locations remain unresolved. Those are real record-status concerns,
but they do not identify a missing supplied condition or incorrect actor/modal
meaning. The source establishes those meanings; reference status is already
recorded, and repeated short quotations account for the location ambiguity.

The frozen label assesses faithful usable meaning for the supplied source. An
evidence-readiness assessment could separately remain unresolved. We did not
change that distinction after seeing the failure. Cell 12 also demands explicit
unavailability wording, although its billing verdict is independently correct
because available subparagraph (B) remains unexplained.

See [raw review](RAW-REVIEW.md), all `inputs/` and `decoded/` records, and
[scores](scores.json). Responses were read in cell order before aggregate scoring;
candidate counts and IDs reveal likely arms, so this was not independent human
blinding. No prompts, labels or models were changed after calls started.

## Mechanical verification and cost

[Local tests](local-tests.txt): **729 passed**, including exact selection, retained
main-quote bounds, preserved component warnings and approval, absent/invalid
judgments, stale assessments, no-change mutation refusal, multiple selected
windows, source-reference validation and replay. The original broad refinement
tests still pass.

[Capture verification](verification.json): sixteen actual requests and responses
re-decode identically; all eight complete candidate command runs replay with
provider access blocked. Native input files, every original meaning/evidence
field, reference warning and approval state remain intact. The only new history
events are model assessments. Schema/replay success does not overturn the failed
semantic gate.

Exactly **16 calls**, no retries or missing responses. Total **149,226 tokens**:
104,784 input, 4,416 visible output and 40,026 thinking tokens. The 11,787 cached
tokens are a subset of input. Summed call time was 129.1 seconds, including local
command processing in B; this is not an isolated provider-latency comparison.

A used 84,363 tokens and B 64,863, a **23.1% reduction**, while B assessed eight
decisions versus A's twenty-eight. This unequal workload and the false alarm
prevent calling it an equal-quality efficiency gain. The collector's raw
`usage.json` includes copied input workspaces; `scores.json` explicitly excludes
those earlier extraction calls. The launch cap therefore counted conservatively;
actual use stayed below the preregistered 200,000-token ceiling.

## Decision and next step

The preregistered no-regression/all-eight-correct gate fails. Keep production
unchanged. The earlier fresh-source positive-task result remains valid for the
tested candidate comparison; this bridge shows that it does not establish the
same behavior for a standalone unchanged-reading check.

The next useful experiment separates **current link-status visibility** from
**removing competing candidates**, using the saved actual leave failure and the
unaffected hazard control. Hold source, meanings, policy and settings fixed in a
four-way comparison. This can distinguish two plausible explanations without
another prompt patch. A model's rationale suggests a confusion between meaning
and traceability, but it does not prove the cause. Repair generation remains a
separate evaluation; do not require new optional fields or insert status warnings
into correct statements to satisfy this checker.

## Retained implementation and replay

`candidate-implementation.patch` contains the exact tested changes to the
refinement runner, CLI and tests. It applies cleanly to parent `95fe284`; these
changes are not in production. To reproduce behavior, use that recorded code
with the patch applied and the same environment. Then run:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-focused-check-integration/verify.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-focused-check-integration/score.py
```

The source pins intentionally fail under unpatched production. Paths in those
pins are local to the recorded checkout. Verification reconstructs ignored exact
input copies from the previous native captures, and byte-identical current runtime
copies from `captures/cell-02/frozen`. Every original capture manifest verifies
the reconstructed bytes. `MANIFEST.json` identifies retained files; no original
experiment was edited. The call limit is reached; verification makes no new calls.
