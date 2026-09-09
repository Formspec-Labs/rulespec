# Default configuration workflow check

Decision: verify that the promoted CLI defaults work through a complete live
extraction, source inventory, comparison and offline replay.

This is a configuration smoke check, not a semantic improvement experiment. There
is no provider-default control arm and no claim about relative cost or accuracy.

Input: the existing 2,536-character passport introduction from
`../audit-mutation-sensitivity/fixtures/passport.json`, `book.document`.
Source SHA-256: `a150f4ee3b06251ce1b4533a18231db38769787697dbaee26861e227c43e353a`.
This is reused development data with a known standalone qualification weakness.

Run the existing CLI without thinking, window, temperature or output-limit flags.
Expected extraction: low thinking, temperature 0, 24,000 characters, 16,384 tokens.
Expected inventory and comparison: medium thinking, temperature 0, 3,000 characters,
32,768 tokens. No numeric thinking budget. Model: `gemini-3.8-flash`.

Bound: one extraction, one inventory and one comparison request, at most three
provider calls. Existing five-minute request timeout applies; no retries, repairs
or follow-on model calls. Stop on a failed phase and preserve its capture.

Acceptance: inspect actual requests and metadata for those settings; the source
fits one window in each stage; processing completes, the graph validates, discovery
retains source/logic, and extraction/audit replay without provider calls. Audit
semantic verdict may pass or fail; `semantic_completeness` remains `not_established`.
Review raw statements and audit rationales against the source, recording omissions
and uncertainty separately from configuration verification. Preserve all captures.
