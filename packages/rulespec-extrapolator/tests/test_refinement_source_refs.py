"""Challenge evidence uses the shared passage resolver, not model-copied text."""
from copy import deepcopy
import json

import pytest

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.core import canonical
from rulespec_extrapolator.documents import prepare_document


def setup(text, *, focus=None, context=(), evidence=()):
    document = prepare_document(text)
    start, end = focus or (0, len(text))
    book = {"document": document, "accepted": []}
    packet = r._packet(book, {"labels": {"expected_units": []}},
                       {"start": start, "end": end, "context_spans": list(context)})
    if evidence:
        packet["claims"]["C0000"] = {"evidence": list(evidence)}
    return document, packet


def check(document, packet, refs, verdict="supported"):
    payload = {"judgments": [{"proposal_id": "P0000", "source_refs": refs,
                              "rationale": "Source-based assessment.", "verdict": verdict}]}
    return r._decode_checks(payload, [], [{"id": "P0000"}], document, packet)


def test_saved_railroad_thin_space_is_retrieved_without_retyping():
    # The actual failing quotation from evidence-catalog/cells/cell-05.
    text = ("(b) A stop need not be made at:\n\n"
            "(1) A streetcar crossing, or railroad tracks used exclusively for industrial "
            "switching purposes, within a business district, as defined in §\u2009390.5 of this chapter.")
    document, packet = setup(text)
    with pytest.raises(ValueError, match="absent"):
        r._source_quote(document, packet, text.replace("\u2009", " "))
    rows, issues = check(document, packet, ["F000:F001"])
    assert not issues
    assert rows["P0000"]["source_spans"] == [
        {"source_id": document["id"], "start": 0, "end": len(text), "quote": text}]


def test_repeated_text_selects_position_and_preserves_unicode_and_layout():
    text = "May\tNot enter\r\n\r\nMay\tNot enter"
    document, packet = setup(text)
    rows, issues = check(document, packet, ["F001"])
    assert not issues
    span, = rows["P0000"]["source_spans"]
    assert span["start"] == text.rindex("May")
    assert span["quote"] == "May\tNot enter"
    assert span["quote"] == document["text"][span["start"]:span["end"]]


@pytest.mark.parametrize("refs", [[], ["F999"], ["C0000"], ["F001:F000"],
    ["F000:C000"], ["F000", "F999"], ["copy source text"]])
def test_bad_selection_refuses_entire_judgment(refs):
    document, packet = setup("Rule one.\n\nRule two.")
    rows, issues = check(document, packet, refs)
    assert rows == {}
    assert any(i["code"] == "unjudged_proposal" for i in issues)


def test_context_and_selected_claim_evidence_do_not_allow_unsupplied_gap():
    text = "Scope. HIDDEN. Exception. Focus."
    document, packet = setup(text, focus=(26, len(text)),
        context=[{"start": 0, "end": 6}], evidence=[{"start": 15, "end": 25}])
    rows, issues = check(document, packet, ["C000", "C001"])
    assert not issues
    assert [s["quote"] for s in rows["P0000"]["source_spans"]] == ["Scope.", "Exception."]
    rows, issues = check(document, packet, ["C000:C001"])
    assert not rows and issues
    assert "HIDDEN" not in canonical(r._challenge_catalog(document, packet))


def test_inserted_source_map_text_is_not_admitted_as_evidence():
    document, packet = setup("A source rule.")
    document["source_map"] = [{"start": 0, "end": 1, "kind": "inserted", "text": "A"},
        {"start": 1, "end": len(document["text"]), "kind": "source", "source_id": "original",
         "source_start": 1, "source_end": len(document["text"])}]
    rows, issues = check(document, packet, ["F000"])
    assert not rows and issues


@pytest.mark.parametrize("verdict", ["supported", "unsupported", "unknown"])
def test_resolving_evidence_preserves_verdict_and_raw_selection(verdict):
    document, packet = setup("A rule.")
    rows, issues = check(document, packet, ["F000"], verdict)
    assert not issues
    assert rows["P0000"]["verdict"] == verdict
    assert rows["P0000"]["source_refs"] == ["F000"]


def test_prompt_catalog_matches_decoder_and_reuses_generated_schema():
    document, packet = setup("First rule.\n\nSecond rule.")
    original = deepcopy(packet)
    prompt = r._challenge_prompt(packet, [], document)
    encoded = prompt.split("\nSource passages: ", 1)[1].split("\nDraft and audit", 1)[0]
    assert json.loads(encoded) == r._challenge_catalog(document, packet)
    assert packet == original
    schema = r.CHECK_SCHEMA["properties"]["judgments"]["items"]["properties"]
    assert schema["source_refs"] == a.SOURCE_REFS
    assert "quotes" not in schema


def test_duplicate_proposal_judgments_are_not_accepted():
    document, packet = setup("A rule.")
    row = {"proposal_id": "P0000", "source_refs": ["F000"],
           "rationale": "Source-based assessment.", "verdict": "supported"}
    rows, issues = r._decode_checks({"judgments": [row, row]}, [],
                                    [{"id": "P0000"}], document, packet)
    assert not rows and issues
