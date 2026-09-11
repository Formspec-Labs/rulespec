# Act-resolution policy: exclusion and known multiple targets

Decision: whether the existing native resolution rules need to cover a single
classification outside a named division and multiple source-credit targets when
Table III offers one answer. Fix demonstrated defects in RefSpec; keep Rulespec
as the existing consumer.

Hypotheses:

1. The division exclusion is incorrectly conditional on multiple Table III rows.
   A known page outside a conservative division range remains outside when it is
   the only row. Unknown pages cannot establish exclusion. Before changing this,
   inspect the producer's retained page-range evidence: a stored first page may
   not describe the entire classification, so widening the current check blindly
   could introduce false refusals.
2. Multiple source-credit targets are positive evidence of non-uniqueness, not
   silence. The combined resolver's singular answer should remain unresolved
   rather than treating Table III as a tiebreaker. Retain all native candidates
   and their source identities; do not invent a contradiction when several
   classifications can all be true.

Arms: the current installed implementation, the smallest justified change to the
page rule alone, the multiplicity rule alone, then their composition if both
earn adoption. Existing copied resolver code is the test-only prior oracle.
Compare original result fields separately from evidence added in the preceding
experiment; preserve a list of every deliberate changed result.

Cases: the saved three authority fields and 608 derived authority pairs; all
source-credit keys reachable through indexed act/division names (bound 20,000
distinct act/section pairs); up to 1,000 sorted single-row out-of-division pairs
from the existing index for raw-page inspection. Record total eligible populations
and truncation. Source-derived pairs are diagnostic lookups, not independently
attested mentions or an accuracy benchmark.

Controls: in-range, outside, unknown and boundary pages; one versus multiple rows;
missing division bounds; a narrowed page range crossing the division boundary;
single versus multiple source-credit targets, duplicate rows for one target,
agreement/disagreement and an explicit division conflict. Inspect raw source
rows and publisher XML around affected examples before changing production code.

Held constant: pinned index files and existing loaders, all source bytes, no
provider calls, downloads, corpus rebuild or new parsing dependency. Scan each
bounded population once per arm and reuse captures. Use the current upstream
bulk XML reader to inspect source records instead of writing another reader.

Gate: remove only answers contradicted by the stated scope or multiplicity;
retain source evidence, unknowns and unaffected answers. Unknown or narrowed
page information must not become proof of exclusion. Both targeted and existing
owner/consumer checks must pass. Record narrower decisions separately if one
hypothesis remains unresolved; verify rebuilt wheels and both application commands
before updating the working environment. Stop each comparison at its declared
bound rather than adding cases until it passes.

## Baseline observations and scoped implementation

The bounded lookup census contains 8,174 distinct pairs: all 6,569 reachable
source-credit pairs, the first 1,000 of 562,243 eligible single-row/outside pairs,
and all 608 publication-derived pairs, with overlap removed. It finds 29 accepted
answers despite multiple source-credit targets, and 58 two-source conflicts.
These are native index lookups; most are not observed citation mentions.

Publisher XML confirms that section 1416 of PL 104-201 has a direct Table III
classification to USC 50:2316 and child-section classifications to other titles.
The pinned USLM credits name 1416(a)(1) for USC 10:282 and 1416(c)(1)(A) for USC
18:175a. A singular section-level answer is therefore incomplete even though
that one classification is real. Preserve its identifier as a specifically named
Table III candidate while refusing to select it over the multiple credit targets.

The producer already retains non-single-page spellings in its quarantine table;
33 such rows affect the selected population. They include lists and compound
spellings such as `3009-454`, not only ordinary ranges. Reuse that sealed table
to mark those act/section pages uncertain for exclusion, without writing another
page grammar or rebuilding the corpus. Verify that classifications and quarantine
belong to the same admitted artifact. Missing pages also cannot prove exclusion.
The application must pin this additional input alongside the existing index files.

The first inspection attempt failed because a harness named `inspect.py` shadowed
Python's standard module. It was renamed before collecting `baseline.json`;
both logs are retained. No production change caused that failure.
