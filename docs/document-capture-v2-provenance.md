# Capture v2 provenance: RS1 design and compatibility

Rulespec adds explicit, opt-in v2 capture resources. The two v1 schema files and existing no-argument resource APIs remain unchanged. A v1 capture is neither silently upgraded nor newly declared fully proven. SpicyDocs owns family declarations and conversion; Rulespec owns the shared fields and their checks.

The retained population is seven captures: bill XML, CFR reconstruction, committee-report HTML, Federal Register XML, public-law XML, Supreme Court PDF, and a Senate PDF page cut. Their eleven known evidence gaps remain findings: two incomplete acquisition timestamps, three absent MODS records, and six unobserved Senate cell boxes. RS1 also reports the public-law archive relationship as pending RS2.

## Shared representation

`provenance` holds `acquisitionKind` (`direct`, `derived`, or `archive-member`), `sourceRecords`, `renditionReason`, and `ruleBindings`. Optional `govinfoIdentity` and `derivedFrom` apply only where stated or required by the pinned profile.

A `SourceRecord` names its own retained receipt or metadata bytes through `artifact` (digest, byte size, media type and locator), plus a selector. An acquisition record separately describes `observedArtifact`: the publisher bytes, URL and acquisition timestamp stated by that receipt. This separates a receipt's digest from the digest of the PDF/XML it describes. MODS records keep explicit package/granule identity, exact identity paths and ordered literal source fields. The shared validator checks the declared binding; the family owner still interprets its publisher metadata.

`derivedFrom` names the original artifact using the existing Artifact shape, a method, and explicit derived-page/source-page pairs. The Senate cut remains the captured artifact. Its original's URL and acquisition time belong to the original; they cannot be relabeled as observations of the cut. The relationship follows the existing rkaf Artifact / PROV derivation semantics. RS2 will add the archive/member relationship beside this using the same byte-evidence shape; archive extraction is not disguised as page derivation.

`ruleBindings` declare a rule id/version bound by a digest to the existing converter's id, version, implementation and dependencies. A Decision carries the same rule id/version. This records a versioned rule binding without duplicating the converter manifest or inventing a package identity for a function. Any changed converter/dependency pin makes an unchanged binding fail. A producer still owns the truth of the rule version; the validator cannot prove source-code semantics from a string.

The native heading captures require one small field-origin distinction: a present heading `level` states its origin as `publisher`, `rule`, `model`, or `generated`. The last three require a Decision even on a native node. Nodes generated without a source structure use the explicit `generated` derivation in v2. Deleting a Decision therefore cannot erase the independent evidence that one is required.

## Requirements and validation

The v2 profile meta-schema permits a finite `x-provenance` declaration: `acquisition`, `govinfo`, `mods`, `pdf-intermediate`, `coordinates`, `page-dimensions`, `decisions`, `rule-bindings`, and `rendition-reason`. These select shared checks, not arbitrary parent-field overrides. The family owner decides applicability; GovInfo is never universally required. The capture cannot weaken its pinned profile declaration.

Shape validation, existing tree/text invariants, provenance checks, and optional retained-byte checks remain distinct. Provenance findings carry stable codes and JSON paths. A date-only timestamp is retained as incomplete evidence; no midnight is manufactured. Effective source coordinates include defaults. Ordered byte ranges and page boxes, page dimensions and PDF cell identity are validated where required. Missing observations remain findings even when an issue explains them.

The package performs no acquisition or implicit filesystem access. A byte-validation caller supplies the exact bytes for a stated artifact; acquisition assertions require independent URL observations supplied by the caller. Equal local file hashes alone do not prove that an unrelated URL names those bytes.

## Migration and packaging

The implementation ships v1 and v2 schemas, explicit versioned resource readers, and the shared checker in `rulespec-artifacts` 1.1.0, retaining its empty dependency closure. Source captures and their v1 schemas are not changed by RS1. A replay outside the source repository copies the seven captures, moves known family provenance to shared fields, pins v2/profile resources, and records every transformation. The migration preserves all artifact descriptors, text-stream digests, text, coordinates and structural identity. Rule versions created by this migration are explicitly tied to the retained converter version, not asserted to have existed in the legacy capture.

Positive controls use observed complete evidence. Negative controls remove or mismatch pins, timestamps, pair scope, metadata bindings, derived-original identities, effective coordinates, dimensions, decisions and rule bindings. Complete records pass only when applicable evidence exists; legacy incomplete records remain incomplete. The parent and profile schema, validator and wheel resources are checked together through the repository Makefile. RS2 archive/member behavior is a separate unit.

## Retained proof and limits

The migration covers all seven selected captures: 934 nodes and 2,444 evidence spans. Federal Register and Supreme Court examples have no shared provenance findings. The other cases retain the eleven known findings; the public-law case also has `archive-member-pending`. The Senate example fails six v2 shape requirements for the same unobserved cell boxes. It is an explicit incomplete fixture, not a passing example with fabricated geometry.

An independent decoding of eight retained receipts compares 39 URL, digest, size, media-type and available timestamp fields. Exact bytes are checked for the six available captured originals, the Senate original PDF and cut, metadata, receipts, PDF intermediates, and the public-law ZIP observation. The CFR original PDF is unavailable in the named local source/corpus locations. Its intermediate is retained and byte-verified; its receipt contains no acquisition time. The original date-only claim remains unchanged and unproven. The committee-report README supplies a date but no full timestamp.

The original committee-report README digest was recovered from the capture's recorded converter revision because the current README has changed. It was not repinned to current bytes. A negative control gives the locally valid public-law XML the ZIP URL; the byte check correctly rejects that URL association even though the XML digest still matches its local file.

Replay scripts, original capture copies, pinned receipt copies, native byte results and gate logs are retained under `~/Work/corpora/supply-2026-09-02/receipts/remaining-gaps-wave1-2026-09-21/rs1/`. `migration-results.json` and `native-byte-results.json` record exact input/output hashes and evidence paths. The copied profiles remain Rulespec review fixtures: SpicyDocs has not adopted or published them. Selector interpretation and any new acquisition stay with that owner.
