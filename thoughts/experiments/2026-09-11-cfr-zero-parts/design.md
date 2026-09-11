# CFR part zero: independent minter correction

Decision: remove the unsupported positive-integer requirement from the numeric
stem of a CFR part, while preserving the existing title, suffix, section and
identifier-space checks. This does not adopt the whole-token/range experiment.

Hypothesis: the minter incorrectly applies the title's positive-integer rule to
parts. Rulespec's existing CFR space allows a zero stem. The OFR index contains
nine part-zero keys; publisher XML confirms all nine, including a reserved part
and eight parts with sections. Normalizing zero as zero should recover these
identifiers without changing any nonzero part or accepting malformed input.

Arms: copied current `_cfr_part` implementation from RefSpec `566df1d4` versus
the same lexical check with nonnegative part normalization. Do not use a roster
to decide whether a syntactically supported part exists in every legal edition.

Cases: all 8,424 distinct stored OFR title/part keys, exact publisher XML headers
and first sections for the nine part-zero keys, and mutations of zero padding,
whitespace, uppercase suffix, valid/invalid titles, negative/decimal numbers,
non-ASCII digits, compound forms and malformed suffixes. A constructed zero-stem
letter suffix tests the existing Rulespec space, not an issued-part claim.

Held constant: no model calls or source refresh. Preserve copied old code,
original XML slices, source hashes, results and errors. Title zero stays invalid;
compound-part policy stays unchanged. Stop after the source/mutation comparison,
relevant owner/application checks and rebuilt/installed-wheel verification.

Decision rule: adopt if all nine source keys mint into the existing Rulespec
space, nonzero keys agree with the old implementation, all changes are confined
to previously refused zero stems, malformed inputs remain refused and the
relevant checks pass. No new schema, compatibility layer or index loader.
