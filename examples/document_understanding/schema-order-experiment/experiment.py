"""Controlled, recorded schema experiment; the normal extraction CLI is unchanged."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import random
import re
import shutil
import time

from jsonschema import Draft202012Validator
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import core, extraction as e

ROOT = Path(__file__).resolve().parent
VARIANTS = ("current", "rich", "definitions_first", "references_first")
SAMPLES = ("names", "photos", "names-excerpts")
MODEL = "gemini-3.8-flash"
MAX_OUTPUT = 32768
CASE_SAMPLES = {
    "NREG-01": "names", "NREG-02": "names", "NREG-03": "names", "NREG-11": "names",
    "R01": "photos", "R05": "photos", "R08": "photos", "R09": "photos",
    "R10": "photos", "R15": "photos",
    "NREG-04": "names-excerpts", "NREG-06": "names-excerpts",
    "NREG-07": "names-excerpts", "NREG-09": "names-excerpts",
    "NREG-10": "names-excerpts", "NREG-13": "names-excerpts",
}

# These instructions describe general field semantics, without benchmark answers.
EXTRA = {
    "kind": "Classify the complete meaning, including headings' inherited context. A recommendation remains recommendation; descriptive possibility is statement. Conditions and exceptions are separate qualifications of a baseline; retain the baseline itself. Definitions and useful descriptive explanations also deserve units.",
    "summary": "Make this a self-contained reading of the source. Include every governing parent case, time limit, negation, exception and qualification needed to avoid broadening or narrowing its meaning. A long supporting quote does not compensate for omitted meaning in this field. Keep descriptive and advisory material at its source force.",
    "actor": "Resolve a pronoun only when the source establishes its antecedent. Do not invent a duty bearer for an impersonal requirement, definition or factual statement. Do not substitute a neighboring actor from a different branch.",
    "action": "Represent the action actually attributed to the actor. Distinguish taking an action, being permitted to take it, and an event merely being possible; normative force is recorded in modality.",
    "object": "Identify the semantic object of the action, not merely a nearby quoted noun. A form named in a timing condition is not necessarily what the action changes. Leave uncertain components empty while retaining the complete source meaning.",
    "actor_quote": "Copy a contiguous passage supporting the actor assignment. An inherited actor may be supported in supplied context. Empty actor has empty support; a matching word alone does not establish its semantic role.",
    "action_quote": "Copy source wording that supports this action, preserving its direction and negation. Do not rewrite the quoted passage to match a normalized action label.",
    "object_quote": "Copy source wording supporting the chosen object and its option grouping. Do not convert a contextual form, date or actor into the object simply because those words occur nearby.",
    "logic_text": "Retain the source's complete logical wording when relevant. Do not uppercase a conjunction to imply executable Boolean logic. A list of independent categories need not require simultaneous membership in all categories. Preserve exact comparators, units and reference dates.",
    "relation": "The source decides which baseline a qualification governs. Contextual proximity alone does not. An even-though or despite clause may preserve a duty rather than remove it. The qualification must retain the baseline's scope and the limits of the modification.",
    "modality": "Use should for recommendations, may for permission, possible for descriptive may/might, and not_required only for an explicit absence of duty. not_stated fits factual definitions and qualifications with no independent normative force. An exception to a recommendation does not itself declare absence of a legal duty. Generally is not universally.",
    "modality_quote": "Include qualifiers that establish the force, such as generally or might. A neighboring must cannot supply the force of a separate recommendation or description. A companion condition can have not_stated while its baseline retains must or should.",
    "scope_text": "Combine all governing conditions for this unit, including inherited lead-ins and antecedents outside its main quotation. Preserve alternative branches and timing boundaries. A split child must still describe the complete case in which it applies; do not import conditions from neighboring independent cases.",
    "scope_quotes": "Provide every source passage needed to substantiate scope_text. Parent cases may appear elsewhere in the supplied focus or context. Every item must be contiguous and exact; use separate items for separate passages.",
    "context_quotes": "Use for explanations and background that help interpret this unit without turning them into prerequisites. Useful descriptive or advisory meaning should also be retained as a unit when independently substantive.",
    "choice_text": "Explain the complete choice and its nesting: all required elements, independently sufficient options, one-or-more groups, and alternatives inside an option. Preserve each option's qualifiers. Do not equate a grammatical conjunction in a category description with a requirement that both categories hold.",
    "choice_quote": "Select a contiguous passage that actually supports the grouping; an entire short list can be appropriate. Do not splice disjoint quotations or invent separators inside the quote.",
    "alternative_quotes": "Retain every leaf option, including options nested under a parent category, with its qualifying wording. A grouped faithful rule can contain all options without creating a separate duty for each option. The list's introductory sentence alone is insufficient.",
    "jurisdiction": "Use only territory explicitly provided by source wording. The document title, institution or web address is not evidence for an inferred territorial applicability claim.",
    "jurisdiction_quote": "Quote the supplied source's territorial wording. When there is no explicit territorial scope, leave both jurisdiction fields empty.",
    "applies_to": "Select the actual baseline whose meaning changes, preserving its complete scope. Never target an unrelated rule just because its quotation is exact. Leave remote targets unresolved rather than supplying text absent from the request.",
    "references": "Keep source cross-reference labels even when their content is unavailable. Preserve the topic of each reference in the unit's meaning; a nearby reference is not a license to infer the missing rule.",
}


def ordered_digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def obj(properties, title, description):
    return {"type": "object", "title": title, "description": description,
            "properties": properties, "required": list(properties), "additionalProperties": False}


def string(title, description):
    return {"type": "string", "title": title, "description": description}


def array(items, title, description):
    return {"type": "array", "title": title, "description": description, "items": items}


def schema_for(variant):
    schema = deepcopy(e.provider_schema().to_provider_config()["response_json_schema"])
    if variant == "current":
        return schema
    schema.update(title="Source-grounded document meanings", description=
        "Retain independently useful rules, definitions, recommendations, permissions, exemptions, qualifications and descriptive statements with exact evidence. Empty collections express absent supported content, never proof of completeness.")
    row = schema["properties"]["extractions"]["items"]
    row.update(title="One semantic unit", description=
        "One independently referenceable source meaning. Separate distinct actions when useful, while preserving their inherited scope and connected qualifications. Overlapping main quotations are allowed.")
    row["properties"]["unit"].update(title="Exact main quotation")
    attrs = row["properties"]["unit_attributes"]
    attrs.update(title="Complete unit meaning and component evidence", description=
        "Interpret this unit using only its source and supplied context. Keep evidence, normative force, conditions, alternatives and meaning mutually consistent. Empty values preserve uncertainty rather than inventing missing details.")
    for field, prop in attrs["properties"].items():
        prop.update(title=field.replace("_", " ").capitalize())
        prop["description"] += " " + EXTRA[field]
    if variant == "rich":
        return schema
    attrs["properties"].pop("applies_to")
    attrs["required"].remove("applies_to")
    concept = obj({
        "id": string("Local concept identifier", "Unique label c1, c2, and so on within this response. It identifies a source-grounded concept, entity or role, not a global vocabulary identifier."),
        "label": string("Source-supported concept label", "A meaningful concept, entity or role used by extracted units. Reuse an existing concept for the same meaning; distinguish materially different meanings. Do not inventory every ordinary word."),
        "kind": {"type": "string", "enum": ["concept", "entity", "role"], "description": "Whether the label denotes a general concept, a particular entity, or a role held by a source participant."},
        "source_quotes": array({"type": "string"}, "Exact concept evidence", "One or more exact contiguous supplied source quotations establishing this meaning. A short repeated term is permitted here; never invent a source definition."),
    }, "Source concept", "A local, evidence-backed meaning that extracted units may share. Do not infer cross-document identity or a canonical RefSpec term.")
    row["properties"] = {
        "id": string("Local unit identifier", "Unique label u1, u2, and so on within this response. Different meanings sharing a quotation have different IDs. Relationships refer to these IDs."),
        "unit": row["properties"]["unit"],
        "actor_ref": string("Actor concept reference", "The ID of the concept identifying this unit's responsible actor, or empty when not stated or uncertain. It must agree with actor and actor_quote, not merely name a nearby concept."),
        "object_refs": array({"type": "string"}, "Object concept references", "IDs of concepts that the action concerns, agreeing with object and object_quote. Empty when inapplicable or uncertain. These references do not determine AND/OR grouping."),
        "unit_attributes": attrs,
    }
    row["required"] = list(row["properties"])
    relationship = obj({
        "source_unit_ref": string("Qualifying unit", "ID of a condition or exception unit in extractions. Preserve the independent baseline and qualification meanings as units; do not create a relation by relabeling the baseline."),
        "target_unit_refs": array({"type": "string"}, "Affected baseline units", "IDs of the non-condition, non-exception units whose meaning this qualification changes. Target the rule actually governed, not another obligation in the same passage. Empty if the target cannot be established."),
        "relation": {"type": "string", "enum": ["scope", "prerequisite", "trigger", "exception"], "description": "The qualification's semantic relationship to the baseline, agreeing with the qualifying unit's relation field. Exceptions can qualify recommendations or descriptive generalizations as well as duties."},
        "evidence_quotes": array({"type": "string"}, "Relationship evidence", "Exact source passages supporting the qualification and its connection to these particular targets. Co-occurrence alone is insufficient. Include an antecedent or cross-reference when needed."),
        "explanation": string("Source-supported relationship meaning", "Explain which case qualifies which baseline and how. Preserve limits, modal force and alternatives; an exception does not automatically guarantee a remedy or cancel a separate duty."),
    }, "Explicit qualification", "A source-supported relationship between extracted meanings. An ID's existence does not establish that it is the correct semantic target.")
    unresolved = obj({
        "source_unit_ref": string("Referring unit", "Existing unit ID, or empty if no corresponding unit can be extracted."),
        "reference": string("Unresolved source reference", "An exact source quotation or section label whose target or meaning is not established in the supplied source."),
        "reason": string("Remaining uncertainty", "Why the source does not establish a target or interpretation. Preserve what is known without inventing a local or remote rule."),
    }, "Unresolved reference", "Retain incomplete links visibly instead of guessing. A locally available target should not be called remote merely because its quotation is elsewhere in the same source.")
    properties = {
        "concepts": array(concept, "Shared source concepts", "Concepts, entities and roles referenced by units. Definitions with independent meaning must also appear as extracted units."),
        "extractions": schema["properties"]["extractions"],
        "relationships": array(relationship, "Explicit qualifications between units", "Retain supported conditions and exceptions with their actual baseline targets. Each source qualification unit has at most one relationship row; multiple targets share that row."),
        "unresolved": array(unresolved, "Unresolved source references", "Record unresolved links and their source-specific uncertainty."),
    }
    schema["properties"] = properties
    schema["required"] = list(properties)
    if variant == "references_first":
        schema["properties"] = {k: properties[k] for k in ("relationships", "extractions", "concepts", "unresolved")}
    return schema


def instructions(variant):
    prompt = e.PROMPT
    if variant in ("definitions_first", "references_first"):
        old = "and exception candidates may set a relation or applies_to. applies_to is a list\nof EXACT main-rule quotations, not summaries. An exception uses relation"
        new = "and exception candidates may set a non-none relation. Use relationships to\nconnect their local unit IDs to baseline unit IDs. An exception uses relation"
        assert old in prompt
        prompt = prompt.replace(old, new)
        prompt += "\nUse the schema's local concept and unit IDs consistently across this response. Keep all existing meaning and evidence fields. Put qualification targets in relationships; retain unavailable targets in unresolved and source section labels in references. Local concept IDs are labels for this response, not canonical external identifiers.\n"
    return prompt


def content_text(raw):
    candidates = raw.get("candidates") or []
    if len(candidates) != 1:
        raise ValueError("Expected one provider candidate")
    return "".join(p["text"] for p in candidates[0].get("content", {}).get("parts", [])
                   if not p.get("thought") and isinstance(p.get("text"), str))


def decode(raw, schema):
    text = content_text(raw)
    payload = json.loads(text, object_pairs_hook=e._pairs_without_duplicates,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite number")))
    Draft202012Validator(schema).validate(payload)
    return payload


def normalize(payload, document, window, variant, run):
    """Reuse strict quotation parsing and Core compilation; retain local ID mappings."""
    local = variant in ("definitions_first", "references_first")
    issues, parsed_rows, local_ids, id_map = [], [], [], {}
    concepts, concept_bindings, relations = [], [], []
    rows = payload["extractions"]
    if local:
        concept_ids = [c["id"] for c in payload["concepts"]]
        unit_ids = [row["id"] for row in rows]
        if len(set(concept_ids)) != len(concept_ids) or len(set(unit_ids)) != len(unit_ids):
            raise ValueError("Duplicate local identifier")
        if any(not re.fullmatch(r"c[1-9][0-9]*", c) for c in concept_ids) or any(
                not re.fullmatch(r"u[1-9][0-9]*", u) for u in unit_ids):
            raise ValueError("Invalid local identifier")
        units = {row["id"]: row for row in rows}
        for concept in payload["concepts"]:
            supported = bool(concept["source_quotes"]) and all(q and q in document["text"] for q in concept["source_quotes"])
            if not supported:
                issues.append({"code": "unsupported_concept_evidence", "concept_id": concept["id"]})
            concepts.append({**concept, "evidence_exact": supported,
                "experimental_id": core.NS + "experimental-concept:" + core.digest([document["id"], run["id"], concept])})
        seen_sources = set()
        for relation in payload["relationships"]:
            source = relation["source_unit_ref"]
            targets = relation["target_unit_refs"]
            valid = source in units and source not in seen_sources and units[source]["unit_attributes"]["kind"] in {"condition", "exception"}
            valid = valid and relation["relation"] == units[source]["unit_attributes"]["relation"]
            valid = valid and len(set(targets)) == len(targets) and all(t in units and units[t]["unit_attributes"]["kind"] not in {"condition", "exception"} for t in targets)
            valid = valid and bool(relation["evidence_quotes"]) and all(q and q in document["text"] for q in relation["evidence_quotes"])
            seen_sources.add(source)
            if not valid:
                issues.append({"code": "invalid_qualification_reference", "relationship": relation})
            relations.append({**relation, "structurally_valid": bool(valid)})
        for item in payload["unresolved"]:
            if (item["source_unit_ref"] and item["source_unit_ref"] not in units) or not item["reference"] or item["reference"] not in document["text"]:
                issues.append({"code": "invalid_unresolved_reference", "reference": item})
    for index, row in enumerate(rows):
        unit_id = row["id"] if local else f"row{index}"
        attrs = deepcopy(row["unit_attributes"])
        if local:
            selected = [r for r in relations if r["source_unit_ref"] == unit_id and r["structurally_valid"]]
            attrs["applies_to"] = [units[t]["unit"] for r in selected for t in r["target_unit_refs"]]
            refs = ([row["actor_ref"]] if row["actor_ref"] else []) + row["object_refs"]
            for ref in refs:
                if ref not in concept_ids:
                    issues.append({"code": "missing_concept_reference", "unit_id": unit_id, "concept_id": ref})
            concept_bindings.append({"unit_id": unit_id, "actor_ref": row["actor_ref"], "object_refs": row["object_refs"]})
        parsed = e.parse_response_text(json.dumps({"extractions": [{"unit": row["unit"], "unit_attributes": attrs}]}), document, window)
        issues.extend({"unit_id": unit_id, **refusal} for refusal in parsed["refusals"])
        for candidate in parsed["candidates"]:
            local_ids.append(unit_id)
            parsed_rows.append(candidate)
    book = core.compile_candidates(document, parsed_rows, run)
    rejected_indices = {r["index"] for r in book["rejected"]}
    accepted_inputs = [i for i in range(len(parsed_rows)) if i not in rejected_indices]
    for index, claim in zip(accepted_inputs, book["accepted"], strict=True):
        id_map[local_ids[index]] = claim["id"]
    by_id = {c["id"]: c for c in book["accepted"]}
    if local:
        # Explicit IDs can distinguish different meanings sharing a main quote.
        # Do not fall back to the old quotation resolver for an invalid ID edge.
        for unit_id, claim_id in id_map.items():
            claim = by_id[claim_id]
            if claim["kind"] in {"condition", "exception"}:
                claim["target_ids"] = []
        for relation in relations:
            targets = relation["target_unit_refs"]
            source = relation["source_unit_ref"]
            if relation["structurally_valid"] and source in id_map and all(t in id_map for t in targets):
                by_id[id_map[source]]["target_ids"] = sorted({id_map[t] for t in targets})
                relation["core_source_id"] = id_map[source]
                relation["core_target_ids"] = [id_map[t] for t in targets]
            elif relation["structurally_valid"]:
                issues.append({"code": "reference_to_refused_unit", "source_unit_id": source, "target_unit_ids": targets})
        book["unresolved"] = [r for r in book["unresolved"] if r.get("code") not in {"ambiguous_target", "missing_target"}]
        book["unresolved"].extend({"source_unit_ref": r["source_unit_ref"], "reference": r["reference"], "reason": r["reason"], "code": "explicit_unresolved_reference"} for r in payload["unresolved"])
        book["graph"] = core.build_graph(document, book["accepted"], run)
    mapping = {"unit_ids": id_map, "concepts": concepts, "concept_bindings": concept_bindings,
               "relationships": relations, "issues": issues,
               "boundary": "Concepts are experimental local records; persistent Core rule/evidence records use the existing compiler. Structural checks do not establish semantic correctness."}
    return book, mapping


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, output / "experiment.py")
    sources = ROOT.parent / "refinement-iteration" / "runs-02"
    for sample in SAMPLES:
        e._save(output / "sources" / f"{sample}.json", e._load(sources / sample / "before.json")["document"])
    original = ROOT.parent / "quality-iteration/reference-assessment/reference-cases.json"
    references = e._load(original)
    cases = [{**c, "sample": CASE_SAMPLES[c["case_id"]]} for c in references["cases"] if c["case_id"] in CASE_SAMPLES]
    assert len(cases) == len(CASE_SAMPLES)
    e._save(output / "expectations.json", {"source_sha256": e._digest(original.read_bytes()), "cases": cases,
        "boundary": "Selected pre-existing development cases; reference answers never enter provider prompts."})
    fingerprints = e._freeze(output, e.invented_examples(), schema_for("current"))
    pins = {str(p.relative_to(ROOT.parent)): e._digest(p.read_bytes())
            for directory in (ROOT.parent / "refinement-iteration", ROOT.parent / "quality-iteration")
            for p in directory.rglob("*") if p.is_file()}
    e._save(output / "original-pins.json", pins)
    variants = {}
    for variant in VARIANTS:
        schema = schema_for(variant)
        Draft202012Validator.check_schema(schema)
        e._save(output / "schemas" / f"{variant}.json", schema)
        (output / "schemas" / f"{variant}.prompt.txt").write_text(instructions(variant))
        variants[variant] = {"ordered_schema_sha256": ordered_digest(schema),
            "schema_semantic_sha256": e._digest(schema), "instructions_sha256": e._digest(instructions(variant)),
            "top_level_order": list(schema["properties"])}
    assert e._digest(schema_for("definitions_first")) == e._digest(schema_for("references_first"))
    assert instructions("definitions_first") == instructions("references_first")
    e._save(output / "design.json", {"created_at": e._now(), "model": MODEL, "temperature": 0,
        "max_output_tokens": MAX_OUTPUT, "repeats": 2, "samples": list(SAMPLES), "variants": variants,
        "runtime": fingerprints, "runner_sha256": e._digest(Path(__file__).read_bytes()),
        "boundary": "Extraction only; no audit/repair loops; no default CLI change; known development sources."})


def call(output, variant, key, sample=None, repeat=0):
    probe = sample is None
    directory = output / ("probes" if probe else "runs") / (variant if probe else f"{sample}/{variant}/{repeat:02d}")
    directory.mkdir(parents=True, exist_ok=False)
    schema = e._load(output / "schemas" / f"{variant}.json")
    if probe:
        window = {"index": 0, "id": "empty-schema-probe"}
        prompt = "There is no substantive source content. Return the schema's object with all top-level arrays empty."
    else:
        document = e._load(output / "sources" / f"{sample}.json")
        windows = e.plan_windows(document, max_chars=6000)
        assert len(windows) == 1
        window = windows[0]
        generator = e._prompt_generator(e.invented_examples(), instructions(variant), example_format="semantic-text/1")
        prompt = e._window_prompt(generator, document, window)
    model = e._create_model(MODEL, key, GeminiSchema.from_schema_dict(schema))
    start = time.monotonic()
    attempt = e._record_window(model, prompt, directory, window, key,
                               max_output_tokens=1024 if probe else MAX_OUTPUT, temperature=0)
    e._save(directory / "attempt.json", attempt)
    stats = {"variant": variant, "sample": sample, "repeat": repeat, "seconds": round(time.monotonic()-start, 3),
        "request_status": attempt["status"], "output_schema_valid": False, "ordered_schema_sha256": ordered_digest(schema)}
    if attempt["response_file"]:
        raw = e._load(directory / attempt["response_file"])
        stats.update(usage=raw.get("usage_metadata"), model_version=raw.get("model_version"),
            finish_reasons=[c.get("finish_reason") for c in raw.get("candidates") or []])
        try:
            payload = decode(raw, schema)
            stats.update(output_schema_valid=True, output_order=list(payload),
                output_order_matches_schema=list(payload)==list(schema["properties"]))
            e._save_provider_json(directory / "output.json", payload, key)
            if not probe:
                run = {"id": "schema-order:" + e._digest([sample, variant, repeat, prompt, ordered_digest(schema)]),
                    "model": MODEL, "model_version": raw.get("model_version", MODEL), "temperature": 0,
                    "prompt_sha256": e._digest(prompt), "provider_schema_sha256": ordered_digest(schema)}
                book, mapping = normalize(payload, document, window, variant, run)
                e._save(directory / "rulebook.json", book)
                e._save(directory / "mapping.json", mapping)
                validation = e._check_graph(book["graph"])
                e._save(directory / "validation.json", validation)
                stats.update(accepted=len(book["accepted"]), rejected=len(book["rejected"]),
                    mapping_issue_counts=dict(Counter(i["code"] for i in mapping["issues"])),
                    component_issues=sum(len(c["issues"]) for c in book["accepted"]),
                    link_issues=len(book["unresolved"]), graph_validation=validation["status"],
                    concepts=len(mapping["concepts"]), explicit_links=sum(len(c["target_ids"]) for c in book["accepted"]))
        except Exception as exc:
            stats.update(processing_error=type(exc).__name__)
    e._save(directory / "stats.json", stats)
    print(json.dumps(stats), flush=True)
    return stats


def replay(output):
    checks = []
    for directory in sorted((output / "runs").glob("*/*/*")):
        stats = e._load(directory / "stats.json")
        if not (directory / "rulebook.json").is_file():
            checks.append({"run": str(directory.relative_to(output)), "replayed": False,
                           "reason": "No normalized result; provider/processing failure retained"})
            continue
        sample, variant = stats["sample"], stats["variant"]
        raw = e._load(directory / "attempt-0000.response.json")
        payload = decode(raw, e._load(output / "schemas" / f"{variant}.json"))
        saved = e._load(directory / "rulebook.json")
        document = e._load(output / "sources" / f"{sample}.json")
        book, mapping = normalize(payload, document, e.plan_windows(document)[0], variant, saved["run"])
        assert book == saved and mapping == e._load(directory / "mapping.json")
        checks.append({"run": str(directory.relative_to(output)), "replayed": True})
    originals = e._load(output / "original-pins.json")
    changed = [name for name, digest in originals.items() if e._digest((ROOT.parent / name).read_bytes()) != digest]
    assert not changed
    e._save(output / "verification.json", {"provider_calls": 0, "replays": checks,
        "protected_originals": len(originals), "changed_originals": changed})
    print(json.dumps({"replayed": sum(c["replayed"] for c in checks), "protected_originals": len(originals)}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "probe", "run", "replay"])
    parser.add_argument("--output", type=Path, default=ROOT / "trial-01")
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.output)
    elif args.command == "replay":
        replay(args.output)
    else:
        key = e._credential(args.env_file)
        if args.command == "probe":
            with ThreadPoolExecutor(max_workers=3) as pool:
                futures = [pool.submit(call, args.output, v, key) for v in VARIANTS]
                results = [f.result() for f in as_completed(futures)]
            e._save(args.output / "probe-results.json", results)
        else:
            probes = e._load(args.output / "probe-results.json")
            if not all(p["request_status"] == "response_received" and p["output_schema_valid"] for p in probes):
                raise ValueError("Inspect retained schema-probe failures before running the matrix")
            jobs = [(s, v, n) for n in (1, 2) for s in SAMPLES for v in VARIANTS]
            random.Random(20260907).shuffle(jobs)
            e._save(args.output / "schedule.json", jobs)
            with ThreadPoolExecutor(max_workers=3) as pool:
                futures = [pool.submit(call, args.output, v, key, s, n) for s, v, n in jobs]
                results = [f.result() for f in as_completed(futures)]
            e._save(args.output / "run-results.json", results)


if __name__ == "__main__":
    main()
