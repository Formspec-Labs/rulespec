# Retain open-ended USC qualifications

Decision: retain an explicit open-ended qualification instead of admitting only
its first section. This was discovered during the positive CLI delivery check,
after the 31-case native-field preservation checks passed. Those earlier results
remain valid for their cases, not for this newly observed form.

Hypothesis: the existing occurrence recorder can consume the written `et seq.`
tail and expose an unresolved-range refusal without changing the authority-field
API or unaffected occurrence results. Use the same treatment for the existing
grammar's `and following` and `ff.` spellings. Do not guess a last section.

Cases: the actual FMLA/USERRA paragraph in `source.json`, constructed controls for
the two alternate spellings, an ordinary trailing sentence, and all 31 prior
inputs. Compare the copied c5c0a27d occurrence function and new function; the
existing authority-field oracle must still agree. Deliberate divergence: only
the previously omitted open-ended tail is now retained with
`usc_open_ended_reference_unresolved`. No target existence or applicability claim.

Gate: complete source wording and refusal survive the owning reader and both
Rulespec commands; no endpoint invention; no changed field-reader results or
unlisted differences on prior cases. Test direct imports before new wheels.
Preserve the initial delivered wheels, receipts and positive-capture refusal.
This is a small new correction, not a passed broader grammar-completeness claim.
No model call, model setting change, new Core schema or lookup service.
