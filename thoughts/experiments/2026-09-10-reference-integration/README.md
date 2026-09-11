# Reference candidates connected to the document workflow

Implemented the previously verified five-family SpicySearch reader as an optional
Rulespec application step. The production package now exposes:

```sh
rulespec-understand references prepared.json --output references.json
rulespec-understand discovery-export my-run --references --output discovery.json
```

The standalone command also accepts source text, a rulebook, or an extraction
directory. The discovery option scans the current review snapshot's pinned
source, including passages without extracted statements. No model calls occur.

## Reuse and boundaries

- Existing SpicySearch recognition supplies public-law, Statutes at Large,
  executive-order, docket, and RIN candidates. The adapter adds no grammar.
- `validate_document`, `_evidence`, `verify_fragment`, and `source_passages`
  supply existing source identity, exact evidence, Rulespec fragment identities,
  and passage links. Offset units remain Unicode codepoints, half-open.
- `export_discovery` reuses its evidence table. Statements, default exports,
  accepted links, review history, and prompts are unchanged.
- No new Core schema is needed: these are application candidates locating
  mentions, not asserted target artifacts or relationships. Existing
  `SourceFragment` evidence conventions are reused; the adapter never claims
  target resolution, applicability, or semantic completeness.
- SpicySearch is declared only in the extractor's optional `references` extra.
  Core validation and default extraction/discovery do not depend on it. An
  explicitly requested scan without the package raises a useful error.

The adapter scans source text once and links candidate spans to the sorted
passage index by binary search. Repeated references at different offsets retain
different identities. References involving inserted source-map text are recorded
as rejected. Invalid source identity or out-of-range parser coordinates fail
instead of producing plausible evidence.

## Verification

The full extractor test directory passed: **459 tests**, with dependency
deprecation warnings. The exact output is in [tests.log](tests.log). Command:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src \
  .tools/document-poc-venv/bin/python -m pytest -q --disable-warnings \
  packages/rulespec-extrapolator/tests
```

The new tests preserve the frozen real-source labels, including the parenthetical
public-law failure and Ohio negative control. Other checks cover repeated
references, Unicode offsets, cross-paragraph evidence, inserted text, changed
source hashes, bad parser offsets, absent optional dependency, all CLI input
forms, refusal to overwrite output, and unchanged actual accepted statements.

An initial integration-test fixture omitted the schema-required `actor` field
and was rejected before export. The fixture was corrected to include the
source-supported actor; no application behavior was loosened for it. The earlier
full run had that one failure and 458 passes; the final run above passes entirely.

Built `dist/reference-integration-20260910/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl`
and installed it with the verified parenthetical SpicySearch wheel and existing
Rulespec wheels into `.tools/reference-integration-20260910`. Both new commands
ran from `/tmp`, with imports resolving to installed `site-packages`. Dependency
validation with `uv pip check` passed. [wheel-smoke.json](wheel-smoke.json)
records commands, module paths, package digest, and the recovered candidate.

The smoke test uses the saved real-source paragraph in a manually constructed
rulebook, not a new model extraction. Its [standalone scan](references.json) and
[discovery export](discovery-references.json) agree on the candidate. Statements,
records, and accounting match the [default export](discovery-default.json).
The fixture run is retained to make this comparison inspectable.

The current `.tools/document-poc-venv` was also updated to the built extractor
wheel and verified SpicySearch wheel. No existing extraction captures were
reprocessed or rewritten. No commit, publication, deployment, or UI change was
performed.

## Practical limits

This integrates the tested reader; it is not a new generalization experiment.
Recognizing selected citations does not establish completeness on new documents.
The five-family restriction still excludes CFR/USC, local paragraph references,
and Federal Register document identifiers. Existing claim-level references remain
as before. Adding more families or resolving legal targets is separate work.

For current local installation, use the explicitly verified SpicySearch wheel:
older builds share version `0.1.4`. Its source digest is recorded in each scan;
its wheel digest remains pinned in the preceding parenthetical-fix record.
