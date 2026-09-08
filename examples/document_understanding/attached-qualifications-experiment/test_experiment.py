from copy import deepcopy
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("attached_trial", ROOT / "experiment.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
SCHEMA = json.loads((ROOT / "provider.schema.json").read_text())


def row(ref="P000", statement="Visitors must wear badges, except infants.", **changes):
    attrs = {key: [] if value["type"] == "array" else "" for key, value in
             SCHEMA["properties"]["extractions"]["items"]["properties"]["unit_attributes"]["properties"].items()}
    attrs.update(kind="requirement", modality="must", modality_quote="must", statement=statement, **changes)
    return {"unit": ref, "unit_attributes": attrs}


def exception(ref="P000"):
    return {"relation": "exception", "statement": "Infants are exempt from the visitors' badge duty.",
            "evidence": [ref], "references": []}


def compile_rows(document, rows):
    payload = {"extractions": rows}
    Draft202012Validator(SCHEMA).validate(payload)
    return trial.compile_output(payload, document, {"id": "urn:test:attached"})


def test_nesting_disambiguates_two_meanings_with_the_same_quote():
    doc = prepare_document("Visitors must wear badges, except infants. Guides must keep maps.")
    book, mapping = compile_rows(doc, [row(qualifications=[exception()]), row(statement="Guides must keep maps.")])
    assert not book["rejected"]
    by_id = {c["id"]: c for c in book["accepted"]}
    child = by_id[mapping[0]["qualification_ids"][0]]
    assert child["target_ids"] == [mapping[0]["baseline_id"]]
    assert child["target_ids"] != [mapping[1]["baseline_id"]]
    assert len(by_id) == 3
    assert trial.core.validate_graph(book["graph"])["shacl_conforms"]


def test_repeated_text_keeps_the_selected_occurrence():
    text = "Visitors must wear badges, except infants."
    doc = prepare_document(text + "\n\n" + text)
    book, _ = compile_rows(doc, [row("P001", qualifications=[exception("P001")])])
    assert not book["rejected"]
    assert all(c["start"] == len(text) + 2 for c in book["accepted"])


def test_bad_qualification_reference_does_not_remove_the_baseline():
    book, _ = compile_rows(prepare_document("Visitors must wear badges, except infants."),
                           [row(qualifications=[exception("P999")])])
    assert len(book["accepted"]) == 1 and len(book["rejected"]) == 1
    assert book["accepted"][0]["kind"] == "requirement"


def test_bad_baseline_cannot_leave_an_orphan_qualification():
    book, mapping = compile_rows(prepare_document("Visitors must wear badges, except infants."),
                                [row("P999", qualifications=[exception()])])
    assert not book["accepted"] and not mapping and book["rejected"]


def test_source_range_preserves_list_markers_and_newlines():
    doc = prepare_document("You must submit either:\n\n(1) a receipt; or\n\n(2) an invoice.")
    book, _ = compile_rows(doc, [row("P000:P002", statement="You must submit either a receipt or an invoice.",
        alternative_quotes=["P001", "P002"], choice_quote="P000:P002",
        choice_text="Either a receipt or an invoice")])
    claim, = book["accepted"]
    assert claim["quote"] == doc["text"] == claim["choice_quote"]
    assert claim["alternative_quotes"] == ["(1) a receipt; or", "(2) an invoice."]
    assert not book["rejected"]


def test_reversed_range_is_refused():
    doc = prepare_document("Visitors must wear badges.\n\nInfants are exempt.")
    book, _ = compile_rows(doc, [row("P001:P000")])
    assert not book["accepted"] and "Reversed" in book["rejected"][0]["reason"]


def test_logic_text_keeps_the_existing_nonfatal_review_behavior():
    book, _ = compile_rows(prepare_document("Visitors must wear badges, except infants."),
                          [row(logic_text="Rewritten logical description")])
    assert not book["rejected"]
    claim, = book["accepted"]
    assert claim["logic_text"] == "Rewritten logical description"
    assert any(i["code"] == "logic_requires_review" for i in claim["issues"])
