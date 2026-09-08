# Finish the document extraction schema integrations

The remaining local work is concepts and assignments, source attribution, typed
values, and explicit effectivity. Preserve evidence, immutable revisions, review
history, and raw captures. No UI, registration, publishing, or legacy adapters.

Implementation sequence:

1. Import Core CUE definitions into the application schema at build time. Keep
   document interpretation in the profile, with concepts first in each unit.
   Compile with native CUE and fingerprint the imported Core sources.
2. Carry optional concept, claimant, typed-value, and effective-period records
   through candidates, exact evidence checks, refinement, and review identity.
3. Emit LocalConcept/ConceptScheme and actual content-derived release manifests;
   reuse the shared assignment construction and release digest implementation.
   Local concepts do not claim RefSpec registration or identity.
4. Emit SourceClaimant separately from actor. Typed values retain lexical source
   evidence, comparators, units, and relative reference events. EffectivePeriod
   only represents explicit in-force timestamps; never infer one from a deadline.
5. Exercise unsupported evidence, invalid values, corrected meanings, release
   membership/digests, review history, and the live Gemini endpoint with replay.
6. Update the active schema-usage checklist with results and actual boundaries.

Semantic interpretation remains provisional. Schema validity and exact quotations
check representation and grounding; they cannot prove completeness or correct
interpretation. RefSpec mappings, authority chains, calibrated confidence, and
product lifecycle links need their actual inputs/consumers before integration.

## Execution checkpoint

Implemented all four structured collections, direct native Core CUE imports,
shared concept assignment construction, packaged Core data/digest reuse, exact
nested evidence, review/refinement carriage, and dedicated audit dimensions.
The existing Core schemas were sufficient; no upstream schema was duplicated.

Validation: 301 tests and 101 subtests passed before two additional tests were
added; those tests also passed in a 45-test focused run. Native generation and
installed wheels passed. Fresh Gemini 3.8 Flash runs at temperature 0.2 accepted
12 passport units and 6 invented-policy units with no parser/compiler refusals.
Both replay exactly. The passport extraction retains all six documentary options
and the important inherited >1-year/DS-11/unchanged-ID conditions.

The independent audit completed its provider calls and correctly flagged two
source-attribution errors. Its semantic result is failed, with 17 covered and
2 unknown inventory units; no semantic-completeness claim. The refinement trial completed in a separate copied review workspace. The first reuse attempt was
refused because a raw-rulebook audit is not an audit of the augmented review
snapshot; the new trial obtains the correct snapshot audit automatically.

The trial applied three corrections: remove the two unsupported claimant
attributions and add an explicit exception link. It retained one refused proposal
and one unsupported proposal as unapplied, so the run is partial. The final audit
passed its assessed 18 units. Strict refinement replay verified all three events
with zero provider calls. This is the natural stopping point; no further model
iteration is running.

Raw captures and original review histories remain intact. Final results are in
examples/document_understanding/schema-reuse-finish/README.md. Implementation
commit: `2e60fb8`. Research and replay evidence are saved in the following commit.
No push or release is included.
