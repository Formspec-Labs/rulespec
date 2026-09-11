# CFR subpart qualifiers preserved through the installed reader

Adopt the bounded extension. RefSpec now retains explicit subparts, their written
list members and stated range endpoints, plus appendices named under subparts.
Rulespec carries those native readings through the existing reference scanner
and discovery evidence table. No model fields, model pass, runtime dependency,
Core schema or second citation grammar was added.

## Source findings and result

The original Ohio paragraph describes alternative ways to mark hazardous-waste
containers. Its `49 CFR Part 172 subpart E (labeling) or subpart F (placarding)`
reference previously stopped at the part number. It now produces:

- `49 CFR 172 subpart E`, supported by `49 CFR Part 172 subpart E (labeling)`.
- `49 CFR 172 subpart F`, supported by ` or subpart F (placarding)` and the first
  occurrence's exact title/part context. The written `or` remains source text;
  the parser does not create an applicability or exemption assertion.

Six new paragraphs were selected in publisher order from pinned eCFR titles 21,
40 and 49, without consulting parser success. Manifest hashes match the original
XML files; full source sections and individual per-title dates are saved. Raw
context showed appendix targets, a parenthetical testimony qualification, plural
subparts, and an ambiguous list of parts followed by a list of subparts.

| Case | Result |
| --- | --- |
| Ohio hazard-marking paragraph | E/F alternatives and descriptors retained |
| 21 CFR 2.125(a) | Appendix A and appendix B to 40 CFR part 82 subpart A remain distinct appendix targets |
| 21 CFR 16.22(a)(5) | 21 CFR part 10 subpart C retained |
| 40 CFR 2.301(j) | Part 59 subpart F retained; other references unchanged |
| 40 CFR 2.401(b)(3) | Part 3 subpart E and its complete parenthetical qualification retained |
| 49 CFR 11.104(b) | 45 CFR part 46 subparts B, C and D retained with their written list context |
| 49 CFR 11.104(d)(4)(iii) | Subparts A/E retained, but their pairing with parts 160/164 remains refused as `cfr_ambiguous_part_scope` |

Across these seven inputs, **10 unambiguous qualified targets** now retain their
qualifiers; **two uncertain part/subpart pairings** retain their evidence and a
refusal. This is a bounded representation improvement. These newly selected
paragraphs informed the extension and are now development/regression data, not
an untouched benchmark or a general extraction-accuracy estimate.

The original nine-case integration fixture still preserves **18 unrelated
occurrences**, including evidence and IDs. Its one Ohio part-level occurrence
becomes two qualified occurrences; those expanded source spans intentionally
produce new IDs. All 16 SpicySearch occurrences remain unchanged. Every native
identity-only CFR reading on the seven inputs remains unchanged too.

## Mapping and checks

| Native meaning | Application field | Existing representation/check | Remaining uncertainty |
| --- | --- | --- | --- |
| Subpart / stated range endpoints | `reading.subpart`, optional `subpart_end` | Native occurrence plus verified `SourceFragment` | Existence and intermediate range members are not inferred |
| Appendix under a subpart | `reading.appendix` and `subpart` | Same source evidence and display value | Target text and edition not fetched |
| Shared title/part and list connectors | Literal occurrence plus `reference_context` evidence | Existing source map, passage IDs and shared discovery evidence | Written adjacency is not governing-condition logic |
| Multiple possible part/subpart pairings | `reading.qualifier_status` and rejection code | Existing rejected-reading export and source evidence | A resolver or review must establish the pairing |

Empty new fields are omitted from application output. Unknown targets and source
insertions cannot acquire supported addresses. Sentence/paragraph boundaries,
intervening prose, damaged word suffixes, wrong-title inheritance, plural-label
rules, repeated Unicode occurrences and stated ranges have explicit controls.
The old occurrence implementation remains a copied test-only oracle upstream;
tests enumerate the deliberate changes rather than ignoring other differences.

## Verification and delivery

- **481 extractor tests passed** in both the source integration check and the
  final working-environment check (37.29 seconds for the latter). See
  `application-tests.log` and `current-application-tests.log`.
- **338 RefSpec parser/resolver tests passed** after the plural-continuation fix.
- **40 selected Unified Agenda caller tests passed**, 110 deselected.
- Complete native/application scans match between direct imports and rebuilt
  wheels on all seven selected inputs; the old nine-case scans also match.
- Six installed CLI calls from `/tmp` passed: both commands on Ohio and the
  ambiguous source, plus unchanged default discovery controls. Fixtures use real
  source text with manually compiled empty rulebooks, not model output.
- Isolated and working-environment dependency checks pass. The working
  `.tools/document-poc-venv` has the new wheels; exact module parity is captured
  in `current-final.json` and checked against `wheel-final.json`.

`verification.json` pins the six dependency wheels. The two new builds are in
`dist/reference-tools-20260911-subparts/` and
`dist/reference-integration-20260911-subparts/`. The package README contains the
working-environment install command. Older builds and captures remain unchanged.
No provider calls, source downloads, corpus rebuild, commits or publication occurred.

`design.md` preserves the initial decision and pre-implementation field choices.
`owner-red.log` records the original failures; `plural-red.log` records a later
mutation where an explicitly plural continuation initially lost its last member.
The one-line fix carries that explicit plural permission forward. `probe.py
--output NEW_FILE` repeats fixed native/application scans; `check_installed.py
--output-dir NEW_DIRECTORY` repeats the packaged commands without overwriting
existing captures. The earlier CFR `check.py --output NEW_FILE` supplies the
unchanged nine-case regression comparison.

This does not complete qualified USC, omitted-title/local paragraph lookup,
general reversed/appended qualifiers, arbitrary nested parentheticals, target-body
lookup, edition matching or reference-assisted model comprehension. Keep those
tasks open in the canonical task list; do not expand this parser into a semantic
or legal-validity oracle.
