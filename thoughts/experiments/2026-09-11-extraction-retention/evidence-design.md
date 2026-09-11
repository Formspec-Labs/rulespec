# Evidence implementation choice, before compound-output comparison

Core already permits multiple `SourceFragment` values in `EvidenceBinding`.
Keep atomic `_evidence` checks strict. Add one shared operation that resolves a
complete quotation, rejects inserted non-whitespace, and returns its verified
original-source pieces. Reuse the discovery source-map slicing algorithm, including
its index so source export does not rescan the full map for every passage.

Whole quotation coordinates remain on the claim. Evidence records retain their
existing shape; a field can have multiple complete, ordered source pieces. Review
validation must compare the entire group with the expected source pieces, refusing
missing, duplicate, moved or fabricated pieces. Definitions, typed values,
attribution, qualification links and fallback context must retain all their pieces.

Concept assignments already tag the complete quoted region of the prepared-text
Artifact. Preserve that target rather than tagging only one piece or silently
changing the target to a rule/revision. A `SourceFragment` may address that exact
prepared region, including its formatting, as an annotation target. Its supporting
EvidenceBinding still names only original-source pieces. Test this distinction:
being a graph node does not by itself make a fragment supporting evidence.

This uses existing Core shapes and generated schemas. No new model field, compound
selector type, parallel evidence table or new extraction stage is required.
