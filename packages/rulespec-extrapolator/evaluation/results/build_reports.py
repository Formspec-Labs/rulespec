#!/usr/bin/env python3
"""Expand explicitly authored source reviews and reproduce the frozen reports.

This is bookkeeping, not a semantic grader. Every claim and coverage verdict
comes from source-review-decisions.json, authored after reading frozen output.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from rulespec_extrapolator.evaluation import (
    DIMENSIONS, claim_digest, compare_runs, content_digest, evaluate, subset_expected,
)

ROOT = Path(__file__).resolve().parents[4]
EVALUATION = ROOT / "packages/rulespec-extrapolator/evaluation"
RESULTS = EVALUATION / "results"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"A saved source review changed: {path}. Create a new assessment revision.")
    else:
        with path.open("xb") as stream:
            stream.write(raw)


def unit_id(short: str) -> str:
    excerpt, unit = short.split(".")
    return f"fam-names-{excerpt}-u{unit}"


def reviewed_spans(expected: dict, unit_ids: list[str]) -> list[dict]:
    units = {unit["id"]: unit for unit in expected["expected_units"]}
    selected = {}
    for key in unit_ids:
        for span in units[key]["source_spans"]:
            selected.setdefault(content_digest(span), span)
    return list(selected.values())


def build() -> dict:
    authored = load(RESULTS / "source-review-decisions.json")
    receipt = load(RESULTS / "unseal-receipt.json")
    session = load(RESULTS / "review-session.json")
    seal = load(EVALUATION / "holdout-seal.json")
    label_path = EVALUATION / seal["labels_path"]
    assert sha256(label_path.read_bytes()).hexdigest() == seal["labels_sha256"]
    labels = load(label_path)
    frozen = {entry["name"]: entry for entry in receipt["verified_runs"]}
    rulebooks, reports = {}, {}
    for name, decisions in authored["runs"].items():
        pin = frozen[name]
        rulebook_path = ROOT / pin["rulebook_path"]
        assert sha256(rulebook_path.read_bytes()).hexdigest() == pin["rulebook_sha256"]
        rulebook = load(rulebook_path)
        assert sha256(rulebook["document"]["text"].encode("utf-8")).hexdigest() == pin["source_sha256"]
        expected = subset_expected(labels, decisions["excerpt_ids"])
        claims = rulebook["accepted"]
        assert {row[0] for row in decisions["claims"]} == set(range(1, len(claims) + 1))
        assert len(decisions["claims"]) == len(claims)
        assert set(authored["dimension_order"]) == set(DIMENSIONS)
        judgments = {
            "schema_version": "rulespec-evaluation-judgments/1",
            "review_provenance": {
                "reviewer": authored["reviewer"], "reviewer_kind": authored["reviewer_kind"],
                "method": authored["method"],
                "review_started_at": session["started_at"],
                "review_completed_at": session["completed_at"],
                "authorship_limit": authored["authorship_limit"],
                "same_agent_authored_labels": True,
                "decision_artifact_sha256": sha256((RESULTS / "source-review-decisions.json").read_bytes()).hexdigest(),
                "frozen_rulebook_path": pin["rulebook_path"],
                "frozen_rulebook_file_sha256": pin["rulebook_sha256"],
                "unseal_receipt_sha256": sha256((RESULTS / "unseal-receipt.json").read_bytes()).hexdigest(),
            },
            "rulebook_sha256": content_digest(rulebook),
            "labels_sha256": content_digest(expected),
            "claim_judgments": [], "unit_judgments": [],
        }
        for number, selected, codes, rationale in decisions["claims"]:
            assert len(codes) == len(DIMENSIONS)
            claim = claims[number - 1]
            unit_ids = [unit_id(value) for value in selected]
            judgments["claim_judgments"].append({
                "claim_id": claim["id"], "claim_sha256": claim_digest(claim),
                "unit_ids": unit_ids,
                "dimensions": {dimension: authored["verdict_codes"][code]
                               for dimension, code in zip(authored["dimension_order"], codes)},
                "rationale": rationale, "source_spans": reviewed_spans(expected, unit_ids),
            })
        assert {unit_id(row[0]) for row in decisions["units"]} == {
            unit["id"] for unit in expected["expected_units"]
        }
        for short, status, numbers, rationale in decisions["units"]:
            key = unit_id(short)
            judgments["unit_judgments"].append({
                "unit_id": key, "status": status,
                "claim_ids": [claims[number - 1]["id"] for number in numbers],
                "rationale": rationale, "source_spans": reviewed_spans(expected, [key]),
            })
        report = evaluate(rulebook, expected, judgments)
        assert not report["issues"], report["issues"]
        assert report["counts"]["reviewed_claims"] == len(claims)
        write(RESULTS / f"{name}.expected.json", expected)
        write(RESULTS / f"{name}.judgments.json", judgments)
        write(RESULTS / f"{name}.report.json", report)
        rulebooks[name], reports[name] = rulebook, report
    for prefix in ("holdout", "section"):
        write(RESULTS / f"{prefix}.repeatability.json",
              compare_runs(rulebooks[f"{prefix}-01"], rulebooks[f"{prefix}-02"]))
    summary = {
        "schema_version": "rulespec-frozen-source-review-summary/1",
        "review_provenance": {"reviewer": authored["reviewer"], "reviewer_kind": "aiAgent",
                              "method": "source_review", "completed_at": session["completed_at"],
                              "limit": authored["authorship_limit"]},
        "runs": {},
    }
    for name, report in reports.items():
        book = rulebooks[name]
        summary["runs"][name] = {
            "status": report["status"], "review_complete": report["review_complete"],
            "accepted_claims": len(book["accepted"]), "expected_units": report["counts"]["expected_units"],
            "coverage": {key: report["coverage"][key] for key in ("covered", "partial", "missing", "unknown")},
            "dimensions": {dimension: {key: value[key] for key in ("correct", "error", "unknown", "not_applicable")}
                           for dimension, value in report["dimensions"].items()},
            "processing": {
                "run_status": book["run"].get("status"),
                "processing_status": book["run"].get("processing_status"),
                "rejected_count": len(book["rejected"]),
                "unresolved_references": len(book["unresolved"]),
                "provider_refusal_count": book["run"].get("refusal_count"),
                "window_outcomes": [{"id": window["id"], "status": window["status"],
                                     "candidate_count": window.get("candidate_count")}
                                    for window in book["run"].get("windows", [])],
            },
        }
    write(RESULTS / "summary.json", summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
