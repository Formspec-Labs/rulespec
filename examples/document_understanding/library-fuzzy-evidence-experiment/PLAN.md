# Configurable library fuzzy matching

Decision: characterize whether known configurable matchers can recover the saved
comparison evidence while respecting the declared rejection cases. No production
adoption is part of this experiment.

Libraries: fuzzysearch 0.8.1 `find_near_matches` (actual substring search with source
offsets and separate insertion/deletion/substitution limits), and the already
installed LangExtract 1.6.0 `Resolver.align` LCS token aligner. No bespoke edit-distance
or similarity algorithm. Reuse the previous experiment's controls and audit harness.
The previous whitespace-only arm remains the recorded reference, not a fuzzy library.

Configuration grid, fixed before calls: fuzzysearch character budgets 1 and 2;
5%, 10%, 15% of quote length (floor, capped at 64 edits); and an asymmetric setting
of at most 32 source insertions, 1 substitution and 0 query deletions, total 33.
LangExtract coverage/density pairs 0.75/one-third, 0.95/0.95, 1.0/1.0, LCS algorithm,
accept_match_lesser=False. Coverage means extraction tokens retained, not probability
of correctness. Similarity scores/budgets are never confidence scores.

Cases: preserve all prior 23 controls and labels, plus three intended typo/format
recoveries (transposition, OCR rn/m, curly apostrophe) and three meaning-changing
long quotations (inserted negation in the real C0006 quote, dropped negation and
changed number). Run the same full saved 36-judgment audit for each setting.

Assessment: report original literal-policy labels separately from semantic danger.
The inherited case-change, zero-width-change and thousands-comma cases are strict
policy differences, not established meaning errors. Table/list joins are layout
risks, not proof that returned source coordinates are wrong. Negation, numbers,
AND/OR, omitted intervening words, ambiguity and out-of-window/inserted text remain
rejection controls. Existing exact fragment behavior cannot establish meaning.

Hypothesis: a configuration may recover actual refusals while avoiding content-
changing matches; any acceptance of meaning-changing long quotes weakens an
acceptance policy even if short quotes pass. Identify recovery/false-acceptance
tradeoffs across the full grid; do not silently choose a favorable threshold.

Keep exact-first matching, source windows, raw responses, verdicts, source-map guard
and original source-offset output equal. The adapter accepts only one returned
candidate after deduplicating identical offsets. Library candidate selection is
not exhaustive uniqueness proof: fuzzysearch consolidates overlapping matches;
LangExtract emits one selected alignment for each extraction. Report their behavior
on repeat/overlap controls explicitly. Do not invent a homegrown disambiguator.

Run once per deterministic setting, with no provider calls and no tuning after
results. Bound: 9 settings times 29 controls and one saved audit each. Inspect raw
match spans, distance/alignment status and audit accounting. Source and original
captures remain unchanged; pin installed library versions and files. Passing these
selected development cases would justify further testing, not general semantic
accuracy or automatic adoption. No passage-ID comparison is performed.

Sources consulted before implementation:
- https://github.com/taleinat/fuzzysearch (API and edit-budget semantics)
- Installed LangExtract resolver.py, including Resolver.align parameters and LCS
  coverage/density semantics; existing production extraction does not enable this
  alignment path for the comparison stage.
