# Following prose is a real failure; neither shortcut earns adoption

**Decision: retain the installed reader.** The numeric-endpoint shortcut recovers
eight newly selected publisher citations but accepts eleven incomplete-range
controls incorrectly. The narrow prose rule fixes the original item-level example
and six constructed cases, but none of the eight fresh public-scanner examples.
Both fail the [predeclared decision rule](PLAN.md). No runtime code, dependency,
wheel, model prompt or installed package changed.

| Arm | Eight new publisher prose cases recovered | Constructed incomplete-range regressions | Decision |
| --- | --- | --- | --- |
| A: installed baseline | 0 | 0 | Existing failure retained |
| B: require readable numeric endpoint | 8 | 11 | Reject: accepts incomplete references |
| C: explicit comparative/instrumental prose forms | 0 | 0 | Defer: no recovery on the selected fresh public examples |

There are 37 comparison inputs: eight publisher paragraphs, the original bare
publisher paragraph, and 28 constructed controls. Eight earlier publisher-range
paragraphs provide an additional unchanged comparison. These selected cases and
revisable manual labels are diagnostic evidence, not a general accuracy benchmark.
The aggregate 22/37, 26/37 and 28/37 counts in [summary.json](summary.json) must not
be interpreted as accuracy: the two failure categories have different consequences.

## What the raw sources establish

The [selection](publisher-selection.json) retains complete XML paragraphs, nearby
raw context, byte positions and publisher-file digests verified against the saved
manifest. Selection took the first eight eligible paragraphs across titles 21,
41 and 49, without choosing for the candidate prose pattern. Seven follow `to`
with an action verb; the eighth uses `to be`. Examples:

- `21 CFR 1301.13(e)(1)(iv) to prescribe ...` appears in a practitioner's
  authorization condition, followed by an alternative registration exemption.
- `5 CFR part 2634 to protect personal information` follows a list of employee
  conduct standards in a privacy section.
- `41 CFR 301-51.100 to authorize and approve cash purchases ...` appears in a
  list of delegated functions, with cash purchases named immediately before it.
- `49 CFR part 191 to determine if control room actions contributed ...` appears
  in an incident-review requirement followed by a list of possible deficiencies.

The baseline preserves the starting coordinate and pinpoint inside a refused
occurrence but makes its identity-only result title-only. B correctly separates
these action phrases from the citation. C leaves all eight unchanged. This points
to infinitive/complement syntax as a broader problem than the original comparative
phrase. Adding the eight observed verbs would tune the sample rather than test a
general solution.

The [original XML](original-source.json) says `§ 50-202.2 to the same extent such
employment is permitted ...`. A's shared item reader captures `§ 50-202.2 to the`
with `range_end_unread`; B/C retain `§ 50-202.2` without that refusal. The normal
scanner returns no CFR reading for this bare citation in all arms: title inference
is still absent. The constructed explicit counterpart tests the shared defect
without claiming a production improvement on the original bare source.

## Why the tempting shortcut fails

B turns `41 CFR § 50-202.2 through` and `... through unknown` into accepted single
coordinates. It does the same to `... to the last section of this part`, unread
subsection endings and a third unread endpoint after a complete pair. The source
does not say that the first coordinate is the complete reference. The identity
API then publishes that shortened address; this is not merely cleaner display.

The cross-citation control retains the following independent `40 CFR part 60`
in all arms, but B also wrongly accepts the preceding unfinished title-41 range.
Counting occurrences alone would miss that defect. Complete ranges, list member
identity, pinpoints and exact source slices were inspected in the native captures.
All eight earlier publisher-range paragraphs remain exactly equal across the
occurrence, identity and authority APIs in all three arms; see
[existing-range-controls.json](existing-range-controls.json).

C does not solve general infinitive or agency prose. It also includes an awkward
constructed `to the same manner` spelling; that passing case is not independent
publisher evidence. Its six improved constructed cases and direct item-level fix
do not satisfy the separate requirement for a fresh public-scanner gain.

## Reproduction and next decision

[compare.py](compare.py) changes only the shared connector's `match` result in a
temporary in-process wrapper and restores it afterward. [runtime.json](runtime.json)
pins the installed grammar, harness and patterns. This is a deterministic reader
comparison; no model calls or repeated stochastic runs were involved. The
unchanged production implementation remains the baseline; no replacement check
was installed. Inputs and outputs use exclusive creation.

Copy the harness, selection and plan to a fresh experiment directory before a
rerun. Use `.tools/document-poc-venv/bin/python`, not the system Python. Source
selection uses standard-library ElementTree; an initial attempt found `lxml`
unavailable and was corrected before collecting source data. A later check used
the system Python accidentally and could not import RefSpec; the successful
comparison and old-range controls used the installed application environment.
Neither failed setup attempt produced a data result.

A future range change needs a different, source-supported way to distinguish
prose from unresolved endpoints, with these cases kept as development controls.
No additional NLP dependency or growing verb roster is justified by this result.
Keep this defect open, but stop treating it as a required quick fix before R17/R18
discovery and feedback. Those consumer tasks already have usable reference data
and an independent existing persistence route. Native-title inference, paragraph
reconstruction and target-edition matching remain separate unresolved work.
