"""Independent offline probes against the blind copied packet, with no provider calls.

Run with the assigned interpreter and PYTHONPATH; the script asserts imported
application/projection paths before invoking them. Source files are not edited.
Concise observations are beside this script. Full run artifacts stay under .tools.
"""
from __future__ import annotations

from copy import deepcopy
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rulespec_extrapolator import core, documents, evaluation, extraction, review_store
from rulespec_projection import evidence, projection, provenance, attestations


REPORT = Path(__file__).resolve().parent
PACKET = Path("/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/code/repo").resolve()
RUNS = Path("/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/workflows-artifacts/workflows-runs")
MODULES = (core, documents, evaluation, extraction, review_store,
           evidence, projection, provenance, attestations)
for module in MODULES:
    assert Path(module.__file__).resolve().is_relative_to(PACKET), module.__file__


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def row(quote="Staff must log requests.", **attrs):
    return {"requirement": quote, "requirement_attributes": {
        "summary": quote, "actor": "Staff", "action": "log", "object": "requests",
        "actor_quote": "Staff", "action_quote": "log", "object_quote": "requests", **attrs}}


def raw(text):
    return {"candidates": [{"content": {"parts": [{"text": text}]}, "finish_reason": "STOP"}],
            "model_version": "offline-synthetic-response"}


class OfflineModel:
    """Only consumes supplied values. It contains no SDK/network transport."""
    def __init__(self, responses, schema):
        self.responses = iter(responses)
        self.schema = schema
        self.calls = 0
        self._client = SimpleNamespace(models=SimpleNamespace(generate_content=self.generate))

    def generate(self, **kwargs):
        self.calls += 1
        response = next(self.responses)
        return SimpleNamespace(model_dump=lambda **options: deepcopy(response))

    def infer(self, prompts, **config):
        for prompt in prompts:
            self._client.models.generate_content(model=extraction.DEFAULT_MODEL, contents=prompt,
                config={**config, **self.schema.to_provider_config()})
            yield []


def overflow_failure():
    source = "Staff must log requests."
    valid = json.dumps(row())
    invalid = '{"requirement":"Staff must log requests.","requirement_attributes":{"summary":"Staff must log requests.","actor":1e999}}'
    response_text = '{"extractions":[' + valid + ',' + invalid + ']}'
    response = raw(response_text)
    path = RUNS / "numeric-overflow"
    document = documents.prepare_document(source)
    parsed = extraction.parse_raw_response(response, document, extraction.plan_windows(document)[0])
    models = []
    def create(model_id, key, schema):
        model = OfflineModel([response], schema)
        models.append(model)
        return model
    # Credential/model injection makes the entire transport offline. Real prompt,
    # schema, parser, compiler, run finalization, and artifact writers still run.
    with patch.object(extraction, "_credential", return_value="synthetic-workflows-probe-key"), \
         patch.object(extraction, "_create_model", side_effect=create):
        try:
            extraction.extract_run(document, path)
            raised = None
        except Exception as exc:
            raised = {"type": type(exc).__name__, "message": str(exc)}
    saved_run = json.loads((path / "run.json").read_text())
    attempt = json.loads((path / "attempt-0000.json").read_text())
    refusal_path = path / "refusals.json"
    facts = {
        "raw_response_text": response_text,
        "parse_status": parsed["status"], "accepted_parse_candidates": len(parsed["candidates"]),
        "refusal_codes": [refusal["code"] for refusal in parsed["refusals"]],
        "refused_actor_python_representation": repr(parsed["refusals"][0]["raw"]["requirement_attributes"]["actor"]),
        "raised": raised, "offline_transport_calls": models[0].calls,
        "run_artifact": str(path / "run.json"),
        "saved_run_summary": {key: value for key, value in saved_run.items() if key != "fingerprints"},
        "saved_attempt": attempt,
        "final_artifact_exists": {name: (path / name).exists() for name in (
            "candidates.json", "refusals.json", "rulebook.json", "graph.jsonld", "validation.json", "manifest.json")},
        "refusals_size": refusal_path.stat().st_size if refusal_path.exists() else None,
    }
    write(REPORT / "workflows-overflow-observed.json", facts)
    return {key: value for key, value in facts.items() if key not in {"saved_run_summary", "saved_attempt"}}


