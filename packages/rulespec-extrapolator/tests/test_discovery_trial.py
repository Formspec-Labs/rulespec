"""The diagnostic must preserve evidence and not reward unsafe interpretations."""
import json
from pathlib import Path
import runpy

from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

trial = runpy.run_path(str(Path(__file__).parents[1] / "evaluation" / "discovery_trial.py"))


def book():
    doc = prepare_document("Only in winter.\n\nYou must carry a coat.\n\nThis avoids chills.")
    return compile_candidates(doc, [{"kind": "requirement", "modality": "must", "modality_quote": "must",
        "summary": "In winter you must carry a coat.", "quote": "You must carry a coat.", "actor": "You",
        "actor_quote": "You", "scope_text": "Only in winter", "scope_quotes": ["Only in winter."],
        "context_quotes": ["This avoids chills."],
        "claimants": [{"text": "Invented Office", "quote": "You must carry a coat.",
                       "attribution": "rkaf:claimantIsDocumentIssuer"}]}], {"id": "urn:test:discovery"})


def test_packets_recover_scope_and_context_without_indexing_invented_attribution():
    b = book()
    rows = trial["records"](b, "test", "packets")
    hit = trial["search"](rows, "carry coat", 1)[0]
    assert {e["quote"] for e in hit["evidence"]} >= {
        "Only in winter.", "You must carry a coat.", "This avoids chills."}
    assert "Invented Office" not in json.dumps(rows)
    # Reversing the scope evidence is discovery navigation, not a legal edge.
    winter = trial["search"](rows, "winter", 1)[0]
    assert b["accepted"][0]["id"] in winter["claim_ids"]
    assert not b["accepted"][0]["target_ids"]


def test_packets_do_not_change_source_ranking_and_do_not_count_wrong_documents():
    b = book()
    source = trial["search"](trial["records"](b, "test", "source"), "winter coat")
    packets = trial["search"](trial["records"](b, "test", "packets"), "winter coat")
    assert [(h["id"], h["score"]) for h in source] == [(h["id"], h["score"]) for h in packets]
    assert not trial["support_found"](packets, "another document", "Only in winter.")


def test_no_source_answer_is_unknown_not_a_vacuous_pass():
    result = trial["run"]({"test": book()}, [{"id": "unknown", "query": "passport fees",
        "source": None, "required_quotes": []}])
    for mode in ("summaries", "source", "packets"):
        assert result[mode]["questions"][0]["all_source_support_at_3"] is None
    assert result["admission"]["test"]["claimants"] == {"candidates": 1, "admitted": 0}
