# Source imports and installed-wheel verification

The extraction/refinement tools passed direct-import checks and installed-wheel
checks. The normal `.tools/document-poc-venv` environment now uses rebuilt wheels
for Rulespec extrapolation, conformance and projection. No package was published.

## Checks and findings

- Direct imports: 445 package/schema-generator tests passed. A live refinement
  of the saved 49 CFR 392.10 railroad document completed seven model requests,
  applied five exemption links, reloaded successfully and replayed with zero
  provider calls. Four external-reference observations remained unresolved.
- Environment repair: dependency checking found `owlrl==7.6.2` paired with
  incompatible `rdflib==7.5.0`, plus missing `rulespec-artifacts`. The resolver
  selected `owlrl==7.1.4` to retain the recorded RDFLib version; installed
  `rulespec-artifacts==1.0.11`. Both development and isolated wheel environments
  passed `uv pip check`. Source tests passed again after repair.
- Installed package: 439 tests passed outside the checkout with `PYTHONPATH`
  unset. Imports and Core validation data resolved inside `site-packages`.
  Wheel replay reproduced the direct-import refinement; discovery output matched
  exactly. The wheel CLI's fresh live extraction produced nine accepted records,
  zero rejected records and three unresolved links, then replayed successfully.
- Presentation/package data: four JavaScript evidence tests passed. The wheel's
  HTTP server served HTML, JavaScript and CSS identical to the tested source;
  its snapshot loaded successfully. All five packaged schemas loaded and CLI
  replay/export worked with Go and CUE absent from `PATH`.

These are integration and packaging checks on one saved source, not a new semantic
accuracy comparison. All live refinement proposals were supported, so withheld
judgments were exercised by the controlled tests rather than this live run.
No extraction prompts or schemas changed. The README now documents dependency
checking and the source-to-wheel workflow. It was included in the final wheel rebuild.

## Retained outputs

- [Verification and final wheel hashes](../../.tools/production-wheel-20260910/verification.json)
- [Direct-import live result](../../.tools/production-wheel-20260910/source-result.json)
- [Installed replay and export parity](../../.tools/production-wheel-20260910/wheel-result.json)
- [Installed HTTP/assets check](../../.tools/production-wheel-20260910/wheel-http-check.json)
- [Live extraction](../../.tools/production-wheel-20260910/wheel-extraction/run.json)
- [Wheel](../../dist/production-20260910/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl)

Raw requests, responses, frozen runtimes and replays remain under
`.tools/production-wheel-20260910/`. Wheels remain under
`dist/production-20260910/`. Both directories are local build/test artifacts.
`installed-versions.json` records the isolated environment's exact versions;
`original-dependencies.txt` retains the incompatible starting versions.

For subsequent source edits, explicitly set
`PYTHONPATH=packages/rulespec-extrapolator/src` while testing; normal CLI calls now
use the installed wheel and require a rebuild/reinstall to pick up code changes.
