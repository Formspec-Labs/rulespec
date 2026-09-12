# Operating reference

Start with [extraction and discovery](README.md). Commands run independently;
references and context exports enter a model request only when a caller explicitly
supplies them. Normal extraction does not call audit, refinement or enrichment.

## Choose an operation

A window is the input slice planned by that operation; extraction and audit have
different default window sizes. Counts below assume successful setup, no reuse and
no interruption. Each model request is retained; there are no automatic retries.

| Command | Input → output | Model calls | Review history | Use |
|---|---|---|---|---|
| `prepare` | Text or supported XML → pinned document JSON | 0 | Unchanged | Set title/source URL or inspect prepared text |
| `extract` | Source or prepared JSON → new run and rulebook | 1 per window | Creates an unreviewed base | Produce the first draft |
| `discovery-export` | Current workspace → passages, statements and evidence | 0 | Unchanged | Feed search/tagging; retain unextracted passages |
| `usage` | Capture directory → recorded token counts | 0 | Unchanged | Inspect consumption; missing usage stays unknown |
| `references` | Source or saved run → supported citation readings | 0 | Unchanged | Locate mentions and optionally supplied target bodies |
| `context-export` | Statement ID or source span → bounded source context | 0 | Unchanged | Inspect surrounding and linked material |
| `serve` | Run and optional saved audit → local browser workspace | 0 | User edits append events | Inspect and correct a draft |
| `review` | Workspace and action JSON → revised workspace | 0 | Appends events | Apply explicit corrections or observations |
| `reference-feedback` | Workspace and saved reading → observation | 0 | Appends an event | Record a disputed citation reading |
| `export` | Workspace → validated current rulebook | 0 | Unchanged | Export corrections before auditing |
| `evaluate` | Rulebook, labels and optional judgments → assessment | 0 | Unchanged | Check recorded judgments, not generate judgments |
| `audit` | Rulebook → inventory, judgments and findings | 2 per window | Unchanged | Identify possible omissions and meaning errors |
| `refine` | Workspace and optional matching audit → proposed/applied corrections | 6–8 per window; matching audit saves 2 | Appends supported AI edits and observations | Optional recovery and qualification links |
| `enrich` | Workspace → actor/term suggestions and corrections | 1 per nonempty window | Appends AI edits and observations | Fill missing actor/definition structure |
| `replay` | Saved extraction → verified reproduction | 0 | Original unchanged | Check captured processing with matching runtime |
| `reprocess` | Saved extraction → new result under current code | 0 | Original unchanged; new run is unreviewed | Apply a parser/compiler change to saved responses |
| `audit-replay` | Saved audit → reproduced assessment | 0 | Unchanged | Check captured audit processing |
| `refine-replay` | Saved refinement → verification result | 0 | Verifies captured history | Check proposals, challenges and applied events |
| `enrich-replay` | Saved enrichment → verification result | 0 | Verifies captured history | Check structural edits and refusals |
| `vocabulary` | Rulebook and optional RefSpec snapshot → suggestions | 0 | Unchanged | Suggest vocabulary identities without asserting equivalence |

Refinement runs an initial audit, recovery proposals, relationship proposals and a
final audit. Each proposal stage adds a source challenge only when valid proposals
exist. Counts scale with its own windows, not necessarily the extraction windows.
An audit is diagnostic; neither source grounding nor agreement between model passes
establishes complete or correct meaning.

## Settings and advanced examples

From the repository root, the existing experimental environment exposes
`.tools/document-poc-venv/bin/rulespec-understand`. With its `bin` directory on
`PATH`, run:

```sh
rulespec-understand prepare manual.txt --title "Manual section" \
  --source-url https://example.org/manual --output prepared.json

rulespec-understand extract prepared.json --model gemini-3.8-flash \
  --thinking-level low --temperature 0 --max-chars 24000 \
  --max-output-tokens provider --env-file /path/to/local.env --output my-run

# Optional: inventory the source before comparing it with the extracted draft.
rulespec-understand audit my-run/rulebook.json --model gemini-3.8-flash \
  --thinking-level medium --max-chars 24000 --max-output-tokens provider \
  --env-file /path/to/local.env --output my-audit

# Retain source passages and links, including passages without an extracted rule.
rulespec-understand discovery-export my-run --output discovery.json

# Optional: locate supported external references in those source passages.
# Requires the verified SpicySearch and RefSpec wheels described below.
rulespec-understand discovery-export my-run --references --output discovery-with-references.json

# This also works before extraction, with no model calls.
rulespec-understand references prepared.json --output references.json

# Provider-reported token counts, separately from local JSON storage.
rulespec-understand usage my-run

# Reproduce the saved processing without provider calls.
rulespec-understand replay my-run --output my-replay
rulespec-understand audit-replay my-audit --output my-audit-replay
```

