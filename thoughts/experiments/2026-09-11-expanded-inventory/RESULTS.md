# Broader inventory helps selected scope links; the overall problem remains

**Decision: do not adopt this as a default audit pass.** The preregistered gate
failed. Expanded inventory still did not catch the saved equipment override or
the new simulator-permission defect. It did attach the PPE applicability limit
and support nine correct findings, but that case's baseline comparison request
failed, so a controlled downstream improvement cannot be claimed.

Verdicts: **bounded inventory improvement**, **not solved overall**, and
**unresolved comparison benefit for PPE**. Production behavior and original
extractions/reviews remain unchanged. The compound-evidence adapter exists only
in this experiment; it has not fixed production audit.

## Comparison and results

A inventoried the first ordinary 3,000-character window and its ordinary context.
B inventoried the complete source assembled by `context-export`. Both comparisons
received the same expanded source and complete fixed rulebook. This isolated the
inventory change within a common experimental comparison setup; it was not a
byte-identical test of the ordinary window-based audit CLI.

We reused the previous comparison adapter and current capture, CUE schemas,
source resolver, Core compiler and evaluation code. The actual requests confirm
Gemini `gemini-3.8-flash`, temperature 0, low-thinking extraction and medium-thinking
inventory/comparison, 32,768 output allowance and no thinking budget. There were
two new untouched provider extractions and one exact saved development failure.

| Case and prelabelled outcome | A: ordinary inventory | B: expanded inventory | Decision |
| --- | --- | --- | --- |
| Equipment: (e)'s special-flight-permit effect on C0000 | No (e) inventory unit; comparison misses the defect despite full source and C0013 being supplied | Inventories (e) separately; still misses its effect on C0000 | E1 not solved |
| New flight review: C0010 grants simulator permission with only the approved-course condition | No simulator inventory units; comparison approves C0010 | Inventories all three conditions separately; comparison still approves the incomplete permission | F1 not solved; neither missing condition caught |
| New PPE: (g) restricts the (d)/(f) duties | Inventory lacks (g); comparison request fails with no saved response | Inventory connects (g) to relevant units; comparison correctly flags all nine prelabelled affected statements | Useful inventory result and supported findings; comparative downstream effect unresolved |
| New PPE: another standard's payment provisions take precedence | Comparison unavailable | Inventories precedence separately, but approves C0015 without its effect | P2 not solved in available comparison |

The nine PPE findings are nine affected statements sharing **one governing
limitation**, not nine independent successful cases. The new sources are selected
diagnostic sections, now development data. There was one observation per arm and
no estimate of general accuracy.

## What the raw outputs show

### Recognition is not attachment

Expanded equipment inventory U0023 says an aircraft may operate under a special
flight permit notwithstanding the other provisions. Its U0000 still describes
the opening prohibition with only the (d) exception. The comparison approves each
separately and cites only the opening passage for C0000.

The new simulator case is more revealing. C0010 says a simulator/device **may be
used**, provided it is used in an approved course at a certificated training
center. The source also requires the landing-recency condition, with its stated
exception, and a device representing aircraft for which the pilot is rated.
Expanded inventory U0016-U0018 records those three conditions separately. The
comparison treats C0010 as a statement of the first condition and approves it,
without checking whether that condition alone justifies the permission.

This is consistent with an attachment/necessary-versus-sufficient-condition
failure (H2), not simply unavailable source or a missing passage identifier.
It does not prove the model's hidden reasoning or that a particular future
representation will fix the problem.

### Explicit source associations can help

For PPE, expanded inventory U0003 explicitly restricts workplace assessment to
the sections listed in (g), and U0010 does the same for training. Several other
units attach the (g) passage as scope evidence, though their own wording does not
always repeat the complete applicability restriction.

The comparison then identifies the precise omission in C0003-C0006, C0008 and
C0010-C0013. It preserves the independent provision/maintenance, safe-design and
damaged-equipment rules and does not apply (g) to payments. It also preserves the
off-job-site-wear requirement and the distinction between intentional and
accidental damage. These are useful counterexample results in the available arm.

That same inventory leaves the final payment-precedence note separate from the
general payment requirement, and the checker misses that omission. This explains
why the result is narrower than "expanded inventory works."

No confirmed false qualification attachment appeared in the five completed
comparisons. One PPE rationale calls excluded sections "respiratory and electrical
PPE" without supplying their titles; the section-number finding is grounded, but
that explanatory gloss is not established by the supplied passage. The missing
PPE baseline means comparative false-alarm/regression behavior remains unresolved
for that pair. Prelabelled ambiguity about flight-review content exemptions and
some modality classifications remains ambiguity, not a manufactured error.

