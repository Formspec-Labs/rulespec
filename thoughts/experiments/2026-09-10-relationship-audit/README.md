# Existing relationship pass: no incremental audit detection

The declared gate fails. Adding mechanically decoded relationship suggestions
did not help the current audit detect either missing remote qualification.
Keep this workflow experimental. Production, saved drafts, review history and
schemas remain unchanged; no commit was made.

## Comparison outcome

| Measure | Fresh current audit A | Audit plus relationship suggestions B |
| --- | ---: | ---: |
| Emergency-plan planted defects detected | 2/2 | 2/2 |
| Extinguisher planted defects detected | 1/2 | 1/2 |
| False alarms on four valid controls | 0/4 | 0/4 |
| Initial seatbelt duty's remote exclusion detected | No | No |
| Mechanically complete comparison runs | 3/3 | 3/3 |

These are repeated development cases, not fresh generalization evidence. The
four originally planted defects and four valid controls are constructed claims
over official source excerpts; seatbelts uses the saved full provider extraction.
All sources, claims and source-first inventories are unchanged from the preceding
experiment. All six comparisons are fresh calls, not historical controls.

Verdict: **no measured audit improvement; relationship-first mechanism not fully
realized**. Neither required remote qualification reached the audit as a decoded
relationship proposal. This is evidence against this tested bundle, not proof
that correctly selected relationship information could never help.

## Where the relationship information was lost

The relationship calls produced eight proposals: five decoded additions and
three refused edits. All five accepted proposals were supplied to B without
manual selection. Existing fields, source evidence and aliases were retained.

| Stage/result | What happened |
| --- | --- |
| Emergency-plan relationships | Correctly linked oral-plan exception to writing and OSHA-required trigger to the unconditional plan duty. No exemption of training. |
| Extinguisher local exception | Correctly linked during-use exception to the general placement duty. Both audit arms already catch this omission. |
| Extinguisher remote exemption | Raw model correctly paired outside-building exemption C0003 with distribution C0000, but tried to edit the existing exemption into an exception. Decoder refused this operation. |
| Extinguisher designated-user exemption | No proposal linked it to distribution. No link was misapplied to maintenance. |
| Seatbelt local links | Raw proposals correctly paired dock personnel and the 91.105 exemption with passenger seating, not pilot briefing duties; both edits were refused. |
| Seatbelt general exemption | Model called the part 121/125/135 exclusion already represented as a standalone exemption and omitted links to the affected rules. |

The five decoded additions contain seven target references total: two emergency-
plan targets, one extinguisher target, three pilot/passenger targets for
Administrator authorization, and one lap-child permission target for the
91.108(j) cross-reference. The last proposal preserves the unresolved external
reference; it does not supply the external rule's content.

Five observations also remain recorded: three unresolved absent-baseline cases
and two already-represented notes. They are not API failures. The three rejected
edits remain in the raw captures and decoded refusal records; they were not
silently repaired or presented to B as accepted suggestions.

## Why this is more specific than another prompt failure

Two different boundaries are visible:

1. **Recognizing a link versus proposing an allowed operation.**
   refinement._decode_proposals rejects relationship-stage edits of records whose
   existing kind is not condition or exception. The rejected originals here are
   exemptions. core._claim likewise permits applies_to only on condition/exception
   candidates. The model tried to change their kind to add a connection, which
   conflicts with preserving baseline records. Removing that protection would
   not be a justified fix. The intended operation is to add a supported connection
   while preserving the existing statement and its normative meaning.

2. **Recording an exemption versus connecting its scope.**
   For the section-wide seatbelt exclusion, no candidate link was produced. The
   relationship rationale explicitly says the standalone exemption is sufficient
   and has no specific single-rule target. Yet this pass already permits multiple
   targets. Resolving the edit-operation mismatch alone therefore cannot solve
   both required failures.

Rulespec Core already has RelationshipAssertion and EvidenceBinding, and the
extractor already emits qualification edges with supporting evidence. The design
gap is how the application proposes connections from existing exemption records
without replacing them, plus how it treats section-wide qualifications. A new
general graph schema is unnecessary. No independent link operation was built or
tested here, and no claim is made that it would fix the model's omitted targets.

All tested audit variants still accept a local rule as complete while accepting
its remote exemption separately. That contradiction remains a useful review case.
The audit's passed status on seatbelts is not accepted as semantic validation.

## Usage, settings and verification

| Provider-reported tokens | Audit A | Audit B only | Relationship stage | Full B workflow |
| --- | ---: | ---: | ---: | ---: |
| Input | 25233 | 27145 | 39199 | 66344 |
| Answer | 10945 | 10971 | 4168 | 15139 |
| Thinking | 10224 | 10084 | 31212 | 41296 |
| Total | 46402 | 48200 | 74579 | 122779 |

Full B used about 2.65 times A's reported total tokens, with no measured detection
gain. Cost accounting includes the three relationship calls. This is token usage,
not a monetary invoice; a single run per case cannot establish stable costs.

All nine calls completed within the bound, with no retries. All report the same
gemini-3.8-flash model version; all requested temperature 0, medium thinking and
32768 output tokens. Fresh paired audit requests differ only by the exact saved
unverified-proposal addition. Source, inventory, draft, audit instructions and
response schema otherwise match. The relationship request uses the existing
RELATIONSHIPS prompt, proposal schema and packet conversion unchanged. The
original complete refine_run recovery/challenge/apply workflow was NOT run.

All raw responses parsed. Three relationship proposals were refused for their
operation, as described above. The six audits had no processing issues and
review_complete true. Partial constructed-draft coverage and real defects yield
failed audit reports for emergency plan/extinguishers; both seatbelt audit reports
pass despite the known omission. All verdicts are retained.

Frozen replay reproduced relationship decoding, added audit text, judgments,
reports and paired-request checks without provider calls. Runtime source hashes
were checked against the pre-call freeze. Manual assessment read every raw
proposal, all observations and all claim/unit audit rationales against pinned
source. BLIND-REVIEW.md was written before opening the A/B map; the masking is
partial and the assessment remains revisable, not gold.

## Stopping point

Do not add this expensive prepass to production on these results. Consolidate the
findings before another model experiment. The next bounded engineering decision
is whether an existing exemption can acquire an independently evidenced outgoing
qualification connection while retaining its own kind, statement and history.
Assess the existing Core edge representation and application review operations
first. Treat section-wide scope propagation as a separate unresolved requirement;
do not equate a stored standalone exemption with complete applicability links.

The successful display-overlap experiment remains a separate possible consumer
improvement. Neither failed semantic experiment cancels its measured lossless text
reduction, and that display result does not justify shipping a new audit stage.

Reproduce from repository root, without provider calls:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-relationship-audit/experiment.py replay
```

PLAN.md/design.json pin the comparison; inputs/ contains exact frozen books,
inventories, packets and baseline prompts. Original source provenance is in those
books and the preceding experiment's sources/. relationships/ retains raw and
decoded proposals. cells/ retains both audit arms. measurements.json includes
all nine calls, request-checks.json verifies actual inputs, and frozen/ retains
shared runtime sources. No new source download or external legal lookup was used.
