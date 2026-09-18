# Granularity sentence: splitting signal, no production adoption

The added sentence separated all thirteen drug-record contents in both repeats;
the current prompt did so in one repeat and bundled them in the other. But the
variant also weakened governing context, local references and a formal
qualification in some default statements. The frozen complete-meaning gate did
not pass. Keep the current production prompt and stop this experiment.

## What changed

Arm A used the exact current separate-section request. Arm B added only:

> Keep independently actionable duties as separate records, including list children that require distinct actions.

The current prompt and CUE schema already request independent meanings. This
tests extra emphasis on list children, not a new schema capability. Source text,
section windows, passage catalog, schema, examples and parser stayed fixed.
All twelve calls used `gemini-3.8-flash`, low thinking and a 16,384-token output
allowance, with sampling settings omitted. There were no retries or prompt edits.
The [pre-call plan](PLAN.md) fixes the cases and decision rule.

These are six paired observations across five known sections, including two
repeats of the drug-record case. They are development evidence, not a fresh-document
benchmark or a reliable estimate of a general success rate.

## Measured results

| Section / repeat | A records | B records | A total tokens | B total tokens | Source review |
|---|---:|---:|---:|---:|---|
| Drug-record contents, 1 | 16 | 16 | 6,587 | 6,445 | Both separate all thirteen contents with full framing. |
| Aviation signals | 12 | 12 | 4,393 | 4,410 | All twelve setting-specific meanings survive; taxonomy differs. |
| Aviation clearances | 8 | 7 | 4,062 | 3,818 | Same seven operative meanings; A also records OMB approval. |
| Technical safeguards | 12 | 12 | 5,794 | 5,731 | B replaces an explicit formal qualification with a paraphrase. |
| CSBG monitoring | 9 | 10 | 5,525 | 5,712 | Same operative meanings; B weakens three referents and separates a historical note. |
| Drug-record contents, 2 | 3 | 16 | 3,405 | 6,193 | A bundles thirteen contents; B separates them but weakens default framing. |
| **Total** | **60** | **73** | **29,766** | **32,309** | **B uses 8.5% more total tokens.** |

B adds seventeen input tokens per request. Across six calls per arm, input tokens
are 14,509 versus 14,611; answer tokens are 15,257 versus 17,698. The study used
62,075 provider-reported tokens in total. Thinking and cache usage were not
separately reported; no dollar estimate is inferred. Summed request duration was
44.5 seconds for A and 49.8 for B, insufficient to establish a latency effect.
See [accounting](accounting.json) and [per-call metrics](metrics.json).

Higher output cost is not itself a failure: individually usable requirements can
justify more tokens. Record totals alone also mislead: the omitted OMB note and
separately stored committee rename do not change operative duty coverage.

## What the raw statements show

**Drug contents:** B's second repeat creates all thirteen separate list records,
but their statements start “Documentation that each significant step ... was
accomplished shall include.” They omit the explicit batch production/control record
target and every-produced-drug-batch setting preserved in the first repeat and
A's composite statement. B's scope text and source quotes recover that context.
This is weaker independent reading, not erased evidence. A's composite retains
all thirteen contents verbatim in meaning; its failure is separate referenceability,
not omitted list content. Both preserve the personnel/automated-equipment alternative.

The two captured A requests are identical, as are the two B requests. A also
matches the previous grouping study's coarse control request. The different A
outputs demonstrate variability under identical visible inputs. Two B successes
suggest a splitting effect but do not establish consistent complete extraction.

**Monitoring:** A identifies “42 U.S.C. 9914,” evaluations of the use of funds,
and “the evaluation report from the Secretary.” B uses “this section,” “such
evaluations,” and “the report.” The receipt trigger and full quoted subsection
survive, but an isolated default statement becomes less clear. Some evaluation
references remain implicit in both arms; A is better here, not fully repaired.

**Technical safeguards:** In five records, A explicitly retains “as an addressable
implementation specification”; B writes “must address implementing.” B's primary
quotes retain `Addressable`, but its default statement substitutes an interpretation
for the formal qualification. The referenced § 164.306 body was not supplied, so
this review does not adjudicate the full implementation policy or equate
Addressable with optional. The exact label is the more faithful captured wording.

**Counterexamples:** Both aviation outputs retain the twelve signal mappings,
three alternative deviation exceptions, cancellation permission, notification,
and the separate conditional 48-hour report. No new table merging, mandatory
alternative splitting or transfer of timing was observed in this round.

## Independent review and checks

An independent agent reviewed all 133 records against the supplied sources in
randomized unlabeled pairs, without arm labels, costs, plans or earlier study
results. Its [review](review/REVIEW.md) was saved and hashed before the assignment
key was opened; see the [receipt](review-receipt.json). The parent separately saved
a [manual assessment](ROOT-REVIEW.md) before reading that review.

After unmasking, both reviews agree on the splitting/framing tradeoff, weaker B
monitoring referents and the Addressable paraphrase. The independent review also
notes reduced every-batch framing in B's second-repeat records 2–3, beyond the
thirteen list children emphasized by the parent. This strengthens the same concern;
there is no material decision disagreement. These are revisable source readings,
not gold labels or additional model samples.

All twelve actual requests match the frozen inputs/settings and replay through
the native parser. All 133 candidates compile into Core without rejection, and
all twelve graphs conform. These checks establish processing compatibility, not
semantic completeness. [Replay results](verification.json),
[Core results](core-compatibility.json), [exact captures](captures/) and
[prepared input structures](inputs/) are retained.

The CFR sources reuse the earlier study's pinned, whitespace-normalized section
text, including table rows. This tests extraction from that prepared text, not
native annual-CFR XML ingestion or publisher-coordinate fidelity. Raw sources,
preparation checks and runtime snapshots remain in the
[preceding study](../2026-09-14-grouping-fresh/RESULTS.md); the design pins those dependencies.

## Disposition

- Splitting criterion: observed in both B repeats versus one A repeat.
- Complete independent meaning / no new material regression criterion: not met.
- Production adoption: hold; retain the current prompt and section-focused flow.
- Further calls or compensating prompt patches in this experiment: none.

The useful lesson is to assess separate referenceability and complete statement
context together. Increasing record count alone can conceal weaker extracted
requirements. No production files changed and no commit was made for this test.
