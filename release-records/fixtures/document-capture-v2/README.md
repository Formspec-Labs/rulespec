# V2 provenance migration examples

These are copies of seven retained SpicyDocs captures, migrated for RS1 review.
They are not new acquisitions, new text extractions, or published family profiles.
The manifest records original and migrated hashes, all explicit field-origin
changes, and the unchanged text-stream digest for each example. Absolute paths
are preserved evidence locators; repository tests do not open them.

| Family | Shared provenance findings | Parent shape findings |
| --- | --- | --- |
| Bill XML | Missing MODS | 0 |
| CFR PDF reconstruction | Incomplete acquisition time; missing MODS | 0 |
| Committee-report HTML | Incomplete acquisition time | 0 |
| Federal Register XML | 0 | 0 |
| Public-law XML | Missing MODS; archive/member proof pending RS2 | 0 |
| Supreme Court PDF | 0 | 0 |
| Senate PDF page cut | Six unobserved cell boxes | The same six absent boxes |

The eleven legacy gaps remain failures under the applicable requirements.
Missing observations are not repaired by changing an issue, date or coordinate.
The archive seam adds a separate pending finding. Only the Federal Register and
Supreme Court examples are complete under their review profile requirements.

The migration preserves artifact descriptors, structure, source coordinates,
text, unresolved content and issues. It adds explicit origin metadata and binds
each existing rule to the retained converter version and manifest digest. This
is a declared migration binding, not evidence that v1 published rule versions.

The replay and byte proof live at
`~/Work/corpora/supply-2026-09-02/receipts/remaining-gaps-wave1-2026-09-21/rs1/`.
The CFR original PDF was not found there or in its named source locations, and
its receipt provides no acquisition time. Those remain explicit byte-proof
limits beyond structural migration checks. Run `make test-document-capture`
for the versioned schemas, invariants and mutation controls.
