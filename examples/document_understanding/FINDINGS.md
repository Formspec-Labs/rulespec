# Proof-of-concept findings — 2026-09-07

## Follow-up: Gemini 3.8 Flash

The requested follow-up is saved in `runs/gemini-3.8-flash-01/`.
The actual provider response reports `gemini-3.8-flash`. The recorded request
contents and generation configuration are exactly equal to the final 3.5 Flash
run; only the requested model differs. This is one run per model on a development
example, not an accuracy benchmark.

| Check | Gemini 3.5 Flash | Gemini 3.8 Flash |
| --- | --- | --- |
| Candidates with exact evidence | 17/17 | 19/19 |
| Resolved qualification links | 6 | 6 |
| Declared but unresolved links | 0 | 0 |
| Core nodes passing JSON Schema and SHACL | 65 | 71 |
| Provider-free rulebook/graph replay | Byte-identical | Byte-identical |

Assistant source review found mixed changes:

- 3.8 retains the House's judgment in the secrecy-exception summary, which 3.5
  omitted. Its consent summary correctly specifies adjournment beyond three days.
- 3.8 separates the duration and location adjournment prohibitions, improving
  granularity. However, it attaches session and consent conditions only to the
  duration rule. The separate location rule loses those shared qualifications.
  This is a substantive scope omission, despite zero unresolved declared links.
- The quorum summary is clearer ("constitutes" rather than "must constitute"),
  but remains classified as a requirement. The authority-versus-duty and
  necessary-versus-sufficient trigger issues remain.
- 3.8 adds a permission for each House to specify manner and penalties; its short
  supporting quote ("each House may provide") requires surrounding context.

Product conclusion: 3.8 improves some wording and separation, but the split creates
a new scope omission. A model upgrade does not replace a rule profile with shared
conditions or human review. Open [the 3.8 review](runs/gemini-3.8-flash-01/review.html).

## Result

LangExtract plus Gemini can produce source-grounded candidates that this Rulespec
prototype converts into existing Core records. The final live run produced
**17 candidates, all with exact source quotations, six qualification relationships,
and 65 nodes passing Core JSON Schema and SHACL validation**. A provider-free
replay reproduced the rulebook and graph byte for byte.

This demonstrates the producer → evidence verification → Core representation →
review path. It does not establish complete or reliably correct rule understanding.

Open [the final review](runs/gemini-3.5-flash-03/review.html),
[the rulebook](runs/gemini-3.5-flash-03/rulebook.json), or
[the validation result](runs/gemini-3.5-flash-03/validation.json).

## Source and method

The source is the National Archives' historical transcription of Article I,
Section 5 of the U.S. Constitution. The retained excerpt is 1,026 Unicode
characters, four paragraphs plus a heading, covering internal congressional
procedure. Original HTML, text-selection method and source hashes are retained.

One source window, one extraction pass, temperature zero. LangExtract 1.6.0;
Gemini model response reports `gemini-3.5-flash`. The final provider uses a JSON
schema inferred from separate invented examples. Core validates the converted
records; the model was not handed the entire Core schema collection. Model
responses, requests, prompts and candidate records remain available for inspection.

The adapter reads a Gemini key from an explicitly supplied local environment file.
It does not copy credentials or make SpicyRegs a runtime dependency. Only the
public excerpt and invented examples are sent for extraction.

## Development runs retained

| Run | Outcome |
| --- | --- |
| `qwen3-4b-01` | Seven candidates; one altered quote rejected. First conversion found a missing Artifact identifier; replay with corrected conversion retains six grounded candidates and two unresolved targets. |
| `qwen3-4b-02` | Richer examples: 15 exact-quote candidates, five unresolved targets, and visible permission/requirement classification mistakes. First SHACL validation found an integer temperature where a double was required; the converter now emits a double. |
| `gemini-3.5-flash-01` | Provider returned Markdown-fenced JSON. LangExtract skipped the chunk and produced zero candidates. The original empty graph passed structural checks, exposing a missing success gate. The current CLI returns failure when no grounded candidates remain. |
| `gemini-3.5-flash-02` | JSON MIME configuration: 18 exact-quote candidates, zero unresolved links, 66 valid Core nodes. A supplied model ignores LangExtract's `use_schema_constraints` flag; provider schema setup must be explicit. |
| `gemini-3.5-flash-03` | Explicit Gemini schema derived from examples: 17 exact-quote candidates, zero unresolved links, 65 valid Core nodes. Final demonstration run. |

