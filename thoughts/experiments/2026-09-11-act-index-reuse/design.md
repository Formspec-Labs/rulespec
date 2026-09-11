# Exercise the existing act indexes before choosing an adapter

Decision: Can RefSpec's existing named-act recognition and resolution provide
useful, source-supported results for the Rulespec application without a second
name registry or a locally rewritten parser?

Hypothesis: The sealed local act and source-credit indexes load through RefSpec's
current integrity checks and its recognizer/resolver can supply named-act targets
or explicit unresolved reasons. Counterhypothesis: missing occurrence positions,
lost subsection labels or borrowed nearby division text prevent faithful use even
when a plausible USC target is returned.

Arms: current Rulespec scan (no named-act feature); direct imports of existing
RefSpec recognition/resolution with the two pinned indexes. No model changes,
network calls or copied parser. First inspect the data before designing changes.

Cases: first eight distinct authority texts in physical table order containing
`Act` plus `sec`, `section` or `§`, from the local Unified Agenda authority table.
Save complete selected rows and file/receipt identity before parser execution.
These are real derived publication fields, not an independent benchmark or full
document contexts. Also freeze constructed diagnostics for Clean Air Act section
111, a repeated citation, reversed order with `(d)`, a line-wrapped act name, a
nearby unrelated division, an unknown name, an unclassified section and absent
index files. The upstream saved Clean Air Act control expects USC 42:7411; verify
its raw index rows rather than treating an earlier test as legal authority.

Held constant: same strings, same selected index bytes, same source implementation
per capture. At most eight publication fields plus eight diagnostics in this
inspection. Capture load failures and all recognizer/resolver results. No default
or grammar is changed as part of this first observation.

Decision rule: adopt a thin connection only if required occurrences, qualifiers,
source support and native unresolved reasons survive. Successful target identity
alone does not pass the occurrence/meaning gate. If the owner lacks those fields,
fix that smallest upstream seam next and retain the original failed results.
Verify source and installed wheel before delivering any resulting integration.
