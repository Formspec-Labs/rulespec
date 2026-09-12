# Annual CFR source preparation and reader gap

Yes: the native source reader should support GovInfo's annual CFR XML. Annual
editions give this workflow dated, reproducible source documents. Add that support
to RefSpec's existing legal XML reader and let Rulespec consume the same prepared
document interface. Do not create a second Rulespec parser or send XML to a model
for preprocessing.

Current verified gap: `load_document` refuses these `CFRGRANULE` roots with
`Expected captured eCFR ECFR or typed DIV XML`. This experiment does not change
production parsing. It uses the already installed DocSpec `XmlVisibleTextExtractor`
as an acquisition tool, retaining XML, visible text, metadata, blocks and byte runs.
Rulespec evidence refers to the frozen visible-text rendition. Its offsets are
not native XML offsets; the separate acquisition map preserves that relationship.

All SECTION/P paragraphs survived whitespace-insensitive comparison: 28/28 in
14 CFR 91.213, 12/12 in 40 CFR 262.11. These checks establish retained paragraph
text, not complete structural/metadata semantics. Failed eCFR API requests and
GovInfo HTML/text error-page redirects remain saved and were not model inputs.
21 CFR 50.23 remains an unselected candidate, as described in PLAN.md.

## Small upstream task

- Extend the existing RefSpec XML reader to recognize annual `CFRGRANULE` and
  section/volume structures, using existing text extraction and source indexing.
- Preserve section addresses, paragraph order, inline text, notes, tables, and
  original-byte evidence using existing reader representations. Cover section
  granules and at least one volume fixture; do not assume a section-only wrapper.
- Preserve publisher and edition-date metadata. An annual edition date is not
  automatically every provision's effective date or proof of a matching remote
  reference edition.
- Validate text and source spans against retained XML, then exercise the existing
  Rulespec preparation/reference/context flow with that native result.

This is recorded follow-up work, not implemented support. Keep this experiment's
already frozen rendition and extraction inputs unchanged when that reader lands.
