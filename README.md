# Rulespec

*Making rules legible to software.*

**Platform artifacts** `spicy-artifact/1.0` implemented locally, unpublished ·
**Bridge contract** `rkaf-bridge/1.0` · **Conformance
corpus** L1-L4 fixtures plus L0 carrier-mapping and vocabulary audits

---

## The problem

We are very good at writing rules — statutes, regulations, policy memos, court rulings, agency guidance. We are very bad at making those rules legible to the software that increasingly carries the load: eligibility portals, intake forms, case management systems, AI assistants, search tools.

The rules live in PDFs. The software lives in code. The bridge between them is usually a person who is overworked, often gone by next quarter, and rarely able to write down everything they knew.

Rulespec is that bridge, written down — a structured, machine-validatable record of what a rule says, where it came from, who has authority over it, where it is in its lifecycle, and what software is allowed to do with it.

## From documents to referenceable knowledge

The product objective is to turn source documents into structured, traceable
knowledge: individually identifiable rules, requirements, concepts, and entities
that software can reference and connect, with every assertion grounded in the
exact passages that support it.

Given a passport adjudication manual, the intended workflow is to:

1. Preserve its chapters, sections, paragraphs, and tables as referenceable
   source passages.
2. Identify the requirements, eligibility conditions, exceptions, definitions,
   procedural steps, entities, and required evidence those passages describe.
3. Connect those pieces: an exception modifies a requirement, a definition
   explains a term, or a document serves as evidence for a condition.
4. Give each piece a stable identity and retain its supporting passages, so
   another system can refer to a specific requirement and inspect its basis.

A section and a rule need not correspond one to one. One paragraph may express
several requirements; one complete requirement may depend on a paragraph, a
definition elsewhere, and an exception in another chapter. The workflow must
preserve both the document's structure and these relationships of meaning.
It must also distinguish direct source statements from interpretations assembled
across passages, retaining uncertainty and review status.

For validating this workflow, Rulespec must operate independently of other
platform products, except RefSpec for tags, terms, and thesauri. Given a local
document, Rulespec owns the input preparation, segmentation by meaning,
extraction, evidence linking, and validation needed to evaluate the result.
DocSpec's document segmentation does not supply the semantic boundaries this
workflow needs; a DocSpec release or service is not a prerequisite.

