# Reuse publisher USLM links and exact source targets

Decision: Can RefSpec's existing `extract_uslm_reference_edges.iter_edges` become
a shared application reader that preserves publisher link context and locates
the written reference and any in-document target without a second citation parser?
This is R14 and a source-supported route toward R11/R12; the failed CFR paragraph
heuristic remains unchanged and experimental.

## Hypotheses and arms

H1: Publisher identifiers remove the need to infer paragraph ancestry for USLM
inputs. Exact identifier lookup should select the actual nested target, while a
missing or duplicate identifier stays unresolved.
H2: The main integration gap is occurrence location. An opt-in XML node path on
the existing native occurrence can connect it to deterministic prepared-text
positions, preserving repeated identical references without quotation search.
H3: A text-only citation scan and publisher links provide different information.
Historical notes, source credits and contents links must remain distinguishable;
adding publisher data must not turn them into operative rule relationships.

A: Copy the current native reader as a test-only oracle and capture its output
on fixed sources. The current Rulespec text scan is a separate application
baseline; absence from that scan does not prove a source contains no citation.
B: Reuse the same native reader from a public RefSpec module, with optional
element paths. Map source elements to text positions using the XML tree, not
matching repeated strings. Connect exact target identifiers to existing source
spans and selectors. Original native fields and refusal behavior must be preserved.

## Inputs, controls and bounds

Use the pinned local USLM archive at release point 119-102. Verify its digest and
selected title-member digests against the existing source-credit receipt. From
titles 5 and 42, select the first section in source order with 2–40 href-bearing
elements, 1,000–25,000 serialized bytes, and at least one href equal to a nested
identifier present in that section. Skip nested section elements for the bounded
source capture. Selection uses publisher attributes before either changed reader.
Preserve the complete section bytes and the original namespace context.

Inspect those raw sections before trusting the new paths. Add constructed
counterexamples for duplicate target identifiers, absent targets, identical
reference text at different positions, Unicode/entities, nested inline markup,
source credits versus operative references, notes, contents entries, non-section
units, missing identifiers, fragment-only links and unknown href prefixes.
Reuse the existing owner fixtures where they supply these cases. Compare default
outputs with the copied oracle on real source and mutations, including errors
and skipped counts. Mark constructed results as such.

Held constant: captured XML bytes, declared title/release, identifier spelling,
native context/classification semantics and exact evidence rules. No model calls,
new legal editions, artifact rebuilds or changes to default text extraction.
Run deterministic comparisons once; repeat only to verify a recorded change or
source/package parity. Stop this experiment after the two real sections and the
declared owner/control cases settle the integration decision.

## Adoption rule

Every original native field, occurrence order, skipped count and refusal must
match the oracle unless a separate source-backed correction is explicitly
recorded. Each added node path must select exactly the originating XML element.
The mapped text must be the actual element text, with exact codepoint offsets;
XML paths are not raw byte offsets or prepared-text positions. Unchanged repeated
mentions remain distinct. In-document target lookup requires exactly one matching
publisher identifier in the declared source; absence is not nonexistence in law.

Preserve context and original identifiers, including Unicode dashes. Return a
navigation result, not an applicability or exception judgment. Use existing
`SourceFragment`, XPath/text selectors, evidence identity and source passages.
No model-facing fields or parallel Core schema. Keep the optional reader outside
Core validation's dependencies. If the comparison passes, verify direct imports,
upstream/application tests, then rebuilt wheels and installed CLI behavior before
marking the integration delivered. Original captures remain immutable.

## Reuse and expected footprint

Move the pure native reading functions out of the existing build script rather
than copying its parser into Rulespec. The script keeps acquisition/reporting and
imports the shared functions. Python's XML/IO primitives can handle text order and
node traversal; a crawler, new database or general parser framework is unnecessary.
Processing should be linear in source size plus emitted occurrences and target
lookups; do not scan the whole document once per reference.
