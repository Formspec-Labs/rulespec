from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import sqlite3

import pytest

from rulespec_extrapolator.core import canonical, compile_candidates, validate_graph
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewError, ReviewIntegrityError, ReviewStore, RevisionConflict


MAIN = "Supervisors must inspect vehicles and retain records."
PERMISSION = "Drivers may depart."
EXCEPTION = "Unless the road is closed."


def make_run(tmp_path, *, extra_source="", extraction_refusals=None):
    text = f"🚦 {MAIN}\n{PERMISSION}\n{EXCEPTION}\n{extra_source}"
    document = prepare_document(text, title="Vehicle operations", source_url="https://example.test/manual")
    candidates = [
        {"kind": "requirement", "summary": "Supervisors must inspect vehicles and retain records.",
         "actor": "Supervisors", "actor_quote": "Supervisors", "quote": MAIN,
         "action": "inspect vehicles and retain records", "action_quote": "inspect vehicles and retain records",
         "object": "vehicles", "object_quote": "vehicles"},
        {"kind": "permission", "summary": "Drivers may depart.", "actor": "Drivers",
         "actor_quote": "Drivers", "quote": PERMISSION, "action": "depart", "action_quote": "depart"},
        {"kind": "exception", "summary": "Road closure qualifies permission to depart.", "actor": "Drivers",
         "actor_quote": "Drivers", "quote": EXCEPTION, "relation": "exception", "applies_to": [PERMISSION]},
    ]
    run = {"id": "fixture-review-run", "model": "fixture", "status": "partial_failure", "windows": [
        {"id": "good-window", "status": "complete"}, {"id": "bad-window", "status": "failed"},
    ]}
    rulebook = compile_candidates(document, candidates, run)
    rulebook["extraction_refusals"] = extraction_refusals or []
    assert len(rulebook["accepted"]) == 3
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    for name, value in {"document.json": document, "run.json": run, "rulebook.json": rulebook,
                        "candidates.json": candidates, "graph.jsonld": rulebook["graph"]}.items():
        (run_dir / name).write_text(canonical(value), encoding="utf-8")
    return run_dir


def action(snapshot, operation, targets, *, replacements=None, actor="Review test agent", actor_kind="aiAgent"):
    request = {"expected_revision": snapshot["revision"], "actor": actor, "actor_kind": actor_kind,
               "action": operation, "targets": targets, "rationale": "Checked the quoted source and the affected meaning."}
    if replacements is not None:
        request["replacements"] = replacements
    return request


