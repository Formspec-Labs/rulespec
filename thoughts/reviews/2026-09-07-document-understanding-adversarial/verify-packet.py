"""Check review copies, source inventory seals, and released output hashes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


REPORT = Path(__file__).resolve().parent
REPO = REPORT.parents[2]
PACKET = REPO / ".tools/blind-review-20260907"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((REPORT / "packet-manifest.json").read_text())
failures = []
counts = {"packet_files": 0, "unchanged_original_files": 0, "derived_claim_views": 0,
          "released_files": 0, "sealed_inventories": 0}
for entry in manifest["files"]:
    copied = PACKET / entry["packet"]
    if digest(copied) != entry["sha256"]:
        failures.append({"check": "packet_hash", "path": entry["packet"]})
    counts["packet_files"] += 1
    original = REPO / entry["source"]
    if not entry.get("derived"):
        if digest(original) != entry["sha256"]:
            failures.append({"check": "original_changed", "path": entry["source"]})
        counts["unchanged_original_files"] += 1
    elif copied.name == "claims.json":
        book = json.loads(original.read_text())
        view = json.loads(copied.read_text())
        if view != {key: book[key] for key in ("accepted", "rejected", "unresolved")}:
            failures.append({"check": "derived_claims_changed", "path": entry["packet"]})
        counts["derived_claim_views"] += 1

inventories = []
for name in ("photos", "names"):
    receipt = json.loads((REPORT / f"{name}-output-release.json").read_text())
    inventory = REPORT / receipt["inventory"]
    actual = digest(inventory)
    if actual != receipt["inventory_sha256"]:
        failures.append({"check": "inventory_seal", "path": inventory.name})
    counts["sealed_inventories"] += 1
    inventories.append({"path": inventory.name, "sha256": actual,
                        "output_released_at": receipt["output_released_at"]})
    for path, expected in receipt["files"].items():
        if digest(Path(receipt["output_directory"]) / path) != expected:
            failures.append({"check": "released_output_hash", "path": f"{name}/{path}"})
        counts["released_files"] += 1

result = {"verified_at": datetime.now(timezone.utc).isoformat(),
          "status": "passed" if not failures else "failed", "counts": counts,
          "inventories": inventories, "failures": failures,
          "limits": "Hashes establish unchanged supplied artifacts, not a filesystem access boundary or independent semantic truth."}
(REPORT / "packet-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
raise SystemExit(bool(failures))
