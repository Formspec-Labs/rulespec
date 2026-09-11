# Compilation citations: bounded improvement, XML source preference

Adopted the existing SpicySearch recognition of page-first Title 3 compilation
citations in RefSpec's shared grammar, then connected exact occurrences to
Rulespec's optional reference and discovery exports. No new dependency, model
field or Core schema was needed. Production changes add 36 net lines in RefSpec
and four net lines in the Rulespec adapter.

`3 CFR 60–61 (1971–1975 Comp.)` now retains both volume years and both page
endpoints. It no longer becomes CFR part 60. No executive order or proclamation
identity is inferred. Repeated occurrences retain separate evidence; an unclosed
parenthetical retains a refusal. The existing year-first forms remain supported.

## Evidence and decision

[Design](design.md), [comparison](comparison.json), [raw case outputs](case-results.json)
and [full corpus changes](corpus-results.json) preserve the comparison. The copied
old checks live in RefSpec's test-only `compilation_parser_oracle.py`.

| Check | Observed result |
| --- | --- |
| Nine contiguous citations in the two saved court opinions | All nine retain complete native and application locators; the old reader returned no compilation locators |
| All 68 opinions in the pinned capture | Nine CFR readings removed, none added, two opinions changed |
| Source spelling, repetition, ordinary parts, nearby references and malformed controls | 141 focused upstream cases pass; deliberate differences are the newly recognized ordering, range endpoints and `Comp` word boundary |
| Publisher USLM XML, title 18 section 798A | Both compilation mentions and all 12 publisher links survive |
| Application suite | 585 pass from source and installed wheels |
| Relevant RefSpec suite | 466 pass from source and installed wheels |
| Saved extraction reprocess and replay | Four accepted, zero rejected, processing complete, zero provider calls |

These are selected development cases and a bounded source comparison, not a
general extraction accuracy rate. The copied old grammar is substituted only
for compilation-span suppression when comparing the otherwise unchanged CFR
occurrence reader. SpicySearch's unchanged strict reader refuses these strings
as compilation locators; the RefSpec API adds the volume/page reading and exact
source coordinates needed by the consumer.

**Decision:** adopt the contiguous-text improvement. The broader source-layout
problem is **not solved**: a tenth printed citation crosses a PDF page boundary,
with a footnote and page header inserted into the saved reading order. Both
readers still interpret the footnote marker as CFR part 9. The original
[gap and surrounding text](page-boundary-case.json), [raw readings](page-boundary-results.json)
and rendered pages 115–116 remain saved. A regex must not jump over unrelated
prose to manufacture adjacency. This is a separately scoped partial adoption,
not a passed end-to-end completeness gate.

## XML where available

Publisher XML is the preferred input when it contains the needed document text
in a supported format. Rulespec already accepts USLM in `prepare`, `extract` and
`references`; use that path directly so source structure and publisher links
survive. The caller currently chooses the format. This work adds no generic XML
reader or automatic source fetcher, and establishes no XML counterpart for the
court opinions.

[Original section bytes](title-18-s798A.xml) were captured from the pinned publisher
archive and wrapped in its original `uscDoc` opening tag.
[Hashes and source offsets](xml-source-pin.json) retain the exact provenance.
The two compilation mentions occur in the operative text and an editorial note.
The note says the printed proclamation number probably should be another number;
the prepared document preserves that uncertainty, and the locator chooses neither.
[XML output](xml-results.json) retains the readable text, source map, publisher
links, occurrence evidence and discovery export.

Constructed XML controls check that citation-like attributes do not become
visible references and a differing publisher target survives alongside its text
reading. The first test used an invented `/us/cfr` href, which the existing USLM
reader explicitly rejects. That fixture error remains in `xml-tests-01.log`;
the corrected control uses a supported identifier family. Generic href support
was not added to make the test pass.

## Remaining limits and delivery

The older `AuthorityCitation` output is still marked `partial` and carries only
the compilation start year and first page. Its existing Parquet consumer lacks
endpoint fields. The new occurrence API and both Rulespec exports retain all
endpoints; this change does not claim to fix the older metadata row format.
Compound CFR parts and graph-reader migration remain open under R8; PDF reading
order remains open under R23.

[Wheel inputs](wheel-inputs.json) pin all seven local packages. The installed
check compares every Python file in those wheels with its installed bytes and
compares RefSpec, the extractor and projection files with their source trees.
CLI checks run from `/tmp` with an empty `PYTHONPATH`; publisher XML outputs match
the direct-source result. The isolated and working environments produce the same
reference/discovery data. Dependency checks pass in both environments. Original
model captures remain unchanged. No model call, push, publication or deployment
was performed.

The initial application-test failure used a nonexistent discovery-output key;
the corrected test checks the existing shared evidence table. Both attempts are
preserved. Initial build logs and wheels predate the README update; the final
wheel receipt identifies the installed builds. Logs distinguish source tests,
installed tests and CLI verification rather than merging their results.
