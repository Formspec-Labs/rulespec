#!/usr/bin/env python3
"""Capture official manual pages once; reproduce exact text and excerpt files.

This script does not read evaluation labels or call a model. Existing artifacts
must match their pinned bytes; new source editions require a new corpus folder.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent / "corpus"
PAGES = {
    "fam-photos": ("040201", "8 FAM 402.1 Passport Photographs"),
    "fam-names": ("040301", "8 FAM 403.1 Name Usage and Name Changes"),
    "fam-responsibilities": ("010301", "8 FAM 103.1 Responsibilities"),
}
# Anchors select source text, not semantic answers. End anchors are exclusive.
SELECTION = [
    ("fam-photos-01", "development", "fam-photos", "8 FAM 402.1-1(d)", "d. Infants pose a particular challenge.", "e. Because minors do not typically submit identification,"),
    ("fam-photos-02", "development", "fam-photos", "8 FAM 402.1-2(1)-(2)", "You must request a new photograph if the photograph submitted", "(3) The photograph should be 2” x 2”"),
    ("fam-photos-03", "development", "fam-photos", "8 FAM 402.1-2(6)", "(6) The photograph must be free of material damage:", "8 FAM 402.1-3 Quality of Photographs"),
    ("fam-photos-04", "development", "fam-photos", "8 FAM 402.1-4(e)(1)", "e. Eyeglasses/contact lenses:", "(2) Clear contact lenses are acceptable."),
    ("fam-photos-05", "development", "fam-photos", "8 FAM 402.1-5", "8 FAM 402.1-5 Facial Expression", "8 FAM 402.1-6 Religious Objections to Photograph Requirements"),
    ("fam-photos-06", "development", "fam-photos", "8 FAM 402.1-8(a)", "a. Applications received without photographs:", "b. You must examine photographs"),
    ("fam-names-01", "holdout", "fam-names", "8 FAM 403.1-1(b)(1) note", "NOTE: The term “applicant” is used hereinafter", "(2) To facilitate the passage of the applicant"),
    ("fam-names-02", "holdout", "fam-names", "8 FAM 403.1-4(a)-(c)", "8 FAM 403.1-4 Material Discrepancies", "d. The applicant's name is an integral part"),
    ("fam-names-03", "holdout", "fam-names", "8 FAM 403.1-4(d)", "d. The applicant's name is an integral part", "e. An adult applicant cannot document"),
    ("fam-names-04", "holdout", "fam-names", "8 FAM 403.1-4(A)(c)-(d)", "c. The court order or decree must be final:", "8 FAM 403.1-4(A)(1) Documenting Name Change Orders"),
    ("fam-names-05", "holdout", "fam-names", "8 FAM 403.1-3(B)", "8 FAM 403.1-3(B) Name Spacing", "8 FAM 403.1-3(C) Punctuation,"),
    ("fam-names-06", "holdout", "fam-names", "8 FAM 403.1-5(B)(c)-(e)", "c. Arabic ordinal numbers must be changed to Roman numerals,", "8 FAM 403.1-5(C) Ranks and Titles"),
]


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def immutable_write(path: Path, raw: bytes) -> None:
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"Pinned artifact changed: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


class ParagraphText(HTMLParser):
    """Keep paragraph/heading text in document order and collapse whitespace."""

    blocks = {"p", "h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.paragraphs: list[str] = []
        self.depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.blocks:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.blocks and self.depth:
            self.depth -= 1
            if not self.depth:
                value = " ".join("".join(self.parts).split())
                if value:
                    self.paragraphs.append(value)
                self.parts = []

    def handle_data(self, value: str) -> None:
        if self.depth:
            self.parts.append(value)


def prepare_text(raw: bytes) -> str:
    # All three pinned official pages declare this encoding. Strict decoding
    # preserves every byte; HTMLParser resolves numeric and named entities.
    if not re.search(rb"charset=iso-8859-1", raw[:2000], re.IGNORECASE):
        raise ValueError("Unexpected HTML encoding; review source preparation")
    parser = ParagraphText()
    parser.feed(raw.decode("iso-8859-1", errors="strict"))
    parser.close()
    return "\n\n".join(parser.paragraphs) + "\n"


def capture(source_id: str, code: str, title: str, allow_download: bool) -> dict:
    original = ROOT / "original" / f"{source_id}.html"
    receipt = ROOT / "original" / f"{source_id}.capture.json"
    url = f"https://fam.state.gov/FAM/08FAM/08FAM{code}.html"
    if not original.exists():
        if not allow_download:
            raise ValueError(f"Missing pinned source: {original}")
        with tempfile.TemporaryDirectory(prefix="rulespec-corpus-") as folder:
            target = Path(folder) / "source.html"
            result = subprocess.run(
                ["curl", "--fail", "--location", "--silent", "--show-error",
                 "--max-time", "45", "--output", str(target), "--write-out",
                 "%{json}", url], check=True, text=True, capture_output=True,
            )
            transfer = json.loads(result.stdout)
            raw = target.read_bytes()
        metadata = {
            "id": source_id, "title": title, "source_url": url,
            "retrieved_url": transfer["url_effective"],
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "http_status": transfer["http_code"],
            "content_type": transfer.get("content_type"),
            "source_encoding": "iso-8859-1",
            "original_sha256": digest(raw), "original_bytes": len(raw),
            "capture_method": "curl with certificate verification enabled",
            "attribution": "U.S. Department of State, Foreign Affairs Manual",
        }
        immutable_write(original, raw)
        immutable_write(receipt, json_bytes(metadata))
    metadata = json.loads(receipt.read_text())
    raw = original.read_bytes()
    if digest(raw) != metadata["original_sha256"]:
        raise ValueError(f"Original digest mismatch: {source_id}")
    prepared = prepare_text(raw)
    text_path = ROOT / "prepared" / f"{source_id}.txt"
    immutable_write(text_path, prepared.encode("utf-8"))
    return {
        **metadata,
        "original_path": original.relative_to(ROOT).as_posix(),
        "capture_path": receipt.relative_to(ROOT).as_posix(),
        "text_path": text_path.relative_to(ROOT).as_posix(),
        "text_sha256": digest(prepared.encode("utf-8")),
        "text_characters": len(prepared),
    }


def build(allow_download: bool = False) -> dict:
    sources = [capture(key, *value, allow_download) for key, value in PAGES.items()]
    source_by_id = {source["id"]: source for source in sources}
    excerpts = []
    for excerpt_id, split, source_id, section, begin, end in SELECTION:
        source = source_by_id[source_id]
        full = (ROOT / source["text_path"]).read_text(encoding="utf-8")
        if full.count(begin) != 1 or full.count(end) != 1:
            raise ValueError(f"Ambiguous or absent source anchor: {excerpt_id}")
        start, stop = full.index(begin), full.index(end)
        if stop <= start:
            raise ValueError(f"Invalid excerpt order: {excerpt_id}")
        excerpt = full[start:stop].rstrip()
        stop = start + len(excerpt)
        path = ROOT / "excerpts" / split / f"{excerpt_id}.txt"
        immutable_write(path, excerpt.encode("utf-8"))
        excerpts.append({
            "id": excerpt_id, "split": split, "source_id": source_id,
            "section_label": section, "source_url": source["source_url"],
            "text_path": path.relative_to(ROOT).as_posix(),
            "source_start": start, "source_end": stop,
            "sha256": digest(excerpt.encode("utf-8")),
            "characters": len(excerpt), "words": len(excerpt.split()),
            "context_source_ids": [source_id, "fam-responsibilities"],
        })
    manifest = {
        "schema_version": "rulespec-evaluation-corpus/1",
        "dataset_id": "fam-passports-2026-09-07",
        "attribution": "U.S. Department of State, Foreign Affairs Manual",
        "preparation": {
            "version": "fam-paragraph-text/1",
            "encoding": "Declared ISO-8859-1 decoded strictly; HTML entities resolved",
            "whitespace": "Collapse Unicode whitespace inside paragraphs; join paragraphs with two newlines",
            "coordinate_unit": "Unicode codepoints into prepared source text",
            "limitations": "Text only; embedded example photographs and layout are not evaluated",
            "script_sha256": digest(Path(__file__).read_bytes()),
        },
        "sources": sources, "excerpts": excerpts,
    }
    immutable_write(ROOT / "manifest.json", json_bytes(manifest))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-missing", action="store_true")
    args = parser.parse_args()
    manifest = build(args.download_missing)
    print(json.dumps({"verified_sources": len(manifest["sources"]),
                      "verified_excerpts": len(manifest["excerpts"])}))
