# Evidence context is available in the local application

The existing source/reference/feedback work is now usable from one current
statement or source selection through `rulespec-understand context-export`.
The [package instructions](../../../../packages/rulespec-extrapolator/README.md)
describe the command and Python functions. The [experiment result](../RESULTS.md)
records why automatic interpretation and meaning corrections remain deferred.

Inputs: current retained statement or source positions, original prepared text,
optional publisher sources, and saved review feedback. The application gathers
existing context, short enclosing sections, linked claims, and one-hop uniquely
located target bodies. It emits selected evidence with separate source catalogs,
original source data, current reference scan, complete relevant observations and
input/code fingerprints. Existing resolvers retrieve exact evidence from the
supplying source. Omitted, unavailable and ambiguous context stays explicit.
No model call or review mutation occurs.

`examples/` contains exports for all six frozen cases. The command-generated
`installed-cli-context.json` reproduces the external good-cause example from its
original source file. `command-help.txt` is the installed command's help.

Validation: 674 application tests pass from source and from the installed wheel
in an isolated directory. The 12 added tests cover duplicate/external evidence,
missing/ambiguous targets and allowances, source substitution, inserted whitespace,
unseen conditions, invalid selections, feedback/approval preservation and the
normal command. All six exported materials match the frozen experiment apart from
an added focus role and source metadata stored once. Source, isolated wheel and
the updated local environment produce identical export fingerprints. All 136
previously recorded runtime inputs remain byte-identical; no sibling dependency
was upgraded. Twelve model captures replay identically without provider calls.

The installed-check setup initially omitted the evaluation helper and placed
fixtures at the wrong relative depth. Those failures are retained in
`../installed-preflight-failure.log` and `../installed-layout-failure.log`.
After copying the required test assets with their expected layout, all 674 tests
passed. No production code was changed to bypass those failures. Dependency
deprecation warnings remain in the logs.

Only the application wheel was installed into `.tools/document-poc-venv`, using
`--no-deps`. `wheel-inputs.json` preserves the new application wheel and unchanged
dependency inputs. `receipt.json` records delivery boundaries. Work is local and
uncommitted; nothing was pushed or deployed. Original statements, approvals,
review events, captures and prior failed experiments are unchanged.

This completes the current integration plan's bounded comparison and evidence
delivery. The failed model gate stays failed. The original automatic extraction
and reviewed-workflow objectives remain broader work: the next focused hypothesis
must address unsupported actor/scope additions and context cost. No further model
calls or automatic meaning changes are needed to close this comparison.
