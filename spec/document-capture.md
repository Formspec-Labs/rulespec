# Document capture

**Status:** Draft schema, version 1, under architecture review. Owner ruling
of 2026-09-19 in [`docs/decisions.md`](../docs/decisions.md), amended the same
day after the architecture and visual reviews.

One JSON shape captures a federal document in whatever rendition it arrived
in: its structure as a tree of nodes, its exact text as an ordered partition
of evidence spans, and the provenance of both. Any node can be cited as a
`rkaf:SourceFragment` (`rkaf-core.md` §4.2) without loss. The schema is
[`release-records/schemas/document-capture-v1.schema.json`](../release-records/schemas/document-capture-v1.schema.json)
(JSON Schema draft 2020-12), pinned by the sha256 of its bytes.

Rulespec owns the parent shape, the composition rule below, and the validator
for both, the way it owns generic container mechanics under REF-048. SpicyDocs
owns the family profiles that compose it and the converters that produce
captures. Rulespec builds no converter: a capture reaches this repository as a
document, never as a pipeline.

## 1. What a capture is

| Part | Holds | Reason |
| --- | --- | --- |
| `artifact` | Always the publisher's own bytes: digest, size, media type, a credential-free locator, publisher identifiers with their rkaf scheme | The artifact is what `oa:hasSource` names; its digest is `rkaf:sourceArtifactDigest`. A consumer that follows `locator.url` and checks `sha256` must land on the same bytes, so a derived file never takes this slot |
| `rendition.intermediate` | The extractor document between the artifact and the text stream, when one exists: its digest, media type, producer and retained path | A PDF's text order is the extractor's, not the publisher's. Naming the extractor output separately lets a PDF capture say PDF → evidence lines → stream, each once, instead of passing the extractor's JSON off as the publisher's document |
| `rendition.textStream` | A derived artifact: the text every span addresses, its digest, its length in Unicode code points, and the stated normalization from the artifact (through the intermediate, if any) to it | Code points are the unit `rkaf:carrier-local-fragment` fixes, so every leaf gets a carrier-local URN for free |
| `rendition.spanDefaults` | Span source fields constant across the whole document, stated once | A per-span `"coordinateSystem": "utf8-byte", "literal": true` is the same fact repeated once per span; hoisting it keeps a capture's size proportional to its text rather than to its span count |
| `nodes` | The structure: document, front and back matter, divisions, sections with designations, headings with levels, paragraphs, lists, quotes, tables with rows and cells, notes and footnotes, figures as references, page furniture, pages and lines | Capture is not interpretation: the vocabulary is structural, the publisher's own element name travels in `source.element`, and no node states legal meaning |
| `evidence` | The partition: contiguous, non-empty spans covering the text stream, each with its exact text and the artifact's own coordinates | Concatenating the spans reproduces the text stream; its digest is the round-trip witness, and any consumer can re-derive it |
| `unresolved` | Runs of spans no rule placed, with the issue that says why | Unplaced text survives with a reason rather than being dropped |
| `converter`, `capture`, `profile` | Who produced it (id, version, repository, revision, file digest, dependencies), when, and under which family profile pinned by digest | A capture is reproducible evidence only if its producer is named |

