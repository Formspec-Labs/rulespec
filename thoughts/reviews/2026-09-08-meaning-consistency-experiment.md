# Meaning consistency experiment: retain the current default

Nine live Gemini 3.8 Flash calls tested the two prompt changes proposed after
the [raw extraction diagnosis](2026-09-08-raw-extraction-diagnosis.md). Neither
demonstrated an overall improvement. Preserve the captures and keep both
instruction blocks out of the default extractor.

Classification guidance corrected the distinction between an absent duty and
an absent prohibition. In the same treatment, two invented baseline rules lost
their exceptions, which survived only in separate statements. Baggage rules
also merged. A correct label does not compensate for an incomplete rule.

Field-consistency guidance improved the firearm declaration and captured its
full logical condition list. It also improved evidence for the leave proviso.
Other outputs regressed: baggage applicability disappeared from a scope, and
the leave definition lost the subject matter of two cross-references. Their
citations and original source remained available, but extracted meaning was
less complete.

Fresh controls corrected some previously observed photo and leave defects
without changed requests. The three real-document control requests exactly
match the saved adoption requests, yet their responses differ. This is direct
evidence of output variability at temperature 0; one observation per cell
cannot establish that a treatment caused every observed difference.

The evidence supports the earlier diagnosis that the model distributes meaning
unevenly across fields. It does not establish the internal cause. Premature
classification and competing generation tasks remain hypotheses. The next
narrow experiment could move the complete statement before classification and
supporting fields while holding instructions and field meanings fixed. This
experiment did not test that change, and it should not be adopted on theory
alone. Include fresh controls and judge complete meaning across all criteria,
not just the motivating failure.

All nine runs replayed to identical books without provider calls. Their 77
accepted statements passed Core graph validation, with no parsing or Core
refusals. Raw statement, scope, kind and modality matched the compiled values.
This places the observed meaning defects in model output, not conversion.
Total reported usage was 65,921 tokens, including thinking; there were no
retries, repair calls or model review calls.

The [experiment directory](../../examples/document_understanding/meaning-consistency-experiment/README.md)
contains the predeclared criteria, pinned inputs, exact requests and responses,
frozen runtimes, twelve source-review findings and replay verification. These
are revisable agent assessments, not gold labels. Prior captures and reviews
remain unchanged. This is a natural stopping point for this iteration; no
production changes or further provider calls are warranted by these results.
