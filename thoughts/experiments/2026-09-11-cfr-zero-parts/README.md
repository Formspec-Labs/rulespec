# Published CFR part zero now mints correctly

RefSpec's `mint_cfr_iri` incorrectly rejected part zero by applying the positive
title-number rule to parts. The existing Rulespec identifier space already allows
zero. The fix preserves that value while removing leading padding; title zero
and malformed part strings remain rejected. No schema or dependency was added.

This corrects an exposed RefSpec utility. The current Rulespec CFR scanner does
not call it, so this is not a measured extraction-quality improvement or a graph
parser migration. The independent [complete-range gate](../2026-09-11-cfr-whole-tokens/README.md)
remains unmet.

## Evidence and checks

[Design](design.md), [publisher XML witnesses](source-cases.json),
[complete index comparison](comparison.json) and compressed raw results
(`index-results.jsonl.gz`) preserve the comparison. All nine indexed part-zero
titles—15, 16, 19, 24, 28, 29, 31, 38 and 47—have corroborating publisher XML.
Title 15's part is reserved; the others include organizational or conduct text.
Each witness retains its source hash, part location, heading and available first
section context. The XML hashes match the pinned publisher manifest.

- On 8,424 structured OFR index keys, mintable keys increased from 8,226 to
  8,235. All nine changes are part zero; all 8,415 nonzero keys are unchanged.
  The remaining 189 compound keys remain refused. These counts do not include
  parser truncations and must not be compared as equivalent to parser output.
- The 62 new cases retain the copied old check and name the deliberate zero
  divergences, including padding and constructed zero-stem letter forms.
  Before the fix, 38 failed and 24 passed. Afterward, these and the existing
  minter tests pass: **112 passed** from source and the isolated installed wheel.
- The extractor source suite passes **585 tests**. A saved reference scan has
  identical candidate data after installation. Its minter module fingerprint
  changes as expected; the scanner's RIN helper shares that module.
- Both isolated and working environments verify all **406 Python files** in
  the seven pinned wheels, including all nine source-backed zero mints.
  Dependency checks pass. **Zero model calls** were made.

The [wheel inputs](wheel-inputs.json), [isolated verification](verified-isolated.json)
and [working verification](verified-working.json) record the installed builds.
The rebuilt RefSpec wheel is
`dist/reference-integration-20260911-cfr-zero/refspec-0.1.0.dev0-py3-none-any.whl`.
Other package wheels are unchanged. Installation is local; nothing was published.

**Decision:** adopt this bounded utility correction independently. A mintable
identifier describes a supported spelling; it does not prove issuance,
applicability, or complete extraction.