def expected_for(text, units):
    source_id = "offline-source"
    source = {"id": source_id, "text": text, "sha256": core.digest(text)}
    span = {"source_id": source_id, "quote": text, "start": 0, "end": len(text)}
    labels = {"schema_version": evaluation.LABEL_VERSION,
              "dataset_id": "offline-workflows-probe", "split": "synthetic",
              "label_provenance": {"reviewer": "Independent workflows probe", "reviewer_kind": "aiAgent", "method": "source_review"},
              "sources": [source],
              "expected_units": [{"id": identity, "excerpt_id": "offline-excerpt", "meaning": meaning,
                                  "source_spans": [deepcopy(span)]} for identity, meaning in units]}
    return labels, span


def omission_accounting():
    text = "Staff must log requests."
    labels, span = expected_for(text, [("unit-1", text)])
    rulebook = {"accepted": [], "run": {"status": "no_candidates"}}
    judgments = {"schema_version": evaluation.JUDGMENT_VERSION,
                 "review_provenance": {"reviewer": "Independent workflows probe", "reviewer_kind": "aiAgent", "method": "source_review"},
                 "rulebook_sha256": evaluation.content_digest(rulebook),
                 "labels_sha256": evaluation.content_digest(labels),
                 "claim_judgments": [],
                 "unit_judgments": [{"unit_id": "unit-1", "status": "missing", "claim_ids": [],
                                     "rationale": "The output contains no claims, so the only source duty is absent.",
                                     "source_spans": [span]}]}
    report = evaluation.evaluate(rulebook, labels, judgments)
    write(REPORT / "workflows-omissions-input.json", {"rulebook": rulebook, "labels": labels, "judgments": judgments})
    write(REPORT / "workflows-omissions-observed.json", report)
    return {key: report[key] for key in ("status", "review_complete", "counts", "coverage", "issues")}


def make_store(name, source, candidates):
    document = documents.prepare_document(source)
    run = {"id": "offline-" + name, "model": "synthetic", "status": "complete", "windows": []}
    rulebook = core.compile_candidates(document, candidates, run)
    path = RUNS / name
    path.mkdir()
    for filename, value in (("document.json", document), ("run.json", run), ("rulebook.json", rulebook)):
        write(path / filename, value)
    return review_store.ReviewStore(path)


def act(store, snapshot, action, targets, replacements=None):
    request = {"expected_revision": snapshot["revision"], "actor": "Independent workflows probe",
               "actor_kind": "aiAgent", "action": action, "targets": targets,
               "rationale": "Bounded offline test of the review state transition."}
    if replacements is not None:
        request["replacements"] = replacements
    return store.apply(request)


def stale_qualification_approval():
    main = "Drivers may depart."
    exception = "Unless the road is closed."
    source = main + "\n" + exception
    store = make_store("stale-qualification", source, [
        {"kind": "permission", "summary": main, "quote": main, "actor": "Drivers", "actor_quote": "Drivers"},
        {"kind": "exception", "summary": "Road closure prevents departure.", "quote": exception,
         "actor": "Drivers", "actor_quote": "Drivers", "relation": "exception", "applies_to": [main]}])
    before = store.snapshot()
    permission, qualification = before["accepted"]
    edited = act(store, before, "edit", [permission["id"]], [{"summary": "Drivers are permitted to depart."}])
    viewed = next(c for c in edited["current"] if c["id"] == qualification["id"])
    approved = act(store, edited, "approve", [qualification["id"]])
    relation_ids = {n["@id"]: n for n in approved["graph"]["@graph"] if n.get("@type") == "rkaf:RelationshipAssertion"}
    attestation_targets = json.loads(approved["attestations"][-1]["target_ids_json"])
    result = {"viewed_target_ids": viewed["target_ids"], "viewed_link_issues": viewed["link_issues"],
              "approved_old_relationships": [relation_ids[i] for i in attestation_targets if i in relation_ids],
              "old_permission_id": permission["id"],
              "new_permission_id": edited["history"][-1]["replacements"][0]["id"],
              "approved_current_qualification": next(c for c in approved["current"] if c["id"] == qualification["id"])}
    write(REPORT / "workflows-stale-qualification-observed.json", result)
    return {"viewed_target_ids": result["viewed_target_ids"], "warnings_retained": bool(result["viewed_link_issues"]),
            "old_relationship_approved": bool(result["approved_old_relationships"])}


