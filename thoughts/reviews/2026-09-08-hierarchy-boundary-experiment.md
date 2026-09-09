# Hierarchy and window boundaries: parser fix and next step

The core parser had a reproducible structural defect. In CFR-style lists,
`(b)` could become a child of the previous `(3)`, numbered children lost their
lettered parent, and `(ii)`/`(iii)` lost their numbered parent. Corrected
`documents.source_passages` to distinguish dotted-letter and parenthesized-letter
list styles and recognize Roman grandchildren. Source text, offsets and passage
identities stay unchanged. Seven context tests, including the saved baggage and
leave lists and a split Roman child, pass; the package suite passes 308 tests.
The parser remains a bounded text heuristic, not a general legal-scope parser.

The live experiment compares the corrected parser with and without model-facing
parent aliases. Both variants use the same source text, schema, instructions and
context selection. Whole versus split processing is a separate comparison. Two
repeats on baggage and a new invented permit document produce sixteen runs and
24 planned provider calls. The parser correction is not being compared live to
the old parser, so model gains cannot be attributed to that correction here.

Preflight already establishes a separate input-completeness defect. At the
selected baggage boundary, one request lacks the lock/key condition and the
other lacks the declaration. Neither request sees the whole four-condition
firearm rule. The first permit request similarly lacks the storm authorization
condition; its second request receives the complete storm rule as focus plus
context. Parent hints cannot supply missing source text.

Proposed next implementation, supported by the completed source review:

1. Reuse the corrected source passage tree to avoid splitting a governing list
   when that entire group fits within the configured window limit. Prefer an
   earlier boundary before the group, preserving exact source offsets.
2. Keep the context budget explicit. When a group cannot fit, test supplying the
   governing lead-in and complete condition list as context; preserve an explicit
   record of anything still unavailable. Structural siblings are source context,
   not automatic legal conditions.
3. Compare identical documents before/after that boundary change. Check complete
   conditions, unrelated-scope leakage, duplicates, source availability, token
   usage and provider completion separately. Include the present failed captures
   and whole-document controls; preserve originals.

Final verification: all sixteen runs replay exactly, including six partial
outcomes. All eight whole-document runs complete; six of eight deliberately
split runs exhaust the token allowance in their second request and return
malformed JSON. The 162 accepted statements pass Core graph validation. Usage
is 250,785 reported tokens, including thinking, across 24 calls with no retries.

Parent hints improve some scopes but do not produce consistent overall gains.
Keep them experimental. In every first baggage split result, the model drops
hard-sided-container wording despite receiving it as context, in addition to
lacking the lock/key clause entirely. The one completed second permit request
receives the entire storm rule but fails to retain its wind and authorization
conditions as an explicit complete exception. Both input preparation and use of
supplied context need improvement.

The next boundary change is now concrete: earlier cuts at baggage position 1376
and permit position 1034 would keep each targeted governing list in focus with
the same two requests and unchanged character limits. These proposed ranges
were checked deterministically; they have not been implemented or sent to the
model. The experiment does not prove that boundary changes will resolve every
semantic or completion defect.

The [experiment README](../../examples/document_understanding/hierarchy-boundary-experiment/README.md)
links the parser comparison, exact request windows, input availability, ten raw
source-review findings, replay verification, token accounting and candidate
boundaries. Original captures remain unchanged. The parser fix is local and
uncommitted; no model-facing hierarchy change was adopted.
