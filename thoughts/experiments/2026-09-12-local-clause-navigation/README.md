# Local clause navigation delivered

Rulespec now connects the two IEP attendance records to the separately captured
writing requirement, and the writing requirement back to both attendance records.
This implements the [bounded plan](../../plans/2026-09-12-local-clause-navigation.md)
using RefSpec recognition and existing Rulespec source lookup and context export.

## What changed

| Saved source case | Previous trace | Current result |
|---|---|---|
| Writing requirement references to clause (i)/(ii) | Unrecognized | Two exact occurrences; two unique native targets |
| Attendance R004/R005 context | No related claims | Each exposes writing requirement R006 |
| Writing R006 context | No related claims | Exposes target claims R004 and R005 |
| Team definition R003 and transition R007 | No qualification connection | No incoming or related claim added |
| IEP's two external publisher readings | Target not supplied | Identical readings and disposition |
| LEA's eight external publisher readings | Target not supplied | Identical readings and disposition |

The actual source says:

> A parent’s agreement under clause (i) and consent under clause (ii) shall be in writing.

Those words are ordinary text inside the native clause, not publisher hyperlinks.
RefSpec's `find_local_clause_occurrences` now retains their exact positions.
Rulespec uses the actual parent `/us/usc/t20/s1414/d/1/C` and its direct clause
children; the target addresses and source evidence already existed. Incoming
claim selection requires the focus to fit within the located target. Outgoing
claim selection requires each current claim to fit within that target. All
containing referring claims remain visible when several overlap.

`reference_readings` reports candidate claim IDs, direction and
`semantic_role=not_assessed`. `related_claims.reference_ids` records why a claim
is present. No statement, kind, modality, `target_ids`, identity, source text or
review history changed. The two attendance statements still need semantic
qualification work before they are independently complete; this delivery makes
the existing qualification easier to find. It does not establish better model
accuracy or automatically send the context export to extraction or audit.

## Checks and delivery

- **713 extractor/schema tests passed**, including the actual saved IEP book and
  controls for repeated labels, missing/duplicate targets, native number/address
  conflicts, notes, quoted content, unsupported syntax, current-claim overlap,
  publisher links, context budgets and unchanged reviews.
- **180 targeted RefSpec grammar tests passed** (`-m 'not slow'`); Ruff passed on
  the changed owner source and tests. RefSpec commit: `c9cc5410`.
- The [verification](verification.json) repeats two source scans and eight context
  exports. Original decoded books and every file in the earlier trace's manifest
  remain unchanged. Source imports and installed wheel imports give identical
  results. The installed `context-export` CLI matches the source result outside
  the checkout with `PYTHONPATH` unset. All 92 installed dependencies are compatible.
- [Delivery receipt](delivery.json) records both local wheel hashes and import
  locations. Wheels are in `dist/reference-integration-20260912-local-clause/`.
  These are local builds of the existing development versions, not published
  releases. **Zero model calls and zero additional output-token cost.**

Recheck with the installed environment:

```sh
env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 \
  /Users/mikewolfd/Work/rulespec/.tools/document-poc-venv/bin/python \
  /Users/mikewolfd/Work/rulespec/thoughts/experiments/2026-09-12-local-clause-navigation/verify.py
```

## Limits and next decision

This is a bounded navigation improvement on an existing failure, with constructed
counterexamples. Lists, ranges, nested pinpoints and explicit other-container
qualifications remain refused; general local-address grammar is unfinished. IEP's
plural `clauses (ii)` reading is now an explicit refusal, not a located target.
Plain text cannot establish native local scope. A reference in a note or quoted
XML element does not trigger operative local lookup. No cross-document clause
guessing or automatic governing relationship was added.

Native lookup indexes nodes once: O(N log N + R(log N + depth + matches)), plus
the evidence it emits. Current-claim association scans the accepted claims for
each reference relevant to the single focus: O(C × relevant R). That part is
superlinear when both sets grow; it has no new interval-index dependency and has
not been benchmarked on full-title claim inventories. Source expansion remains
one hop and uses the existing character allowance.

The next semantic question remains separate: represent and verify which part of
a captured writing requirement qualifies which attendance rule without changing
its `requirement` kind or bypassing the current relationship guard. Keep the
purpose-versus-applicability cleanup and broader fresh-source assessment open.