Rulespec Core defines how the results are represented and checked. An
[experimental local application](packages/rulespec-extrapolator/README.md) now
extracts from exact text, preserves model responses for replay, and supports
persistent corrections and review. Its
[passport-manual results](packages/rulespec-extrapolator/evaluation/results/FINDINGS.md)
expose remaining omissions and scope errors. The complete standalone workflow
remains an implementation objective. Existing
[Extrapolation release formats](spec/rulespec-releases.md#3-extrapolationrelease)
describe an exchange path using prepared upstream inputs; they do not define
the prerequisites for a local validation run. The
[product decisions](docs/decisions.md) record this distinction.

Success means a consumer can reference an individual requirement, follow its
conditions and exceptions, and recover the exact source evidence and any
interpretation involved. Passing schema validation alone does not establish
that the extraction is correct or complete.

## What Rulespec captures

Rulespec represents structured assertions about a document's meaning alongside
the evidence and context that make those assertions trustworthy for software
to use:

- **Origin.** A specific section of a statute, a regulation, a policy memo, a court ruling, an internal interpretation. Citations stay attached to the assertion.
- **Authority.** The chain from "the law" down to "this particular requirement" — legislature, agency, sub-agency, delegated officer. Software can walk the chain and check it ends in something legitimate.
- **Lifecycle.** Active, superseded, retired, withdrawn — with the date each transition happened. A rule that has been overturned cannot quietly keep driving decisions.
- **Adoption.** Which office, jurisdiction, or contract has adopted this rule for use, and starting when.
- **Usage eligibility.** Whether software can search for the rule, draft against it, use it in a real eligibility decision, or cite it in an official notice. These are different permissions, and they are not interchangeable.
- **Concepts.** The word "household" means one thing in SNAP, another in Medicaid. Rulespec records which definition is in play and where two registries disagree.
- **Evidence and trust.** Every durable assertion uses one evidence path and
  keeps construction origin, epistemic basis, review, confidence, and
  eligibility separate.
- **Reference releases.** Assignments and mappings pin the exact digest-backed
  ontology, thesaurus, code list, or classification release whose meaning they
  use.
- **Cascade.** When a rule changes, which forms, workflows, notices, and prior decisions are now affected. Software can compute the blast radius.

## A few questions Rulespec lets software answer

- *Can I use this rule to generate an official notice today, or only to draft one for review?*
- *Has the underlying authority for this rule been overturned?*
- *When this regulation was amended last week, what intake forms quietly became stale?*
- *Two registries disagree on a definition. Which one do we follow, and how should the system surface the disagreement?*
- *This determination was made under the old rule. Can it stand under a point-in-time exception, or does it need to be redone?*

Each used to require a phone call, an email chain, or a careful re-read of a long memo. Rulespec lets a piece of software answer them, with a citation trail strong enough to defend in an audit.

## What Rulespec is not

A workflow engine, a form builder, a case manager, an AI assistant, a search
engine, a document generator, or a policy authoring tool. Rulespec Core is the
portable substrate underneath those products. The separately versioned
Rulespec Extrapolator can produce evidence-bound candidates for review, but
it does not acquire source documents, govern vocabularies, rank results, or
serve search.

Those tools attach a thin layer of Rulespec metadata to whatever they already build — an *overlay* — and in return they get answers to the questions above. They do not give up their own data model. They attach the overlay where it matters and ignore it where it doesn't.

The hardest part of building rule-driven software is not building the engine. It is keeping the engine in sync with the rules as the world changes underneath it. Rulespec is the sync layer.

## How conformance works

Rulespec has two conformance paths. L0 lets tabular, SQL, parquet, and CSV producers use the vocabulary through an audited carrier mapping without pretending to emit JSON-LD. L1–L4 are cumulative JSON-LD levels: parse, shape, constraint, then runtime behavior.

| Layer | What it checks | How |
|---|---|---|
| **L0 — Vocabulary** | Non-JSON-LD fields map to registered terms, identifiers, and enums | `tools/l0_mapping_audit.py` |
| **L1 — Parse** | Valid JSON-LD, contexts resolve, IRIs well-formed | `rulespec-ci-validate` parse pass |
| **L2 — Shape** | JSON Schema conformance per primitive type | Generated schemas under `compiled/json-schema/core/` |
| **L3 — Constraint** | Cross-property invariants and release-manifest integrity | `rulespec-ci-validate` (SHACL plus RDFC-1.0 digest checks) |
| **L4 — Behavior** | Five algorithmic contracts — usage-eligibility reducer, cascade closure, ten bridge-contract rules, point-in-time exceptions, concept-resolution conflict | `rkaf-behavior-validate` (Rust runtime) |

Repository audits such as `tools/vocab_audit.py` keep the specification, CUE source, generated schemas, and fixtures aligned. They are release gates, not a fifth consumer conformance level.

Run the full sweep:

```bash
make test
```

The default Makefile gate uses `uv` to resolve Python 3.12 and the pinned
dependencies in `requirements.txt`; `rdfcanon==1.0.0` requires Python 3.12.
The report cross-references every fixture against every layer. Behavior
fixtures are produced by a small but exact Rust runtime that implements the
five contracts described in `spec/rkaf-behavior.md`.

Rulespec has three non-duplicating distributions. Artifact consumers install the
small `rulespec-artifacts` distribution for canonical JSON, framed-section and
schema-bundle digests, container building, and structural verification. It has
no RDF, JSON-LD, SHACL, `rdflib`, `pyshacl`, or RDF-canonicalization dependency.
The full `rulespec-conformance` validator depends on it and adds the SHACL suite,
compiled graph schemas, JSON-LD context, and Rulespec graph fixture corpus. A
consumer can run either without this repository. Producers of Rulespec data
install `rulespec-projection`, the deterministic layer of the document
projection: it re-slices every fragment against the stored text, mints the
canonical citation IRIs, reifies relationship rows the published tables already
assert, and assembles the JSON-LD document with its run record. It depends on
nothing outside the standard library and is the reference producer of the
format this repository verifies. No distribution is published to an index yet;
build the wheels from a compiled checkout:

```bash
make compile
uv build --project packages/rulespec-artifacts --wheel --out-dir dist/artifacts
uv build --project packages/rulespec-projection --wheel --out-dir dist/projection
uv build --wheel
pip install dist/artifacts/rulespec_artifacts-*.whl dist/rulespec_conformance-*.whl
rulespec-ci-validate --json your-graph.jsonld
```

`make test-package` runs every distribution outside the checkout. Its
`test-package-artifacts` stage uses a separate empty environment and proves the
artifact wheel does not install `rdflib`, `pyshacl`, or `rdfcanon`; its
`test-package-conformance` stage then checks the full graph validator in a
second environment; its `test-package-projection` stage installs the projection
wheel alone, proves its dependency closure is empty, and reruns the package's
suite, whose parity fixtures were produced by the producer it was moved from.
`tools/ci_validate.py` remains as a shim so in-checkout invocations keep
working. L4 behavior validation is the Rust runtime and is not in the wheel.

The same wheel carries the contract itself, for consumers that build Rulespec
data rather than validate someone else's:

```python
from rulespec_conformance.contract import USAGE_ELIGIBILITY, resources, terms

USAGE_ELIGIBILITY.index(level)         # rank in the normative closed lattice
resources.json_schema("artifact")      # compiled Draft 2020-12 schema
resources.shacl("warrant")             # compiled Turtle
resources.shapes("rkaf-shapes-core")   # hand-authored Turtle
resources.context()                    # the JSON-LD context document
terms.hasContentDigest                 # "rkaf:hasContentDigest"
```

Data is reached through `importlib.resources`, never a path built from
`__file__`. `contract.enums` and `contract.terms` are generated from the CUE
and the normative specs by `tools/build_contract_exports.py`, so a term
Rulespec renamed or retired is an `ImportError` in the consumer's build rather
than a string that validates as a string. `python -m
rulespec_conformance.contract` prints what the installed contract carries and
fails if any of it is missing.

## Who this is for

People building software that makes consequential decisions on the public's behalf.

- A state benefits agency building an eligibility portal that has to keep working when next year's amendments land.
- A nonprofit running a legal-aid intelligence tool where every answer needs receipts.
- A federal contractor building a case management system that must outlast its developers.
- A grants office tracking which awards are still legally authorized as Congress amends the underlying program.
- An AI assistant claiming trustworthy answers and needing to show, on demand, exactly which rule it relied on and whether that rule is still in force.

Anywhere the rules move faster than the developers can rewrite them.

## How to read this repository

- **Conceptual entry point** — [`spec/`](spec/) (prose specification) and [`fixtures/`](fixtures/) (worked examples; narratives included).
- **Validation tooling** — [`tools/`](tools/) (Python gates: parse, shape, vocab, conformance report).
- **Runtime** — [`crates/rkaf-runtime/`](crates/rkaf-runtime/) (Rust engine implementing the five behavioral contracts), [`crates/rkaf-runtime-cli/`](crates/rkaf-runtime-cli/) (the CLI the conformance report shells out to).
- **Shape source** — [`constraints/`](constraints/) (CUE) compiles into JSON Schema, Rust types, SHACL, and TypeScript.
- **Release records** — [`spec/rulespec-releases.md`](spec/rulespec-releases.md) defines independent Core and Extrapolator releases; [`release-records/`](release-records/) contains closed schemas and offline conformance fixtures.
- **Decisions and history** — [`docs/decisions.md`](docs/decisions.md) records the product boundary, [`thoughts/`](thoughts/) holds earlier ADRs and design notes, and [`CHANGELOG.md`](CHANGELOG.md) records changes.
- **Contributing** — [`CONTRIBUTING.md`](CONTRIBUTING.md) describes how spec, schemas, validators, and fixtures move together.

## Where Rulespec is in its life

Rulespec is greenfield infrastructure. The semantic foundation has solidified — what gets captured, how it is validated, what software can safely do with it. The current focus is making the substrate stable enough for serious systems to depend on it for years, not weeks.

In practice, schemas, validation shapes, fixtures, and the runtime move together as one coherent thing. Every release is verified by a stack of automated gates that catch quiet drift before it ships. There is no installed base yet to break, and that grace period is being spent on getting the contract right.

## License

- **Specification, schemas, shapes, and documentation** — see [`LICENSE-SPEC`](LICENSE-SPEC). Published openly so any tool in any organization can adopt Rulespec without negotiation.
- **Tooling and runtime** — see [`LICENSE-CODE`](LICENSE-CODE). Professionally licensable for organizations that want supported implementations.

## Citing

If you build on Rulespec, please cite it. A formal citation will appear here once the specification reaches its canonical hosted URL.
