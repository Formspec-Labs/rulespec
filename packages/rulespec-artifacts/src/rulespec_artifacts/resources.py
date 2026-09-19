"""Installed specification and common fixture corpus."""

from __future__ import annotations

import json
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from ._artifact import parse_canonical_json


def _data() -> Traversable:
    packaged = resources.files("rulespec_artifacts") / "_data"
    if packaged.is_dir():
        return packaged
    return Path(__file__).resolve().parents[4]


def platform_artifact_spec() -> str:
    return (_data() / "spec" / "platform-artifacts.md").read_text(encoding="utf-8")


def document_capture_spec() -> str:
    return (_data() / "spec" / "document-capture.md").read_text(encoding="utf-8")


def _schema(name: str) -> Traversable:
    packaged = _data() / "schemas" / name
    if packaged.is_file():
        return packaged
    return _data() / "release-records" / "schemas" / name


def document_capture_schema_bytes() -> bytes:
    """The DocumentCapture v1 parent schema exactly as shipped.

    A consumer that vendors a copy pins it by the sha256 of these bytes, so
    read the bytes and not a re-serialization of the parsed object: a
    round trip through a JSON encoder moves the digest and the pin with it.
    """

    return _schema("document-capture-v1.schema.json").read_bytes()


def document_capture_schema() -> dict[str, object]:
    value = json.loads(document_capture_schema_bytes())
    if not isinstance(value, dict):
        raise TypeError("the document capture schema must be a JSON object")
    return value


def document_capture_profile_schema_bytes() -> bytes:
    """The profile meta-schema: the structural half of the composition rule, as data."""

    return _schema("document-capture-profile-v1.schema.json").read_bytes()


def document_capture_profile_schema() -> dict[str, object]:
    value = json.loads(document_capture_profile_schema_bytes())
    if not isinstance(value, dict):
        raise TypeError("the document capture profile meta-schema must be a JSON object")
    return value


def fixture_corpus() -> dict[str, object]:
    value = json.loads(
        (_data() / "platform-fixtures" / "corpus.json").read_text(encoding="utf-8")
    )
    if not isinstance(value, dict):
        raise TypeError("platform fixture corpus must be a JSON object")
    return value


def canonical_json_corpus() -> dict[str, object]:
    """Return the byte-exact canonical-JSON encoder corpus shipped in the wheel."""

    raw = (_data() / "platform-fixtures" / "canonical-json" / "corpus.json").read_bytes()
    value = parse_canonical_json(raw)
    if not isinstance(value, dict):
        raise TypeError("canonical-JSON fixture corpus must be a JSON object")
    return value


def fixture(name: str) -> Traversable:
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError("fixture name must be one path segment")
    target = _data() / "platform-fixtures" / "cases" / name
    if not target.is_dir():
        raise FileNotFoundError(name)
    return target
