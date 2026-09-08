"""Ground application candidates and emit existing immutable Core assertions."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from types import SimpleNamespace

from jsonschema import Draft202012Validator, ValidationError
from rulespec_projection.evidence import resolve_exact_evidence_offsets
from rulespec_projection.projection import verify_fragment
from rulespec_projection.provenance import canonical_json

SCHEMA_VERSION = "document-understanding/1"
NS = "urn:rulespec:document-understanding:"
KINDS = ("requirement", "permission", "prohibition", "authority", "threshold",
         "definition", "condition", "exception")
RELATIONS = ("none", "scope", "prerequisite", "trigger", "exception")
TEXT_FIELDS = ("kind", "summary", "actor", "quote", "action", "object",
               "actor_quote", "action_quote", "object_quote", "logic_text",
               "relation", "section_id", "window_id")
CANDIDATE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "additionalProperties": False,
    "required": ["kind", "summary", "actor", "quote"],
    "properties": {
        **{field: {"type": "string"} for field in TEXT_FIELDS},
        "kind": {"enum": list(KINDS)},
        "summary": {"type": "string", "minLength": 1},
        "quote": {"type": "string", "minLength": 1},
        "relation": {"enum": list(RELATIONS)},
        "start": {"type": ["integer", "null"], "minimum": 0},
        "end": {"type": ["integer", "null"], "minimum": 0},
        "applies_to": {"type": "array", "items": {"type": "string", "minLength": 1}},
        "references": {"type": "array", "items": {"type": "string", "minLength": 1}},
    },
}


def canonical(value):
    return canonical_json(value)


def digest(value):
    if not isinstance(value, (str, bytes)):
        value = canonical(value)
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def data_root():
    packaged = Path(__file__).parent / "_data"
    return packaged if packaged.is_dir() else Path(__file__).resolve().parents[4]


def _issue(code, field, message):
    return {"code": code, "field": field, "message": message}


def _evidence(document, quote, field, start=None, end=None, within=None):
    # A unique match within a verified parent quote can disambiguate repeated words.
    text = document["text"]
    if within and quote:
        lo, hi = within
        local = resolve_exact_evidence_offsets(text[lo:hi], quote, None, None)
        if local:
            start, end = lo + local.start, lo + local.end
    pos = resolve_exact_evidence_offsets(text, quote, start, end)
    if pos is None:
        return None
    if any(part["kind"] != "source" and part["start"] < pos.end and pos.start < part["end"]
           for part in document.get("source_map", [])):
        return None
    artifact = SimpleNamespace(raw_fields={"text": text})
    fragment = verify_fragment(artifact, key=field, source_field="text",
                               start=pos.start, end=pos.end, artifact_iri=document["id"],
                               expected_text=quote)
    return {"field": field, "quote": quote, "start": pos.start, "end": pos.end,
            "fragment_id": fragment.urn}


def _claim(document, candidate, *, rule_id, occurrence_id, origin="aiSuggested"):
    Draft202012Validator(CANDIDATE_SCHEMA).validate(candidate)
    c = {field: "" for field in TEXT_FIELDS}
    c.update({"relation": "none", "applies_to": [], "references": [],
              "start": None, "end": None})
    c.update(deepcopy(candidate))
    main = _evidence(document, c["quote"], "summary", c["start"], c["end"])
    if main is None:
        raise ValueError("Main quotation is absent or ambiguous in the pinned source")
    c.update(start=main["start"], end=main["end"])
    section = next((s for s in document["sections"]
                    if s["start"] <= c["start"] < s["end"]), None)
    if c["section_id"] and not any(s["id"] == c["section_id"] and
        s["start"] <= c["start"] < s["end"] for s in document["sections"]):
        raise ValueError("Candidate section does not contain its source quote")
    c["section_id"] = section["id"] if section else ""
    evidence, issues = [main], []
    if not c["actor"]:
        issues.append(_issue("unknown_actor", "actor", "The actor needs review."))
    for field in ("actor", "action", "object"):
        if not c[field]:
            continue
        support = _evidence(document, c[field + "_quote"], field,
                            within=(main["start"], main["end"]))
        if support:
            evidence.append(support)
        else:
            issues.append(_issue("component_evidence_unresolved", field,
                                 f"Exact supporting text for {field} needs review."))
    if c["logic_text"]:
        support = _evidence(document, c["logic_text"], "logic_text",
                            within=(main["start"], main["end"]))
        if support:
            evidence.append(support)
        issues.append(_issue("logic_requires_review", "logic_text",
                             "Logical grouping, quantities or timing remain uninterpreted."))
    if c["kind"] in ("condition", "exception"):
        if c["relation"] == "none" or not c["applies_to"]:
            issues.append(_issue("qualification_target_missing", "applies_to",
                                 "This qualification needs its affected rule or rules."))
    elif c["relation"] != "none" or c["applies_to"]:
        raise ValueError("Only condition or exception candidates may qualify other rules")
    if c["kind"] == "exception" and c["relation"] != "exception":
        raise ValueError("An exception must use the exception relationship")
    # Application revision identity is not a Core assertion identity.
    semantic = {k: c[k] for k in ("kind", "summary", "actor", "action", "object",
                "logic_text", "relation", "applies_to", "references")}
    c.update(id=NS + "revision:" + digest([rule_id, semantic, evidence]),
             rule_id=rule_id, occurrence_id=occurrence_id, origin=origin,
             evidence=evidence, issues=issues, target_ids=[], assertion_ids=[])
    c["assertion_ids"] = [node["@id"] for node in _component_nodes(c, {})]
    return c


def _value_proposition(subject, predicate, value):
    return {"rkaf:assertsSubject": subject, "rkaf:assertsPredicate": predicate,
            "rkaf:assertsValue": {"@value": value, "@language": "en"},
            "rkaf:assertionPolarity": "rkaf:affirmed"}


def assertion_id(proposition):
    keys = ("rkaf:assertsSubject", "rkaf:assertsPredicate", "rkaf:assertsObject",
            "rkaf:assertsValue", "rkaf:assertionPolarity")
    return NS + "assertion:" + digest({k: proposition[k] for k in keys if k in proposition})


def _component_nodes(claim, disposition):
    for field in ("summary", "actor", "action", "object", "logic_text"):
        if not claim.get(field):
            continue
        predicate = NS + ("states-" + claim["kind"] if field == "summary" else field)
        proposition = _value_proposition(claim["rule_id"], predicate, claim[field])
        yield {"@id": assertion_id(proposition), "@type": "rkaf:ValueAssertion",
               **disposition, **proposition}


def resolve_links(document, claims):
    unresolved = []
    by_quote = {}
    for c in claims:
        if c["kind"] not in ("condition", "exception"):
            by_quote.setdefault(c["quote"], []).append(c)
    for c in claims:
        c["target_ids"] = []
        incomplete = False
        for quote in c["applies_to"]:
            matches = by_quote.get(quote, [])
            if len(matches) == 1:
                c["target_ids"].append(matches[0]["id"])
            else:
                incomplete = True
                unresolved.append({"claim_id": c["id"], "reference": quote,
                    "code": "ambiguous_target" if matches else "missing_target"})
        c["target_ids"] = [] if incomplete else sorted(set(c["target_ids"]))
        c["reference_links"] = []
        for label in c["references"]:
            clean = re.sub(r"\s+", " ", label).strip().casefold()
            matches = [s for s in document["sections"]
                       if clean in {re.sub(r"\s+", " ", s["label"]).strip().casefold(),
                                    s["id"].casefold()}]
            entry = {"text": label, "status": "resolved" if len(matches) == 1 else "unresolved"}
            if len(matches) == 1:
                entry["section_id"] = matches[0]["id"]
            else:
                unresolved.append({"claim_id": c["id"], "reference": label,
                                   "code": "section_reference_unresolved"})
            c["reference_links"].append(entry)
    return unresolved


def compile_candidates(document, candidates, run):
    from .documents import validate_document
    validate_document(document)
    accepted, rejected = [], []
    for index, candidate in enumerate(candidates):
        try:
            if not isinstance(candidate, dict):
                raise ValueError("Candidate must be a JSON object")
            occurrence = NS + "occurrence:" + digest([document["id"], run.get("id", "fixture"),
                                                     index, candidate])
            rule_id = NS + "rule:" + digest([document["id"], run.get("id", "fixture"),
                                            index, candidate.get("quote")])
            accepted.append(_claim(document, candidate, rule_id=rule_id,
                                   occurrence_id=occurrence))
        except (ValueError, TypeError, KeyError, ValidationError) as exc:
            # Retain a malformed model row; downstream validation still fails loudly.
            rejected.append({"index": index, "candidate": candidate, "reason": str(exc)})
    unresolved = resolve_links(document, accepted)
    return {"schema_version": SCHEMA_VERSION, "document": deepcopy(document),
            "run": deepcopy(run), "accepted": accepted, "rejected": rejected,
            "unresolved": unresolved, "graph": build_graph(document, accepted, run)}


def revise_claim(document, original_claim, replacement_fields, event_id, origin="humanAsserted"):
    if origin not in ("humanAsserted", "aiSuggested"):
        raise ValueError("Corrections require an explicit human or AI origin")
    candidate = {k: deepcopy(v) for k, v in original_claim.items()
                 if k in CANDIDATE_SCHEMA["properties"]}
    allowed = set(CANDIDATE_SCHEMA["properties"])
    if set(replacement_fields) - allowed:
        raise ValueError("Correction contains unsupported fields")
    candidate.update(deepcopy(replacement_fields))
    claim = _claim(document, candidate, rule_id=original_claim["rule_id"],
                   occurrence_id=NS + "occurrence:" + digest(event_id), origin=origin)
    claim["id"] = NS + "revision:" + digest([claim["id"], event_id])
    claim["supersedes"] = [original_claim["id"]]
    claim["prior_assertion_ids"] = list(original_claim["assertion_ids"])
    claim["review_event_id"] = event_id
    return claim


def build_graph(document, claims, run, attestations=None):
    nodes = {}
    def add(node):
        # The first creation's origin is immutable when propositions are reused.
        nodes.setdefault(node["@id"], node)
    add({"@id": document["id"], "@type": "rkaf:Artifact",
         "rkaf:hasArtifactIdentifier": document["id"],
         "rkaf:artifactIdentifierScheme": "rkaf:hash-sha256",
         "rkaf:hasContentDigest": "sha256:" + document["sha256"], "dcterms:format": "text/plain"})
    lineage_id = NS + "lineage:" + digest(run)
    add({"@id": lineage_id, "@type": "rkaf:AILineage",
         "rkaf:modelId": run.get("model", "fixture"),
         "rkaf:modelVersion": run.get("model_version", "not-recorded"),
         "rkaf:temperature": 0.0,
         "rkaf:promptTemplateRef": NS + "prompt:" + run.get("prompt_sha256", digest("fixture")),
         "rkaf:inputContextHash": "sha256:" + document["sha256"]})
    activities = {}
    for window in run.get("windows", []):
        if not window.get("request_sha256"):
            continue
        aid = NS + "activity:" + digest([run["id"], window["id"], window["request_sha256"]])
        activities[window["id"]] = aid
        add({"@id": aid, "@type": "rkaf:ExtractionActivity",
             "rkaf:extractionMethod": "rkaf:modelExtraction", "rkaf:extractionRun": run["id"],
             "rkaf:extractedBy": NS + "extractor:langextract", "rkaf:extractorVersion": SCHEMA_VERSION,
             "rkaf:requestContractDigest": "sha256:" + window["request_sha256"],
             "rkaf:extractionModelRef": NS + "model:" + digest(run.get("model")),
             "rkaf:extractionPromptRef": NS + "prompt:" + run.get("prompt_sha256", digest("fixture")),
             "rkaf:inputDigest": ["sha256:" + document["sha256"]],
             "rkaf:hasAILineage": lineage_id})
    for c in claims:
        origin = c.get("origin", "aiSuggested")
        claim_lineage = lineage_id
        if origin == "aiSuggested" and c.get("review_event_id"):
            claim_lineage = NS + "lineage:" + digest(c["review_event_id"])
            add({"@id": claim_lineage, "@type": "rkaf:AILineage",
                 "rkaf:modelId": "review-agent", "rkaf:modelVersion": "not-recorded",
                 "rkaf:temperature": 0.0, "rkaf:promptTemplateRef": c["review_event_id"],
                 "rkaf:inputContextHash": "sha256:" + document["sha256"]})
        disposition = {"rkaf:assertionOrigin": "rkaf:" + origin,
                       "rkaf:epistemicBasis": "rkaf:statisticalInference" if origin == "aiSuggested" else "rkaf:userAssertion",
                       "rkaf:usageEligibility": "rkaf:reviewQueueOnly",
                       "rkaf:consumerLifecycleState": "rkaf:draft"}
        if origin == "aiSuggested":
            disposition["rkaf:hasAILineage"] = claim_lineage
        if not c.get("review_event_id") and c.get("window_id") in activities:
            disposition["rkaf:hasExtractionProvenance"] = activities[c["window_id"]]
        for e in c["evidence"]:
            add({"@id": e["fragment_id"], "@type": "rkaf:SourceFragment",
                 "oa:hasSource": document["id"],
                 "rkaf:fragmentIdentityScheme": "rkaf:carrier-local-fragment",
                 "rkaf:sourceArtifactDigest": "sha256:" + document["sha256"],
                 "rkaf:fragmentContentDigest": "sha256:" + digest(e["quote"]),
                 "rkaf:selectorKind": ["oa:TextQuoteSelector", "oa:TextPositionSelector"],
                 "oa:hasSelector": [{"@type": "oa:TextQuoteSelector", "oa:exact": e["quote"]},
                     {"@type": "oa:TextPositionSelector", "oa:start": e["start"], "oa:end": e["end"],
                      "rkaf:coordinateSystem": "rkaf:unicode-codepoint"}]})
        components = list(_component_nodes(c, disposition))
        c["assertion_ids"] = [n["@id"] for n in components]
        for node in components:
            prior = [p for p in c.get("prior_assertion_ids", [])
                     if p != node["@id"] and p in nodes and
                     nodes[p].get("rkaf:assertsPredicate") == node["rkaf:assertsPredicate"]]
            if prior:
                node["rkaf:supersedesAssertion"] = prior
            add(node)
            field = "summary" if node["rkaf:assertsPredicate"].startswith(NS + "states-") else node["rkaf:assertsPredicate"].removeprefix(NS)
            evidence = [e["fragment_id"] for e in c["evidence"] if e["field"] == field]
            binding = {"@id": NS + "binding:" + digest([node["@id"], evidence, c["occurrence_id"]]),
                       "@type": "rkaf:EvidenceBinding", "rkaf:bindsAssertion": node["@id"],
                       "rkaf:evidenceRole": "rkaf:textualEvidence", "rkaf:evidentiaryFunction": "rkaf:supports"}
            if evidence:
                binding["rkaf:bindsSourceFragment"] = evidence
            else:
                binding["rkaf:noEvidenceReason"] = "rkaf:declared-hypothesis"
            add(binding)
        for target in c.get("target_ids", []):
            proposition = {"rkaf:assertsSubject": c["id"],
                           "rkaf:assertsPredicate": NS + c["relation"],
                           "rkaf:assertsObject": target, "rkaf:assertionPolarity": "rkaf:affirmed"}
            rid = assertion_id(proposition)
            add({"@id": rid, "@type": "rkaf:RelationshipAssertion", **disposition, **proposition})
            c["assertion_ids"].append(rid)
            add({"@id": NS + "binding:" + digest([rid, c["evidence"][0]["fragment_id"]]),
                 "@type": "rkaf:EvidenceBinding", "rkaf:bindsAssertion": rid,
                 "rkaf:bindsSourceFragment": [c["evidence"][0]["fragment_id"]],
                 "rkaf:evidenceRole": "rkaf:textualEvidence", "rkaf:evidentiaryFunction": "rkaf:qualifies"})
    for row in attestations or []:
        if row.get("@type") == "rkaf:Attestation":
            add(deepcopy(row))
            continue
        aid = row["attestation_id"]
        if ":" not in aid:
            aid = NS + aid
        actor = row["attestor_id"]
        if ":" not in actor:
            actor = NS + "reviewer:" + digest(actor)
        add({"@id": aid, "@type": "rkaf:Attestation",
             "rkaf:attestor": actor, "rkaf:attestorKind": row["attestor_kind"],
             "rkaf:targets": json.loads(row["target_ids_json"]),
             "rkaf:decision": row["decision"], "rkaf:attestationScope": row["attestation_scope"],
             "rkaf:attestedAt": row["attested_at"], "rkaf:rationale": row.get("rationale") or ""})
    context = json.loads((data_root() / "context/rkaf-context.jsonld").read_text())["@context"]
    return {"@context": context, "@graph": list(nodes.values())}


def validate_graph(graph):
    import rdflib
    from pyshacl import validate
    types = {"Artifact": "artifact", "AILineage": "ai-lineage", "Attestation": "attestation",
             "ExtractionActivity": "extraction-activity",
             "ValueAssertion": "value-assertion", "RelationshipAssertion": "relationship-assertion",
             "SourceFragment": "source-fragment", "EvidenceBinding": "evidence-binding"}
    for node in graph["@graph"]:
        name = node["@type"].removeprefix("rkaf:")
        if name not in types:
            raise ValueError(f"Unsupported Core type: {name}")
        schema = json.loads((data_root() / f"compiled/json-schema/core/{types[name]}.schema.json").read_text())
        Draft202012Validator({**schema, "$ref": f"#/$defs/{name}"}).validate(node)
        for selector in node.get("oa:hasSelector", []):
            cls = selector["@type"].removeprefix("oa:")
            Draft202012Validator({**schema, "$ref": f"#/$defs/{cls}"}).validate(selector)
            if cls == "TextPositionSelector" and selector["oa:start"] >= selector["oa:end"]:
                raise ValueError("Evidence interval must be nonempty")
    data = rdflib.Graph().parse(data=canonical(graph), format="json-ld")
    shapes = rdflib.Graph()
    for path in sorted((data_root() / "shapes").glob("*.ttl")):
        shapes.parse(path, format="turtle")
    conforms, _, report = validate(data, shacl_graph=shapes, inference="rdfs", advanced=True)
    if not conforms:
        raise ValueError(str(report))
    return {"core_nodes": len(graph["@graph"]), "shacl_conforms": True,
            "semantic_accuracy": "Requires independent source review"}
