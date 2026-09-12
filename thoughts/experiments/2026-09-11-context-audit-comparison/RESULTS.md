# Expanded context did not earn an automatic audit pass

**Decision: defer integration.** Supplying the existing context export to the
comparison stage produced no confirmed additional defect finding on the two
fresh sources. Both arms missed the equipment statement's overriding exception
and failed to identify the saved unsupported adulthood restriction. The gate in
[PLAN.md](PLAN.md) failed. No extraction, audit default, statement or review was
changed. The deterministic context export remains available and was committed
separately as `6942225`.

## What happened

Two complete 2025 annual CFR sections received one normal low-thinking extraction
each: 14 CFR 91.213 produced 14 accepted statements; 40 CFR 262.11 produced 23.
No candidates were rejected. We compared the first ordinary audit window from each
plus the saved labeling failure and two constructed companion controls. Each pair
shared the exact draft and one source-only inventory. A received ordinary context;
B received the existing context export. Both used the current comparison prompt,
medium thinking, temperature 0 and 32,768 output allowance without a thinking budget.

| Case | Ordinary context A | Expanded context B | Assessment |
| --- | --- | --- | --- |
| Fresh equipment rules, 10 claims | Passes all claims; misses the overriding special-flight-permit exception in C0000 | Same | No improvement; missing exception survives even with its source supplied |
| Fresh waste rules, 6 claims | Passes all claims | Flags delisting permission for missing nonexclusion/generator context | Interpretation uncertainty, not an established gain; relevant lead-ins were already in both requests |
| Saved labeling claim | Flags missing (B)(4) exception | Same finding | Existing audit already finds this narrow defect; neither explains the broader use-condition issue |
| Saved adulthood answer, constructed claim | Flags general support/format/scope issues; does not challenge age | Same failure to challenge age | Required specific defect not found in either arm |
| Faithful companion statement, constructed control | Demands extra furnishing/scope language | Accepts the statement's summary and scope | One control false alarm avoided; both also flag the compiler-default uncertain modality |

The raw review was written with anonymous randomized output files before the
arm key was opened. See [BLIND-REVIEW.md](BLIND-REVIEW.md), its hash receipt, and
`arm-key.json`. All claim and inventory-unit rationales were inspected, including
successful verdicts, not just rows marked error. Labels remain revisable.

### Concrete failures

The equipment draft says no person may take off with inoperative equipment unless
(a)(1)-(a)(5) are met, except under (d). Later (e) allows operation under a special
flight permit notwithstanding the other provisions. Both auditors approved the
opening claim without discussing (e). The extraction did capture (e) separately
as C0013 outside the selected window, so this is a standalone-meaning omission,
not a claim that the whole extraction lost the exception.

The constructed saved answer says the child must be accompanied by an
“authorized adult.” The source says parent, guardian or a designated attendant;
“adult” belongs to the separate lap-held-infant option. Both audit rationales
repeat or accept the adult wording while complaining about other aspects of the
answer. An error verdict is not evidence that the important error was detected.

The expanded waste audit says the source excludes petitions by non-generators or
for already-excluded waste. The paragraph supports a generator's determination
sequence, but those broader limits on petition rights are not established by the
supplied source alone. The referenced petition provisions were unavailable. The
prelabels already treated inherited nonexclusion scope here as uncertain; we did
not upgrade this new allegation to a beneficial finding after seeing it.

## Mechanical checks and usage

All 16 planned calls completed: 2 extractions, 4 inventories and 10 comparisons.
No retries. The comparisons returned all 38 expected claim judgments and 46 unit
judgments. All 138 source-reference selections grounded, C/U links were reciprocal,
and there were no provider/schema/mapping issues. Ten comparison captures replay
identically with zero model calls. Actual request settings, identical pair inputs,
source/installed application bytes and frozen input hashes were checked.

The evaluation reports still expose unreviewed statements elsewhere in the full
books. A complete focus comparison does not establish a complete document audit;
`semantic_completeness` remains `not_established`.

| Comparison usage | A | B |
| --- | ---: | ---: |
| Input tokens | 27,694 | 41,648 |
| Answer tokens | 7,391 | 7,777 |
| Reported thinking tokens | 5,961 | 29,649 |
| Total reported tokens | 41,046 | 79,074 |

B used **1.93× total comparison tokens**. Most extra thinking came from the one
waste comparison (24,058 thinking tokens); one observation cannot establish a
stable cost ratio. Shared extraction/inventory used another 30,643 tokens, for
150,763 across the experiment. These are recorded tokens, not a billed-dollar
estimate. The prior experiment's failed 2× gate remains unchanged; this experiment
used its own preregistered semantic gate.

## Limits and next decision

This tests expanded evidence in the comparison stage, with the inventory held
fixed. It does not test expanded source inventory or discovery of completely
missing rules outside that inventory. A uses a common source-qualified encoding
and full draft fields rather than the normal CLI's compact quote encoding; it is
not a byte-identical CLI control. No external target body is supplied in this test.

The two fresh sections are selected diagnostic cases, now development data.
There is one observation per arm, no estimate of general extraction accuracy, and
no whole-document audit. The two constructed companion records inherited
`modality=uncertain` from the compiler, creating a classification distraction.
The original saved answer and raw captures remain intact; neither was repaired or
rerun to obtain a cleaner result.

The responses are consistent with a checker that follows the shared inventory
and local wording more closely than it searches for contradictory context. That
is an inference from outputs, not a claim about internal reasoning. Additional
context was demonstrably available; reliable use of it remains unproven.

Stop this comparison here. Keep the useful deterministic source integration.
Before another model experiment, choose a distinct process question: whether
source-first inventory over the assembled context can identify qualifications
before matching them to claims, with independent evaluation of both stages on a
broader frozen set. Do not add another generic instruction or automatically apply
these uncertain audit findings. Corrections under R25 remain separate.

The annual-CFR format question has a concrete, independent answer: **support it
in RefSpec's existing XML reader.** The native reader currently rejects these
GovInfo annual roots. This test reused an installed DocSpec reader solely for
acquisition, preserving XML and byte-map artifacts; production gained no new
DocSpec dependency. [SOURCE-PREPARATION.md](SOURCE-PREPARATION.md) records the gap,
acceptance scope and R23 follow-up. The frozen text replays identically, and every
original section paragraph survived whitespace-insensitive comparison (28/28 and
12/12). Those checks do not establish native annual-reader support.

Reproduce the saved comparison processing without calls:

```sh
.tools/document-poc-venv/bin/python thoughts/experiments/2026-09-11-context-audit-comparison/run.py replay
```

Receipts: `checks.json`, `replay.json`, `usage.json`, `preparation-checks.json`,
`source-replay.json`, `precall-pins.json`, `runtime-sha256.json`. Raw requests and
responses live in `extract/`, `inventory/` and `comparison/`.
