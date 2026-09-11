# Preserve generated meaning through passage and evidence processing

Decision: adopt the smallest source-grounded fixes for the two deterministic losses
identified by the completed fresh-reference-context experiment. These changes do
not adopt its failed model/context intervention.

Hypotheses:

1. Passage-range losses come from catalog numbering holes, not unseen content.
   Resolving the supplied endpoints and existing entries between them, while
   retaining the non-whitespace gap check, should recover the nine observed rows.
   A counterexample crossing unprovided content must remain refused.
2. Complete-quotation losses come from the single-fragment source-map restriction.
   Reusing original-source slices and existing multiple-fragment evidence bindings
   should preserve eligible full statements without treating inserted formatting
   as original evidence. Incorrect spans, non-whitespace insertions and genuinely
   contradictory meanings must not become accepted as a side effect.

Arms: unchanged installed baseline; passage-range fix alone; compound-evidence fix
alone; both fixes. Compare each question independently before combining. Snapshot
the baseline application before edits. Do not change the model schema or prompts.

Cases: all twelve captured cells from `2026-09-11-fresh-reference-context`, including
the incomplete output. Their original manifests remain unchanged. The diagnostics
identify nine range refusals and 103 exact main-quotation refusals across repeated
outputs, plus seven separate kind/modality contradictions. Counts describe events,
not distinct legal rules. Further previously hidden errors may become visible after
an earlier refusal is removed; report them instead of forcing an accepted count.

Constructed controls: newline/space/Unicode blank gaps; mixed focus/context,
missing endpoints, leading-zero or reversed IDs, non-whitespace omitted text,
overlapping spans, and large numeric gaps. Evidence controls cover original versus
inserted whitespace, non-whitespace insertion, all-inserted text, mixed sources,
wrong positions, repeated text and Unicode, compound definitions/components,
qualification targets and review tampering/reload. Labels are mechanical and
source-coordinate checks, not a general semantic judgment.

Held constant: source bytes/maps/passages, raw provider responses, request catalogs,
model settings, schemas and unrelated parser behavior. No provider calls. Use
direct imports first, then rebuilt wheels outside the checkout for adopted code.
Run the fixed cells and relevant controls once per distinct implementation; retain
failed attempts. Run the affected package suite after integration. Repetition is
for a changed implementation or observed failure, not to improve a score.

Decision rule: adopt a fix when it resolves its actual source-supported failures,
preserves existing successful outcomes/identities unless the changed evidence
requires a new revision, rejects counterexamples, and survives Core/discovery and
review checks. The incomplete provider output remains incomplete. Definitions,
component evidence and relationship support must not silently retain only one
piece of a compound quotation. If a consumer assumption blocks the full outcome,
fix that owner or leave the relevant adoption open with the evidence recorded.

Stop this comparison at a documented adopt/defer outcome and verified local
delivery. Broader citation integration, discovery value and workflow preparation
remain on the canonical R1–R26 backlog. Runtime capture coverage is a separate
delivery check, not an extra model intervention.
