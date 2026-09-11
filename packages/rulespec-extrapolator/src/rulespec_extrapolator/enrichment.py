"""Source-supported Core records for discovery and workflow preparation."""
from datetime import datetime
import re

from rdflib import Graph, Literal, URIRef, XSD
from rulespec_conformance.contract import resources
from rulespec_conformance.reference_release_digest import compute_digest
from rulespec_projection.projection import concept_assignment


def _timestamp(value):
    # Core calls these dateTimes. Require an explicit timezone rather than
    # silently choosing midnight or local time for a source calendar date.
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
        raise ValueError("Effectivity needs a complete timestamp with timezone")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _check_claimant(item, claim):
    """Admit only a directly named speaker at the start of this unit's evidence.

    This intentionally leaves implied speakers, separate attribution context and
    document issuers for review. A citation or agency mention is not attribution.
    It is a bounded textual check, not a general entailment verifier.
    """
    if item["attribution"] == "rkaf:claimantNotStated":
        return
    prefix = re.escape(item["text"].strip()) + r"\s+(?:states|says|declares|reports|asserts|announces)\s*:\s*"
    if (item["attribution"] != "rkaf:claimantNamedInSource"
            or not re.match(prefix, item["quote"].lstrip(), re.IGNORECASE)
            or not claim["quote"].lstrip().startswith(item["quote"].lstrip())):
        raise ValueError("Attribution needs a directly named speaker introducing this unit; other attribution needs review")


def _check_duration(item):
    """Compare a simple source duration with its literal, without unit conversion.

    Supported wording is comparator + whole number (digits or one through twelve)
    + years/months/days + optional reference event. Compound, fractional, ranged,
    implicit and differently expressed durations remain unresolved.
    """
    words = "one two three four five six seven eight nine ten eleven twelve".split()
    numbers = {word: i for i, word in enumerate(words, 1)}
    number = r"(?:0|[1-9][0-9]*|" + "|".join(words) + r")"
    prefix = re.escape(item["comparator"]) + r"\s+" if item["comparator"] else ""
    # The reference event is copied exactly. Only a small explicit set of
    # connectors may sit between the duration and that event.
    suffix = (r"\s+(?:(?:of|after|before|prior to|following)\s+)?" + re.escape(item["anchor"])) if item["anchor"] else ""
    match = re.fullmatch(prefix + r"(" + number + r")\s+(years?|months?|days?)" + suffix + r"[.;]?", item["quote"].strip(), re.IGNORECASE)
    if not match or match[2].casefold() != item["unit"].casefold():
        raise ValueError("Duration wording is outside the supported simple quantity and reference-event grammar")
    quantity = numbers.get(match[1].casefold())
    if quantity is None:
        quantity = int(match[1])
    expected = f"P{quantity}{match[2][0].upper()}"
    if item["value"] != expected:
        raise ValueError(f"Duration disagrees with source quantity; expected {expected} without unit conversion")


