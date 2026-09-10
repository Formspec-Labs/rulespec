# Explicit contrast audit: no measured accuracy improvement

The six fresh comparison calls completed. Requiring an explicit applicability
contrast in each rationale did not improve confirmed defect detection on either
fresh source. The declared advance gate fails; retain the existing audit prompt.
No production files, schemas, UI, review history or original extractions changed.
Experimental artifacts are saved locally; this work has not been committed.

## Results against the predeclared cases

| Measure | Current audit A | Explicit contrast B |
| --- | ---: | ---: |
| Emergency-plan planted defects detected | 2/2 | 2/2 |
| Emergency-plan valid controls falsely flagged | 0/2 | 0/2 |
| Extinguisher planted defects detected | 1/2 | 1/2 |
| Extinguisher valid controls falsely flagged | 0/2 | 0/2 |
| Known seatbelt remote-exclusion defect detected | No | No |
| Mechanically complete comparison runs | 3/3 | 3/3 |

These are selected diagnostic counts, not a general accuracy rate. The eight
fresh-source claims are constructed examples, with four deliberate defects and
four valid controls. The seatbelt case uses the full saved 17-claim provider
extraction. One observation per arm/case cannot establish stability.

B adhered to the explicit rationale format on all 25 assessed claims: it supplied
a concrete source/draft contrast for three errors and an explicit no-contrast
statement for the other 22. That is instruction adherence, not proof that the
counterexample search succeeded. No new material false alarms were observed on
the four predeclared valid controls, and no additional material meaning regression
was identified in the other-dimension comparison. The broad gate still fails.

## Raw examples explain the limit

**Local exception found by both.** The constructed extinguisher duty omitted
"except during use." A identifies the lost temporal boundary; B explicitly
describes an extinguisher being used during a fire as a case the draft would
incorrectly prohibit. The explanation is more concrete, but the detected defect
is the same.

**Remote exception missed by both.** The Class A distribution draft omits the
outside-building and designated-user-plan exemptions that limit paragraph (d).
Both accept the draft as correct, citing only its local passage F015. B says
"No supported applicability contrast" even though it separately accepts the
outside-building exemption (F002) and designated-user exemption (F006).
The source and both exemptions are present in the actual requests.

**The saved seatbelt failure remains.** Both audits accept the initial takeoff
duty as complete without the section's part 121/125/135 exclusions. Both also
accept the separate exclusion statement. Neither selects the exclusion passage
F024 when assessing that initial duty. Both report the complete seatbelt draft
as passed; our manual assessment rejects that conclusion for standalone meaning.

The shared inventories exhibit the same split: local duties and remote exemptions
are recorded separately, while the duty's inventory meaning lacks the remote
restriction. This supports investigating how dependencies are connected. It does
not prove the inventory caused the failure: both comparison arms also had the
full selected source, and no inventory intervention was tested.

Verdict dimensions also vary without changing defect detection. For the missing
oral-plan exception, A marks scope error while B marks scope correct and flags
summary/alternatives. For the during-use exception, A flags boundary and B action.
Both explain the actual defect. A single dimension's error count would therefore
misrepresent the semantic comparison.

## Usage and processing

| Provider-reported tokens | A, three comparisons | B, three comparisons |
| --- | ---: | ---: |
| Input | 25233 | 25557 |
| Generated answer | 9328 | 11102 |
| Thinking | 16994 | Not fully reported |
| Total | 51555 | 39257 |

B generated 19.0% more answer tokens but reported 23.9% fewer total tokens. Two B
runs reported substantially fewer thinking tokens than their controls; the third
did not report a thinking-token value. Missing is not recorded as zero. All
reported total values are retained rather than reconstructed from incomplete
components. This is a possible efficiency signal, not a repeated cost result or
an invoice estimate. A separate repeat comparison would be needed to test it.

The three shared inventory calls used 21553 reported total tokens. All nine calls
together used 112365 reported total tokens. No retry was made. Model versions all
report gemini-3.8-flash. Settings were temperature 0, medium thinking and 32768
maximum output tokens. Paired actual request bodies match exactly after removing
the sole preregistered prompt addition; schemas, source, draft, inventory, model
and configuration remain constant within each pair.

All three inventories and all six comparison outputs parsed and grounded through
the existing audit helpers without processing issues. Frozen replay reproduced
all inventories, labels, judgments and reports. Both emergency-plan and
extinguisher reports have status failed with review_complete true, as expected
from real defects and intentionally partial drafts. These verdicts are retained;
they are not failed API calls. Both seatbelt reports pass mechanically but miss
the known semantic defect. Semantic completeness remains not_established.

## What to do with this result

Do not add the explicit-contrast instruction to production. It mostly makes the
audit's existing behavior more verbose on this set. Keep the separate successful
display-overlap result separate from this failed semantic-improvement gate.

The next distinct hypothesis would be to assess **which claims each source
qualification governs before judging claim correctness**, using source passages
and existing claim IDs. That changes the order and focus of the task instead of
asking for more elaborate explanations. It must include cases where an exception
applies to distribution only and cannot propagate to maintenance. Merely finding
an exception elsewhere in the document is insufficient. This approach remains
untested and would require a new bounded plan; no additional calls were made.

## Reproduction and provenance

Sources were downloaded as 2025 government snapshots:

- [29 CFR 1910.38, emergency action plans](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol5/xml/CFR-2025-title29-vol5-sec1910-38.xml), full section.
- [29 CFR 1910.157, portable fire extinguishers](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol5/xml/CFR-2025-title29-vol5-sec1910-157.xml), selected contiguous paragraphs (a) through (d).
- Seatbelts: the existing consistency-transfer/cells/cell-00/rulebook.json,
  unchanged, with its complete pinned source.

Source search found no prior saved experiments using the two new section numbers.
That is a repository-history check, not a claim about model training exposure.
Raw XML, complete extracted text and selected text are retained. Section (e)
onward is outside the extinguisher excerpt; those referenced provisions remain
unresolved. The investigator reviewed selected source, all inventory meanings,
all comparison claim/unit rationales and source references. Numerical cell labels
were used before inspecting the arm map, but the output format revealed the
intervention, so the review is not fully blinded. Agent labels are revisable.

PLAN.md and design.json pin pre-call criteria, inputs, settings, random order and
runtime. expected.json distinguishes faithful readings from deliberately flawed
drafts. setup-failure/ preserves the initial candidate preparation mistake and
correction before any model calls. inventories/ and cells/ preserve every actual
request, provider response and derived result. frozen/ saves the shared runtime.
measurements.json records request checks and all usage, including missing values.
BLIND-REVIEW.md records the assessment before opening the arm map.

From repository root, replay without provider calls:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-explicit-audit-contrast/experiment.py replay
```

The comparison schema is the existing audit module's wrapper, using existing
profile meanings and source-reference types. No newly invented provider schema
or extra explanation field was introduced. This is a bounded audit diagnostic,
not an end-to-end extraction-quality or production-adoption test.
