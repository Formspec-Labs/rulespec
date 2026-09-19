# Document capture

**Status:** Draft schema, version 1, under architecture review. Owner ruling
of 2026-09-19 in [`docs/decisions.md`](../docs/decisions.md).

One JSON shape captures a federal document in whatever rendition it arrived
in: its structure as a tree of nodes, its exact text as an ordered partition
of evidence spans, and the provenance of both. Any node can be cited as a
`rkaf:SourceFragment` (`rkaf-core.md` §4.2) without loss. The schema is
[`release-records/schemas/document-capture-v1.schema.json`](../release-records/schemas/document-capture-v1.schema.json)
(JSON Schema draft 2020-12), pinned by the sha256 of its bytes.

Rulespec owns the parent shape and the composition rule below, the way it
owns generic container mechanics under REF-048. SpicyDocs owns the family
profiles that compose it and the converters that produce captures. Rulespec
builds no converter: a capture reaches this repository as a document, never
as a pipeline.

## 1. What a capture is

| Part | Holds | Reason |
| --- | --- | --- |
| `artifact` | The rendition bytes: digest, size, media type, a credential-free locator, publisher identifiers with their rkaf scheme | The artifact is what `oa:hasSource` names; its digest is `rkaf:sourceArtifactDigest` |
| `rendition.textStream` | A derived artifact: the text every span addresses, its digest, its length in Unicode code points, and the stated normalization from the artifact to it | Code points are the unit `rkaf:carrier-local-fragment` fixes, so every leaf gets a carrier-local URN for free |
| `nodes` | The structure: document, front and back matter, divisions, sections with designations, headings with levels, paragraphs, lists, quotes, tables with rows and cells, notes and footnotes, figures as references, page furniture, pages and lines | Capture is not interpretation: the vocabulary is structural, the publisher's own element name travels in `source.element`, and no node states legal meaning |
| `evidence` | The partition: contiguous, non-empty spans covering the text stream, each with its exact text, content digest and the artifact's own coordinates | Concatenating the spans reproduces the text stream; its digest is the round-trip witness, and any consumer can re-derive it |
| `unresolved` | Runs of spans no rule placed, with the issue that says why | Unplaced text survives with a reason rather than being dropped |
| `converter`, `capture`, `profile` | Who produced it (id, version, repository, revision, file digest, dependencies), when, and under which family profile pinned by digest | A capture is reproducible evidence only if its producer is named |

