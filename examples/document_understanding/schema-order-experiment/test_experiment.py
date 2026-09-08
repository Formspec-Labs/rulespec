"""Offline checks for the new experiment's reference adapter."""
from copy import deepcopy

import pytest
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document

import experiment as x


def fixture():
    document = prepare_document("Staff must sign and date records, except temporary staff.")
    schema = x.schema_for("definitions_first")
    fields = schema["properties"]["extractions"]["items"]["properties"]["unit_attributes"]["properties"]

    def unit(identity, kind, quote, action=""):
        attrs = {k: [] if p["type"] == "array" else "" for k, p in fields.items()}
        attrs.update(kind=kind, summary=quote, actor="Staff" if action else "", action=action,
                     object="records" if action else "", actor_quote="Staff" if action else "",
                     action_quote=action, object_quote="records" if action else "",
                     modality="must" if action else "not_stated", modality_quote="must" if action else "",
                     relation="none" if action else "exception")
        return {"id": identity, "unit": quote, "actor_ref": "c1" if action else "",
                "object_refs": [], "unit_attributes": attrs}

    same_quote = "Staff must sign and date records"
    payload = {"concepts": [{"id": "c1", "label": "Staff", "kind": "role", "source_quotes": ["Staff"]}],
        "extractions": [unit("u1", "requirement", same_quote, "sign"),
                        unit("u2", "requirement", same_quote, "date"),
                        unit("u3", "exception", "except temporary staff")],
        "relationships": [{"source_unit_ref": "u3", "target_unit_refs": ["u2"],
            "relation": "exception", "evidence_quotes": [document["text"]],
            "explanation": "Fixture pins a specific baseline sharing its quotation with another unit."}],
        "unresolved": []}
    return document, payload


def normalize(payload, document):
    return x.normalize(payload, document, e.plan_windows(document)[0], "definitions_first", {"id": "test"})


def test_explicit_reference_distinguishes_units_with_identical_quotations():
    document, payload = fixture()
    book, mapping = normalize(payload, document)
    assert len(book["accepted"]) == 3 and not book["rejected"]
    assert book["accepted"][2]["target_ids"] == [mapping["unit_ids"]["u2"]]
    assert mapping["unit_ids"]["u1"] != mapping["unit_ids"]["u2"]
    assert not mapping["issues"]


@pytest.mark.parametrize("target", ["u99", "u3"])
def test_missing_target_and_modifier_target_do_not_fall_back_to_quotes(target):
    document, payload = fixture()
    payload["relationships"][0]["target_unit_refs"] = [target]
    book, mapping = normalize(payload, document)
    assert not book["accepted"][2]["target_ids"]
    assert any(i["code"] == "invalid_qualification_reference" for i in mapping["issues"])


def test_duplicate_local_identity_is_refused():
    document, payload = fixture()
    payload["extractions"][1]["id"] = "u1"
    with pytest.raises(ValueError, match="Duplicate local identifier"):
        normalize(payload, document)


def test_missing_concept_and_unsupported_concept_evidence_remain_visible():
    document, payload = fixture()
    payload["concepts"][0]["source_quotes"] = ["Invented officials"]
    payload["extractions"][0]["actor_ref"] = "c99"
    _, mapping = normalize(payload, document)
    assert {i["code"] for i in mapping["issues"]} >= {"unsupported_concept_evidence", "missing_concept_reference"}


def test_refused_unit_cannot_become_a_reference_target():
    document, payload = fixture()
    payload["extractions"][1]["unit"] = "Unquoted source invention"
    book, mapping = normalize(payload, document)
    assert "u2" not in mapping["unit_ids"]
    assert any(i["code"] == "reference_to_refused_unit" for i in mapping["issues"])
    assert all(not c["target_ids"] for c in book["accepted"])


def test_order_comparison_changes_only_serialization_order():
    first, last = (x.schema_for(v) for v in ("definitions_first", "references_first"))
    assert first == last
    assert x.ordered_digest(first) != x.ordered_digest(last)
    assert x.instructions("definitions_first") == x.instructions("references_first")
    document, payload = fixture()
    reordered = {k: deepcopy(payload[k]) for k in last["properties"]}
    assert normalize(payload, document) == normalize(reordered, document)
