# Fresh official sources: choose an actor/definition integration path

Decision: choose combined first-pass extraction versus fixed enrichment for the
initial supported actor/definition workflow. User has authorized making and
implementing the engineering decision; experiment conclusions still govern scope.

Hypothesis: fixed enrichment provides supported structure without changing saved
meaning; combined extraction may be cheaper but may change completeness. Compare
both, including all baseline failures, rather than assume either is more accurate.

Arms: unchanged B/current, I/combined actor+index, and B+E/fixed enrichment from the
preceding experiment. Reuse its exact schemas/prompts, capture, merge and Core.
Only source cases change. Read complete selected sections, not hand-picked clauses.

Cases: official eCFR 21 CFR 11.3 plus 11.10 (electronic records) and 14 CFR 107.3
plus 107.19 (small unmanned aircraft), displayed as of 2026-09-04. These sections
were not previously used by this extractor's saved source tests. Original web
retrieval and normalization notes are saved. XML retrieval failed; use the saved
official rendered section bodies. These are selected section bundles, not whole
regulatory parts and not a population benchmark. Criteria in REVIEW.md precede
model calls. Never tune prompts after results.

Held constant: Gemini 3.8 Flash, temperature 0, low thinking, 16,384 output cap,
one complete source window per bundle, one call per arm/case, six calls maximum,
twenty-minute bound before another call starts. B/I order randomized; E follows
B. No retries/repairs. Keep failures and refusals. Same runtime and pinned helper.

Decision rule: require source-supported actors on directly checked duties, null
for unnamed designation actor/definitions, correct definition subjects and key
usage links, no invented definitions, no dropped governing scope in I relative
to B, and strict no-rewrite for E. Record every missing role/link rather than
equating valid IDs with correct meaning. If both satisfy structure checks, prefer
the cheaper combined path for new drafts; preserve a fixed-enrichment route for
existing reviewed material. If combined introduces a material checked error,
choose fixed enrichment provided its added structure is sound and B+E uses at
most twice I's reported total tokens. If neither clears all semantic checks,
ship only conservative evidence-validated structure with explicit unresolved
items and document the narrower scope; do not claim a passed broader gate.

Assess statements from opaque views before reading arm names; inspect actors and
links separately afterward. Review judgments are revisable model labels, not
gold. Read every row. Exact replay verifies processing, not semantic accuracy.
