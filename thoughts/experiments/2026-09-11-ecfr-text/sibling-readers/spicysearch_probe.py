"""Offline direct imports; diagnose representation differences, not performance."""

import hashlib
import json
from pathlib import Path
import socket
from unittest.mock import patch

import spicysearch.derived_topic_passes.court as court
import spicysearch.experiments.body_retrieval_lanes as lanes
import spicysearch.list_of_subjects as subjects

HERE = Path(__file__).resolve().parent
SOURCES = HERE.parents[1] / "2026-09-11-reference-bodies/catalog-probe"
CONTROLS = {
    "paragraphs": "<DIV8><P>First requirement.</P><P>Second requirement.</P></DIV8>",
    "empty-cells": "<DIV8><TABLE><TR><TD></TD><TD>20</TD></TR><TR><TD>A</TD><TD></TD></TR></TABLE></DIV8>",
    "inline-word": "<DIV8><P><E>re</E>quired unless waived.</P></DIV8>",
    "line-break": "<DIV8><P>Manufactured or<BR/>imported before<BR/>November 15, 1993</P></DIV8>",
    "malformed": "<DIV8><P>broken</DIV8>",
    "subjects-positive": "<ROOT><LSTSUB><P>Air pollution control, Reporting and recordkeeping requirements.</P></LSTSUB></ROOT>",
}
READERS = {
    "experiment-html": lanes.strip_html_to_visible_text,
    "court-markup": court.visible_text,
    "list-of-subjects": subjects.extract_blocks_from_xml_body,
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    result = {
        "network_calls": 0,
        "model_calls": 0,
        "purpose": "fixed-input representation diagnosis; no corpus or timing claims",
        "modules": {
            module.__name__: {
                "path": module.__file__,
                "sha256": sha(Path(module.__file__).read_bytes()),
            }
            for module in (court, lanes, subjects)
        },
        "cases": [],
    }
    inputs = {path.stem: path.read_bytes() for path in sorted(SOURCES.glob("*-0.xml"))}
    inputs.update({name: value.encode() for name, value in CONTROLS.items()})
    output_path = HERE / "spicysearch-results.json"
    if output_path.exists():
        raise FileExistsError("Preserve the previous capture before another run")
    with patch.object(socket.socket, "connect", side_effect=RuntimeError("Offline only")):
        for name, raw in inputs.items():
            for arm, reader in READERS.items():
                row = {
                    "input": name,
                    "constructed": name in CONTROLS,
                    "input_sha256": sha(raw),
                    "arm": arm,
                }
                try:
                    value = reader(raw.decode())
                    row["output_type"] = type(value).__name__
                    if isinstance(value, str):
                        filename = f"{name}.{arm}.txt"
                        with (HERE / filename).open("x") as stream:
                            stream.write(value)
                        row.update(output_file=filename, output_sha256=sha(value.encode()))
                    else:
                        row["output"] = value
                except Exception as error:
                    row["error"] = {"type": type(error).__name__, "message": str(error)}
                result["cases"].append(row)
    with output_path.open("x") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(output_path)


if __name__ == "__main__":
    main()