## Mechanical validity and failures

- 14 attempted calls: 2 extractions, 6 inventories, 6 comparisons. Thirteen
  responses, one request failure, zero retries. The failure has
  `provider_request_failed` and no recorded response or diagnostic detail;
  its underlying cause and billing are unknown.
- Both new extractions retained all their candidate statements: 13 flight-review
  statements and 26 PPE statements, with zero rejected rows. PPE also produced
  12 term-component refusals: its definition was attached to a requirement,
  so the existing parser withheld that term and its references. The original
  statements and refusals were preserved and shared across arms.
- Five comparisons produced 80 claim judgments, 98 inventory-unit judgments and
  325 grounded source-reference selections. There were no schema, source-mapping
  or reciprocal-link issues in those five. The failed comparison has its request
  failure plus the consequent missing-wrapper issue, not usable semantic results.
- Ordinary audit's inserted-text rejection would affect one unique PPE inventory
  span in A and two unique inventory/judgment spans in B. The shared experimental
  adapter retained their original evidence pieces. Deterministic counterexamples
  confirm that inserted substantive words are still refused.
- All six inventory/comparison processing outcomes, including the failed request,
  replay identically without model calls. Both fresh extractions also replay with
  identical raw parsing, graph compilation and validation.
- Actual comparison prompts/source/claims are identical within each pair except
  the inventory. Frozen pre-audit inputs and runtime copies match their hashes.
- All semantic outputs were reviewed in randomized anonymous order before opening
  the saved arm key. The larger inventory can reveal the likely arm, so masking
  is imperfect. The review was hashed before unmasking; its labels remain revisable.

The initial context-freeze assertion failure is retained in PLAN.md: ordinary
catalogs can skip whitespace-only alias numbers, while context export renumbers
them. The harness now checks actual source spans/text and resolves each request's
own IDs. This change occurred before all inventory/comparison calls, preserved
the original extraction captures, and did not change the semantic criteria.

## Cost and bounds

Recorded usage was **214,813 tokens** across the experiment: 17,117 extraction,
37,215 inventory and 160,481 comparison. The failed request has no usage receipt,
so this is recorded usage, not a complete billing statement. Capture/extraction
operations took about four minutes in total; manual preparation/review time is
not included in that timing.

| Completed pair, inventory plus comparison | A tokens | B tokens |
| --- | ---: | ---: |
| Equipment | 26,421 | 35,315 |
| Flight review | 37,680 | 34,679 |
| Both complete pairs | 64,101 | 69,994 |

B used 1.09× total tokens on the two completed pairs, with no target-defect gain
there. Costs moved in opposite directions because reported thinking varied. The
PPE B inventory/comparison used 59,147 tokens; A only reports its 4,454 inventory
tokens. Do not compare that incomplete pair as a cost ratio. One observation per
case cannot establish a stable relative cost.

## Lesson and next decision

We now have distinct evidence for **missing qualification discovery** versus
**missing qualification attachment**. Increasing inventory breadth can recover
the source passage and sometimes associate it with the right rule. It does not
reliably preserve the effect of an override or the complete conditions of a
permission.

Stop this experiment at its bound. Keep the existing deterministic context export.
Do not add a general expanded-inventory default or repair these saved outputs.
The next useful process question is whether an explicit source-backed association
between a qualification and its affected rule preserves the relation's effect:
exception, prerequisite, limited exemption or precedence. A permission must be
checked against all necessary conditions jointly; matching it to one condition
does not establish sufficiency. Start with existing Rulespec qualification and
evidence structures rather than another summary field or generic prompt patch.
That recommendation is untested and requires its own decision and bounded test.

The production compound-evidence inconsistency remains a separate small repair.
This experiment demonstrates why the shared evidence path is useful, but does
not itself implement or authorize adoption of either change.

Receipts: [PLAN](PLAN.md), [prelabels](PRELABELS.md), [anonymous review](BLIND-REVIEW.md),
[summary](summary.json), [mechanics](mechanical-results.json),
[input checks](input-checks.json), [comparison replay](replay.json),
[extraction replay](extraction-replay.json), [usage](usage.json).
Raw requests and outputs are in `extract/`, `inventory/`, and `comparison/`.

Replay this experiment's saved inventory/comparison processing:

```sh
.tools/document-poc-venv/bin/python thoughts/experiments/2026-09-11-expanded-inventory/run.py replay
```
