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
from rulespec_conformance.contract import resources
from .schemas import LIST_FIELDS, TEXT_FIELDS, load_schema

SCHEMA_VERSION = "document-understanding/3"
NS = "urn:rulespec:document-understanding:"
CANDIDATE_SCHEMA = load_schema("candidate")
KINDS = tuple(CANDIDATE_SCHEMA["$defs"]["Kind"]["enum"])
RELATIONS = tuple(CANDIDATE_SCHEMA["$defs"]["Relation"]["enum"])
MEANING_TEXT_FIELDS = ("modality", "modality_quote", "scope_text", "choice_text",
                       "choice_quote", "jurisdiction", "jurisdiction_quote")
MEANING_LIST_FIELDS = ("scope_quotes", "context_quotes", "alternative_quotes")
STRUCTURED_FIELDS = ("concepts", "claimants", "typed_values", "effective_periods")
TERM_FIELDS = ("defined_terms", "term_refs")
MEANING_FIELDS = MEANING_TEXT_FIELDS + MEANING_LIST_FIELDS + STRUCTURED_FIELDS + TERM_FIELDS
MODALITIES = tuple(CANDIDATE_SCHEMA["$defs"]["Modality"]["enum"])
MODALITY_KINDS = {"must": {"requirement"}, "should": {"recommendation"},
                  "may": {"permission", "authority"}, "must_not": {"prohibition"},
                  "not_required": {"exemption", "exception"}, "possible": {"statement"}}


def evidence_expectations(claim):
    """One shared field-to-quote map for compilation and retained review checks."""
    expected = {"summary": claim.get("quote")}
    for field in ("actor", "action", "object", "modality", "choice_text", "jurisdiction"):
        if claim.get(field):
            quote_field = "choice_quote" if field == "choice_text" else field + "_quote"
            expected[field] = claim.get(quote_field, "")
            if field == 'choice_text' and not expected[field]:
                expected[field] = claim['quote']
    if claim.get("logic_text"):
        expected["logic_text"] = claim["logic_text"]
    for field, quotes in (("scope_text", "scope_quotes"), ("context", "context_quotes"),
                          ("alternative", "alternative_quotes")):
        expected.update({f"{field}:{i}": quote for i, quote in enumerate(claim.get(quotes, []))})
    for field in STRUCTURED_FIELDS:
        expected.update({f"{field}:{i}": item["quote"] for i, item in enumerate(claim.get(field, []))})
    for i, item in enumerate(claim.get("defined_terms", [])):
        expected[f"defined_terms:{i}"] = item["quote"]
        expected.update({f"defined_terms:{i}:source:{j}": quote for j, quote in enumerate(item["source_quotes"])})
    return expected


def _scope_record(claim):
    from .enrichment import period_record
    fields = {e["field"] for e in claim["evidence"]}
    condition = claim.get("scope_text") and claim.get("scope_quotes") and all(
        f"scope_text:{i}" in fields for i in range(len(claim["scope_quotes"])))
    period = period_record(claim)
    if not condition and not period:
        return None
    body = {"rkaf:appliesInJurisdiction": [claim["jurisdiction"]] if "jurisdiction" in fields else []}
    if condition:
        body["rkaf:applicabilityCondition"] = claim["scope_text"]
    if period:
        body["rkaf:hasEffectivePeriod"] = period["@id"]
    return {"@id": NS + "scope:" + digest(body), "@type": "rkaf:ApplicabilityScope", **body}


def canonical(value):
    return canonical_json(value)


def sparse(value):
    """Omit absent optional values for consumers; retain zero and false."""
    if isinstance(value, dict):
        return {k: cleaned for k, v in value.items() if (cleaned := sparse(v)) not in (None, '', [], {})}
    if isinstance(value, (list, tuple)):
        return [sparse(v) for v in value]
    return value


def digest(value):
    if not isinstance(value, (str, bytes)):
        value = canonical(value)
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def data_root():
    return Path(str(resources.DATA_ROOT))


