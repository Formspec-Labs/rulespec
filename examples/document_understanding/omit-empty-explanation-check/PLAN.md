# Logic and modality without empty placeholders

Decision: determine whether omission-only output removes null/empty overhead while
retaining useful logic/modality explanations and source-faithful statements.
No production adoption is authorized by this exploratory experiment.

Observed: required-nullable explanation fields coincided with hundreds of other
optional fields being emitted as null. Logic supplied selective supported notes;
modality supplied inspectable classifications and an uncertainty-handling signal.
Post-processing can remove noise from later consumers but cannot recover already
generated output tokens, so test the model-facing schema and prompt.

Hypothesis: optional non-null, nonempty values with omission instructions eliminate
placeholder output and reduce generated tokens. The hypothesis is weakened if
the model invents values, emits literal null/N/A placeholders, loses useful notes,
or produces less faithful statements. Separate omission compliance, explanation
usefulness and statement quality; saving tokens alone does not establish accuracy.

Two arms per field, tested independently for logic_explanation/modality_explanation:
- N: exact previous required-nullable field schema and current prompt, called fresh.
- O: explanation optional and non-null; existing optional enrichment non-null;
  present strings/lists nonempty; instructions use omission instead of null.
  Keep existing field order, substantive guidance and current parsing/Core records.

O is a deliberate schema-plus-aligned-instruction bundle. It does not isolate
optional requiredness, non-null constraints, minimum length, or wording alone.
All types come from the existing native CUE exporter and an isolated copy of the
canonical application profile; do not hand-write a competing provider schema.
No new fields or changes to production are included. Null/omission conversion in
the current parser stays supported; omission is a provider output policy.

Cases: full saved notice and waste documents, including the actual notice
qualification miss, may-not-be-required uncertainty, nested venting exceptions,
AND label components, three-day alternatives and all destinations. Neighboring
explicit modalities, first-time/repeat leave conditions, generator categories and
descriptive material are counterexamples against inventing content to fill fields.
Use the prior field-specific review criteria; preserve failed/uncertain labels.

Eight calls: one N/O call per field per document. Fixed randomized dispatch order;
gemini-3.8-flash, temperature 0, low thinking, 16384 output tokens and full source
window. No retries, repair/audit calls or extra cells. Historical runs are context,
not fresh controls. One repeat per cell does not establish stability.

Decision rule: O must emit zero optional null, empty-string/list or literal null/N/A
placeholders on both sources for the relevant field. Target >=20% fewer output
tokens in each matched pair, with no loss of named correct statements or useful
baseline notes. If the source had a useful baseline explanation, omitting it is
an explanation-retention tradeoff even if the statement stays correct. Do not
require a note on every row. A positive outcome supports a bounded omission-policy
proposal, not automatic adoption or a broad quality claim. Record failed gates.

Review canonicalized statements first under opaque IDs without notes, config or
usage; save judgments before inspecting notes/arms. Then review note content and
field adherence. These are revisable Codex labels on development sources, not
independent human gold. Preserve original responses, refusals, schema/runtime
hashes, notes and deterministic zero-provider replay.

Pre-call feasibility adjustment: adding list.MinItems(1) triggered the current
native-schema metadata adapter's "Only homogeneous model-schema lists are
supported" error. No provider call occurred. Keep the existing homogeneous list
types and do not modify the production exporter for this trial. O's schema forbids
null and empty strings; its prompt requests omission of empty lists, whose actual
emission is still checked against the original zero-placeholder criterion. This
narrows structural enforcement without weakening that observed-output criterion.
