# Why the remaining extraction errors occur

The strongest explanation is inconsistent organization and classification of
meaning across fields. The model often understands a condition well enough to
write it correctly in one field, then abbreviates or omits it in another. Some
classification distinctions and splitting decisions also remain underspecified.
These are hypotheses grounded in the captures, not access to the model's hidden
reasoning or conclusions from controlled experiments.

## What I inspected

I read the complete pinned source and all 35 raw output rows from the four final
runs in `examples/document_understanding/meaning-first-adoption/final`, the actual
request prompt and generated schema, and compared the initial raw statements,
classifications and request changes. I checked the converter and evidence checks.

All four final inputs fit in one complete focus window, with no omitted context.
All responses finished STOP; recorded output was 1,775–2,830 tokens against a
16,384-token output budget. These cases do not show source-window truncation or
an output-limit failure. Names, photos, leave and baggage source hashes are
identical between the initial and final calls.

For all 35 final rows, raw statement, scope_text, kind and modality equal their
compiled counterparts (statement maps to summary). The four semantic examples
were already wrong or incomplete in the raw response. Conversion did not invent
the classification or drop those words.

## 1. The model distributes meaning across fields

Final baggage row 3 gives the complete declaration in choice_text, including the
aircraft operator, the bag's firearm, its unloaded status, timing and oral/written
alternatives. scope_text also retains those details. The later statement reduces
it to the passenger declares it. This is strong evidence of compression across
fields, rather than failure to encounter or understand the declaration.

Final leave row 1 has a generic scope_text about assessing twelve months, followed
by a statement that correctly adds provided that the governing rules in
29 CFR 825.110(b) are met. The following rules F006:F009 are assigned as context,
not scope, and the later counting passages F010:F011 are not selected for this
row. The problem includes evidence roles and field consistency, not merely prose.

An additional example missed in the earlier review: final photos row 8 says a
changed hairstyle/facial-hair photograph is acceptable if still a good likeness.
Its scope_text says only when a photograph shows a change; the actual likeness
condition is absent. The scope evidence contains it, so the existing structural
check passes and only logic_requires_review appears on this claim.

The requested and actual field order is kind, scope evidence/text, context,
modal evidence/force, alternatives, choice, logic, references, statement. Thus
scope is written before the complete statement. Baggage shows later compression;
leave shows a qualification appearing later without updating earlier scope.
This makes order a plausible contributor, not a demonstrated cause: no matched
order-only comparison was run, and the model may plan ahead before writing JSON.

The schema deliberately asks statement, scope and choice to repeat overlapping
meaning. It already says ALL and complete repeatedly, including BOTH scope_text
and statement in the prompt. More generic emphasis is therefore a weak next test.
A better test would make the responsibilities and cross-field consistency check
explicit, while preserving a readable complete statement for standalone use.

## 2. Negative classifications lack sufficient semantic distinctions

Final baggage row 5 pairs exact does not prohibit evidence and faithful prose
with exemption / not_required. The model identified the source wording; its
category mapping is wrong. The earlier initial row used statement / not_stated
for the same source. Final leave row 5 maps Nothing in this section prevents to
permission / may. This is unstable classification of related negative phrasing,
not proof that the model cannot recognize negation.

The profile clearly distinguishes must_not from not_required, but offers no
explicit not_prohibited label or worked contrast for removal of a prohibition.
It does have statement / not_stated and uncertain, so the schema does not force
this error. The word exemption also covers several everyday senses. Requiring
exemption to pair with not_required can make a mistaken first category produce
a consistent but wrong second category. kind is written first in every raw row;
anchoring is a plausible explanation, not an observed internal reasoning step.

A related concern extends to baggage row 1: does not apply withdraws a prohibition
for the named cases, yet also receives not_required. The earlier review credited
its correctly limited prose without separately challenging this classification.
It needs the same distinction between absence of a duty, removal of a ban, and
non-applicability of a referenced rule. These should not silently become a broad
permission or be relabeled without a declared interpretation.

The prompt prohibits separate condition/exception records in this pass while
the shared kind enum still includes both, and its description recommends them
as qualifications. That is actual conflicting guidance, although none of the
final 35 rows chose those kinds. Removing this contradiction is sensible; it is
not established as the cause of the ammunition error.