Supply `GEMINI_API_KEY` through the environment or the explicitly selected env
file. Each new run needs a new output directory. CLI and library calls default to
low extraction and medium audit. This promotes the operating recommendation; the
recent experiments did not compare these levels against the provider's implicit
default. The recipe above also explicitly increases the audit window and removes
application output caps, which remain separate from the thinking defaults:

| Setting | Extraction default | Audit default | Recipe above |
|---|---|---|---|
| Focus characters | 24,000 | 3,000 | 24,000 for both |
| Generation allowance | 16,384 tokens | 32,768 tokens | provider limit |
| Thinking level | low | medium | low / medium |
| Temperature | 0 | 0 | 0 |

`--max-output-tokens provider` omits the application's cap; provider limits still
apply. `--thinking-level` accepts low, medium or high and sends no numeric
`thinking_budget`. Python callers can explicitly pass `thinking_level=None` to
use the provider default. Saved requests retain their recorded setting during
replay and reprocessing. Requests allow up to five minutes, with no automatic retries.
Settings and actual SDK requests are recorded and checked during replay. Fresh
calls can differ even at temperature zero.

See [installation](README.md#installation) for a fresh environment.

For source iteration, set `PYTHONPATH=packages/rulespec-extrapolator/src` when
running its tests or importing its tools. After those checks pass, build wheels
and test a fresh installation outside the checkout:

```sh
uv build --project packages/rulespec-artifacts --wheel --out-dir dist/document-understanding
uv build --wheel --out-dir dist/document-understanding
uv build --project packages/rulespec-projection --wheel --out-dir dist/document-understanding
uv build --project packages/rulespec-extrapolator --wheel --out-dir dist/document-understanding
uv venv --python 3.12 /tmp/rulespec-wheel-check
uv pip install --python /tmp/rulespec-wheel-check/bin/python dist/document-understanding/*.whl
uv pip check --python /tmp/rulespec-wheel-check/bin/python
```

Use a new directory if that test environment already exists. Run its CLI outside
the checkout with `PYTHONPATH` unset, and confirm imports resolve to `site-packages`.
Keep compatible dependency versions when comparing a saved run: strict replay
checks runtime versions as well as captured files. A working editable environment
alone does not establish that its dependencies are compatible or its wheel is complete.

## What goes in, what happens, what comes out

### Optional reference recognition

`references` scans exact source text for explicit Code of Federal Regulations
(CFR) and U.S. Code (USC) citations, public laws, Statutes at Large citations, executive orders,
dockets, and Regulation Identifier Numbers (RINs). It accepts
text, a prepared document, rulebook JSON, or an extraction directory. It reads
the document once and preserves repeated occurrences separately. Each candidate
has its display value, exact quotation and Unicode codepoint offsets, an
existing Rulespec fragment ID, and the IDs of overlapping source passages.
USC display values preserve source spelling; the native `reading` fields and
inherited context describe the normalized target. Other kinds retain their
existing normalized display values.

`discovery-export --references` runs the same adapter against the current review
snapshot's pinned document. It adds `reference_scan` and reuses the export's
shared evidence table. It also finds references in passages with no extracted
statement. It does not change statements, prompt fields, review history, existing
reference links, or default exports. These commands make no model calls.

With `--act-index`, the same commands also recognize indexed named-act sections
and consult RefSpec's existing classification tables. The optional source-credit
index adds its independent resolution evidence. Each index is verified by its
own upstream loader; the output records its files and digests.
RefSpec also reads the act index's retained page-uncertainty table. A shortened
or unknown page cannot prove that a classification lies outside an act's division.

```sh
rulespec-understand references prepared.json \
  --act-index ../RefSpec/output/usc-act-index-2026-08-22 \
  --source-credit-index ../RefSpec/output/usc-source-credit-index-2026-08-02 \
  --output references-with-acts.json
```

These options also work on `discovery-export`; supplying an act index enables
the reference scan. Repeated mentions keep their own evidence. A reading such as
`Section 111(d) of the Clean Air Act` retains `(d)` separately from its mapped
U.S. Code section. RefSpec does not establish that the code uses the same
subsection letters, so the output explicitly reports `pinpoint_mapping=not_performed`.
Unknown names remain unrecognized; known acts with unclassified sections retain
the native unresolved reason. The supplied indexes may describe later editions
than the input document. No target body, matching historical edition, or legal
applicability is established by this lookup.

The adapter reuses RefSpec's `find_cfr_citations`, `find_usc_citations` and SpicySearch's
`detect_identifiers`, restricted to the five additional kinds above. CFR readings
retain native title/part/section fields, validity flags and attached subsection
labels. For `40 CFR §§ 82.155(a), 82.156(b)`, each member has its own occurrence;
the abbreviated second member also cites the written title-bearing context.
Both accepted and rejected readings use the discovery export's shared evidence.
CFR display values retain the original source spelling. The reader also connects
`§ 1954.3(d)(1)(i) of title 29, Code of Federal Regulations` to its written
title, section and pinpoint. Lists retain separate occurrences and shared title
evidence; a complete single citation needs one quotation. This does not infer
titles for bare references from document headings or filenames.
A compound part such as
`41 CFR 102-193` stays one part. A range such as
`41 CFR 101-19.600 to 101-19.607` stores separate `start` and `end` coordinates,
including attached endpoint labels. It never becomes a single first-part target
or a generated list of intermediate provisions. Incomplete endings and ambiguous
hyphen chains retain their full observed wording under an explicit refusal.
RIN candidates also use RefSpec's `mint_rin_iri` to check Rulespec's supported
identifier space. Values outside it retain their exact evidence under `rejected`
with `rin_outside_supported_identifier_space`. This removes lexical lookalikes such
as the amendment heading `1998—Pars.` without changing SpicySearch query parsing.
It is not an existence check: some published RIN values fall outside the supported
space, and a matching product code can still be a false candidate.
Subpart lists retain individual targets, literal connectors and parenthetical
context. For `49 CFR Part 172 subpart E (labeling) or subpart F (placarding)`,
the two readings preserve E/F and the written `or`; the second reuses the first
reading's source context. An appendix to a subpart remains an appendix target.
Stated subpart ranges retain their endpoints without generating intermediate
members. A subpart list following multiple parts is refused as
`cfr_ambiguous_part_scope`, with its partial reading and evidence retained.

USC readings preserve section and range-end subsections, chapters, subchapters,
appendices, notes and the basis for an abbreviated range. `19 U.S.C. 1484-86`
keeps that written display value; its reading exposes endpoints 1484 and 1486
with `usc_section_span_rule=abbreviated-span`. No interior sections are generated.
Repeated mentions keep separate evidence. Listed members cite their inherited
title context, and the prose list stops at intervening text. Invalid titles,
damaged tokens and unresolved qualifications retain explicit refusal codes.
A positioned note such as `42301 preceding note` stays refused rather than
becoming a plain section. Open-ended forms such as `38 U.S.C. 4301, et seq.`
retain their full wording with `usc_open_ended_reference_unresolved`; the reader
does not infer an ending section. These readings do not establish target existence.

Title 3 compilation citations retain their volume years and page endpoints.
`3 CFR 60–61 (1971–1975 Comp.)` yields a compilation locator, with pages 60–61
and years 1971–1975. It does not identify CFR part 60 or infer an executive order.
The existing year-first spelling is also supported. Repeated mentions stay
separate, and an unclosed parenthetical retains an explicit refusal.

Rulespec's existing document validation, exact evidence resolver, fragment identity
and passage index provide grounding; no new citation grammar or Core assertion
type is introduced. A mention is not a resolved target, an applicability judgment,
or a complete representation of every possible qualifier.
Document-local paragraph recognition remains outside the text scanner's scope;
the USLM path below also retains publisher-supplied links.
Unsupported kinds are excluded. A candidate or required title context crossing
inserted source-map text is recorded under `rejected`; native impossible-title or
implausible-part readings retain their flags and evidence there. When source
grounding also fails, `parser_refusal` preserves the upstream reason alongside it.
Invalid source identity, parser coordinates or a parser quotation that differs from the source
fail the scan. An empty candidate list does not establish completeness.

SpicySearch and RefSpec are optional application dependencies (`references` extra),
never Core validation dependencies. Use compatible, pinned builds in the same
Python environment as the extractor. Check actual wheel/module digests as well as
versions, since local builds can share a version. The
[historical installation receipt](EVIDENCE.md#historical-optional-reader-installation-checkpoint)
records a tested dependency set; it is not an instruction to replace newer builds.
SpicySearch's dependency metadata also installs DocSpec, but Rulespec's semantic
segmentation and Core validation do not call it.

Optional provision lookup reuses RefSpec's native XML reader and section-address
helpers. Supply captured USLM or eCFR XML, or a prepared document, to either command:

```sh
rulespec-understand references prepared.json --reference-source usc05.xml --output references-with-text.json
rulespec-understand discovery-export my-run --reference-source usc05.xml --output discovery-with-text.json
rulespec-understand references section.xml --reference-source title-49.xml --output cfr-with-text.json
```

Repeat `--reference-source` to supply additional sources or editions. The Python
APIs accept prepared documents through `reference_sources=[document, ...]`.
Exact accepted USC sections/pinpoints and publisher links can locate targets
inside supplied sections. Exact CFR sections can also resolve when the supplied
eCFR XML contains native `TITLE` ancestry. A bare eCFR `SECTION` is readable input,
but cannot supply a title for external lookup. CFR pinpoints, ranges, subparts and
appendices do not fall back to a whole section. Each target retains its XML selector, digest and source
identity. `reference_sources` stores publication metadata and containing section
records once; `target.record_id` selects a record, and target offsets address that
source's prepared text. For a record-local slice, subtract `record.start`.
Discovery stores external evidence in that source's own `evidence` table.

Matching text in a supplied release does not establish the citation's intended
edition: `edition_match` remains `not_established`. Multiple target versions remain
ambiguous. Open-ended citations, ranges and notes are not reduced to plain section
anchors; broad external title/chapter bodies return `target_scope_not_supported`.
Containing sections preserve parent conditions and editorial notes for reading,
without deciding their legal effect. This adds no model call, prompt text or
recursive fetching. Format detection distinguishes USLM and eCFR native XML.
The [reader comparison](../../thoughts/experiments/2026-09-11-ecfr-text/README.md)
records the source-preservation checks and current delivery status. Full-title
inputs use substantial memory: the saved Title 40 reader check peaked near 3.4 GB.
Each lookup scan builds one index per distinct supplied source and shares targets
across mentions; it does not reparse the full title per citation. Preparation and
later source verification are separate reads.

Prefer publisher XML when it contains the required document text in a supported
format. Supply that XML directly instead of first flattening it to text or
extracting a PDF copy. Format selection is currently the caller's responsibility.

`context-export` brings this evidence back to one extracted statement or selected
passage. It assembles current neighboring context, a complete short enclosing
section, directly linked statements, uniquely located reference targets and
relevant saved reference feedback. Repeated targets share text; separate sources
keep separate coordinates. Missing targets, competing editions, and omitted
context remain explicit. This export makes no model calls and changes no meaning
or review decisions.

```sh
rulespec-understand context-export my-run --claim CURRENT_CLAIM_REVISION_ID \
  --reference-source usc05.xml --output statement-context.json

# A prepared source selection also works before extraction.
rulespec-understand context-export prepared.json --span 100 400 \
  --reference-source usc05.xml --output passage-context.json
```

The same optional act/source-credit index flags work here. `--span` uses half-open
prepared-text positions. `--extra-chars` defaults to 20,000 additional unique source
characters beyond the selected statement and its existing context; whole additions
that exceed the allowance are skipped with a reason. An enclosing section is added
only when at most 12,000 characters; a referenced provision gains its containing
section when at most 6,000. Expansion follows references in the original selection
only. A whole section may contain editorial or historical notes; selection does
not establish that any supplied text governs the statement.

The output separates readable `material` from the selected original `documents`,
the full `reference_scan`, and complete relevant feedback `observations`. Source
metadata is shared by source ID. The current review
revision, rulebook fingerprint and exporter fingerprint identify the input and code.
For application use, `context.export_context(book, focus, ...)` builds the same
data; `context.resolve_context({"source": "S1", "passage": "F009:F011"}, result)`
returns exact original-source evidence using the appropriate document's resolver.
Existing `ReviewStore` observations and revision-checked edits remain available
for recording subsequent findings or corrections.

The [fixed-question experiment](../../thoughts/experiments/2026-09-11-integrated-context-check/RESULTS.md)
recovered additional meaning in three of four selected natural cases, but failed
its promotion gate: one answer invented an actor restriction, and integrated
requests used 2.15× baseline reported tokens. The automatic model check and meaning
corrections remain experimental; the evidence export alone is available here.

With these packages, `prepare`, `extract` and `references` accept USLM and eCFR `.xml`
files. RefSpec supplies readable heading/list/table boundaries; Rulespec retains
the original UTF-8 XML and maps prepared text back to it. Inserted separators never
become source quotations, and raw XML attributes stay out of model prompts.
`references` and `discovery-export --references` expose publisher links and a shared
table of targets present in the supplied XML. Each occurrence keeps XML evidence,
visible text when present, and its operative/source-credit/note context. Empty
links retain XML evidence; duplicate target identifiers remain ambiguous. Targets
outside the selected XML remain unresolved. This provides source navigation, not
a decision that the target governs the current rule.

Text-parser readings associated with a publisher occurrence retain their own
evidence and refusals. A reading associates only when exactly one publisher label
fully contains it. Nested ambiguous associations and boundary-crossing mentions
remain separate; association does not establish target agreement. The
[containment comparison](../../thoughts/experiments/2026-09-11-reference-containment/README.md)
records the four resolved overlapping rows and its counterexamples. The earlier
[source-preparation record](../../thoughts/experiments/2026-09-11-uslm-readable-text/README.md)
preserves that delivery's original findings. General XML formats, full visual
table layout and automatic reference-context interpretation remain outside this
reader's scope.

Year-first indexed act names retain their original source
spelling. Multi-target source credits retain native target records, and conflicting
sources retain both identifiers without selecting either. These details appear
only when present; ordinary results gain no empty fields. Multiple source-credit
targets prevent selecting a lone Table III answer; its identifier remains a
`table3_candidate_iri` alongside the alternatives. Known complete pages outside
the act's conservative division bounds are excluded even for a single row.
If a popular name identifies multiple laws or scopes, `name_sources` preserves
the paired source records and `candidate_resolutions` retains each compatible
lookup. The parent result says `act_name_ambiguous` and selects no USC identifier.
A stated division can narrow those candidates; missing division information does
not exclude a source record. `act_division` exposes the division used by a lookup.
The written citation appears once in the application output. Ordinary names gain
no candidate arrays. The [earlier policy comparison](../../thoughts/experiments/2026-09-11-act-resolution-policy/README.md)
retains its previous checkpoint.
The earlier [source-credit comparison](../../thoughts/experiments/2026-09-11-source-credit-consumption/README.md),
[subpart comparison](../../thoughts/experiments/2026-09-11-cfr-subparts/README.md),
[CFR integration](../../thoughts/experiments/2026-09-11-cfr-integration/README.md)
and [act-index integration](../../thoughts/experiments/2026-09-11-act-index-reuse/README.md)
retain their original builds, failures and counterexamples.
Missing parser installation raises an error when requested, rather than silently
returning no matches. Default extraction and discovery need neither parser package.

**Input:** UTF-8 text, USLM XML, or prepared JSON with exact text, its SHA-256 digest and
named section coordinates. Newlines remain intact; offsets count Unicode
codepoints in half-open intervals, `text[start:end]`. Optional source maps
identify inserted separators. Preparation does not discover a manual's section
hierarchy. PDF, OCR and layout extraction are outside this package.
Discovery retains prepared passage text and stable passage IDs while limiting
source evidence to the original-source slices. Inserted headings or separators
remain readable but are not cited as original evidence.
Complete statement and component quotations may cross inserted whitespace: their
whole coordinates stay on the claim, while existing evidence bindings retain all
original-source pieces. Inserted non-whitespace remains unsupported. Review checks
require the complete evidence group, and passage ranges still refuse unseen text.
Inventory, audit comparison, and refinement use the same Core evidence check:
formatting-only whitespace may join original pieces, while inserted words and
formatting alone cannot support a judgment. The selected text and offsets remain
unchanged, and the saved document retains the source map needed to recover those
pieces.

**Processing:** the application indexes paragraphs and list items, plans bounded
windows, and supplies parent/neighbor context. Fitting list groups stay together;
larger groups can split. Structural parents are clues, not proven governing
conditions. The model emits complete statements, kind, modal force and source
references using the CUE-generated schema. Scope, choice and other enrichment are
optional. LangExtract supplies its Gemini
adapter; Rulespec supplies evidence resolution, validation, identities and Core
records.

`unit` selects a focus passage such as `F003` or a contiguous range such as
`F003:F009`. Supporting fields can also select context passages (`C000`). The
application resolves those selections to exact original text. `logic_quote`
becomes verbatim `logic_text`; model `statement` becomes candidate `summary`.
One passage can support several meanings or alternatives. Every option and
qualification must still survive in the explicit meaning; a quotation alone is
not proof of semantic completeness.

Omitted or null model enrichment becomes an empty string/list in the existing Core
record shape; the raw capture preserves what the model actually emitted. Separate
scope, choice or logic fields are not required to repeat a complete statement.
Audit input omits empty fields and replaces exact catalog quotations with passage
references while preserving every populated meaning field and its role. Saved
evidence, review history and source text remain complete.

Invalid main references refuse a row. Invalid supporting references withhold the
component and preserve the statement, raw suggestion and field-specific refusal.
Schema and kind/modality contradictions can reject candidates. The application
does not silently guess replacements. Optional component uncertainty can remain
on accepted records.

**Output:** `rulebook.json`, a Core JSON-LD graph, exact source, requests,
responses, candidates, refusals, validation results and frozen runtime inputs.
The `rulespec-discovery/2` export stores source text once in ordered `records`,
statements once in `statements`, definitions in `terms`, and shared source offsets
in `evidence`. Each `evidence_refs` entry identifies a shared span and its support
roles. Concatenating record text reconstructs the pinned source; slicing its
`start:end` retrieves any evidence quotation. Statements carry both `rule_id`
(logical identity) and `id` (immutable revision); term IDs survive editorial
corrections. Empty optional fields and choice/logic text identical to the statement
are omitted from this consumer export. Original captures and review history stay
complete. Existing list parents and note markers are retained as structural clues,
not inferred governing conditions. Export makes no model calls or embeddings.

The browser review groups overlapping verified evidence into one source passage.
Role buttons highlight each original interval without repeating its quotation;
identical words at distinct source positions remain separate. This changes only
presentation, not saved evidence or model input. Run its focused checks with
`node --test packages/rulespec-extrapolator/tests/review_evidence.test.cjs`
from the repository root.

**Audit:** a separate source-first inventory selects focus passage IDs for each
observation and focus/context IDs for its scope. The existing resolver turns these
into exact source text and offsets; invalid selections refuse the observation.
A subsequent draft comparison selects `source_refs` using the same CUE-generated
passage references and resolver. Full selected source passages and governing
context are retained with exact offsets. Invalid or unavailable selections are
refused; a valid ID alone does not prove relevance. Comparison produces raw judgments, a detailed report and existing Core `Finding` records in
`findings.jsonld`. It does not modify the draft. Inventories and judgments remain
fallible observations; missing or invalid inventory entries limit what was checked.

## How to interpret the checks

| Result | What it establishes |
|---|---|
| Accepted candidate | Passed compiler checks; meaning may still be wrong |
| Exact evidence | The cited text exists at the saved offsets |
| Schema / SHACL validation | Records and graph satisfy structural constraints |
| Processing complete | Planned work reached its recorded terminal outcome |
| Review complete | Audit judgments passed its accounting and consistency checks |
| Covered inventory units | The checker assessed those accepted units as covered |
| Identical replay | Saved responses reproduce the same processing results |

None establishes that every source meaning was discovered. Read `audit_issues`
and `review_complete` before interpreting coverage counts: the final example
marks 20 accepted units covered while four substantive inventory entries were
refused. It is not 100% source coverage. No check emits a `ClosureClaim`.

The [qualification regression cases](evaluation/qualification-regressions.md)
retain missed overrides, incomplete permissions, and coverage-link mistakes from
recorded provider outputs, with source review and counterexamples for future
evaluations. These are development cases, not an independent accuracy benchmark.

## Review, refinement and changed runtimes

```sh
rulespec-understand serve my-run --audit my-audit
rulespec-understand review my-run --action correction.json
rulespec-understand export my-run --output reviewed-rulebook.json
rulespec-understand evaluate reviewed-rulebook.json --labels expected.json \
  --judgments judgments.json --output evaluation.json

# Explicitly apply the installed parser/compiler to saved responses.
rulespec-understand reprocess my-run --output my-reprocessed-run

# Optional model-proposed recovery and qualification links, with source checks.
rulespec-understand refine my-run --output my-refinement \
  --env-file /path/to/local.env
rulespec-understand refine-replay my-refinement --output my-refinement-replay
```

Review supports add, edit, split, merge, reject, approve and observe, recording the reviewer,
reason and expected revision. SQLite preserves review history. Approval records
an assessment; assertions remain `reviewQueueOnly`. See the
[review action examples](../../examples/document_understanding/manual-slice/review-demo/README.md).

Reference feedback uses the same history. Save the scan you inspected, select its
zero-based candidate index (or use `--rejected`), and supply the current review
revision from `export` or the review workspace:

```sh
rulespec-understand references my-run --output reference-scan.json
rulespec-understand reference-feedback my-run --scan reference-scan.json \
  --candidate 0 --expected-revision 0 --actor "Review user" \
  --rationale "Please check the cited section and its edition."
rulespec-understand discovery-export my-run --references --output discovery-with-feedback.json
```

The command preserves the comment, selected reading, source evidence, reader/index
pins, supplied-source diagnostics and referenced target context. Repeated mentions retain separate positions;
refused readings retain their reasons even when they have no accepted reference ID.
Discovery includes the observations under `enrichment_issues`, with their event
IDs. A later scan can differ while the earlier observation remains unchanged.
Feedback records a reported problem; it does not approve claims, modify scanner
output or resolve the report automatically. The operation uses an existing saved
run and makes no model call. Its Python helper is
`reference_feedback.reference_observation(document, scan, collection, index, message=...)`;
the returned observation can also use the existing `review --action` route.

Export the current review state before auditing corrections. Refinement appends
AI-attributed review events only after local checks and a separate model challenge;
it preserves refused proposals. It performs bounded recovery, qualification-link
and final-audit passes, with at most 60 current claims and eight proposals per
focus group. `--audit` can reuse an assessment only when it matches the current
snapshot. Audit/refinement results remain specific to the recorded source and settings.

Refinement challenges use the same CUE-derived passage-reference schema and exact
source resolver as the audit. The model selects supplied passages; Rulespec records
their original text and offsets with the judgment. This avoids quotation-copying
errors without introducing whitespace or fuzzy matching. Proposal quotations still
require exact grounding. The [integration check](../../thoughts/experiments/2026-09-10-challenge-source-refs/README.md)
retains the live railroad result and refusal controls; reference validity alone
does not establish that a judgment is correct.

Existing exemptions use a compact `link` proposal containing the current claim
alias, target aliases and rationale. Rulespec copies the existing CUE-derived
meaning fields and original evidence, retains existing links, and runs the normal
preview, source challenge and review edit. Other qualification additions/edits
still carry their complete fields. Links cannot rewrite an exemption, silently
remove existing targets or bypass current-record/revision checks. See the
[integration check](../../thoughts/experiments/2026-09-10-compact-link-integration/README.md).

Withheld refinement proposals remain visible as model assessments in review and
discovery issues. They retain their proposed targets, source judgment and request
provenance through the existing `observe` history action. They do not change claim
meaning or approval. Observations about superseded claims stay at document level;
Rulespec does not silently attach them to a replacement. Replay checks these
observations against the saved proposal and source judgment.

Strict replay checks saved artifacts and runtime fingerprints and refuses drift.
Reprocessing preserves the original capture and records the changed processing;
it supports the current response format, not retired formats. Recorded compiler
failures can be reprocessed when both run and validation metadata identify the
failure. Missing outputs from a nominally successful run remain an integrity error.
Audit version 4 uses passage IDs in inventory and comparison. Earlier captures
require their frozen historical runtime. Old experiments retain that runtime; do not rewrite their manifests
to make an older capture pass under newer code.

## Schema ownership and reuse

The [CUE application profile](src/rulespec_extrapolator/schema_data/document-understanding.cue)
owns interpretation fields, descriptions, titles and field order. Native CUE
produces five views of shared definitions: `provider.schema.json` for normal
extraction, `meaning.schema.json` for complete defaults/refinement and audit field
guidance, `candidate.schema.json` for local validation, and `inventory.schema.json`
for audit evidence selection and observations, plus `enrichment.schema.json` for
actor and definition additions to existing claims. Python does not
maintain a competing copy of those field definitions.

The profile imports existing Core attribution, assignment-role, datatype and
period definitions. The application reuses Core assertions, evidence bindings,
`ApplicabilityScope`, provenance, review records and `Finding`; shared evidence
and release-digest helpers come from Rulespec packages. Fix shared definitions
upstream when needed. The [schema usage assessment](../../thoughts/reviews/2026-09-07-document-understanding-schema-usage.md)
records connected and unused capabilities.

Full meaning records support optional concepts, source claimants, typed values
and effective periods. They create existing Core records only when their source
and value checks pass. Local concepts have document-local identities and do not
claim RefSpec registration. Date-only effectivity does not invent a timezone;
relative deadlines are not periods in force. These richer collections are not
requested by the normal meaning-first pass.

Rulespec requires no DocSpec or SpicyRegs service or release. RefSpec is the only
optional platform integration. `vocabulary` accepts a normalized versioned
snapshot containing `source: RefSpec`, `release_id`, and `concepts` with `id`,
`label` and `aliases`. It matches actor/object labels, records ambiguity and pins
digests; it does not fetch/authenticate a RefSpec release or assert equivalence.
Normal extraction supplies supported actors; object components still require
enrichment or review before vocabulary matching.

```sh
python tools/build_extraction_schemas.py
python tools/build_extraction_schemas.py --check
.tools/document-poc-venv/bin/python -m pytest \
  packages/rulespec-extrapolator/tests tools/test_extraction_schemas.py -q
```

Generation needs Go 1.25 or newer. Installed extraction/replay load packaged JSON
and need neither Go nor CUE. Hashes bind sources, generated files and each run.

## Actors and defined terms

New extraction requests include actor assessment and a document-local definition
index. `defined_terms` stores source-backed names and aliases on defining claims;
`term_refs` links uses to those definitions. These become existing Core
`LocalConcept`, `ConceptScheme`, `RelationshipAssertion`, and `EvidenceBinding`
records. They do not declare matching labels or acronyms globally equivalent.
Term identities persist across wording, name and alias corrections. The review
editor's **Replace this sense** control creates a new identity; API callers remove
the term's `id` when submitting that replacement. Rejected or explicitly replaced
definitions leave previous uses visibly unresolved, retaining the former name.
Historical descriptions, assertions and review decisions remain available.
`term_refs` represents explicit uses of a defined sense, not background topical
association. A definition uses `defines` without a redundant self-use relationship.

For an existing draft, add structure without rewriting its meaning:

```sh
rulespec-understand enrich path/to/review-workspace \
  --env-file path/to/credentials.env --output path/to/new-enrichment-capture
rulespec-understand enrich-replay path/to/new-enrichment-capture \
  --output path/to/new-replay-result
```

`enrich` fills empty actor fields and adds missing definition/reference list entries
through ordinary AI review edits. Existing wording and conflicting populated
components remain unchanged. Withheld or conflicting suggestions become recorded
observations and Core Findings, visible on the assessed revision; a later correction
supersedes that revision while retaining its observations in history. Document-level
provider failures stay visible separately. New revisions need their own review;
prior approvals remain in history. AI revisions retain the captured model version,
request fingerprint, fixed-claim input fingerprint and capture location.
The capture retains requests, responses, component refusals, before/after snapshots
and every applied action. Replay verifies these without contacting the model.
The review UI edits defined names, aliases and uses, shows component changes in
history, and identifies unavailable definitions by name. Discovery
exports retain the same structure and flag unavailable definitions.

The [fresh-source comparison](../../examples/document_understanding/fresh-structure-check/README.md)
found 16 definitions and 17 actors with both approaches on two regulatory section
bundles. The separate pass used 55% more total tokens. This supports a cost choice,
not a complete-meaning guarantee: a subsequent live passport extraction repeated
the known loss of a local-modification qualification from a standalone requirement.
Fixed enrichment preserved all 14 existing passport statements while adding six
actors and two definitions. Keep the full source and related permission available.

Definition links are resolved within each source window, including its supplied
context. Cross-window/cross-document sense reconciliation remains future work;
the resolver does not guess from matching words. Exact evidence verifies location,
not correct actor roles, term senses, or complete coverage.


## Research evidence

See the [evidence index](EVIDENCE.md) for historical experiments and their limits.
