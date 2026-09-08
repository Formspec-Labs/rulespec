# Live endpoint check — 2026-09-08

Gemini 3.8 Flash accepted the current CUE-generated extraction schema and
returned a complete response at temperature 0.2. One real request processed the
saved 2,651-character name-change section in about 14.4 seconds. No source,
prompt, schema, or implementation changes were made for this run.

- [Original run](live-names-01/run.json): 13 model units, 12 accepted candidates,
  one parser refusal, no compiler rejections. Status correctly remains `partial`.
- [Raw response](live-names-01/attempt-0000.response.json): finish reason `STOP`;
  all required model fields present. Usage: 6,145 input tokens, 5,271 response
  tokens, 718 thought tokens; 12,134 total tokens reported by the provider.
- [Validation](live-names-01/validation.json): 300 Core nodes; JSON Schema and
  SHACL pass. [Offline replay](live-names-01-replay/run.json) reproduces the result.

## Source review

The limited-validity passport permission retains the inherited more-than-one-year,
DS-11 and unchanged-ID conditions, plus insufficient time before urgent/emergency
travel. The final documentation requirement retains the within-one-year and
unchanged-ID conditions. The previous-name exception links to the correct
prohibition. The exemption, descriptive possibility, and qualified “generally”
statement survive with their source wording. These are observations from this
single run, not a completeness or accuracy score.

The refusal is raw row 2, the document-submission requirement. Its first
`alternative_quotes` item collapses the court-order parent and child list into
one line that does not occur verbatim in the source. All named alternatives are
represented in its proposed meaning, but the entire unit is excluded from the
accepted graph because of that quotation. The original row remains in
[refusals.json](live-names-01/refusals.json). This leaves a substantive requirement
and its alternatives unavailable to graph consumers until corrected.

One accepted definition has unresolved modality evidence: the short quote “is”
is ambiguous. Three actor omissions remain visible, alongside routine logic
review flags. All ten unresolved links are section/reference lookups outside
this excerpt; the emitted local exception target resolves.

The live schema integration works. The next focused quality issue is exact
quotation of nested lists, including the impact of rejecting a whole unit when
one component quotation fails. This check made no automatic repairs.
