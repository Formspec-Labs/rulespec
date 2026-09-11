# CFR compound names and range consumers

Read-only assessment, 2026-09-11. No production edits, installs, model calls, tests, or commits. The separate part-zero minting change is outside this review.

## Decision

Extend RefSpec's existing CFR grammar and result types, then update the explicit field-copy and single-target consumers together. A larger token regex alone is insufficient: it would preserve `101-19` but still lose the end of `101-19.600 to 101-19.607`. Putting range data only on `CfrCitationOccurrence` would also leave the existing `parse_cfr_citations` consumers unable to distinguish a range from one address.

The smallest complete slice is: native range fields, whole source spans, propagation through `AuthorityCitation` and both Unified Agenda tables, lossless Rulespec reference output, and explicit withholding at consumers that only support one target. Reuse the existing `rkaf:us-cfr` space for supported single compound parts; do not invent a range identifier, enumerate intervening members, or build a second parser/index loader.

## Source evidence and meaning

Started with [the experiment design](../experiments/2026-09-11-cfr-whole-tokens/design.md), [source cases](../experiments/2026-09-11-cfr-whole-tokens/source-cases.json), and [controls](../experiments/2026-09-11-cfr-whole-tokens/controls.json). I also read the original local title-41 XML around byte 354934, using `uv run --no-project python` and a bounded byte read. Under section `51-10.151`, the paragraph says the Architectural Barriers Act requirements, “as established in 41 CFR 101-19.600 to 101-19.607,” apply to the buildings described. The surrounding paragraph establishes a section range, not a single part; the adjacent XML element is itself a reserved section range. This supports retaining written endpoints and rejects treating every XML `TYPE="SECTION"` or `TYPE="PART"` value as one identifier.

Other copied source specimens distinguish the cases that must remain separate:

- `41 CFR Part 60-3`: one compound part in a list of agencies' published regulations.
- `41 CFR parts 102-193 and 102-194`: two compound parts, explicitly linked by `and`.
- `41 CFR parts 300-3, 301-10, and 301-70`: three compound parts.
- `40 CFR parts 1500 through 1508`: a stated part range in an authority note.
- A title-48 paragraph cites `41 CFR part 102-38`: use the cited title, not the containing document's title.
- `5 CFR part 10001`: a real five-digit part; token-length shortcuts must not remove it.

The full source hashes and experiment results were not recomputed in this assessment. These are development cases and inspected source context, not an independent accuracy estimate.

## Current consumers

Paths below are relative to the named repository. “Reachable” means an implementation call chain exists; it does not establish that a build, service, or release is currently running.

