"""A vocabulary suggestion must preserve uncertainty and the original wording."""
import json

import pytest

from rulespec_extrapolator.core import digest
from rulespec_extrapolator.vocabulary import annotate, load_vocabulary


def test_exact_aliases_preserve_ambiguity_unmapped_text_and_source(tmp_path):
    vocabulary = {"source": "RefSpec", "release_id": "urn:refspec:test:release",
                  "concepts": [
                      {"id": "urn:concept:officer", "label": "Officer", "aliases": ["Staff"]},
                      {"id": "urn:concept:employee", "label": "Employee", "aliases": ["Staff"]},
                      {"id": "urn:concept:passport", "label": "Passport", "aliases": ["Travel document"]},
                  ]}
    path = tmp_path / "vocabulary.json"
    path.write_text(json.dumps(vocabulary))
    book = {"accepted": [{"id": "urn:claim:1", "actor": "STAFF", "object": "Travel document"},
                         {"id": "urn:claim:2", "actor": "Unlisted role", "object": ""}]}
    before = digest(book)
    result = annotate(book, load_vocabulary(path))
    assert digest(book) == before == result["rulebook_sha256"]
    assert result["vocabulary_sha256"] == digest(vocabulary)
    assert result["release_id"] == vocabulary["release_id"]
    assert [r["status"] for r in result["records"]] == ["ambiguous", "suggested", "unmapped"]
    assert result["records"][0]["text"] == "STAFF"
    assert len(result["records"][0]["concept_ids"]) == 2
    assert result["records"][2]["text"] == "Unlisted role"
    assert all(r["review_required"] for r in result["records"])


def test_vocabulary_is_optional_and_never_discards_mentions():
    result = annotate({"accepted": [{"id": "urn:claim:1", "actor": "Applicant", "object": "Document"}]})
    assert result["release_id"] is None
    assert result["vocabulary_sha256"] is None
    assert len(result["records"]) == 2
    assert all(r["status"] == "unmapped" for r in result["records"])


@pytest.mark.parametrize("change", [
    {"source": "other"}, {"release_id": "unversioned-label"},
    {"concepts": [{"id": "urn:c:1", "label": "A"}, {"id": "urn:c:1", "label": "B"}]},
    {"concepts": [{"id": "urn:c:1", "label": "A", "aliases": [""]}]},
])
def test_snapshot_requires_release_identity_and_valid_concepts(tmp_path, change):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps({"source": "RefSpec", "release_id": "urn:release:1", "concepts": [], **change}))
    with pytest.raises(ValueError):
        load_vocabulary(path)
