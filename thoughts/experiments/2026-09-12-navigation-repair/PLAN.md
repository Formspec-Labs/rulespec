# Does navigation improve the existing repair pass?

Decision: whether the newly available reference navigation is useful input to the
existing recovery operation. Do not add a production pass, change the schema or
automatically apply model proposals on this experiment alone.

Observed failure: IEP attendance statements omit the separately captured parental
writing requirements. Local reference navigation now identifies the two target
clauses and current claims. Previous inventory/confidence/checker passes missed
these standalone omissions despite seeing the full source.

Hypotheses:

- H1: making the existing source-to-claim associations explicit helps the current
  recovery pass put the required detail into the affected default statements.
- H2: recovery already succeeds without navigation; the earlier failures concerned
  checking rather than repair. Both arms should produce faithful repairs.
- H3: the model still treats retention elsewhere as sufficient, or overgeneralizes
  a reference into a prerequisite. Explicit associations then fail or regress.

Arms: A uses the current `RECOVERY` prompt/schema/packet. B adds only deterministic
navigation rows obtained from `context-export`, mapped to existing claim aliases.
Both arms receive the same full source, current draft, empty audit inventory and
the same one-sentence explanation of optional navigation's nonsemantic status.
No hand-picked correct semantic edges or defect labels enter either request.

Cases, fixed before calls:

1. Actual saved IEP confidence-arm book, all eight claims unchanged. C0004 must
   retain written parental agreement, C0005 written parental consent separately
   from the member's pre-meeting written input. Preserve all other conditions,
   kinds and modal force, and keep C0006 as a writing requirement. C0003 and C0007
   must not inherit the writing requirement. C0000's explicit-detail loss and
   C0006's actor are disputed/development issues, scored separately from the
   primary target gate; other edits get a raw source review.
2. Constructed USLM counterexample, not a fresh real document or model extraction.
   An electronic-request permission is followed by a required name/reference
   number and a separate agency annual-reporting duty. A second native branch has
   an inspection permission and annual-reporting duty. All three duties refer to
   their branch's clause (i). Add the required request contents to the first
   permission's default reading; do not make annual reporting a prerequisite for
   either permission, or transfer request contents across the repeated labels.

Held constant: gemini-3.8-flash, temperature 0, medium thinking, no numeric thinking
budget, 32,768 output cap. One sample per case/arm, randomized order and anonymous
cell IDs. At most four calls, no retries, and no new call after 900 elapsed seconds
or 120,000 reported tokens. Review anonymous outputs before revealing arm IDs.

Reuse assessment: existing `summary` plus grounded `context_quotes` can retain a
cross-clause requirement without changing the source requirement's kind. Core
already emits assertion evidence with `providesContext`; `scope_text` instead
emits `ApplicabilityScope` and `definesScope`, so do not misuse purpose text or
assert that a writing defect legally invalidates an exemption. A full source
quote or an isolated scope field does not pass the standalone-statement gate.
The current `requirement` qualification guard stays intact. Before model calls,
prove a constructed faithful edit compiles/previews through the existing code.

Checks: preserve requests, responses, settings, source/runtime pins and refused
proposals. Decode through existing recovery validation and preview on temporary
review copies. Verify original books/history, source positions, kinds, extra
evidence and replay; no real review actions. Manually assess all generated fields
for conditions, modality, wrong inheritance, unnecessary changes and bloat.

Decision rule: B must repair both IEP omissions and the request-content omission
in default statements without false inheritance, changed source requirement or
new loss. B gains over A support H1 on this small development set; equal success
supports using existing recovery but not an incremental navigation benefit. Equal
failure or regressions leave the hypothesis unresolved/rejected for adoption.
Any result still needs fresh real documents before a production quality claim.
