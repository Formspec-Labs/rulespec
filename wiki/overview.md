# Rulespec repository overview

## Purpose

Rulespec makes rules legible to software. It defines a machine-validatable record of a rule’s origin, authority, lifecycle, adoption, usage permissions, concepts, and supporting evidence.

The repository provides three connected capabilities:

1. Compile authoritative CUE constraints into schemas, types, validation shapes, and policy artifacts.
2. Assess implementations and fixtures through L0–L4 conformance checks.
3. Verify immutable platform artifacts and release records before consumers admit them.

Rulespec supplies the semantic and validation foundation beneath rule-driven products; it is not a workflow engine, document processor, search engine, or publication system.

## End-to-end architecture

```mermaid
flowchart LR
    Sources["Semantic sources<br/>CUE constraints, JSON-LD context,<br/>vocabulary and behavior specifications"]

    Compiler["Constraint compiler<br/>parse, normalize, resolve,<br/>and validate"]
    Registry["Contract term registry<br/>admitted rkaf terms"]

    Generated["Generated artifacts<br/>JSON Schema, Rust, TypeScript,<br/>SHACL, and Rego"]
    PythonAPI["Python authoring API<br/>rulespec_conformance.contract"]

    Data["Rulespec JSON-LD data<br/>fixtures and consumer records"]
    Mappings["SQL, CSV, and Parquet<br/>mapping declarations"]

    Conformance["Conformance assessment<br/>L0 mapping audit and<br/>L1-L4 fixture reporting"]
    Evidence["Reports, verdicts,<br/>self-certification, and exit status"]

    Candidates["Platform artifacts and<br/>Core or Extrapolation releases"]
    Integrity["Artifact and release<br/>integrity verification"]
    Admission["Verified artifact or<br/>ordered refusal reasons"]

    Sources --> Compiler --> Generated
    Sources --> Registry --> PythonAPI
    PythonAPI --> Data
    Generated --> Conformance
    Data --> Conformance
    Mappings --> Conformance
    Conformance --> Evidence

    Generated --> Integrity
    Candidates --> Integrity
    Integrity --> Admission
```

Compilation and validation remain separate responsibilities. The term registry helps Python producers use admitted names, but it does not define their meaning or validate data. Compiled JSON Schema, SHACL, and runtime behavior implement those checks.

### Assessment and integrity paths

```mermaid
flowchart TD
    Input{"Input type"}

    Input -->|"Non-JSON-LD mapping"| L0["L0: audit terms, types,<br/>ranges, transforms, and samples"]
    L0 --> L0Result["Mapping and partner verdicts"]

    Input -->|"JSON-LD fixture"| L1["L1: decode JSON-LD"]
    L1 --> L2["L2: select compiled schema<br/>and validate structure"]
    L2 --> L3["L3: validate SHACL,<br/>digests, and semantic rules"]
    L3 --> L4["L4 when applicable:<br/>run Rust behavior validator"]
    L4 --> Report["Fixture result and report"]

    Input -->|"spicy-artifact/1.0"| Artifact["Check canonical manifests,<br/>membership, sizes, hashes,<br/>counts, and product semantics"]
    Artifact --> ArtifactResult["VerifiedArtifact or<br/>deterministic refusal"]

    Input -->|"Core or Extrapolation v1"| V1["Apply closed JSON Schema,<br/>identity, pin, evidence,<br/>receipt, and coverage checks"]
    V1 --> V1Result["ValidationIssue list"]

    Input -->|"Extrapolation v2 bundle"| V2["Check manifests, schemas,<br/>Parquet rows, pins, evidence,<br/>dispositions, and totals"]
    V2 --> V2Result["VerificationResult"]
```

These checks produce evidence for a release decision. Passing them does not publish, deploy, or activate an artifact.

## Core module documentation

### Semantic compilation and binding

- [Semantic contract compilation and binding](/Users/mikewolfd/Work/rulespec/wiki/semantic_contract_compilation_and_binding.md)
- [Constraint compiler AST](/Users/mikewolfd/Work/rulespec/wiki/constraint_compiler_ast.md) — parses the supported CUE subset, resolves composed shapes, and emits target formats.
- [Contract term registry](/Users/mikewolfd/Work/rulespec/wiki/contract_term_registry.md) — exposes admitted `rkaf:` terms through the Python package.

### Conformance assessment and certification

- [Conformance assessment and certification](/Users/mikewolfd/Work/rulespec/wiki/conformance_assessment_and_certification.md)
- [Compiled schema binding](/Users/mikewolfd/Work/rulespec/wiki/compiled_schema_binding.md) — discovers schemas and selects immutable bindings for L2 validation.
- [Conformance fixture reporting](/Users/mikewolfd/Work/rulespec/wiki/conformance_fixture_reporting.md) — runs L1–L4 checks and renders reports or reference self-certification.
- [L0 mapping audit](/Users/mikewolfd/Work/rulespec/wiki/l0_mapping_audit.md) — audits non-JSON-LD mappings against the vocabulary.

### Artifact and release integrity

- [Artifact and release integrity](/Users/mikewolfd/Work/rulespec/wiki/artifact_and_release_integrity.md)
- [Platform artifact runtime](/Users/mikewolfd/Work/rulespec/wiki/platform_artifact_runtime.md) — constructs and verifies canonical `spicy-artifact/1.0` artifacts.
- [Release record validation](/Users/mikewolfd/Work/rulespec/wiki/release_record_validation.md) — validates Core and Extrapolation version 1 release records.
- [Extrapolation release v2 verification](/Users/mikewolfd/Work/rulespec/wiki/extrapolation_release_v2_verification.md) — verifies partitioned version 2 bundles and their evidence.