A useful discriminating test is matched invented clauses about required,
not required, prohibited, not prohibited, and a rule not applying, with the
referenced baseline alternately imposing a duty and a ban. Test classification
independently of statement quality before adding a new force or changing order.

## 3. The instructions leave a judgment call about splitting

The prompt asks for distinct actions/forces to be individually referenceable,
complete baseline meanings with all exceptions attached, and coherent statements.
It explicitly allows a whole option list to stay with one duty. It does not give
a precise boundary between an attached qualification and an independently useful
rule nested inside that qualification.

Names row 5 merges the identity fact and possible evidence requirement into one
because sentence. Leave row 3 merges prior-service counting, military-absence
counting and the no-greater-entitlement limit. Photos row 9 retains photo-reuse
as scope alongside its recency caution rather than a separate statement.

The model can split a single supplied passage: names F014 produces suspension
and emergency permission; photos F002 produces head support and head tilt.
Initial leave output also separated the military-absence and entitlement rules,
and initial photos output separated reuse and caution. Passage IDs therefore
nudge grouping but do not impose it. The follow-up changed both schema and
proviso guidance; we cannot attribute reduced splitting to either change alone.

For discovery, some coherent grouping is acceptable and may improve context.
Calling every merged explanatory fact an error overstates the case. It becomes
a product problem when a distinct rule cannot be referenced or corrected alone,
or when one classification inaccurately covers meanings with different force.

A better next test would distinguish an independent rule from a supporting
qualification using shared actors/actions or explicit sentence roles, while
checking that splitting does not strip inherited limits. It need not mean
one sentence per record or a mandatory second model call.

## 4. Exact source selection still allows incomplete semantic support

Final baggage row 3 selects F011 for logic_quote. The resulting exact logic_text
is only (2) Any unloaded firearm(s) unless—. The actual four conditions are in
F012:F015, correctly selected for alternatives and choice. Baggage row 0 selects
just the sterile-area item ending in or as its logical evidence for a three-way
list. Conversely, photos row 8 selects F006, which includes both the recency
recommendation and hairstyle permission, as logical support for the permission.

This suggests selection of a recognizable operator or a convenient paragraph,
rather than consistently selecting the complete logical expression. The schema
already asks for complete wording. The conversion proves the quote is exact,
not that its beginning/end are sufficient or its extra content is irrelevant.
The existing logic_requires_review flag accurately reflects that limit.

A related low-confidence concern: photos row 2 puts white or off-white blanket
into choice_text even though it is part of an example. The words are real; their
semantic role as an example must survive if a consumer treats choices as rules.

Our improvement removed invented logical quotations. It did not establish
complete logical evidence. The previous success description should be read with
that narrower scope. A focused check of dangling lead-ins and selected operands
would test this without pretending keyword matching proves legal logic.

## 5. Why validation allows the semantic failures

core._claim checks allowed kind/modality pairs, exact evidence and the presence
of scope text and quotes. core._scope_record can emit an ApplicabilityScope when
the selected quotations resolve. Neither check compares the meaning of all
conditions against scope_text or statement. Thus exemption / not_required passes
pair validation, and incomplete scope with exact quotations remains grounded.
This is a known validation boundary, not proof that the schemas malfunction.

There is also a separate code-side evidence limitation: final baggage row 3 has
a correct may not classification, but its short modality_quote is ambiguous.
The phrase is outside its main F011:F015 span and occurs in more than one source
passage. Core first tries the main span, then the document; it does not use the
selected F009 governing scope as the next disambiguation range. This creates
component_evidence_unresolved without changing the rule's prose. Reusing already
resolved scope evidence for disambiguation is a concrete implementation candidate.

## Next experiments, without changing the saved runs

1. Contrast negative force and non-applicability with explicit baseline targets.
2. Test field consistency and selection of complete logical support on the saved
   declaration, proviso and likeness cases. Compare an order-only variant if
   testing output order; do not change multiple prompts and attribute causality.
3. Clarify independent-rule versus attached-qualification splitting, checking both
   referenceability and survival of inherited conditions.

No new provider calls or extractor code changes were made during this review.
The original captures and prior judgments remain intact; this note supplements
and narrows the earlier assessment.
