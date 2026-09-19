# Rulespec release records

This directory contains closed JSON Schemas and offline conformance fixtures
for the independent Rulespec Core and Rulespec Extrapolator release units. See
[`spec/rulespec-releases.md`](../spec/rulespec-releases.md) for the normative
identity and validation rules.

`fixtures/upstream/` holds a byte-for-byte publisher-owned `DocumentRelease`.
Rulespec pins and validates that copy; it does not own its contents. The
bundled `m2-input-releases.json` repeats the document record so the portable
validator can consume one JSON input file. `fixtures/rulespec-atlas-membership-stub/`
is a separate, rulespec-authored fixture (not vendored from anywhere — see
[`tools/atlas_membership_stub.py`](../tools/atlas_membership_stub.py)) that
implements the `AtlasMembershipReader` Protocol the validators require. The
ExtrapolationRelease pins the atlas asset and the exact
`ReferenceResourceRelease` used by its assignments.

`m2-extrapolation-release-positive.json`, `m2-negative-controls.json`, and the
stub atlas fixture are deterministic generated fixtures. Rebuild them with:

```sh
python3 tools/build_rulespec_release_fixtures.py all --write
```

`extrapolation-release-v2/` contains the partitioned scale-format corpus. Its
valid case carries all four active-document dispositions; each sealed invalid
case names the first common verification code a producer and consumer must
return. Rebuild it from a reviewed, publisher-owned `DocumentRelease` v3 copy:

```sh
python3 tools/build_extrapolation_release_v2_fixtures.py \
  --document-release /path/to/document-release-v3 \
  --write
```

Verify the copied bundle without a sibling source checkout:

```sh
python3 -m tools.extrapolation_release_v2 validate \
  release-records/fixtures/extrapolation-release-v2/valid \
  --document-release release-records/fixtures/upstream/spicyregs-document-release-v3 \
  --vocabulary-atlas release-records/fixtures/rulespec-atlas-membership-stub
```

The v2 tool uses `rulespec_artifacts` for canonical JSON bytes and strict
loading. Its Python encoder accepts the owner's string-keyed mappings and
list/tuple sequences; parsed manifests remain JSON objects and arrays.
Refusals retain structured owner details inside the existing release issue
code and file path. Release IDs and accepted manifest bytes stay unchanged.
Embedded v1 records retain their separate finite-float JSON rules.

The version 2 root and row schemas live under
`release-records/schemas/extrapolation-release-v2*`. Version 1 keeps its current
single-JSON schema, fixtures, and validator path.

`schemas/document-capture-v1.schema.json` is the parent schema for a captured
federal document (structure, exact text, provenance), composed per document
family by SpicyDocs profiles; see [`spec/document-capture.md`](../spec/document-capture.md).
`fixtures/document-capture-v1/` holds the smallest conforming capture and
profile, and `tools/test_document_capture_schema.py` checks both, the negative
controls and the composition rule:

```sh
uv run --no-project --python 3.12 --with-requirements requirements.txt python -m unittest tools.test_document_capture_schema
```

To refresh the publisher-owned document fixture, provide the reviewed path:

```sh
python3 tools/build_rulespec_release_fixtures.py all --write \
  --vendor-document-release /path/to/document-release.json
```

Every checked-in release has `release_status=fixture` or is a copied upstream
fixture. These files do not claim a tag, package publication, deployment, or
activation.

The checked stub atlas is authored by this repository's own tooling, not
vendored from any publisher; see
[`tools/atlas_membership_stub.py`](../tools/atlas_membership_stub.py). A real
deployment pins and validates an external, product-owned atlas the same way,
by supplying its own reader for the shared `AtlasMembershipReader` Protocol —
Rulespec's validators only ever see that Protocol, never a concrete format.
These checked files are fixture provenance, not proof that the complete
cross-product publication gate has run.

`fixtures/upstream/refspec-atlas-conformance/` — a byte-for-byte copy of the
conformance corpus RefSpec published at `bindings/atlas/1.0/fixtures/` — was
removed 2026-08-09. RefSpec retired that binding
(`refactor(atlas): retire Atlas 1.0 and 2.0`), so the corpus this copy vendored
no longer exists upstream. The machine-adjudication independence and
complete-support-retention semantics it exercised are ported to rulespec's own
`#MachineAdjudicationProof` contract
(`constraints/analysis/machine-adjudication.cue`) with SHACL fixtures under
`fixtures/edges/` and `fixtures/negatives/`; see `tools/README.md`.
