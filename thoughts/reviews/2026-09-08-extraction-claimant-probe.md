# Issuer attribution validation probe

An offline synthetic probe confirmed that exact evidence does not establish
source attribution. This is a parent-agent finding, separate from the blind
subagent review. No saved capture or production source was changed.

Starting from candidate 0 in
`examples/document_understanding/extraction-polish/selected-names/candidates.json`,
replace its `claimants` with:

```json
[{"text":"Invented Office","quote":"A material discrepancy is any name change that is not defined as immaterial in 8 FAM 403.1-5.","attribution":"rkaf:claimantIsDocumentIssuer"}]
```

Call `core.compile_candidates(document, [candidate], run)` using that capture's
`document.json` and `run.json`. The result has one accepted claim, an empty `issues`
list, and a `rkaf:SourceClaimant` with `rkaf:claimantText` equal to `Invented Office`.
The main quotation contains no issuer attribution. This probe checks compiler
behavior, not a fresh model response or the complete graph validation command.

`core._evidence` checks exact location and source provenance.
`enrichment.check_components` checks claimant count, nonempty text, and consistency
with `claimantNotStated`. Neither determines whether the quotation attributes the
statement to the named party. `supported_components` therefore permits this node.

The blind reviewer subsequently found that eleven of the twelve bad issuer
candidates in the original capture were withheld because their section-label
quotation was ambiguous. One actually reached the graph: candidate 2 resolves
the section-label prefix inside its main quote at offsets 712:725. I verified
this directly in the saved graph and corrected the initial experiment assessment.
Incorrect issuer attribution is not generally blocked. Any proposed fix should test
both ambiguous citations and uniquely located but semantically irrelevant quotes,
alongside a valid explicit attribution and a legitimate source-supported alias.

Existing reuse points for a follow-up are `SourceClaimant`, `EvidenceBinding`, the
component issue mechanism, and the audit's `source_attribution` dimension. A new
semantic check should preserve raw candidates and distinguish lack of verified
attribution from uncertainty about the underlying rule.
