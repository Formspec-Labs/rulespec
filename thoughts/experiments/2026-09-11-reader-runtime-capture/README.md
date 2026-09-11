# Reference-reader runtime capture

The source implementation now records the two application adapters, supported
installed RefSpec/SpicySearch reader and helper files, and both package versions
through the existing runtime capture. No new format, registry, model field or
mandatory dependency was added. The rebuilt wheel is installed and verified in
both the isolated and working environments.

The [design](design.md) defines the boundary: capture supported readers that are
installed, not an exact function-execution trace. A reader change may therefore
cause strict replay drift even for a plain-text run. Existing `reprocess` creates
a new processing result while preserving original captures and review history.

The recorded installed baseline fails the missing-reader coverage control as
expected. The new source passes five controls for coverage, reader/helper mutation
and restoration, optional-package absence, and a broken transitive dependency.
Its full source and isolated installed suites each pass 559 tests, with no skips.
Normal reprocessing, replay, reference/discovery export and review export pass.
These checks establish capture and replay behavior; they do not measure extraction
accuracy. See the [source log](source-suite.log),
[installed log](cli-isolated/application-suite.log) and
[working delivery checks](working-checks.json).

- [x] Record the baseline before implementation and demonstrate the coverage gap.
- [x] Extend the existing source/version capture and pass direct-import controls.
- [x] Reprocess the normal saved run and verify unchanged candidates, refusals,
  source/reference exports and review content. The graph differs only in its
  run-derived lineage ID and links to it, as explained below.
- [x] Build the changed extractor wheel, test it outside the checkout, and update
  the working environment only after those checks pass.
- [x] Record installed equality, retained original evidence and the final manifest.

The first graph comparison incorrectly demanded raw byte equality after changing
the run record. `core.build_graph` derives `AILineage` identity from that complete
record. The revised comparison verifies each ID against its run and permits only
that ID/link substitution; all other fields must match. Controls confirm changed
model provenance or fabricated source text still fails. The failed verifier/log,
original design and appended clarification remain saved. This is an instrument
correction, not a production graph modification or a claim of raw graph equality.

The [wheel inputs](wheel-inputs.json), [build/install commands](build-install.json),
[isolated commands](isolated-delivery-command.json),
[working commands](working-delivery-command.json) and
[working installation](install-working.json) identify the delivered code and checks.
All seven wheel filesets match both installations. The extractor's source files
match its wheel. Existing captured sources differ only in `extraction.py`; eleven
source files and two package-version entries are added. Original retained captures
and the preceding experiment's manifest remain unchanged. No provider calls,
commit, push, publication or deployment occurred.

The preceding [retention delivery](../2026-09-11-extraction-retention/README.md)
is sealed separately. Qualified USC and other reuse candidates remain on the
[canonical task list](../../plans/2026-09-10-reference-integration-task-list.md).
