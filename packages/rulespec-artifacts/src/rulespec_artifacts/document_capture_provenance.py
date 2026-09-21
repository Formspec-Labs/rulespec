"""Opt-in DocumentCapture v2 provenance checks, with no acquisition or implicit I/O.

Validate the parent/profile schemas and document_capture.check_invariants too.
This module checks cross-field evidence bindings; findings never become passes
because an issue explains an absent observation. Family policy lives in the
pinned profile's finite x-provenance declaration, not a family-name registry.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any

from . import resources
from ._artifact import canonical_json_bytes
from .document_capture import check_profile_bindings, effective_source

__all__ = [
    "check_provenance",
    "check_retained_evidence",
    "converter_digest",
    "full_timestamp",
]


def converter_digest(converter: Mapping[str, Any]) -> str:
    """Bind rule versions to the existing converter manifest, without a new identity codec."""
    return hashlib.sha256(canonical_json_bytes(dict(converter))).hexdigest()


def full_timestamp(value: Any) -> bool:
    """Seconds and timezone are required; recorded fractional precision is preserved."""
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return False
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def _byte_pin(value: Mapping[str, Any]) -> bool:
    locator = value.get("locator") or {}
    return bool(
        re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", "")))
        and type(value.get("byteSize")) is int
        and value["byteSize"] >= 0
        and isinstance(value.get("mediaType"), str)
        and value["mediaType"]
        and (locator.get("path") or locator.get("url"))
    )


def _coordinate(source: Mapping[str, Any]) -> bool:
    system = source.get("coordinateSystem")
    if system == "none":
        return True
    if system == "xml-node-path":
        return isinstance(source.get("path"), str) and bool(source["path"])
    if system == "utf8-byte":
        return (
            type(source.get("start")) is int
            and type(source.get("end")) is int
            and 0 <= source["start"] <= source["end"]
        )
    if system == "page-region":
        box = source.get("box")
        return bool(
            type(source.get("page")) is int
            and source["page"] > 0
            and isinstance(box, list)
            and len(box) == 4
            and all(type(v) is int and 0 <= v <= 1000 for v in box)
            and box[0] <= box[2]
            and box[1] <= box[3]
        )
    return False


def _pair(value: Mapping[str, Any]) -> tuple | None:
    package, granule, scope = (
        value.get("packageId"),
        value.get("granuleId"),
        value.get("scope"),
    )
    if not isinstance(package, str) or not package or "granuleId" not in value:
        return None
    if scope == "package" and granule is None:
        return package, None, scope
    if scope == "granule" and isinstance(granule, str) and granule:
        return package, granule, scope
    return None


def check_provenance(
    capture: Mapping[str, Any], *, profile_bytes: bytes
) -> list[dict[str, str]]:
    """Check v2 evidence and the exact pinned profile's requirement declaration.

    V1 is explicitly unsupported here, not silently upgraded. The existing v1
    shape/invariant APIs retain their meaning. Run JSON Schema validation first
    to establish the record types, and this checker for cross-field bindings.
    """
    findings: list[dict[str, str]] = []

    def need(ok: Any, code: str, path: str) -> None:
        if not ok:
            findings.append({"code": code, "path": path})

    if capture.get("captureVersion") != 2:
        return [{"code": "unsupported-provenance-version", "path": "/captureVersion"}]
    try:
        profile = json.loads(profile_bytes)
    except (ValueError, UnicodeError):
        return [{"code": "profile-unreadable", "path": "/profile/schema"}]
    if not isinstance(profile, dict):
        return [{"code": "profile-unreadable", "path": "/profile/schema"}]
    parent_bytes = resources.document_capture_schema_bytes(2)
    parent = json.loads(parent_bytes)
    pin = {"$id": parent["$id"], "sha256": hashlib.sha256(parent_bytes).hexdigest()}
    need(capture.get("schema") == pin, "parent-pin", "/schema")
    need(
        capture.get("profile", {}).get("schema")
        == {
            "$id": profile.get("$id"),
            "sha256": hashlib.sha256(profile_bytes).hexdigest(),
        },
        "profile-pin",
        "/profile/schema",
    )
    need(
        not check_profile_bindings(
            profile, parent_id=pin["$id"], parent_digest=pin["sha256"]
        ),
        "profile-parent-binding",
        "/profile/schema",
    )
    try:
        declaration = profile["allOf"][1]["properties"]["profile"]["properties"]
        need(
            all(
                capture["profile"].get(key) == declaration[key]["const"]
                for key in ("name", "version")
            ),
            "profile-identity",
            "/profile",
        )
    except (KeyError, IndexError, TypeError):
        need(False, "profile-identity", "/profile")
    requested = profile.get("x-provenance")
    known = set(parent["$defs"]["ProvenanceRequirement"]["enum"])
    if (
        not isinstance(requested, list)
        or not requested
        or any(not isinstance(x, str) or x not in known for x in requested)
    ):
        need(False, "profile-requirements", "/profile/schema")
        return findings
    requirements = set(requested)
    provenance = capture.get("provenance") or {}
    artifact = capture.get("artifact") or {}
    kind = provenance.get("acquisitionKind")
    source = artifact
    source_path = "/artifact"
    if kind == "derived":
        relationship = provenance.get("derivedFrom") or {}
        source = relationship.get("artifact") or {}
        source_path = "/provenance/derivedFrom/artifact"
        need(
            bool(relationship.get("method")) and _byte_pin(source),
            "derived-artifact",
            "/provenance/derivedFrom",
        )
        if "generatedAt" in relationship:
            need(
                full_timestamp(relationship["generatedAt"]),
                "generation-timestamp",
                "/provenance/derivedFrom/generatedAt",
            )
        need(
            source.get("sha256") != artifact.get("sha256"),
            "derived-artifact-identity",
            "/provenance/derivedFrom/artifact/sha256",
        )
        original_url = source.get("locator", {}).get("url")
        need(
            not original_url or artifact.get("locator", {}).get("url") != original_url,
            "derived-original-url",
            "/artifact/locator/url",
        )
        need(
            not source.get("retrievedAt")
            or artifact.get("retrievedAt") != source.get("retrievedAt"),
            "derived-original-timestamp",
            "/artifact/retrievedAt",
        )
        mapping = relationship.get("sourcePages") or []
        derived_pages = [item.get("derivedPage") for item in mapping]
        need(
            bool(mapping)
            and len(derived_pages) == len(set(derived_pages))
            and all(
                type(item.get(name)) is int and item[name] > 0
                for item in mapping
                for name in ("derivedPage", "sourcePage")
            ),
            "derived-page-map",
            "/provenance/derivedFrom/sourcePages",
        )
        used = {
            s.get("page")
            for s in [
                *(n.get("source", {}) for n in capture.get("nodes", [])),
                *(effective_source(capture, e) for e in capture.get("evidence", [])),
            ]
            if s.get("page") is not None
        }
        need(
            used.issubset(derived_pages),
            "derived-page-map",
            "/provenance/derivedFrom/sourcePages",
        )
    elif kind == "archive-member":
        # RS2 owns the shared exact archive/member association and byte proof.
        # No family extension is interpreted as a substitute for that contract.
        need(False, "archive-member-pending", "/provenance/acquisitionKind")
        source = {}
    else:
        need(kind == "direct", "acquisition-kind", "/provenance/acquisitionKind")
        need(
            "derivedFrom" not in provenance,
            "unexpected-derived-artifact",
            "/provenance/derivedFrom",
        )

    records = provenance.get("sourceRecords") or []
    ids: set[str] = set()
    acquisitions: list[Mapping[str, Any]] = []
    mods: list[Mapping[str, Any]] = []
    for index, record in enumerate(records):
        path = f"/provenance/sourceRecords/{index}"
        need(
            _byte_pin(record.get("artifact") or {}) and bool(record.get("selector")),
            "source-record-pin",
            path,
        )
        if acquisition_evidence := record.get("acquisitionEvidence"):
            need(
                _byte_pin(acquisition_evidence.get("artifact") or {})
                and bool(acquisition_evidence.get("selector")),
                "source-record-pin",
                path + "/acquisitionEvidence",
            )
        need(
            bool(record.get("id")) and record.get("id") not in ids,
            "source-record-id",
            path + "/id",
        )
        ids.add(record.get("id"))
        if record.get("role") == "acquisition":
            acquisitions.append(record)
            observed = record.get("observedArtifact") or {}
            need(
                _byte_pin(observed),
                "acquisition-record-pin",
                path + "/observedArtifact",
            )
            if source:
                need(
                    all(
                        observed.get(k) == source.get(k)
                        for k in ("sha256", "byteSize", "mediaType", "retrievedAt")
                    )
                    and observed.get("locator", {}).get("url")
                    == source.get("locator", {}).get("url"),
                    "acquisition-record-mismatch",
                    path + "/observedArtifact",
                )
        elif record.get("role") == "mods":
            mods.append(record)
    if "acquisition" in requirements:
        need(bool(acquisitions), "acquisition-record", "/provenance/sourceRecords")
        inspected_sources = (
            [source]
            if source
            else [r.get("observedArtifact", {}) for r in acquisitions]
        )
        for index, acquired in enumerate(inspected_sources):
            path = (
                source_path
                if source
                else f"/provenance/sourceRecords/{index}/observedArtifact"
            )
            need(
                bool(
                    re.fullmatch(
                        r"https?://\S+", str(acquired.get("locator", {}).get("url", ""))
                    )
                ),
                "publisher-url",
                path + "/locator/url",
            )
            need(
                full_timestamp(acquired.get("retrievedAt")),
                "retrieval-timestamp",
                path + "/retrievedAt",
            )
    if "rendition-reason" in requirements:
        need(
            bool(provenance.get("renditionReason")),
            "rendition-reason",
            "/provenance/renditionReason",
        )
    identity = provenance.get("govinfoIdentity") or {}
    if "govinfo" in requirements or identity:
        need(
            _pair(identity) is not None and bool(identity.get("basis")),
            "govinfo-pair",
            "/provenance/govinfoIdentity",
        )
    if "mods" in requirements:
        need(bool(mods), "mods-record", "/provenance/sourceRecords")
    for record in mods:
        index = records.index(record)
        need(
            _pair(identity) is not None
            and _pair(record.get("govinfoIdentity") or {}) == _pair(identity)
            and bool(record.get("identityPaths")),
            "mods-identity-binding",
            f"/provenance/sourceRecords/{index}",
        )
    rendition = capture.get("rendition") or {}
    if "pdf-intermediate" in requirements and rendition.get("kind") == "pdf":
        intermediate = rendition.get("intermediate") or {}
        need(
            _byte_pin(intermediate) and bool(intermediate.get("producer")),
            "pdf-intermediate",
            "/rendition/intermediate",
        )

    pages: set[int] = set()
    for path, value in [
        *(
            (f"/nodes/{i}/source", node.get("source") or {})
            for i, node in enumerate(capture.get("nodes", []))
        ),
        *(
            (f"/evidence/{i}/source", effective_source(capture, span))
            for i, span in enumerate(capture.get("evidence", []))
        ),
    ]:
        if type(value.get("page")) is int:
            pages.add(value["page"])
        if "coordinates" in requirements:
            need(_coordinate(value), "coordinate-fields", path)
    if "page-dimensions" in requirements:
        sizes: dict[int, Mapping[str, Any]] = {}
        for index, size in enumerate(provenance.get("pageSizes", [])):
            need(
                size["page"] not in sizes,
                "duplicate-page-dimensions",
                f"/provenance/pageSizes/{index}",
            )
            sizes[size["page"]] = {k: size[k] for k in ("width", "height", "unit")}
        for index, node in enumerate(capture.get("nodes", [])):
            if node.get("kind") != "page":
                continue
            page, size = node.get("source", {}).get("page"), node.get("pageSize") or {}
            if page in sizes and size:
                need(
                    sizes[page] == size,
                    "conflicting-page-dimensions",
                    f"/nodes/{index}/pageSize",
                )
            if size:
                sizes[page] = size
        for page in sorted(pages):
            size = sizes.get(page) or {}
            need(
                size.get("unit") == "point"
                and all(
                    type(size.get(k)) in (int, float) and 0 < size[k] < float("inf")
                    for k in ("width", "height")
                ),
                "page-dimensions",
                f"/page/{page}",
            )
    binding_digest = converter_digest(capture.get("converter") or {})
    bindings: dict[tuple, Mapping[str, Any]] = {}
    for index, binding in enumerate(provenance.get("ruleBindings") or []):
        key = (binding.get("id"), binding.get("version"))
        need(
            key not in bindings,
            "duplicate-rule-binding",
            f"/provenance/ruleBindings/{index}",
        )
        bindings[key] = binding
        need(
            binding.get("converterSha256") == binding_digest,
            "stale-rule-binding",
            f"/provenance/ruleBindings/{index}/converterSha256",
        )
    for index, node in enumerate(capture.get("nodes", [])):
        path = f"/nodes/{index}"
        required = node.get("derivation") in {
            "markup",
            "pdf-text",
            "reconstructed",
            "generated",
        } or node.get("levelOrigin") in {"rule", "model", "generated"}
        decision = node.get("decision") or {}
        if "level" in node:
            need(
                node.get("levelOrigin") in {"publisher", "rule", "model", "generated"},
                "field-origin",
                path + "/levelOrigin",
            )
        if "decisions" in requirements and required:
            need(
                bool(decision.get("method")) and bool(decision.get("rule")),
                "derived-node-decision",
                path + "/decision",
            )
        if "rule-bindings" in requirements and decision:
            need(
                (decision.get("rule"), decision.get("ruleVersion")) in bindings,
                "decision-rule-binding",
                path + "/decision",
            )
        if "rule-bindings" in requirements and (derived := node.get("derived")):
            need(
                (derived.get("rule"), derived.get("ruleVersion")) in bindings,
                "derived-text-rule-binding",
                path + "/derived",
            )
        if (
            "coordinates" in requirements
            and rendition.get("kind") == "pdf"
            and node.get("kind") == "cell"
        ):
            cell = node.get("cell") or {}
            need(
                all(
                    type(cell.get(k)) is int and cell[k] >= 0 for k in ("row", "column")
                ),
                "pdf-cell-identity",
                path + "/cell",
            )
    return findings


def check_retained_evidence(
    capture: Mapping[str, Any],
    *,
    read_bytes: Callable[[Mapping[str, Any]], bytes],
    observations: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Verify stated byte pins and URLs against explicitly supplied retained evidence.

    read_bytes resolves exactly the supplied artifact; it is caller-owned and
    may refuse unavailable bytes. No URL fetch, path guess, or receipt parsing
    occurs here. observations maps exact publisher URLs to independently retained
    sha256/byteSize/mediaType/retrievedAt values, preserving timestamp precision.
    This checks evidence association, not the semantics of arbitrary selectors.
    """
    findings: list[dict[str, str]] = []
    provenance = capture.get("provenance") or {}
    artifacts = [("/artifact", capture.get("artifact") or {})]
    if derived := provenance.get("derivedFrom"):
        artifacts.append(
            ("/provenance/derivedFrom/artifact", derived.get("artifact") or {})
        )
    if intermediate := capture.get("rendition", {}).get("intermediate"):
        artifacts.append(("/rendition/intermediate", intermediate))
    for index, record in enumerate(provenance.get("sourceRecords") or []):
        artifacts.append(
            (
                f"/provenance/sourceRecords/{index}/artifact",
                record.get("artifact") or {},
            )
        )
        if acquisition_evidence := record.get("acquisitionEvidence"):
            artifacts.append(
                (
                    f"/provenance/sourceRecords/{index}/acquisitionEvidence/artifact",
                    acquisition_evidence.get("artifact") or {},
                )
            )
        if observed := record.get("observedArtifact"):
            artifacts.append(
                (f"/provenance/sourceRecords/{index}/observedArtifact", observed)
            )
    for path, artifact in artifacts:
        try:
            data = read_bytes(artifact)
        except (OSError, KeyError, ValueError):
            findings.append({"code": "retained-bytes-unavailable", "path": path})
        else:
            if hashlib.sha256(data).hexdigest() != artifact.get("sha256") or len(
                data
            ) != artifact.get("byteSize"):
                findings.append({"code": "retained-bytes-mismatch", "path": path})
        if url := artifact.get("locator", {}).get("url"):
            observed = observations.get(url)
            if observed is None:
                findings.append(
                    {"code": "artifact-url-unverified", "path": path + "/locator/url"}
                )
            elif any(
                artifact.get(k) != observed.get(k)
                for k in ("sha256", "byteSize", "mediaType")
            ):
                findings.append(
                    {
                        "code": "artifact-url-bytes-mismatch",
                        "path": path + "/locator/url",
                    }
                )
            if observed is not None and artifact.get("retrievedAt") != observed.get(
                "retrievedAt"
            ):
                findings.append(
                    {
                        "code": "artifact-acquisition-time-mismatch",
                        "path": path + "/retrievedAt",
                    }
                )
    return findings
