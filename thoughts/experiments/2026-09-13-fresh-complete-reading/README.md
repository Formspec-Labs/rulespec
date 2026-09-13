# Fresh-source checker validation: useful gain, concentrated in fewer unnecessary edits

The unchanged shared-task checker improved judgments on eight fresh statutory
excerpts, from **19/32 (59.4%) to 26/32 (81.3%)** on the same edited candidates.
Five source contexts improved, one regressed and two tied. Both versions rejected
all sixteen deliberately wrong-edit judgments. The earlier improvement transfers,
but most of this new gain is rejecting unnecessary action-field enrichment.
Recognition of needed completeness repairs improved only from 3/10 to 4/10.

| Fresh-case measure | Current checker | Shared-task checker |
|---|---:|---:|
| Correct judgments on the same edits | 19/32 | 26/32 |
| Needed complete repairs accepted | 3/10 | 4/10 |
| Deliberately wrong edits rejected | 16/16 | 16/16 |
| Unnecessary component edits rejected | 0/6 | 6/6 |
| Correct no-change decisions | Unassessed | 10/16 |
| Complete readings correctly left unchanged | Unassessed | 6/6 |
| Incomplete no-change decisions correctly rejected | Unassessed | 4/10 |

The revised checker fixes nine judgments that the current version gets wrong
(one credit judgment, two bankruptcy judgments, six unnecessary-edit judgments)
and loses two correct medical judgments. That yields seven net improvements.
These are repeated judgments of constructed diagnostic candidates around real
production extractions, not a 32-document extraction accuracy estimate.

## What changed across sources

| Source | Current correct edits | Shared-task correct edits | Main result |
|---|---:|---:|---|
| Privacy-record access | 2/4 | 2/4 | Both miss the incoming civil-action exclusion. |
| Bankruptcy dismissal | 2/4 | 4/4 | Shared task accepts expanded local qualifications. |
| Free credit disclosures | 3/4 | 4/4 | Shared task consistently accepts the (p)-specific request condition. |
| Inspection authority | 2/4 | 4/4 | Correctly rejects unnecessary action filling. |
| Jury qualification | 2/4 | 4/4 | Correctly rejects unnecessary action filling. |
| Compensatory time | 2/4 | 4/4 | Correctly rejects unnecessary action filling. |
| Employment medical exams | 4/4 | 2/4 | Shared task wrongly rejects useful exception detail. |
| Recall remedies | 2/4 | 2/4 | Both reject adding the timing/evidence/presentation context. |

Medical is a concrete regression. The draft says there are specified exceptions
for informing supervisors, first-aid personnel and investigating officials, but
omits restrictions/accommodations and appropriateness/emergency-treatment
conditions. The old checker accepts their restoration; the new checker calls it
stylistic and says the original is complete, twice. Both reject changing the
three governing conditions from conjunction to alternatives.

Privacy exposes a plausible wording problem. The shared instruction says:

> A full quotation or another record retaining a condition does not incorporate it
> into this statement.

Both responses interpret that sentence as forbidding incorporation of a condition
already present in another record. This is visible nonadherence in the rationales;
it is not proof of an internal reasoning mechanism. A positive instruction about
including necessary governing conditions is a candidate for a separate comparison.
The tested prompt was not changed after observing this failure.

The old notice regression also persists: the shared checker correctly handles the
exemption candidates but approves the baseline without its incoming exception in
both repetitions. Those fourteen regression judgments are excluded from all fresh
metrics. The current checker also still accepts the saved bad action/object pair.

## Decision against the revised criteria

The experiment meets three criteria: improvement exceeds fifteen percentage
points; at least three new source contexts improve; and acceptance of the known
wrong edits does not increase. It misses the other two: 81.3% edited-candidate
accuracy is below 85%, and 62.5% no-change accuracy is below 75%.

Preserve the useful signal. Do not replace the entire production checker or adopt
its no-change decisions as a completeness check. The next integration candidate
should isolate rejection of unnecessary action/object filling while protecting
real component corrections and the medical detail that was lost. Test the
privacy instruction wording separately; bundling both changes would obscure
which behavior improved.

The recall label has the previously recorded boundary uncertainty: paragraph (2)
provides evidentiary and timing context for paragraph (1), rather than an absolute
60-day remedy trigger. The constructed reading preserves that distinction.
Excluding recall leaves a 17/28 to 24/28 improvement on shared edits, so the
comparative signal survives that uncertainty. This sensitivity analysis does
not replace the original labels or erase the medical regression/no-op failures.

No production code, default extraction prompt, schema or review policy changed
in this experiment. Repair proposals were constructed for testing; this did not
measure the model's ability to generate the repairs. Existing source-level
retention and independent default-reading completeness remain separate criteria.

## Sources, verification and cost accounting

Eight complete native U.S. Code units from pinned release 119-102, covering eight
different sections, were prepared with the existing RefSpec/Rulespec reader.
The distinctive-phrase search found no previous experiment/example uses, excluding
frozen dependencies. These are selected excerpts from one publisher/format;
they do not establish general performance across document formats or whole laws.
The sources, initial criteria and limits were frozen before extraction; candidate
labels and both actual checker inputs were frozen before checker calls.

The normal low-thinking extractor produced 35 accepted records, with seven
complete runs and one partial credit run. Two component quotations were withheld
around footnote/ellipsis handling; all failures and remaining location issues
were preserved. Three selected readings were already independently complete.
Inspection was correctly split into independent authorities; the selection
clarification is recorded before checking in BASELINE-REVIEW.md.

All sixteen edited candidate fixtures passed the existing quotation decoder and
real review preview without modifying original books. Eight native extraction
runs replay identically with provider access blocked. All 94 checker judgments
re-decode identically with valid passage selections. No semantic approval follows
from those mechanical checks.

44 recorded calls: eight production extractions, 32 fresh checker calls and four
old-regression calls. Totals: 312,228 tokens, comprising 215,370 input, 22,445 visible
output and 74,413 thinking tokens. The provider reports 11,619 cached input tokens
as a subset of input, not additional tokens. Summed provider-call time: 328.5 seconds.
No retries, provider errors, missing responses or missing usage receipts. The
44-call bound is exhausted; no further tuning calls were made.

Both checker arms used Gemini 3.8 Flash, medium thinking and 32768 maximum output
tokens; new requests omit deprecated sampling settings. The shared task/schema
are reused unchanged from the prior experiment. Paired candidate ordering is
identical, with fresh order per repetition and randomized call scheduling. The
raw review preceded opening the fresh arm key; task wording and candidate counts
make this only partial masking, not independent human blinding.

## Reproduce and inspect

Use the repository document-poc environment and
`PYTHONPATH=packages/rulespec-extrapolator/src`:

- `run.py extract` records the initial extraction stage once.
- `prepare_checks.py` constructs and freezes the declared candidate comparison.
- `run.py check` records the bounded checker calls without replacing captures.
- `verify.py` replays all native runs and re-decodes checks with provider access
  blocked. It restores identical runtime files when needed.
- `score.py` applies the frozen labels after the raw-review receipt exists.

The 141-file native runtime snapshot is byte-identical across all eight runs and
is retained once under `extract/privacy/frozen`. The other seven manifests still
bind every original byte; verification reconstructs their native layout from
that shared copy and verifies their own manifests. Restoring a sparse capture was
also tested before replay. This avoids seven duplicate versioned runtime trees.

The original plan, source criteria, baseline review, raw review, labels and scored
rows remain separate, alongside every request/response and source receipt.
