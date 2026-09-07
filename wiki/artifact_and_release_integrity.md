# Artifact and release integrity

## Purpose

`artifact_and_release_integrity` groups three complementary integrity components. Together, they construct and admit immutable platform artifacts, validate content-addressed Core and version 1 Extrapolation records, and verify partitioned version 2 Extrapolation bundles against pinned inputs, schemas, evidence, and totals.

Each component targets a distinct format family and integrity layer. Apply every gate relevant to that format. A successful check does not approve, publish, deploy, or activate a release.

## Architecture

```mermaid
flowchart LR
    subgraph Inputs["Immutable inputs"]
        ArtifactInputs["Build data or materialized artifact,<br/>storage readers, and optional semantics"]
        V1Inputs["Core or v1 Extrapolation JSON,<br/>input releases, and atlas facts"]
        V2Inputs["v2 bundle, copied DocumentRelease v3,<br/>atlas facts, and bundled plus checked-in schemas"]
    end

    subgraph Integrity["artifact_and_release_integrity"]
        Artifact["platform_artifact_runtime<br/>construction and structural admission"]
        V1["release_record_validation<br/>identity and semantic checks"]
        V2["extrapolation_release_v2_verification<br/>bundle and semantic checks"]
    end

    ArtifactInputs --> Artifact --> ArtifactResult["VerificationResult or<br/>admitted VerifiedArtifact"]
    V1Inputs --> Shape["Separate closed<br/>JSON Schema gate"]
    V1Inputs --> V1 --> V1Result["ValidationIssue list"]
    V2Inputs --> V2 --> V2Result["VerificationResult"]

    V1 -.->|"selected v1 JSON, digest,<br/>and stable-ID helpers"| V2

    ArtifactResult --> Gate["Applicable product<br/>release gate(s)"]
    Shape --> Gate
    V1Result --> Gate
    V2Result --> Gate
```

The verification path depends on the candidate format:

```mermaid
flowchart TD
    Candidate["Candidate artifact or release"] --> Kind{"Format"}

    Kind -->|"spicy-artifact 1.0"| PA1["Canonical root and manifests"]
    PA1 --> PA2["Exact membership, sizes,<br/>SHA-256 digests, and counts"]
    PA2 --> PA3["Optional product semantics"]
    PA3 --> PA4["Admitted artifact or<br/>first deterministic refusal"]

    Kind -->|"RulespecCoreRelease or<br/>ExtrapolationRelease v1"| V11["Separate closed JSON Schema gate<br/>plus content-derived identity"]
    V11 --> V12["Core manifest checks or v1 pins,<br/>evidence, receipts, and coverage"]
    V12 --> V13["Empty or populated issue list"]

    Kind -->|"ExtrapolationRelease v2 directory"| V21["Canonical root, manifests,<br/>closed membership, and hashes"]
    V21 --> V22["Exact schema set plus<br/>Arrow and JSON row checks"]
    V22 --> V23["Pins, evidence, coordinates,<br/>dispositions, and totals"]
    V23 --> V24["VerificationResult"]
```

## Core component documentation

| Component | Implementation | Responsibility |
| --- | --- | --- |
| [Platform artifact runtime](platform_artifact_runtime.md) | `packages/rulespec-artifacts/src/rulespec_artifacts/_artifact.py` | Builds canonical roots and manifests, verifies exact structure and bytes, and supports race-resistant reads and durable no-replace publication. `verify_artifact()` returns `VerificationResult`; `admit_artifact()` returns `VerifiedArtifact` or raises `ArtifactVerificationError`. |
| [Release record validation](release_record_validation.md) | `tools/rulespec_release.py` | Validates `RulespecCoreRelease` and single-JSON `ExtrapolationRelease` v1 identities and semantics. It returns `list[ValidationIssue]`; callers must also apply the closed JSON Schema. |
| [Extrapolation release v2 verification](extrapolation_release_v2_verification.md) | `tools/extrapolation_release_v2.py` | Verifies partitioned v2 roots, manifests, schemas, Parquet rows, pins, evidence, dispositions, and rollups. It returns `VerificationResult` with ordered issues and a stable primary code. |

The version 2 verifier reuses strict version 1 JSON loading, canonical bytes and digests, digest syntax, and stable record IDs from `rulespec_release.py`. It separately validates embedded version 1 evidence records against their registered schemas. The platform artifact runtime remains a separate, product-neutral format and runtime.