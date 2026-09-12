"""Check the installed SpicyDocs provider after auxiliary catalog retirement.

This probe replaces the old profile-lookup experiment for current candidates.
It makes no publisher requests and preserves the earlier script/results.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.metadata
import json
import socket
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import spicy_docs
from spicy_docs import source_native_profiles
from spicy_docs.sources.federal_register import body_sources


def inspect_provider(wheel: Path) -> dict:
    package = Path(spicy_docs.__file__).resolve().parent
    if "site-packages" not in package.parts:
        raise ValueError("probe requires an installed wheel outside a source checkout")
    with ZipFile(wheel) as archive:
        members = [name for name in archive.namelist() if name.startswith("spicy_docs/") and not name.endswith("/")]
        if not members:
            raise ValueError("candidate wheel contains no SpicyDocs package")
        for name in members:
            if (package.parent / name).read_bytes() != archive.read(name):
                raise ValueError(f"installed member differs from candidate wheel: {name}")
    descriptions = {
        name: {
            "name": profile.name,
            "sourceSystemId": profile.source_system_id,
            "sourceStateScope": profile.source_state_scope,
        }
        for name in source_native_profiles.__all__
        if name.endswith("_PROFILE")
        for profile in [getattr(source_native_profiles, name)]
    }
    if any("cfr" in name.casefold() or "cfr" in row["name"].casefold() for name, row in descriptions.items()):
        raise ValueError("new CFR profile requires reviewing this experiment's conclusions")
    result = {
        "packageVersion": importlib.metadata.version("spicy-docs"),
        "wheelSha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "installedPackage": str(package),
        "verifiedPackageMembers": len(members),
        "sourceProfiles": descriptions,
        "cfrReleaseAdapter": "not supplied by these public native profiles",
        "spicyRegsCfrReference": {
            "declaration": "src/spicy_regs/data_dictionary.py:cfr_sections",
            "producer": "src/spicy_regs/transforms/build_cfr_sections.py",
            "scope": "section metadata and citations only; no section bodies",
            "remoteAvailabilityTested": False,
        },
        "modules": {
            module.__name__: {
                "path": module.__file__,
                "sha256": hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
            }
            for module in (source_native_profiles, body_sources)
        },
    }
    with patch.object(
        socket.socket, "connect", side_effect=AssertionError("offline probe attempted a connection")
    ) as connect:
        try:
            body_sources.body_source_locators(
                {
                    "document_number": "390.5",
                    "publication_date": "2026-08-19",
                    "body_html_url": "https://www.ecfr.gov/api/versioner/v1/full/2026-08-19/title-49.xml",
                }
            )
        except body_sources.FederalRegisterBodySourceError as error:
            result["ecfrOnFederalRegisterApi"] = {"type": type(error).__name__, "message": str(error)}
        else:
            raise AssertionError("Federal Register-only locator accepted an eCFR document")
        result["constructedFederalRegisterLocator"] = dataclasses.asdict(
            body_sources.body_source_locators(
                {
                    "document_number": "2026-12345",
                    "publication_date": "2026-08-19",
                    "body_html_url": "https://www.federalregister.gov/documents/full_text/html/2026/08/19/2026-12345.html",
                }
            )
        )
        result["networkCalls"] = connect.call_count
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--provider-revision", required=True)
    parser.add_argument("--spicy-regs-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = inspect_provider(args.wheel)
    result["providerRevision"] = args.provider_revision
    result["spicyRegsCfrReference"]["inspectedRevision"] = args.spicy_regs_revision
    with args.output.open("x") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({"output": str(args.output), "wheelSha256": result["wheelSha256"], "networkCalls": 0}))


if __name__ == "__main__":
    main()
