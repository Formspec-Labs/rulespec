# Blind adversarial review: what still needs work

**The extraction produces useful drafts with exact evidence, but it still loses
source meaning.** The most consequential failures are omitted permissions,
missing document alternatives, and duties or permissions separated from the
conditions that limit them. These failures already appear in the recorded model
responses. The three saved corrections improve their intended targets, while
the corrected section remains incomplete.

The application also has three reproduced defects: an overflowing number in a
refused model row can prevent durable failure recording and normal recovery;
evaluation cannot mark a fully reviewed total omission complete; and compilation
can replace a valid child-section assignment with its parent.

This pass made no production fixes, model calls, commits, or releases. Findings,
proposed semantic regression cases, executable offline probes, and observations
are saved here. The next implementation should focus on the core extraction
workflow and these regressions.

## What was independently reviewed

Three fresh agents received no conversation history or earlier assessments.
Two built source inventories before receiving any output; those inventories
were sealed by hash. The third challenged copied code and existing tests.
The integrator had prior context, verified examples and reproductions, and is
not blind. The [protocol](README.md) describes the shared-workspace limits and
the separate photograph-inventory erratum.

| Review | Recorded output examined | Source expectations |
| --- | --- | --- |
| [Photographs](photos-review.md) | One run; 33 raw and accepted candidates | 54 annotations, including 7 context/scope annotations |
| [Names](names-review.md) | Four runs; 88 raw candidates, 87 accepted, 1 rejected | 50 annotations for each selected-excerpt run; 24 for each overlapping contiguous-section run |
| [Correction case](names-review.md#the-three-saved-corrections) | Three actions, 12 current claims, 17 retained revisions | All 24 annotations in the contiguous input |
| [Workflows](workflows-review.md) | Extraction, compilation, review, evaluation and recovery code/tests | 91 selected existing tests passed; new offline probes exposed gaps |

The [accounting verification](audit-verification.json) checks that every raw
candidate and accepted claim is represented in its audit. All 121 raw rows
retain their fields in candidates; all 120 accepted claims retain their
candidate fields. Every original candidate quotation and accepted evidence
span matches its pinned input. One candidate is visibly rejected during
compilation, as described below.

These checks establish exact support and processing fidelity. They do not
establish correct interpretation or completeness. The inventories include
overlapping propositions, alternatives and guidance, so annotation counts are
not required output-row counts or independently enforceable-rule counts. The
inputs overlap and the reviewers are AI agents; no general accuracy percentage
or human time-saving claim follows.

## Highest-priority extraction findings

**1. Whole source statements and lists disappear.**

The photograph run omits infant closed-eye acceptance, infant head tilt,
acceptance of harmless damage, and the statement that applicants need not sign
the photograph. It also omits the coordinated six-month, likeness and
identification guidance, and the temporary-medical-eyeglasses recommendation
for urgent or emergency travel. The infant omission is particularly material
because the output retains the general eyes-open guidance.

All four name runs preserve an instruction to supply one or more listed
documents but omit the actual list. Both selected-excerpt runs also omit weaker
spacing guidance and qualified rewrite rules. Grouping equivalent content would
be acceptable; these omissions are not merely disagreements about how many
claims to create. Evidence: photograph F01/F03 in the
[source review](photos-review.md), and names findings 1–3 in the
[names review](names-review.md).

**Next check:** account for each substantive source passage and list item as
represented, refused, unresolved, or deliberately excluded with a reason. Keep
permissions, exemptions, definitions and guidance in that accounting. A
nonempty output or a completed processing window cannot satisfy this check.

**2. Splitting adjacent sentences widens the resulting rules.**

Photograph candidate **C31** says “The applicant must re-execute Form DS-11.”
Its summary and logic omit the missing-photograph and acceptance-facility case
in the preceding sentence. It has no incoming qualification and no claim
issues. The adjacent suspension claim retains those limits, but does not
transfer them to the applicant duty.

All four name runs similarly lose part of the older-than-one-year, DS-11,
unchanged-ID branch governing emergency limited-validity issuance. The
recent-change documentation duty also loses inherited DS-11/timing scope.
Some local condition links are correct while the parent condition is absent.
Evidence: photograph F02 and names findings 4–5, with exact offsets and raw
candidate locations in their audits. Candidate indices in both reviews are
zero-based.

**Next check:** every extracted child rule must retain its governing lead-in
and antecedent, either in its own supported scope or through explicit links.
Test the neighboring case where the condition is false, not only the case
where the action applies. Source context across window boundaries is part of
this work; larger windows alone do not repair the observed same-window losses.

**3. Exception handling varies through omission and classification.**

The emitted local modifier links in this sample have correct direction and
targets. The failure is an incomplete set of relationships:

- In `holdout-01`, the confidential-former-name exception correctly qualifies
  the court-document requirement to show both names. In `holdout-02`, the same
  passage becomes an unlinked permission to receive a court order. The
  descriptive possibility and its exception role have been confused.
- The recent-ID exemption is present in `holdout-01` raw output but has an
  invalid exception relationship. The compiler correctly rejects it and
  preserves the rejected candidate. Two other runs omit it. `section-01`
  retains a correct “do not need to submit” summary, but its permission/action
  fields leave absence of obligation ambiguous.
- Photograph disability and medical eye-closure permissions survive without
  explicit exception relationships to the general expression/eyes-open rules.
  The medical eye-closure permission's own trigger is correctly linked.

Evidence: names findings 6–8 and its complete modifier-link table; photograph
F07 and its seven-record target audit. Neither source reviewer found a wrong
resolved local target. Remote reference contents remain unknown and cannot be
assumed to repair an omitted condition.

**Next check:** test the existence, role, scope and target of each exception,
including representations of “not required.” A validly rejected row must remain
part of the coverage workload. Do not force the recent-change exemption onto
the older-change suspension duty: they describe different timing classes.

**4. Exact component quotations can coexist with incorrect force or meaning.**

The photograph prompt defines `requirement` as “must do,” yet three accepted
records in that category still say `should` in their summaries. The source
words survive, but the category conflicts with their force. The material-damage
definition also weakens “no longer a good likeness” or impeded facial
recognition into merely “affecting” them.

In the name-change output, one condition uses `form DS-11` as the object of
`has had a material name change`; the form is application context. This
component error remains in the corrected current set. Empty actors and
grammatical subjects are treated separately as uncertainty where the source
does not establish a responsible party.

Evidence: photograph F04–F06 and names finding 9. These findings concern the
representation; no automated policy execution was inspected.

**Next check:** distinguish obligation, recommendation, permission, prohibition,
absence of obligation and descriptive possibility. Independently check actor,
action, object, negation and thresholds against their source relationships.
Retain ambiguity when the available representation cannot express the meaning.

## What the correction case establishes

The blind reviewer found all three saved corrections improve their targeted
meaning, with no new substantive falsehood identified in those new records:

1. The documentation edit restores the complete alternatives and their grouping.
2. The emergency-permission merge restores the older-change/DS-11/unchanged-ID
   branch and the urgent-travel timing condition.
3. The documentation-duty merge restores the recent-change/DS-11 applicant class.

The current set still omits two qualified source statements: identity evidence
*might* be required under Department guidance, and applicants *generally* need
the name-change documentation to update their ID. The original incorrect
action/object pairing and negative-force ambiguity also remain. No dangling
current modifier targets or reversed links were found in the released case;
all current claims remain pending.

This supports the usefulness of the correction workflow. It does not show a
complete repaired section or better automatic extraction. The assessment is
based on saved actions and results, not a new browser usability study.

## Reproduced application defects

These are separate from model-quality findings. All three are **P2 defects
with high-confidence offline reproductions**.

| Finding | Trigger and observed result | Required regression |
| --- | --- | --- |
| **W1: Failure cannot be finalized** | A refused row containing JSON number `1e999` decodes to infinity. Serializing `refusal.raw` raises before guarded finalization. The saved run remains `running`, without its manifest or rulebook. Review, replay and reprocessing cannot open it. Raw response and the valid neighboring candidate survive. | Mixed valid/overflow response must finish with a durable terminal outcome, serializable refusal, retained raw capture and valid candidate, and a supported recovery path. |
| **W2: Completed review reported unfinished** | No accepted claims, a nonempty expected set, and fresh judgments marking every expected item missing produce the correct quality failure but `review_complete: false`. There are no unjudged items or unknown units. | A fully judged total omission must be a completed, failed review. Review completeness and extraction success must remain separate. |
| **I1: Specific section assignment overwritten** | A candidate explicitly selects a valid child section. With its overlapping parent listed first, compilation silently assigns the parent instead. Reordering the section list changes the result. Quotation and Core validation still pass. | Preserve a valid explicit section ID independent of section-array order; define the fallback when none is supplied. |

W1 is at [`extraction.py:215`](../../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py#L215)
and the unguarded writes beginning at line 551; W2 is at
[`evaluation.py:261`](../../../packages/rulespec-extrapolator/src/rulespec_extrapolator/evaluation.py#L261).
Their complete traces, counterarguments and probes are in the
[workflow review](workflows-review.md). The integrator reran both inputs and
[confirmed the results](integrator-workflows-confirmed.json).
I1 is at [`core.py:95`](../../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L95),
with a separate [integrator review and probe](integrator-review.md). I1 was not
discovered by a blind agent and was not observed in the flat recorded corpus.

The 91 selected existing tests passed despite W1/W2. Those passes cover their
existing assertions, not these newly exposed paths. No full-suite rerun or
production regression implementation was performed for this report.

## Limits and next implementation order

The workflow reviewer also executed a window-boundary case where the governing
condition is absent from the duty's prompt. This proves context exclusion and
acceptance of a synthetic unqualified response; it does not measure a model's
real failure rate. Existing merge behavior inherits the first claim's fields
unless replaced, and approving a stale qualification still attests its retained
historical relationship while showing a current-link warning. These are
documented workflow hazards, not additional confirmed violations of the
current behavior. See the workflow report's counterarguments.

The blind pass independently corroborates the earlier name-output assessment.
It adds the photograph audit, a semantic review of all three saved corrections,
and new failure/evaluation/source-section probes. It does not reopen the
specific defects already closed by the earlier implementation review.

The next core-extraction iteration should:

1. Turn W1/W2/I1 into failing regression tests and repair their narrow accounting
   and source-assignment paths.
2. Use the saved semantic cases to test source coverage, inherited conditions,
   exception completeness, force and component meaning. Preserve positive cases
   and negative controls so repairs do not invent new duties or broad exemptions.
3. Add a coverage and affected-rule check after corrections; correcting three
   selected claims does not account for all source content.
4. Assess the changed workflow on newly sealed blind inputs. These reviewed
   sources now serve as known regression material and cannot establish fresh
   holdout performance after tuning against them.

Thirty concrete semantic cases are saved in
[the photograph audit](photos-coverage-claim-audit.json) and
[the name-change regression fixtures](names-adversarial-regressions.json).
They are proposed assertions, not implemented or passing application tests.
The [packet verification](packet-verification.json) confirms unchanged inventory
seals, released artifacts, and the 129 original files directly copied for this
review. The raw captures and source snapshots remain intact.
