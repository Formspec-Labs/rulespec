"""Adversarial checks concern semantic mismatches that lexical validation misses."""
import pytest

from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document


def compile_one(text, **fields):
    candidate = {"kind": "statement", "modality": "not_stated", "quote": text,
                 "summary": text, "actor": "", **fields}
    return candidate, compile_candidates(prepare_document(text), [candidate], {"id": "urn:test:support"})


@pytest.mark.parametrize("text,name,quote,attribution,admitted", [
    ("The Office states: File within one year.", "The Office", "The Office states:", "claimantNamedInSource", True),
    ("The Office is criticized for delays.", "The Office", "The Office is criticized for delays.", "claimantNamedInSource", False),
    ("The Office does not state this rule.", "The Office", "The Office does not state this rule.", "claimantNamedInSource", False),
    ("See 8 FAM 403.1-4(C).", "Department of State", "8 FAM 403.1-4", "claimantIsDocumentIssuer", False),
    ("The Office states: File within one year.", "Invented Office", "The Office states:", "claimantNamedInSource", False),
    ("Issued by The Office. File within one year.", "The Office", "Issued by The Office.", "claimantIsDocumentIssuer", False),
    ("The Office states: File within one year.", "The Office", "The Office states:", "claimantImpliedBySource", False),
])
def test_attribution_needs_more_than_a_unique_quote(text, name, quote, attribution, admitted):
    item = {"text": name, "quote": quote, "attribution": "rkaf:" + attribution}
    original, book = compile_one(text, claimants=[item])
    assert not book["rejected"]
    assert book["accepted"][0]["claimants"] == original["claimants"]
    nodes = [n for n in book["graph"]["@graph"] if n["@type"] == "rkaf:SourceClaimant"]
    assert bool(nodes) == admitted
    assert any(i["field"] == "claimants:0" for i in book["accepted"][0]["issues"]) != admitted


@pytest.mark.parametrize("quote,unit,anchor,value,admitted", [
    ("within one year after notice", "year", "after notice", "P1Y", True),
    ("within one year after notice", "year", "after notice", "P2Y", False),
    ("within one year after notice", "year", "after notice", "P365D", False),
    ("within one year after notice", "year", "after notice", "invalid", False),
    ("within one year after notice", "year", "before notice", "P1Y", False),
    ("within one year after notice", "days", "after notice", "P1Y", False),
    ("within six months of applying", "months", "applying", "P6M", True),
    ("within 30 days after notice", "days", "after notice", "P30D", True),
    ("within twenty one years after notice", "years", "after notice", "P1Y", False),
    ("within 1.5 years after notice", "years", "after notice", "P5Y", False),
    ("within one year and two months after notice", "months", "after notice", "P2M", False),
    ("within one to two years after notice", "years", "after notice", "P2Y", False),
])
def test_duration_must_match_source_without_guessing_conversions(quote, unit, anchor, value, admitted):
    text = "Applicants file " + quote + "."
    item = {"name": "filing window", "quote": quote, "value": value, "datatype": "xsd:duration",
            "comparator": "within", "unit": unit, "anchor": anchor}
    original, book = compile_one(text, typed_values=[item])
    assert not book["rejected"]
    assert book["accepted"][0]["typed_values"] == original["typed_values"]
    literals = [n.get("rkaf:assertsValue") for n in book["graph"]["@graph"]]
    assert ({"@value": value, "@type": "xsd:duration"} in literals) == admitted
    assert any(i["field"] == "typed_values:0" for i in book["accepted"][0]["issues"]) != admitted