def test_complete_review_history_survives_reopen_and_preserves_originals(tmp_path):
    run_dir = make_run(tmp_path)
    originals = {path.name: path.read_bytes() for path in run_dir.iterdir()}
    store = ReviewStore(run_dir)
    before = store.snapshot()
    original = before["accepted"][0]
    approved = store.apply(action(before, "approve", [original["id"]]))
    assert approved["accepted"][0]["origin"] == "aiSuggested"
    row = approved["attestations"][0]
    assert row["attestor_kind"] == "rkaf:aiAgent"
    assert row["method"] == "llm"
    assert set(json.loads(row["target_ids_json"])) == set(original["assertion_ids"])
    assert original["id"] in row["attestation_scope"]

    edited = store.apply(action(approved, "edit", [original["id"]], actor="Fixture human reviewer",
                               actor_kind="humanUser", replacements=[{"summary": "Inspect vehicles and retain the inspection records."}]))
    correction = edited["accepted"][-1]
    assert correction["rule_id"] == original["rule_id"]
    assert correction["id"] != original["id"]
    assert correction["origin"] == "humanAsserted"
    assert correction["review_status"] == "pending"
    split = store.apply(action(edited, "split", [correction["id"]], replacements=[
        {"summary": "Supervisors must inspect vehicles.", "quote": "Supervisors must inspect vehicles",
         "start": None, "end": None, "action": "inspect vehicles", "action_quote": "inspect vehicles"},
        {"summary": "Supervisors must retain records.", "quote": "retain records", "start": None, "end": None,
         "action": "retain records", "action_quote": "retain records", "object": "records", "object_quote": "records"},
    ]))
    pieces = split["history"][-1]["replacements"]
    assert len({piece["rule_id"] for piece in pieces}) == 2
    assert all(piece["rule_id"] != correction["rule_id"] for piece in pieces)
    merged = store.apply(action(split, "merge", [piece["id"] for piece in pieces], replacements=[
        {"summary": "Supervisors must inspect vehicles and retain records.", "quote": MAIN, "start": None, "end": None,
         "action": "inspect vehicles and retain records", "action_quote": "inspect vehicles and retain records"},
    ]))
    merged_claim = merged["history"][-1]["replacements"][0]
    assert set(merged_claim["supersedes"]) == {piece["id"] for piece in pieces}
    assert set(merged_claim["prior_assertion_ids"]) == {identity for piece in pieces for identity in piece["assertion_ids"]}
    rejected = store.apply(action(merged, "reject", [merged_claim["id"]]))
    assert all(claim["id"] != merged_claim["id"] for claim in rejected["accepted"])
    assert rejected["review_summary"]["rejected"] == 1
    assert rejected["run"]["status"] == "partial_failure"
    assert rejected["review_summary"]["usage"] == "review_only"
    assert canonical(ReviewStore(run_dir).snapshot()) == canonical(rejected)
    assert {name: (run_dir / name).read_bytes() for name in originals} == originals
    assert rejected["revisions"][0]["origin"] == "aiSuggested"
    assert rejected["revisions"][0]["review_status"] == "superseded"
    assert len(rejected["revisions"]) == 7
    assert len(rejected["history"]) == 5
    assert validate_graph(rejected["graph"])["shacl_conforms"]
    restored = store.apply(action(rejected, "approve", [merged_claim["id"]]))
    assert any(claim["id"] == merged_claim["id"] for claim in restored["accepted"])
    assert len(restored["attestations"]) == 3
    assert all(node.get("rkaf:usageEligibility", "rkaf:reviewQueueOnly") == "rkaf:reviewQueueOnly" for node in restored["graph"]["@graph"])


def test_only_one_concurrent_action_can_use_a_revision(tmp_path):
    run_dir = make_run(tmp_path)
    first, second = ReviewStore(run_dir), ReviewStore(run_dir)
    snapshot = first.snapshot()
    target = snapshot["accepted"][0]["id"]
    requests = [(first, action(snapshot, "approve", [target])), (second, action(snapshot, "reject", [target]))]
    def apply(request):
        try:
            return request[0].apply(request[1])
        except RevisionConflict as error:
            return error
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(apply, requests))
    assert sum(isinstance(result, RevisionConflict) for result in results) == 1
    assert first.snapshot()["revision"] == 1


def test_bad_evidence_and_identity_changes_do_not_append_events(tmp_path):
    store = ReviewStore(make_run(tmp_path))
    before = store.snapshot()
    target = before["accepted"][0]["id"]
    for fields in ({"quote": "This sentence was invented."}, {"origin": "humanAsserted"},
                   {"id": target}, {"kind": "made-up-kind"}, {"start": -1}):
        with pytest.raises(ReviewError):
            store.apply(action(before, "edit", [target], replacements=[fields]))
        assert store.snapshot()["revision"] == 0
    edited = store.apply(action(before, "edit", [target], replacements=[{"actor_quote": "words absent from the source"}]))
    claim = edited["history"][-1]["replacements"][0]
    assert any(issue["code"] == "component_evidence_unresolved" for issue in claim["issues"])
    assert all(store.document["text"][e["start"]:e["end"]] == e["quote"] for e in claim["evidence"])
    approved = store.apply(action(edited, "approve", [claim["id"]]))
    assert approved["current_issues"]
    with pytest.raises(ReviewError, match="replaced"):
        store.apply(action(approved, "approve", [target]))
    assert store.snapshot()["revision"] == 2


