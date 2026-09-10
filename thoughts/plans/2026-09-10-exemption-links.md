# Preserve exemption meaning while adding qualification links

Decision: extend the existing exemption candidate, edit/revision path and Core
RelationshipAssertion emission. No new operation, graph schema or duplicate
exception statement. An exemption remains an exemption with not_required force;
optional relation=exception and applies_to connect it to affected baseline IDs.

Standalone exemptions remain valid without a target. A linked exemption must
have relation exception and at least one target. Ordinary requirements/permissions
cannot carry qualification links. Self-targeting must remain unresolved.

The relationship proposal decoder may edit an existing exemption only to change
relation/targets. Its statement, kind, modality, components and source evidence
must match the prior record exactly. Reclassification proposals saved in the
relationship-audit experiment remain rejected, not silently rewritten. Explicit
review edits use normal revision history and stale-target handling.

Verification: native CUE generation/drift check; focused Core/refinement/review
tests; replay the three saved rejected edits unchanged to confirm refusal, then
test clearly labeled adaptations that retain original fields and add only the
proposed connection. Confirm same logical rule ID, new revision, unchanged
meaning, Core edge/evidence, reload, and stale/rejected target behavior. Include
ordinary-duty reclassification, self-link and non-exception relation negatives.

This is deterministic capability work. It does not establish model adherence,
correct selection of every target, complete default statement wording, or
section-wide applicability. No automatic target propagation or new provider
calls. No commit requested in this turn.
