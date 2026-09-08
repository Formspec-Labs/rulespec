# Blind adversarial review: workflow, evaluation, and raw-response boundaries

**Verdict: REQUEST CHANGES.** An invalid numeric value in a model row can prevent the run from recording its failure and block normal review, replay, and reprocessing. Evaluation also marks a fully reviewed total omission as an incomplete review. Neither defect was covered by the 91 selected existing tests, all of which passed.

This is a bounded review of copied code and tests, not a semantic endorsement of the development labels or a full repository review. No fixes, external provider calls, network calls, or production source/result edits occurred.

## Findings

### W1 — Overflowing JSON numbers defeat terminal failure recording

**Severity: WARNING / P2. Category: correctness. Confidence: high; executed end to end offline.**

Primary location: [`extraction.py:215`](/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/code/repo/packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py:215), with the failing write at [`extraction.py:551`](/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/code/repo/packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py:551).

The JSON decoder rejects the literal `NaN` through `parse_constant`, but a valid JSON number such as `1e999` takes the float-decoding path and becomes Python `inf`. If this appears in an invalid candidate field, the schema rejection includes the entire decoded row in `refusal.raw` (`extraction.py:261–264`). The parser therefore returns a partial result containing a valid candidate and a refusal that cannot be serialized by `_save`, which uses `allow_nan=False` (`extraction.py:85–87`).

The decisive input contains one valid requirement row and a second row with `"actor":1e999`. `_finalize` saves `candidates.json`, then attempts to save `refusals.json` before entering its guarded compilation block (`extraction.py:549–561`). That write raises `ValueError: Out of range float values are not JSON compliant: inf`. The final status was updated only in memory immediately before `_finalize` (`extraction.py:652–658`), so the previously saved run still says it is running.

Observed on disk after `extract_run` returned by exception:

| Record | Actual state |
| --- | --- |
| `run.json` | `status: "running"`; no `finished_at` |
| Window record | `status: "partial"`; one candidate, one refusal, one attempt |
| Attempt record | `status: "response_received"`; no provider error |
| Raw request and response | Preserved |
| `candidates.json` | Preserved, including the valid row |
| `refusals.json`, `rulebook.json`, `graph.jsonld`, `validation.json`, `manifest.json` | Absent |

The follow-up probe confirms that `ReviewStore` rejects the run because `rulebook.json` is absent, while both `replay_run` and `reprocess_run` raise `FileNotFoundError` for `manifest.json`. Those operations leave the retained artifacts unchanged. Their entry points require these files at `review_store.py:102–107`, `extraction.py:673`, `extraction.py:926`, and `extraction.py:1010`.

**Why this is a defect despite review-only status:** the failure concerns acquisition and durable accounting before semantic approval. The code explicitly promises terminal outcomes and preserved refused rows. Invalid model content is an expected refusal case; it must not leave a successfully acquired run permanently recorded as running. The preserved raw response permits manual recovery, but none of the normal recovery entry points can use it.

**Test gap:** `test_malformed_responses_fail_explicitly` tests the literal `NaN` (`test_extraction.py:75–89`); `test_invalid_rows_do_not_hide_valid_rows_or_their_failure` tests malformed types and mixed valid/invalid rows (`test_extraction.py:100–108`). Neither tests a numeric overflow or whether refusal serialization itself can fail. The compilation-failure tests begin after the failing write and do not exercise this path.

**Suggested next step:** reject non-finite float results during decoding, or retain refused raw content in a representation the artifact writer can always serialize. Add an end-to-end regression that checks a terminal run status, retained valid rows and raw input, a saved failure record, and access through the normal recovery path.

Evidence: [probe code](workflows-probes.py), [concise overflow observations](workflows-overflow-observed.json), [recovery probe](workflows-recovery-probe.py), [recovery observations](workflows-recovery-observed.json). Full captures and frozen runtime inputs are retained under `.tools/blind-review-20260907/workflows-artifacts/workflows-runs/numeric-overflow/`.

### W2 — A completely reviewed total omission is reported as incomplete

**Severity: WARNING / P2. Category: evaluation accounting. Confidence: high; executed.**

Primary location: [`evaluation.py:261`](/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/code/repo/packages/rulespec-extrapolator/src/rulespec_extrapolator/evaluation.py:261).

For an output with no accepted claims, one expected source unit, and a fresh explicit judgment that the unit is missing, the evaluator reports:

```json
{
  "status": "failed",
  "review_complete": false,
  "unjudged_or_stale_claims": 0,
  "coverage": {"missing": 1, "unknown": 0},
  "issues": []
}
```

Every item requiring review has been judged. The `or not claims` term nevertheless sets `unfinished` to true, and `review_complete` negates that value (`evaluation.py:260–266`). This confuses extraction failure with unfinished review. By contrast, a fully reviewed omission when another claim remains can be complete.

