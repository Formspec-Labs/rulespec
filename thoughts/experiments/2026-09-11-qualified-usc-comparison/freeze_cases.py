"""Freeze revisable written-target labels before observing either reader."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
old = json.loads((HERE.parent / "2026-09-10-broader-parser-comparison/cases.json").read_text())["cases"]
labels = {
    "case-05": "Section 1395w-4 of title 42; one compound section name.",
    "case-06": "Section 552 of title 5, inside prose; surrounding prose is not a token defect.",
    "case-07": "Chapter 5 of title 5; not section 5.",
    "case-08": "Section 3 in the appendix to title 5; not title 5 section 3.",
    "case-09": "The note under title 42 section 1983; not section 1983 itself.",
    "case-23": "Two sections of title 5: 552 and 552a. Second occurrence needs the stated title context.",
    "case-27": "No USC namespace is stated; do not infer one.",
    "case-29": "Damaged 1983affirmed must not be admitted as an intact section token.",
}
rows = [{**row, "expectation": labels[row["id"]]} for row in old if row["id"] in labels]
publisher_labels = {
    "publisher-subsection": "Title 5 section 3105 and title 5 section 5372(b); dates are not USC list members.",
    "publisher-chapter": "Title 5 chapter 81, subchapter I. Preserve subchapter I with its chapter, not as a complete chapter-wide target.",
    "publisher-note": "Title 50 section 403j and the note under title 50 section 402. Public Law 86-36 and other employment categories are surrounding context, not USC section identities.",
}
for row in json.loads((HERE / "selected-sources.json").read_text())["paragraphs"]:
    rows.append({**row, "expectation": publisher_labels[row["id"]]})
constructed = [
    ("pinpoints", "5 U.S.C. 552(a)(1)", "Title 5 section 552, with both attached labels (a)(1)."),
    ("stated-range", "5 U.S.C. 552-553", "Written endpoints 552 and 553, stated range; do not enumerate interior sections."),
    ("abbreviated-range", "19 U.S.C. 1484-86", "Written 1484-86; expanded endpoint 1486 only with the abbreviation basis exposed. Do not treat it as a stated endpoint."),
    ("descending-pair", "5 U.S.C. 553-552", "Keep written 553-552 opaque or explicitly unresolved. Do not reverse or expand it into an increasing range. Section existence is unknown."),
    ("unicode", "⚖ See 42\u00a0U.S.C.\u00a01395w–4(a).", "One compound section 1395w-4 with pinpoint (a), retaining original Unicode spelling and original character positions."),
    ("repeat", "5 U.S.C. 552 applies; see 5 U.S.C. 552 again.", "Two separate occurrences of the same title/section, with their own original positions."),
    ("year", "See 5 U.S.C. 552 (2024).", "Section 552; 2024 is a year, not a subsection or another section."),
    ("chapter-range", "5 U.S.C. chapters 5-7", "Chapters 5 through 7, with written endpoints; not a section range."),
    ("compound-letter-tail", "42 U.S.C. 1395w-114a", "One compound section name 1395w-114a; preserve its entire lettered tail."),
    ("appendix-note", "50 U.S.C. App. 2401 note", "A note under appendix section 2401 of title 50; preserve both appendix and note."),
    ("dotted-damage", "26 USC 1.104-1(c)", "Do not admit section 1 by truncating this regulation-shaped token."),
    ("reserved-title", "53 USC 101", "Reserved title: retain an explicit refusal or no accepted USC reading; not a valid current-title assertion."),
    ("zero-title", "0 USC 1", "Invalid title: no accepted USC identity."),
    ("high-title", "55 USC 1", "Outside the currently defined title range: no accepted USC identity."),
    ("ordinary-numbers", "The report lists 1983, 1987 and 1988, with 552 applications.", "Ordinary prose numbers; no USC namespace is supplied."),
    ("unrelated-list", "Under 5 U.S.C. 552 the agency reports counts, 2020, 2021, and 2022 applications.", "One stated USC reference to section 552; application counts must not become USC list members."),
    ("historical-cfr", "35 CFR 1.1", "Historical CFR title 35 remains lexically possible. No USC reading; check RefSpec CFR separately."),
    ("comma-note", "50 U.S.C. 402, note", "The note under section 402 of title 50, including the comma-qualified note spelling."),
]
for name, raw, expectation in constructed:
    rows.append({"id": name, "raw": raw, "expectation": expectation,
                 "origin": "constructed diagnostic, manually selected"})
assert len(rows) <= 32 and len({row["id"] for row in rows}) == len(rows)
for row in rows:
    digest = hashlib.sha256(row["raw"].encode()).hexdigest()
    assert row.get("text_sha256", digest) == digest
    row["text_sha256"] = digest
with (HERE / "cases.json").open("x") as stream:
    json.dump(rows, stream, indent=2, ensure_ascii=False)
    stream.write("\n")
print(f"Frozen {len(rows)} cases: {len(publisher_labels)} publisher paragraphs; the rest constructed development diagnostics.")
