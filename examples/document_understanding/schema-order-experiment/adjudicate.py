"""Serialize authored source judgments; this is not an automatic semantic scorer."""
from collections import Counter
from pathlib import Path
import json
import re

from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent
TRIAL = ROOT / "trial-01"
VARIANTS = ("current", "rich", "definitions_first", "references_first")
CASES = {
    "names": ["NREG-01", "NREG-02", "NREG-03", "NREG-11"],
    "photos": ["R01", "R05", "R08", "R09", "R10", "R15"],
    "names-excerpts": ["NREG-04", "NREG-06", "NREG-07", "NREG-09", "NREG-10", "NREG-13"],
}
# Decisions follow the raw/source review recorded in REVIEW-NOTES.md. P/F/U are
# pass/fail/unknown. Unknown receives no passing credit and is not called wrong.
DECISIONS = {
    "names": {"current/01": "FPPF", "current/02": "PPPP", "rich/01": "PPPF", "rich/02": "PPPF",
        "definitions_first/01": "PPPP", "definitions_first/02": "FPPP",
        "references_first/01": "PPPP", "references_first/02": "PFPP"},
    "photos": {"current/01": "FFPFFF", "current/02": "FFPFFF", "rich/01": "FPPFFF", "rich/02": "FUPFFF",
        "definitions_first/01": "FUPFFF", "definitions_first/02": "FUPFFF",
        "references_first/01": "FUPFFF", "references_first/02": "FFPFFF"},
    "names-excerpts": {"current/01": "FPFFFP", "current/02": "FFFFFF", "rich/01": "FPPFPP", "rich/02": "FPPPPP",
        "definitions_first/01": "FPPFPP", "definitions_first/02": "FPPFPP",
        "references_first/01": "FFFPPF", "references_first/02": "FFFPFP"},
}
PASS = {
    "NREG-01": "All six leaf options, one-or-more selection, nested court-order grouping, cited basis and unresolved married-name reference survive without a universal exemption.",
    "NREG-02": "The discretionary limited-validity issuance retains the older-than-one-year DS-11/unchanged-ID parent case and insufficient-time/urgent-or-emergency condition; the suspension duty remains distinct.",
    "NREG-03": "The recent DS-11 name-change exemption and conditional documentation duty both survive with their complete applicant class.",
    "NREG-11": "Both possible identity evidence (including purpose and cited guidance) and generally-needed name-change documentation survive without becoming universal duties.",
    "R05": "Material-damage alternatives, the facial-area boundary and examples survive; immaterial categories are explicitly independently acceptable in the rich/1 reading.",
    "R08": "The applicant's re-execution duty retains no-photo AND acceptance-facility scope, alongside the distinct passport-specialist suspension duty.",
    "NREG-06": "Court finality, separate new-name passport/FS-240 prohibitions and mandatory pending-name clearance despite both qualifications survive.",
    "NREG-07": "Mandatory determination of multipart-name appearance and both conditional should-spacing branches survive, including no-prior-passport and alternative evidence sources.",
    "NREG-09": "A modifier targets the general family-consistency recommendation; the special-issuance sponsor recommendation remains distinct and should stays should.",
    "NREG-10": "Both spacing and suffix generalizations retain generally, the Department-disregard qualification, and unresolved further guidance without guaranteeing a rewrite.",
    "NREG-13": "Applicant includes the citizenship/identity individual and DS-2060; minor retains chapter scope, under-18 age and non-emancipation.",
}


