# Maintained extraction evaluation cases

These selected development cases preserve useful successes and known failures.
Desired outcomes are revisable source-review labels, not absolute legal judgments.
Observed outcomes describe saved calls; a missed defect is never the desired
result of a regression test. None of these counts estimates general accuracy.

## How to use the cases

Reuse each experiment's fixtures, labels, raw responses and runner. The comparison
views contain `document` and `accepted`, not complete validated Core graphs: use
`audit._judgments`, `audit._assessment` and `evaluation.evaluate` through the saved
comparison runners. Do not pass these views to the full `audit` CLI. Extraction
controls use their prepared documents and saved complete rulebooks.

Claims below use the model-facing `Cnnnn` alias (zero-based accepted-record index).
For a fresh evaluation, retain a new capture and assess the desired fields before
comparing with the historical observation. Never overwrite the original captures,
labels or manifests. Live model quality checks stay separate from deterministic
CI and offline replay. Replay reproduces processing; it does not prove semantics.

## Comparison cases

| Input and target | Desired behavior | Historical observation |
|---|---|---|
| [Passport A/B](audit-mutation-sensitivity/fixtures/passport.json), C0004 | A: retain agencies/centers and their approval exception. B: identify the transplanted posts actor in `summary` and `scope_text`. | Original correct; planted actor/scope error detected. |
| Same passport pair, C0013 | A: retain IN response exemption. B: flag the reversed `kind`, `modality` and `summary` as a duty. | Original correct; reversal detected. |
| [Waste A/B](audit-mutation-sensitivity/fixtures/waste.json), C0008 | A: require both label components. B: reject either component alone in `summary` and `choice_text`; do not infer exclusive OR. | Original correct; AND-to-OR detected. One rationale overstates exclusivity. |
| Same waste pair, C0009 | Preserve three consecutive calendar days, trigger and destinations. Flag thirty in B's `summary` and `choice_text`. | Original correct; wrong threshold detected. |
| Passport C0012, both arms | Retain the separate IN-change prohibition; do not transfer the IRL actor mutation to it. | Correct in both. |
| Waste C0007, both arms | Retain closed-container duty and its exceptions; do not transfer label/deadline mutations. | Correct in both. |
| Passport C0005, both arms | Assess the standalone cleared-language duty against its local-adaptation qualification; distinguish complete context from complete short wording. | Both accepted without identifying the known standalone qualification issue. Consumption-dependent label, still open. |
| [Notice A](audit-field-distinction/views/A.json), C0014 | Flag incomplete standalone `summary` and empty `scope_text`; `logic_text` retains emergency/unusual circumstances but omits the governing unforeseeability qualification. | Summary/scope accepted in 2/2; both reports passed. Known miss. |
| [Notice B](audit-field-distinction/views/B.json), C0014 | Flag the same short statement/empty scope while explicitly recognizing complete governing `logic_text`; do not count a quotation alone as represented meaning. | Scope error 2/2, summary error 1/2, explicit logic distinction 0/2. Strong criterion unmet. |
| [Notice C](audit-field-distinction/views/C.json), C0014 | Accept complete summary and logic. Empty structured scope alone is not loss when prose retains qualifications. | Correct in 2/2. |

Passport and waste A are original controls; B contains constructed mutations.
Their [exact field edits](audit-mutation-sensitivity/mutations.json),
[views](audit-mutation-sensitivity/views), [raw captures](audit-mutation-sensitivity/runs),
[parsed judgments/reports](audit-mutation-sensitivity/results.json),
[review](audit-mutation-sensitivity/blind-review.md) and
[manifest](audit-mutation-sensitivity/manifest.json) preserve provenance.

Notice uses the [original fixture and source inventory](audit-field-distinction/original-fixture.json),
[raw A1/A2/B1/B2/C1/C2 captures](audit-field-distinction/runs),
[parsed judgments/reports](audit-field-distinction/results.json),
[review](audit-field-distinction/blind-review.md) and
[manifest](audit-field-distinction/manifest.json). B/C are constructed views;
other claims and the original Core graph are retained in the source fixture.

## Independent extraction boundaries

