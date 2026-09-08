"""Run inside a fresh installed-wheel environment outside the checkout."""
import json
from pathlib import Path
import shutil
import tempfile

from rulespec_extrapolator import core, extraction, schemas
from rulespec_extrapolator.documents import prepare_document

assert shutil.which("cue") is None and shutil.which("go") is None
package = Path(core.__file__).parent
assert "site-packages" in str(package)
assert core.data_root() == package / "_data"
model_schema = extraction.provider_schema().to_provider_config()["response_json_schema"]
document = prepare_document("Visitors must wear badges.")
candidate = {"kind": "requirement", "summary": document["text"], "quote": document["text"],
             "actor": "Visitors", "actor_quote": "Visitors", "action": "wear", "action_quote": "wear",
             "object": "badges", "object_quote": "badges"}
book = core.compile_candidates(document, [candidate], {"id": "urn:test:wheel-run", "model": "offline-fixture"})
assert len(book["accepted"]) == 1 and not book["rejected"]
assert extraction._check_graph(book["graph"])["status"] == "passed"
sources = extraction._runtime_sources()
assert set(schemas.runtime_sources()) <= set(sources)
assert all(path.is_file() for path in sources.values())
with tempfile.TemporaryDirectory() as directory:
    fingerprints = extraction._freeze(Path(directory), extraction.invented_examples(), model_schema)
    for name in schemas.runtime_sources():
        assert (Path(directory) / "frozen/sources" / name).is_file()
print(json.dumps({"status": "passed", "provider_calls": 0, "installed_package": str(package),
                  "go_and_cue_available": False, "candidate_compilation": "passed", "core_validation": "passed",
                  "schema_inputs_frozen": len(schemas.runtime_sources()),
                  "provider_schema_sha256": fingerprints["provider_schema_sha256"],
                  "runtime": extraction._runtime_versions()}))