def test_qualifications_require_confirmation_after_their_rule_changes(tmp_path):
    store = ReviewStore(make_run(tmp_path))
    before = store.snapshot()
    permission, qualification = before["accepted"][1:]
    old_assertions = list(qualification["assertion_ids"])
    edited = store.apply(action(before, "edit", [permission["id"]], replacements=[{"summary": "Drivers are permitted to depart."}]))
    current_qualification = next(c for c in edited["accepted"] if c["id"] == qualification["id"])
    assert current_qualification["target_ids"] == []
    assert any(issue["code"] == "qualification_target_changed" for issue in current_qualification["link_issues"])
    retained = next(c for c in edited["revisions"] if c["id"] == qualification["id"])
    assert retained["target_ids"] == [permission["id"]]
    assert retained["assertion_ids"] == old_assertions
    confirmed = store.apply(action(edited, "edit", [qualification["id"]], replacements=[{"applies_to": [PERMISSION]}]))
    new_qualification = confirmed["history"][-1]["replacements"][0]
    new_permission = edited["history"][-1]["replacements"][0]
    assert new_qualification["id"] != qualification["id"]
    assert new_qualification["target_ids"] == [new_permission["id"]]
    effective = next(c for c in confirmed["accepted"] if c["id"] == new_qualification["id"])
    assert not effective["link_issues"]
    approved = store.apply(action(confirmed, "approve", [new_qualification["id"]]))
    assert set(json.loads(approved["attestations"][-1]["target_ids_json"])) == set(new_qualification["assertion_ids"])
    assert set(new_qualification["assertion_ids"]) <= {n["@id"] for n in approved["graph"]["@graph"]}


def test_snapshot_does_not_modify_retained_records(tmp_path):
    store = ReviewStore(make_run(tmp_path))
    before = deepcopy(store.base)
    first = store.snapshot()
    first["accepted"][0]["summary"] = "Caller mutated its response."
    assert store.base == before
    assert store.snapshot()["accepted"][0]["summary"] != first["accepted"][0]["summary"]


