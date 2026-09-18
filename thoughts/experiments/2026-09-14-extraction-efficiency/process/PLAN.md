# Source assembly instead of rewriting: bounded process pilot

Decision: Is a source-annotation path worth a broader trial as an alternative to
rewriting every meaning, particularly for discovery? This does not authorize
adoption or replacement of independently usable workflow statements.

Hypothesis: Selecting exact primary clauses and explicit governing passages can
retain details that generated summaries omit, with lower generation tokens.
The hypothesis weakens if the model still omits governing context, treats nearby
clauses as scope, combines independent forces, or spends similar total tokens.
Assembly removes paraphrase loss only for text actually selected; wrong selection
and wrong classification remain possible.

Arms: A is the current production prompt and CUE-derived extraction schema.
B is a deliberate process bundle: same passage catalog and field definitions for
terms, actors, kind, modality, and primary selection; no generated statement,
scope description or choice description. It selects governing and background
passages separately, and code renders exact quotations with those roles. B uses
an experimental subset/extension of generated schema, not a production schema.
No automatic legal inheritance from headings or proximity. The study cannot
attribute changes to one prompt sentence or one removed field.

Cases: The unchanged section-focused windows for 42 USC 9908 and 9910 from the
2026-09-13 complete CSBG retest, pinned release 119-102. These are development
cases, not fresh independent documents. Full notes and source passages remain.

Predeclared quality checks (manual, revisable source labels):

1. All thirteen 9908(b) contents individually addressable, even if item (1) splits.
2. Retain urban-origin best practices AND methodologies for widespread replication.
3. Retain low-income beneficiaries of coordinated service delivery, b(5).
4. Retain on-request Secretary submission and optional coordinated assessments, b(11).
5. Retain performance system alternatives and FY2001 timing, b(12).
6. Preserve State-plan assurance/content framing, rather than making every listed
   program activity an unconditional direct duty.
7. Keep discretionary State-plan revision and mandatory submission distinguishable.
8. Counterexample: redistribution for funding reduction must not become a cause
   for termination merely because the next paragraph shares a parent.
9. Retain private nonprofit CSBG scope for the appointive-official exception, 9910(a).
10. Counterexample: public organizations retain the alternative State mechanism;
    they must not inherit private nonprofit elected-official board requirements.
11. Report the FY2000 transition override explicitly as source context/meaning;
    do not silently make current subsection (b) duties unconditional for that year.

Also assess how much unrelated evidence each reading includes and whether a
consumer can understand it without consulting a separate document. Exact but
uninterpreted bundles do not count as executable or approved rules.

Held constant: Actual source windows/catalog, model gemini-3.8-flash, low thinking,
provider-managed sampling, 16,384 generation tokens, one call per arm/source.
Alternating AB/BA order. Stop after four calls or 15 minutes; no retries or tuning.
Use existing capture, passage resolver and baseline decoder. Validate the
experimental output and reference selections locally. Retain exact requests,
responses, model versions, runtime hashes, failures, and token counts including
thinking. No checker/model judging calls; raw review by the investigating agent.

Decision rule: Broader investigation only if B preserves every tested baseline
success, fixes at least one observed loss or saves at least 20% total tokens,
and avoids new cross-branch scope errors. Otherwise no adoption; identify whether
the useful result is bounded to discovery or whether source-unit granularity
prevents self-contained meaningful statements. Four calls cannot justify default
adoption or general accuracy/cost claims. Production stays unchanged.

Prior work considered: source-plus-context comprehension helped when the relevant
passages arrived but missed remote scope (2026-09-10-design-context); indiscriminate
source/statement concatenation harmed retrieval (2026-09-10-design-pilots);
full/sparse repairs did not fix fresh omissions (2026-09-13-repair-finish).
This pilot tests avoiding paraphrase generation, not another audit or repair pass.
