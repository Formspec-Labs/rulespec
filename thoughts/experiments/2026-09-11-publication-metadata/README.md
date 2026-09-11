# Publication metadata experiment — checkpoint

Saved at the user's request on 2026-09-11. The reader check passed; the comparison
and production decision are **unfinished**. No application code, dependencies,
model prompts or installed wheels changed.

## What is established

The existing public `docspec.source_catalog.SourceCatalogArtifactReader` fully
verified the selected Federal Register catalog and then consumed all 93 located
rows. It preserves the row's native fields, normalized fields, interpretation
outcomes and partition blob identity. There is no need to write another metadata
normalizer merely to display these fields.

The diagnostic [first row](first-row.json), document `2026-07034`, retains:

- Publication date `2026-04-13`, comment deadline `2026-05-13`, and docket field
  `0648-XF618`, each with its normalization source path.
- An absent RIN list and absent last-updated date as explicit normalization
  outcomes. Language `en` is explicitly policy-supplied.
- Native `cfr_references: []`, the original agency objects and publisher URLs.
- A selected HTML URL with **no captured-byte digest or size**. This is a
  candidate rendition, not proof that a local body corresponds to it.

All 93 inventoried rows select a `source-url` rendition. The actual reader
verification is recorded in [admission.json](admission.json); the compact row
inventory is [inventory.json](inventory.json). Inventory does not replace the
full native rows for a downstream consumer.

The [plan](PLAN.md) was saved before collecting these results. The reader probe
is preparatory evidence, not a passed adoption gate or an accuracy measurement.

## Inputs and runtime

Catalog root:

```text
/Users/mikewolfd/Work/corpora/supply-2026-09-02/catalogs/catalog-B-slice/catalog
```

Pinned artifact digest:

```text
sha256:7add578ed4a369e666564629e3d8c35239e2bfc79ba64fac25d97c12fa2580d9
```

The command receipt's exact reference and declared historical DocSpec producer
were explicitly selected for this local experiment. This is not an automatic
production trust policy for arbitrary receipt-supplied producers.

The probe used `/Users/mikewolfd/Work/DocSpec/.venv/bin/python`, with DocSpec HEAD
`41a6b144c06c08ebaf8f57e9c7fe4c6927dff11f` recorded in `admission.json`. Runtime
module paths and byte hashes are saved there, so a version string or branch name
is not the only provenance. The sibling checkout moved after the probe; use those
captured hashes when discussing the result. The repository snapshot at saving
time is [checkpoint-repositories.json](checkpoint-repositories.json).

Replay into a fresh directory to preserve the original capture:

```sh
/Users/mikewolfd/Work/DocSpec/.venv/bin/python \
  /Users/mikewolfd/Work/rulespec/thoughts/experiments/2026-09-11-publication-metadata/catalog_probe.py \
  /tmp/rulespec-publication-metadata-replay
```

Use a different output directory if it already contains a capture. The probe now
refuses overwrites and returns a nonzero exit status on admission failure; those
two capture safeguards were added after the successful original run. It does not
install packages or fetch documents.

## Body lookup and proposed cases

Six provisional examples were selected from the metadata inventory to investigate
different mechanisms; their comparison expectations have **not** been frozen:

| Document | Reason to examine |
| --- | --- |
| `2026-07034` | Docket and deadline, absent RIN and CFR fields |
| `2026-07052` | Airbus airplane proposal, RIN `2120-AA64` |
| `2026-07101` | Airbus helicopter proposal, same RIN `2120-AA64`; must remain a different document |
| `2026-07061` | Coal combustion residuals proposal; candidate for native CFR fields |
| `2026-07088` | Delegations of Authority; RIN present, docket list absent |
| `2026-07046` | Publisher docket field contains `OMB Control No. 3235-0059`; retain the publisher field without assuming every value is a regulations.gov docket |

[body-lookup.json](body-lookup.json) records a diagnostic search of the 8,284
document rows in `DocSpec/output/document-release-10k-v3/data/documents.jsonl`.
None contains any of those six document numbers. The member's bytes and hash
are recorded. **The release was not admitted and no bodies were read.** This
establishes only that these candidates were not located in that member; it does
not establish that no matching local capture exists elsewhere.

Do not replace the selected examples with whatever happens to be present merely
to get a passing association. If a different source selection is warranted,
document the reason before comparing it and retain this lookup result.

## Owner and consumer findings

- DocSpec's public facade supplies `SourceCatalogArtifactReader`,
  `LocalSourceCatalogStore`, and located items. Import `SourceCatalogRef` from
  `docspec.domain.references`. `verify_snapshot()` runs the full build gate;
  `open_snapshot().located_items` preserves the partition digest and must be
  consumed fully. The convenience `.items` property discards the location.
- Federal Register normalization already belongs to DocSpec's
  `application/federal_register_catalog.py`. Native facts carry the fields that
  its normalized metadata does not expose; a second body parser is unnecessary
  for reading stated catalog values.
- Rulespec's `documents.prepare_document()` currently supplies source text,
  identity, title and URL. `discovery.export_discovery()` exports those source
  descriptors, not catalog metadata. Connecting arbitrary rows to those bodies
  needs an evidenced association, not a title match.
- SpicySearch's public `source_catalog_metadata.prepare_metadata_subject()` takes
  an **already verified** row and produces identifiers, facets and field-scoped
  text evidence. It was read, **not executed in this experiment**. Its evidence
  uses `decoded-json-value-utf8-byte` coordinates, not document-body offsets.
- SpicySearch's `platform_source_catalog.py` still imports the old private
  DocSpec artifact module. Current DocSpec has split those modules; its older
  vendored wheel differs from the live source. The dedicated public-reader owner
  work is DocSpec D09 / SpicySearch SC01. Do not relocate private imports or
  casually rebuild sibling dependencies to make this experiment run.
- Existing Rulespec graph functions `federal_register_facts` and
  `unified_agenda_facts` remain a separate consumer. The first-proceedings-match
  behavior previously found there is not a safe association mechanism to reuse.

## Exact resumption point

1. Recheck sibling worktrees before changes: DocSpec and SpicyDocs had unrelated
   concurrent edits at checkpoint time. Preserve them. The current experiment
   has no live process to poll.
2. Locate a captured rendition for a bounded set of these catalog records using
   existing source/release readers and identity/capture receipts. Prefer supported
   publisher XML. A URL or matching title does not prove a matching edition/body.
3. Freeze no more than six real cases and six constructed controls before the
   comparison. Include absent/malformed fields, wrong document, distinct versions,
   body/metadata disagreement and a changed artifact member. None of those
   constructed controls has been executed yet.
4. Compare the named Rulespec discovery consumer with and without existing
   catalog observations. Exercise SpicySearch's preparation directly only if the
   consumer needs its indexed identifier/text representation. Reuse owners and
   keep metadata evidence separate from body quotations.
5. Apply the original decision rule. If supported, implement the small connection,
   verify direct imports, then build/install the changed wheel and test the normal
   caller. If the association cannot be established within the bound, save the
   precise missing prerequisite. Do not call this partial reader check a completed
   production integration.

No model calls, network acquisition, production changes, wheel rebuilds, push or
deployment occurred in this experiment. R20 has new inventory evidence; R21 and
the overall reuse goal remain open.
