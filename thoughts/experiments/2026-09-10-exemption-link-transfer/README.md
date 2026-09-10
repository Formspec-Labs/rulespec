# Exemption linking improved on two fresh source sections

**Bounded improvement.** The updated relationship instructions and decoder
produced six correct, usable exemption links versus zero usable links from the old
workflow. Four of the six links were on fresh source sections. No incorrect
exemption targets appeared in these samples. The prespecified gate for a larger
evaluation passed; this does not justify adding an automatic relationship pass.

## What changed in the result

| Fixed draft | Expected exemption edges | Old raw / accepted | Updated raw / accepted |
| --- | ---: | ---: | ---: |
| 1904.1 recordkeeping — fresh section | 1 | 1 / 0 | 1 / 1 |
| 1910.119 process safety — fresh section | 3 | 0 / 0 | 3 / 3 |
| 1910.157 extinguishers — development case | 2 | 1 / 0 | 2 / 2 |

The updated workflow recovered all four positive exemption target sets. These are
four exemption records, not six independent document successes: one section-wide
record has three targets. Both arms passed the empty-target small-company control.
Neither exempted incident reporting, modified a definition, or excused maintenance
through a distribution-only exemption. Neither created duplicate companion
statements for the already existing exemptions.

The old model outputs found two correct connections but attempted to turn the
exemptions into `exception` records. Both decoders refused these rewrites. They
also called the other two exemptions already represented and left them unlinked.
The updated outputs retained each original exemption's full fields and exact
quote and changed only relation/targets. The updated decoder accepted all four
edits; the old decoder refused them. This distinguishes improved target discovery
from the separate improvement in expressing and accepting the discovered links.

The process-safety result is the clearest fresh transfer: the updated output
connected the single section exclusion to all three employee-participation duties,
leaving the hot-work definition alone. The old output explicitly claimed that the
standalone exclusion needed no link. Thus the earlier broad hypothesis that the
model cannot connect section-wide exclusions is weakened; representation guidance
can affect that behavior on this constructed draft. The historical seatbelt
failure itself was not rerun or demonstrated fixed here.

## Mechanical checks and limits

- Six calls returned complete, parseable responses. No retries or prompt tuning.
- Each raw capture was decoded with both versions; replay matched all results.
- Actual requests match on model, temperature, thinking level and output allowance.
  Only prompt and schema guidance differ; schema structure is unchanged.
- All six accepted proposals across the respective arms passed isolated review
  previews: the old during-use addition, four updated exemption edits and the
  updated during-use addition. All four edits retain meaning/evidence and logical
  identity, create a new pending revision, and resolve the expected targets.
- Original extraction/review files were untouched. No automated challenge stage,
  human approval or changes to a user's saved rulebook were exercised.

The old process-safety addition failed exact-evidence validation: its `logic_text`
was synthesized, including ellipses. Two old extinguisher observations also failed
grounding. These failures are retained in the assessment, not hidden behind the
exemption-link score. The updated outputs still left additional positive scope
conditions and an unrepresented exemption unresolved. Complete applicability and
default statement wording remain separate work.

## Cost and uncertainty

| Reported usage across three calls | Old | Updated |
| --- | ---: | ---: |
| Input tokens | 11,327 | 11,570 |
| Answer tokens | 3,776 | 3,055 |
| Thinking tokens | 30,267 | 15,791 |
| Total tokens | 45,370 | 30,416 |
| Sum of captured call durations | 97.2 s | 53.6 s |

The updated arm used 33% fewer reported total tokens in this sample; it did not
inflate answer output. Single calls cannot establish a stable cost or latency
advantage, and total tokens are not a dollar-price calculation. The six-call
experiment used 75,786 reported tokens.

Sources are preserved official 2025 CFR snapshots: full
[1904.1](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol5/xml/CFR-2025-title29-vol5-sec1904-1.xml)
and a contiguous [1910.119](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol5/xml/CFR-2025-title29-vol5-sec1910-119.xml)
excerpt through employee participation. The drafts were deliberately constructed,
including already identified exemptions. This tests connecting existing meanings,
not whether a new extraction finds those meanings. Both new sources are OSHA
regulations; one sample per arm per section does not establish cross-domain
reliability. They are now development cases, not untouched evaluation material.

Raw outputs were shuffled and arm labels hidden for the manual review, with its
findings saved before revealing the mapping. Blinding was partial: behavior made
arms inferable, and the same agent built and judged the fixtures. Labels are
revisable engineering judgments, not authoritative legal determinations.

## Decision and remaining work

Keep the small local exemption-link implementation; do not add more prompt patches
or turn the previously unsuccessful extra audit pass on by default. No production
files changed during this experiment. The previous implementation remains
uncommitted.

The next useful evaluation would start from fresh **model-extracted** rulebooks
from another document family and run the existing proposal/challenge/review path
in isolated workspaces. Freeze expected targets before relationship calls, include
missing exemptions as well as already captured ones, and measure whether final
consumer-visible meaning is complete. That distinguishes this observed linking
gain from the still-unproven end-to-end user benefit. This evaluation is not run.

Artifacts: [frozen plan](PLAN.md), [raw manual review](BLIND-REVIEW.md),
[counts, refusals, previews and usage](assessment.json),
[replay result](replay-checks.json). `cells/` retains every request and response;
`sources/`, `inputs/` and `frozen/` preserve the source, drafts and runtime.

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-exemption-link-transfer/experiment.py replay
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-exemption-link-transfer/assess.py
```
