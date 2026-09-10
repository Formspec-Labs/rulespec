"""Load packaged schemas generated from the CUE application profile."""
import hashlib
import json
from pathlib import Path

SCHEMA_DATA = Path(__file__).with_name("schema_data")
PROFILE_SOURCES = ("document-understanding.cue", "cue.mod/module.cue")
SCHEMA_FILES = {name: name + ".schema.json" for name in ("candidate", "meaning", "provider", "inventory", "enrichment")}


def load_schema(name: str) -> dict:
    if name not in SCHEMA_FILES:
        raise ValueError(f"Unknown extraction schema: {name}")
    manifest = json.loads((SCHEMA_DATA / "manifest.json").read_text(encoding="utf-8"))
    content = {}
    for key, names in (("profile_sources_sha256", PROFILE_SOURCES),
                       ("outputs_sha256", SCHEMA_FILES.values())):
        for source in names:
            content[source] = (SCHEMA_DATA / source).read_bytes()
            if hashlib.sha256(content[source]).hexdigest() != manifest[key][source]:
                raise RuntimeError(f"Extraction schema input differs from its build manifest: {source}")
    return json.loads(content[SCHEMA_FILES[name]])


def runtime_sources() -> dict[str, Path]:
    names = (*SCHEMA_FILES.values(), "manifest.json", *PROFILE_SOURCES)
    return {"application/schema_data/" + name: SCHEMA_DATA / name for name in names}


UNIT_SCHEMA = load_schema("provider")["properties"]["extractions"]["items"]
PROVIDER_FIELDS = UNIT_SCHEMA["properties"]["unit_attributes"]["properties"]
# Full Core/refinement fields are independent of what one provider pass selects.
UNIT_FIELDS = load_schema("meaning")["properties"]
TEXT_FIELDS = tuple(name for name, field in UNIT_FIELDS.items() if field["type"] == "string")
LIST_FIELDS = tuple(name for name, field in UNIT_FIELDS.items() if field["type"] == "array")
