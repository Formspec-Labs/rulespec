# Small extraction improvements: one adopted, two tested

Discovery exports now retain each accepted statement's existing `logic_text`.
This preserves detailed wording already available in the rulebook, including
qualifications missing from a short statement. It does not rewrite the statement,
certify the logic, or replace full source passages. No new model pass was added.

The two audit changes remain experimental. Shared CUE classification guidance
improved some labels but introduced a scope regression in one output. Changing
unit judgment field order produced no measured improvement in the verdict checks.

## Separate controlled comparisons

[PLAN.md](PLAN.md) was saved before requests. All 16 calls used
`gemini-3.8-flash`, medium thinking, temperature zero, no numeric thinking budget
or application output cap, and no retries. Each arm/case ran twice. Both used the
same original 6,919-character development source. The full raw inputs, actual SDK
requests, responses, parser results and shuffled review packet are saved here.

| Comparison | Baseline | Treatment | Decision |
|---|---|---|---|
| CUE kind/modality descriptions added to inventory prompt | Need-not-count kind: permission, exception | Exemption in both runs | Label improvement with a meaning tradeoff; keep experimental |
| Evidence/rationale before unit coverage status | 6/6 primary verdict checks | 6/6 primary verdict checks | No measured accuracy improvement; keep current order |

The classification treatment reuses generated descriptions verbatim and changes
no response fields. Both arms retain real accounting permission and uniformity
must-force, including defensible combined units. Treatment uses statement for
non-FMLA possibility in both runs; baseline uses permission once and a combined
conditional requirement once. Classification depends partly on segmentation;
these counts do not imply every unit has one indisputable label.

One treatment output separates the teacher example and omits its inaccurate-record
condition, while both baseline outputs retain it. That treatment also splits
accounting permission away from its governing exceptions. This fails the
prespecified no-regression rule despite better labels. The runs produced 15/16
baseline versus 24/17 treatment inventory units, all mechanically accepted. More
units are not evidence of better recall.

The order experiment uses the original failing accounting claim with its full
source, plus constructed complete and qualification-absent counterparts. A
manually specified inventory describes the complete target accounting meaning;
this differs from the historical full-document comparison. Both orders flag
summary/scope errors in original and absent cases, and accept complete wording.
The actual request and response orders match their assigned arms in all 12 calls.
Only one baseline original-case rationale explicitly recognizes the qualification
retained in `logic_text`; neither treatment original-case rationale does. The
verdict checks therefore pass while the fuller explanation goal remains unmet.
We did not isolate whether smaller comparison scope or a better inventory caused
the improved baseline behavior relative to history.

Reported tokens: inventory baseline 10,235, treatment 11,455; comparison baseline
46,616, treatment 41,880; total **110,186**. All responses ended STOP. Small samples
on development data do not establish general accuracy or stable cost savings.
The initial arm-blinded source judgments are agent-authored and revisable.

## Fresh complete workflow

After saving the comparison decisions, the unchanged production audit and updated
export ran once on a reserved [2025 government section](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol3/xml/CFR-2025-title29-vol3-sec825-303.xml)
about unforeseeable leave notice. That section was not found in earlier repository
experiments; it is not guaranteed unseen by the model. Original XML and the exact
4,360-character prepared text are retained, including XML formatting whitespace.

- Low extraction: **18 accepted statements, zero rejected, zero extraction refusals**.
- Medium inventory: **19 accepted observations including one heading**, zero refusals.
- Medium comparison: **15 of 18 claim judgments accepted**. Three claim judgments
  and their three matching unit judgments failed exact quotation checks.
- Accepted audit coverage: 13 covered, two partial, three unknown; report status
  `failed`, `review_complete=false`. These are model judgments, not source recall.
- Discovery retains five source passages and all 18 statements' `logic_text` values.

Direct review before reading the audit found timing, emergency-room versus inhaler
examples, notice alternatives, first versus subsequent requests, reasonable-inquiry
conditions, and the three-part stabilization/phone-access/phone-use condition
preserved in prose. One employer call-in permission lacks its governing scope in
standalone wording. Its full paragraph remains in `logic_text`, demonstrating the
export fix on new data. Some modality labels remain debatable.

The raw audit identifies that overbroad permission, but its evidence normalizes
source whitespace and the exact parser refuses the judgment. The other two refused
pairs alter thin-space/formatting whitespace as well. A diagnostic-only normalized
comparison confirms matching text; acceptance was not relaxed and original
captures were not modified. The audit also flags two expected-to-act statements
as possible modality errors. Those judgments require interpretation, not automatic
conversion into recommendations.

The three calls reported **78,887 tokens**: 6,181 extraction, 4,488 inventory,
68,218 comparison. Comparison input alone was 45,154 tokens despite the short
source, illustrating the cost of repeated full evidence in claim records. This
is one observed run, not an estimated typical document price. All calls ended STOP.
No tuning or retries were performed after this new-document result.

## Verification and stopping point

The 14 focused extraction/discovery tests pass. A saved previous accounting claim
keeps its detailed exceptions in the new export while source records remain
identical. The new-document export retains `logic_text` exactly for every claim.
No production audit prompt, CUE schema or generation setting changed.

The sixteen comparisons replay from their saved requests and responses; replay
checks actual schema order as well as object values. The full extraction, audit
and export replay identically, including the recorded failures. Manifests preserve
all inputs and captures. The full-workflow harness is reused from the previous
experiment and pinned by hash; production runs retain their frozen runtime.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/minor-audit-improvements/experiment.py replay
.tools/document-poc-venv/bin/python examples/document_understanding/minor-audit-improvements/workflow.py replay --output /tmp/rulespec-new-replay
```

Replay needs the recorded runtime; the comparison runner reports runtime drift
and fails if recomputed observations differ. It never treats replay as a fresh
model result or broad semantic validation.

The next narrow candidate is passage-ID evidence for comparison judgments, where
fresh whitespace failures now prevent useful findings from being accepted. That
change is proposed only. Reusing source references may also help reduce repeated
evidence in requests, but no cost-saving intervention was tested here. Further
prompt accumulation is not supported by these results.
