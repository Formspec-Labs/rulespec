# Reference feedback through existing review history

**Adopt the saved-run feedback command.** It preserves a person's comment and
the exact reading they challenged through review history and discovery export.
It reuses `ReviewStore.observe`, Core `Finding`, source evidence and reader pins;
there is no new store, identity scheme, dependency or model call.

The [plan](PLAN.md) compares two constructed designs: retain only an occurrence
ID, or retain the selected reading and its source/reader context. This is a data
fidelity experiment, not a model accuracy or user productivity measurement.

## Findings

- An accepted occurrence ID can stay unchanged when the native reading changes.
  In the constructed control, changing part `1910` to `1911` leaves that ID
  unchanged. The captured reading and scan digest retain the distinction.
- The actual reverse-title XML repeats `part 1910 of title 29, Code of Federal
  Regulations`. Feedback on the later occurrence preserves its distinct source
  position (`874:924`) and evidence.
- The actual title-21 paragraph yields the refused reading
  `21 CFR 1301.13(e)(1)(iv) to prescribe`. Its `cfr_range_end_unread` reason,
  coordinates and quotation survive without inventing an accepted reference ID.
- Selected external targets retain their source, surrounding record and edition
  metadata. Competing editions and publisher/text disagreement remain visible;
  unrelated target bodies are omitted.
- The first export check exposed a missing comment: event rationale alone does
  not appear in discovery. The observation now carries the comment explicitly.
- An independent [source survey](../../reviews/2026-09-11-source-feedback-cross-relevance.md)
  exposed another omission: supplied-source diagnostics were dropped when no
  target was located. The final helper retains those diagnostics and their XML
  fragments. A constructed combined-section control preserves
  `native_section_scope_not_supported` for `49 CFR 11.105-11.106`, without
  interpreting either endpoint as the whole node.

These diagnostics are retained source observations. They do not prove that every
source issue explains a particular missing target, that a reported parser reading
is correct, or that a selected edition governs the primary document.

## Verification and delivery

| Check | Final result |
| --- | --- |
| Focused feedback cases | 17 passed; [log](source-issue-followup.log) |
| Full application suite from source | 662 passed; [log](source-suite-with-issues.log) |
| Full application suite from isolated wheel, outside checkout | 662 passed; [log](installed-suite-with-issues.log) |
| Normal reference → feedback → discovery commands | Repeated and refused cases agree across source, isolated and working installs; [comparison](command-parity-with-issues.json) |
| Seven pinned wheels in both installations | 1,344 files, including 410 Python files, match wheel bytes; all 21 application Python files match source; [receipt](wheel-verification-with-issues.json) |
| Provider calls | 0 |

The focused cases also cover stale revisions, altered source evidence, invalid
selection, unchanged claim approval, absent optional readers during reload,
edition ambiguity, and unresolved inserted-source grounding. Full suites report
11,147 warnings; those logs are retained, not described as warning-free runs.
Command comparison preserves complete observations and removes only generated
event IDs when comparing discovery. Event IDs and timestamps naturally differ.

The final [wheel inputs](wheel-inputs.json) and
[source freeze](source-issue-freeze.json) identify the delivered runtime. The
working installation is `.tools/document-poc-venv`; the isolated installation is
`.tools/reference-feedback-20260911`. This is local delivery, not publication or
deployment. The package README documents the command and matching install recipe.

Earlier failures, captures, wheels and logs remain intact. `first-tests.log`
records an incomplete constructed claim fixture; `comment-export-failure.log`
and `source-issue-failure.log` record the two actual retention omissions. The
initial 661-test checkpoint and its metadata-only rebuild precede the final
source-issue correction. Files named `with-issues`, `source-issue` and the final
`wheel-inputs.json` describe the final implementation.

## Remaining work

R18 remains partly open. The command selects an existing accepted or rejected
scan row in a saved run. A completely missed mention, source-only workspace,
dedicated consumer display, report-resolution state and cross-reprocessing
continuity remain separate work. Observations neither change scanner output nor
approve claims. The next R17 comparison should establish whether the available
source and reference evidence improves a concrete discovery task.
