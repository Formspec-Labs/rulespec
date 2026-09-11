# CFR source qualifiers stay unresolved

The source reader now retains `note` / `notes` (including preceding/following), `et seq.`, `and following`, and `ff.` markers and refuses to treat those references as a bare section target. This fixes both reported constructed application failures. It adds no schema or application regex and does not resolve note identities or enumerate open-ended ranges.

The change is 22 added lines in RefSpec `citation_grammar.py`. It reuses the existing USC tail lexemes and paragraph barrier in the CFR source-occurrence callback. `parse_cfr_citations` remains the older identity-only API; it deliberately cannot establish that a target body represents the entire written reference. `find_cfr_citations` retains exact source spans and refusals. `parse_authority_citation` propagates the refusal to its existing `cfr_refusal` field.

| Constructed source | Previous source reading | Current source reading |
|---|---|---|
| `49 CFR 390.5 note` | bare 390.5, no refusal | complete marker, `cfr_note_target_unresolved` |
| `49 CFR 390.5 et seq.` | bare 390.5, no refusal | complete marker, `cfr_open_ended_reference_unresolved` |
| `49 CFR 390.5 notes that the rule applies.` | bare 390.5 | unchanged; `notes` is a verb |
| `49 CFR 390.5. Note the change.` | bare 390.5 | unchanged; sentence boundary |
| `49 CFR 390.5 note` followed by blank line and `That provision ...` | bare 390.5 | note retained; next paragraph cannot turn it into a verb |

## Delivery follow-up: refusal names

The final upstream names are `note_target_unresolved` and `open_ended_reference_unresolved`, matching existing unprefixed CFR refusal values. Rulespec adds its own `cfr_` namespace; the initial names would have produced a duplicated prefix. This changes the names only, with no application workaround.

`refusal-name-followup.json` compares all 90 original captures against current output and permits only those two renames: zero other source or authority differences and zero identity-only differences. The focused gates again passed all 778 tests (`refusal-name-tests.log`). Original `results.json` and `source-freeze.json` remain unchanged. **The final code/test hashes are in `source-freeze-followup.json`.** The original observations below describe the first capture and retain its earlier names.

## Evidence

- `PLAN.md` predates the production edit. `baseline-source.json` pins that source. `tests/cfr_scope_tail_oracle.py` copies the old source callback and parser entry points; unchanged coordinate helpers and data classes remain shared.
- First focused run: **341 passed**. Additional manual boundary review found that the new ordinary-prose guard could look across a blank paragraph after a real note. The failing diagnostic is retained in `prose-boundary-failure.log`; the guard now honors the same paragraph barrier. This is an added development diagnostic, not an independent heldout success.
- Final focused and existing CFR/USC regression gate: **778 passed** (`regression-tests.log`). Includes pinpoints, ranges, mixed lists, qualified list continuations, prior ambiguity, subpart collapse, and the two list policies.
- `capture.py` replays **90 raw source cases**, including 21 saved publisher source/XML/readable-text controls. **53 declared source differences**, **0 unlisted differences**, **0 identity-only differences**. These are 52 combinations of 13 constructed qualifier markers with four anchor shapes, plus the additional paragraph diagnostic. Selected real controls are compatibility evidence, not evidence of naturally occurring note/open-ended frequency.
- The saved raw source contexts were manually inspected. The alcohol-definition XML's 49 CFR part 172, subpart F applies within its commercial-motor-vehicle definition; the Ohio paragraph's labeling/placarding subparts remain distinct. The raw output keeps those established qualifiers and their context intact.

## Consumer meaning and limits

A body lookup must honor `refusal` / `cfr_refusal` and existing qualifier ambiguity. An accepted identity-only parse is insufficient. No XML body lookup, existence verification, native address logic, package build, installation, or commit occurred in this task.

This is bounded support for existing written scope lexemes, not a general natural-language note grammar. The retained marker does not establish a specific numbered note or its governing meaning. A single line break can be publisher wrapping; a blank line terminates attachment. A qualifier after the final explicit list item remains attached to that item; relationships among list members are not inferred. Additional per-occurrence work consists of two anchored tail matches and local boundary checks; the underlying traversal is unchanged.

The source and two new test files are frozen in `source-freeze.json` for coordinated delivery. No further source edits are pending from this agent.
