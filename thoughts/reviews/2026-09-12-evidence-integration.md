# Integrated evidence fix and retained qualification regressions

The shared audit evidence helper now calls Core's existing `evidence_parts`.
Inventory, comparison, refinement proposal grounding and refinement challenges
accept exact source selections crossing formatting-only whitespace. They continue
to reject inserted substantive text and selections supported only by formatting.
Whole quotation coordinates and saved source maps remain unchanged. No schema,
prompt, model configuration, extra model pass or public output shape changed.

The [qualification regression index](../../packages/rulespec-extrapolator/evaluation/qualification-regressions.md)
connects the saved equipment, simulator and PPE failures to their source, original
claims, review criteria and counterexamples. The real three-alias coverage failure
is a deterministic evaluator regression: it must remain `needs_review` with three
unknown units. The semantic omissions remain open evaluation cases, not passing
accuracy tests.

Both experiment directories retain their original raw inputs/outputs, runtime
copies, review labels, failures and manifests. Their findings describe the state
at the time of each experiment; this note records the subsequent production-code
integration. The expanded-inventory and additional relationship passes were not
adopted. The existing evaluator already detects inconsistent coverage links.

Validation:

- New tests reproduced four failures before the production fix: formatting-space
  audit, formatting-newline audit, compound refinement, and native PPE evidence.
  Four refusal controls passed before and after the change.
- Focused audit/refinement/evaluation checks: 117 passed.
- Full extractor suite plus schema tests: **689 passed**. Reported warnings came
  from dependencies; no test failed.
- Recorded audit and refinement tests confirm source/history preservation and
  identical replay without provider calls.
- Both saved experiment decoders replay identically: six inventory/comparison
  pairs and nine relationship/comparison captures. No fresh model requests.
- Built and installed the extractor wheel into the local document environment.
  Imports from `site-packages`, invoked outside the checkout with `PYTHONPATH`
  unset, match current source. The two saved affected native PPE spans succeed;
  inserted substantive wording is refused. All 92 installed packages pass
  `uv pip check`. This checks the package with existing dependencies, not a new
  independent dependency resolution or a remote deployment.

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python -m pytest \
  packages/rulespec-extrapolator/tests tools/test_extraction_schemas.py --disable-warnings -q
```

Audit schemas remain at their existing version because the output structure did
not change. Runtime hashes continue to distinguish processing versions; historical
strict CLI replay requires its captured runtime. Original saved artifacts are not
rewritten to claim that their prior refusals were successes.
