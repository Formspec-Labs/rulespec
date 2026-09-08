"""Verify audit coverage and field correspondence, without judging meaning."""
from datetime import datetime, timezone
import json
from pathlib import Path


REPORT = Path(__file__).resolve().parent
PACKET = REPORT.parents[2] / ".tools/blind-review-20260907"


def read(path):
    return json.loads(path.read_text())


photos = read(REPORT / "photos-coverage-claim-audit.json")
names = read(REPORT / "names-coverage.json")
photo_inventory = read(REPORT / "photos-source-inventory.json")
name_inventory = read(REPORT / "names-source-inventory.json")
assert {unit["unit_id"] for unit in photos["coverage"]} == {unit["unit_id"] for unit in photo_inventory["units"]}
observed = []
run_audits = [("photos", "development-01", photos["candidate_audit"])]
for run in names["runs"]:
    run_audits.append(("names", run["name"], run["claim_reviews"]))
    expected_ids = set(name_inventory["coverage"][run["input"]]["unit_ids"])
    assert {unit["unit_id"] for unit in run["unit_coverage"]} == expected_ids

for group, run_name, audit in run_audits:
    root = PACKET / group / "outputs" / run_name
    candidates = read(root / "candidates.json")
    claims = read(root / "claims.json")
    document = read(root / "document.json")
    raw_rows = []
    for response_path in sorted(root.glob("attempt-*.response.json")):
        response = read(response_path)
        text = "".join(part.get("text", "") for part in response["candidates"][0]["content"]["parts"])
        raw_rows.extend(json.loads(text)["extractions"])
    assert len(raw_rows) == len(candidates) == len(audit)
    accepted = {claim["id"]: claim for claim in claims["accepted"]}
    assert {entry["claim_id"] for entry in audit if entry.get("claim_id")} == set(accepted)
    indices = [entry["index"] if group == "photos" else entry["candidate_index"] for entry in audit]
    assert sorted(indices) == list(range(len(candidates)))
    for entry, index in zip(audit, indices):
        row = raw_rows[index]
        kind = next(key for key in row if not key.endswith("_attributes"))
        raw_fields = {"kind": kind, "quote": row[kind], **row[kind + "_attributes"]}
        candidate = candidates[index]
        assert all(candidate[key] == value for key, value in raw_fields.items())
        assert document["text"][candidate["start"]:candidate["end"]] == candidate["quote"]
        if entry.get("claim_id"):
            claim = accepted[entry["claim_id"]]
            assert all(claim[key] == value for key, value in candidate.items())
            for evidence in claim["evidence"]:
                assert document["text"][evidence["start"]:evidence["end"]] == evidence["quote"]
    observed.append({"run": run_name, "raw_and_audited_candidates": len(raw_rows),
                     "accepted_claims_audited": len(accepted), "rejected_candidates": len(claims["rejected"]),
                     "raw_fields_preserved": True, "accepted_fields_preserved": True,
                     "quotations_and_evidence_exact": True})

case = read(PACKET / "names/outputs/review-cases.json")
assert {claim["id"] for claim in case["current"]} == {
    entry["claim_id"] for entry in names["review_case"]["current_claim_reviews"]}
assert len(names["review_case"]["correction_assessments"]) == len(case["actions"]) == 3
assert {unit["unit_id"] for unit in names["review_case"]["unit_coverage"]} == set(
    name_inventory["coverage"]["contiguous"]["unit_ids"])
result = {"verified_at": datetime.now(timezone.utc).isoformat(), "status": "passed",
          "runs": observed, "total_accepted_claims_audited": sum(run["accepted_claims_audited"] for run in observed),
          "total_raw_candidates_audited": sum(run["raw_and_audited_candidates"] for run in observed),
          "corrected_current_claims_audited": len(case["current"]),
          "correction_actions_audited": len(case["actions"]),
          "all_scoped_inventory_ids_accounted_for": True,
          "limits": "This verifies accounting, exact quotations, and field preservation; it does not prove semantic judgments correct."}
(REPORT / "audit-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
