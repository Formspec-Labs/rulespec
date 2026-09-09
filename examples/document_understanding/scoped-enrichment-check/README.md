# Keep explanations while omitting empty enrichment

This narrower change retained the useful control explanations and removed every
null from the other optional fields, with **24–43% fewer output tokens per pair**.
The reviewed statement checks did not regress. This is a bounded improvement over
the experimental required-note controls; it is not a measured saving over current
production, which has no dedicated explanation field.

The [previous omission trial](../omit-empty-explanation-check/README.md) made the
explanation optional too and lost every explanation. Here the explanation's type,
requiredness, description and position stayed exactly the same in both arms.
Only other optional enrichment changed to non-null/nonempty strings with omission
instructions. The [preregistered plan](PLAN.md) records that bundle and the gates.

## Fresh results

N is the required-nullable control; E omits empty values from other enrichment.
Each cell is one fresh Gemini 3.8 Flash call, temperature 0, low thinking, 16,384
maximum output tokens, using a full notice or waste source window. Eight calls
were made, without retries, repair or audit passes.

| Field | Source | Output tokens N → E | Reduction | Non-null notes N → E | Useful note retention |
|---|---|---:|---:|---:|---|
| Logic | Notice | 3,707 → 2,117 | 42.89% | 0 → 0 | Untested; neither run supplied notes |
| Logic | Waste | 4,731 → 3,381 | 28.54% | 2 → 9 | Both useful control explanations retained |
| Modality | Notice | 3,894 → 2,468 | 36.62% | 9 → 18 | Useful and uncertain classifications retained |
| Modality | Waste | 4,440 → 3,363 | 24.26% | 13 → 14 | Useful control explanations retained |

Other optional fields emitted **390 nulls in N and zero in E**. Neither arm emitted
empty strings/lists/objects or literal null/N/A placeholders in those fields.
The required explanation slot still emitted **40 nulls in N and 23 in E**. This
deliberately does not solve all-null elimination: it isolates the larger source of
noise while preserving the explanation mechanism.

Output totaled 16,772 → 11,329 tokens, **32.5% fewer**, despite non-null notes rising
from 24 to 41. Reported input tokens were 12,230 → 12,442 and total tokens were
29,002 → 23,771, an 18.0% total reduction. Thinking-token counts were unavailable.
Changes to populated enrichment and record grouping also affect token use; these
savings cannot be attributed to null removal alone.

## Logic and modality behave differently

Logic retained the useful closure/venting explanation and excess-waste deadline
explanation. For example, E wrote:

> When accumulating excess waste at or near a point of generation, the generator
> must within three consecutive calendar days either comply with central
> accumulation area requirements or remove the excess to one of three specified
> destinations.

It also clarified the two required label components and cumulative excess-period
duties. Other notes repeated prohibitions or permissions. Neither notice run
provided any logic notes, so that source does not test retention of useful notes.

Modality retained explanations distinguishing recommendations, descriptive
possibilities and possible consequences. For example:

> 'May result' describes a potential consequence rather than granting permission.

But E wrote a modality explanation for every record, including straightforward
must/shall statements. The omission policy worked; the instruction to use null
when modal force is straightforward did not produce selective modality notes.
This remains a noise tradeoff, and increased explanation count is not an accuracy
improvement. The enum mappings for expected conduct and may-not-be-required remain
uncertain rather than adjudicated gold.

## Source fidelity and remaining failures

All named waste checks survived in both arms: satellite applicability, both label
components and illustrative methods, nested closure exceptions, excess trigger,
three-day alternatives, three removal destinations and generator categories.
The missing satellite context seen in the previous fully optional trial did not
recur. One call per cell does not establish a reliable repair.

All four notice runs still missed the unforeseeable-leave and unusual-circumstances
limits on the standalone designated-number/person permission (row 14). No named
statement check improved or regressed. A separate source-fidelity failure appeared
in the logic control T05: “may not be required” became “is not required” at row 16.
E retained the original uncertainty. This is an observed secondary difference,
not proof that omission caused a semantic improvement.

The logic control T04 omitted the parenthetical appendix-for-examples citation
from two statements, but retained it in their reference fields. Raw captures and
both representations remain available. Explanations never substitute for complete
statements or exact evidence.

## Decision

Both fields pass the other-field zero-placeholder and per-pair 20% output-saving
gates. Every useful control explanation observed was retained, and no named
correct statement was lost. Logic-note retention on notice remains untested.
These results support separating the explanation slot from the omission policy
for other enrichment.

The outcome is consistent with keeping a required slot helping preserve notes,
but this trial did not include a contemporaneous fully optional explanation arm.
It does not prove that requiredness alone explains the previous disappearance.

Do not add dedicated explanation fields to production based on token savings over
other experimental variants. No experiment here demonstrates a dependable accuracy
gain from those fields. Stop repeating this same development set for now. If
explanations are pursued, the next decision is their marginal value on untouched
documents compared with current statement-first extraction, with logic and modality
judged separately. A schema-only omission change without explanation fields is also
a separate production decision. No additional calls or production changes are made.

## Verification and artifacts

Native CUE generation verified identical explanation properties, required lists
and first-property order. Offline checks verified that the note is required and
nullable while other optional nulls/empty strings are rejected and omission is
valid. Empty-list omission remains prompt-controlled; no exporter changes were
made. Actual request schemas/settings and observed note-before-statement order
were checked on every run.

All 128 records were accepted; no schema/response errors, refusals or rejected
records occurred. All eight Core graphs validated. Unresolved reference records
remain: two per notice run and 32–43 per waste run. These checks establish
mechanical validity, not semantic completeness.

[Statement review](statement-review.json) was saved before reading explanations
and arm labels. Opaque IDs hid labels, though optional fields can hint at arms.
[Explanation review](explanation-review.json) matches useful notes by subject rather
than row position. These are revisable Codex judgments on development sources.
[Metrics](metrics.json) retain per-run tokens, placeholder locations and outcomes.
Requests, responses, source documents, schema/runtime hashes and original failures
are preserved. Production and previous experiments remain unchanged.

Replay checks exact requests and deterministic parsing/Core results without making
provider calls. From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/scoped-enrichment-check/run.py replay
```