Earlier outputs are not rewritten to pretend they were produced by the final code.
Replay directories and run metadata distinguish extraction from later conversion.
The local 8B model download completed while Gemini work proceeded; no 8B inference
was run after the user directed the experiment to Gemini.

Prompt changes and provider configuration changes make this a development record,
not a controlled model benchmark. The example document was inspected during
development; there is no blind human-labeled holdout or accuracy percentage.

## Semantic review of the final run

The assistant compared all 17 candidate summaries and their links against the
retained source. This review is not a human attestation or authoritative legal
interpretation. All candidates remain in the review queue.

| Finding | Evidence in final output | Practical consequence |
| --- | --- | --- |
| Correctly separates journal keeping, publication and secrecy exception. | Candidates 9–11 (zero-based), with the exception linked to publication. | The workflow can extract useful separately referenceable pieces. |
| Correctly connects the two-thirds threshold to expulsion. | Candidates 7–8. | A qualification can become a separate assertion with evidence and a relationship. |
| Quorum is represented as an obligation rather than a constitutive threshold. | Candidate 1: “A majority ... must constitute a quorum”. | The small class set needs authority/definition/threshold distinctions, not just obligation words. |
| Judicial authority over members' qualifications may be overstated as a duty to act. | Candidate 0 changes “shall be the Judge” to “must judge”. | Review the distinction between assigning authority and requiring an action. |
| Secrecy summary omits the House's judgment. | Candidate 11 says parts “requiring secrecy”; the quote retains “in their Judgment”. | Exact quotes preserve recovery evidence but do not guarantee lossless summaries. |
| One-fifth summary can read as a necessary condition instead of a trigger for an obligation. | Candidate 13 says entering votes “requires” that desire. | A structured condition needs direction: sufficient trigger, necessary prerequisite, or exception. |
| Consent summary is too broad in isolation. | Candidate 16 says “Adjourning requires ... consent”; the target rule limits duration/place and session. | Qualifications themselves need explicit scope; a correct target link is not enough. |
| Two adjournment prohibitions remain one compound candidate. | Candidate 14 combines duration and place restrictions. | Source coverage is present but the intended atomic granularity was not achieved. |

The remaining permissions and conditions are recognizable readings of the source,
but neither the actor strings nor the summaries have been accepted by a human.
No claim of semantic completeness follows from zero unresolved links: that count
only measures whether the model's declared targets resolved unambiguously.

## Checks and limitations

- All **14 focused tests pass**. They cover evidence mutation, ambiguous repeats, Unicode coordinates,
  source and provider/candidate tampering, unresolved targets, unknown classes,
  provisional AI restrictions, SHACL temperature typing and HTML escaping.
- All six Core schemas used by the converter match freshly compiled CUE output
  byte for byte. The retained experiment files were checked against the actual
  credential value; no credential was present.
- Live extraction, existing Core JSON Schema validation, existing SHACL validation,
  and provider-free replay all ran locally. Exact replay equality was checked for
  `graph.jsonld` and `rulebook.json`.
- Some overlapping or out-of-order example extractions trigger LangExtract
  alignment warnings even though their substrings exist. The application does not
  rely on those labels as evidence proof; it independently resolves unique quotes.
- The example uses a small experiment-owned candidate schema and experimental
  predicates. It does not add a normative CUE rule profile or an automatic schema
  derivation system. Actor text remains review metadata.
- The whole source fits in one window. SpicyRegs segmenter integration, PDF parsing,
  multi-document/version handling, RefSpec alignment, editable review and human
  attestations remain unimplemented.
- Replay validates saved candidates and compiles them; it does not regenerate
  LangExtract annotations from the raw provider response. Historical runs without
  candidate hash fields have weaker tamper checks, explicitly retained as such.

## Next slice

Define a small rule profile around the observed failures: authority versus duty,
constitutive thresholds, necessary versus sufficient conditions, shared scope, and
compound actions. Add a separate held-out source excerpt and independently reviewed
expected results before expanding model or segmentation experiments. The prototype
shows that the library and Core can connect; the next work should improve semantic
representation and evaluation rather than add another generic chunker.
