from copy import deepcopy

import pytest

from rulespec_extrapolator.core import (
    NS, assertion_id, build_graph, compile_candidates, revise_claim, validate_graph,
)
from rulespec_extrapolator.documents import prepare_document


def fixture():
    text = "Visitors must wear badges. Staff must wear badges."
    document = prepare_document(text)
    candidate = {"kind": "requirement", "summary": "Visitors must wear badges.",
                 "actor": "Visitors", "actor_quote": "Visitors",
                 "action": "wear", "action_quote": "wear",
                 "object": "badges", "object_quote": "badges",
                 "quote": "Visitors must wear badges.", "modality": "must", "modality_quote": "must"}
    run = {"id": "urn:test:run", "model": "fixture"}
    return document, candidate, run


def test_explicit_child_section_survives_parent_order():
    document, candidate, run = fixture()
    parent = {"id": "parent", "label": "Parent", "start": 0, "end": len(document["text"])}
    child = {"id": "child", "label": "Child", "start": 0, "end": len(candidate["quote"])}
    candidate["section_id"] = "child"
    for sections in ([parent, child], [child, parent]):
        document["sections"] = sections
        claim = compile_candidates(document, [candidate], run)["accepted"][0]
        assert claim["section_id"] == "child"
    candidate.pop("section_id")
    document["sections"] = [parent, child]
    assert compile_candidates(document, [candidate], run)["accepted"][0]["section_id"] == "child"


def by_predicate(graph):
    return {n["rkaf:assertsPredicate"]: n for n in graph["@graph"]
            if n["@type"] == "rkaf:ValueAssertion"}


def test_exact_components_are_independently_grounded_and_core_valid():
    document, candidate, run = fixture()
    result = compile_candidates(document, [candidate], run)
    assert not result["rejected"]
    claim = result["accepted"][0]
    assert not claim["issues"]
    assert {e["field"] for e in claim["evidence"]} == {"summary", "actor", "action", "object", "modality"}
    assert all(document["text"][e["start"]:e["end"]] == e["quote"] for e in claim["evidence"])
    assert validate_graph(result["graph"])["shacl_conforms"]


@pytest.mark.parametrize("temperature", [0, 0.2, 1, 2])
def test_core_lineage_records_the_actual_request_temperature(temperature):
    document, candidate, run = fixture()
    run["temperature"] = temperature
    book = compile_candidates(document, [candidate], run)
    lineage = [n for n in book["graph"]["@graph"] if n["@type"] == "rkaf:AILineage"]
    assert len(lineage) == 1
    assert lineage[0]["rkaf:temperature"] == temperature
    assert validate_graph(book["graph"])["shacl_conforms"]


def test_actor_change_changes_only_actor_proposition_and_preserves_ai_origin():
    document, candidate, run = fixture()
    base = compile_candidates(document, [candidate], run)
    old = base["accepted"][0]
    new = revise_claim(document, old, {"actor": "Staff", "actor_quote": "Staff"},
                       "urn:test:edit")
    old_nodes = by_predicate(base["graph"])
    changed_nodes = by_predicate(build_graph(document, [new], run))
    assert old["id"] != new["id"]
    assert old["rule_id"] == new["rule_id"]
    assert old_nodes[NS + "actor"]["@id"] != changed_nodes[NS + "actor"]["@id"]
    for field in ("states-requirement", "action", "object"):
        assert old_nodes[NS + field]["@id"] == changed_nodes[NS + field]["@id"]
    graph = build_graph(document, [old, new], run)
    original_nodes = {n["@id"]: n for n in graph["@graph"]}
    assert original_nodes[old_nodes[NS + "states-requirement"]["@id"]]["rkaf:assertionOrigin"] == "rkaf:aiSuggested"
    actor_node = original_nodes[changed_nodes[NS + "actor"]["@id"]]
    assert actor_node["rkaf:supersedesAssertion"] == [old_nodes[NS + "actor"]["@id"]]
    assert validate_graph(graph)["shacl_conforms"]


def test_evidence_only_revision_preserves_every_core_proposition():
    document, candidate, run = fixture()
    old = compile_candidates(document, [candidate], run)["accepted"][0]
    new = revise_claim(document, old, {"quote": document["text"]}, "urn:test:evidence")
    assert old["id"] != new["id"]
    assert old["assertion_ids"] == new["assertion_ids"]
    assert old["evidence"] != new["evidence"]


def test_assertion_identity_ignores_review_origin_and_evidence():
    proposition = {"rkaf:assertsSubject": "urn:test:s", "rkaf:assertsPredicate": "urn:test:p",
                   "rkaf:assertsValue": {"@value": "A", "@language": "en"},
                   "rkaf:assertionPolarity": "rkaf:affirmed"}
    altered = {**proposition, "rkaf:assertionOrigin": "rkaf:humanAsserted",
               "rkaf:usageEligibility": "rkaf:officialUse", "evidence": ["different"]}
    assert assertion_id(proposition) == assertion_id(altered)


