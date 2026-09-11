"""Offline probe of the existing public DocSpec catalog reader. No installs."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback

from docspec.domain.references import SourceCatalogRef
from docspec.source_catalog import LocalSourceCatalogStore, SourceCatalogArtifactReader
from rulespec_artifacts import Producer


HERE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
CATALOG = Path(
    "/Users/mikewolfd/Work/corpora/supply-2026-09-02/catalogs/catalog-B-slice/catalog"
)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    if any((HERE / name).exists() for name in ("admission.json", "inventory.json", "first-row.json")):
        raise SystemExit("Capture exists; pass a fresh output directory to preserve it.")
    HERE.mkdir(parents=True, exist_ok=True)
    receipt_bytes = (CATALOG / "source-catalog-build-command-receipt.json").read_bytes()
    receipt = json.loads(receipt_bytes)
    report = {
        "catalog_root": str(CATALOG),
        "reference": receipt["catalog"],
        "accepted_historical_producer": receipt["producer"],
        "command_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "runtime": sys.executable,
        "docspec_head": subprocess.check_output(
            ["git", "-C", "/Users/mikewolfd/Work/DocSpec", "rev-parse", "HEAD"], text=True
        ).strip(),
        "operations": [],
    }
    try:
        reference = SourceCatalogRef.from_dict(receipt["catalog"])
        reader = SourceCatalogArtifactReader(
            LocalSourceCatalogStore(CATALOG, create=False),
            producer=Producer.from_dict(receipt["producer"], path="selected producer"),
        )
        summary = reader.verify_snapshot(reference)
        report["operations"].append({"verify_snapshot": "pass", "item_count": summary.item_count})
        located = list(reader.open_snapshot(reference).located_items)
        report["operations"].append({"open_snapshot_full_consumption": "pass", "item_count": len(located)})
        report["partition_blobs"] = sorted({row.blob_ref for row in located})
        inventory = []
        for row in located:
            item = row.item.to_dict()
            inventory.append({
                key: value for key, value in item.items()
                if key in {"sourceItemId", "documentId", "sourceIssuedVersion", "normalizedMetadata", "candidateRenditions", "selection"}
            } | {"partition_blob": row.blob_ref})
        save("inventory.json", inventory)
        # A diagnostic example is not an outcome-selected comparison case.
        save("first-row.json", located[0].item.to_dict())
        report["status"] = "pass"
    except Exception as error:
        report.update(status="refused", error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc())
    report["runtime_modules"] = {
        name: {"path": module.__file__, "sha256": hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()}
        for name, module in sorted(sys.modules.items())
        if name.startswith(("docspec", "rulespec_artifacts"))
        and getattr(module, "__file__", None) and module.__file__.endswith(".py")
    }
    save("admission.json", report)
    print(json.dumps({key: value for key, value in report.items() if key != "runtime_modules"}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
