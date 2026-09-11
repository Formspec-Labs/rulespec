# Keep a publisher occurrence and its distinct text readings together

**Decision: adopt unique full containment.** The
[preregistered comparison](design.md) associates all four previously repeated
public-law rows while preserving every native reading, target, disposition and
shared discovery evidence entry in the selected cases. The rebuilt wheels and
working installation are verified with the independent
[RIN representation fix](../2026-09-11-rin-reference-space/README.md).

| Saved source | Associated text readings before | After | Remaining separate text readings |
| --- | ---: | ---: | ---: |
| Title 5 section 423 | 16 | 18 | 0 |
| Title 42 section 242c | 33 | 34 | 0 |
| Title 5 sections 302/5721 | 24 | 25 | 1 rejected RIN reading |

All 107 publisher occurrences and their target information remain. The four
additional associations place a shorter mention such as `Pub. L. 113–235`
inside its full publisher label `section 1301(b) of Pub. L. 113–235`. The parser
reading still names the law; the publisher still names a particular section.
The change does not assert that those targets are equivalent.

Eleven constructed controls cover repeated, nested, coextensive, adjacent and
empty links; two readings inside one link; disagreeing targets; rejected readings;
boundary crossing; and a reading after an already closed child link. Ambiguous
nested associations stay separate. A publisher target `/us/pl/89/554/s2` retains
its conflicting parsed reading `Public Law 94-183`. A contained `99 CFR 1.1`
keeps its `cfr_title_impossible` refusal. These raw cases were manually inspected.

The first comparison checked an independent exhaustive oracle's association
count. Before closing the gate, the same oracle was strengthened to check the
identity of each containing publisher occurrence as well. Both runs remain saved;
the acceptance requirement and inputs did not change.

## Implementation and cost boundary

The application sorts existing publisher text intervals once and records their
enclosing anchors. XML intervals are nested or disjoint. Each text lookup uses
binary search followed by its enclosing-anchor chain, stopping after finding two
possible owners. For R publisher links, M text readings and maximum publisher-link
nesting depth D, the added work is O(R log R + M(log R + D)), with O(R) indexing
space. It does not scan every XML node per reference or add a parser dependency.
The exhaustive O(RM) oracle is test-only on these small captured cases.

Both arms use the same separately adopted RIN behavior, unchanged source maps,
native readers and source bytes. [The copied baseline](uslm_before.py) is the
test-only previous association implementation. No provider calls, model fields,
target-resolution decisions or review meanings changed. Reduced repeated rows are
a representation benefit, not a demonstrated extraction or discovery-quality gain.

## Evidence

- [Original comparison reports](direct/reports.json).
- [Comparison with exact-owner oracle](direct-owner-oracle/reports.json) and
  [final comparison checks](direct-owner-oracle/checks.json).
- Each output directory contains both full native scans and discovery exports
  for every case; [comparison code](compare.py) reverses only association when
  checking preservation of the complete native readings.
- [Application tests](../../../packages/rulespec-extrapolator/tests/test_uslm.py)
  and their [shared controls](../../../packages/rulespec-extrapolator/tests/fixtures/uslm/containment.json).
- The combined source and isolated-wheel suites each pass 523 application tests.
  [Shared delivery verification](../2026-09-11-rin-reference-space/delivery-verification.json)
  checks all 24 CLI artifacts and both installations; the
  [final receipt](../2026-09-11-rin-reference-space/verification.json) pins this slice.

The earlier [USLM delivery](../2026-09-11-uslm-readable-text/README.md) remains
sealed with its original four-overlap finding. This experiment records their
subsequent resolution, rather than rewriting that result.