def test_base_drift_and_event_tampering_are_detected(tmp_path):
    run_dir = make_run(tmp_path)
    store = ReviewStore(run_dir)
    original = store.snapshot()
    store.apply(action(original, "approve", [original["accepted"][0]["id"]]))
    with sqlite3.connect(store.path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("UPDATE events SET payload = '{}' WHERE sequence = 1")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM events WHERE sequence = 1")
        connection.execute("DROP TRIGGER events_no_update")
        connection.execute("UPDATE events SET payload = '{}' WHERE sequence = 1")
    with pytest.raises(ReviewIntegrityError, match="integrity"):
        store.snapshot()
    (run_dir / "run.json").write_text('{"id":"changed"}')
    with pytest.raises(ReviewIntegrityError, match="changed"):
        store.snapshot()
    with pytest.raises(ReviewIntegrityError, match="differs"):
        ReviewStore(run_dir)


@pytest.mark.parametrize("field,value", [("actor_kind", "aiModel"), ("actor_kind", None),
                                          ("actor_kind", []), ("action", []), ("actor", ""),
                                          ("rationale", "  "), ("expected_revision", True)])
def test_reviewer_identity_and_request_shape_are_explicit(tmp_path, field, value):
    store = ReviewStore(make_run(tmp_path))
    snapshot = store.snapshot()
    request = action(snapshot, "approve", [snapshot["accepted"][0]["id"]])
    request[field] = value
    with pytest.raises(ReviewError):
        store.apply(request)
    assert store.snapshot()["revision"] == 0


def seal_manifest(run_dir):
    from rulespec_extrapolator.extraction import _write_manifest
    for name in ("refusals.json", "validation.json", "frozen/candidate-schema.json", "frozen/provider-schema.json",
                 "frozen/examples.json", "frozen/runtime.json", "frozen/prompt.txt"):
        path = run_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    _write_manifest(run_dir)


def test_first_open_verifies_manifest_before_creating_review_database(tmp_path):
    run_dir = make_run(tmp_path)
    seal_manifest(run_dir)
    rulebook = json.loads((run_dir / "rulebook.json").read_text())
    rulebook["accepted"][0]["summary"] = "Supervisors must pay an invented fee."
    (run_dir / "rulebook.json").write_text(canonical(rulebook))
    with pytest.raises(ReviewIntegrityError, match="manifest"):
        ReviewStore(run_dir)
    assert not (run_dir / "review.sqlite3").exists()


def test_manifest_checks_artifacts_without_requiring_extraction_runtime(tmp_path, monkeypatch):
    from rulespec_extrapolator import extraction
    run_dir = make_run(tmp_path)
    seal_manifest(run_dir)
    def never_verify_runtime(*args, **kwargs):
        raise AssertionError("Viewing a review must not require the extraction runtime.")
    monkeypatch.setattr(extraction, "_verify_runtime", never_verify_runtime)
    store = ReviewStore(run_dir)
    assert store.snapshot()["revision"] == 0
    (run_dir / "frozen/prompt.txt").write_text("changed frozen input")
    with pytest.raises(ReviewIntegrityError, match="manifest"):
        store.snapshot()


@pytest.mark.parametrize("mutation", ["summary", "assertion_id", "missing_assertion", "invented_evidence", "invented_claim_quote",
                                       "evidence_position", "fragment_id", "missing_main_evidence"])
def test_manifest_free_claims_must_agree_with_source_and_component_identities(tmp_path, mutation):
    run_dir = make_run(tmp_path)
    rulebook = json.loads((run_dir / "rulebook.json").read_text())
    claim = rulebook["accepted"][0]
    if mutation == "summary":
        claim["summary"] = "Supervisors must pay an invented fee."
    elif mutation == "assertion_id":
        claim["assertion_ids"][0] = "urn:missing:assertion"
    elif mutation == "missing_assertion":
        claim["assertion_ids"].pop()
    elif mutation == "invented_evidence":
        claim["evidence"][0]["quote"] = "Invented source evidence."
    elif mutation == "invented_claim_quote":
        claim["quote"] = claim["evidence"][0]["quote"] = "Invented source evidence."
        claim["start"] = claim["evidence"][0]["start"] = 0
        claim["end"] = claim["evidence"][0]["end"] = len(claim["quote"])
    elif mutation == "evidence_position":
        claim["evidence"][0]["start"] += 1
    elif mutation == "fragment_id":
        claim["evidence"][0]["fragment_id"] = "urn:missing:fragment"
    else:
        claim["evidence"] = [e for e in claim["evidence"] if e["field"] != "summary"]
    (run_dir / "rulebook.json").write_text(canonical(rulebook))
    with pytest.raises(ReviewIntegrityError):
        ReviewStore(run_dir)
    assert not (run_dir / "review.sqlite3").exists()


def test_attestation_targets_must_resolve_before_an_event_is_saved(tmp_path, monkeypatch):
    from rulespec_extrapolator import review_store
    store = ReviewStore(make_run(tmp_path))
    snapshot = store.snapshot()
    original_row = review_store.attestation_row
    def dangling_row(**kwargs):
        return original_row(**{**kwargs, "targets": ["urn:missing:assertion"]})
    monkeypatch.setattr(review_store, "attestation_row", dangling_row)
    with pytest.raises(ReviewIntegrityError, match="attestation target.*missing"):
        store.apply(action(snapshot, "approve", [snapshot["accepted"][0]["id"]]))
    assert store.snapshot()["revision"] == 0


MISSED_RULE = "Operators must log every trip."
MISSED_EXCEPTION = "Unless a trip is canceled."


def missed_candidate():
    return {"kind": "requirement", "summary": "Operators must log every trip.", "actor": "Operators",
            "quote": MISSED_RULE, "actor_quote": "Operators", "action": "log every trip", "action_quote": "log every trip",
            "object": "every trip", "object_quote": "every trip"}


def test_add_missing_rules_keeps_history_without_fabricating_predecessors(tmp_path):
    run_dir = make_run(tmp_path, extra_source=MISSED_RULE + "\n" + MISSED_EXCEPTION)
    original_files = {path.name: path.read_bytes() for path in run_dir.iterdir()}
    store = ReviewStore(run_dir)
    before = store.snapshot()
    added = store.apply(action(before, "add", [], actor="Fixture human reviewer", actor_kind="humanUser", replacements=[
        missed_candidate(),
        {"kind": "exception", "summary": "Canceled trips do not require a log.", "actor": "Operators",
         "actor_quote": "Operators", "quote": MISSED_EXCEPTION, "relation": "exception", "applies_to": [MISSED_RULE]},
    ]))
    event = added["history"][-1]
    assert event["action"] == "add"
    assert event["targets"] == event["assertion_targets"] == []
    assert not event["attestations"]
    new_rules = event["replacements"]
    assert len(new_rules) == 2
    assert new_rules[1]["target_ids"] == [new_rules[0]["id"]]
    old_rule_ids = {c["rule_id"] for c in before["current"]}
    assert len({c["rule_id"] for c in new_rules}) == 2
    assert all(c["rule_id"] not in old_rule_ids for c in new_rules)
    assert all(c["origin"] == "humanAsserted" for c in new_rules)
    assert all("supersedes" not in c and "prior_assertion_ids" not in c for c in new_rules)
    assert all(c["review_status"] == "pending" for c in added["current"][-2:])
    assert added["review_summary"]["usage"] == "review_only"
    assert len(added["accepted"]) == len(before["accepted"]) + 2
    assert canonical(ReviewStore(run_dir).snapshot()) == canonical(added)
    assert {name: (run_dir / name).read_bytes() for name in original_files} == original_files
    assert validate_graph(added["graph"])["shacl_conforms"]
    approved = store.apply(action(added, "approve", [new_rules[0]["id"]], actor="Fixture human reviewer", actor_kind="humanUser"))
    assert approved["attestations"][-1]["attestor_kind"] == "rkaf:humanUser"
    assert approved["attestations"][-1]["method"] == "human"


def test_add_request_retries_and_duplicate_entries_do_not_duplicate_history(tmp_path):
    store = ReviewStore(make_run(tmp_path, extra_source=MISSED_RULE))
    before = store.snapshot()
    with pytest.raises(ReviewError, match="more than once"):
        store.apply(action(before, "add", [], replacements=[missed_candidate(), missed_candidate()]))
    request = action(before, "add", [], replacements=[missed_candidate()])
    added = store.apply(request)
    assert added["history"][-1]["replacements"][0]["origin"] == "aiSuggested"
    with pytest.raises(RevisionConflict):
        store.apply(request)
    assert store.snapshot()["revision"] == 1
    assert len(store.snapshot()["current"]) == 4


@pytest.mark.parametrize("problem", ["predecessor", "identity", "target", "invented_quote", "missing_quote", "empty"])
def test_add_refuses_invalid_evidence_and_predecessors_atomically(tmp_path, problem):
    store = ReviewStore(make_run(tmp_path, extra_source=MISSED_RULE))
    before = store.snapshot()
    candidate = missed_candidate()
    request = action(before, "add", [], replacements=[candidate])
    if problem == "predecessor":
        candidate["supersedes"] = [before["accepted"][0]["id"]]
    elif problem == "identity":
        candidate["rule_id"] = before["accepted"][0]["rule_id"]
    elif problem == "target":
        request["targets"] = [before["accepted"][0]["id"]]
    elif problem == "invented_quote":
        candidate["quote"] = "This text never appeared in the source."
    elif problem == "missing_quote":
        candidate.pop("quote")
    else:
        request["replacements"] = []
    with pytest.raises(ReviewError):
        store.apply(request)
    assert store.snapshot()["revision"] == 0
    assert len(store.snapshot()["current"]) == 3


def test_add_can_recover_a_run_with_no_accepted_candidates(tmp_path):
    run_dir = make_run(tmp_path, extra_source=MISSED_RULE)
    document = json.loads((run_dir / "document.json").read_text())
    run = json.loads((run_dir / "run.json").read_text())
    rulebook = compile_candidates(document, [], run)
    (run_dir / "rulebook.json").write_text(canonical(rulebook))
    store = ReviewStore(run_dir)
    before = store.snapshot()
    assert before["review_summary"]["status"] == "no_claims"
    added = store.apply(action(before, "add", [], replacements=[missed_candidate()]))
    assert len(added["current"]) == 1
    assert added["current"][0]["review_status"] == "pending"
    assert not added["attestations"]
    assert "supersedes" not in added["current"][0]
