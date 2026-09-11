# Independent source review: bounded improvement

The captured grammar preserves the two fresh explicit ranges and one previously truncated compound part. Two existing hyphenated-section readings remain unchanged. A historical ambiguous reference now retains its complete source text with an explicit refusal. No new endpoint-loss or scope defect was observed in these six selected paragraphs.

This is a six-paragraph diagnostic review, not an accuracy estimate or an adoption gate. It does not check RefSpec consumers, the Rulespec adapter, installed wheels, target existence, or legal applicability. No fresh following-list-member case was selected; the root comparison must cover that boundary. No source case contains endpoint pinpoints.

## Frozen source judgments and results

The source cases and judgments were saved before any proposed-parser run in [source-cases.json](source-cases.json), SHA-256 `4bf0ced4eac341852515fb9e3fd2454053a9b50bcfd96797044083131970f98f`. These are revisable reviewer judgments, not legal gold. Each case retains the source file hash, manifest entry, publisher URL/date, exact paragraph XML, byte coordinates, surrounding raw XML, section tag, flattened text, and expected reading or refusal. All three source files matched the supplied manifest's hashes and sizes; none of these paragraphs is one of the eight prior whole-token specimens.

| Source paragraph | Predeclared reading | Frozen baseline | Captured current grammar |
| --- | --- | --- | --- |
| Title 2, section 182.610; `21 CFR 1308.11 through 1308.15` | Both written section endpoints | Stops at `1308.11` | Both endpoints, complete occurrence |
| Title 2, highest-level-owner definition; `48 CFR 52.204-17` | Single complete section, or explicit refusal if unsupported | Complete single | Same complete single |
| Title 29, service-contract procurement paragraph; `32 CFR 1-403` | Historical address unresolved; explicit refusal | Accepts only part `1` | Complete token with `ambiguous_hyphen` refusal |
| Title 29, Walsh-Healey overtime paragraph; `41 CFR part 50-201` | One compound part | Stops at part `50` | Complete part `50-201` |
| Title 47, section 0.458; `47 CFR 19.735-203` | Single complete section, or explicit refusal if unsupported | Complete single | Same complete single |
| Title 47, fee-collection paragraph; `47 CFR 1.1901 through 1.1952` | Both written section endpoints | Stops at `1.1901` | Both endpoints, complete occurrence |

The raw context matters. The FCC paragraph earlier names `§ 19.735-203(a) of this chapter`; that supports a single hyphenated section rather than a range to part 203. The historical title-32 reference appears after procurement case citations, and its paragraph does not establish a range of parts 1 through 403. That label remains uncertain; the current refusal preserves the uncertainty instead of resolving the historical address. The two `through` ranges have explicit endpoint sections and nearby unrelated statutory citations, which remained outside the CFR occurrences.

Five current readings are complete accepted references; one is a full-source refusal. The frozen baseline already preserved two singles but failed the other four declared checks. This establishes a bounded improvement over these cases, not general parser quality. Every saved occurrence's text equals its original source slice. The two unchanged singles are null controls; the baseline failures show that the same assessment catches endpoint and token loss.

## Consumer implication

The native occurrence for `32 CFR 1-403` contains `cfr_part="1-403"`, `part_is_plausible=true`, and `refusal="ambiguous_hyphen"`. This is a retained candidate reading with refusal, not an accepted target. A consumer that checks only `part_is_plausible` would erase that distinction. The root and consumer implementers were notified; no consumer behavior was tested here.

## Execution and limits

After the grammar owner declared `CfrCitationRange` ready, [compare.py](compare.py) captured the current grammar bytes into [grammar-snapshot.py](grammar-snapshot.py) and imported that snapshot. Its SHA-256 is `789b5d6b99d8b505331103ffd0352628532af8fb03fdce678eec67a72e9b3fac`. The live grammar file remained unchanged across the run. The baseline is the parent experiment's existing frozen `baseline.py`, SHA-256 `2999239dc9a99f5c21749686369ab2931abe336d1671101a3252115eef1c09a9`.

Executed once from RefSpec:

```sh
uv run python /Users/mikewolfd/Work/rulespec/thoughts/experiments/2026-09-11-cfr-ranges/fresh-review/compare.py
```

[observations.json](observations.json) retains both arms' native results, exact source spans, and per-case assessments. The scripts deliberately refuse to overwrite existing observations. No labels changed after output, no network or model calls were made, and no production files, policies, external tests, or commits were changed. Later grammar edits are outside this captured result.
