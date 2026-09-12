# Current SpicyDocs provider probe

Use `spicydocs_provider_probe.py` for current SpicyDocs candidates. The former
`spicydocs_probe.py` and its recorded output remain historical evidence. Their
`catalog.profiles` lookup described a table declaration; it did not establish a
CFR source-release adapter or captured section bodies. SpicyDocs has retired
that auxiliary registry and its generated catalogs without a compatibility shim.

The current probe lists the installed public native profiles, checks every
packaged SpicyDocs member against the supplied wheel, records package/module
digests, and checks the Federal Register-only locator's refusal of an eCFR URL.
It records a separate citation to SpicyRegs' metadata-only `cfr_sections` table.
It does not test remote availability or acquire source text.

Install the candidate wheel and its declared dependencies into an isolated
environment. Run from outside a source checkout, supplying the exact tested
provider revision and the separately inspected SpicyRegs revision:

```sh
uv run --no-project --python /path/to/environment/bin/python python -I \
  /path/to/spicydocs_provider_probe.py \
  --wheel /path/to/spicy_docs-0.1.0-py3-none-any.whl \
  --provider-revision PROVIDER_COMMIT --spicy-regs-revision SPICY_REGS_COMMIT \
  --output /path/to/new-provider-probe.json
```

The output path must be new. Keep the result with the candidate's qualification
records. An exact wheel check establishes which implementation this probe used;
it does not qualify DocSpec intake or the broader Rulespec artifact integration.
