# Native USC checkpoint: tested upstream, application integration pending

RefSpec now exposes `find_usc_citations` from the existing authority matcher.
The upstream change is committed locally as `c5c0a27d`.
The 29 frozen source expectations pass: subsection and range-end labels, chapter
and subchapter, appendix and note, repeated mentions, original character positions,
and inherited list context remain inspectable. Invalid titles and damaged tokens
retain source text and an explicit refusal. This is a bounded development result,
not an accuracy rate or a complete legal-reference grammar.

The existing `parse_authority_citation` keeps its separate authority-field policy.
A copied test-only version agrees on all 31 inputs and seven variants per input
(217 comparisons; some variants coincide). The two additional inputs are the
pinned authority notes for 12 CFR 615 and 14 CFR 121, read with their original
part headings and complete AUTH elements. Their source hashes match the saved
publisher files. The raw context explains why a field reader can legitimately
resume an earlier USC list after a Statutes at Large citation, while prose
occurrences need an adjacency boundary.

## What the additional checks found

The first control run had four failures and 70 passes. A bare appendix absorbed
the next prose word; an incomplete subchapter marker and two subchapter label
forms lost their qualification. The next run passed all 74 controls. Those logs
remain in `native-controls-first.txt` and `native-controls-second.txt`.

The first broader run passed 463 tests, with 14 slow tests deselected. Manual
review of the two added authority-note outputs then found false token-boundary
refusals on comma-separated numbers. The original output remains in
`native-checkpoint.json`. A comma is now a separator, while an actual attached
Unicode word still produces a refusal. Added tests cover both the short example
and the two publisher notes.

The FAA note also writes `42301 preceding note`. The final occurrence retains
that entire qualification and refuses `usc_note_position_unresolved`; a plain
section or generic note would lose meaning. A constructed `following note`
counterpart exercises the same boundary. No positional note identity is guessed.

The final owner run passed **468 tests**, with **14 slow tests deselected** and
no skips. It covers the USC additions, existing citation grammar, CFR and act
occurrences, authority notes, act lookup and policies. `native-owner-tests-second.txt`
is the complete log. The new tests pass lint. The changed grammar retains two
pre-existing `SIM102` lint findings in unrelated code; no new lint finding remains.
`native-lint-comparison.json` preserves the baseline comparison;
`native-lint-final.json` records the final committed files.

`native-verified.json` contains all 31 final raw results; `native-verified-receipt.json`
pins the source and test files. An immediate second read reproduced them exactly.
The original R5 parser outputs and first prototype output remain unchanged.
No model calls were made.

## Remaining boundary

Rulespec does not yet call this API. No wheel was rebuilt or installed, and the
running UI and existing extraction runs still use the prior installed packages.
R6 remains open until the existing reference adapter preserves every qualified
field and refusal, then passes its direct-import and installed-wheel checks.
The positioned-note refusal must survive that connection. Do not mint an
unqualified section identity for it.

The prose reader deliberately stops at intervening prose or another citation
family. In the FAA authority note it does not resume the original title after
the Public Law/Statutes at Large clause; the whole-field API still does. This is
an exposed recall boundary, not proof that all references in that note were found.
General qualifier coverage, larger untouched evaluation and legal target
existence remain separate work.

The implementation adds source recording to the existing matcher and uses its
native authority data. It adds no model/CUE schema or competing USC parser.
Dash normalization is bounded to full-input passes, rather than repeated for
each occurrence. The shared reader retains its existing list-membership and
span-overlap scans, which can be quadratic in the number of matches; this slice
makes no large-corpus performance claim.
