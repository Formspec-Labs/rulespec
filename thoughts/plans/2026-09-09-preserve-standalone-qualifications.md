# Next focused task: preserve qualifications in standalone rules

Decision: Can the existing extraction profile produce a self-contained duty when
its source also permits a qualified departure, without merging unrelated rules?

Observed: transfer passport C0005 says posts must use cleared IRL language and has
no scope_text or logic_text. C0006 separately preserves permission to adapt that
language for local needs. The collection retains meaning, but a standalone C0005
consumer cannot see the qualification. The audit and independent inventory accept
the same split. This is a consumption risk, not proof that C0005 explicitly forbids
all modifications. The earlier notice C0014 is a clearer overbroad permission and
actually omits the unforeseeable-leave lead-in from logic_text.

Reuse: CUE #Summary guidance, scope_text/scope references and logic_quote selecting
a complete source range; existing EvidenceBinding and ApplicabilityScope conversion
where already connected. The waste transfer shows that current output can preserve
nested duties and exceptions in complete prose. No new Core schema, fuzzy matcher,
merging algorithm or extra audit pass is justified yet.

Proposed intervention: one profile-level instruction explaining that splitting a
qualification into another claim must not leave the original duty overstated when
read alone. State the qualification in the duty's existing statement/scope/logic
fields; a separate qualification record remains optional. Treat this as a hypothesis,
not a guaranteed fix. First inspect existing guidance to avoid duplicate wording.

Cases: saved passport cleared-language split; saved notice permission; successful
waste closed-container exceptions and three-day disposal alternatives as regressions;
constructed adjacent rules with different actors or independent permissions where
merging or copying conditions would be wrong. Use the original complete source
context. Newly inspected transfer cases are now development data.

Before any new provider calls, freeze a small baseline/treatment comparison using
the existing experiment harness and CUE-generated schemas. Hold model, thinking,
source and output settings fixed. Judge standalone meaning, whole-record meaning,
source support and instruction adherence separately. Retain uncertain labels for
the passport distinction and use the clearer notice failure to avoid relying on it.
Permission for this experiment is separate from the completed six-call transfer
check; no calls or profile changes for this next task have been made.

Success: qualifications survive in the original duty's explicit meaning, the known
notice lead-in survives, and complete groups/independent rules do not regress.
If the model still ignores the existing fields, stop adding synonymous prompt
patches and reconsider the representation or consumption boundary.

Lower-priority, separate work: local citation targets remain unresolved in the waste
case, and short/noncontiguous modality evidence still causes warnings/refusals.
Keep these outside the condition-preservation comparison so its result is interpretable.
