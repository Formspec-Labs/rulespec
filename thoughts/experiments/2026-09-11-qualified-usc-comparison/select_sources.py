"""Select source paragraphs before running readers; adapt the CFR experiment."""
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
CORPUS = HERE.parents[3] / "RefSpec/output/ecfr-title-xml-2026-08-24"
manifest = json.loads((CORPUS / "manifest.json").read_text())
source = next(row for row in manifest["titles"] if row["title"] == 5)
path = CORPUS / source["path"]
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == source["sha256"]
patterns = {
    "note": re.compile(r"\b\d+\s+U\.?S\.?C\.?.{0,35}\bnote\b", re.I),
    "chapter": re.compile(r"\b\d+\s+U\.?S\.?C\.?.{0,10}\bch(?:apter)?\.?\s*\d", re.I),
    "subsection": re.compile(r"\b\d+\s+U\.?S\.?C\.?\s*\d+\([a-zA-Z0-9]+\)"),
}
selected = {}
for _, section in ET.iterparse(path, events=("end",)):
    if section.get("TYPE") != "SECTION":
        continue
    for paragraph in section.iter("P"):
        text = "".join(paragraph.itertext())
        if len(text) > 1400:
            continue
        for name, pattern in patterns.items():
            if name in selected or not pattern.search(text):
                continue
            number = section.get("N")
            start = re.search(rb'<DIV8\b[^>]*\bN="' + re.escape(number.encode()) + rb'"[^>]*>', raw).start()
            end = raw.index(b"</DIV8>", start) + len(b"</DIV8>")
            capture = f"title-5-section-{number}.xml"
            if not (HERE / capture).exists():
                (HERE / capture).write_bytes(raw[start:end])
            selected[name] = {
                "id": f"publisher-{name}", "raw": text,
                "origin": "first matching pinned eCFR title 5 paragraph, before parser outputs",
                "source": source, "section": number,
                "section_capture": capture, "xml_start": start, "xml_end": end,
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            }
    section.clear()
    if len(selected) == len(patterns):
        break
result = {"paragraphs": list(selected.values()),
          "absent_categories": sorted(set(patterns) - set(selected))}
with (HERE / "selected-sources.json").open("x") as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
    stream.write("\n")
for row in result["paragraphs"]:
    print(row["id"], row["section"], row["raw"], sep="\n")
print("Absent categories:", result["absent_categories"])
