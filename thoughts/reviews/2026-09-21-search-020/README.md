# Qualified optional readers: Search 0.2.0

Rulespec's `references` extra now installs `spicysearch==0.2.0` with
`refspec==0.1.0.dev11`. The retained Search identifier API still supplies the
same source-backed public-law, Statutes at Large, executive-order, docket and
RIN occurrences. No Engine installation or running service is required.

The RefSpec update is required: its former `0.1.0.dev0` wheel pins
`rulespec-artifacts==1.0.11`, which conflicts with Search 0.2.0's `1.0.12` pin.
The [resolver refusal](prior-pin-refusal.log) records that incompatibility.
RefSpec dev11 and DocSpec 0.7.0 also agree on PyArrow 25. All other declared
Rulespec dependencies remain unchanged; the extractor is outside the root uv
workspace, so this changes no workspace lock or Core dependency.

The consumer calls RefSpec's `read_edges` callback API and records that parser
name in scan provenance. Its per-reference
processing body is unchanged, preserving source XPath, exact quotations,
publisher targets and refusal behavior. The reader must complete before the
scan returns. Runtime capture also freezes the four SpicyDocs modules now
behind RefSpec's XML readers and records the SpicyDocs version. A changed parser
therefore refuses replay just like a changed RefSpec or Search helper.

## Installed qualification

The worktree starts at Rulespec `21693e0a4e3a71da539444a54399733f2cedbc76`.
The final Search wheel was built from `6fd7801` and has SHA-256
`7f7cd5f4b0601606ae9e714e6edf7424176ee6297fb82ece9ad54ac9cc91cea8`.
The [wheel inputs](wheel-inputs.json) record all eight local wheels, complete
dependency metadata, paths and SHA-256 values. They follow the repository's
existing explicit-wheel installation approach; no wheel is vendored here.

The extractor wheel was built from the changed package. The unchanged current
conformance source was built after generating its 40 Core JSON schemas with
`tools/constraints_compile.py`; an older conformance wheel carried stale
AI-lineage requirements. The existing projection 0.1.0 wheel was retained.
Install these exact wheels together and enable the extractor's `[references]`
extra. The [installation logs](final-install.log) and
[dependency check](dependency-check.log) record successful resolution.

A fresh Python 3.12 environment ran **228 passing tests** across 14 existing
reference, context, USLM/eCFR and runtime-reader test files. The
[command](test-command.json), [output](reference-suite.log) and
[JUnit results](reference-suite.xml) retain the checked population. Tests ran
from `/private/tmp` with `PYTHONPATH` unset; the
[installed-source check](installed-check.json) confirms `site-packages` imports
and exact consumer source bytes. Its recorded reader sources include the new
SpicyDocs parser dependencies. Deprecation warnings remain visible in the log.

The checks include exact source occurrence cases, repeated mentions, publisher
link disagreements, invalid coordinates, local navigation, absent optional
readers, and deliberate parser-source drift followed by successful restoration.
They use captured fixtures and injected model responses. They establish this
installed consumer path, not full-corpus recognition or semantic completeness.
Older saved runs still require their captured runtime; this update does not
relax replay drift checks. No package was published or service deployed.
