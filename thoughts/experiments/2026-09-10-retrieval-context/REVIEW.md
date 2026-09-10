# Result: context helps locally; complete meaning remains unsolved

Compared frozen claims with their main evidence and existing discovery packets.
No provider calls, no production changes. This evaluates available returned
material, not search ranking, downstream answer accuracy, or new extraction.

## Manual assessment

| Case | Statement A | Main evidence B | Packets C |
| --- | --- | --- | --- |
| Posts duty | Local-modification permission missing | Permission explicit in the same source sentence | Same recovery as B, with repetition |
| Pilot takeoff duty | Administrator authorization retained; remote part 121/125/135 exclusions missing | Remote exclusions still missing | Remote exclusions still missing; also includes movement, seating and passenger-alternative material |
| Recording checkbox, non-adopted sentence extraction | Work-related/beyond-first-aid prerequisite missing from default wording | Same incomplete sentence | Governing question and work-related/beyond-first-aid sentence recovered in paragraph |
| First-aid supplies | Supplies duty explicit; disputed inherited scope not explained | Neighboring training condition visible | Same material as B; no basis to force shared applicability |
| Constructed separate exemptions | Visitor/public-tour pair explicit | Librarian/archive pair also visible and distinct | Same distinctions; repeated paragraph |
| Constructed AND duty | Sign AND date before submission preserved; AR not expanded | Same conjunction and timing | Same conjunction and timing; finance definition still absent from these views |

The AND claim's saved term link is outside the tested text views. Its absent
expansion is a dereferencing gap in these views, not evidence the extractor chose
the wrong sense. Likewise, adding both exemptions as context does not assert that
the visitor inherits the librarian's exemption. No links or claims were mutated.

On the three intended loss targets, required source meaning is explicit in 0/3
default statements, recovered in 1/3 main-evidence views and 2/3 packet views.
These are hand-selected diagnostic counts, not accuracy rates. C has incremental
recovery over B in one case. None of the default statements changes. The broader
all-three recovery gate fails. Ambiguous applicability remains unresolved and
must not be counted as a corrected condition.

Verdict: **bounded context recovery, broader problem not solved**. H1 fits Posts;
H2 fits the recording checkbox; H3 fits remote seatbelt exclusions. These are
observed locations of missing meaning, not explanations of hidden model thinking.

## Noise and cost

| Case | A characters | B characters | C characters |
| --- | ---: | ---: | ---: |
| Passport | 48 | 240 | 434 |
| Seatbelts | 406 | 768 | 2771 |
| Recording | 304 | 610 | 1256 |
| First aid | 55 | 330 | 607 |
| Separate exemptions | 56 | 236 | 418 |
| AND duty | 92 | 183 | 276 |
| Total | 961 | 2367 | 5762 |

Counts include unchanged statement plus displayed source spans and separators.
These are characters, not provider tokens. New provider cost is zero. Summing
over these selected results makes C about six times A, without proving user harm
or establishing a universal overhead.

Exact-offset deduplication still shows the same paragraph twice when the passage
includes trailing whitespace and the quote ends before it. Other C outputs show
subspans alongside the paragraph containing them. In seatbelts, a shared context
passage links several claims; collecting all its evidence brings sibling duties
into this view. This is a property of our literal assembly from records(), not a
claim that every existing UI or consumer renders all of these spans.

## Next decision

1. A separate deterministic change could assemble source text from the union of
   overlapping intervals, preserving individual evidence IDs and roles. That can
   remove duplicate text without guessing semantic equivalence. Do not rewrite
   historical evidence or apply string-fuzzy deduplication to rule meanings.
2. Keep retrieval context claim-specific where possible; shared context nodes
   should not automatically import every sibling's evidence. Assess lost useful
   context if narrowing this behavior.
3. A fresh extraction experiment should target dependency selection across
   passages, including remote section exclusions and term definitions. Existing
   ApplicabilityScope, EvidenceBinding and term references provide storage; the
   model still needs to select the correct relationships. More local context
   alone cannot recover an unselected remote exclusion in this diagnostic.
4. For the Posts case, test whether a qualified default statement improves
   standalone use over its already faithful evidence. Do not credit packet
   expansion for a fix already available in main evidence.

Scenario-based auditing and a new complete-rule representation remain untested.
Do not infer their value from this experiment. No production adoption occurred.

## Reproduction and limitations

Run from repository root:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .venv/bin/python thoughts/experiments/2026-09-10-retrieval-context/experiment.py --output /tmp/rulespec-retrieval-context-new
```

The output directory must not exist. run-02/results.json records input and helper
hashes, source coordinates, full displayed text and repository revision. Saved
input paths point to immutable captures already tracked in this repository.
The separate replay/results.json and display.md match run-02 byte for byte.
Every displayed evidence span was checked against its document's exact slice.
Mechanical replay does not establish semantics. No unit suite or UI run was
needed for this isolated diagnostic; git diff --check passed.

Manual review read all six displayed comparisons against the saved source text.
Assessment was unblinded and is revisable. All documents are development data;
two controls are constructed. One target is from the rejected sentence-catalog
experiment, not current production extraction behavior.

setup-failure.txt retains the initial missing-import error. run-01 retains an
incorrectly selected recommendation claim and the original runner. PLAN.md
records the post-result correction to the intended checkbox failure. The initial
six-case protocol therefore had a selection deviation; run-02 is the corrected
comparison, not an independent replication or a hidden best-of selection.