def merge_inheritance():
    first = "Staff must lock gates if unattended."
    second = "Staff must log access after every visit."
    source = first + "\n" + second
    store = make_store("merge-inheritance", source, [
        {"kind": "requirement", "summary": first, "quote": first, "actor": "Staff", "actor_quote": "Staff",
         "action": "lock", "action_quote": "lock", "object": "gates", "object_quote": "gates", "logic_text": "if unattended"},
        {"kind": "requirement", "summary": second, "quote": second, "actor": "Staff", "actor_quote": "Staff",
         "action": "log", "action_quote": "log", "object": "access", "object_quote": "access", "logic_text": "after every visit"}])
    before = store.snapshot()
    merged = act(store, before, "merge", [c["id"] for c in before["current"]],
                 [{"summary": "Staff must lock unattended gates and log access after every visit."}])
    result = {"before": before["current"], "merged": merged["current"][0], "current_issues": merged["current_issues"],
              "saved_replacement_fields": merged["history"][-1]["replacement_fields"]}
    write(REPORT / "workflows-merge-observed.json", result)
    return {"action": result["merged"]["action"], "logic_text": result["merged"]["logic_text"],
            "quote": result["merged"]["quote"], "issues": result["merged"]["issues"]}


def split_window_scope():
    # At the default 6000-character limit, a governing line falls in the
    # preceding window. Neither the second window nor its generic section
    # index contains that condition; the quoted duty itself is unchanged.
    condition = "Only when the alarm is active:\n"
    duty = "Staff must evacuate the building."
    filler_line = "General administrative introduction.\n"
    padding = filler_line * ((6000 - len(condition)) // len(filler_line))
    source = padding + condition + duty
    document = documents.prepare_document(source, title="Emergency procedure")
    windows = extraction.plan_windows(document)
    duty_window = next(w for w in windows if duty in source[w["start"]:w["end"]])
    # Generator records its inputs, avoiding any dependency on an LLM.
    capture = SimpleNamespace(render=lambda text, additional_context: {"text": text, "additional_context": additional_context})
    request = extraction._window_prompt(capture, document, duty_window)
    result = extraction.parse_raw_response(raw(json.dumps({"extractions": [row(duty, action="evacuate",
        object="the building", action_quote="evacuate", object_quote="the building")]})), document, duty_window)
    book = core.compile_candidates(document, result["candidates"], {"id": "offline-scope", "windows": windows})
    observations = {"source": source, "condition": condition, "duty": duty, "windows": windows,
                    "duty_request": request, "parsed": result, "accepted": book["accepted"],
                    "unresolved": book["unresolved"],
                    "duty_request_contains_condition": condition.strip() in json.dumps(request)}
    write(REPORT / "workflows-window-observed.json", observations)
    return {"window_count": len(windows), "duty_request_contains_condition": observations["duty_request_contains_condition"],
            "parse_status": result["status"], "claim_issues": book["accepted"][0]["issues"],
            "claim_logic_text": book["accepted"][0]["logic_text"], "unresolved": book["unresolved"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=RUNS, help="An empty directory for generated run artifacts.")
    RUNS = parser.parse_args().runs_dir.resolve()
    if RUNS.exists() and any(RUNS.iterdir()):
        raise SystemExit("Choose a fresh --runs-dir; existing evidence must remain unchanged.")
    RUNS.mkdir(parents=True, exist_ok=True)
    observations = {"modules": {module.__name__: module.__file__ for module in MODULES}}
    for name, probe in (("overflow_failure", overflow_failure), ("omission_accounting", omission_accounting),
                        ("stale_qualification_approval", stale_qualification_approval),
                        ("merge_inheritance", merge_inheritance), ("split_window_scope", split_window_scope)):
        try:
            observations[name] = probe()
        except Exception as exc:
            observations[name] = {"probe_error": type(exc).__name__, "message": str(exc)}
        write(REPORT / "workflows-observed.json", observations)
        print(name + ": " + json.dumps(observations[name], ensure_ascii=False, allow_nan=False), flush=True)
