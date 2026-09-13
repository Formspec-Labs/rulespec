# Manual validation of the latest assessment labels

The two attendance items have defensible standalone-completeness failures. The
third “clear flaw” is a definite loss of explicit detail but a less certain
semantic failure. The 17 positive labels describe statement fidelity better than
whole-record correctness. The original labels need narrower claims and separate
field-level findings before they are reused as a benchmark.

Scope: I manually read every supplied IEP and LEA passage, all 21 fixed extraction
records and populated fields in the latest experiment, the original label review
and criteria, the actual explicit-prompt SDK request, and the current CUE field
guidance. I did not relabel the other 60 original confidence records. No provider
calls or automatic semantic grading were used. I have already seen the assessment
results; this is a post-result audit, not a new blind evaluation.

All prior captures, labels, assessments and manifests remain unchanged. The
companion [audit data](2026-09-12-confidence-label-audit.json) records these
revisable judgments and the exact input hashes separately.

## What the original labels actually required

The original [confidence experiment plan](../experiments/2026-09-12-extractor-confidence/PLAN.md)
calls a meaning flawed when it loses a substantive condition or required component
needed to use that meaning independently. The latest actual instruction explicitly
requires completeness of the statement and agreement of populated component fields
with the source. Those are stronger requirements than checking whether the quoted
clause was extracted accurately.

The distinction is also in CUE: `#FirstMeaning` makes the statement the complete
default reading; `#Summary` requires the governing qualifications there. Optional
fields or long evidence quotations do not replace omitted meaning. `#ScopeText`
describes governing conditions; `#ContextQuotes` accommodates explanatory material
without asserting prerequisites. `#Actor` requires a source-supported responsible
party and permits an absent actor for an impersonal rule.

Source:
[document-understanding.cue](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data/document-understanding.cue).

## The three previously negative items

### IEP R004 and R005: keep the standalone-completeness failures

F045 labels clause (i) “Attendance not necessary.” F046 then permits the
attendance exemption when the parent and agency agree that the member's area is
not being modified or discussed. F048–F050 describe clause (ii), excusal when
the member's area is involved, with parental/agency consent and the member's
written input before the meeting.

F053 supplies a separate requirement:

> A parent’s agreement under clause (i) and consent under clause (ii) shall be in writing.

R004 faithfully reproduces F046 but omits written parental agreement. R005
faithfully reproduces the excusal conditions but omits written parental consent.
The member's written input in R005 is not the parent's written consent.

The qualifier and the clause labels appear in the actual checker input, including
inside each of these composed item questions. The omissions are not caused by
withholding source text from the checker.

However, **the extraction collection did capture the writing rule**: R006 repeats
F053 and retains references to clauses (i) and (ii). These are failures to make
the individual statements complete, not proof that extraction lost the writing
requirement from the document as a whole. A consumer that resolves and composes
the separate rule can recover it. This audit does not assert that a particular
production graph consumer already does so.

Disposition: retain `flawed` for the declared standalone-statement test, with
issue type `missing_governing_qualification`. Do not call the statements fabricated,
contradictory to their local clauses, or the writing rule wholly unextracted.
This is a representation assessment, not a legal ruling that a procedural defect
necessarily invalidates an attendance exemption.

### IEP R000: separate explicit-detail loss from a clear semantic error

F025 says:

> the transition services (including courses of study) needed to assist the child in reaching those goals

R000 retains “transition services needed to assist the child in reaching those
goals” but drops “including courses of study.” The textual detail is definitely
missing; the earlier review was correct about that observation.

Calling it an unambiguous change of meaning is stronger. The retained umbrella
term does not exclude courses of study. A reader may treat the parenthetical as
explicit elaboration already included in transition services. For a form-generation
use case, retaining the named component is valuable, but the prior binary rubric
did not operationalize when omitting an included example/component crosses from
loss of explicit specificity to materially incomplete meaning.

Disposition: `uncertain` for a conservative semantic-completeness reference label;
retain `explicit_detail_omitted` as a confirmed observation. It remains a failure
under an explicitly exhaustive component-retention criterion. Do not redefine the
historical criterion silently, erase the omission, or count it as a clear semantic
error without identifying which criterion is being used.

## The disputed IEP R006 actor

The statement is an exact copy of F053. Its clause references are retained. It is
clear as a source-linked writing rule; as an isolated statement it does not name
attendance/excusal, so independent usability remains limited.

The record assigns `actor: parent`. The source names the parent's agreement and
consent, which supports a parent-related role. It does not explicitly name who
must prepare or retain the written record. A rule about the form of a document
can therefore reasonably be represented as impersonal. Neither the possessive
“parent's” nor the grammatical subject alone settles the actor assignment.

The checker's additional objection about imposing an action “solely” on the
parent goes beyond the stored actor field; that field does not assert exclusive
responsibility. The earlier claim that its objection was simply wrong was too
confident. Conversely, its false verdict is not a validated detection of the
original unresolved-reference concern.

Disposition: retain `uncertain`, with actor assignment and standalone reference
interpretation recorded separately. Exclude this item from hard success/error
counts. A component-specific actor convention and examples are needed to make
the expected result reproducible.