def check_components(claim):
    """Keep questionable model interpretations visible, without emitting them as facts."""
    issues = []
    for field in ("concepts", "claimants", "typed_values", "effective_periods"):
        for i, item in enumerate(claim[field]):
            try:
                if not item["quote"].strip():
                    raise ValueError("A structured component needs exact evidence")
                if field == "concepts" and not (item["label"].strip() and item["definition"].strip()):
                    raise ValueError("A local concept needs a label and a definition distinguishing its sense")
                if field == "claimants":
                    if len(claim[field]) > 1:
                        raise ValueError("Resolve competing attributions before selecting a source claimant")
                    if item["attribution"] == "rkaf:claimantNotStated":
                        if item["text"]:
                            raise ValueError("An unstated claimant cannot also name a claimant")
                    elif not item["text"].strip():
                        raise ValueError("An attributed claimant needs source-supported text")
                    _check_claimant(item, claim)
                if field == "typed_values":
                    if not item["name"].strip() or not item["value"].strip():
                        raise ValueError("A typed component needs a name and a lexical value")
                    literal = Literal(item["value"], datatype=XSD[item["datatype"].removeprefix("xsd:")], normalize=False)
                    if literal.ill_typed:
                        raise ValueError("The value is not a valid lexical form for its Core datatype")
                    # These are source words, not executable operators. Keeping
                    # them verbatim avoids silently upgrading a model paraphrase.
                    if any(item[key] and item[key] not in item["quote"] for key in ("comparator", "unit", "anchor")):
                        raise ValueError("Comparator, unit and anchor must occur in the component quotation")
                    if item["datatype"] == "xsd:duration":
                        _check_duration(item)
                if field == "effective_periods":
                    if len(claim[field]) > 1:
                        raise ValueError("Multiple effectivity branches need separate semantic units")
                    start = _timestamp(item["start"])
                    if item["end"] and _timestamp(item["end"]) < start:
                        raise ValueError("An effective period cannot end before it starts")
            except ValueError as error:
                issues.append({"code": "structured_component_unresolved", "field": f"{field}:{i}", "message": str(error)})
    return issues


def supported_components(claim, field):
    evidence = {}
    for item in claim['evidence']:
        evidence.setdefault(item['field'], []).append(item['fragment_id'])
    invalid = {issue["field"] for issue in check_components(claim)}
    for i, item in enumerate(claim[field]):
        key = f"{field}:{i}"
        if key in evidence and key not in invalid:
            yield key, item, evidence[key]


def period_record(claim):
    from .core import NS, digest
    for _, item, _ in supported_components(claim, "effective_periods"):
        body = {"@type": "rkaf:EffectivePeriod", "rkaf:effectivePeriodStart": item["start"]}
        if item["end"]:
            body["rkaf:effectivePeriodEnd"] = item["end"]
        return {"@id": NS + "period:" + digest(body), **body}


def claimant_record(claim, meaning_id):
    from .core import NS, digest
    for _, item, fragments in supported_components(claim, "claimants"):
        body = {"@type": "rkaf:SourceClaimant", "rkaf:claimsAssertion": meaning_id,
                "rkaf:claimantAttribution": item["attribution"], "rkaf:attributedInFragment": fragments}
        if item["text"]:
            body["rkaf:claimantText"] = item["text"]
        return {"@id": NS + "claimant:" + digest(body), **body}


