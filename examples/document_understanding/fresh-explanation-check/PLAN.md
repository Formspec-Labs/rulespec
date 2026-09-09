# Fresh-source explanation accuracy check

Decision: do dedicated logic or modality explanations improve extracted meaning
on new documents enough to justify further evaluation before production adoption?

Observed: previous development-source trials reduced empty-field overhead while
retaining notes, but did not demonstrate a dependable accuracy gain. Notes might
help preserve rule structure; alternatively they may merely restate an extraction
without repairing it, add unsupported interpretation, or consume more tokens.

Four arms per source, twelve fresh calls total:
- baseline: exact current statement-first production schema and prompt.
- omit_only: the tested non-null optional enrichment policy, without a note.
- logic_explanation: exact tested scoped-enrichment logic variant.
- modality_explanation: exact tested scoped-enrichment modality variant.

The last three use the same omission prompt. Native CUE generation must show that
each note variant differs from omit_only only by its one required-nullable first
property. This separates note effects from omission cleanup. No guidance is tuned
to these documents and no output-driven schema/prompt changes are permitted.

Sources: full official eCFR sections 14 CFR 91.211 (oxygen), 29 CFR 1910.165 (alarms),
and 2 CFR 200.320 (procurement), version 2026-09-04. No prior occurrences of their
section numbers/titles were found in document-understanding experiments, thoughts
or extractor tests before retrieval. This is repository freshness, not a claim of
model training-data novelty. Now freeze these sources as evaluation data; do not
use their outputs for another round of prompt tuning. They are three selected
sections, not a random corpus sample or a long-document benchmark.

Held constant: Gemini 3.8 Flash, temperature 0, low thinking, 16384 maximum output
tokens, full single-window input, production parser/Core. One repeat per cell;
randomized dispatch and opaque output IDs. Stop after twelve calls, with no retries,
repair passes or audits. Prior experiments remain historical context. No production
adoption or commits are included. A failed/unfinished call stays in the accounting.

Before calls, freeze REVIEW.md from the source text. Review each standalone
statement and relevant modality label under opaque IDs with notes and arm labels
hidden; save judgments before reviewing notes or unblinding. Notes/evidence in
other records cannot repair missing qualifications. Assess logic and modality
checks separately, preserve false positives and secondary issues, and report
reviewer uncertainty. These are revisable Codex judgments, not human gold.

Decision rule for each explanation field: for a positive accuracy signal, repair
at least two predeclared field-relevant checks across at least two sources compared
with both baseline and omit_only; no new named-check failures on any source and
no unsupported material note interpretation. A gain only against baseline cannot
be attributed to notes if omit_only also achieves it. All arms passing a check is
a ceiling, not improvement. Report token overhead separately; a qualifying signal
would justify a larger evaluation, not automatic adoption. If no signal meets the
gate, leave explanations out of production and stop this hypothesis branch.

Save XML, deterministic prepared text, URLs/date/digests, source-review criteria,
schemas/runtime hashes, exact requests/responses and failures. Verify processing
with zero-provider replay. Schema validity never establishes semantic completeness.
