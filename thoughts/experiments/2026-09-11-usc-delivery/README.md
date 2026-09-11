# USC references are connected and installed

Committed locally: Rulespec `547157f` and RefSpec `53c0f387`. The exact commits,
parents and staged trees are saved in [commits.json](commits.json).

Rulespec's existing `references` and `discovery-export --references` commands now
use RefSpec's source-occurrence reader. Qualified targets, source positions,
inherited title context and explicit refusals survive the shared Core evidence
path. The application adds no parser or model field. USC display values preserve
source wording; native fields describe the normalized reading.

The final delivery includes the [open-ended qualification correction](../2026-09-11-usc-open-ended/README.md).
Use that directory's [wheel inputs](../2026-09-11-usc-open-ended/wheel-inputs.json),
not this directory's initial wheel receipt. Earlier builds and results remain
available to reproduce the progression.

Verified results:

- 579 application tests pass from source and from the final isolated installation.
- 503 upstream owner tests pass, with 14 slow tests deselected. The installed
  focused USC suite passes 116 tests, including unchanged-output comparisons.
- The same 31 inputs retain 63 accepted and six refused USC occurrences through
  both exports. These are selected diagnostic counts, not accuracy estimates.
  All prior-family readings, default discovery output and publisher targets stay
  unchanged. The publisher fixture adds six associated USC text readings.
- All seven wheel filesets match the final isolated and working installations.
  The two changed package sources match the wheels. Captured source identities
  change only for application `references.py` and RefSpec `citation_grammar.py`.
- The normal saved-response fixture retains its four accepted claims and no
  rejected claims. Reprocess/replay completes with no provider call; review content
  and graph content remain unchanged except the recorded run and its lineage ID.
  Negative comparison controls reject changes to lineage content and source quotes.
- Working and isolated CLI outputs match byte for byte. The original sealed
  retention and runtime-capture manifests remain intact.

Final receipts are `isolated-open-ended-01-packages.json`,
`working-open-ended-01-packages.json`, the matching `*-comparison` directories,
and `run-checks-isolated-open-ended-01-working-open-ended-01.json`. The initial
578-test runs predate the added open-ended counterexample and remain historical.

## Additional historical capture checks

The normal replay fixture contains no USC mention. A further positive CLI check
first selected a research cell whose manifest omits required artifacts. Both the
old and new installations refuse it; see `cli-usc-positive-01`. We did not alter
its capture or bypass validation.

The first manifest-complete USC example supplies the real
`38 U.S.C. 4301, et seq.` failure. Both installed commands now retain that entire
phrase with an unresolved open-ended-reference reason. However, this historical
model response uses an older unit schema: both the earlier installation and the
new one withhold all 17 old units and retain the same 18 parsing refusals.
The reference export succeeds independently of those units, as designed. This
additional case proves the positive reference path, not successful extraction
under the current schema. The separate
[processing review](../2026-09-11-usc-open-ended/processing-status-review.json)
records the distinction. A zero CLI exit code alone is not processing success.

R6's selected reader integration is delivered. General target existence and
edition lookup, unsupported qualification forms, document-local references,
broader untouched evaluation and the remaining R1–R26 work stay open.
