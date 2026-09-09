# Extraction handoff

The current operating guide is packages/rulespec-extrapolator/README.md. Historical
experiment reports remain immutable evidence of their own runtime and settings;
they are not competing current implementation plans.

Final fresh check: one saved 6,919-character leave-eligibility regulation through
low extraction, medium source-first inventory and medium comparison. Three STOP
responses, 19 accepted statements, no extraction refusals or rejected candidates.
64,117 reported tokens and 48.24 seconds of request time. Four inventory entries
failed absent/ambiguous bare marker grounding, so the final audit correctly reports
needs_review and review_complete=false despite 20/20 accepted units marked covered.

Direct source review finds the principal rules, alternatives and examples retained.
Accounting exceptions remain in logic_text but are missing from standalone summary
and scope; the audit misses that distinction. Similar split-statement limitations,
modal classifications and compressed explanatory detail remain. There are no
explicit exception edges in the normal pass; their accuracy was not tested.

Verification: 333 package tests, 6 schema-generator tests, native CUE drift check,
identical production extraction/audit replay, and identical discovery export.
Discovery retains all 17 source passages. Detailed evidence and eleven revisable
source checks are in examples/document_understanding/low-extract-medium-audit/.

Decision: useful draft/discovery tooling with optional medium audit, not automatic
certification for executable workflows. No default thinking changes or additional
prompt tuning. Preserve feedback/review as a normal part of both user workflows.

Next focused work when resumed:
1. Inventory should cite substantive governing text or existing passage IDs rather
   than absent/ambiguous bare section labels. Reuse existing passage/evidence
   machinery; retain refused captures rather than silently repairing quotations.
2. Evaluate short statement/scope completeness separately from conditions retained
   in logic_text, with source-backed positive and omission controls.
3. Check optional relationship refinement and cross-file concept resolution only
   when a consumer needs them; do not expand the cheap pass for schema coverage.

Commit grouping: coupled extractor/schema/test changes; preserved experiment and
research evidence; consolidated operating guidance and this final full-run record.
No push, deployment, release or global memory change is part of this handoff.