## The positive items and a missed field issue

The four other IEP statements retain their source meanings. I found no new
substantive defect in their inspected fields. All 13 LEA statements retain their
plan-description obligations, conjunctions, alternatives, conditions, and source
citations. The LEA actor identifies the agency responsible for the plan, including
where the plan describes other parties' actions; those nested actors do not
automatically replace the actor of the plan-description requirement.

But every LEA `scope_text` contains this purpose wording from F000:

> To ensure that all children receive a high-quality education, and to close the achievement gap ...

The ellipsis above abbreviates this audit quotation only; raw evidence and model
inputs contain the full sentence. This is a rationale, not a condition that
determines whether the plan-description duty applies. It belongs in the statement
as faithful source context, or in explanatory context if useful. Its placement as
structured applicability is questionable under `#ScopeText` and should be reviewed.
R007, R011 and R012 also include real applicability/discretion qualifiers, which
must be preserved if the purpose text is removed from that field.

This is one repeated issue pattern, not 13 independent discoveries. It does not
make the 13 statements factually false. It does mean they are not demonstrated
clean negative controls for the latest prompt's **all-populated-fields** judgment.
I am recording the field issue separately rather than retroactively converting
13 controls into 13 new clear semantic defects.

## Item-by-item disposition

“Keep positive” below is about the statement's substantive source meaning, not a
guarantee that every component is suitable for automated use.

| Item | Original | Statement-completeness disposition | Source-based check / component finding |
|---|---|---|---|
| IEP R000 | Flawed | Uncertain; explicit-detail loss confirmed | F025 courses-of-study parenthetical omitted; umbrella term retained |
| IEP R001 | Faithful | Keep positive | F028–F029 construction limit retained; no additional duty introduced |
| IEP R002 | Faithful | Keep positive | F028/F030 exemption from duplicate information retained; team actor supported |
| IEP R003 | Faithful | Keep positive | F032–F043 membership counts, qualifications, discretion and alternatives retained |
| IEP R004 | Flawed | Keep negative for standalone completeness | F053 written parental agreement missing from F046-based statement |
| IEP R005 | Flawed | Keep negative for standalone completeness | F053 written parental consent missing; F050 member input is different |
| IEP R006 | Uncertain | Keep uncertain | F053 exact statement; unresolved clause interpretation and disputed actor |
| IEP R007 | Faithful | Keep positive | F056 prior-service case, parental request, invitation recipients and purpose retained |
| LEA R000 | Faithful | Keep positive; scope needs review | F000–F005 all four monitoring methods retained |
| LEA R001 | Faithful | Keep positive; scope needs review | F007 required disparities, student groups, teacher categories and citation retained |
| LEA R002 | Faithful | Keep positive; scope needs review | F008 specific referenced duties retained; unsupplied text need not be invented |
| LEA R003 | Faithful | Keep positive; scope needs review | F009 poverty criteria and attendance-area citation retained |
| LEA R004 | Faithful | Keep positive; scope needs review | F010 general description, outside-school qualification and recipient categories retained |
| LEA R005 | Faithful | Keep positive; scope needs review | F011 reserved funds, three service goals and coordination retained |
| LEA R006 | Faithful | Keep positive; scope needs review | F012 parent/family engagement strategy and citation retained |
| LEA R007 | Faithful | Keep positive; scope needs review | F013 if-applicable limit, integration levels and transition plans retained |
| LEA R008 | Faithful | Keep positive; scope needs review | F014 school setting, teachers/leaders, consultation parties and eligibility retained |
| LEA R009 | Faithful | Keep positive; scope needs review | F015–F017 both transitions, applicable methods and nested alternatives retained |
| LEA R010 | Faithful | Keep positive; scope needs review | F019 discipline-reduction duty, optional method and subgroup citation retained |
| LEA R011 | Faithful | Keep positive; scope needs review | F020–F022 agency discretion, optional experiential learning and conditional credit retained |
| LEA R012 | Faithful | Keep positive; scope needs review | F024–F026 agency discretion, funding purpose and optional examples retained |

## What changes in the reported conclusion

Use the conservative statement-completeness breakdown of **two clear negative,
17 statement-positive, and two uncertain** items. Both tested prompts still
approve both clear negatives. The verdict vectors are identical regardless of
these label qualifications, so the finding of no measured difference between
the prompts remains valid.

Do not repeat “three unambiguous errors and 17 wholly clean items.” The original
0/3 result remains reproducible under its saved labels; this post-result audit
supports the narrower **0/2 clear standalone-completeness failures detected**,
plus an explicit-detail omission and unresolved component issues. Neither count
is a general accuracy estimate. In particular, the 17 statement-positive items
do not establish a false-positive rate for an all-fields checker.

Before further quality comparisons, record separate judgments for source support,
standalone completeness, explicit component retention, and field assignment.
Reuse the existing schema meanings; no new production schema or additional model
pass is justified by this audit alone. Make the intended assembled-vs-isolated
reading explicit, and give ambiguous cases their own status rather than forcing
them into a single correctness label.
