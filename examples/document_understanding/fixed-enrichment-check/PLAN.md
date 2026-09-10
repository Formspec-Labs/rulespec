# Enrich fixed statements without rewriting them

Decision: Does a separate actor/definition enrichment step preserve extraction
meaning while providing useful roles and scoped links at an acceptable marginal
cost? Experiment only; no production adoption or commit implied.

Hypothesis: A response limited to additions keyed by existing claim IDs cannot
rewrite statements; it can still identify actors and definition links correctly.
The no-rewrite property follows from deterministic processing, not superior model
accuracy. Incorrect roles, missing links, unsupported aliases and wrong sense
merges remain possible. A second call may cost more than first-pass enrichment.

Arms: for each case, fresh current extraction (B), fresh actor+index first-pass
extraction (I), and fixed enrichment of B (E). Compare B+E with I for complete
pipeline cost and supported structure, and with B for preserved meaning. Reuse
the preceding index schema unchanged for I. E omits statement output entirely;
its only per-claim fields are claim_id, actor, actor_quote, defines_term and
term_refs, with the same term-index definition. This tests a two-stage bundle,
not the separate effect of prompt, field ordering or schema size.

Cases: exact saved passport UI source, plus a newly authored document with two
locally defined senses of review notice/RN and explicit/unstated actor controls.
The passport source is development data; constructed controls are not an
independent benchmark. Do not reuse frozen oxygen/alarm/procurement sources.
Source-specific criteria are in REVIEW.md and frozen before calls.

Held constant: Gemini 3.8 Flash, temperature 0, low thinking, 16,384 maximum output
tokens, complete source window, one call per cell. Randomize independent B/I
calls and E ordering while respecting B -> E dependency. B/I have identical
existing extraction prompts; E necessarily adds B's fixed claim packet and uses
an enrichment instruction. Six calls maximum, no repairs/retries, stop before
starting another call after twenty minutes. Missing/refused baseline records
remain in accounting; do not silently substitute historical controls.

Decision rule:
- Mechanical: all submitted claim IDs resolve exactly once; term IDs unique;
  references resolve; names have exact source support; existing candidate/Core
  actor evidence checks pass. No statement, source selection, kind, modality or
  pre-existing enrichment may change when applying E.
- Meaning: assess B and I independently on the frozen checks. E inherits all B
  successes and failures; invariance does not repair B's omissions. No material
  new actor/link errors and no checked actor or link omissions in E.
- Benefit: correct actors, definitions/aliases, and all checked scoped usage
  links, with no merging of two RN senses. The same semantic gate applies to I.
- Cost: report B+E versus I input/output/total tokens and request duration, and E's
  marginal cost. Under a bounded quality pass, investigate integration if B+E's
  reported total tokens are at most 2x I; otherwise record a quality/cost tradeoff
  and stop. This is a chosen budget gate, not a dollar-pricing assumption.
- One call per cell cannot establish rates or causation. A narrower improvement
  does not waive a failed broader gate. No automatic production adoption.

Reuse: native CUE, #Actor/#ActorQuote, preceding experimental #DefinedTerm,
passage IDs, current capture, parser, Core compiler and validation. Existing
refinement proposes complete add/edit records and can rewrite statements; this
test needs only an additions-by-ID response and an allowlisted merge. Term links
remain experimental data; no new Core types or UI work. Pin the helper digest,
runtime files, native schemas, inputs and current base commit; do not copy whole
runtimes. Preserve all previous experiments and current UI review history.

Review: inspect randomized opaque B/I statement views before identifying arms.
Then review E/I actors and links against source; their differing format reveals
treatment at that stage. One model reviewer's judgments are revisable, not gold.
Retain failures and full raw outputs. Stop after assessing the six calls.
