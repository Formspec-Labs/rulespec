# Extraction: current value and remaining effort

Decision, 2026-09-07: stop implementation after this verified iteration. The
foundation is strong enough for a discovery pilot and for producing source-backed
drafts that an agent or person reviews before constructing a workflow. The next
investment should improve missing content and exception relationships using the
existing process. Further architecture expansion has lower value right now.

## What already earns its complexity

Rulespec can take exact document text, produce individually referenceable
meanings, keep their conditions and evidence, expose omissions, and record
corrections without losing history. It owns this workflow locally. The complete
meaning representation, exact evidence, provenance and replay are useful for both
search/discovery and later workflow construction.

The implementation passes 223 tests and 101 subtests. Five historical runs remain
compatible, seven new runs reprocess and replay, eight audits replay with their
verified frozen application, and the built wheel works with packaged Core data.
All 1,406 protected original files remain unchanged. The two real negative
controls detect an omitted document alternative and a semantically wrong
exception target. These are concrete successes of the data process.

The quality evidence is narrower. At temperature 0, 17 of 29 named extraction
cases pass; 12 fail. Temperature 0.2 passes 16 and fails 13. These cases overlap
and target difficult behaviors, often requiring every listed clause and explicit
relationship. A missing relationship can fail a case whose prose is otherwise
useful. The numbers are not percentages of the document extracted correctly.

Several earlier high-impact defects now pass: emergency permission retains its
parent conditions; recent-change ID exemption remains distinct from a submission
duty; photo re-execution retains the missing-photo/facility case; should remains
should; the complete contiguous name-document list retains its nested options.
The reference decisions and evidence are in the
[30-case assessment](../../examples/document_understanding/quality-iteration/reference-assessment/RESULTS.md).

## What remains, weighed against effort

Effort below is relative engineering scope, not a schedule commitment. Low means
a bounded change within an existing path; moderate means connected changes plus
source/output experiments; high means a broader capability or sustained quality
program. No work in this table has been started after the stopping decision.

| Work | User value | Effort | Recommendation |
| --- | --- | --- | --- |
| Recover omitted qualified statements using the source inventory | More searchable guidance and fewer missing workflow branches; addresses recurring omissions such as rewrite caveats and certificate guidance | Moderate: connect selected findings to bounded additions through existing review actions, then reassess neighbors | Highest priority |
| Identify explicit exception targets after extraction | More reliable concept graphs and safer translation into workflow conditions; much of the qualifying prose already exists | Moderate: separate relationship reasoning, exact target identity, source evidence and bounded correction | Highest priority, particularly for workflow use |
| Resolve ambiguous component quotations and grouping | Cleaner evidence and fewer false unknowns; avoids downstream confusion over category lists versus conjunctions | Low to moderate: improve local anchoring and selected fixtures, without a general logic language | Fix observed cases alongside the two priorities |
| Measure the full process on a small varied sample | Establishes whether improvements carry beyond this passport sample and whether checking saves effort | Moderate, mostly evaluation: freeze expectations before extraction and compare the same end-to-end process | Do one bounded sample before scaling |
| More temperature or model permutations | May help isolated passages, but current temperature results trade gains for losses | Low code effort, moderate recurring model/review effort | Defer; keep temperature 0 |
| More browser work | Little additional evidence about extraction quality | Low to high depending on scope | Defer as requested |
| More Core schemas, general executable policy logic or full document-format support | Enables broader future use but does not directly fix observed omissions and missing links | High | Defer until a concrete consumer needs it |
| Perfect semantic completeness | Would reduce residual mistakes but has no demonstrated finite stopping point across arbitrary legal documents | High and ongoing | Do not make it the gate for discovery |

The checker itself needs calibration, not blind trust. It missed an inherited
condition and factual-modality errors in earlier runs. A real handoff defect
also hid existing references from it; that defect is fixed and tested. Keep
the source-adjudicated gold reference set versioned, preserve disagreements and
use it to measure the checker as well as the extractor. The agent can adjudicate
these cases; an unresolved application field does not automatically require a
human meeting or manual review queue.

## How the two uses change the stopping point

**Discovery, tagging, embeddings and knowledge graphs:** the output is ready to
pilot as source-backed draft knowledge. It retains useful meaning and evidence,
and later feedback can revise it. An actual search or graph consumer has not been
evaluated here, so retrieval benefit remains unmeasured. Omission recovery should
come first; it increases the content users can find. Explicit exception edges
matter more as the graph starts answering relationship questions.

**Workflow and forms:** the output is a substantially better preliminary draft.
Use the same process with closer adjudication of the specific branches being
implemented. Missing conditions or exceptions have more direct consequences
here. The saved confidential-name correction proves the representation can
express the right result without destroying neighboring duties. It does not
make the uncorrected extraction ready for automatic workflow generation.

## Recommended next investment

After the break, make one bounded iteration that recovers omitted meanings and
adds supported exception targets through the existing correction path. Use the
present gold cases to check regressions, then a small set of previously unused
passages to check transfer. Preserve the original extraction and compare the
final corrected output, including any new errors introduced by repair.

Stop widening the extractor once that process materially improves those two
failure classes without damaging the conditions and modal distinctions already
working. Put the resulting records into one real discovery use, or adjudicate one
small workflow branch for a forms/workflow consumer. That will answer the product
value question more directly than another large infrastructure milestone.

Current delivery is local and uncommitted. Full results and runnable commands are
in the [iteration report](../../examples/document_understanding/quality-iteration/README.md).