def _issue(code, field, message):
    return {"code": code, "field": field, "message": message}


def _evidence_position(document, quote, start=None, end=None, within=None):
    # A unique match within a verified parent quote can disambiguate repeated words.
    text = document["text"]
    if within and quote:
        lo, hi = within
        local = resolve_exact_evidence_offsets(text[lo:hi], quote, None, None)
        if local:
            start, end = lo + local.start, lo + local.end
    return resolve_exact_evidence_offsets(text, quote, start, end)


def _fragment(document, quote, field, start, end):
    """Address exact prepared text; callers separately check source eligibility."""
    artifact = SimpleNamespace(raw_fields={"text": document['text']})
    fragment = verify_fragment(artifact, key=field, source_field="text",
                               start=start, end=end, artifact_iri=document["id"],
                               expected_text=quote)
    return {"field": field, "quote": quote, "start": start, "end": end,
            "fragment_id": fragment.urn}


def _evidence(document, quote, field, start=None, end=None, within=None):
    pos = _evidence_position(document, quote, start, end, within)
    if pos is None:
        return None
    if any(part["kind"] != "source" and part["start"] < pos.end and pos.start < part["end"]
           for part in document.get("source_map", [])):
        return None
    return _fragment(document, quote, field, pos.start, pos.end)


def evidence_parts(document, quote, field, start=None, end=None, within=None):
    """Keep a complete quote supported by original slices across inserted whitespace."""
    pos = _evidence_position(document, quote, start, end, within)
    if pos is None:
        return []
    if whole := _evidence(document, quote, field, pos.start, pos.end):
        return [whole]
    text = document['text']
    if any(p['kind'] != 'source' and text[max(pos.start, p['start']):min(pos.end, p['end'])].strip()
           for p in document.get('source_map', []) if p['start'] < pos.end and pos.start < p['end']):
        return []
    from .documents import source_slicer
    return [_fragment(document, text[start:end], field, start, end)
            for start, end in source_slicer(document)(pos.start, pos.end)]


def _fragment_node(document, evidence):
    return {"@id": evidence["fragment_id"], "@type": "rkaf:SourceFragment",
            "oa:hasSource": document["id"],
            "rkaf:fragmentIdentityScheme": "rkaf:carrier-local-fragment",
            "rkaf:sourceArtifactDigest": "sha256:" + document["sha256"],
            "rkaf:fragmentContentDigest": "sha256:" + digest(evidence["quote"]),
            "rkaf:selectorKind": ["oa:TextQuoteSelector", "oa:TextPositionSelector"],
            "oa:hasSelector": [{"@type": "oa:TextQuoteSelector", "oa:exact": evidence["quote"]},
                {"@type": "oa:TextPositionSelector", "oa:start": evidence["start"], "oa:end": evidence["end"],
                 "rkaf:coordinateSystem": "rkaf:unicode-codepoint"}]}


