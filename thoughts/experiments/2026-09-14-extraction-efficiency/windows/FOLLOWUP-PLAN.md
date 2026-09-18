# Explicit task identities within the grouped request

Written after the three original calls, before a fourth call. Original plan/criteria remain unchanged. This is a separate development follow-up, not a retroactive pass of the original grouping gate.

Observed: naive grouping retains all 14 selected source-detail checks but combines four monitoring duties into one statement and combines other independent duties. It saves 34.2% total recorded tokens while reducing 17 records to 12. Distinct referenceability is user value, so this is a tradeoff.

Decision: is explicit identification of the two section tasks worth broader evaluation as an alternative to naive grouping?

Hypothesis: a short task directive can preserve individual monitoring and training-process records in one request, without emitting a second schema or extra planning output. Prediction: four monitoring controls and two training-process duties return as separate statements, with all source detail/control checks preserved. Failure or larger input/overall token cost than the fresh separate controls weakens it.

Arms: the already captured B9913_9914 grouped call is the control; Btasks uses the identical prompt and source catalog, with one short addition immediately before the passage catalog naming each original section's F passage range as an independent task, and requiring distinct independently actionable duties (including distinct list children) to retain separate records. This intervention bundles explicit task identities and granularity instruction; it cannot attribute an effect to either independently. This is an adaptive selected-case test, not an untouched holdout.

Held constant: current CUE schema, original focus/context/catalog, 4,911 focus chars, model and provider-managed settings, one additional call, max16,384 output tokens, low thinking. No retries. Four total calls across both experiments, within parent authorization. Persist exact request, raw response, timing/usage, native parse, and replay.

Decision rule: investigate further only if source details/force/counterexamples survive, four monitoring requirements and two process requirements are individually referenceable, and total recorded tokens are less than the fresh separate controls. Any new meaning failure blocks a success claim. One call cannot establish repeatability or universal behavior; production stays unchanged.
