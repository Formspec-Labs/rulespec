# Generate the extraction schemas with native CUE

Move the extraction application's schema authority into CUE and remove the
independently authored Python schema once the native path passes its checks.
This follows the settings recheck. Existing Core constraint generation stays
on its current path while the application profile is tested separately.

The CUE profile will own shared fields, classifications, rich guidance, model
field order, and the distinct constraints of model output and local candidates.
Native CUE generates validation rules. A bounded adapter may resolve local
references and restore titles and ordering from CUE metadata; it must not
interpret CUE expressions or silently weaken validation.

Generated JSON files ship with the Python package. CUE and Go are build-time
tools, not requirements for extraction or offline replay. Record the source and
generator versions and include generated schema inputs in frozen run provenance.

Acceptance:

1. Preserve the exact evaluated model schema, including titles, descriptions,
   field order, and required fields. Refinement must keep receiving the same
   shared meaning fields.
2. Match native CUE and generated JSON Schema on valid candidates and targeted
   mutations: missing fields, extra fields, wrong types/enums, empty evidence,
   repeated component evidence, and nullable/nonnegative offsets.
3. Replay saved responses through the current parser and Core conversion without
   changing normalized results or historical captures. Historical strict replay
   must still notice implementation changes.
4. Run the application tests, schema generation drift checks, and an installed
   wheel check outside the checkout. Preserve existing Core source/output files.
5. Save a concrete report of what changed, evidence checked, and remaining limits.

Status: implemented locally and verified. `core.py` loads the generated candidate
schema and classifications; `extraction.py` loads the generated model schema.
The rich descriptions, model schema, and refinement schema retain their exact
evaluated contents and order. Generated files and CUE source ship with the wheel
and participate in frozen run provenance. Runtime loading rejects source/output
hash drift.

Verification: 181 source/schema controls passed, 227 application tests passed,
and 34 affected tests passed (overlapping the application suite). All 24 saved
outputs normalize unchanged; all 9,476 protected files and 62 Core source files
retain their hashes. A fresh installed-wheel environment compiles a candidate,
validates its Core graph, and freezes schema inputs without Go or CUE on PATH.
The generation drift check passes. A CI check was added but has not run remotely.

The final native path loads a CUE package, rather than loose files, so the module
language version is applied and recorded. No new model call, commit, push, or
Core compiler migration is part of this delivery. Detailed evidence is in
`examples/document_understanding/native-extraction-schema/`.