def _claim(document, candidate, *, rule_id, occurrence_id, origin="aiSuggested"):
    Draft202012Validator(CANDIDATE_SCHEMA).validate(candidate)
    c = {field: "" for field in TEXT_FIELDS}
    c.update({field: [] for field in LIST_FIELDS})
    c.update(relation="none", modality="uncertain", section_id="", window_id="", start=None, end=None)
    c.update(deepcopy(candidate))
    expected_kinds = MODALITY_KINDS.get(c["modality"])
    if expected_kinds and c["kind"] not in expected_kinds:
        raise ValueError("Candidate kind contradicts its declared modality")
    main = _evidence_position(document, c["quote"], c["start"], c["end"])
    if main is None:
        raise ValueError("Main quotation is absent or ambiguous in the pinned source")
    evidence = evidence_parts(document, c['quote'], 'summary', main.start, main.end)
    if not evidence:
        raise ValueError("Main quotation contains inserted content without complete original-source support")
    c.update(start=main.start, end=main.end)
    from .terms import term_identity, definition_error
    for term in c['defined_terms']:
        if not definition_error(c, term) and evidence_parts(document, term['quote'], 'definition', within=(main.start, main.end)):
            term['id'] = term_identity(document, c, term)
    containing = [s for s in document["sections"]
                  if s["start"] <= c["start"] and c["end"] <= s["end"]]
    if c["section_id"] and not any(s["id"] == c["section_id"] for s in containing):
        raise ValueError("Candidate section does not contain its source quote")
    if not c["section_id"]:
        section = min(containing, key=lambda s: (s["end"] - s["start"], s["start"], s["id"]), default=None)
        c["section_id"] = section["id"] if section else ""
    issues = []
    for field in ("actor", "action", "object"):
        if not c[field]:
            continue
        support = evidence_parts(document, c[field + "_quote"], field,
                                 within=(main.start, main.end))
        if support:
            evidence.extend(support)
        else:
            issues.append(_issue("component_evidence_unresolved", field,
                                 f"Exact supporting text for {field} needs review."))
    if c["logic_text"]:
        support = evidence_parts(document, c["logic_text"], "logic_text",
                                 within=(main.start, main.end))
        if support:
            evidence.extend(support)
        else:
            issues.append(_issue('component_evidence_unresolved', 'logic_text',
                                 'Exact logical wording is absent or ambiguous.'))
        issues.append(_issue("logic_requires_review", "logic_text",
                             "Logical grouping, quantities or timing remain uninterpreted."))
    for field, quote in evidence_expectations(c).items():
        if field in {"summary", "actor", "action", "object", "logic_text"}:
            continue
        if field == "modality" and not quote:
            continue
        support = evidence_parts(document, quote, field, within=(main.start, main.end))
        if support:
            evidence.extend(support)
        else:
            issues.append(_issue("component_evidence_unresolved", field, "Exact supporting text is absent or ambiguous."))
    if c["modality"] == "uncertain":
        issues.append(_issue("modality_unresolved", "modality", "The source meaning has not been classified."))
    if bool(c["scope_text"]) != bool(c["scope_quotes"]):
        issues.append(_issue("scope_evidence_incomplete", "scope_text", "Scope needs both its meaning and source quotations."))
    if c["alternative_quotes"] and not c["choice_text"]:
        issues.append(_issue("alternative_grouping_unresolved", "choice_text", "Retain the source's wording for choosing among these options."))
    if c["kind"] in ("condition", "exception"):
        if c["relation"] == "none" or not c["applies_to"]:
            issues.append(_issue("qualification_target_missing", "applies_to",
                                 "This qualification needs its affected rule or rules."))
    elif c["kind"] == "exemption":
        if c["relation"] != "none" or c["applies_to"]:
            if c["relation"] != "exception" or not c["applies_to"] or c['modality'] != 'not_required':
                raise ValueError("A linked exemption needs not_required force, an exception relationship and affected rules")
    elif c["relation"] != "none" or c["applies_to"]:
        raise ValueError("Only condition, exception or exemption candidates may qualify other rules")
    if c["kind"] == "exception" and c["relation"] != "exception":
        raise ValueError("An exception must use the exception relationship")
    # Application revision identity is not a Core assertion identity.
    semantic = {k: c[k] for k in ("kind", "summary", "actor", "action", "object",
                "logic_text", "relation", "applies_to", "references")}
    semantic.update({k: c[k] for k in MEANING_FIELDS})
    from .enrichment import check_components
    issues.extend(check_components(c))
    from .terms import definition_error
    for i, term in enumerate(c.get("defined_terms", [])):
        if error := definition_error(c, term):
            issues.append(_issue("term_definition_unresolved", f"defined_terms:{i}", error))
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


