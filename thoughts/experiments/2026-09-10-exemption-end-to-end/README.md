# The full workflow preserved meaning and added seven correct links

**Bounded success, with a substantial cost tradeoff.** Two fresh model-extracted
transportation sections completed extraction → audit → recovery → relationships →
challenge → review edits → final audit. Seven correct qualification links survived
all stages and offline replay. The cheap initial extraction already preserved the
expected meanings; refinement improved explicit relationships, not statement accuracy.

| Result | Alcohol, 49 CFR 392.5 | Railroad crossings, 49 CFR 392.10 |
| --- | ---: | ---: |
| Initial → final records | 13 → 15 | 15 → 15 |
| Initial → final explicit qualification links | 0 → 2 | 0 → 5 |
| Applied relationship changes | 2 companion exceptions added | 5 existing exemptions linked |
| Original statements/meaning/evidence changed | 0 | 0 |
| Wrong targets observed | 0 | 0 |
| Provider calls | 8 | 8 |

All eight frozen source scenarios remain represented: the two alcohol-possession
exclusions, the review-dependent State reporting deadline, and the five no-stop
cases. The review-dependent deadline stays in a complete grouped statement; it
does not need an additional record to pass the stated semantic criterion.

The possession exceptions target only the possession prohibition, not the driver's
alcohol-use prohibitions. The railroad exemptions target the grouped stop/listen/look
rule, with wording limiting the effect to stopping. None targets the no-gear-change
prohibition or Exempt-sign consent requirement. An edge to a grouped rule still
requires reading the modifier; it is not executable cancellation of every component.

## What this establishes

The railroad case exercises the new capability on actual extracted records:
five `exemption`/`not_required` records gain `exception` links through ordinary
edit proposals, source challenge and review revisions. Their logical identities,
statements, every other meaning field and source evidence stay unchanged. No
duplicate exemption record is created. The alcohol case exercises the existing
companion-exception addition path; its extraction grouped exceptions into a complete
prohibition, so it does not directly test exemption edits.

Both recovery passes returned no proposals. Both relationship passes produced
correct proposals, and every challenge supported them. No proposal, challenge or
application failed; one alcohol observation records the already represented deadline.
Both extraction and refinement runs report complete. This does not measure whether
challenge would reject an incorrect proposal—none arose in these samples.

Offline replay verified both original extractions and both full refinement runs,
including source packets, requests, decoding, challenges, actions and review history.
Independent deterministic checks verified original meaning/evidence preservation,
review reload, discovery export, and Core relationship assertions with qualifying
evidence bindings. All records remain pending review, not human-approved.

## Cost and practical value

| Reported total tokens | Alcohol | Railroad | Combined |
| --- | ---: | ---: | ---: |
| Extraction alone | 5,577 | 6,563 | 12,140 |
| Additional full refinement workflow | 106,389 | 127,154 | 233,543 |
| Complete workflow | 111,966 | 133,717 | 245,683 |

The complete path used **20.2 times** the reported tokens of extraction alone and
finished its 16 calls in 226 seconds. This is a token comparison, not a dollar
estimate; input, answer and thinking tokens may have different prices. Missing
thinking-token fields in extraction responses are not interpreted as zero thinking.
All requests and responses were retained; no retries or unreported selections.

The full path includes two audits (each an inventory and comparison), recovery,
relationship generation and challenge. The earlier cheaper isolated linking result
does not imply that this entire workflow is cheap. No repeat samples were run, so
neither latency nor token ratios are a stable population estimate.

## Remaining friction observed manually

1. **Repeated inherited evidence.** Railroad exemption ranges are `F025:F026`,
   `F025:F027`, through `F025:F030`: each starts at the shared no-stop header and
   absorbs all earlier siblings. The five main quotes total 2,541 characters while
   their union is 856 characters. Each also repeats the full paragraph (a) context.
   Passage IDs keep extraction output compact, but downstream expanded quotes and
   repeated context enlarge proposal/challenge packets. This is visible upstream
   of refinement; the link-only edits correctly preserve it rather than silently
   rewriting evidence. Narrow child evidence plus explicit parent evidence, or
   reusing the already tested overlap compaction in packet construction, merits a
   separate controlled test.
2. **Actor/modality evidence warnings.** Alcohol starts with 13 unresolved component
   warnings and ends with 15 because the two additions each introduce another
   ambiguous `driver` quote. Railroad retains one warning. Readable meanings are
   correct, but structured evidence is not fully resolved. A passage-aware locator
   deserves attention before another broad prompt patch.
3. **References remain unresolved.** Seven alcohol and eight railroad reference
   warnings persist, including local paragraph references. Explicit exemption edges
   do not resolve every source citation or vehicle-scope relationship.
4. **Audit scores are not an accuracy benchmark.** Both initial and final audits
   report all reviewed units covered. The alcohol inventory changes from 13 to 16
   expected units on the same source; those percentages do not measure improvement
   against a fixed denominator. The frozen manual scenarios—not the model's own
   all-correct ratings—support the outcome reported here.

## Decision

The prespecified semantic/link-survival gate passes on these two selected sections.
Keep the small exemption-link capability and preserve cheap extraction as the
normal discovery path. Use the larger workflow selectively when explicit graph
relationships justify its cost. No production configuration or code was changed
in this experiment, and no automatic extra pass was enabled.

Stop tuning these documents. The next high-value experiment is reducing duplicated
evidence in saved packets while preserving child/parent source identity and all
qualifications. Reuse existing passage IDs, evidence structures and the prior
overlap-compaction work. Separately retain this full-path run as a regression case.
Neither task is implemented here. Current implementation/research remain uncommitted.

The full official 2025 source snapshots are preserved:
[49 CFR 392.5](https://www.govinfo.gov/content/pkg/CFR-2025-title49-vol5/xml/CFR-2025-title49-vol5-sec392-5.xml)
and [49 CFR 392.10](https://www.govinfo.gov/content/pkg/CFR-2025-title49-vol5/xml/CFR-2025-title49-vol5-sec392-10.xml).
These are now development cases. Two adjacent regulatory sections, one sample each,
same-provider challenges, and same-agent source judgments cannot establish general
reliability. Before/after reading order was randomized with labels hidden, but added
edges made timing partly inferable. The comparison tests the current workflow as a
bundle, not the isolated causal effect of the exemption patch. No source with an
actually omitted exemption happened to arise, so recovery of missing exemptions
remains untested here.

Evidence: [frozen plan](PLAN.md), [alcohol manual review](reading/alcohol/REVIEW.md),
[railroad manual review](reading/rail-crossings/REVIEW.md),
[verification and usage](verification.json), [replay checks](replay-checks.json).
`cases/` retains all raw inputs/outputs, audits, proposals, challenges, review history
and final discovery exports. Original extraction artifacts remain immutable.
