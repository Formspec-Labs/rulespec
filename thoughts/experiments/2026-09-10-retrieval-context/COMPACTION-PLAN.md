# Display overlapping evidence once

Decision: whether exact source-coordinate union is a useful display-only reduction
to take forward. Experimental permission does not authorize production adoption.

Hypothesis: repetition comes partly from overlapping source intervals, including
trimmed quotations inside whitespace-padded passages. Combining overlapping
intervals should reduce displayed characters without deleting any selected source
character or evidence reference. Disjoint passages must stay separate, even if
their text is identical. This cannot repair missing dependency links.

Arms: saved run-02 C packet assembly versus the same statement and selected
source positions displayed once per overlapping interval. Do not trim source,
merge across gaps, merge adjacent intervals, rewrite claims, or infer shared scope.
Retain original spans/roles and point each display block to its contributing span
indices. Keep each document separate. Use existing saved packets and document
validation; no new extraction or production schema.

Cases: all six corrected saved comparisons, plus constructed counterexamples for
nested ranges, partial overlap, gaps, adjacent ranges, identical words at different
positions, Unicode offsets, separate documents and invalid quotes.

Held constant: inputs pinned by run-02 hashes; no model calls; one deterministic
pass and one replay to a separate directory. No post-result algorithm tuning.

Decision rule: all saved cases preserve exactly the selected source positions,
unchanged statements, every original span/role, and exact document slices; every
counterexample must pass. At least one real saved case must get smaller, and none
may get larger. Report all six sizes, not just the best. Passing establishes a
bounded lossless display reduction, not better semantic accuracy or paid-token
savings. If any condition fails, do not propose adoption under this gate.

Stop after raw-display review and replay. Separately inspect existing dependency
selection and audit behavior before proposing a fresh semantic experiment.
