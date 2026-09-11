# Publisher-link reuse: shared reader verified, application ingestion open

RefSpec's existing USLM link reader now lives in `refspec.registry.uslm`; its
build tool imports that shared implementation. Optional `include_source_path=True`
adds an exact XPath location for each emitted occurrence. The default output,
ordering, skips and refusals are preserved against the copied original reader.

The shared reader is installed and verified. The Rulespec consumer in this
directory remains experimental: its decoded XML text is a diagnostic coordinate
space, not normal readable document preparation. No extraction settings, model
fields or Core schemas changed. Normal `references` and discovery commands do not
yet consume these publisher links.

## Result against the registered comparison

The [design](design.md) fixed two source selections, default-behavior parity,
exact occurrence evidence, local target lookup and counterexamples before execution.

| Check | Result | What it establishes |
| --- | --- | --- |
| Publisher occurrences | 70: 7 operative, 5 source-credit, 58 note | Native links retain their source contexts |
| Targets inside the selected sources | 2 located; 68 outside the selections | Bounded lookup, not absence elsewhere in the law |
| Constructed controls | 10 passed | Repeats, Unicode, duplicate/absent targets, empty/nested text, contexts and native refusals |
| Independent XPath engine | 95 source/target fragments across 11 cases passed | Paths select the intended elements and decoded text |
| Focused upstream tests | 52 passed from source and installed wheel | Default reader parity and source-path behavior |
| Working extractor tests | 497 passed | Existing application regressions |
| Direct / isolated-wheel / working probe | Exact equality | Packaged reader matches the tested implementation |
| Existing application commands | 3 outputs equal the preceding checkpoint | No change to existing reference/discovery behavior |

Both locally located targets are **editorial-note links**. This population does
not demonstrate an operative provision inheriting the meaning of its target.
Unmarked references such as “paragraph (1)” remain outside native href coverage.
No model calls were made and no general extraction accuracy was measured.

Source selections come from the verified USLM release 119-102: title 5 section
423 and title 42 section 242c. [cases.json](cases.json) records archive/member
digests, original section byte locations, namespace wrapping and native rows.
XPath selectors address those captured XML selections, not the full original
title. XML positions and prepared-text codepoint offsets remain separate.

## Source fidelity and remaining work

The probe reuses `SourceFragment`, `oa:XPathSelector` and existing exact text
evidence. Repeated equal mentions have distinct locations; duplicate publisher
identifiers retain competing targets. Unknown target prefixes retain the native
error rather than becoming invented identifiers.

The decoded `itertext()` output can join a heading directly to prose, for example
“In generalThe…”. Correct coordinates do not make that suitable extraction input.
Next, preserve readable boundaries with a replayable source map, then connect the
publisher occurrences and available targets to the existing application commands.
Reuse shared evidence IDs instead of adopting the probe's repeated diagnostic
target text. Fresh source cases must include an operative link with a supplied
target before claiming that use works. Consumer comprehension remains a separate
comparison after navigation works.

## Preserved failures

- `owner-paths.log` retains the initial two failing tests. ElementTree's limited
  path lookup did not implement the full XPath positional semantics used by the
  producer. The test was corrected to walk child positions; independent lxml
  XPath verification then passed. Producer behavior was not changed for that test.
- `install.log` retains the first fresh-install failure: SpicySearch's existing
  dependencies required a local DocSpec wheel. The retry supplied that wheel and
  pinned dependencies. No DocSpec segmentation or validation service is used.
- `freeze.json` is unchanged. Its source/case/code pins match; only `freeze.log`
  differs because the log was hashed before buffered output finished. The final
  manifest pins the completed log separately.

## Reproducible local checkpoint

[verification.json](verification.json) verifies seven wheel inputs, eight
source/installed/wheel module identities, three probe versions and three existing
command outputs. The test counts above come from the completed saved logs; the
verification-record closeout did not rerun those suites. This is a local build,
not a published release or completed application ingestion feature.

The working environment uses the new RefSpec wheel and the unchanged named-act
extractor wheel. For a fresh Python 3.12 environment, the successful installation
used these pinned inputs from the Rulespec repository root:

```sh
uv pip install --python .tools/reference-integration-20260911-uslm/bin/python \
  --constraint thoughts/experiments/2026-09-11-uslm-source-links/dependency-constraints.txt \
  dist/production-20260910/rulespec_artifacts-1.0.11-py3-none-any.whl \
  dist/production-20260910/rulespec_conformance-0.2.0rc18-py3-none-any.whl \
  dist/production-20260910/rulespec_projection-0.1.0-py3-none-any.whl \
  dist/reference-tools-20260910-parenthetical/spicysearch-0.1.4-py3-none-any.whl \
  dist/reference-tools-20260911-uslm/refspec-0.1.0.dev0-py3-none-any.whl \
  dist/reference-integration-20260911-names/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl \
  ../DocSpec/dist/docspec-0.2.11-py3-none-any.whl
```

Exact wheel digests are in [wheel-inputs.json](wheel-inputs.json). Existing probe
and verification scripts retain the comparison; original failures and source
captures remain available beside the successful outputs. R14/R23 in the
[canonical task list](../../plans/2026-09-10-reference-integration-task-list.md)
track application preparation and integration.
