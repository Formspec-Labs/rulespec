"""Semantic review must not inherit the prototype's false-summary 20/20 result."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest

from rulespec_extrapolator.evaluation import (
    MEANING_DIMENSIONS,
    claim_digest,
    compare_runs,
    content_digest,
    evaluate,
    subset_expected,
    validate_expected,
)

EVALUATION = Path(__file__).resolve().parents[1] / "evaluation"


@pytest.fixture
def reviewed_output():
    labels = json.loads((EVALUATION / "development-labels.json").read_text())
    labels["expected_units"] = [unit for unit in labels["expected_units"]
                                if unit["id"] in {"fam-photos-06-u03", "fam-photos-06-u04"}]
    specialist, applicant = labels["expected_units"]
    quote = specialist["source_spans"][0]["quote"]
    rulebook = {"schema_version": "document-understanding/2", "accepted": [
        {"id": "claim-1", "rule_id": "rule-1", "kind": "requirement",
         "summary": "Passport specialists must suspend DS-11 applications received without a photograph from an acceptance facility.",
         "actor": "Passport specialists", "quote": quote, "target_ids": []},
        {"id": "claim-2", "rule_id": "rule-2", "kind": "requirement",
         "summary": "The applicant must re-execute that DS-11.",
         "actor": "The applicant", "quote": quote, "target_ids": []},
    ]}
    judgments = {
        "schema_version": "rulespec-evaluation-judgments/1",
        "review_provenance": {"reviewer": "Evaluation regression author", "reviewer_kind": "aiAgent", "method": "source_review"},
        "rulebook_sha256": content_digest(rulebook), "labels_sha256": content_digest(labels),
        "claim_judgments": [], "unit_judgments": [],
    }
    for claim, unit in zip(rulebook["accepted"], (specialist, applicant)):
        judgments["claim_judgments"].append({
            "claim_id": claim["id"], "claim_sha256": claim_digest(claim),
            "unit_ids": [unit["id"]], "dimensions": {key: "correct" for key in MEANING_DIMENSIONS},
            "rationale": "Source paragraph explicitly separates the specialist suspension and applicant re-execution duties; this claim preserves its assigned duty and scope.",
            "source_spans": unit["source_spans"],
        })
        judgments["unit_judgments"].append({
            "unit_id": unit["id"], "status": "covered", "claim_ids": [claim["id"]],
            "rationale": "The reviewed claim preserves this expected action, actor, and condition.",
            "source_spans": unit["source_spans"],
        })
    return rulebook, labels, judgments


def test_complete_explicit_source_review_passes(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "passed"
    assert report["coverage"]["covered"] == 2
    assert report["dimensions"]["actor"]["correct"] == 2
    assert report["review_provenance"]["reviewer_kind"] == "aiAgent"


def test_fully_judged_total_omission_is_complete_but_failed(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    rulebook["accepted"] = []
    judgments["rulebook_sha256"] = content_digest(rulebook)
    judgments["claim_judgments"] = []
    for unit in judgments["unit_judgments"]:
        unit.update(status="missing", claim_ids=[], rationale="The empty output omits this source meaning.")
    report = evaluate(rulebook, labels, judgments)
    assert report["review_complete"] is True
    assert report["status"] == "failed"
    assert report["coverage"]["missing"] == 2


def test_no_review_is_unknown_even_with_exact_correct_quotes(reviewed_output):
    rulebook, labels, _ = reviewed_output
    report = evaluate(rulebook, labels)
    assert report["status"] == "needs_review"
    assert report["coverage"]["covered"] == 0
    assert report["coverage"]["unknown"] == 2
    assert report["dimensions"]["summary"]["unknown"] == 2
    assert report["dimensions"]["summary"]["reviewed_correct_fraction"]["value"] is None


@pytest.mark.parametrize("field,replacement", [
    ("summary", "Every applicant must pay a $5,000 fee before receiving a passport."),
    ("actor", "The commercial photographer"),
])
def test_summary_and_actor_corruptions_invalidate_previous_pass(reviewed_output, field, replacement):
    rulebook, labels, judgments = reviewed_output
    assert evaluate(rulebook, labels, judgments)["status"] == "passed"
    for claim in rulebook["accepted"]:
        claim[field] = replacement
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "needs_review"
    assert report["dimensions"][field]["correct"] == 0
    assert report["dimensions"][field]["unknown"] == 2
    assert report["coverage"]["covered"] == 0
    assert sum(issue["code"] == "stale_claim_judgment" for issue in report["issues"]) == 2


@pytest.mark.parametrize("dimension", MEANING_DIMENSIONS)
def test_explicit_semantic_errors_are_reported_separately(reviewed_output, dimension):
    rulebook, labels, judgments = reviewed_output
    review = judgments["claim_judgments"][0]
    review["dimensions"][dimension] = "error"
    review["rationale"] = f"Source review identifies a deliberately introduced {dimension} error."
    judgments["unit_judgments"][0]["status"] = "partial"
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "failed"
    assert report["dimensions"][dimension]["error"] == 1
    assert report["dimensions"][dimension]["error_examples"][0]["claim_id"] == "claim-1"
    assert report["coverage"]["partial"] == 1


@pytest.mark.parametrize("field,replacement", [
    ("summary", "The applicant must pay a $5,000 passport processing fee."),
    ("actor", "Commercial photographers"),
])
def test_corrupt_output_with_fresh_negative_source_review_fails(reviewed_output, field, replacement):
    rulebook, labels, judgments = reviewed_output
    claim = rulebook["accepted"][0]
    claim[field] = replacement
    judgments["rulebook_sha256"] = content_digest(rulebook)
    review = judgments["claim_judgments"][0]
    review["claim_sha256"] = claim_digest(claim)
    review["dimensions"][field] = "error"
    review["dimensions"]["support"] = "error"
    review["rationale"] = "The source assigns suspension to passport specialists and contains no fee duty or commercial-photographer duty. The original exact quote does not support this changed claim."
    judgments["unit_judgments"][0]["status"] = "partial"
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "failed"
    assert report["dimensions"][field]["error"] == 1
    assert report["dimensions"]["support"]["error"] == 1


def test_invented_extra_claim_cannot_be_hidden_by_perfect_expected_coverage(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    extra = {"id": "invented-extra", "summary": "Applicants must buy a premium subscription.",
             "actor": "Applicants", "quote": rulebook["accepted"][0]["quote"]}
    rulebook["accepted"].append(extra)
    judgments["rulebook_sha256"] = content_digest(rulebook)
    report = evaluate(rulebook, labels, judgments)
    assert report["coverage"]["covered"] == 2
    assert report["status"] == "needs_review"
    assert report["dimensions"]["support"]["unknown"] == 1
    judgments["claim_judgments"].append({
        "claim_id": extra["id"], "claim_sha256": claim_digest(extra), "unit_ids": [],
        "dimensions": {dimension: "error" if dimension in {"summary", "support"} else "unknown" for dimension in MEANING_DIMENSIONS},
        "rationale": "The selected source imposes no subscription requirement; the exact quote is unrelated to the asserted duty.",
        "source_spans": labels["expected_units"][0]["source_spans"],
    })
    assert evaluate(rulebook, labels, judgments)["status"] == "failed"


def test_explicit_omission_and_unjudged_unit_are_distinct(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    omitted = rulebook["accepted"].pop()
    judgments["rulebook_sha256"] = content_digest(rulebook)
    judgments["claim_judgments"] = [entry for entry in judgments["claim_judgments"] if entry["claim_id"] != omitted["id"]]
    missing = judgments["unit_judgments"].pop()
    report = evaluate(rulebook, labels, judgments)
    assert report["coverage"]["unknown"] == 1
    assert report["coverage"]["missing"] == 0
    missing.update(status="missing", claim_ids=[], rationale="Review of all emitted claims finds no applicant re-execution duty.")
    judgments["unit_judgments"].append(missing)
    report = evaluate(rulebook, labels, judgments)
    assert report["coverage"]["missing"] == 1
    assert report["status"] == "failed"


def test_claim_id_alone_cannot_carry_a_pass(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    judgments["claim_judgments"][0].pop("claim_sha256")
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "needs_review"
    assert report["coverage"]["covered"] == 1


def test_missing_dimension_never_defaults_to_correct(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    judgments["claim_judgments"][0]["dimensions"].pop("actor")
    report = evaluate(rulebook, labels, judgments)
    assert report["dimensions"]["actor"]["unknown"] == 1
    assert report["status"] == "needs_review"
    assert report["coverage"]["covered"] == 1


def test_error_or_unknown_claim_cannot_prove_full_unit_coverage(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    judgments["claim_judgments"][0]["dimensions"]["summary"] = "error"
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "failed"
    assert report["coverage"]["covered"] == 1
    assert report["coverage"]["unknown"] == 1
    assert any(issue["code"] == "inconsistent_coverage_judgment" for issue in report["issues"])


def test_labels_changed_after_review_invalidates_assessment(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    labels["expected_units"][0]["meaning"] = "A different reviewed interpretation."
    report = evaluate(rulebook, labels, judgments)
    assert report["status"] == "needs_review"
    assert report["coverage"]["covered"] == 0


def test_empty_labels_cannot_claim_perfect_coverage(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    labels["expected_units"] = []
    with pytest.raises(ValueError, match="empty expected-unit"):
        evaluate(rulebook, labels, judgments)


def test_wrong_source_offsets_are_not_repaired(reviewed_output):
    _, labels, _ = reviewed_output
    labels["expected_units"][0]["source_spans"][0]["start"] += 1
    with pytest.raises(ValueError, match="pinned span"):
        validate_expected(labels)


def test_reviewer_origin_and_exact_source_review_are_required(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    judgments["review_provenance"]["method"] = "keyword_overlap"
    with pytest.raises(ValueError, match="source_review"):
        evaluate(rulebook, labels, judgments)


def test_not_applicable_cannot_bypass_summary_or_support(reviewed_output):
    rulebook, labels, judgments = reviewed_output
    judgments["claim_judgments"][0]["dimensions"]["summary"] = "not_applicable"
    with pytest.raises(ValueError, match="every claim"):
        evaluate(rulebook, labels, judgments)


def test_repeatability_report_distinguishes_material_changes_and_duplicate_counts(reviewed_output):
    rulebook, _, _ = reviewed_output
    second = deepcopy(rulebook)
    second["accepted"][0]["id"] = "fresh-run-new-revision-id"
    assert compare_runs(rulebook, second)["first_only"] == []
    second["accepted"].append(deepcopy(second["accepted"][0]))
    assert len(compare_runs(rulebook, second)["occurrence_count_changes"]) == 1
    second["accepted"][1]["actor"] = "Commercial photographers"
    report = compare_runs(rulebook, second)
    assert len(report["first_only"]) == len(report["second_only"]) == 1


def test_corpus_is_pinned_and_preparation_is_replayable_without_network():
    spec = importlib.util.spec_from_file_location("rulespec_corpus_builder", EVALUATION / "build_corpus.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    manifest = builder.build(allow_download=False)
    assert len(manifest["excerpts"]) == 12
    assert Counter(excerpt["split"] for excerpt in manifest["excerpts"]) == {"development": 6, "holdout": 6}
    for excerpt in manifest["excerpts"]:
        source = next(source for source in manifest["sources"] if source["id"] == excerpt["source_id"])
        text = (EVALUATION / "corpus" / source["text_path"]).read_text()
        selected = (EVALUATION / "corpus" / excerpt["text_path"]).read_text()
        assert selected == text[excerpt["source_start"]:excerpt["source_end"]]
        assert sha256(selected.encode()).hexdigest() == excerpt["sha256"]
        assert "\ufffd" not in selected


def test_development_labels_preserve_agent_authorship_and_exact_source_spans():
    labels = json.loads((EVALUATION / "development-labels.json").read_text())
    _, units = validate_expected(labels)
    assert len(units) == 32
    assert labels["label_provenance"]["reviewer_kind"] == "aiAgent"


def test_select_expected_units_for_input_scope_keeps_context_and_changes_digest():
    labels = json.loads((EVALUATION / "development-labels.json").read_text())
    selected = subset_expected(labels, ["fam-photos-06"])
    assert len(selected["expected_units"]) == 5
    assert {unit["excerpt_id"] for unit in selected["expected_units"]} == {"fam-photos-06"}
    assert selected["sources"] == labels["sources"]
    assert content_digest(selected) != content_digest(labels)
    assert selected["selection"]["parent_labels_sha256"] == content_digest(labels)
    assert len(labels["expected_units"]) == 32
    assert evaluate({"accepted": []}, selected)["coverage"]["unknown"] == 5


@pytest.mark.parametrize("selection", [[], ["not-in-corpus"], ["fam-photos-06", "fam-photos-06"]])
def test_invalid_input_scope_selection_is_rejected(selection):
    labels = json.loads((EVALUATION / "development-labels.json").read_text())
    with pytest.raises(ValueError):
        subset_expected(labels, selection)


def test_holdout_seal_verifies_bytes_without_reading_labels():
    seal = json.loads((EVALUATION / "holdout-seal.json").read_text())
    assert sha256((EVALUATION / seal["labels_path"]).read_bytes()).hexdigest() == seal["labels_sha256"]
