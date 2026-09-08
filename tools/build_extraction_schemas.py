#!/usr/bin/env python3
"""Generate the extraction profile with pinned upstream CUE, without runtime Go."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data"
GENERATOR = ROOT / "tools/cue_schema_export"


def serialized(value):
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def inline_references(schema, definitions, seen=()):
    """Inline local references; refuse recursion or constraint-bearing siblings."""
    if isinstance(schema, list):
        return [inline_references(x, definitions, seen) for x in schema]
    if not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/") or ref in seen:
            raise ValueError(f"Unsupported model-schema reference: {ref}")
        key = ref.removeprefix("#/$defs/").replace("~1", "/").replace("~0", "~")
        if key not in definitions:
            raise ValueError(f"Missing model-schema definition: {ref}")
        siblings = {k: v for k, v in schema.items() if k != "$ref"}
        if set(siblings) - {"title", "description"}:
            raise ValueError(f"Constraint-bearing reference siblings require explicit support: {ref}")
        result = inline_references(definitions[key], definitions, (*seen, ref))
        if not isinstance(result, dict):
            raise ValueError(f"A model-schema reference must resolve to an object: {ref}")
        return {**result, **siblings}
    return {k: inline_references(v, definitions, seen) for k, v in schema.items()}


def model_schema(native, metadata):
    """Restore presentation metadata without rewriting native constraints."""
    source = {k: v for k, v in native.items() if k not in {"$schema", "$defs"}}
    source = inline_references(source, native.get("$defs", {}))

    def visit(schema, meta):
        result = dict(schema)
        if meta.get("title"):
            result["title"] = meta["title"]
        if "enum" in result and all(isinstance(x, str) for x in result["enum"]):
            # A string-only enum already implies this type. Gemini's existing
            # schema spells it explicitly; preserve that equivalent spelling.
            if "type" in result and result["type"] != "string":
                raise ValueError("String enum conflicts with the generated type")
            result["type"] = "string"
        if meta.get("sortEnum"):
            if "enum" not in result or not all(isinstance(x, str) for x in result["enum"]):
                raise ValueError("@sortEnum requires a string enum")
            result["enum"] = sorted(result["enum"])
        if "properties" in result:
            order = meta.get("order", [])
            if len(order) != len(set(order)) or set(order) != set(result["properties"]):
                raise ValueError("Native object fields differ from CUE metadata")
            result["properties"] = {name: visit(result["properties"][name], meta["properties"][name]) for name in order}
            if "required" in result:
                if set(result["required"]) - set(order):
                    raise ValueError("A native required field is missing from its object")
                result["required"] = [name for name in order if name in result["required"]]
        if "items" in result:
            if not isinstance(result["items"], dict) or "items" not in meta:
                raise ValueError("Only homogeneous model-schema lists are supported")
            result["items"] = visit(result["items"], meta["items"])
        # Preserve the evaluated request's keyword order as well as field order.
        if result.get("type") == "object":
            order = ("type", "properties", "required", "additionalProperties", "title", "description")
        elif result.get("type") == "array":
            order = ("type", "items", "description", "title")
        elif meta.get("sortEnum"):
            order = ("type", "enum", "description", "title")
        else:
            order = ("type", "description", "enum", "title")
        return {**{key: result[key] for key in order if key in result},
                **{key: value for key, value in result.items() if key not in order}}

    return visit(source, metadata)


def generate():
    with tempfile.TemporaryDirectory(prefix="rulespec-cue-schema-") as temporary:
        binary = Path(temporary) / "cue-schema-export"
        subprocess.run(["go", "build", "-mod=readonly", "-trimpath", "-o", str(binary), "."],
                       cwd=GENERATOR, check=True, capture_output=True, text=True)
        # Native CUE imports the existing Core package. Stage an isolated module
        # so the repository needs neither duplicated definitions nor a second
        # module layout in its authoritative Core directory.
        module = Path(temporary) / "profile"
        shutil.copytree(SOURCE, module)
        shutil.copytree(ROOT / "constraints/core", module / "cue.mod/pkg/rulespec.invalid/core")
        exports = {}
        for definition in ("Candidate", "ExtractionResponse"):
            result = subprocess.run([str(binary), "-definition", "#" + definition, str(module)],
                                    cwd=SOURCE, check=True, capture_output=True, text=True)
            exports[definition] = json.loads(result.stdout)
    provider = exports["ExtractionResponse"]
    if set(provider["source_files"]) != {str(module / "document-understanding.cue")}:
        raise ValueError("The application schema package contains unrecorded CUE files")
    candidate = exports["Candidate"]["schema"]
    candidate_order = exports["Candidate"]["metadata"]["order"]
    if set(candidate_order) != set(candidate["properties"]):
        raise ValueError("Native candidate fields differ from CUE metadata")
    candidate["properties"] = {name: candidate["properties"][name] for name in candidate_order}
    candidate["required"] = [name for name in candidate_order if name in candidate["required"]]
    files = {"candidate.schema.json": serialized(candidate),
             "provider.schema.json": serialized(model_schema(provider["schema"], provider["metadata"]))}
    inputs = [SOURCE / "document-understanding.cue", SOURCE / "cue.mod/module.cue", Path(__file__),
              GENERATOR / "main.go", GENERATOR / "go.mod", GENERATOR / "go.sum",
              *sorted((ROOT / "constraints/core").glob("*.cue"))]
    manifest = {
        "format": "rulespec-native-extraction-schema/1",
        "generator": "cuelang.org/go/encoding/jsonschema",
        **provider["generator"],
        "profile_sources_sha256": {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
                                   for name in ("document-understanding.cue", "cue.mod/module.cue")},
        "sources_sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "outputs_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items()},
    }
    files["manifest.json"] = serialized(manifest)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="fail if generated files differ")
    ap.add_argument("--output", type=Path, default=SOURCE, help="write an isolated trial before adopting generated files")
    args = ap.parse_args()
    try:
        files = generate()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.stderr or str(error)) from None
    if args.check:
        drift = [name for name, content in files.items() if not (args.output / name).is_file() or (args.output / name).read_text() != content]
        if drift:
            raise SystemExit("Extraction schema generation drift: " + ", ".join(drift))
        print("Extraction schemas match native CUE generation.")
        return
    args.output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (args.output / name).write_text(content, encoding="utf-8")
    print(f"Generated {len(files)} extraction schema files in {args.output}")


if __name__ == "__main__":
    main()
