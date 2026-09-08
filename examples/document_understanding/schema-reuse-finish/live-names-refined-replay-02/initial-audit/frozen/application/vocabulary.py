"""Suggest labels from an explicitly supplied RefSpec snapshot; retain unmatched text."""
import json
from pathlib import Path
import re

from .core import digest

IRI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$")


def load_vocabulary(path):
    value = json.loads(Path(path).read_text())
    if value.get("source") != "RefSpec" or not IRI.fullmatch(value.get("release_id", "")):
        raise ValueError("Vocabulary must identify a RefSpec release")
    concepts = value.get("concepts")
    if not isinstance(concepts, list):
        raise ValueError("Vocabulary concepts must be a list")
    ids = set()
    for concept in concepts:
        identity, label = concept.get("id", ""), concept.get("label", "")
        if not IRI.fullmatch(identity) or identity in ids or not isinstance(label, str) or not label.strip():
            raise ValueError("Concept IDs and labels must be unique, valid and nonempty")
        aliases = concept.get("aliases", [])
        if not isinstance(aliases, list) or any(not isinstance(a, str) or not a.strip() for a in aliases):
            raise ValueError("Concept aliases must be nonempty strings")
        ids.add(identity)
    return value


def annotate(rulebook, vocabulary=None):
    index = {}
    for concept in (vocabulary or {}).get("concepts", []):
        for text in [concept["label"], *concept.get("aliases", [])]:
            index.setdefault(text.strip().casefold(), set()).add(concept["id"])
    records = []
    for claim in rulebook["accepted"]:
        for field in ("actor", "object"):
            text = claim.get(field, "")
            if not text:
                continue
            matches = sorted(index.get(text.strip().casefold(), []))
            records.append({"claim_id": claim["id"], "field": field, "text": text,
                            "status": "suggested" if len(matches) == 1 else "ambiguous" if matches else "unmapped",
                            "concept_ids": matches, "method": "exact-label-or-alias",
                            "review_required": True})
    return {"schema_version": "document-vocabulary/1", "rulebook_sha256": digest(rulebook),
            "vocabulary_sha256": digest(vocabulary) if vocabulary else None,
            "release_id": (vocabulary or {}).get("release_id"),
            "records": records, "note": "Label matches are suggestions; source text is retained."}
