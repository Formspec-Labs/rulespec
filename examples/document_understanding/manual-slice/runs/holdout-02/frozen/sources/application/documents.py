"""Immutable text snapshots and source sections, independent of model windows."""
from pathlib import Path
import json

from .core import NS, digest


def prepare_document(text, *, title="Untitled document", source_url="", sections=None):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Document text must not be empty")
    sha = digest(text)
    document = {"id": NS + "document:" + sha, "sha256": sha, "text": text,
                "title": title, "source_url": source_url,
                "sections": sections or [{"id": "section-1", "label": title,
                                         "start": 0, "end": len(text)}]}
    validate_document(document)
    return document


def validate_document(document):
    text = document["text"]
    if digest(text) != document["sha256"] or document["id"] != NS + "document:" + digest(text):
        raise ValueError("Document identity or digest does not match the pinned text")
    seen = set()
    for section in document["sections"]:
        if section["id"] in seen:
            raise ValueError("Duplicate section identity")
        seen.add(section["id"])
        start, end = section["start"], section["end"]
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ValueError("Section coordinates do not resolve in the document")
    if not seen:
        raise ValueError("Document needs at least one source section")
    if "source_map" in document:
        cursor = 0
        for part in document["source_map"]:
            if type(part["start"]) is not int or type(part["end"]) is not int or not (
                part["start"] == cursor < part["end"] <= len(text)
            ):
                raise ValueError("Source map must account for every character in order")
            if part["kind"] == "source":
                if part["source_end"] - part["source_start"] != part["end"] - part["start"]:
                    raise ValueError("Source slice length differs from its prepared text")
            elif part["kind"] == "inserted":
                if text[part["start"]:part["end"]] != part["text"]:
                    raise ValueError("Inserted text differs from its source-map record")
            else:
                raise ValueError("Unsupported source-map transformation")
            cursor = part["end"]
        if cursor != len(text):
            raise ValueError("Source map does not account for every character")
    return document


def load_document(path, *, title=None, source_url=""):
    path = Path(path)
    if path.suffix == ".json":
        document = json.loads(path.read_text())
        return validate_document(document)
    return prepare_document(path.read_text(), title=title or path.stem, source_url=source_url)