def _component_family(node):
    if node["@type"] == "rkaf:RelationshipAssertion":
        predicate = node["rkaf:assertsPredicate"]
        return "qualification" if predicate in {NS + relation for relation in RELATIONS if relation != "none"} else predicate
    predicate = node.get("rkaf:assertsPredicate", "")
    return "summary" if predicate.startswith(NS + "states-") else predicate


def _component_nodes(claim, disposition):
    values = {field: claim.get(field) for field in ("summary", "actor", "action", "object", "logic_text",
                                                   "modality", "scope_text", "choice_text", "jurisdiction")}
    values.update({f"alternative:{i}": quote for i, quote in enumerate(claim.get("alternative_quotes", []))})
    # Scope is part of this proposition's value, so a changed scope creates
    # a new proposition without mutating a reused summary or its history.
    meaning = {field: claim.get(field) for field in (
        "kind", "summary", "actor", "action", "object", "logic_text", "modality",
        "scope_text", "choice_text", "alternative_quotes", "jurisdiction", *STRUCTURED_FIELDS)}
    meaning.update({field: claim[field] for field in TERM_FIELDS if claim.get(field)})
    values["meaning"] = canonical(sparse(meaning))
    for field, value in values.items():
        if not value:
            continue
        predicate = NS + ("states-" + claim["kind"] if field == "summary" else field)
        proposition = _value_proposition(claim["rule_id"], predicate, value)
        if field == "meaning":
            proposition["rkaf:assertsValue"] = {"@value": value, "@type": "xsd:string"}
        node = {"@id": assertion_id(proposition), "@type": "rkaf:ValueAssertion", **disposition, **proposition}
        if field == "meaning" and (scope := _scope_record(claim)):
            node["rkaf:hasApplicability"] = scope["@id"]
        if field == "meaning":
            from .enrichment import claimant_record
            if claimant := claimant_record(claim, node["@id"]):
                node["rkaf:hasSourceClaimant"] = claimant["@id"]
        yield node


def resolve_links(document, claims):
    from .terms import term_link_issues
    unresolved = term_link_issues(document, claims)
    baselines = {c['id']: c for c in claims if c['kind'] not in ('condition', 'exception')}
    for c in claims:
        c["target_ids"] = []
        incomplete = False
        for identity in c["applies_to"]:
            if identity in baselines and identity != c['id']:
                c["target_ids"].append(identity)
            else:
                incomplete = True
                unresolved.append({"claim_id": c["id"], "reference": identity,
                    "code": "missing_target"})
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
    for index, term in enumerate(candidate.get('defined_terms', [])):
        if not term.get('id'):
            # Removing identity explicitly replaces a sense, even when its
            # initial wording matches a previous description.
            term['id'] = NS + 'term:' + digest([document['id'], event_id, index])
    claim = _claim(document, candidate, rule_id=original_claim["rule_id"],
                   occurrence_id=NS + "occurrence:" + digest(event_id), origin=origin)
    claim["id"] = NS + "revision:" + digest([claim["id"], event_id])
    claim["supersedes"] = [original_claim["id"]]
    claim["prior_assertion_ids"] = list(original_claim["assertion_ids"])
    claim["review_event_id"] = event_id
    return claim


