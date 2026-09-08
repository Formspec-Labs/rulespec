import copy
import importlib.util
import sys
from pathlib import Path

import pytest
from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).parent))

spec = importlib.util.spec_from_file_location("poc", Path(__file__).with_name("poc.py"))
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)


def run(text):
    return {"source_sha256": poc.digest(text), "model": "test-fixture",
            "model_digest": "fixture", "temperature": 0, "seed": 17,
            "prompt_sha256": poc.digest("fixture")}


def candidate(quote, **overrides):
    return {"kind": "requirement", "quote": quote, "summary": "Wear badges",
            "actor": "Visitors", "applies_to": "", "start": None, "end": None, **overrides}


def test_unicode_offsets_and_core_conversion():
    text = "§ Visitors must wear badges."
    result = poc.compile_candidates(text, [candidate("Visitors must wear badges")], run(text))
    assert result["accepted"][0]["start"] == 2  # codepoints, not UTF-8 bytes
    poc.validate_graph(result["graph"])
    assertions = [n for n in result["graph"]["@graph"] if n["@type"] == "rkaf:ValueAssertion"]
    assert assertions[0]["rkaf:usageEligibility"] == "rkaf:reviewQueueOnly"


@pytest.mark.parametrize("quote", ["Wear badges", "Visitors must wear a badge", ""])
def test_absent_or_modified_evidence_is_retained_as_rejection(quote):
    text = "Visitors must wear badges."
    result = poc.compile_candidates(text, [candidate(quote)], run(text))
    assert not result["accepted"]
    assert len(result["rejected"]) == 1


def test_repeated_quote_requires_correct_explicit_location():
    text = "Wear badges. Wear badges."
    result = poc.compile_candidates(text, [candidate("Wear badges")], run(text))
    assert len(result["rejected"]) == 1
    result = poc.compile_candidates(text, [candidate("Wear badges", start=13, end=24)], run(text))
    assert result["accepted"][0]["start"] == 13


def test_exception_links_require_an_unambiguous_grounded_target():
    text = "Visitors must wear badges, except children."
    rule = candidate("Visitors must wear badges")
    exception = candidate("except children", kind="exception", applies_to=rule["quote"])
    result = poc.compile_candidates(text, [rule, exception], run(text))
    assert not result["unresolved"]
    assert result["accepted"][1]["target_id"] == result["accepted"][0]["id"]
    poc.validate_graph(result["graph"])
    absent = poc.compile_candidates(text, [exception], run(text))
    assert len(absent["unresolved"]) == 1
    assert not any(n["@type"] == "rkaf:RelationshipAssertion" for n in absent["graph"]["@graph"])


def test_replay_refuses_changed_source():
    with pytest.raises(ValueError, match="Source digest"):
        poc.compile_candidates("tampered", [], run("original"))


def test_unknown_candidate_type_does_not_silently_disappear():
    text = "Visitors must wear badges."
    result = poc.compile_candidates(text, [candidate(text, kind="imaginary")], run(text))
    assert len(result["rejected"]) == 1


def test_schema_rejects_operational_ai_claim():
    text = "Visitors must wear badges."
    result = poc.compile_candidates(text, [candidate(text)], run(text))
    graph = copy.deepcopy(result["graph"])
    claim = next(n for n in graph["@graph"] if n["@type"] == "rkaf:ValueAssertion")
    claim["rkaf:usageEligibility"] = "rkaf:officialUse"
    with pytest.raises(ValidationError):
        poc.validate_graph(graph)


def test_html_escapes_untrusted_source_and_summary():
    text = "<script>alert(1)</script>"
    result = poc.compile_candidates(text, [candidate(text, summary=text)], run(text))
    page = poc.review_html(text, result)
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_replay_detects_changed_candidates_and_provider_records(tmp_path):
    poc.save(tmp_path / "candidates.json", [])
    poc.save(tmp_path / "request-0.json", {"contents": "original"})
    record = {"candidates_sha256": poc.digest((tmp_path / "candidates.json").read_bytes()),
              "request_sha256": {"request-0.json": poc.digest((tmp_path / "request-0.json").read_bytes())}}
    poc.verify_recorded_run(tmp_path, record)
    poc.save(tmp_path / "candidates.json", ["changed"])
    with pytest.raises(ValueError, match="candidates"):
        poc.verify_recorded_run(tmp_path, record)
    poc.save(tmp_path / "candidates.json", [])
    poc.save(tmp_path / "request-0.json", {"contents": "changed"})
    with pytest.raises(ValueError, match="provider artifact"):
        poc.verify_recorded_run(tmp_path, record)


