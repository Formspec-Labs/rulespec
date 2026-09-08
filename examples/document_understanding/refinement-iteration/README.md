# Recorded extraction refinement

Rulespec can now turn source findings into recorded corrections: recover missing
meaning, connect qualifications, and check the resulting rulebook. The measured
final process passes **25 of 29 saved cases**, up from **17**, while preserving
all original passes. It recovers the confidential-name exception, both qualified
rewrite statements, definitions, weaker guidance and several photo relationships.

The new command is `rulespec-understand refine`. It starts from the current
review snapshot, so prior corrections and decisions remain part of the input.
Each accepted addition or edit appends an `aiAgent` review event through the
existing `ReviewStore`. Original source, raw extraction, proposed corrections,
refusals, before/after states and final checks remain separately inspectable.

The [case-by-case assessment](assessment/RESULTS.md) is the main result. The
[approved plan](../../../thoughts/plans/2026-09-07-extraction-quality-refinement.md)
sets the bounds; the [execution record](../../../thoughts/plans/2026-09-07-refinement-execution.md)
records decisions and verification.

## What goes in and comes out

```text
current extraction + prior review history
    -> source-only inventory and draft comparison
    -> recovery proposals -> source challenge -> recorded additions/edits
    -> qualification proposals -> source challenge -> recorded additions/edits
    -> final source audit + before/after comparison + usage
```

The process reuses `document-understanding/2`, existing Core evidence and assertion
records, scope/context bindings, target resolution and review history. No new Core
schema or platform dependency is required. Models select meaning and targets;
deterministic code checks exact evidence, converts records and preserves history.
Core validity and a model's agreement are separate from the source adjudication.

Each focus group allows at most eight proposals and 60 current claims. Recovery
and relationships each run once, followed by a final audit. Unknown or refused
work remains visible. A complete processing status does not establish complete
meaning; records remain drafts and do not receive automatic approval.

## Results and effort

| Measurement | Initial | Refined | Practical result |
| --- | --- | --- | --- |
| 29 saved automatic cases | 17 pass | 25 pass | Eight failures closed, including the two required name cases; all original passes retained |
| Three fresh CFR passages, 20 expected meanings | 16 pass | 20 pass | Slope meanings unchanged; authorization prerequisite linked; four marketing meanings recovered |
| Two deliberate defects | Both detected | Both still have a defect | Detection works; full repair is not reliable |
| Three original correction actions | Preserved | Replay verified | Earlier history and neighboring duties survive |

The fresh expectations were frozen before extraction. The initial marketing
response reached its output limit and produced no usable candidates; refinement
recovered it. This is success of the combined process, not improved initial
extraction. The fresh result still has component-level issues, including an
awkward object field and noncontiguous `logic_text`; it is not ready-made workflow
logic. [Full fresh-source assessment](assessment/fresh-cases.json).

Both measured implementation revisions score 25 on the saved cases, but recover
different content. The final revision gains the confidential-name and disability
links while declining certificate guidance that the first revision recovered.
The final four failures are the infant exception link, the certificate caution
and advisory coverage (two overlapping cases), and an ambiguous damage-category
list. [All applied changes and limitations](assessment/applied-changes.json).

The two negative controls expose specific remaining process weaknesses:

- The missing document option is detected and a complete repair is proposed, but
  the source challenge refuses it because the proposal also fills an unsupported
  actor. The useful part is not salvaged in this bounded iteration.
- The wrong exception target is detected and corrected, but later edits change
  the target revision. The review store requires reconfirmation. A duplicate
  guard incorrectly prevents the same meaning from reconfirming the new target.
  That guard is now fixed and regression-tested. The recorded provider experiment
  remains a failed repair; no unperformed rerun is counted as success.

The source checker also makes incorrect judgments: it can confuse a broad
governing condition with replacement of a child's narrower scope, or demand
permissive modality on an exception that correctly uses `not_stated`. These
findings are kept alongside the source adjudication. [Control records](assessment/controls.json).

For the same three baseline sources, total recorded refinement tokens fell from
**2,055,895 to 1,026,905** (50.1%), with input tokens down 60.5%. Both revisions
made 37 requests, including initial and final audits. The final samples took
about 3.7, 5.1 and 6.6 minutes each, running concurrently. Removing opaque hashes
and repeated proposal fields reduced input size while preserving all meaning,
source quotations, positions and citations. [Usage and timing](assessment/processing-cost.json).

The nested proposal schema required one provider-specific adjustment. Controlled
probes accepted the identical shape after removing the outer `maxItems: 8`
keyword; the local parser still enforces eight proposals. Required fields, enums,
descriptions and all semantic/evidence fields remain. [Probe evidence](schema-probes/results.json).

This completes the two measured revisions. The improvement warrants trying the
records in a small discovery use case. Further extraction work should target
weaker-guidance recovery, local qualification discovery, and smaller independent
corrections before expanding document size. The current full audit/refinement
sequence is too expensive and inconsistent to assume it should run on every
document by default. No further model sweep or UI work is part of this delivery.

## Reproduce and inspect

The saved data can be read without credentials. Start with
[names-excerpts before](runs-02/names-excerpts/before.json),
[after](runs-02/names-excerpts/after.json), and
[applied actions](runs-02/names-excerpts/changes.json).

```sh
# Operates on a review workspace and appends its correction history.
.tools/document-poc-venv/bin/rulespec-understand refine my-run \
  --env-file /path/to/local.env --output my-refinement

# Exact replay uses the same recorded runtime; it makes no provider calls.
.tools/document-poc-venv/bin/rulespec-understand refine-replay my-refinement \
  --output my-refinement-replay
```

The experiment helpers retain source preparation, frozen expectations, isolated
workspaces and authored assessment. `run_sample.py` and `run_control.py` make
provider calls using the explicitly selected local credential file; `adjudicate.py`
materializes the source judgments and makes none. Re-running an experiment needs
a new output/workspace; existing captures are refused.

Strict replay intentionally refuses changed code or dependencies. The final
duplicate-guard fix postdates the live captures. `verify_delivery.py` uses each
capture's verified frozen application for replay, and separately checks legacy
reprocessing and the final built wheel. Run it only on these trusted local
captures. Its output directory must be new.

## Verification and artifacts

- [Runtime verification](runtime-verification.json): 11 extraction captures,
  13 refinement replays and 26 audit replays, with zero provider calls.
- [History verification](history-verification.json): three original correction
  actions, retained graph nodes, current targets and identical reopened state.
- [Tests](test-verification.json) and [test output](test-output.txt): package and
  projection suites: **236 tests and 101 subtests pass**, including exact evidence, stale audits, prior history,
  unsupported proposals, partial failures, replay tampering and link reconfirmation.
- A built wheel imports the refinement workflow and compiles/validates records
  with packaged Core data. All **4,371** protected original files remain unchanged.

`runs-01/` and `runs-02/` hold the two measured revisions. `slice-01/` preserves
the failed schema attempt and `slice-02/` the first successful recovery slice.
`fresh-source/` holds native XML, prepared passages and expectations frozen before
extraction. `controls/` holds deliberate-defect experiments. `assessment/` holds
Codex-authored reference decisions with source and capture hashes.

These are historical source samples and agent-authored project references, not
current legal advice, human accuracy measurements or proof of semantic closure.
All work remains local and uncommitted.