def test_missing_component_evidence_is_visible_not_fabricated():
    document, candidate, run = fixture()
    candidate.update(actor="An unrelated vendor", actor_quote="An unrelated vendor")
    result = compile_candidates(document, [candidate], run)
    assert result["accepted"][0]["issues"][0]["code"] == "component_evidence_unresolved"
    assert not any(e["field"] == "actor" for e in result["accepted"][0]["evidence"])
    assert validate_graph(result["graph"])["shacl_conforms"]


def test_partial_target_set_emits_no_misleading_qualification_link():
    text = "Staff must log requests and publish decisions, except private details."
    doc = prepare_document(text)
    candidates = [
        {"kind": "requirement", "summary": "Staff must log requests.", "actor": "Staff",
         "quote": "Staff must log requests"},
        {"kind": "exception", "summary": "Private details are exempt.", "actor": "Staff",
         "quote": "except private details", "relation": "exception",
         "applies_to": ["Staff must log requests", "publish decisions"]},
    ]
    result = compile_candidates(doc, candidates, {})
    assert result["unresolved"]
    assert not result["accepted"][1]["target_ids"]
    assert not any(n["@type"] == "rkaf:RelationshipAssertion" for n in result["graph"]["@graph"])


def test_bad_candidates_retained_and_changed_source_rejected():
    document, candidate, run = fixture()
    invalid = deepcopy(candidate)
    invalid["quote"] = "Made up text"
    result = compile_candidates(document, [invalid, 7], run)
    assert len(result["rejected"]) == 2
    document["text"] += " changed"
    with pytest.raises(ValueError, match="digest"):
        compile_candidates(document, [candidate], run)


@pytest.mark.parametrize("start", [-7, 0.5, True])
def test_original_source_coordinates_reject_negative_fractional_and_boolean(start):
    from rulespec_extrapolator.documents import validate_document
    doc = prepare_document("Evidence")
    doc["source_map"] = [{"kind": "source", "start": 0, "end": 8,
                         "source_id": "original", "source_start": start, "source_end": start + 8}]
    with pytest.raises(ValueError, match="coordinates"):
        validate_document(doc)


@pytest.mark.parametrize("separator", ["\r\n", "\r", "\n\r\n"])
def test_plaintext_loading_preserves_newlines_and_source_coordinates(tmp_path, separator):
    from rulespec_extrapolator.documents import load_document
    from rulespec_extrapolator.core import digest
    text = "Staff must log arrivals." + separator + "Staff must log departures."
    path = tmp_path / "manual.txt"
    path.write_bytes(text.encode("utf-8"))
    document = load_document(path)
    assert document["text"] == text
    assert document["sha256"] == digest(path.read_bytes())
    result = compile_candidates(document, [{"kind": "requirement", "summary": "Log departures.",
                                          "actor": "Staff", "quote": "Staff must log departures."}], {})
    claim = result["accepted"][0]
    assert claim["modality"] == "uncertain"
    assert claim["meaning_assertion_id"] in claim["assertion_ids"]
    assert "modality_unresolved" in {issue["code"] for issue in claim["issues"]}
    evidence = claim["evidence"][0]
    assert evidence["start"] == text.index("Staff must log departures.")
    assert text[evidence["start"]:evidence["end"]] == evidence["quote"]


def test_rule_kind_correction_supersedes_the_old_summary():
    document, candidate, run = fixture()
    old = compile_candidates(document, [candidate], run)["accepted"][0]
    new = revise_claim(document, old, {"kind": "permission", "modality": "may"}, "urn:test:kind")
    graph = build_graph(document, [old, new], run)
    nodes = by_predicate(graph)
    assert nodes[NS + "states-permission"]["rkaf:supersedesAssertion"] == [
        nodes[NS + "states-requirement"]["@id"]]
    assert validate_graph(graph)["shacl_conforms"]


def test_restore_prior_proposition_keeps_revision_history_without_changing_origin():
    import json
    from rulespec_extrapolator.core import digest
    document, candidate, run = fixture()
    a = compile_candidates(document, [candidate], run)["accepted"][0]
    b = revise_claim(document, a, {"actor": "Staff", "actor_quote": "Staff"}, "urn:test:b")
    restored = revise_claim(document, b, {"actor": "Visitors", "actor_quote": "Visitors"},
                            "urn:test:restore")
    graph = build_graph(document, [a, b, restored], run)
    nodes = {n["@id"]: n for n in graph["@graph"]}
    assert nodes[restored["id"]]["prov:wasDerivedFrom"] == [{"@id": b["id"]}]
    assert nodes[b["id"]]["prov:wasDerivedFrom"] == [{"@id": a["id"]}]
    body = nodes[restored["id"]]["dcterms:description"]
    assert nodes[restored["id"]]["rkaf:hasContentDigest"] == "sha256:" + digest(body)
    assert json.loads(body)["assertion_ids"] == restored["assertion_ids"]
    actor = next(n for n in nodes.values() if n.get("rkaf:assertsPredicate") == NS + "actor"
                 and n["rkaf:assertsValue"]["@value"] == "Visitors")
    assert actor["rkaf:assertionOrigin"] == "rkaf:aiSuggested"
    assert "rkaf:supersedesAssertion" not in actor
    assert validate_graph(graph)["shacl_conforms"]
