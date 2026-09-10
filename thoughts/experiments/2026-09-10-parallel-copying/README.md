# Reducing copying: link edits help; actor references remain experimental

**The smaller exemption-link response preserved all five correct links and reduced proposal answer tokens by 85.8%. Actor references showed no grounding improvement over the current distinctive-quote instruction and selected unnecessary surrounding text. Neither mechanism was added to production.**

Twelve live Gemini 3.8 Flash calls completed without retries, missing responses or incomplete output. Temperature 0, maximum output 32,768, provider-default thinking. Input sources and expectations were frozen before their respective calls. This is one sample per case/arm, using a saved railroad packet, two saved alcohol exception proposals, and a constructed actor-versus-approver control. The actor labels were supplied; this does not measure actor discovery. No full audit was run.

## A. Smaller existing-exemption link edits

Both arms received the complete saved railroad source/draft/audit packet and the same restricted task: link existing exemptions. A used the current production full-field schema. B returned only claim alias, target aliases and rationale. The experiment reconstructed all unchanged fields from the existing record, then reused production decoding, preview, passage-reference challenge, review history and discovery export.

| Measure | Full fields A | Small edit B |
| --- | ---: | ---: |
| Correct links proposed / applied | 5 / 5 | 5 / 5 |
| Wrong links / refusals | 0 / 0 | 0 / 0 |
| Proposal answer tokens | 3,076 | 437 |
| Proposal total tokens | 30,614 | 27,258 |
| Proposal + challenge input tokens | 52,969 | 53,042 |
| Proposal + challenge answer tokens | 3,733 | 1,043 |
| Proposal + challenge thinking tokens | 6,080 | 3,060 |
| Proposal + challenge total tokens | 62,782 | 57,145 |

All five stopping exemptions C0009–C0013 target C0000. Neither arm targets the separate safe-crossing permission, gear-shifting prohibition or sign-installation authority. Every existing meaning field and evidence record remains unchanged except the intended relation/targets. The full-field baseline made no copying error: **no error-rate improvement was observed**. The 9.0% complete-route token reduction partly reflects variable thinking and is not a stable cost estimate. Cached-input usage is preserved in raw metadata; token totals are not dollar costs.

Twelve offline checks pass. Empty, self, nonexistent targets and attempted extra meaning edits are refused. The ordinary production equality protection also rejects a constructed rewritten statement. A wrong but existing target, C0009→C0002, passes mechanical decoding; this is explicitly recorded as a semantic negative, never applied. No claim is made that schemas establish correct applicability or that this negative was challenged live.

**Decision: bounded efficiency improvement; investigate a narrow link-edit integration.** This tests existing exemption links only. Additions and other edit types still need their existing representation. Retain the source challenge and equality checks; do not infer a general semantic improvement or whole-workflow savings rate.

## B. Actor evidence: diagnostic and current-guidance comparison

The initial diagnostic deliberately requested shortest copied quotations. It reproduced the actual historical failure: `driver` could not resolve within the short exception quote or uniquely across the full alcohol source. References selected the parent driver/possession passages and resolved both. Both arms correctly distinguished Staff's two duties from the Director's approval duty.

That shortest-quote instruction is **not current production guidance**. Once identified, it was preserved as a diagnostic and followed by a separately preregistered four-call comparison using the existing advice to select longer distinctive quotations when short words repeat. These fresh calls count in the total; no previous observation was overwritten or retried.

| Measure, two cases / four fixed actors | Current distinctive quotes A | Passage references B |
| --- | ---: | ---: |
| Exact usable support records | 4 / 4 | 4 / 4 |
| Wrong actor/occurrence selections observed | 0 | 0 |
| Input tokens | 1,499 | 1,491 |
| Answer tokens | 241 | 366 |
| Thinking tokens | 3,223 | 17,309 |
| Total tokens | 4,963 | 19,166 |

A returns `(a) No driver shall—` for both alcohol exceptions: this is unambiguous, valid support for the fixed driver label. B returns ranges F000:F004 and F000:F005. They include the required possession scope but also unrelated alcohol-use prohibitions; the passenger selection includes the shipment exception too. The original reference diagnostic selected the narrower F000 + F003. This variation shows that references do not themselves produce concise evidence. The 3.86× token increase is a single-sample observation, mostly thinking, not a projected production multiplier.

The Staff control passes through both representations. A selects `Staff must file reports` and `Staff must archive receipts`; B selects the corresponding full passages, retaining Director as approver. Existing parent-relative matching already resolves the short occurrences correctly.

**Decision: no measured grounding improvement over current advice; do not adopt actor references from this test.** They avoid copying and preserve selectable positions, but the tested output also adds evidence bloat and variable cost. Existing production advice deserves credit for solving the actual short-quote ambiguity in this focused comparison.

## Persistence and replay limits

The experiment reuses the CUE-derived `audit.SOURCE_REFS`, `extraction.resolve_passage`, and Core `_evidence` fields, including source text, offsets and fragment identity. A constructed identical-passage control proves that explicit offsets select the intended second occurrence while quote-only matching refuses ambiguity; it never chooses the first occurrence.

Current actor candidate fields hold one `actor_quote`. They cannot preserve arbitrary multiple selected spans or selected offsets for identical repeated full passages. Actor reference results here are experimental support records, **not a completed production persistence/review integration**. Existing full quote matching works for the distinct selected live passages. This is a useful boundary to revisit only with a real unsolved production case.

Both [initial](replay.json) and [follow-up](followup-replay.json) saved responses decode identically with zero provider calls. Link review snapshots rebuild from retained histories, original fields/evidence match, and discovery export is saved. Actor replay checks exact selected source positions and Core evidence records; it does not demonstrate persistence through a new actor schema. The [assessment](assessment.json) excludes the two copied historical extraction runs: **12 new requests, 151,747 reported total tokens**.

The same agent selected cases and reviewed outputs; response shapes reveal arms. These are revisable manual judgments, not independent benchmark labels. Source cases are development data. No production files or previous captures changed.

- [Original preregistration](PLAN.md) and [current-guidance follow-up](FOLLOWUP-PLAN.md)
- [Raw semantic review](MANUAL-REVIEW.md)
- [Offline controls](controls.json)
- [Frozen inputs / code fingerprints](design.json) and [follow-up fingerprint](followup-design.json)
- Raw requests and responses: `cells/*/{proposal,challenge,actor}/attempt-0000.*.json`