def enrich_graph(document, claim, disposition, add):
    from .core import NS, assertion_id, canonical, digest, _fragment, _fragment_node

    def supported(field):
        return supported_components(claim, field)

    def binding(assertion, fragments):
        identity = fragments[0] if len(fragments) == 1 else fragments
        add({"@id": NS + "binding:" + digest([assertion, identity, claim["occurrence_id"]]),
             "@type": "rkaf:EvidenceBinding", "rkaf:bindsAssertion": assertion,
             "rkaf:bindsSourceFragment": fragments, "rkaf:evidenceRole": "rkaf:textualEvidence",
             "rkaf:evidentiaryFunction": "rkaf:supports"})

    def value_assertion(predicate, value, fragment):
        proposition = {"rkaf:assertsSubject": claim["rule_id"], "rkaf:assertsPredicate": predicate,
                       "rkaf:assertsValue": value, "rkaf:assertionPolarity": "rkaf:affirmed"}
        identity = assertion_id(proposition)
        add({"@id": identity, "@type": "rkaf:ValueAssertion", **disposition, **proposition})
        binding(identity, fragment)
        claim["assertion_ids"].append(identity)
        return identity

    # The complete meaning changes when attribution changes, so old attributions
    # continue to point at the original meaning through an append-only review.
    if claimant := claimant_record(claim, claim["meaning_assertion_id"]):
        add(claimant)

    for _, item, fragment in supported("typed_values"):
        # Pair the useful typed literal with its interpretation. The descriptor
        # is part of its predicate identity: 18 years age and 18 days deadline
        # cannot accidentally share the same proposition.
        descriptor = {key: item[key] for key in ("name", "comparator", "unit", "anchor")}
        predicate = NS + "value:" + digest(descriptor)
        value_assertion(predicate, {"@value": item["value"], "@type": item["datatype"]}, fragment)
        add({"@id": predicate, "@type": "rkaf:Artifact", "rkaf:hasArtifactIdentifier": predicate,
             "rkaf:artifactIdentifierScheme": "rkaf:urn-persistent",
             "rkaf:hasContentDigest": "sha256:" + digest(descriptor), "dcterms:format": "application/json",
             "dcterms:description": canonical(descriptor)})

    if period := period_record(claim):
        add(period)

    tags = list(supported("concepts"))
    if not tags:
        return
    # Tag the complete prepared region. Formatting can be part of this annotation
    # target; the supporting bindings still contain only original-source slices.
    target = _fragment(document, claim['quote'], 'summary', claim['start'], claim['end'])
    add(_fragment_node(document, target))
    scheme_id = NS + "concept-scheme:" + document["sha256"]
    scheme = {"@id": scheme_id, "@type": "rkaf:ConceptScheme", "skos:prefLabel": {"en": "Document concepts"},
              "rkaf:schemeFacet": NS + "topic", "rkaf:definedInScope": document["id"]}
    concepts = {}
    for _, item, _ in tags:
        identity = NS + "concept:" + digest([document["id"], item["label"], item["definition"]])
        concepts[identity] = {"@id": identity, "@type": "rkaf:LocalConcept",
            "skos:prefLabel": {"en": item["label"]}, "skos:definition": {"en": item["definition"]},
            "skos:inScheme": scheme_id, "rkaf:definedInScope": document["id"],
            "rkaf:conceptScope": document["id"]}
    content = {"@context": resources.context()["@context"], "@graph": [scheme, *[concepts[k] for k in sorted(concepts)]]}
    version = digest(content)
    distribution_id = NS + "concept-content:" + version
    distribution = {"@id": distribution_id, "@type": "rkaf:Artifact",
        "rkaf:hasArtifactIdentifier": distribution_id, "rkaf:artifactIdentifierScheme": "rkaf:urn-persistent",
        "rkaf:hasContentDigest": "sha256:" + version, "dcterms:format": "application/ld+json",
        "dcterms:description": canonical(content)}
    release_id = NS + "concept-release:" + version
    release = {"@id": release_id, "@type": "rkaf:ReferenceResourceRelease", "dcterms:isVersionOf": scheme_id,
        "dcat:version": version, "dcterms:type": "skos:ConceptScheme", "rkaf:membershipMode": "rkaf:completeMembership",
        "rkaf:versionBasis": "rkaf:contentDerived", "prov:hadMember": sorted(concepts),
        "dcat:distribution": [distribution_id]}
    rdf = Graph().parse(data=canonical({"@context": content["@context"], "@graph": [release, distribution]}), format="json-ld")
    release["rkaf:referenceReleaseDigest"] = compute_digest(rdf, URIRef(release_id))
    for node in [scheme, *concepts.values(), distribution, release]:
        add(node)
    for key, item, fragment in tags:
        concept_id = NS + "concept:" + digest([document["id"], item["label"], item["definition"]])
        proposition = {"rkaf:assertsSubject": target["fragment_id"], "rkaf:assertsPredicate": item["role"],
                       "rkaf:assertsObject": concept_id, "rkaf:assertionPolarity": "rkaf:affirmed"}
        identity = assertion_id(proposition)
        add(concept_assignment(assertion_iri=identity, subject=proposition["rkaf:assertsSubject"],
            concept_iri=concept_id, role=item["role"], release_iri=release_id, **disposition))
        binding(identity, fragment)
        claim["assertion_ids"].append(identity)
    claim["assertion_ids"] = list(dict.fromkeys(claim["assertion_ids"]))
