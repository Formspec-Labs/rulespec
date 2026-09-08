#!/usr/bin/env python3
"""Transfer source judgments only after proving all interpreted input unchanged.

Strictly replay corrected-compiler outputs without a provider call, retain the
original source reviews, and write separate transfer receipts and reports.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from rulespec_extrapolator.evaluation import (
    claim_digest, content_digest, evaluate, subset_expected,
)
from rulespec_extrapolator.extraction import replay_run

ROOT = Path(__file__).resolve().parents[4]
EVALUATION = ROOT / "packages/rulespec-extrapolator/evaluation"
RESULTS = EVALUATION / "results"
DESTINATION = RESULTS / "reprocessed"
NAMES = ("holdout-01", "holdout-02", "section-01", "section-02")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: dict, verify_only: bool) -> None:
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(f"Existing transfer artifact differs: {path}")
    elif verify_only:
        raise ValueError(f"Missing transfer artifact: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(raw)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def transfer(verify_only: bool = False) -> dict:
    seal = load(EVALUATION / "holdout-seal.json")
    label_path = EVALUATION / seal["labels_path"]
    require(file_digest(label_path) == seal["labels_sha256"], "Sealed labels changed")
    labels = load(label_path)
    unseal = load(RESULTS / "unseal-receipt.json")
    frozen = {entry["name"]: entry for entry in unseal["verified_runs"]}
    checked = []
    # Complete all identity/source checks before creating a transfer artifact.
    for name in NAMES:
        old_path = ROOT / frozen[name]["rulebook_path"]
        new_path = ROOT / f"examples/document_understanding/manual-slice/reprocessed/{name}/rulebook.json"
        require(file_digest(old_path) == frozen[name]["rulebook_sha256"], f"Frozen output changed: {name}")
        old, new = load(old_path), load(new_path)
        expected_path = RESULTS / f"{name}.expected.json"
        judgment_path = RESULTS / f"{name}.judgments.json"
        report_path = RESULTS / f"{name}.report.json"
        expected, judgments, report = load(expected_path), load(judgment_path), load(report_path)
        require(expected == subset_expected(labels, expected["selection"]["excerpt_ids"]), f"Selected labels changed: {name}")
        require(judgments["labels_sha256"] == content_digest(expected), f"Stale original labels binding: {name}")
        require(judgments["rulebook_sha256"] == content_digest(old), f"Stale original review binding: {name}")
        require(evaluate(old, expected, judgments) == report, f"Original assessment no longer reproduces: {name}")
        old_claims = {claim["id"]: claim_digest(claim) for claim in old["accepted"]}
        new_claims = {claim["id"]: claim_digest(claim) for claim in new["accepted"]}
        require(len(old_claims) == len(old["accepted"]) and len(new_claims) == len(new["accepted"]), f"Duplicate accepted IDs: {name}")
        require(old_claims == new_claims and old["accepted"] == new["accepted"], f"An accepted interpretation changed: {name}")
        require(old["document"] == new["document"], f"The source document or its metadata changed: {name}")
        source_sha = sha256(old["document"]["text"].encode("utf-8")).hexdigest()
        require(source_sha == old["document"]["sha256"] == new["document"]["sha256"] == frozen[name]["source_sha256"], f"Source text digest differs: {name}")
        require(old["run"]["id"] == new["run"]["id"], f"Acquisition run identity changed: {name}")
        changed = sorted(key for key in set(old) | set(new) if old.get(key) != new.get(key))
        require(set(changed) <= {"run", "graph"}, f"An unapproved part of the rulebook changed: {name}: {changed}")
        require(new["run"].get("record_kind") == "pipeline_reprocessing", f"Not an explicit reprocessing record: {name}")
        require(new["run"]["reprocessing"]["provider_calls"] == 0, f"Reprocessing records new provider calls: {name}")
        require(all(new["run"]["reprocessing"]["acquisition_matches_current"].values()), f"Acquisition settings differ: {name}")
        checked.append((name, old_path, new_path, old, new, expected_path, expected,
                        judgment_path, judgments, report_path, report, old_claims, changed, source_sha))

    replays = {}
    with TemporaryDirectory(prefix="rulespec-judgment-transfer-") as temporary:
        for name, _, new_path, _, new, *_ in checked:
            replay_output = Path(temporary) / name
            replayed = replay_run(new_path.parent, replay_output)
            require(replayed == new, f"Strict replay changed the rulebook: {name}")
            replays[name] = load(replay_output / "replay.json")
            require(replays[name]["provider_calls"] == 0, f"Replay made provider calls: {name}")

    if not verify_only:
        DESTINATION.mkdir(exist_ok=True)
    manifest = {"schema_version": "rulespec-judgment-transfer-manifest/1", "runs": {}}
    for (name, old_path, new_path, old, new, expected_path, expected, judgment_path,
         judgments, report_path, report, claim_digests, changed, source_sha) in checked:
        receipt_path = DESTINATION / f"{name}.transfer-receipt.json"
        previous_receipt = load(receipt_path) if receipt_path.exists() else None
        replay = replays[name]
        if previous_receipt:
            prior_replay = previous_receipt["strict_replay"]
            require({key: value for key, value in prior_replay.items() if key != "replayed_at"}
                    == {key: value for key, value in replay.items() if key != "replayed_at"},
                    f"Replay evidence changed: {name}")
            replay = prior_replay
        receipt = {
            "schema_version": "rulespec-judgment-transfer/1",
            "transferred_at": previous_receipt["transferred_at"] if previous_receipt else datetime.now(timezone.utc).isoformat(),
            "actor": "Codex evaluation worker /root/evaluation", "actor_kind": "aiAgent",
            "method": "Exact accepted-claim, document, source-text and selected-label equality, followed by provider-free strict replay",
            "semantic_reassessment": False,
            "original_rulebook": {"path": old_path.relative_to(ROOT).as_posix(), "file_sha256": file_digest(old_path), "canonical_sha256": content_digest(old)},
            "reprocessed_rulebook": {"path": new_path.relative_to(ROOT).as_posix(), "file_sha256": file_digest(new_path), "canonical_sha256": content_digest(new)},
            "original_judgments": {"path": judgment_path.relative_to(ROOT).as_posix(), "file_sha256": file_digest(judgment_path)},
            "original_report": {"path": report_path.relative_to(ROOT).as_posix(), "file_sha256": file_digest(report_path)},
            "selected_labels": {"path": expected_path.relative_to(ROOT).as_posix(), "file_sha256": file_digest(expected_path), "canonical_sha256": content_digest(expected), "excerpt_ids": expected["selection"]["excerpt_ids"]},
            "sealed_labels_file_sha256": seal["labels_sha256"],
            "unchanged_document_sha256": content_digest(old["document"]),
            "unchanged_source_text_sha256": source_sha,
            "unchanged_acquisition_run_id": old["run"]["id"],
            "accepted_claim_checks": [{"claim_id": claim_id, "unchanged_claim_sha256": value}
                                      for claim_id, value in claim_digests.items()],
            "unchanged_accepted_array_sha256": content_digest(old["accepted"]),
            "changed_rulebook_fields": changed,
            "strict_replay": replay,
            "scope_limit": "Rebinds the original agent-authored interpretation judgments only. It is not a new model sample, semantic improvement, human approval, or transfer to changed claim/source content.",
        }
        save(receipt_path, receipt, verify_only)
        transferred = deepcopy(judgments)
        transferred["rulebook_sha256"] = content_digest(new)
        transferred["review_provenance"]["judgment_transfer"] = {
            "receipt_path": receipt_path.relative_to(ROOT).as_posix(),
            "receipt_file_sha256": file_digest(receipt_path),
            "transferred_at": receipt["transferred_at"], "semantic_reassessment": False,
            "reprocessed_rulebook_path": new_path.relative_to(ROOT).as_posix(),
        }
        require(transferred["claim_judgments"] == judgments["claim_judgments"] and
                transferred["unit_judgments"] == judgments["unit_judgments"], f"Judgment content changed: {name}")
        new_report = evaluate(new, expected, transferred)
        for field in ("status", "review_complete", "counts", "dimensions", "coverage", "issues", "claim_results", "unit_results"):
            require(new_report[field] == report[field], f"Assessment result changed during transfer: {name}: {field}")
        save(DESTINATION / f"{name}.expected.json", expected, verify_only)
        save(DESTINATION / f"{name}.judgments.json", transferred, verify_only)
        save(DESTINATION / f"{name}.report.json", new_report, verify_only)
        manifest["runs"][name] = {
            "accepted_claims_unchanged": len(claim_digests), "status": new_report["status"],
            "coverage": {key: new_report["coverage"][key] for key in ("covered", "partial", "missing", "unknown")},
            "strict_replay": "verified", "provider_calls": 0,
            "artifacts": {path.name: file_digest(path) for path in (
                receipt_path, DESTINATION / f"{name}.expected.json",
                DESTINATION / f"{name}.judgments.json", DESTINATION / f"{name}.report.json")},
        }
    save(DESTINATION / "transfer-manifest.json", manifest, verify_only)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    options = parser.parse_args()
    print(json.dumps(transfer(options.verify_only), ensure_ascii=False, indent=2))