def reason(sample, variant_repeat, case, status):
    if status == "P":
        return PASS[case]
    if status == "U":
        return "Both immaterial-damage categories and acceptance survive, without invented capitalized AND. The choice text still uses and/along with/together with; independent membership remains ambiguous. This is not proof of an erroneous Boolean conjunction, and receives no passing credit."
    if case == "NREG-01":
        return "The complete options appear in raw meaning but a flattened court-order sublist is not an exact contiguous component quote; the parser refuses the requirement."
    if case == "NREG-02":
        return "The raw emergency permission retains complete scope but combines permission kind with exception relation; Core refuses it and the source unit of its edge is invalid."
    if case == "NREG-11":
        return "The possible identity-evidence statement survives, but generally needing name-change documentation to update ID is omitted."
    if case == "R01":
        if variant_repeat == "references_first/02":
            return "The raw infant unit targets the correct eyes recommendation, but permission kind plus exception relation is refused; no accepted infant qualification remains."
        return "Infant/newborn partial-or-complete eye closure survives, but no explicit modifier or unresolved exception relation represents its qualification of the available eyes baseline."
    if case == "R05":
        return "The immaterial categories become a capitalized AND in current/1; current/2 and references-first/2 omit the damage definitions. The full damage-boundary case is not retained."
    if case == "R09":
        return "The four required medical-acceptance child links are absent. Most runs retain their scope in prose; definitions-first/1 additionally loses the statement requirement to a kind/relation conflict, and references-first/2 omits three child meanings."
    if case == "R10":
        if variant_repeat == "references_first/01":
            return "The disability permission u25 is assigned exception relation and targets u23 (endorsement 46) rather than u24 (natural expression); the record/edge is refused."
        if variant_repeat == "references_first/02":
            return "The disability acceptance permission and its qualification are omitted."
        return "The disability-conditioned permission survives, but its modifier relation to the natural-expression baseline is absent."
    if case == "R15":
        return "The certificate-photo timing caution is omitted; retaining other advisory/descriptive material does not recover this meaning."
    if case == "NREG-04":
        mixed = variant_repeat in {"rich/01", "rich/02", "definitions_first/01", "references_first/01"}
        return ("The application-disclosure requirement is combined with exception relation and refused. The court-document qualification is not retained as a valid separate modifier." if mixed else
                "The confidential-former-name qualification of the court-document both-names rule is absent; the neighboring application/evidence clauses do not establish this edge.")
    if case == "NREG-06":
        return "Court-order finality is not retained as an independent constraint. Current/2 also omits the FS-240 prohibition and clearance duty; references-first retains those other clauses but still fails the composite case."
    if case == "NREG-07":
        return "The mandatory determine-appearance unit is omitted. Current runs also omit the should-spacing branches; references-first retains those branches but not the complete case."
    if case == "NREG-09":
        return "The explicit preference exception edge is absent. Rich and definitions-first preserve both recommendations in prose; the current runs omit the family material."
    if case == "NREG-10":
        return "The qualified generally-not-sufficient spacing and suffix rewrite statements are omitted."
    if case == "NREG-13":
        return "The applicant definition is omitted. Current/2 retains the minor definition; references-first/1 omits both definition units."
    raise ValueError((sample, variant_repeat, case, status))


def selected_rows(payload, document, evidence):
    selected = []
    for index, row in enumerate(payload["extractions"]):
        quote = row["unit"]
        matches = list(re.finditer(re.escape(quote), document["text"])) if quote else []
        overlap = any(m.start() < s["end"] and s["start"] < m.end() for m in matches for s in evidence)
        if overlap:
            selected.append(row.get("id", f"row{index}"))
    return selected


def estimate(usage):
    # Official standard paid-tier prices, verified 2026-09-07, effective through
    # 2026-12-31. This is reported API usage, not a billing invoice.
    prompt = usage.get("prompt_token_count") or 0
    cached = usage.get("cached_content_token_count") or 0
    output = (usage.get("candidates_token_count") or 0) + (usage.get("thoughts_token_count") or 0)
    return ((prompt - cached) * .75 + cached * .075 + output * 3.75) / 1_000_000


