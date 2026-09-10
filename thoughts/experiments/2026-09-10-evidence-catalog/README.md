# Shared evidence catalog: lower token use, failed adoption gate

**Decision: retain as an experiment; do not integrate.** Sharing repeated source
quotations reduced input tokens by 31.66% and total tokens by 22.75%, but the
candidate applied one fewer correct relationship. Both versions also missed the
same expected relationship in the fresh refrigerant document.

## What we compared

A used the current relationship and challenge inputs. B stored repeated exact
quotation strings once and referenced that text from their original fields.
Source positions, identities, roles, statements, and review data stayed intact.
Both versions still returned literal quotations under the same output schemas.
The encoding round-tripped exactly; this establishes data preservation, not model
accuracy.

We ran one paired comparison on each of three cases: alcohol, railroad crossings,
and fresh 40 CFR 82.154(a)-(b). A single fresh extraction supplied both arms of the
last case. There were 13 live calls: one shared extraction and six proposal/check
pairs. No retries, post-result tuning, or production changes were made.

## Recorded results

| Measure, six calls per arm | A: repeated quotations | B: shared catalog |
| --- | ---: | ---: |
| Input tokens | 97,696 | 66,764 |
| Answer tokens | 8,822 | 7,749 |
| Thinking tokens | 34,775 | 34,631 |
| Total tokens | 141,293 | 109,144 |

The shared extraction used another 4,599 reported total tokens, excluded from the
paired comparison. Its thinking-token field was absent. All 13 calls together
reported 255,036 total tokens. These are token counts, not dollar estimates.

| Case | Expected primary links | A proposed / applied | B proposed / applied |
| --- | ---: | ---: | ---: |
| Alcohol | 2 | 2 / 2 | 2 / 2 |
| Railroad crossings | 5 | 5 / 5 | 5 / 4 |
| Refrigerants | 3 | 2 / 2 | 2 / 2 |
| Total | 10 | 9 / 9 | 9 / 8 |

No incorrect targets or destructive meaning changes were observed. Original
meaning and evidence survived. B's alcohol additions included two actor fields
whose evidence remained unresolved; A omitted those fields on its additions.

The lost railroad link was a challenge-grounding failure. B proposed the correct
link, but its challenge copied source `§ 390.5` (U+2009 THIN SPACE) as `§ 390.5`
(U+0020 SPACE). Exact grounding rejected the quotation. P0000 remained unjudged
and unapplied; its standalone exemption remained intact. See
[the raw challenge](cells/cell-05/challenge/attempt-0000.response.json) and
[decoded results](cells/cell-05/result.json). We did not normalize the capture or
count a proposed link as applied.

Both arms omitted C0001 → C0004 in the refrigerant case: the listed-substitute
exemption also qualifies the local appliance-service requirement. A incorrectly
described those other duties as unavailable remotely, despite C0004 being present.
B supplied no omission explanation. C0004 already says non-exempt substitute, so
this is incomplete explicit linking, not a newly overbroad default statement.
Both preserved the listed end uses, effective date, good-faith condition, and
alternative compliance routes.

## Interpretation and next hypothesis

The cost gate passed; the useful-output gate failed. One sample per case cannot
establish that compression caused the quotation error or predict its frequency.
It does establish that this observed candidate did not retain all useful output.
The review was performed by the same agent using shuffled, hidden arm labels;
these are revisable judgments, not independent gold labels.

The next separable hypothesis is that **returning source references instead of
retyping evidence removes copying failures without weakening grounding**. Reuse
the existing audit approach: `audit.py` already derives `SOURCE_REFS` from the
generated schema, asks for passage references, and resolves them to source text.
The canonical CUE schema already defines `#SourceRef` and `#FocusSourceRef`.
Assess that path before introducing another identifier or resolver.

Test the challenge-output change independently from input compression. Include
the saved thin-space failure, wrong/missing references, repeated text at different
positions, and governing conditions spanning passages. Resolving a valid reference
does not prove that the selected passage supports the judgment. The fresh missed
relationship is a separate target-discovery problem and should remain visible.
No follow-up change or live test is included in this experiment.

## Evidence and verification

- [Preregistered design](PLAN.md), [frozen cells](cells-design.json), and
  [source expectations](expected.json).
- [Sixteen offline counterexample checks](preflight.json), including Unicode,
  repeated text with distinct identities, overlap, AND/OR, and invalid references.
- [Manual review before arm reveal](BLIND-REVIEW.md) and
  [recorded usage and applied changes](assessment.json).
- [Replay result](replay-checks.json): saved proposal/challenge decoding matched
  with zero provider calls. Review-store reloads and discovery exports also
  matched saved outputs. This replay does not independently reconstruct every
  applied review event.
- Immutable source, request, response, isolated review workspaces, and runtime
  fingerprints are retained in this directory.
