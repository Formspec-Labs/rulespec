# Citation ownership and removal of unused copies

Decision: Can Rulespec remove the unused citation helpers inherited by
`rulespec-projection`, while retaining its existing graph output and using
RefSpec for document reference reading? Is RefSpec already a complete
replacement for its remaining CFR reader?

Hypothesis: Several copied helpers have no production caller in the inspected
repositories and are outside the package's exported API. Removing those helpers
will leave every surviving function and graph result unchanged. RefSpec should
preserve lettered CFR parts better, but its documented compound-part gap may
prevent an unconditional reader replacement.

Arms: Frozen Rulespec commit `762900d` versus deletion of unreachable helpers;
RefSpec `53c0f387` and SpicySearch `10824d4` are comparison readers, imported
directly without modifying them. SpicySearch's permissive query behavior is not
the proposed source-reading policy; compare its explicit strict reader.

Cases: All distinct title/part keys in RefSpec's saved OFR subject-index CSV,
rendered as constructed citation strings, plus selected counterexamples for
letter suffixes, compound parts, ranges, another namespace, list inheritance,
compilation locators, damaged tokens and impossible titles. The CSV is a
publisher-derived index, not an independently labeled prose benchmark. Existing
projection fixtures are frozen outputs of the original producer and test the
actual graph-building calls.

Held constant: No model calls. Same interpreter and inputs; one deterministic
pass per arm. Record module paths, commits, hashes, raw reader outputs and
criteria. Stop after the comparison, existing package/application correctness
tests and one installed-wheel check; do not add grammar exceptions in this
experiment.

Decision rule: Remove a helper only after caller tracing and reachability agree
it is unused, an existing upstream API owns the useful feature, all surviving
definitions are unchanged, and existing graph/package tests pass. Preserve
compilation guards used by the remaining CFR reader. Do not claim unknown
external callers have been audited. Adopt a wholesale reader replacement only
if the candidate preserves the required complete identifiers, refusal detail,
dictionary/compact input behavior and graph semantics. Otherwise retain the
live reader and document the concrete follow-up; do not create a new package
or dependency to make the comparison pass.

The preceding goal turn only reported already committed state. It made no
goal progress. This experiment resumes the open R8 work.
