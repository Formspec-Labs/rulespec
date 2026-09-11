# RIN candidate representation: fixed-data comparison

Preregistered 2026-09-11 before running the comparison. The prior independent
source review is recorded in
[rin-boundary-review](../../reviews/2026-09-11-rin-boundary-review.md).
This is a deterministic reader/consumer experiment; no provider calls.

**Decision:** whether Rulespec should reuse an existing identifier-space check
for RIN candidates before presenting them as supported reference readings.
Preserve source evidence and refusals rather than deleting unusual values.

**Hypotheses and predictions:**

- H1: the real `1998—Pars.` false positive crosses an intentional difference
  between permissive query recognition and Rulespec's supported identifier space.
  An existing narrower helper should refuse it, preserve supported RIN values,
  and require no change to SpicySearch query parsing.
- H2: a whole-value normalization check alone fixes the false positive.
  RefSpec's existing broad normalizer is predicted to still accept `1998-PARS`;
  this distinguishes normalization from the narrower space check.
- H3: a narrower shape proves the mention means an issued RIN. The constructed
  product code `9999-ZZ99` is expected to disprove this: it fits the supported
  shape but has no corroborated RIN meaning in its source sentence.

**Arms:** A, current SpicySearch RIN candidates and current application scan;
B, those same candidates admitted only when RefSpec `mint_rin_iri` succeeds;
C, the existing Rulespec projection `normalize_rin` on those same candidates.
Also record RefSpec `normalize_rin` as the H2 diagnostic. B and C are alternatives
for the same boundary; no new normalizer, parser mode or model field.

**Cases:**

- The exact saved amendment paragraph and all three frozen USLM sources from the
  readable-text experiment. Preserve the adjacent public-law occurrence.
- Constructed bare/labeled, lowercase, Unicode-dash, repeated and whitespace
  controls; `0648-ABCD`; null/Not Assigned; an Office of Management and Budget
  control number; and a shape-valid product code with explicit product context.
- All five unusual RIN values documented in RefSpec's historical source notes:
  `0648-XD990`, `0648-XC705`, `3090-00XX`, `1115-09AE`, `2070-78AB`.
  Their source attestation is historical; this run does not revalidate issuance.
  Values the baseline scanner never detects remain a known coverage limitation.
- Distinct stated RIN values in the locally available Unified Agenda actions
  artifact, only after the existing verifier accepts its receipt and file hashes.
  Save selected raw rows and declared source editions for context. This measures
  compatibility with that artifact, not recall on arbitrary prose or current law.

**Held constant and bound:** frozen input bytes, exact candidate spans, unchanged
SpicySearch query code, current schemas, one deterministic comparison per input.
At most the three saved sources, the declared constructed controls and the one
local actions table. No source fetches, roster repairs, model calls or timing
claims. Stop once the boundary decision is answered. An invalid or incompatible
artifact remains an explicit limitation, not an empty population.

**Decision rule:** adopt one existing helper if it refuses the real amendment
heading, retains every supported baseline RIN in the verified artifact, preserves
exact evidence for admitted and refused candidates, and leaves other families and
query output unchanged. Differences between B and C must be explained from their
actual inputs before choosing one. Prefer the existing owner with the smallest
consumer/dependency change. Keep successful readings unresolved as to existence;
never describe refusal as proof that an identifier does not exist. A failure of
these checks keeps the change experimental.

**Delivery if adopted:** reuse the existing application rejection path and parser
fingerprints; add actual-source and counterexample regressions; inspect ordinary
and discovery exports; run affected owner/application checks; rebuild and install
the changed wheels outside the checkout. Keep prior captures sealed. Correct the
upstream explanatory overclaims separately; those prose corrections do not prove
the candidate's accuracy. Record source identity, raw results, failures and the
adoption decision. No commits or releases are included in this slice.

## Execution note

The first run completed the constructed controls, then stopped because the
harness incorrectly looked for the two earlier USLM captures in the newer
readable-text directory. They remain in `2026-09-11-uslm-source-links`.
`direct/`, `direct.log` and `measurement.json` preserve that attempt. The retry
uses the same declared source bytes at their actual saved paths and a new output
directory; no cases or acceptance criteria changed.
