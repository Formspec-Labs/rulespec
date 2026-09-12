# Focused extraction recovers the plan contents, with remaining detail gaps

**Decision: bounded improvement; capture is not fully solved.** Giving the
complete State-plan section its own extraction focus produced distinct records
addressing all thirteen required plan contents. A fresh repeat of the original
broad-window request reproduced the one-record, reference-only summary. Three
contents still omit subordinate meaning, and finer splitting exposes scope/modal
field weaknesses. Keep this as evidence for improving focus selection, not proof
that section-based extraction is ready for general adoption.

No production planner, prompt, schema, model setting, automatic context injection,
audit, or review history changed. Form/workflow mapping remains deferred.

## Comparison

The [plan](PLAN.md) and input/runtime pins were saved before five model calls.
We reused the SAME 135,797-character chapter document, coordinates and section
index from the [original CSBG run](../2026-09-12-csbg/RESULTS.md).

- **A:** exact fresh repeats of original windows 1 and 2, spanning 23,981 and
  23,431 focus characters. Actual request JSON equals the historical requests.
- **B:** separate complete sections 9908, 9910 and 9915 as focus: 14,755, 4,672
  and 3,140 characters. Existing `with_context` supplies parent/adjacent text.
  No new instructions, missing-source supplementation or citation traversal.

Both use `gemini-3.8-flash`, low thinking, temperature zero and 16,384 output
tokens. Existing prompt/catalog, capture, response parsing and Core compilation
functions process both arms. This harness supplies explicit experimental windows;
it does not implement a production selection algorithm. One observation per cell.

Capture order was randomized. Paired outputs were reviewed with arm names hidden;
the [review](BLIND-REVIEW.md) was hashed before opening the [key](review-key.json).
Different record shapes make full masking impossible. Labels remain revisable
assistant judgments. [Input checks](input-checks.json) confirm every meaningful
source line being evaluated was supplied in both corresponding requests.

## The main result

| State-plan measure | Broad A | Focused B |
| --- | ---:| ---:|
| Top-level contents individually addressed | 0 / 13 | 13 / 13 |
| Specific content records | 0 | 15, because item (1) has A/B/C records |
| Faithful at the preregistered detail level | 0 / 13 | 10 / 13 |
| Partial meanings | 0 / 13 | 3 / 13 |
| Missing meanings replaced by a generic pointer | 13 / 13 | 0 / 13 |

Both outputs also retain a parent submission/timing record. A's single record
selects the whole list as evidence but refers only to its paragraph numbers. B
captures the actual required contents and retains their State-plan assurance or
information role, instead of recasting every downstream activity as a direct duty.

For example, B now separately captures:

- The community-action-plan funding condition, required needs assessment,
  Secretary submission **at the Secretary's request**, and optional coordination
  with other assessments.
- The prior-year proportional-funding protection, cause, notice, record hearing
  and Secretary review.
- Representation petitions and their inadequacy trigger; maximum-extent-possible
  partnerships; where-appropriate energy-crisis coordination; performance-system
  alternatives and the historical deadline.

The three partial contents are narrower versions of the original compression gap:

1. **9908(b)(1):** the immediate/urgent-needs limitation on emergency assistance,
   and urban-intervention/widespread-replication detail in the partnership outcome,
   are absent. Some examples are abbreviated.
2. **9908(b)(3):** all four requested descriptions appear, but the gap-filling
   methods—information, referrals, case management and followup consultations—are
   omitted. Public/private resource detail is generalized.
3. **9908(b)(5):** service/workforce coordination appears, but this record omits
   the explicit low-income recipients of effective service delivery.

These judgments concern missing meaning, not literal copying. The content-topic
count alone would overstate completeness. The all-thirteen-faithful criterion
is not met, even though the top-level granularity improvement is substantial.

## Controls and representation limits

The board section changes from three combined records to five. Elected-official
shortage substitution, democratic selection/residence, and the public-board OR
alternative mechanism survive. The focused private-board records put the private-
nonprofit scope in `scope_text`, while their primary statements refer generically
to the board. The whole record retains scope; the default statement alone is
less self-contained than A's explicit reference to 9910(a).

Corrective action changes from seven records to eleven. The assistance/report
branches, notice/hearing, unless-corrected condition and 60-/30-day clocks survive.
B's standalone 90-day default-finality statement also retains the documentation
trigger that fresh A leaves in a separate record.

However, B isolates the discretionary improvement-plan option as
`requirement`/`must`, with the wording **must, at its discretion**. Discretion is
still present, so this does not prove the model converted the option into an
unconditional duty. It creates a misleading standalone modality for the option;
the old broad record's must label covered a process with actual mandatory steps.
Finer segmentation needs checks for both retained scope and correct modal force.

B's plan records also select cumulative source ranges starting at the common
lead-in. Later records' main evidence includes earlier, unrelated plan items.
The records have distinct meanings, but their evidence is still broad and repeated.
Existing `scope_quotes` could carry the shared lead-in separately; this experiment
did not enforce that selection or alter any captured evidence.

## Processing, consumption and verification

| Cell | Accepted units | Input tokens | Output tokens | Capture seconds |
| --- | ---:| ---:| ---:| ---:|
| A: original window 1 | 33 | 11,250 | 9,718 | 20.3 |
| A: original window 2 | 38 | 12,345 | 10,875 | 22.6 |
| B: State-plan section | 28 | 7,525 | 8,851 | 18.3 |
| B: board section | 5 | 4,596 | 1,591 | 6.2 |
| B: corrective-action section | 11 | 3,466 | 3,643 | 9.4 |

All five responses ended `STOP`, with no retries, incomplete responses or rejected
statements. A's first window retained three non-exact modality-quote refusals;
B's three captures had no parser refusals. Core separately recorded 25 component
support issues in A and 46 in B, including repeated actor/modal phrases within
broad evidence. These are not counts of semantic errors. Graph validation passed.

Total recorded consumption was **73,860 tokens**: 39,182 input and 34,678 output.
The capture/compilation harness completed in **87.6 seconds**; provider capture
times above exclude subsequent local compilation. B consumes 29,672 tokens across
three requests versus A's 44,188 across two, but B does less total source work.
This is not a same-coverage cost comparison or a predicted whole-chapter saving.

All five saved responses reproduce the same parsing, compilation and validation
with provider setup disabled. Actual settings, exact A request equality, source
pins and original captures remain verified. This is [custom-window replay](verification.json),
not a claim of ordinary CLI whole-document-run replay. Inspect [raw captures](captures/)
and [decoded records](decoded/) for every observation.

## What this supports next

Request focus is a useful variable: the broad-window failure reproduced, while
the complete focused section recovered every top-level requirement. This test
does not distinguish reduced competing content from more output allocation per
source item, nor establish performance on other documents. Source was already
available in both requests; it supplies no evidence for adding more reference text.

The remaining capture problem is now concrete: preserve subordinate meanings when
separating requirements, and keep their scope/modality correct. Evaluate reuse of
the existing focus, scope-evidence and validation functions around those failures.
Do not adopt blanket paragraph splitting, keep shrinking this source, or add a
mandatory model pass from this one comparison. Stop this experiment here; the
[task list](../../plans/2026-09-10-reference-integration-task-list.md) records the
next capture work separately from missing-reference-context integration.
