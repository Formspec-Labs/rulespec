"""Complete meaning must survive compilation and durable corrections."""
from copy import deepcopy
import json

import pytest

from rulespec_extrapolator.core import NS, build_graph, compile_candidates, revise_claim, validate_graph
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore, ReviewIntegrityError


def source_case():
    text = ("In California, if a card is lost, visitors should request a replacement. "
            "Either a receipt or an invoice is acceptable. Keep the record for six months. "
            "If a card is damaged, visitors may request a replacement.")
    doc = prepare_document(text)
    candidate = {"kind": "recommendation", "modality": "should", "modality_quote": "should",
        "summary": "Visitors with a lost card in California should request a replacement.",
        "actor": "visitors", "actor_quote": "visitors", "action": "request", "action_quote": "request",
        "object": "a replacement", "object_quote": "a replacement",
        "quote": "visitors should request a replacement.",
        "scope_text": "In California, if a card is lost", "scope_quotes": ["In California, if a card is lost"],
        "context_quotes": ["Keep the record for six months."],
        "alternative_quotes": ["a receipt", "an invoice"], "choice_text": "Either a receipt or an invoice is acceptable.",
        "choice_quote": "Either a receipt or an invoice is acceptable.",
        "jurisdiction": "US-CA", "jurisdiction_quote": "California"}
    return doc, candidate


def test_meaning_compiles_to_existing_core_with_distinct_evidence_roles():
    doc, candidate = source_case()
    book = compile_candidates(doc, [candidate], {})
    assert not book["rejected"]
    claim = book["accepted"][0]
    assert not claim["issues"]
    assert validate_graph(book["graph"])["shacl_conforms"]
    nodes = {n["@id"]: n for n in book["graph"]["@graph"]}
    meaning = nodes[claim["meaning_assertion_id"]]
    assert nodes[meaning["rkaf:hasApplicability"]]["rkaf:applicabilityCondition"] == candidate["scope_text"]
    roles = {n["rkaf:evidentiaryFunction"] for n in nodes.values() if n["@type"] == "rkaf:EvidenceBinding"}
    assert {"rkaf:supports", "rkaf:definesScope", "rkaf:providesContext"} <= roles
    value = json.loads(meaning["rkaf:assertsValue"]["@value"])
    assert value["modality"] == "should"
    assert value["alternative_quotes"] == candidate["alternative_quotes"]


def test_scope_only_correction_preserves_both_scoped_meanings():
    doc, candidate = source_case()
    old = compile_candidates(doc, [candidate], {})["accepted"][0]
    changed = revise_claim(doc, old, {"scope_text": "If a card is damaged", "scope_quotes": ["If a card is damaged"]}, "urn:test:scope-edit")
    graph = build_graph(doc, [old, changed], {})
    nodes = {n["@id"]: n for n in graph["@graph"]}
    assert old["meaning_assertion_id"] != changed["meaning_assertion_id"]
    scopes = [nodes[nodes[c["meaning_assertion_id"]]["rkaf:hasApplicability"]]["rkaf:applicabilityCondition"] for c in (old, changed)]
    assert scopes == [candidate["scope_text"], "If a card is damaged"]
    assert validate_graph(graph)["shacl_conforms"]


@pytest.mark.parametrize("kind,modality", [("requirement", "should"), ("permission", "not_required"), ("permission", "possible")])
def test_modality_cannot_silently_contradict_kind(kind, modality):
    doc, candidate = source_case()
    candidate.update(kind=kind, modality=modality)
    book = compile_candidates(doc, [candidate], {})
    assert not book["accepted"]
    assert "modality" in book["rejected"][0]["reason"]


def test_missing_scope_evidence_is_visible_and_does_not_make_a_scope_node():
    doc, candidate = source_case()
    candidate["scope_quotes"] = ["If an invented circumstance applies"]
    book = compile_candidates(doc, [candidate], {})
    assert any(i["code"] == "component_evidence_unresolved" for i in book["accepted"][0]["issues"])
    assert not any(n["@type"] == "rkaf:ApplicabilityScope" for n in book["graph"]["@graph"])


@pytest.mark.parametrize("jurisdiction,quote", [("", ""), ("US-MARS", "An invented territory")])
def test_supported_conditions_use_core_scope_without_asserting_unverified_territory(jurisdiction, quote):
    doc, candidate = source_case()
    candidate.update(jurisdiction=jurisdiction, jurisdiction_quote=quote)
    book = compile_candidates(doc, [candidate], {})
    scopes = [n for n in book["graph"]["@graph"] if n["@type"] == "rkaf:ApplicabilityScope"]
    assert len(scopes) == 1
    assert scopes[0]["rkaf:appliesInJurisdiction"] == []
    assert scopes[0]["rkaf:applicabilityCondition"] == candidate["scope_text"]
    assert validate_graph(book["graph"])["shacl_conforms"]
    if jurisdiction:
        assert any(i["field"] == "jurisdiction" and i["code"] == "component_evidence_unresolved"
                   for i in book["accepted"][0]["issues"])


def test_same_quote_can_support_and_define_scope_without_binding_collision():
    doc, candidate = source_case()
    candidate["scope_quotes"] = [candidate["quote"]]
    book = compile_candidates(doc, [candidate], {})
    summary_id = next(n["@id"] for n in book["graph"]["@graph"] if n.get("rkaf:assertsPredicate") == NS + "states-recommendation")
    bindings = [n for n in book["graph"]["@graph"] if n.get("rkaf:bindsAssertion") == summary_id]
    assert len(bindings) == 3
    assert len({n["@id"] for n in bindings}) == 3


def test_split_and_reopen_preserve_scope_alternatives_and_original_history(tmp_path):
    doc, candidate = source_case()
    run = {"id": "urn:test:run", "profile": "document-understanding/2"}
    book = compile_candidates(doc, [candidate], run)
    for name, value in (("document.json", doc), ("run.json", run), ("rulebook.json", book)):
        (tmp_path / name).write_text(json.dumps(value))
    store = ReviewStore(tmp_path)
    before = store.snapshot()
    original = before["accepted"][0]
    after = store.apply({"action": "split", "expected_revision": 0, "actor": "Regression author", "actor_kind": "aiAgent",
        "rationale": "Exercise retained context on split components; this is a compiler fixture, not a semantic approval.",
        "targets": [original["id"]], "replacements": [{"summary": "First source-backed view"}, {"summary": "Second source-backed view"}]})
    assert len(after["accepted"]) == 2
    for child in after["accepted"]:
        for field in ("scope_text", "scope_quotes", "alternative_quotes", "choice_text", "modality"):
            assert child[field] == original[field]
    reopened = ReviewStore(tmp_path).snapshot()
    assert reopened == after
    assert validate_graph(reopened["graph"])["shacl_conforms"]
    assert (tmp_path / "rulebook.json").read_text() == json.dumps(book)


def test_changed_scope_evidence_cannot_reopen_under_old_assertion_identity(tmp_path):
    doc, candidate = source_case()
    book = compile_candidates(doc, [candidate], {})
    book["accepted"][0]["scope_text"] = "A different scope"
    for name, value in (("document.json", doc), ("run.json", {}), ("rulebook.json", book)):
        (tmp_path / name).write_text(json.dumps(value))
    with pytest.raises(ReviewIntegrityError, match="identities"):
        ReviewStore(tmp_path)
