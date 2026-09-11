# Reference feedback through existing review history

Decision: connect one durable reference-feedback operation to the current review
store without a second store, claim approval, parser correction or model pass.

Hypothesis: retaining the selected reading and its source/reader context preserves
what was challenged after a rescan, where retaining an occurrence ID alone cannot.
The existing observation action should preserve this data through reload/export.
This compares two constructed feedback designs; an ID-only reference-feedback
product does not already exist.

Arms: A records only an accepted reference ID (or rejected source position).
B records the selected immutable reading, document pin, parser/index pins and
referenced target context, then uses the same `ReviewStore.apply(observe)` route.
No new scan IDs, source IDs or Core types are required. Rejected records can be
selected by collection/index in the saved scan; the observation must preserve
their actual data rather than rely on that mutable array position afterward.

Cases: the retained reverse-CFR XML (including two identical part references at
different positions), the newly selected publisher infinitive/refusal paragraph,
and existing USLM local/external-target fixtures. Constructed mutations cover a
changed reading with the same occurrence ID, wrong document, forged evidence,
invalid selection, stale review revision, absent optional readers during reload,
and a grounding refusal without verified original-source evidence. Preserve an
earlier observation when adding a follow-up. Do not relabel a reported mistake as
an established legal fact or transfer claim approval.

Held constant: same saved sources and reader output, no model calls, at most 20
focused regression cases. Use existing document validation, source-fragment
verification, canonical hashing, review actions, Findings, and CLI output helpers.
Core's Finding already stores the observation rationale and subject; a new Core
schema is unnecessary for this optional application operation.

Decision rule: B must preserve the challenged reading/version, exact source
evidence and distinct repeated occurrences through normal commands and reload;
reject wrong-document and forged-evidence submissions; preserve unresolved
grounding; and leave claims, approvals and scanning behavior unchanged. Keep
external source IDs and target text separate from primary-document evidence.
Capture only selected target/record/fragment context, not unrelated scan bodies.
If this passes, connect the command, test direct imports, then build/install the
application wheel and verify normal command behavior outside the checkout.
This does not complete a reference-feedback UI, source-only review workspace,
automatic resolution, or the broader discovery-value comparison.
