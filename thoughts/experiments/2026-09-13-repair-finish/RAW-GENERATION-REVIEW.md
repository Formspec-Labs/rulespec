# Manual generation review before arm totals

All 24 raw response payloads were read against source and the frozen baseline
criteria before opening aggregate scores. Source/selected-target context was
inspected when an empty result did not identify its targets. Shape can reveal
the arm, so this is an anonymized read by the experiment designer, not independent
human blinding. No checker response was available to influence these labels.

| Cell | Source-based observation |
| --- | --- |
| 01 | Constructed component error: corrects participant to Secretary and preserves complete default meaning. Also fills action/object, duration and reference fields and paraphrases the statement unnecessarily. Native preview succeeds. |
| 02 | Same needed actor correction and faithful default meaning, but newly populated `logic_text` omits source list markers; the entire proposal is refused for absent exact evidence. Keep this real refusal in the outcome. |
| 03 | Known pension: incorporates both 2007 conditions, year-end positive balance, prior provision, single-employer scope and until-zero permission. Full source scope quotes support the added meaning. Adds redundant action/object structure and an inline external-content disclaimer. Preview succeeds. |
| 04 | Benefits: no edits. Calls C0003 and C0027 complete while their selected default readings still omit the supplied annual alternative or what requirement it satisfies. C0021 correctly stays unchanged. |
| 05 | Benefits: no edits. Discusses the already correct Secretary actor and unavailable external provision; does not repair either selected local-meaning gap. |
| 06 | FOIA: no edits. Discusses unavailable references and a supported actor; clock-start/tolling and response-ending-tolling gaps remain. Appeal control stays unchanged. |
| 07 | Constructed component error: corrects Secretary and preserves the default meaning; also emits the whole fields object and fills optional action/object/duration/reference fields. Preview succeeds. |
| 08 | Accommodation: no proposals or observations. Local conditions stay intact, but missing-introduction/force uncertainty is not identified. |
| 09 | Benefits: no edits. Declares all selected records complete, missing the same two local-reading gaps. Claims the actor evidence flag is resolved by source wording, although no evidence-location action resolves it. |
| 10 | Known pension: correct complete default meaning using only three returned fields. Also populates action and object without their component quotes, and adds no direct evidence for the newly incorporated eligibility criteria. Native preview succeeds; meaning and evidence coverage must be assessed separately. |
| 11 | Denial: clarifies modality quote and narrows main/scope evidence to the first sentence. Leaves the default meaning unchanged and still omits notice grounds and both exceptions. This is a traceability edit, not the requested complete reading. |
| 12 | Known pension: correct complete default meaning and explicit source scope support for the 2007 criteria. Also adds optional action/object fields and external-reference observation. Preview succeeds. |
| 13 | Constructed component error: corrects Secretary, retains the complete statement and emits all fields, with optional action/object filling. Preview succeeds. |
| 14 | Denial: repeats cell 11's modality/evidence narrowing; still no grounds requirement or exceptions in the default statement. |
| 15 | Accommodation: empty output. Local conditions preserved; missing-context force uncertainty unreported. |
| 16 | Known pension: correct complete default reading and supporting scope quotations. Also fills the full fields object, adds a concept definition, action/object, logic and reference detail. This is not a minimally changed output. Preview succeeds. |
| 17 | Denial: no edit because the required grounds and exceptions are already in C0001. That observation is true about the book but does not complete selected C0000. |
| 18 | Accommodation: no edits; confirms covered-entity actor without addressing the missing introductory force. |
| 19 | Denial: no edit; explicitly credits C0001 for grounds/exceptions and C0000 for prompt notice. Both remain split for the independent-reading goal. |
| 20 | Benefits: no edits. Credits the companion delivery permission and says qualification links belong in a later pass; it still does not explain the referenced three-year requirement in C0027 or the annual alternative in C0003. |
| 21 | Accommodation: empty output. Same uncertainty remains. |
| 22 | FOIA: no edits. Focuses on unavailable outside provisions; supplied timing conditions are still absent from the selected default readings. |
| 23 | FOIA: empty output, including no acknowledgement of the selected gaps. |
| 24 | FOIA: no edits. Again reports external references without incorporating the available clock and tolling qualifications. |

## Decisive observation

No generated proposal repairs a selected fresh default-meaning gap. The only
fresh-source proposals are the two denial evidence edits, which leave their
missing default meaning unchanged. The familiar pension repair and controlled
actor correction demonstrate narrower capability; they cannot supply the fresh
gain or minimum fresh-repair count required by either adoption rule.

Both primary adoption routes therefore fail regardless of advisory checker
verdicts or later token totals. Stop model calls now under the plan's decision
stop rule. Do not spend the optional 24 checker calls to confirm an already settled
non-adoption decision. This leaves checker agreement and generation-plus-check
cost unmeasured in this experiment; do not report them as zero or as a cost gain.

Complete selected controls stay unchanged. Accommodation's missing-parent
uncertainty remains excluded from decisive scores as frozen before generation.
It is not counted as a new accurate control merely because no edit was emitted.

## Further interpretation limits

The positive complete-reading task and the original recovery language coexist in
both arms. The latter discourages duplication of retained meaning and describes
later relationship work. Some responses explicitly prefer those interpretations.
That is a plausible task conflict, not an isolated causal result: this experiment
changed response shape, not those instructions. No prompt patch follows here.

The broad source passages and all neighboring records were supplied. Meaning can
be accurate across a book and still incomplete in a selected standalone statement.
The source-location checks do not establish semantic completeness, nor does an
AI rationale clear a genuine stored warning. Sparse output was possible (cell 10),
but its availability did not consistently prevent full-field output or enrichment.

For the offline review/export exercise, apply structurally valid proposals only
in disposable workspaces. Label this explicitly as an application rehearsal,
not model-checker approval or production adoption. Keep the incomplete denial
edits visible so the rehearsal cannot be mistaken for a semantic quality gate.