Every node carries `derivation`: `native` (the publisher's own structural
vocabulary), `markup` (structure the converter read off markup that is not
that vocabulary), `pdf-text` (an extractor's pages and lines) or
`reconstructed` (placed by a rule or model over extracted lines, with the
`decision` that placed it). Text a rule assembled from the exact spans (a
print wrap's hyphen dropped, small capitals restored) goes in `derived`, with
the rule named; the exact text stays in `text`.

`level` is heading depth, 1 being the highest: the depth of the unit the
heading opens, not the node's depth in the tree. Absent means unlevelled,
which is what a family states when its rendition marks no depth; it never
means level 1. A family that sets `level` at all sets it on every heading it
can derive one for, and its profile says how.

`designation` is the publisher's own printed label, verbatim. On a `page` node
that is the printed page number, not the ordinal of the page in the file: a
slip opinion restarts its printed numbering at each opinion, and a capture
that silently renumbered would be asserting something the print denies. A
`page` node may also carry `pageSize`, the displayed page's size in points,
which is what makes a permille `box` convertible back to the unit a PDF
fragment identifier states.

Two fields are derivable and therefore optional: a span's `sha256` (over its
`exact`) and a leaf's `text` (the concatenation of its spans). A producer may
state them or omit them; a validator recomputes them either way and refuses a
stated value that differs. Omitting them is how a large capture stays small
without losing anything a consumer cannot rebuild.

The `artifact.identifiers[].scheme` enum is copied from the rkaf artifact
identifier scheme enum in [`rkaf-core.md`](rkaf-core.md) §4.1 and re-pinned
with it: a scheme added or retired there moves this enum, this schema's
digest, every profile's `x-parent` pin and every capture's `schema` pin in the
same change. It is a copy because a capture must validate with no Rulespec
checkout, and it is named here so the copy is maintained rather than
discovered.

Every id is minted by the converter and the document says so
(`capture.idOrigin = generated`, `capture.idScheme = document-order`). No
consumer reads one as a publisher identifier.

## 2. Invariants the schema cannot state

JSON Schema validates each record's shape. A conforming capture also
satisfies these, and a validator MUST check them:

1. **Partition and digests.** `evidence[0].start == 0`; each span's `end` is
   the next span's `start`; the last span's `end` equals
   `textStream.codePoints`; each span's `end - start` equals the length of
   `exact` in code points; a stated span `sha256` is sha256 over the UTF-8 of
   its `exact`; sha256 over the UTF-8 of the concatenated `exact` equals
   `textStream.sha256`; and every span's effective source locator — the
   `rendition.spanDefaults` updated by the span's own `source` — states a
   `coordinateSystem`.
2. **Ownership.** Every span id appears in exactly one node's or one
   unresolved region's `evidence`, and every id in an `evidence` list names a
   span in `evidence` (a dangling citation is a defect, not a missing span).
3. **Tree.** `nodes[0]` is the root (`kind` `document`, `parent` null);
   every other node's `parent` names an earlier node; `depth` is the
   parent's plus one; siblings' `ordinal` values are dense from 0.
4. **Leaf text.** A node with no children may carry `text`, and if it does
   the value is the concatenation of its spans' `exact` in order; a node with
   children carries no `text`, and the spans it owns itself are whitespace or
   separators. Citable text always sits on a leaf.
5. **Kind namespace.** A node `kind` is a core kind or `<profile.name>:<Kind>`
   where the profile's schema enumerates `<Kind>`.

The implementation is
[`rulespec_artifacts.document_capture.check_invariants`](../packages/rulespec-artifacts/src/rulespec_artifacts/document_capture.py),
shipped in the `rulespec-artifacts` wheel beside the schema itself. It is the
one implementation: a product that produces or consumes captures imports it
rather than restating it, and it reads the core vocabulary out of the shipped
parent schema rather than keeping a second copy of the enum. It needs nothing
outside the standard library, because the wheel requires nothing.

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
  artifact's own coordinates, under the three rules below; always an
  `oa:TextQuoteSelector`.

The text stream `oa:hasSource` names is itself an `rkaf:Artifact`, and a
consumer at L1 or above materializes it rather than leaving a dangling IRI:
its identifier is `textStream.iri` under scheme `rkaf:hash-sha256`, its
`rkaf:hasContentDigest` is `sha256:<textStream.sha256>`, its media type is
`text/plain; charset=utf-8`, and it is `prov:wasDerivedFrom artifact.iri`
under the activity `textStream.normalization.id`. When
`rendition.intermediate` is present it is an `rkaf:Artifact` on the same
terms, derived from `artifact.iri` by `intermediate.producer`, and the text
stream is derived from it rather than from the artifact directly. This
expansion is the capture's, the way §4.2's carrier-local URN expansion is the
fragment's: nothing in the capture file changes, and a consumer that never
leaves the capture never needs it.

**One selector per run.** A leaf's spans may be several disjoint runs in the
artifact as well as in the stream. Emit one `oa:TextPositionSelector` per
contiguous byte run, never one selector from the minimum start to the maximum
end: a collapsed range selects the markup between the runs, so the position
selector and `rkaf:fragmentContentDigest` would describe different regions.

**XPath without a namespace context.** A capture carries an
`oa:XPathSelector` as a string, with nowhere to declare a prefix binding. An
expression naming a prefixed element (`/pLaw[1]`, `/bill[1]/dc:title[1]`)
therefore selects nothing when the document has a default namespace, and
raises an undefined-prefix error when the prefix is not bound. Emit
namespace-agnostic steps instead — `/*[local-name()='pLaw'][1]/…` — or carry
an explicit namespace map beside the selector. The publisher's own element
name is already in `source.element`, so nothing is lost.

**Page regions in the unit RFC 8118 names.** An `oa:FragmentSelector` with
`dcterms:conformsTo` RFC 8118 addresses `application/pdf` and states
`viewrect` in the default user space unit, 1/72 inch. A capture stores boxes
in integer permille, because permille integers are admissible to canonical
identity JSON and floats are not; the page's own `pageSize` in points is what
converts one to the other, which is why `page` nodes retain it. Emit the
fragment against `artifact.iri` — the PDF — with `viewrect` in points, and
emit it only when the page size is known. A family that cannot recover the
page size does not claim RFC 8118 conformance: it uses
`rkaf:partner-defined` and states the permille rule in `rdf:value`.

A container is cited through its leaves. Nothing in a capture is an
`rkaf:EvidenceBinding`: binding a fragment to an assertion stays with the
product that makes the assertion.

## 4. The composition rule

A family profile is a JSON Schema that composes the parent. The rule is
data, not a checker:
[`release-records/schemas/document-capture-profile-v1.schema.json`](../release-records/schemas/document-capture-profile-v1.schema.json),
a meta-schema a profile validates against with any JSON Schema
implementation. Every object in it is closed, so a keyword it does not name
is a refusal rather than an unnoticed tightening. A profile MUST:

1. carry `x-parent` with the parent's `$id` and the sha256 of the parent's
   bytes it was written against;
2. be exactly `allOf: [{"$ref": <parent $id>}, <own narrowing>]`;
3. in its own narrowing, touch only `properties.profile` (narrowing `name`
   to a constant, `version` to a constant, and `ext` to its closed
   document-level block) and `properties.nodes.items.allOf`, which is exactly
   three clauses in order: an `if`/`then` binding node `kind` in the
   profile's own namespace to the family's enumerated kinds; a `not` pattern
   refusing every other namespace's prefix on `kind`; and the family's closed
   per-node `ext` block.

It MUST NOT restate, loosen or tighten any other parent field. A profile with
no family kind of its own still carries all three clauses, with an empty enum.

Two bindings the meta-schema cannot state, because JSON Schema cannot read
one part of a document from another, are
`rulespec_artifacts.document_capture.check_profile_bindings`: that the
`x-parent` digest is the parent's own bytes, and that the kind pattern, every
enumerated kind and the refusal pattern all carry the profile's own declared
name. That is the whole of the code; the shape is the schema.

This replaces a hand-written whitelist over `properties` keys that lived here
and in a second copy beside the SpicyDocs profiles. Seven tightenings a
profile must not make — `else` on a node clause, `required` or
`additionalProperties: false` or `not` on the narrowing, `required` on
`profile`, a `then` loosening `kind` to any string, `minItems` on `nodes` —
passed both copies, five of them changing what a capture validated as, and
the two copies had already drifted from each other. Each is now a negative
control in `tools/test_document_capture_schema.py`.

A capture validates against the parent and its profile, and records both pins
in `schema` and `profile.schema`.

## 5. What this is not

- Not a segmentation. DocSpec's segments and Rulespec's semantic units are
  consumers of a capture, and §4.2's rule stands: a processing segment is
  not a `SourceFragment` unless it is a stable, meaningful region.
- Not an interpretation. No node kind, field or profile states what a
  passage requires, permits or defines.
- Not an artifact container. A capture travels inside a release the way any
  product-owned JSON does under `platform-artifacts.md`; its own identity is
  content-derived (`capture.id`) but it claims no release, tag or seal.
- Not an identity value. Style sizes and page sizes are floats; only the
  digests are admissible to canonical identity JSON, and page boxes are
  integer permille for that reason.

## 6. Files

| File | What |
| --- | --- |
| `release-records/schemas/document-capture-v1.schema.json` | The parent schema |
| `release-records/schemas/document-capture-profile-v1.schema.json` | The profile meta-schema: the composition rule as data |
| `packages/rulespec-artifacts/src/rulespec_artifacts/document_capture.py` | The invariant validator and the two profile bindings a schema cannot state |
| `release-records/fixtures/document-capture-v1/minimal-valid.json` | The smallest conforming capture, pinning the parent and its profile |
| `release-records/fixtures/document-capture-v1/profile-example.schema.json` | The smallest conforming profile |
| `tools/test_document_capture_schema.py` | Metaschema check, fixture validation, the schema and invariant negative controls, and the composition refusals including the seven probes |

Both schemas and this spec ship in the `rulespec-artifacts` wheel's `_data`
(`resources.document_capture_schema_bytes`,
`resources.document_capture_profile_schema_bytes`,
`resources.document_capture_spec`), so a consumer imports them rather than
copying a checkout. A consumer that must vendor a copy pins it by the sha256
of the shipped bytes and checks that pin against the wheel's.

Run the check through the tooling runner the Makefile uses:

```sh
make test-document-capture
# or directly
uv run --no-project --python 3.12 --with-requirements requirements.txt python -m unittest tools.test_document_capture_schema
```

`make test` runs it.

The worked conversions that prove the shape fits six renditions, and the
design record, are in SpicyDocs:
`docs/research/document-capture-schema-2026-09-19.md`.

## 7. V2 shared provenance (RS1)

V2 is an explicit opt-in. `document_capture_schema_bytes(2)` and
`document_capture_profile_schema_bytes(2)` read the v2 resources shipped in the
artifacts wheel. Their no-argument forms still return the exact v1 bytes. Existing
v1 captures and profiles remain valid under v1; their validation does not establish
v2 provenance completeness. An upgrade creates a separately identified capture
and pins the v2 parent and its composed v2 profile.

The v2 parent adds `provenance`. Its source records distinguish retained receipt
or metadata bytes (`artifact`, with a selector) from the publisher object an
acquisition receipt describes (`observedArtifact`). Both have byte digest, size,
media type and locator. `govinfoIdentity` represents package and granule scope
explicitly; a package has `granuleId: null`, while a granule has a nonempty id.
MODS records retain the observed identity paths and literal source fields.
SpicyDocs owns their interpretation and family applicability.

`acquisitionKind: derived` requires `derivedFrom`: the original Artifact, method,
and explicit derived-page/source-page mapping. The page cut keeps its own byte
identity. It does not inherit the original's publisher URL or acquisition time.
An optional generation time is a separate observation. `archive-member` reserves
the seam for RS2 and currently returns `archive-member-pending`; v2 does not yet
qualify a shared archive/member proof.

`ruleBindings` pair a rule id/version with `converterSha256`, the SHA-256 digest
of the existing converter manifest encoded by `canonical_json_bytes`. Decisions
and derived text identify that rule version. A changed converter or dependency
invalidates an unchanged binding. Generated structure uses `derivation: generated`.
When a node has `level`, `levelOrigin` names `publisher`, `rule`, `model`, or
`generated`; the last three require a Decision even when the structure itself is
native. These fields describe the observed conversion, not a new extraction
model or independent proof that a producer's declared rule version is truthful.

The v2 profile meta-schema adds a finite `x-provenance` list: `acquisition`,
`govinfo`, `mods`, `pdf-intermediate`, `coordinates`, `page-dimensions`,
`decisions`, `rule-bindings`, and `rendition-reason`. Family profiles select the
applicable checks and pin them by profile digest; they retain v1's restrictions
on overriding parent fields. The parent still requires a structurally complete
provenance record and explicit PDF intermediate even if a profile omits a check.

Validate the parent, profile meta-schema and composed profile with JSON Schema;
then call `check_invariants(capture, parent_schema=document_capture_schema(2))`
and `document_capture_provenance.check_provenance(capture, profile_bytes=...)`.
The latter verifies pins and cross-field bindings, returning code/path findings.
It does not replace shape validation. Date-only acquisition times and absent
geometry remain incomplete evidence; an issue explaining them does not waive a
requirement. Coordinates include effective span defaults.

`check_retained_evidence` separately accepts a caller-owned byte reader and
independently retained URL observations. It compares digest, size, URL byte
identity, and the recorded acquisition timestamp without changing its precision.
It performs no acquisition, implicit path resolution or receipt parsing. Exact
receipt bytes establish the evidence being cited; publisher-specific code must
still check that a selector and metadata interpretation agree with those bytes.

The seven migration fixtures under
`release-records/fixtures/document-capture-v2/retained/` are review examples, not
published SpicyDocs profiles or assertions that incomplete records pass. Their
manifest records exact input/output hashes, field-origin changes, text-stream
digests, and findings. The [RS1 design record](../docs/document-capture-v2-provenance.md)
explains reuse, migration and the archive seam. `make test-document-capture`
validates both versions, and `make test-package-artifacts` checks the installed
wheel outside the checkout.
