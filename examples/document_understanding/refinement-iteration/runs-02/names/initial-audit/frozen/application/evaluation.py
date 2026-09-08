"""Account for source-reviewed semantic judgments without inventing a score.

This module verifies the identity, source references, and completeness of an
assessment. It cannot decide whether natural-language claims are true. A source
reviewer supplies those judgments; absent or stale judgments remain unknown.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from typing import Any

from rulespec_projection.evidence import resolve_exact_evidence_offsets
from rulespec_projection.provenance import canonical_json

DIMENSIONS = ("summary", "actor", "support", "scope", "links", "boundary")
MEANING_DIMENSIONS = DIMENSIONS + ("modality", "action", "object", "alternatives", "thresholds")
VERDICTS = {"correct", "error", "unknown", "not_applicable"}
COVERAGE = {"covered", "partial", "missing", "unknown"}
LABEL_VERSION = "rulespec-evaluation-labels/1"
JUDGMENT_VERSION = "rulespec-evaluation-judgments/1"


def content_digest(value: Any) -> str:
    """Bind a review to exact JSON content using existing canonicalization."""
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def claim_digest(claim: dict) -> str:
    """Include every reviewed component, evidence reference, and revision ID."""
    return content_digest(claim)


def _index(records: list, field: str, description: str) -> dict[str, dict]:
    if not isinstance(records, list):
        raise ValueError(f"{description} must be a list")
    result = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get(field), str) or not record[field]:
            raise ValueError(f"Each {description} record needs a nonempty {field}")
        key = record[field]
        if key in result:
            raise ValueError(f"Duplicate {description} ID: {key}")
        result[key] = record
    return result


def _provenance(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field} is required")
    if value.get("reviewer_kind") not in {"aiAgent", "humanUser"}:
        raise ValueError(f"{field}.reviewer_kind must identify an agent or human")
    if not isinstance(value.get("reviewer"), str) or not value["reviewer"].strip():
        raise ValueError(f"{field}.reviewer is required")
    if value.get("method") != "source_review":
        raise ValueError(f"{field}.method must be source_review")


def _spans(spans: Any, sources: dict, description: str) -> None:
    if not isinstance(spans, list) or not spans:
        raise ValueError(f"{description} needs source spans reviewed for this judgment")
    for span in spans:
        if not isinstance(span, dict) or span.get("source_id") not in sources:
            raise ValueError(f"Unknown source in {description}")
        quote, start, end = span.get("quote"), span.get("start"), span.get("end")
        if not isinstance(quote, str) or type(start) is not int or type(end) is not int:
            raise ValueError(f"Invalid source coordinates in {description}")
        text = sources[span["source_id"]]["text"]
        resolved = resolve_exact_evidence_offsets(text, quote, start, end)
        # Evaluation labels pin coordinates. Unlike candidate preparation, this
        # check may not repair offsets: changed labels require another review.
        if resolved is None or (resolved.start, resolved.end) != (start, end):
            raise ValueError(f"Source text does not match pinned span in {description}")


def validate_expected(expected: dict) -> tuple[dict, dict]:
    """Validate source pins and label records, without endorsing their meaning."""
    if expected.get("schema_version") != LABEL_VERSION:
        raise ValueError(f"Expected {LABEL_VERSION}")
    _provenance(expected.get("label_provenance"), "label_provenance")
    sources = _index(expected.get("sources", []), "id", "source")
    for source in sources.values():
        if not isinstance(source.get("text"), str):
            raise ValueError("Each labeled source needs exact text")
        if sha256(source["text"].encode("utf-8")).hexdigest() != source.get("sha256"):
            raise ValueError(f"Labeled source digest mismatch: {source['id']}")
    units = _index(expected.get("expected_units", []), "id", "expected unit")
    if not units:
        raise ValueError("An empty expected-unit set cannot establish coverage")
    for unit in units.values():
        if not isinstance(unit.get("meaning"), str) or not unit["meaning"].strip():
            raise ValueError(f"Expected unit {unit['id']} needs a reviewed meaning")
        _spans(unit.get("source_spans"), sources, f"expected unit {unit['id']}")
    return sources, units


def subset_expected(expected: dict, excerpt_ids: list[str]) -> dict:
    """Select coverage targets explicitly while retaining pinned source context.

    Use this only after the holdout output freeze when selecting held-out
    labels. The returned selection has its own digest; judgments for another
    input scope cannot silently transfer to it. Context sources do not become
    additional expected units.
    """
    _, units = validate_expected(expected)
    if not isinstance(excerpt_ids, list) or not excerpt_ids or any(
        not isinstance(value, str) or not value for value in excerpt_ids
    ) or len(set(excerpt_ids)) != len(excerpt_ids):
        raise ValueError("Select one or more distinct excerpt IDs")
    available = {unit.get("excerpt_id") for unit in units.values()}
    unknown = set(excerpt_ids) - available
    if unknown:
        raise ValueError(f"Unknown excerpt selection: {', '.join(sorted(unknown))}")
    selected = deepcopy(expected)
    selected["expected_units"] = [unit for unit in selected["expected_units"]
                                  if unit["excerpt_id"] in excerpt_ids]
    selected["selection"] = {
        "excerpt_ids": sorted(excerpt_ids),
        "parent_labels_sha256": content_digest(expected),
        "coverage_scope": "Only these excerpts contribute expected units; other pinned text is context.",
    }
    return selected


def _fraction(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator,
            "value": numerator / denominator if denominator else None}


def evaluate(rulebook: dict, expected: dict, judgments: dict | None = None) -> dict:
    """Return separate semantic and coverage counts from explicit source review.

    ``expected`` contains agent- or human-authored source labels. ``judgments``
    binds every reviewed claim and expected unit to the exact rulebook and label
    digests. Reviewers must assess all accepted claims, including extra claims.
    Missing judgments, stale reviews, and unreviewed units never count as passes.
    Malformed input raises ``ValueError``; incomplete review produces a report.
    """
    sources, units = validate_expected(expected)
    required_dimensions = MEANING_DIMENSIONS if rulebook.get("schema_version") == "document-understanding/2" else DIMENSIONS
    claims = _index(rulebook.get("accepted", []), "id", "accepted claim")
    issues: list[dict] = []
    claim_reviews: dict[str, dict] = {}
    unit_reviews: dict[str, dict] = {}
    assessment_current = False
    provenance = None
    if judgments is not None:
        if judgments.get("schema_version") != JUDGMENT_VERSION:
            raise ValueError(f"Expected {JUDGMENT_VERSION}")
        _provenance(judgments.get("review_provenance"), "review_provenance")
        provenance = judgments["review_provenance"]
        claim_reviews = _index(judgments.get("claim_judgments", []), "claim_id", "claim judgment")
        unit_reviews = _index(judgments.get("unit_judgments", []), "unit_id", "unit judgment")
        assessment_current = True
        for field, actual in (("rulebook_sha256", content_digest(rulebook)),
                              ("labels_sha256", content_digest(expected))):
            if judgments.get(field) != actual:
                assessment_current = False
                issues.append({"code": "stale_assessment", "field": field,
                               "message": "Review does not bind the current input; all results remain unknown."})
        for claim_id in claim_reviews.keys() - claims.keys():
            issues.append({"code": "absent_reviewed_claim", "claim_id": claim_id})
        for unit_id in unit_reviews.keys() - units.keys():
            issues.append({"code": "unknown_reviewed_unit", "unit_id": unit_id})

    claim_results = []
    for claim_id, claim in claims.items():
        review = claim_reviews.get(claim_id)
        result = {"claim_id": claim_id, "claim_sha256": claim_digest(claim),
                  "status": "unjudged", "unit_ids": [],
                  "dimensions": {dimension: "unknown" for dimension in required_dimensions}}
        if review is not None:
            if review.get("claim_sha256") != claim_digest(claim):
                issues.append({"code": "stale_claim_judgment", "claim_id": claim_id,
                               "message": "Claim content changed after source review."})
                result["status"] = "stale"
            elif assessment_current:
                dimensions = review.get("dimensions", {})
                if not isinstance(dimensions, dict) or set(dimensions) - set(required_dimensions):
                    raise ValueError(f"Unknown judgment dimensions for {claim_id}")
                for dimension, verdict in dimensions.items():
                    if verdict not in VERDICTS:
                        raise ValueError(f"Invalid {dimension} verdict for {claim_id}")
                    if verdict == "not_applicable" and dimension in {"summary", "support", "boundary"}:
                        raise ValueError(f"{dimension} must be assessed for every claim")
                unit_ids = review.get("unit_ids", [])
                if not isinstance(unit_ids, list) or len(set(unit_ids)) != len(unit_ids):
                    raise ValueError(f"Invalid unit_ids for {claim_id}")
                if set(unit_ids) - units.keys():
                    raise ValueError(f"Unknown expected unit in claim judgment {claim_id}")
                if not isinstance(review.get("rationale"), str) or not review["rationale"].strip():
                    raise ValueError(f"Source review needs a rationale for {claim_id}")
                _spans(review.get("source_spans"), sources, f"claim judgment {claim_id}")
                result.update(status="reviewed", unit_ids=unit_ids,
                              dimensions={dimension: dimensions.get(dimension, "unknown") for dimension in required_dimensions},
                              rationale=review["rationale"], source_spans=review["source_spans"])
            else:
                result["status"] = "stale"
        claim_results.append(result)
    claim_by_id = {result["claim_id"]: result for result in claim_results}

    unit_results = []
    for unit_id, unit in units.items():
        result = {"unit_id": unit_id, "excerpt_id": unit.get("excerpt_id"),
                  "status": "unknown", "claim_ids": []}
        review = unit_reviews.get(unit_id)
        if review is not None and assessment_current:
            status = review.get("status")
            if status not in COVERAGE:
                raise ValueError(f"Invalid coverage judgment for {unit_id}")
            claim_ids = review.get("claim_ids", [])
            if not isinstance(claim_ids, list) or len(set(claim_ids)) != len(claim_ids):
                raise ValueError(f"Invalid claim_ids for {unit_id}")
            if not isinstance(review.get("rationale"), str) or not review["rationale"].strip():
                raise ValueError(f"Coverage review needs a rationale for {unit_id}")
            _spans(review.get("source_spans"), sources, f"coverage judgment {unit_id}")
            linked = [claim_by_id.get(claim_id) for claim_id in claim_ids]
            invalid = any(claim is None or claim["status"] != "reviewed" or unit_id not in claim["unit_ids"] for claim in linked)
            if status in {"covered", "partial"} and not claim_ids:
                invalid = True
            if status == "missing" and claim_ids:
                invalid = True
            # A claim with a failed or unknown semantic dimension cannot prove
            # complete coverage. Explicit partial coverage remains measurable.
            if status == "covered" and any(
                verdict not in {"correct", "not_applicable"}
                for claim in linked if claim is not None
                for verdict in claim["dimensions"].values()
            ):
                invalid = True
            if invalid:
                issues.append({"code": "inconsistent_coverage_judgment", "unit_id": unit_id,
                               "message": "Coverage lacks current, consistent reviewed claim matches."})
            else:
                result.update(status=status, claim_ids=claim_ids,
                              rationale=review["rationale"], source_spans=review["source_spans"])
        unit_results.append(result)

    dimensions = {}
    for dimension in required_dimensions:
        counts = Counter(result["dimensions"][dimension] for result in claim_results)
        correct, errors = counts["correct"], counts["error"]
        dimensions[dimension] = {
            **{verdict: counts[verdict] for verdict in sorted(VERDICTS)},
            "reviewed_correct_fraction": _fraction(correct, correct + errors),
            "reviewed_fraction": _fraction(len(claims) - counts["unknown"], len(claims)),
            "error_examples": [
                {"claim_id": result["claim_id"], "summary": claims[result["claim_id"]].get("summary"),
                 "actor": claims[result["claim_id"]].get("actor"), "rationale": result.get("rationale")}
                for result in claim_results if result["dimensions"][dimension] == "error"
            ],
        }
    coverage_counts = Counter(result["status"] for result in unit_results)
    coverage = {**{status: coverage_counts[status] for status in sorted(COVERAGE)},
                "covered_fraction": _fraction(coverage_counts["covered"], len(units)),
                "missing_examples": [
                    {"unit_id": result["unit_id"], "meaning": units[result["unit_id"]]["meaning"],
                     "status": result["status"], "rationale": result.get("rationale")}
                    for result in unit_results if result["status"] in {"missing", "partial"}
                ]}
    known_error = any(value["error"] for value in dimensions.values()) or coverage["missing"] or coverage["partial"]
    unfinished = bool(issues) or coverage["unknown"] or any(value["unknown"] for value in dimensions.values())
    return {
        "schema_version": "rulespec-evaluation-report/1",
        "assessment_kind": "source-reviewed-judgment-accounting",
        "status": "failed" if known_error else "needs_review" if unfinished else "passed",
        "review_complete": not bool(unfinished),
        "dataset_id": expected.get("dataset_id"), "split": expected.get("split"),
        "rulebook_sha256": content_digest(rulebook), "labels_sha256": content_digest(expected),
        "label_provenance": expected["label_provenance"], "review_provenance": provenance,
        "counts": {"accepted_claims": len(claims), "expected_units": len(units),
                   "reviewed_claims": sum(result["status"] == "reviewed" for result in claim_results),
                   "unjudged_or_stale_claims": sum(result["status"] != "reviewed" for result in claim_results)},
        "dimensions": dimensions, "coverage": coverage, "issues": issues,
        "claim_results": claim_results, "unit_results": unit_results,
        "limitations": [
            "Semantic verdicts are supplied by the named source reviewer; this evaluator does not infer truth from text overlap.",
            "Source span and digest checks establish assessment integrity, not semantic correctness.",
            "Counts describe this bounded labeled set; they are not a general extraction accuracy estimate.",
        ],
    }


def compare_runs(first: dict, second: dict) -> dict:
    """Describe material differences between fresh outputs without scoring them."""
    from .core import MEANING_FIELDS
    fields = ("kind", "summary", "actor", "action", "object", "logic_text",
              "relation", "quote", "applies_to", "references", *MEANING_FIELDS)
    def meanings(rulebook: dict) -> dict[str, dict]:
        result = {}
        for claim in rulebook.get("accepted", []):
            content = {field: claim.get(field) for field in fields}
            key = content_digest(content)
            if key not in result:
                result[key] = {"content": content, "count": 0}
            result[key]["count"] += 1
        return result
    left, right = meanings(first), meanings(second)
    return {
        "schema_version": "rulespec-repeatability-report/1",
        "first_sha256": content_digest(first), "second_sha256": content_digest(second),
        "first_claims": len(first.get("accepted", [])), "second_claims": len(second.get("accepted", [])),
        "shared_material_forms": len(left.keys() & right.keys()),
        "first_only": [left[key] for key in sorted(left.keys() - right.keys())],
        "second_only": [right[key] for key in sorted(right.keys() - left.keys())],
        "occurrence_count_changes": [
            {"content": left[key]["content"], "first_count": left[key]["count"], "second_count": right[key]["count"]}
            for key in sorted(left.keys() & right.keys()) if left[key]["count"] != right[key]["count"]
        ],
        "limitation": "Exact material-field comparison describes differences; paraphrases require source review and this is not semantic equivalence.",
    }