Every node carries `derivation`: `native` (the publisher's own structural
vocabulary), `markup` (structure the converter read off markup that is not
that vocabulary), `pdf-text` (an extractor's pages and lines) or
`reconstructed` (placed by a rule or model over extracted lines, with the
`decision` that placed it). Text a rule assembled from the exact spans (a
print wrap's hyphen dropped, small capitals restored) goes in `derived`, with
the rule named; the exact text stays in `text`.

Every id is minted by the converter and the document says so
(`capture.idOrigin = generated`, `capture.idScheme = document-order`). No
consumer reads one as a publisher identifier.

## 2. Invariants the schema cannot state

JSON Schema validates each record's shape. A conforming capture also
satisfies these, and a validator MUST check them:

1. **Partition.** `evidence[0].start == 0`; each span's `end` is the next
   span's `start`; the last span's `end` equals `textStream.codePoints`;
   each span's `end - start` equals the length of `exact` in code points;
   sha256 over the UTF-8 of the concatenated `exact` equals
   `textStream.sha256`.
2. **Ownership.** Every span id appears in exactly one node's or one
   unresolved region's `evidence`.
3. **Tree.** `nodes[0]` is the root (`kind` `document`, `parent` null);
   every other node's `parent` names an earlier node; `depth` is the
   parent's plus one; siblings' `ordinal` values are dense from 0.
4. **Leaf text.** A node with no children carries `text` equal to the
   concatenation of its spans' `exact` in order; a node with children
   carries no `text`. A container's own spans are whitespace or separators;
   citable text always sits on a leaf.
5. **Kind namespace.** A node `kind` is a core kind or `<profile.name>:<Kind>`
   where the profile's schema enumerates `<Kind>`.

A leaf's spans need not be contiguous in the stream (a reconstructed
paragraph interrupted by page furniture is one leaf); the fragment rendering
below handles both cases.

## 3. Binding a node to a SourceFragment

Any leaf renders as two `rkaf:SourceFragment` records, both with
`rkaf:fragmentContentDigest` over the leaf's `text`:

- **Stream fragment.** `oa:hasSource` is `textStream.iri`;
  `rkaf:sourceArtifactDigest` is `textStream.sha256`; one
  `oa:TextPositionSelector` in `rkaf:unicode-codepoint` per contiguous run
  of the leaf's spans, plus an `oa:TextQuoteSelector` whose `oa:exact` is the
  text. A leaf with one run also denotes the carrier-local URN
  `urn:rkaf:fragment:<encoded textStream.iri>:<start>:<end>:sha256-<digest>`
  exactly as §4.2 defines it.
- **Rendition fragment.** `oa:hasSource` is `artifact.iri`;
  `rkaf:sourceArtifactDigest` is `artifact.sha256`; selectors from the
  artifact's own coordinates: `oa:XPathSelector` over `source.path` and an
  `oa:TextPositionSelector` in `rkaf:utf8-byte` for markup, an
  `oa:FragmentSelector` conforming to RFC 8118 (`page=N&viewrect=...`, in
  permille) for a page region, `rkaf:uslm-section` for the enclosing USLM
  identifier when the family states one; always an `oa:TextQuoteSelector`.

A container is cited through its leaves. Nothing in a capture is an
`rkaf:EvidenceBinding`: binding a fragment to an assertion stays with the
product that makes the assertion.

## 4. The composition rule

A family profile is a JSON Schema that composes the parent. It MUST:

1. carry `x-parent` with the parent's `$id` and the sha256 of the parent's
   bytes it was written against;
2. be exactly `allOf: [{"$ref": <parent $id>}, <own narrowing>]`;
3. in its own narrowing, touch only `properties.profile` (narrowing `name`
   to a constant, `version` to a constant, and `ext` to its closed
   document-level block) and `properties.nodes.items.allOf`, whose clauses
   narrow only node `kind` (an `if` on the `^<name>:` pattern, `then` an
   enum of the family's kinds) and node `ext` (the family's closed per-node
   block).

It MUST NOT restate, loosen or tighten any other parent field. The check is
mechanical: `tools/test_document_capture_schema.py::check_profile_composition`
here, and the same function beside the profiles in SpicyDocs. A capture
validates against the parent and its profile, and records both pins in
`schema` and `profile.schema`.

## 5. What this is not

- Not a segmentation. DocSpec's segments and Rulespec's semantic units are
  consumers of a capture, and §4.2's rule stands: a processing segment is
  not a `SourceFragment` unless it is a stable, meaningful region.
- Not an interpretation. No node kind, field or profile states what a
  passage requires, permits or defines.
- Not an artifact container. A capture travels inside a release the way any
  product-owned JSON does under `platform-artifacts.md`; its own identity is
  content-derived (`capture.id`) but it claims no release, tag or seal.
- Not an identity value. Style sizes are floats; only the digests are
  admissible to canonical identity JSON, and page boxes are integer permille
  for that reason.

## 6. Files

| File | What |
| --- | --- |
| `release-records/schemas/document-capture-v1.schema.json` | The parent schema |
| `release-records/fixtures/document-capture-v1/minimal-valid.json` | The smallest conforming capture, pinning the parent |
| `release-records/fixtures/document-capture-v1/profile-example.schema.json` | The smallest conforming profile |
| `tools/test_document_capture_schema.py` | Metaschema check, fixture validation, negative controls, the composition rule and its refusals |

Run the check through the tooling runner the Makefile uses:

```sh
uv run --no-project --python 3.12 --with-requirements requirements.txt python -m unittest tools.test_document_capture_schema
```

The worked conversions that prove the shape fits six renditions, and the
design record, are in SpicyDocs:
`docs/research/document-capture-schema-2026-09-19.md`.
