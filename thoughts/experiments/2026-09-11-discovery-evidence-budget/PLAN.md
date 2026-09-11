# Discovery evidence after source ranking

Decision: does the existing evidence expansion improve a bounded discovery result,
and does ordering direct hits before expansion avoid useful text being displaced?

Hypotheses: inherited conditions and grouped source quotations can complete a
short hit without changing ranking. Alternatively, the evidence may be missing,
too broad, or consume the budget before another direct hit. If the useful passage
is not ranked, expansion may not recover it. These are distinct failure mechanisms.

Arms: A uses `discovery.records(..., 'source')`. B uses the current `packets`
evidence in hit order. C uses the same packet evidence, placing the direct source
evidence of all top-three hits first, then their additional evidence in hit order.
All rank the identical source text using the unchanged `discovery_trial.search`.
C changes allocation order only; no new context, inferred relation or generated
prose is added. Each arm has 1,500 unique source characters. Admit or omit whole
evidence fragments; never truncate a condition to fit. Deduplicate coordinates
within their pinned source identity. Retain admitted/omitted fragments and full
rankings. Also measure uncapped support to distinguish budget from missing links.

Cases: eight newly authored questions plus four original diagnostic controls on
the four prior retrieval documents and one additional retained title-20 chapter.
Use the first baseline model observation reprocessed with the delivered retention
fix for title 20, not a chosen best response. The whole chapter remains searchable,
including editorial material and unprocessed sections. Questions are source-read
before ranking, with exact required source intervals frozen in `queries.json`.
These are development sources and agent-authored queries, not untouched documents
or real-user labels. Preserve original control labels even where they are less
complete; report the two groups separately. No sealed holdout is opened.

Controls: remove all statements; duplicate a statement; supply fabricated context
that cannot verify; use equal text with different source identities; verify the
budget and whole-fragment behavior; check native exact lookup, ambiguous editions
and an unresolved target through the current optional RefSpec adapter. Native
lookup is a separate capability check, not part of the lexical score or evidence
expansion. Existing feedback persistence has already been delivered and will not
be retested as a new finding here.

Held constant: same books/source maps/statement versions, tokenizer/ranker, top
three, one deterministic comparison plus exact replay, no provider calls or new
dependencies. Freeze code, settings, queries and source hashes before scoring.
Stop after the fixed cases and controls; do not adjust ranking, labels, budget or
ordering after results. Record runtime and bytes, not hypothetical token charges.

Decision rule: recommend a bounded consumer trial of B or C only if at least two
of the eight new questions gain all selected required support over A, no new
question loses any required support A retained, no original control regresses,
and evidence/identity/refusal controls pass. Compare B/C separately. A budget that
never binds cannot show constrained-context value. Equal support at higher cost
is no measured gain. Failing or inconclusive results keep the production paths
unchanged. Even a passing result does not prove complete legal answers, human
time saved or embedding performance; those require the actual consumer trial.

Reuse `discovery.records`, `source_slicer`, exact evidence validation and the prior
retrieval harness's source-coordinate support accounting. Keep any display-budget
code inside this experiment until a named production caller needs it. R17/R24 stay
open beyond this bounded result, and the full cross-repository reuse goal remains.

Preflight clarification, before any ranking or result collection: selected support
can span several paragraphs whose blank separators are not part of a retrieved
passage. Score coverage of every non-whitespace source character within the frozen
required intervals. This avoids crediting expansion merely for copying blank
separators. Evidence validation and budgeting still use exact, complete original
fragments including their whitespace; no fuzzy or content-changing match is used.
Original preflight code/plan/freeze are retained. Query labels and allocation rules
are unchanged. The N6 support selection itself exceeds 1,500 source characters;
report that feasibility limit, not an extraction omission.