| Repository and path | Current behavior and necessary consequence |
| --- | --- |
| RefSpec `src/refspec/registry/citation_grammar.py:1871`, `:1886` | `CfrCitation` has one title/part/section. `CfrCitationOccurrence` adds source coordinates, pinpoints, context, subparts and `subpart_end`; it has no part/section endpoint. Extend these existing types rather than introducing a second family. |
| RefSpec `citation_grammar.py:2603`, `:2648`, `:2706` | Both public readers share `_parse_cfr_citations`. Its collector at `:2730` is the central place to construct complete readings. Preserve that shared path. |
| RefSpec `citation_grammar.py:522`, `:553`, `:2757` | The part capture stops before compound tails. The plural-plus-hyphen heuristic at `:2764` clears the part but retains the shorter match span; it also mistakes plural compound lists for ranges. Replace this heuristic with whole-token recognition and explicit range handling in standard, longhand, and list paths. |
| RefSpec `citation_grammar.py:3701` | **Reachable authority parser consumer.** Copies CFR title, part, section and plausibility into `AuthorityCitation` at `:1943`. New fields must survive this copy; `parse_status="partial"` alone does not tell a downstream consumer which endpoint was lost. |
| RefSpec `src/refspec/registry/unified_agenda_parquet.py:8530` | **Reachable builder consumer.** Uses `list_expansion="always"` for structured fields, then explicitly builds rows at `:8550`. Preserve that field-specific list policy and carry endpoints/status. |
| RefSpec `src/refspec/registry/cfr_authority_notes.py:544`, `:557` | **Indirect authority-parser consumer.** Reduces a CFR reading to a part comparison via `cfr_citation` at `:349`. Dropping a section is deliberate here; dropping a cross-part range is not established by that rationale. Withhold unsupported range comparisons, or explicitly define a supported comparison; never use the first part alone without disclosure. |
| RefSpec `unified_agenda_parquet.py:4440`, `:4498` | The authority-note comparison and held-reference-part lookup also select only `cfr_part`. They must not admit a range as a single corroborating part. Same-part section-range coarsening can remain only if explicitly documented as part-level comparison. |
| RefSpec `src/refspec/registry/term_explanation.py:372`, `:440` | `_explain_cfr_part` takes `citations[0]`, fetches that part's note and describes it as the input's subject. It is reachable from public `explain_term`, but no production caller of `explain_term` was found in these four repositories; tests do call it. Guard ranges and multiple readings before lookup. This is an exposed API, not evidence of a live serving route. |
| RefSpec `src/refspec/registry/iri_minting.py:388`, `:476` | Public `mint_cfr_iri` currently refuses complete hyphen-number parts but accepts a truncated numeric head. No production call site for this function was found in the four source trees. Keep that distinction: the danger is real at its API boundary, but current graph exports use other helpers. Update its single-part grammar and recorded rationale only alongside complete parsing. |
| Rulespec `packages/rulespec-extrapolator/src/rulespec_extrapolator/references.py:76` | **Direct occurrence consumer.** `asdict(match.citation)` preserves added native fields automatically, but `value` is manually rebuilt from the first part/section at `:81`. Prefer `match.text` for the value, as the USC path already does at `:108`; retain native reading, source quotation checks, context evidence and refusals. CFR scanning does not call `mint_cfr_iri`. |
| Rulespec `packages/rulespec-projection/src/rulespec_projection/projection.py:440`, `:705`, `:802` | Public graph-building functions still use the separate `rulespec_projection.citations` parser and `canonical_cfr_iri`. `_cfr_iri` copies typed row fields; `unified_agenda_facts` reparses raw JSON references and immediately produces IRIs. These functions are exported APIs with internal call chains; no non-test caller was found in these four source trees. Updating RefSpec alone will not change them. |
| SpicyRegs `src/spicy_regs/transforms/build_rule_targets.py:213` | **Reachable pipeline consumer of a separate parser**, `spicy_regs.ontology.citations.parse_cfr_citation`, not RefSpec. The pipeline invokes the transform at `src/spicy_regs/pipelines/rulemaking_dataset.py:109`. Its dictionary branch at `ontology/citations.py:632`, prose branch at `:660`, and numeric continuation at `:681` need migration to shared reading or explicit unsupported-token refusal. Preserve the API dictionary and compact-key inputs when doing so. |
| SpicyRegs `src/spicy_regs/transforms/build_proceedings.py:351` | Reads `rule_targets`, keeps the compact reference, then mints from only title/part/section at `:363` using local `canonical_cfr_iri`. This is a real downstream first-endpoint hazard if producer rows merely gain optional endpoints while old consumers ignore them. |
| SpicySearch `src/spicysearch/cfr_citations.py:121`, `:139` | Its `CfrCitation` is a different local type. Strict mode retains compound tokens but refuses them; default mode retains numeric-prefix matching. Direct production callers are `derived_topic_passes/court.py:536` and `presidential.py:505`, both using the default and converting results to part keys. Validation calls the same reader at `validation/cfr_citations.py:69`. These are part-tagging paths, not RefSpec occurrence consumers or CFR IRI minters. Migrate only with their explicit tagging/policy checks. |

Do not conflate these local `CfrCitation` classes merely because their names match. Rulespec and SpicyRegs local `canonical_cfr_iri` implementations accept only numeric parts through `_digits` (Rulespec `citations.py:353`; SpicyRegs `ontology/citations.py:384`). They cannot become compound-aware through a RefSpec release alone.

## Typed rows and export limits

RefSpec's `CFR_REFERENCES_SCHEMA` (`unified_agenda_parquet.py:243`) and `LEGAL_AUTHORITIES_SCHEMA` (`:319`, CFR fields at `:373`) expose strings for part and section, so complete compound names fit without changing their field types. Neither schema contains CFR range endpoints. The writer uses `pa.Table.from_pylist(rows, schema=schema)` at `:9216`; adding keys to Python dictionaries alone does not carry them into these explicit Arrow schemas.

Update all of the following together:

1. `CfrCitation` and `AuthorityCitation` fields, plus the authority copy at `citation_grammar.py:3705`.
2. Both Arrow schemas, reference row emission at `unified_agenda_parquet.py:8550`, and authority emission at `:8930`.
3. `_CITATION_IDENTITY_COLUMNS` at `:787`, otherwise distinct ranges sharing a start compare as the same citation.
4. `_JOIN_CITATION_COLUMNS` at `:5669` and the joined-row copy at `:5813`, otherwise joined authority rows lose endpoints.
5. The index-membership boolean at `:8562`: it currently judges one `(title, part)`. For a range, do not present start membership as membership of the entire range; retain null/explicitly bounded evidence.
6. The existing output schema digests/receipt at `:9208` onward. Regenerate versioned artifacts through the existing builder, not by altering sealed output in place.

