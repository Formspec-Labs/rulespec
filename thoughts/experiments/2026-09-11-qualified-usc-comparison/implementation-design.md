# R6: source occurrences from the existing authority matcher

Decision: add a RefSpec USC occurrence API and use it through Rulespec's existing
reference adapter once qualified targets and refusal controls pass.

Hypothesis: recording source matches before the authority reader deduplicates them
will preserve repeated references, original positions and qualifications without
introducing another USC token parser. An adjacent prose-list walk can avoid the
observed application-count false positives while preserving qualified list items.

Comparison: the frozen R5 outputs versus the new occurrence API on exactly the
same inputs. Keep the old whole-field reader as a copied test-only oracle; its
existing consumers have a distinct, measured list policy. Require unchanged
identity-only output on all frozen inputs and on additional real authority strings
and mutations. No deliberate old-API output changes are planned in this slice.

Reuse: `AuthorityCitation`, the authority matchers and range interpretation,
`usc_title_is_possible`, existing pinpoint-label handling, source-note spelling,
and the CFR occurrence-recorder pattern. Add occurrence metadata only where the
source needs it: original span/text, pinpoints at either range endpoint,
subchapter qualification, context for inherited list items, and an explicit refusal.
The occurrence path can consume a comma before the existing note suffix and
apply that suffix to appendix and listed citations. Its richer reading does not
change the separately published whole-field result. Preserve whole-value label
repair for field consumers; do not run it when original source positions matter.

Controls: every R5 input, plus adjacent lists containing pinpoints/notes, repeated
sections with different pinpoints, range-end pinpoints, Unicode boundary damage,
ordinary prose between a reference and numbers, chapter-range ambiguity,
another explicit citation after a range separator, bare titles/appendices, and
real authority-field list continuations. Read source before labeling additions.
Do not infer missing titles, enumerate range interiors, or treat parse status as
title validity or legal existence.

Gate: complete written targets and exact original positions on the frozen
positives; no accepted shortened damaged token, invented count-as-section or
silently broadened qualification on controls. Preserve prior field-reader outputs
exactly. Use existing Core evidence and sparse reference output; no model-facing
schema, prompt, model call, recursive lookup or UI change. Test direct imports
before building an upstream wheel and exercising the same Rulespec commands from
an isolated installation. Keep production adoption separate from a passing native
prototype. Stop and record a failed gate rather than quietly narrowing it.
