# RIN recognition: reuse the existing identifier-space check

Reviewed 2026-09-11. This records an independent read-only assessment by
`rin_boundary_review` and the parent agent's source verification. No experiment,
parser change, wheel build or model call was performed for this review. The
recommendation is a hypothesis to test, not a verified accuracy improvement.
The implementation tasks remain in
[R7 of the comprehensive task list](../plans/2026-09-10-reference-integration-task-list.md#r7--evaluate-the-remaining-reference-families-individually).

## Observed failure

The saved [USLM source](../experiments/2026-09-11-uslm-readable-text/fresh-title-05-pair.xml)
contains this entry inside the amendments note, between entries for 2007 and 1982:

> 1998—Pars. (6), (7). Pub. L. 105–264 added pars. (6) and (7).

The application reports `1998-PARS` as a Regulation Identifier Number (RIN).
Here the source describes amendment paragraphs. The neighboring public-law
reference is a distinct real occurrence and must survive any correction.
The original source and output remain in the sealed
[readable-text experiment](../experiments/2026-09-11-uslm-readable-text/raw-review.md).

## Existing code and what it establishes

| Existing API | What it does | What it does not establish |
| --- | --- | --- |
| SpicySearch `detect_identifiers` | Finds permissive shapes and exact spans; normalizes case and dashes | That a mention is intended as a RIN, or an identifier was issued |
| RefSpec `normalize_rin` and SpicySearch `is_regulation_identifier_number` | Check the whole value against the permissive shape | A narrower check that rejects `1998-PARS` |
| RefSpec `mint_rin_iri` | Checks whether a normalized value fits the supported `rkaf:us-rin` identifier space, then creates its IRI | Issuance, roster membership, source meaning or target text |
| Rulespec projection `normalize_rin` / `canonical_rin_iri` | Already implement the narrower shape; an alternative existing helper | A corroborated identity or a general source occurrence reader |
| RefSpec `corrected_rin(value, roster)` | Requires a unique roster-supported correction for the damage forms it handles | General existence checking; it declines already shape-valid input |

The independent review's recommended boundary is the small Rulespec consumer
loop: apply RefSpec's existing minter to RIN candidate values and retain a refusal
when it returns `None`. The parent also verified the narrower Rulespec projection
helper above; do not overlook it or introduce a duplicate normalizer. Prefer an
already compatible owner/API after checking dependency and provenance costs.

If adopted, keep the existing source/evidence record and use a precise reason such
as `rin_outside_supported_identifier_space`. Keep successful values as candidates;
do not change `target_resolution` merely because an IRI can be constructed.
Record the native helper alongside the other parser fingerprints. This needs
neither a new model field nor a change to SpicySearch's permissive query default.

RefSpec's private `citation_grammar._RIN_TOKEN` is a guard inside U.S. Code list
parsing, not a public RIN occurrence reader. It is not a replacement scanner.

## Counterexamples and limits

- Preserve supported identifiers with labels, lowercase spelling, Unicode dashes
  and repeated occurrences. Check the normalized candidate, not an entire sentence.
- The existing case `0648-ABCD` passes the permissive shape but cannot be expressed
  in the supported identifier space. A precise refusal should remain visible.
- RefSpec's historical source notes identify `0648-XD990`, `0648-XC705`,
  `3090-00XX`, `1115-09AE` and `2070-78AB` as published RIN values outside that
  space. Their publisher evidence was not revalidated in this review. They are
  necessary counterexamples to “refused means nonexistent”; some are already
  outside the scanner's shape and cannot be recovered by a downstream check.
- A constructed product code `9999-ZZ99` fits the supported shape. It demonstrates
  why shape acceptance cannot establish issuance or the meaning of a mention.
- Preserve Office of Management and Budget control numbers as non-RIN controls.
  Do not broaden identifier syntax merely to rescue one unusual value.

The next comparison should use fixed source/output data, unchanged query defaults
and exact evidence. Verify any roster artifact before making population claims.
No comparison has yet shown an end-to-end accuracy improvement from this proposal.

## Upstream explanations to correct

1. **Scope of the format evidence.** RefSpec's
   [identifier-shape comments](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/identifier_shapes.py:362)
   correctly limit the Fish and Wildlife Service statement to that agency.
   The [minter introduction](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/iri_minting.py:129)
   and [REF-054 discussion](/Users/mikewolfd/Work/RefSpec/docs/decisions.md:4383)
   overgeneralize it into a publisher-wide rule. Correct the explanation without
   silently changing the recorded decision or the supported identifier space.
2. **Actual refusal mechanism.** The
   [published-exception test](/Users/mikewolfd/Work/RefSpec/tests/test_iri_minting.py:443)
   attributes refusal to missing roster corroboration. The
   [minter](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/iri_minting.py:562)
   receives no roster and checks syntax only. Fix that explanation upstream.

Additional implementation pointers:
[Rulespec candidate loop](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/references.py:61),
[existing Rulespec normalizer](../../packages/rulespec-projection/src/rulespec_projection/citations.py:417),
[SpicySearch detection](/Users/mikewolfd/Work/spicysearch/src/spicysearch/identifiers.py:1286).

## Subsequent resolution

The [controlled comparison and installed result](../experiments/2026-09-11-rin-reference-space/README.md)
now implement the proposed consumer check and correct the upstream explanations.
Both existing narrow helpers preserved the verified artifact's 46,562 distinct
RIN values; the constructed product-code counterexample still disproves identity
from shape alone. The initial review above remains its historical assessment.
