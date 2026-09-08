"""Offline regressions for raw parsing, terminal accounting, and replay."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator import extraction as e


def row(quote="Staff must log requests", **attributes):
    fields = {name: "" for name in e.TEXT_FIELDS}
    fields.update({name: [] for name in e.LIST_FIELDS})
    fields.update(kind="requirement", summary=quote, actor="Staff", action="log", object="requests",
                  actor_quote="Staff", action_quote="log", object_quote="requests",
                  modality="must", modality_quote="must", relation="none")
    fields.update(attributes)
    return {"unit": quote, "unit_attributes": fields}


def raw(payload=None, *, text=None, finish="STOP"):
    if text is None:
        text = json.dumps({"extractions": [row()] if payload is None else payload})
    return {"candidates": [{"content": {"parts": [{"text": text}]}, "finish_reason": finish}],
            "model_version": "gemini-3.8-flash"}


def parsed(response, text="Staff must log requests."):
    document = prepare_document(text)
    return e.parse_raw_response(response, document, e.plan_windows(document)[0])


def codes(result):
    return {refusal["code"] for refusal in result["refusals"]}


def test_window_partition_has_complete_unicode_coverage_and_global_offsets():
    text = "Intro ☃.\nStaff must log requests.\nGuests may borrow maps."
    document = prepare_document(text)
    windows = e.plan_windows(document, max_chars=28)
    assert windows == e.plan_windows(document, max_chars=28)
    assert "".join(text[w["start"]:w["end"]] for w in windows) == text
    assert all(a["end"] == b["start"] for a, b in zip(windows, windows[1:]))
    assert all(0 < w["end"] - w["start"] <= 28 for w in windows)
    window = next(w for w in windows if "Staff must log requests" in text[w["start"]:w["end"]])
    result = e.parse_raw_response(raw(), document, window)
    candidate = result["candidates"][0]
    assert candidate["start"] == text.index("Staff")
    assert text[candidate["start"]:candidate["end"]] == candidate["quote"]
    assert candidate["window_id"] == window["id"]


@pytest.mark.parametrize("max_chars", [0, -1, True, 1.5])
def test_invalid_window_size_is_refused(max_chars):
    with pytest.raises(ValueError):
        e.plan_windows(prepare_document("Source"), max_chars)


def test_parser_uses_raw_text_not_sdk_parsed_cache():
    response = raw()
    response["parsed"] = {"extractions": [row("An invented obligation")]}
    result = parsed(response)
    assert result["status"] == "complete"
    assert result["candidates"][0]["quote"] == "Staff must log requests"


def test_legacy_per_kind_output_is_refused():
    legacy = {"requirement": "Staff must log requests", "requirement_attributes": {
        "summary": "Staff must log requests", "actor": "Staff"}}
    result = parsed(raw([legacy, row()]))
    assert len(result["candidates"]) == 1
    assert result["status"] == "partial"
    assert codes(result) == {"invalid_semantic_unit"}


def test_fenced_json_and_split_text_parts_replay_faithfully():
    text = "```json\n" + json.dumps({"extractions": [row()]}) + "\n```"
    response = raw(text=text)
    response["candidates"][0]["content"]["parts"] = [
        {"text": "Internal thought", "thought": True}, {"text": text[:27]}, {"text": text[27:]},
    ]
    assert parsed(response) == parsed(raw())


@pytest.mark.parametrize("text,code", [
    ('{"extractions": [', "malformed_json"),
    ('```json\n{"extractions": []}', "malformed_fence"),
    ('Here is the answer: {"extractions": []}', "malformed_json"),
    ('{"extractions": [], "extractions": []}', "duplicate_json_key"),
    ('{"extractions": null}', "invalid_extractions_wrapper"),
    ('[]', "invalid_extractions_wrapper"),
    ('{"extractions": [NaN]}', "malformed_json"),
    ('', "empty_response"),
])
def test_malformed_responses_fail_explicitly(text, code):
    result = parsed(raw(text=text))
    assert result["status"] == "failed"
    assert code in codes(result)
    assert not result["candidates"]


def test_valid_empty_output_is_distinct_from_missing_provider_content():
    result = parsed(raw([]))
    assert result == {"candidates": [], "refusals": [], "status": "no_candidates"}
    missing = parsed({"candidates": []})
    assert missing["status"] == "failed"
    assert "missing_provider_candidates" in codes(missing)


def test_invalid_rows_do_not_hide_valid_rows_or_their_failure():
    response = raw([row(), "invalid", row(actor=None), row(kind="mystery"),
                    {"requirement_attributes": {}}, row(extra_field="unexpected")])
    result = parsed(response)
    assert result["status"] == "partial"
    assert len(result["candidates"]) == 1
    assert codes(result) == {"invalid_semantic_unit"}
    assert result["refusals"][0]["raw"] == "invalid"


def test_overflow_refusal_is_serializable_and_preserves_valid_neighbor():
    response = raw(text='{"extractions": [' + json.dumps(row()) +
                        ', {"requirement": "Staff", "requirement_attributes": {"summary": 1e999, "actor": "Staff"}}]}')
    result = parsed(response)
    assert result["status"] == "partial"
    assert len(result["candidates"]) == 1
    serialized = json.dumps(result, allow_nan=False)
    assert "1e999" in serialized


@pytest.mark.parametrize("field", ["actor", "scope_quotes", "modality", "alternative_quotes"])
def test_missing_required_attributes_are_not_invented(field):
    malformed = row()
    del malformed["unit_attributes"][field]
    result = parsed(raw([malformed]))
    assert result["status"] == "failed"
    assert codes(result) == {"invalid_semantic_unit"}


@pytest.mark.parametrize("response", [None, [], {"candidates": [None]},
    {"candidates": [{"content": "invalid", "finish_reason": "STOP"}]},
    {"candidates": [{"content": {"parts": [None]}, "finish_reason": "STOP"}]},
    {"prompt_feedback": "invalid", "candidates": []}])
def test_malformed_provider_shapes_produce_terminal_refusals(response):
    assert parsed(response)["status"] == "failed"


def test_nonstop_finish_cannot_look_complete_even_with_valid_json():
    result = parsed(raw(finish="MAX_TOKENS"))
    assert result["status"] == "partial"
    assert len(result["candidates"]) == 1
    assert "provider_incomplete" in codes(result)


def test_blocked_empty_and_nontext_responses_remain_visible():
    blocked = parsed({"prompt_feedback": {"block_reason": "SAFETY"}})
    assert {"provider_blocked_prompt", "missing_provider_candidates"} <= codes(blocked)
    response = raw()
    response["candidates"][0]["content"]["parts"] = [{"function_call": {"name": "unexpected"}}]
    result = parsed(response)
    assert {"nontext_provider_part", "empty_response"} <= codes(result)
    assert result["status"] == "failed"


@pytest.mark.parametrize("quote,source,code", [
    ("Staff must log requests", "Staff must log requests. Staff must log requests.", "ambiguous_quote_in_window"),
    ("Staff must log requests", "Staff may log requests.", "quote_not_in_window"),
])
def test_no_fuzzy_or_ambiguous_evidence_alignment(quote, source, code):
    result = parsed(raw([row(quote)]), source)
    assert result["status"] == "failed"
    assert codes(result) == {code}


def test_quote_outside_window_is_not_recovered_from_whole_document():
    document = prepare_document("Staff must log requests.\nDifferent source window.")
    window = e.plan_windows(document, 27)[-1]
    result = e.parse_raw_response(raw(), document, window)
    assert result["status"] == "failed"
    assert "quote_not_in_window" in codes(result)


def test_remote_references_and_complex_logic_are_preserved():
    text = "For section 2, two votes and a written request are required."
    item = row(text, kind="condition", summary="Section 2 requires two votes and a written request",
               actor="", actor_quote="", action="", action_quote="", object="", object_quote="",
               modality="not_stated", modality_quote="", relation="prerequisite",
               applies_to=[], references=["section 2"], logic_text="two votes and a written request")
    result = parsed(raw([item]), text)
    assert result["status"] == "complete"
    assert result["candidates"][0]["references"] == ["section 2"]
    assert result["candidates"][0]["logic_text"] == "two votes and a written request"


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.text = "unused: raw response parsing is independent"

    def model_dump(self, **kwargs):
        assert kwargs["exclude"] == {"sdk_http_response"}
        return deepcopy(self.payload)


class FakeModel:
    def __init__(self, responses, schema):
        self.responses = iter(responses)
        self.schema = schema
        self.calls = 0
        self._client = SimpleNamespace(models=SimpleNamespace(generate_content=self.generate))

    def generate(self, **kwargs):
        self.calls += 1
        response = next(self.responses)
        if isinstance(response, BaseException):
            raise response
        return FakeResponse(response)

    def infer(self, prompts, **config):
        for prompt in prompts:
            response = self._client.models.generate_content(model=e.DEFAULT_MODEL, contents=prompt,
                config={**config, **self.schema.to_provider_config()})
            yield [SimpleNamespace(output=response.text)]


@pytest.fixture
def offline(monkeypatch, tmp_path):
    models = []
    env_file = tmp_path / "credentials.env"
    env_file.write_text("GEMINI_API_KEY=synthetic-test-credential\n")

    def install(responses):
        def create(model_id, key, schema):
            assert key == "synthetic-test-credential"
            model = FakeModel(responses, schema)
            models.append(model)
            return model
        monkeypatch.setattr(e, "_create_model", create)
        return env_file
    return install, models


@pytest.fixture
def failed_compilation(offline, tmp_path, monkeypatch):
    install, models = offline
    env_file = install([raw()])
    original = tmp_path / "failed-compilation"

    def fail(*args):
        raise ValueError("Do not retain arbitrary compiler exception values")

    with monkeypatch.context() as patch:
        patch.setattr(e.core, "compile_candidates", fail)
        with pytest.raises(RuntimeError, match="attempted run was saved"):
            e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    return original, models


def test_recorded_run_and_raw_replay_are_identical_without_provider_calls(offline, tmp_path, monkeypatch):
    install, models = offline
    env_file = install([raw()])
    directory = tmp_path / "original"
    document = prepare_document("Staff must log requests.")
    rulebook = e.extract_run(document, directory, env_file=env_file)
    assert rulebook["run"]["status"] == "complete"
    assert len(rulebook["accepted"]) == 1
    assert models[0].calls == 1
    original_bytes = {str(p.relative_to(directory)): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    monkeypatch.setattr(e, "_create_model", lambda *args: pytest.fail("Replay called the provider"))
    replayed = e.replay_run(directory, tmp_path / "replay")
    assert replayed == rulebook
    assert all((directory / name).read_bytes() == data for name, data in original_bytes.items())
    assert (directory / "candidates.json").read_bytes() == (tmp_path / "replay/candidates.json").read_bytes()
    assert (directory / "graph.jsonld").read_bytes() == (tmp_path / "replay/graph.jsonld").read_bytes()
    with pytest.raises(FileExistsError):
        e.extract_run(document, directory, env_file=env_file)
    with pytest.raises(FileExistsError):
        e.replay_run(directory, directory)


def test_overflow_run_finishes_replays_and_reprocesses(offline, tmp_path):
    install, models = offline
    text = '{"extractions": [' + json.dumps(row()) + ', {"mystery": {"nested": [1e999, -1e999]}}]}'
    env_file = install([raw(text=text)])
    directory = tmp_path / "overflow"
    book = e.extract_run(prepare_document("Staff must log requests."), directory, env_file=env_file)
    assert book["run"]["status"] == "partial"
    assert len(book["accepted"]) == 1
    assert (directory / "manifest.json").is_file()
    assert text == e._load(directory / "attempt-0000.response.json")["candidates"][0]["content"]["parts"][0]["text"]
    assert e.replay_run(directory, tmp_path / "overflow-replay") == book
    processed = e.reprocess_run(directory, tmp_path / "overflow-reprocessed")
    assert processed["extraction_refusals"] == book["extraction_refusals"]
    assert len(processed["accepted"]) == 1
    assert models[0].calls == 1


def test_successful_window_cannot_hide_failed_window_and_replays(offline, tmp_path):
    install, models = offline
    document = prepare_document("Staff must log requests.\nStaff may issue passes.")
    windows = e.plan_windows(document, max_chars=26)
    assert len(windows) == 2
    env_file = install([raw(), raw(text='{"extractions": [')])
    rulebook = e.extract_run(document, tmp_path / "partial", env_file=env_file, max_chars=26)
    assert models[0].calls == 2
    assert rulebook["run"]["status"] == "partial"
    assert [window["status"] for window in rulebook["run"]["windows"]] == ["complete", "failed"]
    assert all(len(window["attempts"]) == 1 for window in rulebook["run"]["windows"])
    assert "malformed_json" in {r["code"] for r in rulebook["extraction_refusals"]}
    assert e.replay_run(tmp_path / "partial", tmp_path / "replayed") == rulebook


def test_provider_errors_do_not_store_or_print_credentials(offline, tmp_path, capsys):
    install, _ = offline
    env_file = install([RuntimeError("https://provider/?key=synthetic-test-credential")])
    rulebook = e.extract_run(prepare_document("Staff must log requests."), tmp_path / "failed", env_file=env_file)
    assert rulebook["run"]["status"] == "failed"
    assert rulebook["extraction_refusals"][0]["code"] == "provider_request_failed"
    records = b"".join(p.read_bytes() for p in (tmp_path / "failed").rglob("*") if p.is_file())
    assert b"synthetic-test-credential" not in records
    assert b"https://provider/" not in records
    assert "synthetic-test-credential" not in str(capsys.readouterr())
    assert e.replay_run(tmp_path / "failed", tmp_path / "replayed")["run"]["status"] == "failed"


def test_credential_echo_in_response_is_not_written(offline, tmp_path):
    install, _ = offline
    env_file = install([raw(text="synthetic-test-credential")])
    rulebook = e.extract_run(prepare_document("Staff must log requests."), tmp_path / "failed", env_file=env_file)
    assert rulebook["extraction_refusals"][0]["code"] == "response_recording_failed"
    assert not list((tmp_path / "failed").glob("*.response.json"))


def test_real_langextract_adapter_records_explicit_schema_and_generation_settings(tmp_path):
    schema = e.provider_schema()
    model = e._create_model(e.DEFAULT_MODEL, "synthetic-test-credential", schema)
    sdk_client = model._client
    fake = FakeModel([raw()], schema)
    model._client = fake._client
    document = prepare_document("Staff must log requests.")
    window = e.plan_windows(document)[0]
    attempt = e._record_window(model, "An offline prompt", tmp_path, window, "synthetic-test-credential", temperature=0.2)
    sdk_client.close()
    request = e._load(tmp_path / attempt["request_file"])
    assert attempt["status"] == "response_received"
    assert fake.calls == 1
    assert request["config"] == {"temperature": 0.2, "max_output_tokens": e.MAX_OUTPUT_TOKENS,
        "candidate_count": 1, "response_mime_type": "application/json",
        "response_json_schema": schema.schema_dict}


def test_native_schema_preserves_closed_meaning_fields_without_json_prompt_examples():
    from jsonschema import Draft202012Validator
    schema = e.provider_schema().schema_dict
    row_schema = schema["properties"]["extractions"]["items"]
    attrs = row_schema["properties"]["unit_attributes"]
    assert set(attrs["required"]) == {*e.TEXT_FIELDS, *e.LIST_FIELDS}
    assert attrs["additionalProperties"] is False
    assert attrs["properties"]["modality"]["enum"] == list(e.core.MODALITIES)
    assert set(attrs["properties"]["kind"]["enum"]) == set(e.core.KINDS)
    for example in e.invented_examples():
        for item in example.extractions:
            Draft202012Validator(row_schema).validate({"unit": item.extraction_text, "unit_attributes": item.attributes})
    prompt = e._prompt_generator(e.invented_examples()).render("Staff must log requests.")
    assert "invoice bearing the account number" in prompt
    assert '"unit_attributes"' not in prompt


def test_temperature_survives_recording_replay_and_reprocessing(offline, tmp_path):
    install, _ = offline
    env = install([raw([row()])])
    original = tmp_path / "temperature"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env, temperature=0.2)
    assert e._load(original / "attempt-0000.request.json")["config"]["temperature"] == 0.2
    assert e.replay_run(original, tmp_path / "replayed")["run"]["temperature"] == 0.2
    assert e.reprocess_run(original, tmp_path / "reprocessed")["run"]["temperature"] == 0.2
    assert e.replay_run(tmp_path / "reprocessed", tmp_path / "reprocessed-replay")["run"]["temperature"] == 0.2
    with pytest.raises(ValueError, match="Temperature"):
        e.extract_run(prepare_document("Text"), tmp_path / "invalid", temperature=float('nan'))
    assert not (tmp_path / "invalid").exists()


@pytest.mark.parametrize("mixed", [False, True])
def test_compiler_rejection_changes_final_status_without_erasing_parse_status(offline, tmp_path, mixed):
    install, _ = offline
    invalid = row(relation="prerequisite", applies_to=["Staff must log requests"])
    env_file = install([raw(([row()] if mixed else []) + [invalid])])
    original = tmp_path / "original"
    rulebook = e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    assert rulebook["run"]["processing_status"] == "complete"
    assert rulebook["run"]["status"] == ("partial" if mixed else "failed")
    assert len(rulebook["rejected"]) == 1
    if not mixed:
        assert rulebook["run"]["failure_code"] == "no_grounded_candidates"
    assert e.replay_run(original, tmp_path / "replayed") == rulebook


def test_graph_validation_failure_preserves_graph_and_replays(offline, tmp_path, monkeypatch):
    install, _ = offline
    env_file = install([raw()])
    def fail(graph):
        raise ValueError("Do not retain arbitrary exception values")
    monkeypatch.setattr(e.core, "validate_graph", fail)
    directory = tmp_path / "original"
    rulebook = e.extract_run(prepare_document("Staff must log requests."), directory, env_file=env_file)
    assert rulebook["run"]["status"] == "failed"
    assert rulebook["run"]["failure_code"] == "graph_validation_failed"
    assert (directory / "attempt-0000.response.json").exists()
    assert (directory / "graph.jsonld").exists()
    validation = e._load(directory / "validation.json")
    assert validation == {"status": "failed", "error_code": "graph_validation_failed", "error_type": "ValueError"}
    assert e.replay_run(directory, tmp_path / "replayed") == rulebook


def test_recorded_compilation_failure_recovers_only_through_reprocessing(failed_compilation, tmp_path, monkeypatch):
    from rulespec_extrapolator.review_store import ReviewIntegrityError, ReviewStore

    original, models = failed_compilation
    monkeypatch.setattr(e, "_create_model", lambda *args: pytest.fail("Recovery called a provider"))
    assert not (original / "rulebook.json").exists()
    assert not (original / "graph.jsonld").exists()
    failed_run = e._load(original / "run.json")
    assert failed_run["status"] == "failed"
    assert failed_run["failure_code"] == "compilation_failed"
    assert e._load(original / "validation.json") == {
        "status": "failed", "stage": "compilation", "error_code": "compilation_failed", "error_type": "ValueError"}
    original_bytes = {path.relative_to(original).as_posix(): path.read_bytes()
                      for path in original.rglob("*") if path.is_file()}
    with pytest.raises(e.ReplayDriftError, match="required artifact"):
        e._verify_manifest(original)
    with pytest.raises(e.ReplayDriftError, match="required artifact"):
        e.replay_run(original, tmp_path / "strict-replay")
    with pytest.raises(ReviewIntegrityError):
        ReviewStore(original)
    assert not (original / "review.sqlite3").exists()

    recovered = e.reprocess_run(original, tmp_path / "recovered")
    assert recovered["run"]["status"] == "complete"
    assert "failure_code" not in recovered["run"]
    assert recovered["run"]["id"] == failed_run["id"]
    assert recovered["run"]["reprocessing"]["provider_calls"] == 0
    assert recovered["run"]["reprocessing"]["candidates_identical"] is True
    assert len(recovered["accepted"]) == 1
    assert models[0].calls == 1
    assert all((original / name).read_bytes() == content for name, content in original_bytes.items())
    assert e._load(tmp_path / "recovered/previous/run.json") == failed_run
    assert e.replay_run(tmp_path / "recovered", tmp_path / "recovered-replay") == recovered


@pytest.mark.parametrize("filename,changes", [
    ("run.json", {"status": "complete"}),
    ("run.json", {"failure_code": "graph_validation_failed"}),
    ("validation.json", {"status": "passed"}),
    ("validation.json", {"stage": "graph_validation"}),
    ("validation.json", {"error_code": "graph_validation_failed"}),
])
def test_compilation_recovery_requires_matching_failure_records(failed_compilation, tmp_path, filename, changes):
    original, _ = failed_compilation
    value = e._load(original / filename)
    value.update(changes)
    e._save(original / filename, value)
    e._write_manifest(original)
    with pytest.raises(e.ReplayDriftError, match="recorded compilation failure"):
        e.reprocess_run(original, tmp_path / "recovered")
    assert not (tmp_path / "recovered").exists()


@pytest.mark.parametrize("artifact", [
    "attempt-0000.json", "attempt-0000.request.json", "attempt-0000.response.json",
    "frozen/sources/application/core.py", "frozen/provider-schema.json",
    "candidates.json", "refusals.json", "validation.json",
])
def test_compilation_recovery_still_requires_all_pinned_inputs(failed_compilation, tmp_path, artifact):
    original, _ = failed_compilation
    (original / artifact).unlink()
    e._write_manifest(original)
    with pytest.raises(e.ReplayDriftError):
        e.reprocess_run(original, tmp_path / "recovered")
    assert not (tmp_path / "recovered").exists()


@pytest.mark.parametrize("artifact", ["rulebook.json", "graph.jsonld"])
def test_reprocessing_cannot_repair_missing_completed_outputs(offline, tmp_path, artifact):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "completed"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    (original / artifact).unlink()
    e._write_manifest(original)
    with pytest.raises(e.ReplayDriftError, match="recorded compilation failure"):
        e.reprocess_run(original, tmp_path / "reprocessed")
    assert not (tmp_path / "reprocessed").exists()


def test_explicit_envfile_has_precedence_and_does_not_expand_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("GEMINI_API_KEY", "wrong-environment-key")
    monkeypatch.setenv("ANOTHER_SECRET", "do-not-expand")
    env_file = tmp_path / "chosen.env"
    env_file.write_text("GEMINI_API_KEY='${ANOTHER_SECRET}'\n")
    assert e._credential(env_file) == "${ANOTHER_SECRET}"
    env_file.write_text("UNRELATED=1\n")
    with pytest.raises(ValueError):
        e._credential(env_file)


def test_setup_failure_records_every_planned_window(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    rulebook = e.extract_run(prepare_document("One source line.\nSecond source line."), tmp_path / "failed", max_chars=20)
    windows = rulebook["run"]["windows"]
    assert len(windows) == 2
    assert all(window["status"] == "failed" and window["attempts"] for window in windows)
    assert len(rulebook["extraction_refusals"]) == 2


def test_no_candidates_and_partial_empty_runs_are_explicit(offline, tmp_path):
    install, _ = offline
    env_file = install([raw([])])
    rulebook = e.extract_run(prepare_document("An ordinary descriptive sentence."), tmp_path / "empty", env_file=env_file)
    assert rulebook["run"]["status"] == "no_candidates"
    assert not rulebook["accepted"]
    env_file = install([raw([]), RuntimeError("provider failed")])
    partial = e.extract_run(prepare_document("First sentence.\nSecond sentence."), tmp_path / "partial", env_file=env_file, max_chars=18)
    assert partial["run"]["status"] == "partial"
    assert not partial["accepted"]


@pytest.mark.parametrize("artifact", ["document.json", "candidates.json", "attempt-0000.response.json", "frozen/prompt.txt"])
def test_replay_refuses_changed_recorded_artifacts(offline, tmp_path, artifact):
    install, _ = offline
    env_file = install([raw()])
    directory = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), directory, env_file=env_file)
    path = directory / artifact
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(e.ReplayDriftError, match="recorded artifact"):
        e.replay_run(directory, tmp_path / "replay")
    assert not (tmp_path / "replay").exists()


def test_replay_reparses_instead_of_trusting_candidates_even_with_updated_hash(offline, tmp_path):
    install, _ = offline
    env_file = install([raw()])
    directory = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), directory, env_file=env_file)
    candidates = e._load(directory / "candidates.json")
    candidates[0]["summary"] = "Staff must pay an invented fee"
    e._save(directory / "candidates.json", candidates)
    e._write_manifest(directory)
    with pytest.raises(e.ReplayDriftError, match="different candidates"):
        e.replay_run(directory, tmp_path / "replay")


def test_replay_refuses_prompt_and_dependency_drift(offline, tmp_path, monkeypatch):
    install, _ = offline
    env_file = install([raw()])
    directory = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), directory, env_file=env_file)
    original_prompt = e.PROMPT
    monkeypatch.setattr(e, "PROMPT", original_prompt + "Changed instructions")
    with pytest.raises(e.ReplayDriftError, match="prompt_sha256"):
        e.replay_run(directory, tmp_path / "replay")
    monkeypatch.setattr(e, "PROMPT", original_prompt)
    versions = e._runtime_versions()
    versions["packages"]["google-genai"] = "0.0.0"
    monkeypatch.setattr(e, "_runtime_versions", lambda: versions)
    with pytest.raises(e.ReplayDriftError, match="runtime"):
        e.replay_run(directory, tmp_path / "replay")


def test_reprocess_after_runtime_drift_preserves_model_capture_and_independently_replays(offline, tmp_path, monkeypatch):
    install, models = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    before = e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    original_bytes = {path.relative_to(original).as_posix(): path.read_bytes()
                      for path in original.rglob("*") if path.is_file()}
    versions = e._runtime_versions()
    versions["packages"]["google-genai"] += "+changed-runtime"
    monkeypatch.setattr(e, "_runtime_versions", lambda: versions)
    monkeypatch.setattr(e, "_create_model", lambda *args: pytest.fail("Reprocessing called a provider"))
    with pytest.raises(e.ReplayDriftError, match="runtime"):
        e.replay_run(original, tmp_path / "strict-replay")
    after = e.reprocess_run(original, tmp_path / "reprocessed")
    assert after["run"]["id"] == before["run"]["id"]
    assert after["run"]["record_kind"] == "pipeline_reprocessing"
    assert after["run"]["reprocessing"]["provider_calls"] == 0
    assert after["run"]["reprocessing"]["candidates_identical"] is True
    assert after["accepted"][0]["id"] == before["accepted"][0]["id"]
    assert after["accepted"][0]["assertion_ids"] == before["accepted"][0]["assertion_ids"]
    assert after["run"]["reprocessed_from"]["response_sha256"]
    assert models[0].calls == 1
    assert all((original / name).read_bytes() == content for name, content in original_bytes.items())
    assert (original / "attempt-0000.response.json").read_bytes() == (tmp_path / "reprocessed/attempt-0000.response.json").read_bytes()
    assert e.replay_run(tmp_path / "reprocessed", tmp_path / "replayed") == after
    # Reprocessing does not turn the original extraction into a valid strict replay.
    with pytest.raises(e.ReplayDriftError, match="runtime"):
        e.replay_run(original, tmp_path / "still-strict")


def test_reprocess_keeps_actual_old_prompt_when_current_prompt_changes(offline, tmp_path, monkeypatch):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    before = e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    monkeypatch.setattr(e, "PROMPT", e.PROMPT + "\nDifferent current instructions.\n")
    after = e.reprocess_run(original, tmp_path / "reprocessed")
    run = after["run"]
    assert run["prompt_sha256"] == before["run"]["prompt_sha256"]
    assert run["fingerprints"]["prompt_sha256"] != run["prompt_sha256"]
    assert run["reprocessing"]["acquisition_matches_current"]["prompt"] is False
    assert run["reprocessing"]["acquisition_matches_current"]["requests"] is False
    assert e.replay_run(tmp_path / "reprocessed", tmp_path / "replayed") == after


def test_reprocess_reparses_raw_instead_of_copying_old_candidates(offline, tmp_path, monkeypatch):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    parser = e.parse_raw_response
    def changed_parser(*args):
        result = parser(*args)
        result["candidates"][0]["summary"] = "Staff are required to log requests"
        return result
    monkeypatch.setattr(e, "parse_raw_response", changed_parser)
    after = e.reprocess_run(original, tmp_path / "reprocessed")
    assert after["run"]["reprocessing"]["candidates_identical"] is False
    assert after["accepted"][0]["summary"] == "Staff are required to log requests"
    assert e._load(tmp_path / "reprocessed/previous/candidates.json")[0]["summary"] == "Staff must log requests"
    assert e.replay_run(tmp_path / "reprocessed", tmp_path / "replayed") == after


def test_reprocess_preserves_failed_windows_and_supports_another_reprocessing(offline, tmp_path):
    install, _ = offline
    env_file = install([raw(), raw(text='{"extractions": [')])
    original = tmp_path / "original"
    before = e.extract_run(prepare_document("Staff must log requests.\nOther source text."), original, env_file=env_file, max_chars=26)
    first = e.reprocess_run(original, tmp_path / "first")
    second = e.reprocess_run(tmp_path / "first", tmp_path / "second")
    assert first["run"]["status"] == second["run"]["status"] == "partial"
    assert second["extraction_refusals"] == before["extraction_refusals"]
    assert [window["status"] for window in second["run"]["windows"]] == ["complete", "failed"]
    assert e.replay_run(tmp_path / "second", tmp_path / "replayed") == second


@pytest.mark.parametrize("artifact", ["frozen/prompt.txt", "frozen/sources/application/core.py", "attempt-0000.response.json"])
def test_reprocess_refuses_original_tampering(offline, tmp_path, artifact):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    path = original / artifact
    path.write_bytes(path.read_bytes() + b" altered")
    with pytest.raises(e.ReplayDriftError):
        e.reprocess_run(original, tmp_path / "reprocessed")
    assert not (tmp_path / "reprocessed").exists()


def test_reprocess_checks_original_prompt_even_when_request_hash_is_updated(offline, tmp_path):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    request = e._load(original / "attempt-0000.request.json")
    request["contents"] = "Different source and prompt"
    e._save(original / "attempt-0000.request.json", request)
    run = e._load(original / "run.json")
    run["windows"][0]["request_sha256"] = e._digest((original / "attempt-0000.request.json").read_bytes())
    e._save(original / "run.json", run)
    e._write_manifest(original)
    with pytest.raises(e.ReplayDriftError, match="acquisition prompt"):
        e.reprocess_run(original, tmp_path / "reprocessed")


def test_reprocess_refuses_frozen_fingerprint_disagreement_even_with_updated_manifest(offline, tmp_path):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    (original / "frozen/prompt.txt").write_text("Changed saved instructions")
    e._write_manifest(original)
    with pytest.raises(e.ReplayDriftError, match="declared fingerprint"):
        e.reprocess_run(original, tmp_path / "reprocessed")


def test_reprocessed_replay_requires_complete_original_capture_digests(offline, tmp_path):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    e.reprocess_run(original, tmp_path / "reprocessed")
    path = tmp_path / "reprocessed/run.json"
    run = e._load(path)
    run["reprocessed_from"]["response_sha256"] = {}
    e._save(path, run)
    e._write_manifest(tmp_path / "reprocessed")
    with pytest.raises(e.ReplayDriftError, match="provider-capture digest"):
        e.replay_run(tmp_path / "reprocessed", tmp_path / "replayed")


def test_reprocessing_output_cannot_modify_original_directory(offline, tmp_path):
    install, _ = offline
    env_file = install([raw()])
    original = tmp_path / "original"
    e.extract_run(prepare_document("Staff must log requests."), original, env_file=env_file)
    with pytest.raises(FileExistsError):
        e.reprocess_run(original, original)
    with pytest.raises(ValueError, match="outside"):
        e.reprocess_run(original, original / "nested-output")