def main():
    output = TRIAL / "assessment"
    output.mkdir(exist_ok=True)
    refs = {c["case_id"]: c for c in e._load(TRIAL / "expectations.json")["cases"]}
    judgments = []
    for sample, runs in DECISIONS.items():
        document = e._load(TRIAL / "sources" / f"{sample}.json")
        for variant_repeat, decisions in runs.items():
            assert len(decisions) == len(CASES[sample])
            directory = TRIAL / "runs" / sample / variant_repeat
            payload = e._load(directory / "output.json")
            mapping = e._load(directory / "mapping.json")
            for case, decision in zip(CASES[sample], decisions, strict=True):
                evidence = refs[case]["source_evidence"]
                assert all(document["text"][s["start"]:s["end"]] == s.get("exact_text", s.get("text")) for s in evidence)
                inspected = selected_rows(payload, document, evidence)
                judgments.append({"case_id": case, "name": refs[case]["name"], "sample": sample,
                    "variant": variant_repeat.split("/")[0], "repeat": int(variant_repeat.split("/")[1]),
                    "status": {"P": "pass", "F": "fail", "U": "unknown"}[decision],
                    "expected_invariants": refs[case]["expected_invariants"], "source_evidence": evidence,
                    "rationale": reason(sample, variant_repeat, case, decision),
                    "source_sha256": document["sha256"], "output_rows_overlapping_source": inspected,
                    "accepted_ids": {k: mapping["unit_ids"][k] for k in inspected if k in mapping["unit_ids"]},
                    "run_path": str(directory.relative_to(TRIAL)),
                    "raw_output_sha256": e._digest((directory / "output.json").read_bytes()),
                    "rulebook_sha256": e._digest((directory / "rulebook.json").read_bytes())})
    assert len(judgments) == 128
    stats = e._load(TRIAL / "run-results.json")
    comparisons = {}
    for variant in VARIANTS:
        runs = [r for r in stats if r["variant"] == variant]
        mappings = [e._load(TRIAL / "runs" / r["sample"] / variant / f"{r['repeat']:02d}" / "mapping.json") for r in runs]
        counts = {str(n): dict(Counter(j["status"] for j in judgments if j["variant"] == variant and j["repeat"] == n)) for n in (1, 2)}
        issues = Counter()
        for run in runs:
            issues.update(run["mapping_issue_counts"])
        comparisons[variant] = {"case_counts_by_repeat": counts, "runs": len(runs),
            "schema_valid_responses": sum(r["output_schema_valid"] for r in runs),
            "output_order_matches": sum(r["output_order_matches_schema"] for r in runs),
            "accepted_records": sum(r["accepted"] for r in runs), "core_rejected_records": sum(r["rejected"] for r in runs),
            "mapping_issue_counts": dict(issues), "accepted_qualification_edges": sum(r["explicit_links"] for r in runs),
            "raw_relationship_records": sum(len(m["relationships"]) for m in mappings),
            "concept_records": sum(len(m["concepts"]) for m in mappings),
            "concept_references": sum(bool(b["actor_ref"]) + len(b["object_refs"]) for m in mappings for b in m["concept_bindings"]),
            "total_seconds_across_requests": sum(r["seconds"] for r in runs),
            "reported_tokens": sum(r["usage"]["total_token_count"] for r in runs),
            "estimated_usd": round(sum(estimate(r["usage"]) for r in runs), 6),
            "estimated_usd_per_document": round(sum(estimate(r["usage"]) for r in runs)/len(runs), 6)}
    probes = e._load(TRIAL / "probe-results.json")
    binding_examples = []
    for run, unit_id, explanation in [
        ("names/definitions_first/02", "u15", "The documentation-submission duty has object name-change documentation, but object_refs points only to Form DS-11. The form is the timing/application context, not the submitted documentation."),
        ("names/definitions_first/02", "u14", "The new-name-ID exemption's object_refs points to material discrepancy and Form DS-11 instead of the identity evidence that its object field names."),
        ("photos/definitions_first/02", "u15", "The returned object is the passport application, but object_refs points to New photograph request, the purpose of returning it."),
        ("photos/definitions_first/02", "u4", "The excluded object is the parent's face, but object_refs points to Infant passport applicant. A related participant is not the excluded face."),
        ("photos/definitions_first/02", "u27", "actor is empty but actor_ref identifies Applicant. The two fields disagree about whether an actor was extracted."),
    ]:
        path = TRIAL / "runs" / run / "output.json"
        payload = e._load(path)
        unit = next(u for u in payload["extractions"] if u["id"] == unit_id)
        refs_used = set(unit["object_refs"] + ([unit["actor_ref"]] if unit["actor_ref"] else []))
        binding_examples.append({"run": run, "unit": unit, "referenced_concepts": [c for c in payload["concepts"] if c["id"] in refs_used],
            "assessment": "semantic_role_mismatch", "explanation": explanation, "raw_output_sha256": e._digest(path.read_bytes())})
    e._save(output / "results.json", {"created_at": e._now(), "actor": "Codex source adjudication", "actor_kind": "aiAgent",
        "reference_status": "project_gold_versioned_and_correctable", "semantic_assessor_provider_calls": 0,
        "boundary": "Sixteen selected known development cases, twice per variant. Composite cases measure retained accepted meaning; component warnings alone do not imply a case failure. Four ambiguous damage readings are unknown. Not overall document accuracy or the multi-pass refinement score.",
        "comparisons": comparisons, "judgments": judgments,
        "concept_binding_review": {"scope": "Targeted counterexample review of two definition-first captures; not an error-rate estimate across all bindings.",
            "finding": "All 343 concept references name existing local concepts, but syntactic identity resolution does not establish semantic role agreement. Some object references behave like broad topical tags.",
            "counterexamples": binding_examples},
        "estimate": {"pricing_source": "https://ai.google.dev/gemini-api/docs/pricing#gemini-3.8-flash",
            "price_verified_on": "2026-09-07", "effective_through": "2026-12-31", "basis": "Provider-reported usage; standard paid tier; not invoice",
            "input_per_million_usd": .75, "cached_input_per_million_usd": .075, "output_including_thinking_per_million_usd": 3.75,
            "probe_usd": round(sum(estimate(p["usage"]) for p in probes), 6),
            "total_usd": round(sum(estimate(r["usage"]) for r in stats+probes), 6)},
        "review_notes_sha256": e._digest((ROOT / "REVIEW-NOTES.md").read_bytes())})
    for variant, row in comparisons.items():
        print(variant, json.dumps(row))


if __name__ == "__main__":
    main()