**Counterargument:** the empty-output guard prevents vacuous success. That is useful before review, but the nonempty expected-unit check (`evaluation.py:87–89`), required coverage judgments, and explicit `missing` failure already prevent a pass here. This finding does **not** claim the evaluator incorrectly passes the extraction; `status: "failed"` is correct. The defect is the completeness flag and the resulting inability to represent a completed review of a total miss.

**Test gap:** `test_explicit_omission_and_unjudged_unit_are_distinct` removes one of two claims and checks missing counts and failure, leaving one accepted claim (`test_evaluation.py:150–163`). It does not test total omission or `review_complete`.

**Suggested next step:** derive review completeness from current judgments and unknown units/dimensions, while keeping semantic success/failure separate. Add a total-omission regression with all expected units explicitly judged missing.

Evidence: [input and judgments](workflows-omissions-input.json), [observed report](workflows-omissions-observed.json), and `omission_accounting` in [the probe script](workflows-probes.py).

## Executed limitations and counterarguments, not separate confirmed defects

### Independent windows can exclude the source condition governing a duty

At the default 6,000-character limit, the probe places `Only when the alarm is active:` at the end of one window and `Staff must evacuate the building.` in the next. `plan_windows` preserves every character, but `_window_prompt` provides only the current slice and section labels/coordinates, with no preceding source context (`extraction.py:142–169`, `434–440`). The duty's prompt contains no alarm condition. A synthetic response extracting that duty without its condition parses as `complete`, compiles with no claim issues, and has empty `logic_text` and `unresolved`.

This executes the context loss and acceptance path; it is **not** a provider experiment and does not establish how often a model omits the condition. A correctly extracted condition from the first window may survive as a separate unresolved claim. The review page also shows the full original source. For these reasons, this is an identified limitation requiring source-aware boundary review, not evidence that a particular real extraction silently lost the condition. The existing window test checks byte/Unicode coverage and offsets (`test_extraction.py:36–49`), not governing semantic context.

Evidence: [window input, prompt, and output](workflows-window-observed.json).

### Approval of a stale qualification still targets its retained old relationship

After editing a permission, the current qualification shows `target_ids: []` and `qualification_target_changed`. Approving that qualification targets its original component assertions, including the relationship to the old permission revision. Executed evidence confirms this.

The distinction is intentional in the code: `_state` retains immutable revisions; `_snapshot` separately resolves active links and clears changed targets (`review_store.py:267–319`); `apply` builds the attestation from retained revision assertions (`review_store.py:361–365`, `413–424`). The warning remains visible, and the dialog says recording a decision keeps open issues (`review.js:274–276`). The UI and graph continue to say review only (`index.html:45`, `core.py:282–285`). Therefore I am **not** reporting operational approval, automatic relinking, or a hidden disappearance of the issue. A future component-level review UI should make the old-versus-current relationship explicit when recording this decision.

Evidence: [stale-qualification observations](workflows-stale-qualification-observed.json). The existing changed-target test confirms edit-to-relink behavior (`test_review_store.py:145–166`) but does not inspect approval performed before that confirmation edit.

### Merge defaults inherit only the first claim's structured content

The executed merge combines two summaries but supplies only a new `summary`. The stored replacement retains only the first claim's `action`, `quote`, and `logic_text`; the second claim's temporal qualification does not enter those fields. The server starts replacements from `originals[0]` (`review_store.py:385–393`), and the UI pre-fills the editor from the first selected claim (`review.js:277`). `revise_claim` then applies explicit replacement fields over that first claim (`core.py:228–235`).

This is a workflow hazard, but the merge request deliberately supplies a replacement, retains both predecessors, and saves all prior evidence in history. There is no documented guarantee of automatic union or semantic reconciliation. A reviewer can intentionally rewrite or reject an earlier meaning. Consequently, the probe does not establish an independent implementation defect. The existing merge test checks predecessor identities and retained assertions, not preservation of the second claim's structured qualifiers (`test_review_store.py:83–89`).

Evidence: [merge inputs and resulting claim](workflows-merge-observed.json).

## Patch scope and function trace

The packet implements source-window extraction, exact evidence grounding, immutable revisions, append-only review actions, graph export, and content-bound semantic judgment accounting. No base diff or prior author conclusions were consulted. File references below are relative to the copied repository at `.tools/blind-review-20260907/code/repo/`.