SpicyRegs `rule_targets` stores only `cfr_ref`, `cfr_title`, `cfr_part`, and `cfr_section` (`build_rule_targets.py:31`, `:111`). Its deduplication key at `:109` also assumes one reference. A range requires endpoint-aware rows and deduplication, or explicit withholding from the single-target table while preserving raw source evidence and a refusal. Do not write its first endpoint as an ordinary target. Rulespec's graph edge and IRI lists likewise represent single targets; they should withhold unsupported ranges with a note until a range-preserving output is intentionally adopted.

## Recommended implementation sequence

1. Freeze the existing parser as a test oracle and enumerate intended divergences from the source cases. The experiment's `baseline.py` and `compare.py` are evidence/test code, not deployment candidates. Keep existing `tests/cfr_parser_oracle.py` and inherited controls independent of the new grammar.
2. Extend `CfrCitation` with optional part/section endpoints, following the existing `AuthorityCitation.usc_section_end` naming pattern. An occurrence should carry the complete written range and endpoint pinpoints where present. Keep complete source text, context and ambiguity/refusal information; do not label an unsupported token as an ordinary start-only citation. Adding endpoint fields only to the occurrence type is insufficient.
3. Change the shared grammar's token/continuation handling, including keyword spellings. Separate a supported compound part from explicit `to`/`through` ranges and ambiguous hyphen chains. Revisit `_part_is_plausible` at `citation_grammar.py:2110`: summing every digit in a compound token incorrectly rejects `102-117`, which the experiment already exposes. Do not replace this with source-index membership as legal validity.
4. Update every typed RefSpec copy, schema and single-part comparison above in the same implementation slice. Preserve ranges without enumerating them. Guard the explanation API's first-citation selection.
5. Simplify Rulespec's CFR reference value to source text and explicitly propagate any new occurrence-only endpoint details/refusals. Retain `document-references/2` only if its existing compatibility requirements allow the changed reading; validate through its existing tests and consumers rather than create another output schema.
6. Update RefSpec's single-address minter for complete supported compound parts. It takes scalar arguments and cannot detect an endpoint the caller omits. Require range-aware callers to refuse before minting, or extend this existing entry point with explicit endpoint/refusal arguments and test that guard. An optional argument alone does not protect old three-argument callers. Do not encode a range as one ordinary `rkaf:us-cfr` IRI.
7. Migrate the still-active SpicyRegs graph path and exposed Rulespec graph APIs through the shared packaged reader/minter, keeping thin adapters for dictionaries and compact keys. Preserve provenance and withheld outcomes. Avoid a new parallel grammar. SpicySearch's legacy part-tagging paths remain a separate serving/policy change; their existing permissive behavior must not be mistaken for fixed reference scanning.

## Necessary regression cases

- All raw cases listed above, asserting native parts/sections, both written endpoints, exact original codepoint slices and preserved citation-list context.
- `41 CFR parts 50-1 through 50-200`; `41 CFR 101-19.600 to 101-19.607`; an explicit range crossing parts; end pinpoints and a citation immediately after the range.
- `40 CFR parts 60-63`, `40 CFR 60-63`, and `41 CFR 60-1-60-2`: complete source retention and an explicit supported reading or refusal; never silently mint `40:60` or `41:60` as the whole input.
- Compound lists with `and`, `or`, comma/Oxford-comma forms; singular prose `40 CFR part 37, 12 people attended`; structured-field `list_expansion="always"`; neighboring USC/Statutes/FR citations.
- `7 CFR 15a`, `26 CFR 16A`, ordinary numeric parts, five-digit `10001`, historical title 35, impossible/fused titles, Title 3 compilation locators, malformed tails, Unicode prefixes/dashes/spacing. Preserve the separate part-zero test lane rather than redefining it here.
- RefSpec parser → authority row → both Parquet round trips: distinct ranges sharing a start remain distinct; joins and deduplication retain endpoints; range membership is not misreported from the start alone.
- Rulespec scan: complete range value, native reading, source evidence and rejected outcomes survive serialization; no start-only display value. Mutate an endpoint/span to prove the test observes it.
- SpicyRegs source dictionary/prose → rule target → proceeding IRI, and Rulespec graph API: complete compound singletons produce the intended identity; ranges produce no undisclosed first-endpoint identity. Include refusal/evidence assertions, not only an empty output assertion.

## Limits and inherited cost

This assessment does not establish deployed usage, legal existence, applicable editions, exhaustive syntax coverage, or source-index completeness. No dynamic imports or wheel installations were used to infer consumer identity. Public exported functions with only test callers found are called out above rather than declared dead.

Existing costs to keep bounded: RefSpec's `_overlaps_a_read_span` checks every prior span for each keyword candidate (`citation_grammar.py:2754`), making that overlap path potentially quadratic in citation count; SpicyRegs' list deduplication uses repeated list membership (`ontology/citations.py:666`, `:693`), also potentially quadratic. They are inherited, not caused by range support. Range handling should record endpoints in constant extra space per occurrence and never allocate work proportional to the numerical distance between endpoints.
