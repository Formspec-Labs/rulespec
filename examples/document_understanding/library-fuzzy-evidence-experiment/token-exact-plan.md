# Follow-up: does recovery require fuzzy matching?

Observation after the nine fixed configurations: all six LangExtract recoveries
report match_exact, which refers to token alignment rather than identical source
characters. New decision: whether fuzzy fallback is necessary for these recoveries.

Compare the already-recorded strict 1.0/1.0 LangExtract result with the same public
Resolver.align call using enable_fuzzy_alignment=False and accept_match_lesser=False.
Reuse all 29 controls and the same saved audit, with no other change. Expect the
six recoveries to remain if token-exact alignment is responsible. Any loss weakens
that explanation. Preserve all ambiguity/layout outcomes; this is not an adoption
gate or an attempt to improve the earlier nine configurations. No provider calls.
