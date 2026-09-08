"""Integrator probes; these are separate from the blind agents' findings."""
from pathlib import Path
import json

from rulespec_extrapolator.core import compile_candidates, validate_graph
from rulespec_extrapolator.documents import prepare_document


def overlapping_section_identity():
    text = "Header.\nVisitors must wear badges."
    sections = [
        {"id": "whole-document", "label": "Whole document", "start": 0, "end": len(text)},
        {"id": "specific-paragraph", "label": "Paragraph 1", "start": 8, "end": len(text)},
    ]
    document = prepare_document(text, sections=sections)
    candidate = {"kind": "requirement", "summary": "Visitors must wear badges.",
                 "actor": "Visitors", "actor_quote": "Visitors",
                 "quote": "Visitors must wear badges.", "section_id": "specific-paragraph"}
    book = compile_candidates(document, [candidate], {"id": "urn:adversarial:section-overlap"})
    claim = book["accepted"][0]
    reversed_document = prepare_document(text, sections=list(reversed(sections)))
    reversed_book = compile_candidates(reversed_document, [candidate], {"id": "urn:adversarial:section-overlap"})
    assert claim["section_id"] == "whole-document"
    assert reversed_book["accepted"][0]["section_id"] == "specific-paragraph"
    return {"scenario": "A valid explicit child-section assignment overlaps a parent section.",
            "expected_section_id": candidate["section_id"], "actual_section_id": claim["section_id"],
            "actual_section_id_with_sections_reversed": reversed_book["accepted"][0]["section_id"],
            "accepted": len(book["accepted"]), "rejected": len(book["rejected"]),
            "issues": claim["issues"], "core_validation": validate_graph(book["graph"]),
            "meaning": "The compiler silently replaces the explicit valid paragraph ID with the first containing section."}


if __name__ == "__main__":
    result = {"reviewer": "Integrator; not blind", "probes": [overlapping_section_identity()]}
    Path(__file__).with_name("integrator-probes.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
