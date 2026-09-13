# Composed quoted judgments: no measured detection improvement

The requested representation is implemented in this experiment: each judgment
is one composed question containing quoted source, statement, actor, force,
classification, scope and supporting text. Support IDs expand into quotations;
source and proposed terms repeat within each question. Production is unchanged.

Four fresh calls assessed the same 21 fixed items in both formats. All 42
decisions parsed, all calls ended with STOP, and actual requests and offline
replay matched. The predeclared gate for broader evaluation failed.

| Measure | A: shared source | B: composed quotations |
|---|---:|---:|
| Clear omissions detected | 0/3 | 0/3 |
| False alarms on faithful controls | 0/17 | 0/17 |
| Previously uncertain items flagged | 0/1 | 1/1 |
| Input tokens | 6,962 | 37,702 |
| Output tokens | 166 | 153 |
| Total tokens | 7,128 | 37,855 |

The experiment used 44,983 reported tokens and 5.86 seconds across four calls.
Repeating the full supplied text increased input tokens 5.42 times. No retries.

## Raw review

I read every verdict and compared the three known omissions and the only negative
explanation to their fixed statements and source. Original labels remain intact.

- IEP R000 still omits “including courses of study” from F025. Both arms approve
  the definition despite receiving that source wording.
- IEP R004 still lacks the requirement that the parent's agreement be in writing.
  B quotes the attendance rule F046 and the written-agreement rule F053 inside
  that same question. It nevertheless approves the item.
- IEP R005 similarly lacks written parental consent. The member's written input
  is a distinct requirement and does not satisfy the parental-consent condition.
  Both arms approve it.
- B rejects R006 because it identifies “parent” as the actor, arguing for an
  absent actor or the agreement/consent itself instead. This is a questionable
  objection: it conflates the grammatical subject with the responsible party,
  and calling the source passive voice does not establish a semantic defect.
  The original uncertainty concerned unresolved clause references. This flag
  does not demonstrate detection of that concern or any of the three omissions.
- Both arms approve the 13 previously faithful LEA requirements, including their
  conditional and optional provisions. This is a useful control, not evidence
  of general accuracy.

Exact composed requests: [IEP](prompts/cell-00.txt) and
[LEA](prompts/cell-01.txt). Shared-source controls are cell-02 and cell-03.
Every raw SDK request/response and plaintext answer is under `captures/`.
`assessment.json` retains individual decisions, labels, counts and checks.

## Interpretation and stopping point

Moving the complete supplied source into every question did not fix these
omissions. This weakens the explanation that shared-source placement alone
caused the failures. It does not establish why the model approved the items.
The result is consistent with checking whether a statement is locally supported
without adequately checking whether it is independently complete.

This deliberately tests composition plus repetition. It does not isolate prose
style from repetition, nor test a concise narrative containing only the governing
snippets. Full-source repetition may itself make the relevant relationship harder
to distinguish. A focused-quotation comparison remains untested; do not report
this result as rejecting that approach. Existing context selection needs its
own verification before claiming it found all governing text.

These are repeatedly examined development cases, one call per format/document,
with revisable labels. No general accuracy rate follows. Stop this format
iteration at the declared bound; no production confidence feature or new prompt
patch follows from this result.

## Reproduce without more provider calls

The exact run script, fixed inputs, runtime source hashes, labels and prompts
were pinned before capture in `precall-pins.json`. `verification` within
`assessment.json` records actual request equality and replay with provider
creation blocked. The saved experiment imports the preceding narrative renderer
for its control and reuses Rulespec passage resolution and request capture.

Before the pins and any calls, preparation encountered a missing local JSON
helper. The empty generated cells file was removed and the helper fixed. The
resolver's dict return was also corrected before the requests were generated.
No provider observations were discarded or replaced.