| Prepared input | Desired behavior | Historical observation |
|---|---|---|
| [Same actor](passage-boundary-experiment/fixtures/same_actor.json) | Keep signing each report mandatory and a blue pen optional. No permission to skip signing or duty to use blue ink. | Both catalog arms preserved two independent meanings. |
| [Different actors](passage-boundary-experiment/fixtures/different_actor.json) | Visitors file notice on arrival; staff may work remotely. Do not transfer actor or arrival condition. | Both arms preserved two independent meanings. |
| [Seasonal and independent controls](standalone-qualification-experiment/fixtures/controls.json) | Preserve six meanings: the preceding two pairs plus a winter ski-pass duty and summer bicycle permission, each with its own scope. | Both description arms preserved all six. |

The boundary experiment's [runs](passage-boundary-experiment/runs),
[review](passage-boundary-experiment/blind-review.md) and
[manifest](passage-boundary-experiment/manifest.json) preserve controls and the
notice intervention. The standalone experiment's
[runs](standalone-qualification-experiment/runs),
[review](standalone-qualification-experiment/blind-review.md) and
[manifest](standalone-qualification-experiment/manifest.json) preserve both
schema descriptions. Neither treatment improved the target notice statement;
these positive controls do not justify adopting either treatment.

## Fresh-source explanation comparison

The [fresh-source comparison](fresh-explanation-check/README.md) tested complete
official eCFR sections for oxygen (14 CFR 91.211), employee alarms (29 CFR 1910.165)
and procurement (2 CFR 200.320). The [30 checks](fresh-explanation-check/REVIEW.md)
were frozen before the twelve calls; each source had current, omission-only,
logic-explanation and modality-explanation arms.

Neither explanation field met its accuracy gate. Preserve these sections as frozen
evaluation evidence rather than tuning fixtures. The
[source files](fresh-explanation-check/sources),
[statement judgments](fresh-explanation-check/statement-review.json),
[raw captures](fresh-explanation-check/runs) and
[manifest](fresh-explanation-check/manifest.json) retain the evidence needed to
revisit those judgments. Passing schema validation does not establish that a
statement preserves every condition or that extraction found every rule.

## Pinned sources

Hashes below cover the exact UTF-8 document text, as in `document.sha256`.
Fixture and capture file hashes are separately pinned by each linked manifest.

| Fixture | Source SHA-256 |
|---|---|
| [audit-mutation-sensitivity/fixtures/passport.json](audit-mutation-sensitivity/fixtures/passport.json) | `a150f4ee3b06251ce1b4533a18231db38769787697dbaee26861e227c43e353a` |
| [audit-mutation-sensitivity/fixtures/waste.json](audit-mutation-sensitivity/fixtures/waste.json) | `43f75aaf4a19870db19d481dd6883f99ef4c606c7cb4914012a118a12fbce149` |
| [audit-field-distinction/original-fixture.json](audit-field-distinction/original-fixture.json) | `e3aff6ecabd02a98ec9a62e7959969df8a597ad2170db6d29c66e363b375e6cc` |
| [passage-boundary-experiment/fixtures/same_actor.json](passage-boundary-experiment/fixtures/same_actor.json) | `1bc2c356e53256206faee403b809f7438d9556592c3a07516e61cc86ff8163b4` |
| [passage-boundary-experiment/fixtures/different_actor.json](passage-boundary-experiment/fixtures/different_actor.json) | `271e846aaec818f208357dfe8c260765e5810bd7352ba41c653e507a251b6779` |
| [standalone-qualification-experiment/fixtures/controls.json](standalone-qualification-experiment/fixtures/controls.json) | `9639c22d96d2c938434fca2ebdfb7f5d26eb140456f8911fd19d3875332b5aff` |

Historical experiments pin their pre-default-change runtime. All 26 calls replayed
successfully before the runtime change. Use commit `beb3fbf` and its recorded dependencies for those runners; current-runtime drift refusal is intentional.
For the comparison field test use `replay.py`; its original `run.py replay`
incorrectly selects an extraction-only manifest verifier. Preserve that recorded
failure and its corrective wrapper. No manifest or raw output was rewritten.
