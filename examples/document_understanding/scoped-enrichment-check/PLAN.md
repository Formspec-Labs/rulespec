# Omit empty enrichment while retaining the explanation slot

Decision: can logic/modality explanations remain useful when only the other
optional fields switch to omission? This is a diagnostic experiment, not adoption.

Observed: the prior bundled omission variant removed all 438 nulls but every
explanation disappeared; 400 of those nulls belonged to other fields. Competing
explanations are (1) making the explanation optional encouraged its disappearance,
or (2) the broader omission instructions/schema affected explanation production.
If (1) dominates, keeping the identical required-nullable note should restore useful
notes while other empty fields disappear. If notes still disappear, requiredness
alone does not rescue the mechanism. This comparison cannot isolate the effects
of non-null constraints versus aligned wording for other enrichment.

Arms, independently for logic_explanation and modality_explanation:
- N: fresh calls using the exact preceding required-nullable schema and prompt.
- E: keep the explanation property's type, requiredness, order and description
  identical to N; use the preceding omission policy only for other enrichment.
  Keep statement, kind and modality required. Nonempty optional strings reject
  null/empty string; empty lists remain prompt-controlled. No exporter changes.

Cases: full saved notice and waste sources. Reuse REVIEW.md named checks, including
the actual notice inherited qualification miss and waste exemption-scope failures.
Counterexamples include explicit duties/permissions/prohibitions, descriptive
possibility, first-time/repeat settings, AND labels, nested venting exceptions,
deadline alternatives and every removal destination. Keep expected-conduct and
may-not-be-required enum mappings uncertain rather than assumed gold.

Held constant: model gemini-3.8-flash, temperature 0, low thinking, 16384 output
token cap, full single-window documents, production parser/Core, and one repeat
per cell. Eight calls total, randomized dispatch and opaque output IDs. No retries,
audits, extra cells, production adoption or commits. Zero temperature is not a
determinism claim. Previous results are historical context, not current controls.

Decision rule per field across both documents: zero null/empty/literal-placeholder
values in other optional enrichment, at least 20% fewer output tokens per pair,
no lost named correct statements, and retention of source-supported useful control
explanations matched by meaning rather than row number. Required note nulls are
counted separately and allowed in this isolation. If the fresh control has no
useful notes, explanation retention is untested for that case. More notes alone
is not success; track repetitive, incomplete and unsupported notes separately.

Review statements under opaque IDs before notes/arm labels; save judgments before
unblinding. Optional field presence may hint at arms, so blinding is imperfect.
Assess instruction adherence, semantic quality and tokens separately. Save all
requests, responses, failures, source/runtime/schema hashes and review labels;
replay without provider calls. Labels are revisable Codex judgments on development
sources, not independent gold or a general accuracy estimate. Stop at eight calls.
