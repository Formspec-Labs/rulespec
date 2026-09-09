"""Immutable text snapshots and source sections, independent of model windows."""
from pathlib import Path
import json
import re

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
                if (type(part["source_start"]) is not int or type(part["source_end"]) is not int
                        or not 0 <= part["source_start"] < part["source_end"]
                        or not isinstance(part.get("source_id"), str) or not part["source_id"]):
                    raise ValueError("Original source coordinates must be nonnegative integers")
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
    text = path.read_bytes().decode("utf-8")
    if path.suffix == ".json":
        document = json.loads(text)
        return validate_document(document)
    return prepare_document(text, title=title or path.stem, source_url=source_url)


def source_passages(document):
    """Index exact paragraphs/list items; structural parents are not rule scope.

    Blank lines and explicit list markers supply boundaries. This bounded text
    profile recognizes dotted-letter lists with lettered grandchildren, and
    parenthesized-letter lists with numbered children and Roman grandchildren.
    It reports that method rather than claiming layout or legal-scope recovery.
    """
    validate_document(document)
    text = document["text"]
    boundaries = {0, len(text)}
    boundaries.update(m.end() for m in re.finditer(r"\r?\n[ \t]*\r?\n", text))
    boundaries.update(m.start() for m in re.finditer(r"(?m)^[ \t]*(?:[a-z]\.|\([a-z0-9]+\)|\d+\.)[ \t]+", text))
    bounds = sorted(boundaries)
    passages, parents = [], {}
    previous_section = None
    style, top_letter = None, None
    for start, end in zip(bounds, bounds[1:]):
        content = text[start:end]
        containing = [s for s in document["sections"] if s["start"] <= start and end <= s["end"]]
        section = min(containing, key=lambda s: (s["end"] - s["start"], s["id"]), default=None)
        section_id = section["id"] if section else ""
        if section_id != previous_section:
            parents = {}
            style, top_letter = None, None
        previous_section = section_id
        marker = re.match(r"\s*(?:(?P<top>[a-z])\.|\((?P<number>\d+)\)|\((?P<letter>[a-z]+)\)|(?P<plain>\d+)\.)\s+", content)
        parent = None
        if marker:
            if marker["top"] or marker["plain"]:
                style, level = "dotted", 0
            elif marker["number"]:
                level = 1
            else:
                letter = marker["letter"]
                if style == "dotted":
                    level = 2
                else:
                    style = "parenthesized"
                    next_top = top_letter is not None and len(letter) == 1 and ord(letter) == ord(top_letter) + 1
                    roman = re.fullmatch(r"x{0,3}(?:ix|iv|v?i{0,3})", letter)
                    level = 2 if roman and 1 in parents and not next_top and (
                        letter == "i" or len(letter) > 1 or 2 in parents
                    ) else 0
                    if level == 0:
                        top_letter = letter if len(letter) == 1 else None
            parent = parents.get(level - 1)
            parents = {depth: identity for depth, identity in parents.items() if depth < level}
        identity = NS + "passage:" + digest([document["id"], start, end])
        passage = {"id": identity, "start": start, "end": end, "text_sha256": digest(content),
                   "section_id": section_id, "kind": "list_item" if marker else "paragraph",
                   "parent_id": parent, "structure_method": "text-paragraphs-and-list-markers/2"}
        passages.append(passage)
        if marker:
            parents[level] = identity
    return passages


def with_context(document, window, *, context_chars=2400):
    """Keep focus coverage separate from bounded, explicitly recorded context."""
    passages = source_passages(document)
    by_id = {p["id"]: p for p in passages}
    focused = [p for p in passages if p["start"] < window["end"] and p["end"] > window["start"]]
    wanted = []
    for passage in focused:
        parent = passage["parent_id"]
        while parent:
            wanted.append(by_id[parent])
            parent = by_id[parent]["parent_id"]
        # Supply a split paragraph's lead-in and adjacent antecedents; the model
        # must decide their role, not blindly inherit this structural proximity.
        wanted.append(passage)
        index = passages.index(passage)
        if index and passages[index - 1]["section_id"] == passage["section_id"]:
            wanted.append(passages[index - 1])
        if index + 1 < len(passages) and passages[index + 1]["section_id"] == passage["section_id"]:
            wanted.append(passages[index + 1])
    spans, omitted, seen, remaining = [], [], set(), context_chars
    for passage in wanted:
        if passage["id"] in seen:
            continue
        seen.add(passage["id"])
        for lo, hi in ((passage["start"], min(passage["end"], window["start"])),
                       (max(passage["start"], window["end"]), passage["end"])):
            if hi <= lo:
                continue
            if remaining <= 0:
                omitted.append(passage["id"])
                continue
            stop = min(hi, lo + remaining)
            spans.append({"passage_id": passage["id"], "start": lo, "end": stop,
                          "text_sha256": digest(document["text"][lo:stop]), "truncated": stop < hi})
            remaining -= stop - lo
            if stop < hi:
                omitted.append(passage["id"])
    return {**window, "context_version": "document-context/1", "context_chars": context_chars,
            "passage_ids": [p["id"] for p in focused], "context_spans": spans,
            "context_omitted_passage_ids": list(dict.fromkeys(omitted))}