| Function or entry point | Code location | Inputs → outputs and verified behavior |
| --- | --- | --- |
| `plan_windows`, `_window_prompt` | `extraction.py:142`, `434` | Pinned source → contiguous slices and model prompts; preserves characters, does not supply preceding source context |
| `parse_response_text`, `parse_raw_response` | `extraction.py:191`, `282` | Raw provider text → candidates/refusals; strict wrapper and duplicate-key checks; retains decoded invalid rows |
| `_record_window`, `_attempt_result` | `extraction.py:451`, `508` | Request and response → recorded attempt and parsed terminal window result; synthetic transport used for execution |
| `extract_run`, `_finalize` | `extraction.py:589`, `549` | All windows → run, rulebook, validation, manifest; W1 interrupts before final run save |
| `_verify_manifest`, replay/reprocess | `extraction.py:671`, `1005`, `914` | Saved artifacts → verified replay/reprocessed output; missing W1 manifest prevents entry |
| `_claim`, `resolve_links`, `revise_claim` | `core.py:85`, `168`, `225` | Candidate/replacement → exact grounded revision and quote-based target resolution; first-claim inheritance for partial edits |
| `build_graph` | `core.py:243` | Revisions and attestations → retained Core assertions; keeps draft/review-only use and historical links |
| `ReviewStore.apply`, `_state`, `_snapshot` | `review_store.py:352`, `267`, `296` | Explicit action + expected revision → atomic appended event and current/history views; changed link targets remain issues |
| `ReviewStore._validated_graph` | `review_store.py:207` | Stored revisions → rebuilt assertions with evidence and identity checks |
| `evaluate`, `validate_expected` | `evaluation.py:130`, `76` | Accepted claims, labels, fresh source judgments → dimensions and coverage; W2 conflates empty output with incomplete review |
| `compare_runs` | `evaluation.py:283` | Two accepted-claim sets → exact material-field/count differences; explicitly not semantic equivalence |
| CLI review/export/evaluate | `cli.py:77–91` | Delegates to the same store/evaluator; export includes full retained graph and current/history state |
| HTTP action/snapshot handlers | `review.py:95`, `113` | Delegates to the same store; inspected statically, not executed in this review |
| UI action, replacement, history paths | `static/review.js:151`, `234`, `267`, `281`, `293` | Current selection → explicit action request; manual replacement editor, immutable history text, visible issue warning; static inspection only |

The critical invariants checked were: all acquired windows receive durable terminal outcomes; refusals remain serializable; failed extraction remains distinct from incomplete semantic review; new revisions do not inherit old decisions; changed target relationships remain visible; and merge/edit history preserves superseded records. W1 and W2 violate the first three accounting properties. The executed workflow probes did not establish violations of the last three as the code defines them.

## Test execution and coverage limits

- **61 passed, 2 deselected:** copied `test_review_store.py` and `test_evaluation.py`. The two corpus/holdout tests were deliberately excluded because they refer to material outside the permitted packet. Their inputs were not accessed. Output: [workflows-test-output.txt](workflows-test-output.txt).
- **30 passed, 44 deselected:** selected copied parser/window tests from the first part of `test_extraction.py`, covering malformed JSON, mixed rows, provider shapes, strict evidence alignment, and window coordinates. Output: [workflows-parser-test-output.txt](workflows-parser-test-output.txt).
- **Five independent functional probes plus the recovery probe executed.** All application and projection module paths were asserted to lie inside the packet. The numeric-overflow probe uses real extraction/finalization code and only replaces credential lookup and model construction with an in-process synthetic transport. The other probes use synthetic source text and direct copied APIs.
- The review HTTP tests were read, including their assertions, but not executed. They inspect HTTP behavior and script contents; they do not execute the browser merge/editor flows (`test_review_http.py:42–58`, `81–102`). No browser session was used.
- Passing the development-label tests verifies their digests, shapes, and the evaluator's assertions. I did not independently endorse all 32 labels' meanings. No held-out labels or previous assessment results were read.

For a fresh reproduction, set `PYTHONPATH` to the copied extrapolator and projection `src` directories, use `/Users/mikewolfd/Work/rulespec/.tools/document-poc-venv/bin/python`, and run `workflows-probes.py --runs-dir <fresh-directory-under-.tools>`. Existing run directories are deliberately refused to preserve evidence. Bulk run/frozen/test directories were moved under `.tools/blind-review-20260907/workflows-artifacts/`; tests were not rerun merely for that relocation.

## Source-access disclosure

Static inspection used only this copied code/test packet and the procedural skill `/Users/mikewolfd/.agents/skills/semi-formal-code-review/SKILL.md`. The skill contains the review method, not project conclusions. No memory files, previous reviews, README files, assessment results, or other reviewers' files were read.

Execution necessarily loaded Python standard-library and installed third-party dependencies from the assigned interpreter. The unmodified extraction `_freeze` step also copied installed LangExtract Python sources into the retained frozen runtime tree. I did not inspect those third-party sources for findings. All reviewed `rulespec_extrapolator` and `rulespec_projection` implementations came from the copy; copied validation data was resolved from that same repository. The review report and probe artifacts are the only intentional workspace writes, with bulk generated artifacts under `.tools`.

**Coverage: insufficient for the identified failure and total-omission paths. Confidence: high for W1/W2 and their reproductions; bounded for broader semantic quality and real-provider behavior.**
