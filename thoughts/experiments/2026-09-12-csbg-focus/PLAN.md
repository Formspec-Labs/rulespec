# Does a narrower extraction focus recover the missing plan contents?

Decision: determine whether narrowing the focus to a complete legal section is
a promising way to capture the individual CSBG State-plan requirements. No
automatic selection rule, production change, audit, or form/workflow mapping.

Observation: the original full-chapter run supplied every line of 9908(b), but
the model reduced its thirteen required contents to one reference-only statement.
All source evidence survived. It ended STOP below its output cap.

Hypothesis: a focused request gives the complete plan section enough attention
and output allocation to capture its individual requirements. A competing
explanation is ordinary model variation: a fresh identical broad-window request
may already recover them. Another is persistent preference for coarse units:
both requests may compress the list. This test can distinguish these observed
outcomes, not hidden attention from output-allocation causes.

Arms: A freshly repeats the exact original extraction requests for windows 1 and
2. B makes each complete section 9908, 9910 and 9915 the focus, on the SAME pinned
chapter document and coordinates. Use existing `with_context` to add parent and
adjacent evidence. Section 9908 includes its governing lead-ins, funding-cause
definitions and time-limited transition; do not isolate individual bullets or
remove difficult qualifications. Both arms use the production prompt, passage
catalog, schema, capture, response parser and Core compiler. B changes the focus
boundaries and resulting catalog/context; no extra reference injection is tested.

Cases: assess all thirteen State-plan contents separately. Each must have its
specific meaning captured as plan content, with named actors, conditions,
alternatives and relevant sublists. A generic reference to the numbered list does
not count. A combined statement may preserve meaning, but separately score whether
each top-level content has a distinct requirement record. More units alone is not
success. Use the complete board and corrective-action sections as controls:
preserve the elected-official shortage exception, low-income representation and
residence, public-board OR alternative mechanism, conditional assistance/report
branches, State discretion, 60-/30-day clocks, unless-corrected protection, and
on-request 90-day review with its documentation trigger and default finality.
Do not promote optional examples to mandatory programs. Keep source-based labels
revisable. Read raw output and accepted output separately, including rejected rows.

Held constant: installed runtime, source bytes and section index, prompt and CUE
schema, gemini-3.8-flash, temperature zero, low thinking, 16,384 output tokens per
request, no numeric thinking budget or retries. Five calls total: two A, three B.
One observation per cell, plus the original saved historical outputs. The two
controls share a broad A window but have separate B requests. Aggregate output
allowance and work per request therefore differ; no pure latency/cost advantage
or general segmentation mechanism can be inferred. Stop after five calls or
20 minutes of capture, whichever comes first. No automatic second experiment.

Decision rule: all thirteen plan contents must emerge with faithful meaning and
independent top-level records, without substantive control regressions, to call
this a successful targeted capture result. Fewer gains are partial improvement.
If fresh A also succeeds, treat simple focus reduction as unproven. If both fail,
do not keep shrinking sections or add prompt patches in this batch. Report validity,
grounding, semantics, granularity, tokens and time independently. This selected
development case does not establish general reliability or justify adoption.

Review: randomize capture order and mask arm identities in the paired review
files. Assess those before opening the key. Structural differences may reveal the
arm, so this is only partial masking. Pin the review before revealing identities.
Replay the saved captures through the same parser/compiler with provider setup
disabled; verify actual A requests equal historical requests and all meaningful
source lines of each case appear in both relevant requests.

Implementation boundary: explicit focus windows are an experiment assembled from
existing functions, not a new production planner or supported CLI run. Preserve
the original chapter run and history. Save custom replay receipts without calling
them a replay of an ordinary whole-document extraction run.