def test_shacl_accepts_real_double_temperature():
    text = "Visitors must wear badges."
    result = poc.compile_candidates(text, [candidate(text)], run(text))
    assert poc.validate_shacl(result["graph"])["conforms"]


def test_empty_extraction_does_not_report_success(tmp_path, monkeypatch):
    source = tmp_path / "input"
    source.mkdir()
    (source / "source.txt").write_text("Visitors must wear badges.")
    poc.save(source / "run.json", run("Visitors must wear badges."))
    poc.save(source / "candidates.json", [])
    out = tmp_path / "output"
    monkeypatch.setattr(sys, "argv", ["poc.py", "replay", "--input", str(source), "--output", str(out)])
    with pytest.raises(SystemExit, match="No grounded candidates"):
        poc.main()
    assert poc.load(out / "validation.json")["status"] == "no_grounded_candidates"


def test_saved_gemini_exception_targets_publication_not_journal_keeping():
    directory = Path(__file__).parent / "runs/gemini-3.5-flash-03"
    record = poc.load(directory / "run.json")
    poc.verify_recorded_run(directory, record)
    result = poc.compile_candidates((directory / "source.txt").read_text(),
                                    poc.load(directory / "candidates.json"), record)
    exception = next(c for c in result["accepted"] if c["kind"] == "exception")
    target = next(c for c in result["accepted"] if c["id"] == exception["target_id"])
    assert "publish" in target["quote"]
    assert "keep a Journal" not in target["quote"]
    poc.validate_graph(result["graph"])


def v2_candidate(quote, **overrides):
    return candidate(quote, **{"applies_to": [], "relation": "none", **overrides})


def test_shared_scope_emits_one_link_for_each_action():
    text = "During maintenance, staff must not open doors or start motors."
    candidates = [v2_candidate("open doors", kind="prohibition"),
                  v2_candidate("start motors", kind="prohibition"),
                  v2_candidate("During maintenance", kind="condition", relation="scope",
                               applies_to=["open doors", "start motors"])]
    result = poc.compile_candidates(text, candidates, {**run(text), "profile": "v2"})
    assert len(result["accepted"][2]["target_ids"]) == 2
    links = [n for n in result["graph"]["@graph"] if n["@type"] == "rkaf:RelationshipAssertion"]
    assert len(links) == 2
    assert {n["rkaf:assertsPredicate"] for n in links} == {poc.NS + "scope"}
    poc.validate_graph(result["graph"])
    candidates[2]["applies_to"].append("nonexistent action")
    broken = poc.compile_candidates(text, candidates, {**run(text), "profile": "v2"})
    assert len(broken["unresolved"]) == 1
    assert not any(n["@type"] == "rkaf:RelationshipAssertion" for n in broken["graph"]["@graph"])


@pytest.mark.parametrize("kind,relation,targets", [
    ("authority", "scope", ["something"]),
    ("condition", "none", []),
    ("exception", "trigger", ["something"]),
])
def test_v2_rejects_inconsistent_statement_and_relation(kind, relation, targets):
    text = "Some text."
    result = poc.compile_candidates(text, [v2_candidate(text, kind=kind, relation=relation,
        applies_to=targets)], {**run(text), "profile": "v2"})
    assert len(result["rejected"]) == 1


def test_evaluation_detects_omitted_shared_scope_even_without_dangling_links():
    from evaluate_semantics import evaluate
    text = "During maintenance, staff must not open doors or start motors."
    candidates = [v2_candidate("open doors", kind="prohibition"),
                  v2_candidate("start motors", kind="prohibition"),
                  v2_candidate("During maintenance", kind="condition", relation="scope",
                               applies_to=["open doors"])]
    result = poc.compile_candidates(text, candidates, {**run(text), "profile": "v2"})
    assert not result["unresolved"]
    case = {"statements": {"door": {"anchor": "open doors", "kind": "prohibition"},
                           "motor": {"anchor": "start motors", "kind": "prohibition"}},
            "distinct": [["door", "motor"]],
            "qualifications": [{"anchor": "During maintenance", "relation": "scope",
                                "targets": ["door", "motor"]}]}
    report = evaluate(result, case)
    assert report["passed"] == report["total"] - 1
    assert not report["checks"][-1]["pass"]


def test_condition_direction_changes_assertion_identity():
    text = "Upon request, issue receipt."
    main = v2_candidate("issue receipt")
    condition = v2_candidate("Upon request", kind="condition", relation="trigger", applies_to=["issue receipt"])
    record = {**run(text), "profile": "v2"}
    first = poc.compile_candidates(text, [main, condition], record)
    second = poc.compile_candidates(text, [main, {**condition, "relation": "prerequisite"}], record)
    assert first["accepted"][1]["id"] != second["accepted"][1]["id"]
