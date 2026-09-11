# Parenthetical public-law omission fixed upstream

SpicySearch now recognizes `Public Law (Pub. L.) 119-20`, including the full original source span. Its existing public-law pattern accepts the explicit parenthetical abbreviation; arbitrary parenthetical prose remains unsupported. No Rulespec-specific grammar was added.

The rebuilt wheel is installed in Rulespec's local `.tools/reference-tools-20260910` environment. Its outputs equal the direct source import on all three frozen comparisons. The production extractor has not been connected to the five-family additive reader, and no commit, release, deployment, or corpus rescan was performed.

## Verification and limits

| Frozen comparison | Result with rebuilt wheel |
| --- | --- |
| Real-source passages and historical Ohio control | All 16 labeled additions recovered; only the formerly missed occurrence changed |
| Additive-family development and diagnostic cases | All 15 labeled additions recovered; all 52 case outputs unchanged |
| Broader parser comparison | All four arms unchanged across the 32 cases |

The groups overlap; these are not independent populations. The real source is now a regression case, not fresh holdout evidence. The original real-source gate passes on its unchanged labels: all five families represented, no missed or unexpected additions, exact expected source spans, and unchanged baseline observations. The broader parser adoption gate still fails for its original reasons; unchanged output is not a claim those parsers are correct.

Before editing the parser, the new owner tests reproduced the real-source failure and five spelling/spacing variants while ten negative controls passed. The [red receipt](red.json) and [log](red.log) preserve the failures. After the fix, focused identifier, CFR/USC citation, and court-pass tests passed using `uv run pytest`; the [green receipt](green.json) records the command, inputs, stable HEAD, dirty worktree and load under the owner's measurement lock. Its 199 passes cover only those modules, not the full suite or a corpus accuracy rate. The dirty worktree was pre-existing and remains uncommitted; no clean-tree full-suite claim is made.

The [direct-source](source/summary.json) and [installed-wheel](wheel/summary.json) results agree. The old installed wheel was also rerun as a [contemporaneous control](control/summary.json) before replacement. It reproduced the saved failure. Actual imported module paths and hashes appear in each run record. [Package provenance](package.json) includes build/install commands and wheel hash; both changed parser and strict citation module bytes were checked against the wheel.

The newly recovered candidate is `Public Law 119-20` at passage offsets `[281, 308)`, quoting `Public Law (Pub. L.) 119-20`. Fixture content, source digest, passage digest, and source-relative coordinates were independently verified against the saved published text in [verification.json](verification.json). This evidence check goes beyond what the unit test itself asserts.

## Review and execution issues

The owner-required independent static review found no blocking issue in the syntax change, case sensitivity, boundary handling, overlap selection or source-coordinate handling. It made no claim about real-world legal existence or applicability. See [review](review.md).

Two instrumentation issues were retained rather than hidden:

1. The linter rejected a literal en dash in a Unicode test. The source now uses `\u2013`, producing the same test string. Original output is in `lint.log`; the corrected check is in `lint-fixed.log`.
2. The first comparison compared Python tuples with historical JSON lists, falsely marking some unchanged CFR outputs as differences. The serialized control outputs already equaled the historical files. The comparison now uses the saved JSON representation on both sides. Initial code and captures remain in `compare.initial.py`, `control-initial/`, and `source-initial/`. No parser behavior, expected label, or acceptance criterion was changed for this correction.

## Stopping point

The upstream syntax fix and local wheel verification are complete. The useful next production slice is a thin adapter for the already tested five-family candidates, preserving source coordinates and keeping target resolution separate. That connection remains separate from this completed parser fix. No further fixture tuning or model call is needed for this omission.