def build_graph(document, claims, run, attestations=None):
    nodes = {}
    from .enrichment import enrich_graph
    claims_by_id = {c["id"]: c for c in claims}
    def add(node):
        # Concepts describe the latest observed sense. Immutable revision artifacts
        # retain every prior description; assertion origins still remain immutable.
        if node['@type'] == 'rkaf:LocalConcept':
            nodes[node['@id']] = node
            return
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
         "rkaf:temperature": float(run.get("temperature", 0.0)),
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
             "rkaf:extractedBy": NS + "extractor:langextract", "rkaf:extractorVersion": run.get("profile", SCHEMA_VERSION),
             "rkaf:requestContractDigest": "sha256:" + window["request_sha256"],
             "rkaf:extractionModelRef": NS + "model:" + digest(run.get("model")),
             "rkaf:extractionPromptRef": NS + "prompt:" + run.get("prompt_sha256", digest("fixture")),
             "rkaf:inputDigest": ["sha256:" + document["sha256"]],
             "rkaf:hasAILineage": lineage_id})
    for c in claims:
        origin = c.get("origin", "aiSuggested")
        claim_lineage = lineage_id
        if origin == "aiSuggested" and c.get("review_event_id"):
            provenance = c.get('review_provenance', {})
            claim_lineage = NS + "lineage:" + digest(c["review_event_id"])
            add({"@id": claim_lineage, "@type": "rkaf:AILineage",
                 "rkaf:modelId": provenance.get('model', 'review-agent'), "rkaf:modelVersion": provenance.get('model_version', 'not-recorded'),
                 "rkaf:temperature": float(provenance.get('temperature', 0.0)),
                 "rkaf:promptTemplateRef": NS + 'request:' + provenance['request_sha256'] if provenance else c['review_event_id'],
                 "rkaf:inputContextHash": "sha256:" + provenance.get('input_sha256', document['sha256'])})
        disposition = {"rkaf:assertionOrigin": "rkaf:" + origin,
                       "rkaf:epistemicBasis": "rkaf:statisticalInference" if origin == "aiSuggested" else "rkaf:userAssertion",
                       "rkaf:usageEligibility": "rkaf:reviewQueueOnly",
                       "rkaf:consumerLifecycleState": "rkaf:draft"}
        if origin == "aiSuggested":
            disposition["rkaf:hasAILineage"] = claim_lineage
        if not c.get("review_event_id") and c.get("window_id") in activities:
            disposition["rkaf:hasExtractionProvenance"] = activities[c["window_id"]]
        for e in c["evidence"]:
            add(_fragment_node(document, e))
        components = list(_component_nodes(c, disposition))
        if scope := _scope_record(c):
            add(scope)
        c["assertion_ids"] = [n["@id"] for n in components]
        for node in components:
            prior = [p for p in c.get("prior_assertion_ids", [])
                     if p != node["@id"] and p in nodes and
                     _component_family(nodes[p]) == _component_family(node)]
            if prior:
                node["rkaf:supersedesAssertion"] = prior
            add(node)
            field = "summary" if node["rkaf:assertsPredicate"].startswith(NS + "states-") else node["rkaf:assertsPredicate"].removeprefix(NS)
            if field == "meaning":
                c["meaning_assertion_id"] = node["@id"]
            functions = {"supports": [e["fragment_id"] for e in c["evidence"]
                         if e["field"] == field or e["field"].startswith(field + ":")
                         or (field == "meaning" and not e["field"].startswith(("scope_text:", "context:")))]}
            if field in {"summary", "meaning"}:
                functions.update({function: [e["fragment_id"] for e in c["evidence"] if e["field"].startswith(prefix)]
                                  for function, prefix in (("definesScope", "scope_text:"), ("providesContext", "context:"))})
            for function, fragments in functions.items():
                fragments = list(dict.fromkeys(fragments))
                if not fragments and function != "supports":
                    continue
                if not fragments:
                    # A failed component locator is not a declared hypothesis.
                    # Preserve the examined source as context, not verified support.
                    fragments = [e['fragment_id'] for e in c['evidence'] if e['field'] == 'summary']
                    function = 'providesContext'
                binding = {"@id": NS + "binding:" + digest([node["@id"], fragments, c["occurrence_id"], function]),
                           "@type": "rkaf:EvidenceBinding", "rkaf:bindsAssertion": node["@id"],
                           "rkaf:evidenceRole": "rkaf:textualEvidence", "rkaf:evidentiaryFunction": "rkaf:" + function}
                binding['rkaf:bindsSourceFragment'] = fragments
                add(binding)
        for target in c.get("target_ids", []):
            proposition = {"rkaf:assertsSubject": c["id"],
                           "rkaf:assertsPredicate": NS + c["relation"],
                           "rkaf:assertsObject": target, "rkaf:assertionPolarity": "rkaf:affirmed"}
            rid = assertion_id(proposition)
            relationship = {"@id": rid, "@type": "rkaf:RelationshipAssertion", **disposition, **proposition}
            prior = [p for p in c.get("prior_assertion_ids", []) if p != rid and p in nodes
                     and _component_family(nodes[p]) == "qualification"]
            if prior:
                relationship["rkaf:supersedesAssertion"] = prior
            add(relationship)
            c["assertion_ids"].append(rid)
            qualification_evidence = [e["fragment_id"] for e in c["evidence"]
                                      if e['field'] == 'summary' or e['field'].startswith('scope_text:')]
            target_claim = claims_by_id.get(target, {})
            qualification_evidence.extend(e["fragment_id"] for e in target_claim.get("evidence", [])
                                          if e["field"] == "summary" or e["field"].startswith("scope_text:"))
            qualification_evidence = list(dict.fromkeys(qualification_evidence))
            binding_key = [rid, qualification_evidence, "qualifies"]
            add({"@id": NS + "binding:" + digest(binding_key),
                 "@type": "rkaf:EvidenceBinding", "rkaf:bindsAssertion": rid,
                 "rkaf:bindsSourceFragment": qualification_evidence,
                 "rkaf:evidenceRole": "rkaf:textualEvidence", "rkaf:evidentiaryFunction": "rkaf:qualifies"})
        enrich_graph(document, c, disposition, add)
        from .terms import add_term_graph
        add_term_graph(document, c, disposition, add)
        # Each stored application revision is also an immutable digital artifact.
        # Its derivation chain records A -> B -> A corrections without rewriting
        # the origin of a reused proposition or creating proposition-level cycles.
        payload = {k: deepcopy(c[k]) for k in (
            "id", "rule_id", "occurrence_id", "kind", "summary", "actor", "action",
            "object", "logic_text", "relation", "applies_to", "references", "quote",
            "start", "end", "section_id", "evidence", "target_ids", "assertion_ids",
            "origin", "supersedes", "review_event_id", 'review_provenance') if k in c}
        payload.update({k: deepcopy(c[k]) for k in (*MEANING_FIELDS, "meaning_assertion_id") if k in c})
        body = canonical(payload)
        revision = {"@id": c["id"], "@type": "rkaf:Artifact",
                    "rkaf:hasArtifactIdentifier": c["id"],
                    "rkaf:artifactIdentifierScheme": "rkaf:urn-persistent",
                    "rkaf:hasContentDigest": "sha256:" + digest(body),
                    "dcterms:format": "application/json", "dcterms:description": body,
                    "dcterms:references": [{"@id": a} for a in c["assertion_ids"]]}
        if c.get("supersedes"):
            revision["prov:wasDerivedFrom"] = [{"@id": p} for p in c["supersedes"]]
        add(revision)
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
    types = {"Artifact": "artifact", "AILineage": "ai-lineage", "Attestation": "attestation", "Finding": "finding",
             "ApplicabilityScope": "applicability-scope", "EffectivePeriod": "effective-period",
             "SourceClaimant": "source-claimant", "ConceptScheme": "concept", "LocalConcept": "concept",
             "ConceptAssignment": "concept-assignment", "ReferenceResourceRelease": "reference-resource-release",
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
    from rulespec_conformance.reference_release_digest import release_digest_errors
    if errors := release_digest_errors(data):
        raise ValueError("; ".join(errors))
    shapes = rdflib.Graph()
    for path in sorted((data_root() / "shapes").glob("*.ttl")):
        shapes.parse(path, format="turtle")
    conforms, _, report = validate(data, shacl_graph=shapes, inference="rdfs", advanced=True)
    if not conforms:
        raise ValueError(str(report))
    return {"core_nodes": len(graph["@graph"]), "shacl_conforms": True,
            "semantic_accuracy": "Requires independent source review"}
