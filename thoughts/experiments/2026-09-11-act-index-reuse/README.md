# Named-act references reuse RefSpec's real indexes

Rulespec now optionally recognizes named-act sections and looks up their U.S.
Code section identities through RefSpec. The recognition fix lives in RefSpec;
the application calls its occurrence reader, `ActIndex`, `SourceCreditIndex` and
resolver. Existing source evidence, passage IDs, discovery exports and sparse
records carry the result. There is no new name registry, model pass or Core schema.

## What the comparison established

Both local indexes loaded through their existing integrity checks: 13,560 indexed
names, classification rows for 15,189 enacting laws, and 2,202 source-credit keys.
The saved raw index rows support the development control mapping Clean Air Act
section 111 to `urn:rkaf:us:usc:42:7411` in those supplied artifacts. This is an
index reading, not proof of the provision's content or applicability in 1995.

Across the eight preselected publication fields, named-act recognition increased
from **5 to 7 fields**; **three mappings** remained available. The two added
crop-insurance readings retain `(b)(7)(A)` and an explicit
`act_section_not_classified` result. The parser does not invent a target to improve
the count. The FY-1995 NDAA spelling remains unknown to this supplied name set.

The diagnostic controls exposed and corrected distinct representation problems:

| Input | Before | After |
| --- | --- | --- |
| A repeated `Clean Air Act section 111` | One deduplicated identity, no occurrence positions | Two exact occurrences; identity-only API still deduplicates |
| `Section 111(d) of the Clean Air Act` | `(d)` absent | Original pinpoint retained; mapping to a USC pinpoint explicitly not performed |
| A line break inside `Clean Air Act` | Normalized name only | Exact original text and coordinates alongside the normalized reading |
| `Clean Air Act section 111. A different provision names division B.` | Borrowed `B` from a 40-character window | Division remains absent |
| Separate sentences/paragraphs containing a name and section | Could be joined into one citation | Direct recognition refuses the association; document-context resolution is separate |
| Short `(2025)` / `(as amended)` qualifiers | Identity remained readable | Identity still readable, exact qualifier preserved, neither treated as a subsection |

These are selected real publication fields and constructed development controls.
They demonstrate bounded recognition/evidence improvements, not a general legal
extraction accuracy rate. The authority fields come from the pinned derived
Unified Agenda table; they are not full original document contexts.

## Implementation and verification

RefSpec now exposes `ActRelativeCitationOccurrence` and
`find_act_relative_occurrences`. Its existing identity-only reader calls the same
matcher. The matcher tokenizes the input once, examines at most 24 adjacent tokens
on either side of each section marker, and uses the supplied name set. It avoids
repeatedly splitting the entire document prefix. No whole-corpus rebuild occurred.

Rulespec adds `--act-index` and `--source-credit-index` to the two existing
reference/discovery commands. Index loading remains optional and occurs once per
document scan, not once per citation. Both successful and unresolved native
results survive. Ungrounded inserted text cannot acquire a resolved identity.

- **475 extractor tests passed**: [application-final-tests.log](application-final-tests.log).
- **304 RefSpec parser/resolver tests passed**: [owner-boundary-tests.log](owner-boundary-tests.log).
- **40 selected Unified Agenda caller tests passed**, 110 deselected:
  [caller-final-tests.log](caller-final-tests.log). This is not RefSpec's full suite.
- Six selected application inputs produce identical complete scans from source
  imports and a fresh installed wheel. Both CLI commands pass from `/tmp`, using
  a real publication field with an empty manually compiled rulebook. Default
  records/statements remain unchanged.
- All **19 previous occurrences across nine cases**—16 five-family additions and
  three CFR occurrences—retain their candidates, evidence, IDs and rejection state.
- Isolated/current dependency checks pass. `.tools/document-poc-venv` now imports
  the same module bytes as the tested wheels; see [current-modules.json](current-modules.json).

The exact wheels and comparisons are in [verification.json](verification.json).
Builds are `dist/reference-tools-20260911-acts/refspec-0.1.0.dev0-py3-none-any.whl`
and `dist/reference-integration-20260911-acts/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl`.
The operating guide contains the install command; versions alone cannot select
between these local builds. No provider calls, source downloads, commits or publication
occurred in this experiment.

## Data mapping and limits

`reading` retains the native act name/key, written section, division and pinpoint.
`resolution` retains the native target or unresolved reason, source-credit status,
classification source and available citation metadata. Its duplicate `citation`
object is omitted because the reading already carries it. Index file hashes and
parser hashes identify the inputs behind the result. Existing `SourceFragment`
evidence and discovery's shared evidence table locate the source occurrence.

A mapped section is not a fetched target body or a confirmed historical edition.
Act and codified subsection numbering may differ. The example indexes use different
declared source release points; the output does not silently claim they match an
older source document. `semantic_completeness` stays `not_established`.

The supplied source-credit index was loaded and consulted, but these selected
application cases have no usable source-credit key (`no_key`). They do not
demonstrate an additional mapping obtained only from source credits. A real
division-specific positive/conflict example remains useful follow-up evidence.
General ranges, unknown abbreviations, direct qualified USC citations, local
paragraph addresses and source-body lookup are still open.

First-process index loading varied from about 9 to 12 seconds in the captured
probes; subsequent same-process application scans were about 0.8–1.1 seconds.
These observations include initialization and reuse effects and are not a general
latency promise. Profile initialization before introducing any batch cache or
additional abstraction. No extra work is added to default extraction.

## Retained failures and reproduction

The original designs are [design.md](design.md) and
[occurrence-design.md](occurrence-design.md). Inputs, original output and final
installed output remain in [cases.json](cases.json),
[observations.json](observations.json), and [observations-final.json](observations-final.json).
The original matcher is frozen in RefSpec's `tests/act_parser_oracle.py`; the
real-field/mutation tests declare the intended differences. The new sentence
boundary failures are retained rather than folded into a passing-only record.

Two harness mistakes were corrected without loosening the implementation: an
initial `inspect.py` filename shadowed Python's standard module, and one oracle
expectation incorrectly assumed the old case-sensitive division pattern matched
uppercase `Division`. Their logs remain. Source and wheel captures live in
[source](source) and [wheel](wheel). `check_application.py --output-dir NEW_PATH`
repeats the selected scans; `--cli` adds the three installed commands and refuses
to reuse an existing output directory. `probe.py --output NEW_FILE` records the
eight fields and eight diagnostics without overwriting earlier output.

The broader reuse goal remains active. This delivery connects one useful reader
and resolver; it does not finish the remaining parser, context, vocabulary and
discovery work in the task list.
