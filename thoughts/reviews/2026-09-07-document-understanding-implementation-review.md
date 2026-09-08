# Document-understanding implementation review

Date: 2026-09-07. **Current verdict: APPROVE for the bounded local implementation
after remediation.** The original verdict was **REQUEST CHANGES**. The original
findings and probes remain below; [remediation verification](#remediation-verification)
records their closure and distinguishes independent checks from author-run
regressions.

At the original reviewed snapshot, the local review workflow preserved edits
and blocked the tested browser attacks, but its first opening could accept an
altered extraction. The exported Core history also missed several ordinary
correction transitions. Four findings were reproduced. The following original
review describes that pre-fix snapshot.

This is an independent review of `core.py`, `documents.py`, `vocabulary.py`,
`review_store.py`, `review.py`, and their static assets. The reviewer authored the
separate extraction module and did not review it here. No held-out labels were
read, no provider calls were made, and no runtime files were edited during this
review. All probe decisions identify an AI agent; they do not establish human
review or semantic accuracy.

The [probe results](2026-09-07-document-understanding-implementation-probes.json)
retain observed outcomes and reviewed-file hashes. Finding locations below
describe that snapshot; later corrections may move them.

**Remediation handoff:** the integrator reports fixes for F2/F4, including
content-bound Core Artifact records for each application revision so restored
propositions retain an ordered review history without supersession cycles. The
review worker reports fixes for F1/F3 and is independently checking those Core
changes. Those reports do not replace independent closure verification; the
findings and pre-fix evidence remain below. The extraction worker subsequently
added explicit provider-free `reprocess_run` with 58 passing extraction tests so
current processing can be applied to the original frozen captures without
weakening strict replay.

## Findings

### F1 — BLOCKER: an altered extraction can become the initial review baseline

**Category:** correctness/security. **Location:**
[review_store.py:98](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L98),
[review_store.py:119](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L119),
[review_store.py:263](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L263).

The constructor reads three base files and fingerprints their current bytes. It
does not verify an existing extraction manifest; accepted claims need only
revision IDs and a nonempty assertion-ID list. Approval trusts those IDs, while
the snapshot independently rebuilds a graph from claim text.

**Reproduction:** call the existing `make_run` fixture; record its file hashes in
`manifest.json`; change only `rulebook.json`'s first accepted summary to
“Supervisors must pay an invented fee.” Open `ReviewStore` and approve that
revision. The unchanged manifest no longer matches, yet approval succeeds at
review revision 1. The generated Attestation has one target absent from the
rebuilt graph. Core JSON Schema and SHACL still pass.

**Required fix:** verify an existing extraction manifest before creating the
review database. For hand-authored, manifest-free fixtures, independently check
claim evidence, immutable assertion IDs, and graph agreement. Every attestation
target must identify a retained assertion. Existing post-opening tamper tests do
not cover this first-opening path. The review worker owns remediation.

### F2 — WARNING: Core replacement history drops kind, relationship, and restored-value changes

**Category:** correctness. **Location:**
[core.py:238](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L238),
[core.py:296](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L296),
[core.py:312](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L312).

Value-assertion supersession matches only an unchanged predicate. Relationship
assertions never receive supersession links. Reusing an earlier assertion ID
discards later state through `nodes.setdefault`.

**Reproductions:** correct a misclassified requirement over “Drivers may
depart.” into a permission; both summary assertions remain in the Core graph,
and the correction does not supersede the old requirement assertion. Edit a
qualification; its new relationship does not supersede the old relationship.
Change the actor Supervisors → Drivers → Supervisors; the current actor reuses
its first assertion, while the graph still says the intermediate actor
supersedes it. All three transitions are recorded correctly in the application
revision history.

**Required decision:** preserve these transitions in the exported review/Core
records, or explicitly limit the graph to historical propositions and require
the application revision history to determine the current result. Preserving
the original assertion's origin does not require dropping later review state.
Do not introduce a supersession cycle when a value is restored. Core permits
supersession links; this finding concerns the application's promised history,
not a claim that every Core assertion is required to use them.

### F3 — WARNING: the browser hides recorded parser and provider refusals

**Category:** correctness. **Location:**
[review.js:171](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/static/review.js#L171).

`renderProblems` selects only compiler rejections. It never reads the separate
`extraction_refusals` list.

**Reproduction:** open a fixture containing a failed window and a recorded
`malformed_json` refusal. In the actual browser, the header reports partial
processing, but the “Extraction issues” panel is hidden and the refusal reason
is absent. A reviewer cannot inspect why that source window failed.

**Required fix:** render parser/provider refusals with their window, attempt,
and terminal reason, alongside compiler rejections. Keep the existing text-only
DOM construction. The review worker owns remediation.

### F4 — WARNING: source maps accept impossible original coordinates

**Category:** correctness. **Location:**
[documents.py:41](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L41).

Original source coordinates are checked only by subtracting them and comparing
the length. Their types and lower bounds are unchecked.

**Reproduction:** add a source-map entry covering the prepared text with
`source_start=-7`, or `source_start=0.5`, and set `source_end` to that value plus
the text length. `validate_document` accepts both, and the compiler accepts a
claim grounded through each map.

**Required fix:** require non-boolean integers and
`0 <= source_start < source_end`. Exact original-source verification still needs
the referenced source snapshot; these local checks should not imply that its
contents were independently verified.

## Patch summary and function trace

The new package turns exact source text into Core assertions and a persistent
review interface. `cli.main` calls document loading, review serving, review
actions, export validation, and vocabulary annotation. The following traces
cover the behavior-critical paths; pure serialization and DOM construction
helpers were also read.

| Function | Input → output | Verified behavior and caller |
| --- | --- | --- |
| [prepare_document:8](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L8), [load_document:55](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L55) | Exact text/JSON → document | CLI preparation/loading preserves text and calls validation. |
| [validate_document:20](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L20) | Document → checked document | Compiler/loading checks text identity, sections and prepared source-map coverage; F4. |
| [_evidence:63](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L63), [_claim:85](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L85) | Candidate/source → evidence and revision | Exact projection helpers ground quotes; inserted text is refused and missing component evidence remains an issue. |
| [assertion_id:145](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L145), [_component_nodes:151](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L151) | Rule component → assertion | IDs hash proposition fields; kind changes the summary predicate. |
| [resolve_links:161](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L161) | All claims → target IDs/issues | Any missing or ambiguous target clears the whole target set. |
| [compile_candidates:195](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L195) | Document/candidates/run → rulebook | Validates source, retains rejected candidates, resolves links, builds graph. |
| [revise_claim:218](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L218) | Old revision/fields/event → new revision | Keeps the review handle, verifies evidence, records predecessor IDs. Called by review edits. |
| [build_graph:236](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L236), [validate_graph:342](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L342) | Retained claims/reviews → Core graph/check | Retains original origin and all supplied revisions; validates Core shapes, but not application target agreement; F1/F2. |
| [load_vocabulary:11](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/vocabulary.py#L11), [annotate:30](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/vocabulary.py#L30) | Explicit RefSpec snapshot/rulebook → suggestions | Exact normalized labels return suggested, ambiguous, or unmapped records; source text remains. |
| [ReviewStore.__init__:89](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L89), [_check_base:147](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L147) | Run directory → pinned review store | SQLite pins first-read bytes, later detects file drift; F1. |
| [_read_events:156](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L156), [_state:173](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L173) | Stored events → retained/current revisions | Checks ordered hash chain and forbids targets already replaced. |
| [_snapshot:198](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L198), [snapshot:247](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L247) | Revisions/events → review state | Rebuilds retained graph; changed qualification targets remain explicit issues. |
| [apply:254](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L254), [_validate_request:333](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L333) | Expected revision/action → durable event | `BEGIN IMMEDIATE` serializes writes; only one concurrent action can use a revision. |
| [create_server:146](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review.py#L146), [serve:158](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review.py#L158) | Run/loopback address → HTTP server | CLI route refuses non-loopback listeners and serves only listed assets. |
| [_trusted_request:73](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review.py#L73), [do_GET:95](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review.py#L95), [do_POST:113](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review.py#L113) | HTTP headers/body → response/action | Host, origin, fetch-site and CSRF checks precede writes; body size/type are bounded. |
| [render/detail/highlight:39](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/static/review.js#L39), [openAction:231](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/static/review.js#L231), [submit:254](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/static/review.js#L254) | Snapshot/form → DOM/action | Text nodes prevent source markup execution; Unicode codepoints preserve highlighting; expected revision is fixed when the dialog opens. |

## Data flow and invariants

- Document text is hashed during preparation, checked during compilation, and
  re-sliced by the shared projection evidence helpers. Original-source mapping
  metadata is separate and currently weaker than prepared-text checking (F4).
- Candidate components become proposition-addressed assertions. Review changes
  create new application revisions; unchanged propositions keep IDs and origin.
  `prior_assertion_ids` reaches graph construction, where some transitions are
  lost (F2).
- An action supplies its expected event sequence. One SQLite write transaction
  validates it, produces the complete replacement/attestation record, appends a
  chained event, and commits. Reopening reconstructs current and retained claims.
  This protects ordinary concurrency, not first-opening baseline validity (F1).
- Source/model/reviewer strings enter DOM text APIs. HTTP writes require the
  local origin and a session token. Self-declared reviewer type is attribution,
  not proof that a human made the decision.

## Tests, probes, and limits

The reviewed suite passed **28 tests**, with four rdflib deprecation warnings:

```sh
.tools/document-poc-venv/bin/python -m pytest packages/rulespec-extrapolator/tests/test_core.py packages/rulespec-extrapolator/tests/test_review_store.py packages/rulespec-extrapolator/tests/test_review_http.py -q
```

The Core tests at [test_core.py:28](../../packages/rulespec-extrapolator/tests/test_core.py#L28)
cover exact component evidence, actor-only identity changes, evidence-only
revisions, missing evidence, partial target sets, malformed candidates, and
changed source text. They pass but do not exercise F2's kind/restoration cases
or F4's invalid original offsets.

The review tests at [test_review_store.py:52](../../packages/rulespec-extrapolator/tests/test_review_store.py#L52)
exercise approve/edit/split/merge/reject/reopen, concurrent revision conflicts,
invalid corrections, changed qualifier targets, snapshot isolation, and later
base/event tampering. Their expected behavior passed. First-opening manifest
tampering was untested before the new probe. No direct vocabulary test appeared
in this reviewed suite; matching behavior was checked by tracing its code.

The HTTP tests at [test_review_http.py:41](../../packages/rulespec-extrapolator/tests/test_review_http.py#L41)
exercise actions, stale revision conflicts, foreign host/origin/token rejection,
asset paths, malformed bodies, and loopback binding. Actual Playwright checks
used the separate `implementation-security` session on temporary ports, apart
from the integrator's live run. Hostile-looking source produced **zero** script
or image DOM nodes and did not execute. A second origin could not read the
session endpoint; its POST returned **403**, leaving **zero** events. These
bounded checks support the browser boundary; they are not a general security
audit. The same browser confirmed F3's hidden refusal reason.

## Conclusion

**VERDICT: REQUEST CHANGES at the reviewed snapshot.** First-opening integrity
must be repaired before treating saved approvals as bound to the extraction.
Coordinate checks and failure visibility need narrow fixes. Core replacement
history needs a clear, tested treatment of the three reproduced transitions.

Coverage of the stated edge cases: **INSUFFICIENT before these probes**.
Confidence in the reproduced findings: **HIGH**. Passing structure and browser
checks does not establish semantic completeness or human review.

## Remediation verification

**Current verdict: APPROVE for this bounded local slice.** No material issue
remained in the checked Core history and source-coordinate paths after the
fixes below. This verdict does not authorize operational use or establish
semantic accuracy, human review, deployment, or release.

The review implementation worker independently checked the integrator's
`core.py` and `documents.py` changes. The same worker authored the F1 and F3
fixes, so their checks are **regression verification**, not an independent
security review. No provider calls or runtime-source changes occurred during
this verification.

The [closure evidence](2026-09-07-document-understanding-remediation-verification.json)
records the checked source hashes, exact scenarios, observed outcomes, and
verification roles.

| Finding or follow-up | Result | Verification and evidence |
| --- | --- | --- |
| F1: first-opening integrity | Closed. An existing extraction manifest is verified before database creation. Evidence slices and fragment identities, component assertion IDs, and attestation target resolution are checked before trust or event insertion. | **Author-run regression verification.** [ReviewStore checks](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L148); [first-open tampering](../../packages/rulespec-extrapolator/tests/test_review_store.py#L222), [manifest-free tampering](../../packages/rulespec-extrapolator/tests/test_review_store.py#L249), and [dangling targets](../../packages/rulespec-extrapolator/tests/test_review_store.py#L277) pass. |
| F2: Core correction history | Closed. Kind changes supersede the previous summary. New qualification relationships supersede prior qualification relationships. Immutable revision artifacts retain their component references, content digests, and predecessor chain when an earlier proposition is restored. | **Independent verification.** [Component families](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L151), [relationship supersession](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L319), and [revision artifacts](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L335). Actor A → B → A, requirement → permission, and qualification target counts 2 → 1 → 2 all preserve the expected history and pass Core/SHACL. No assertion-supersession cycles appear. |
| F3: hidden extraction refusals | Closed by the current rendering path. Parser/provider refusals contribute to the issue count and display their window, attempt, and terminal reason alongside compiler rejections. | **Author-run regression verification.** [Refusal rendering](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/static/review.js#L171) uses text-only DOM APIs; the HTTP regression preserves recorded refusals. This verifier did not independently repeat the browser probe. |
| F4: impossible original coordinates | Closed. Source coordinates require non-boolean integers, a nonnegative start, a positive interval, a source identifier, and the mapped length. | **Independent verification.** [Coordinate checks](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L41) reject seven negative, fractional, boolean, empty, or reversed interval cases. Original-source content verification remains separate. |
| Follow-up: newline preservation | Closed. Independent review found that `Path.read_text()` converted CRLF to LF before pinning, changing a 52-codepoint input to 51 codepoints and moving the second rule's start from 26 to 25. Loading now decodes the original UTF-8 bytes directly. | **Independent verification.** [Exact text loading](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L59) preserves CRLF, CR, and mixed LF/CRLF text, its digest, and rule offsets. [Three regressions](../../packages/rulespec-extrapolator/tests/test_core.py#L125) pass. |

The exported graph retains historical propositions and their original origin.
Use the immutable revision artifacts and application review history to
determine the current claim components; proposition-level supersession alone
does not select the restored value in A → B → A. Independent checks also confirm
that inserted preparation text cannot ground a claim, while a mapped original
source passage remains eligible as evidence.

The focused suite passed **57 tests**, with seven rdflib `ConjunctiveGraph`
deprecation warnings:

```sh
.tools/document-poc-venv/bin/python -m pytest packages/rulespec-extrapolator/tests/test_core.py packages/rulespec-extrapolator/tests/test_review_store.py packages/rulespec-extrapolator/tests/test_review_http.py -q
```

Coverage of the checked remediation paths is **ADEQUATE for the bounded
slice**. Confidence in the independently reproduced Core and source-coordinate
outcomes is **HIGH**. F1/F3 retain the narrower author-run regression evidence
described above.
