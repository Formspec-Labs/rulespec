# Rulespec Layer 5 — Behavioral Contracts

**Status:** Normative · **Version pin:** `VERSION` file at repo root · **Profile:** L4 conformance per `spec/rkaf-conformance.md` §4

This document specifies the **runtime behavioral contracts** Rulespec implementations MUST honor. Layer 1 (Vocabulary) and Layer 2 (Constraints) constrain document *shape*; Layer 5 constrains document *meaning under operations*. Algorithms here are normative — `rkaf-runtime` is the reference implementation; partner runtimes MUST produce identical outputs on the conformance corpus under `fixtures/behavior/`.

This spec is what makes `L4: pass` mean something. A consumer that ships only shape validation (L2 + L3) but ignores the contracts here cannot claim L4.

---

## §1 — UsageEligibility reducer

The `usageEligibility` lattice (per `constraints/core/usage-eligibility.cue`):

```
rkaf:notEligible < rkaf:searchOnly < rkaf:reviewQueueOnly < rkaf:draftGenerationAllowed
                < rkaf:localOperationalUse < rkaf:publicationAllowed < rkaf:officialUse
```

### §1.1 — Inputs

The reducer is a pure function of:

| Input | Source | Type |
|---|---|---|
| `assertion.baseline_eligibility` | `rkaf:Assertion.rkaf:usageEligibility` | `rkaf:UsageEligibility` |
| `assertion.@id` | the Assertion under evaluation | IRI |

> **Normative — fixture wrapper:** `BehaviorTestCase.rkaf:subjectAssertion` is **REQUIRED** on every `UsageEligibilityReducer` fixture and MUST carry the `@id` of the Assertion the reducer is applied to. There is no implicit "first `rkaf:Assertion` in the graph" fallback — graphs commonly carry multiple Assertions (justification chains, supersession pairs) and silent selection is unsafe. A fixture omitting `rkaf:subjectAssertion` MUST yield `MalformedTestCase`.
| `assertion.consumerLifecycleState` | `rkaf:Assertion.rkaf:consumerLifecycleState` (if set) | `rkaf:ConsumerLifecycleState` (closed enum) |
| `assertion.applicability_set` | `rkaf:Assertion.rkaf:hasApplicability` (zero or more `ApplicabilityScope` IRIs) | `Set<IRI>` |
| `active_adoptions(assertion.@id)` | every `rkaf:LocalAdoption` where `targetAssertion == assertion.@id` AND `adoptionStatus == rkaf:active` | `Set<LocalAdoption>` |
| `consumer.capability_cap` | consumer's declared maximum eligibility | `rkaf:UsageEligibility` |
| `consumer.evaluation_scope` | the scope IRI the consumer is asking about | IRI \| `None` |
| `evaluation_time` | `BehaviorTestCase.rkaf:evaluationTime` or the workflow evaluation instant | RFC 3339 timestamp \| omitted |
| `honored_pit_exceptions(assertion.@id)` | every exception retaining this assertion whose verified case date falls before its cutoff (§4) | `Set<PointInTimeException>` |

### §1.2 — Algorithm

```text
fn reduce_usage_eligibility(
    assertion: &Assertion,
    graph: &Graph,
    consumer: &BridgeConsumerRegistration,
    eval_scope: Option<IRI>,
    case: CaseDateInput,
    evaluation_time: Option<DateTime>,
) -> UsageEligibility:

    // Step 1 — applicability gate
    if eval_scope.is_some()
       AND not assertion.applicability_set.is_empty()
       AND eval_scope.unwrap() not in assertion.applicability_set:
        return rkaf:notEligible

    // Steps 2 and 3 — lifecycle and date gates
    if assertion has a linked version or a dated retention, and §4 does not select it for this case:
        return rkaf:notEligible
    if assertion.consumerLifecycleState == rkaf:staleForCurrentUse
       AND honored_pit_exceptions(assertion.@id, case).is_empty():
        return rkaf:notEligible

    // Step 4 — broaden the baseline only within an active adoption's scope
    let after_adoptions = assertion.baseline_eligibility OR rkaf:notEligible
    for la in active_adoptions effective at evaluation_time:
        if eval_scope.is_some() AND la.adoptionScope == eval_scope.unwrap():
            after_adoptions = max_on_lattice(after_adoptions, la.usageEligibility)

    // Step 5.5 — freshness gate (Plan 7e.2; optional, narrowing only)
    if consumer.maxAttestationStalenessDays.is_some()
       AND evaluation_time.is_none()
       AND exists att targeting assertion.@id:
        raise MalformedTestCase
    let after_freshness =
        if consumer.maxAttestationStalenessDays.is_some()
           AND evaluation_time.is_some()
           AND exists att in effective_attestations_at(evaluation_time) targeting assertion.@id:
                att.lastVerifiedAt is absent
                OR att.lastVerifiedAt < (evaluation_time - maxAttestationStalenessDays):
            step_down_lattice(after_adoptions)   // one step downward
        else:
            after_adoptions

    // Step 5 — consumer capability cap (narrowing only)
    let capped = min_on_lattice(after_freshness, consumer.capability_cap)

    return capped
```

> **Normative — Step 4 approval dates.** With an evaluation instant, an active approval requires a valid `rkaf:adoptedAt` timestamp and applies from that timestamp, inclusive. A bounded approval also requires an evaluation instant and applies until its `rkaf:validUntil` timestamp, exclusive. The reducer excludes individual approvals with missing or malformed required timestamps. Other active, in-scope approvals still participate. Without an evaluation instant, legacy approvals that omit an expiry remain eligible based on active status.

> **Normative — Step 5.5 freshness gate (Plan 7e.2).** When the consumer declares `rkaf:maxAttestationStalenessDays`, the reducer narrows the effective level **one lattice step downward** if any effective Attestation targeting the assertion lacks `rkaf:lastVerifiedAt` or was last verified before `evaluation_time - maxAttestationStalenessDays`. An Attestation targets the assertion if its `rkaf:targets` array contains the assertion `@id`. An Attestation is effective if it has not been revoked at the evaluation instant and its `rkaf:hasEffectivePeriod`, when set, contains that instant. The reducer skips the freshness check when the consumer omits `rkaf:maxAttestationStalenessDays`. If the reduction reaches this step, the consumer declares a window, and any Attestation targets the assertion, omitting `rkaf:evaluationTime` MUST yield `MalformedTestCase`. Any supplied evaluation time MUST be a valid RFC 3339 string, including when the check can be skipped. Malformed timestamps on `lastVerifiedAt`, `revokedAt`, or `effectivePeriod{Start,End}`, and dangling `rkaf:hasEffectivePeriod` IRIs encountered during the check, MUST yield `MalformedTestCase`.

### §1.3 — Invariants

1. **Consumers MAY narrow. Consumers MUST NOT broaden** — every step except #4 is monotonically narrowing; #4 is bounded to `adoptionScope`. Outside the scope the broadening does not apply.
2. **`LocalAdoption` is the only authorized broadening operation** (v0.1 §1.4 invariant preserved).
3. **Recompute when any input changes, including the case date or its verification status.** Cached effective state MUST be invalidated on attestation, adoption, lifecycle event, or PIT exception ingest.
4. **`assertion.consumerLifecycleState == staleForCurrentUse` plus no honored PIT** ⇒ `notEligible` regardless of all other inputs.
5. A consumer that lacks the evaluation anchor cannot honor the exception. The point-in-time evaluator and bridge rule 4 report `rkaf:UnsupportedEvaluationAnchor`. A case date must satisfy §4 before either the baseline or an office approval can authorize use of a stale assertion.

### §1.4 — Scope enumeration

The reducer is evaluated per scope. For behavior fixtures, the L4 runtime reads the explicit scope list from `BehaviorTestCase.rkaf:evaluationScopes` (a list of scope IRIs). Production runtimes derive the scope set from the union of:

- All `adoptionScope` values across `LocalAdoption` targeting the assertion
- All `appliesInJurisdiction` values across `assertion.hasApplicability`'s `ApplicabilityScope` records
- The literal IRI `"(workspace)"` representing workspace-wide evaluation (no scope)

### §1.5 — Output

For evaluations carrying explicit scopes:
```
{ byScope: { "<scope-iri>": "<rkaf:level>", ... } }
```

For workspace-wide evaluations (no scope), the runtime treats `eval_scope = None`; step 4's LocalAdoption broadening is skipped (LocalAdoptions are scoped facts) and the output is:
```
{ effectiveUsageEligibility: "<rkaf:level>", rationale: "<string>" }
```

A LocalAdoption with `adoptionScope == "(workspace)"` is intentionally not a thing today; adoptions are always scope-bound. Workspace-wide reduction therefore only sees baseline + lifecycle + consumer cap.

---

## §2 — CascadeClosureV1

Transitive closure over the **inverse** of the *dependency* edges listed below, scoped to nodes that are active/adopted at the triggering `LifecycleEvent.effectiveDate`. The algorithm name `rkaf:CascadeClosureV1` is the L4 conformance identifier; partner implementations MUST emit this string.

### §2.1 — Trigger edges vs. cascade edges

v0.1 §4.3 lists 11 edges as "the cascade closure set." This spec disambiguates two functionally distinct categories:

**Trigger edges** — these *establish the seed* of a cascade but are NOT traversed by the closure algorithm. They identify which node was disrupted (the predecessor in a supersession, the assertion superseded by a new version, etc.). The successor / superseder is not affected by its own act of superseding.

| # | Predicate | Role |
|---|---|---|
| T1 | `rkaf:supersedesAssertion` | Successor's outgoing edge ⇒ predecessor is the cascade seed |
| T2 | `rkaf:supersedesWorkProduct` | Successor's outgoing edge ⇒ predecessor is the cascade seed |
| T3 | `rkaf:LifecycleEvent.appliesTo` | LifecycleEvent's outgoing list ⇒ each entry is a cascade seed |

**Cascade edges** — these *propagate* the affected set, traversed BACKWARD from the seed (find all `M` such that `M.predicate = seed.@id` and recurse).

| # | Predicate | What inverse traversal reaches |
|---|---|---|
| C1 | `rkaf:derivedFromFragment` | Every deriver |
| C2 | `rkaf:justifiedByAssertion` | Every dependent work product |
| C3 | `rkaf:hasAuthority` | Every assertion that cited this authority |
| C4 | `rkaf:derivesAuthorityFrom` | Every downstream chain hop |
| C5 | `rkaf:implements` | Every realization |
| C6 | `rkaf:requiresEvidenceType` | Every requirement consumer |
| C7 | `rkaf:collectsEvidenceType` | Every collector |
| C8 | `rkaf:operationallyDependsOn` | Every dependent |
| C9 | `rkaf:LocalAdoption.targetAssertion` | Every adoption of the seed |
| C10 | `rkaf:assertsSubject` / `rkaf:assertsObject` (concept-typed) + 5 SKOS mapping edges | Concept-lifecycle propagation |

**The v0.2 contract reshape adds no edge to either table, and none of its new
classes changes a runtime path.** The reshape introduced `ValueAssertion`,
`SourceClaimant`, `ExtractionActivity`, `ConceptScheme`, `ConceptAssignment`,
the five document-analysis contracts, and the US rulemaking profile. The
decision for each, recorded here because "we checked and nothing changed" is
otherwise indistinguishable from "we did not check":

- **Provenance, evidence, and identity edges are not dependency edges.**
  `rkaf:hasSourceClaimant`, `rkaf:hasExtractionProvenance`,
  `rkaf:bindsSourceFragment`, release pins, and
  `rkaf:versionLineageEvidence` record support or identity rather than an
  operational dependency. Cascading
  over them would mean that re-anchoring a fragment invalidates every
  assertion whose extraction run happened to read it, which is the opposite of
  what §2.1's dependency reading means. `rkaf:derivedFromFragment` (C1) is
  already the edge that says "this assertion's content depends on that
  region"; adding provenance edges beside it would double-count.
- **`rkaf:assertsValue` is not `rkaf:assertsObject`.** C10 traverses
  `assertsObject` because its object is an IRI that may BE a concept
  undergoing lifecycle change. A `ValueAssertion`'s object is a typed literal:
  it names no node, so there is nothing to traverse to.
- **The document-analysis module is downstream-only.** A
  `RelationComparisonContext` points AT two artifact versions, a
  `ResolverProofRecord` points AT its comparison, a `RelationFinding` points AT
  both. Inverse traversal from an artifact would therefore reach every
  comparison ever run over it — turning one amendment into an unbounded sweep
  of historical analysis records, none of which is a consumer artifact that
  needs revalidating. Analysis records are observations about a graph, not
  dependents within it. Adding them is a separate, evidence-bearing decision,
  not a mechanical consequence of the module existing.
- **The profile contributes lifecycle VALUES, not a parallel event class.**
  `#USLifecycleEvent` composes the kernel `#LifecycleEvent` and keeps
  `@type: "rkaf:LifecycleEvent"` (`spec/rkaf-rulemaking.md` §6), so
  `stale::should_be_stale`, which iterates
  `graph.nodes_by_type("rkaf:LifecycleEvent")`, sees a
  `rkaf:proceedingFinal` event exactly as it sees a `rkaf:amendment` one. Had
  the profile minted its own class, every profile-emitted event would have
  been silently invisible to the stale transition and to T3 seed
  determination — with every shape gate still green.

  Two tests cover this, and the split between them is not incidental.
  `crates/rkaf-runtime/tests/profile_isolation_carrier.rs` runs
  profile-contributed kinds through the stale path and fails if a profile
  VALUE ever stops behaving like a kernel one — its payloads state
  `rkaf:LifecycleEvent` as a constant, so it tests the consequent and cannot
  detect a mint on its own.
  `tools/test_semantic_carriers.py::ProfileIsolationCarrierTests::test_the_profile_overlay_keeps_the_kernel_class`
  is what fails if the overlay ever stops targeting the shared class: it reads
  the profile's `@type` binding and its compiled `sh:targetClass` rather than
  restating either.

### §2.2 — Algorithm

```text
fn cascade_closure_v1(
    seed_node_id: IRI,
    graph: &Graph,
    as_of: DateTime,
) -> Set<IRI>:

    let active_filter = node => node.is_active_or_adopted_at(as_of)
    let visited = HashSet::from([seed_node_id])       // seed IS in affectedSet
    let queue = VecDeque::from([seed_node_id])

    while let Some(current_id) = queue.pop_front():
        for predicate in CASCADE_EDGE_PREDICATES:     // C1..C10 only
            for incoming_node in graph.incoming(current_id, predicate):
                if active_filter(incoming_node):
                    if !visited.contains(incoming_node.@id):
                        visited.insert(incoming_node.@id)
                        queue.push_back(incoming_node.@id)

    return visited
```

### §2.3 — Seed determination

The cascade seed is identified by the trigger edge that initiated the closure:

- A `rkaf:LifecycleEvent` that `appliesTo` an `@id` ⇒ seed is that `@id`.
- A `supersedesAssertion`/`supersedesWorkProduct` relationship ⇒ seed is the *predecessor* (the node being superseded), NOT the successor.

Behavior fixtures carry the seed explicitly as `rkaf:cascadeSeed` on the `BehaviorTestCase`. The L4 runtime reads this field; production runtimes derive the seed from incoming `LifecycleEvent.appliesTo` or from supersession edges.

### §2.4 — `is_active_or_adopted_at(as_of)` filter

The `active_filter` referenced in §2.2 excludes nodes from visitation iff EITHER:

(a) **Lifecycle-state exclusion** — `node.rkaf:consumerLifecycleState` is in the terminal/stale set: `{rkaf:staleForCurrentUse, rkaf:retired, rkaf:withdrawn}`. Nodes without a lifecycle state are active by default.

(b) **Effective-period exclusion** — when the `BehaviorTestCase.rkaf:cascadeAsOf` timestamp is provided, the node's attached `rkaf:hasEffectivePeriod` resolves to an `EffectivePeriod`. The as-of timestamp MUST fall within `effectivePeriodStart..effectivePeriodEnd`. Nodes whose period ends before `as_of` (expired) or starts after `as_of` (not yet effective) are excluded. Comparison is **semantic, not lexicographic** — `as_of`, `effectivePeriodStart`, and `effectivePeriodEnd` are parsed as timezone-aware RFC-3339 (e.g. `chrono::DateTime::parse_from_rfc3339`) and compared as instants, so any valid RFC-3339 offset spelling (`Z`, `+00:00`, `-05:00`, …) is supported. A value that fails RFC-3339 parsing MUST yield `MalformedTestCase`; the runtime MUST NOT silently include or exclude a node whose temporal scope it cannot evaluate.

Production runtimes derive `as_of` from the triggering `LifecycleEvent.effectiveDate`. Behavior fixtures pass it explicitly via `BehaviorTestCase.rkaf:cascadeAsOf`.

### §2.5 — Termination + cycle safety

The graph is finite. The visited set prevents revisiting. **Cycles are not normatively prohibited** (a `Warrant` MAY have `hasPredecessor` pointing back at itself per the edge fixture `warrant-self-predecessor-edge.jsonld`); the algorithm tolerates them via the visited check.

### §2.6 — Output

```
{ affectedSet: ["<@id>", ...], algorithm: "rkaf:CascadeClosureV1" }
```

`affectedSet` is an unordered set INCLUDING the seed; the test harness compares as a set. The algorithm IRI is required for L4 verdicts.

---

## §3 — Bridge contract rules (1–10)

Per v0.1 §5.4. Each rule has a decidable predicate over the graph + the consumer's `BridgeConsumerRegistration`. The runtime evaluates one rule at a time; the harness selects via `BehaviorTestCase.contractRuleNumber`.

### §3.1 — Rule 1: No Rulespec-backed authority inference outside the three predicates

**Predicate:** an Assertion `A` carries a legal-family `Warrant` (i.e., `hasWarrant.warrantFamily == rkaf:legal`) but `A` participates in NO `hasAuthority` / `derivesAuthorityFrom` chain AND no `LocalAdoption` targets `A`.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:UnauthorizedLegalInference`.

### §3.2 — Rule 2: usageEligibility via reducer; narrow OK, broaden NOT

**Predicate:** for every `ConsumerEffectiveDeclaration` `D` in the graph, `D.declaredEffective` is `≤ reduce_usage_eligibility(forAssertion, ..., D.declaredScope)` on the lattice. Higher = broadened, which is forbidden except by LocalAdoption (which the reducer already accounts for in §1.2 step 4).

Rule 2 runs the same reducer with the declared scope, the selected consumer, the request's verified case facts (§4), and the same `rkaf:evaluationTime` parsing and freshness requirements (§1.2). Each request covers one case. A workspace-wide check without a case date cannot authorize a case-specific declaration.

A supplied `rkaf:evaluationConsumer` must resolve to a registration by its `@id`. A request can omit the field if the graph has at most one registration. When a registration is selected, a declaration's supplied `rkaf:consumer` must match the consumer named by that registration. An official-use declaration must supply that consumer when the graph contains multiple registrations. Its `rkaf:forAssertion` must identify a member of the Assertion family in the input graph.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:UnauthorizedBroadening`.

### §3.3 — Rule 3: authorityKind preserved; no substitution

**Predicate:** for every `BridgeValidationResult` with a `chainTerminusKind`, the declared kind matches the `authorityKind` of the terminus `Warrant`/`Authority` in the chain.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:AuthorityKindSubstitution`.

### §3.4 — Rule 4: declared EvaluationAnchor support; unsupported anchors refused

**Predicate:** for every `PointInTimeException` in the graph, the `evaluationAnchor` is in the selected registration's `rkaf:supportedEvaluationAnchors`. The rule checks each exception because v0.1 §4.6 requires the consumer to refuse unsupported anchors.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:UnsupportedEvaluationAnchor`.

### §3.5 — Rule 5: cascade staleForCurrentUse transition

**Predicate:** every assertion in the affected set of a recent `LifecycleEvent` has `consumerLifecycleState == rkaf:staleForCurrentUse` UNLESS the event declares a `safeAutomaticMigration` in the consumer's `supportedAutomaticMigrations`.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:MissingStaleTransition`. Implemented in `stale.rs` (§5 below) and delegated from `bridge.rs`.

### §3.6 — Rule 6: concept resolution ≠ authority

**Predicate:** no `@id` resolving to a `rkaf:Concept` (RegisteredConcept or LocalConcept) appears in any `BridgeValidationResult.usedAsAuthority`.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:ConceptUsedAsAuthority`. The BVR field `usedAsAuthority` is the carrier (added to `constraints/core/bridge-validation-result.cue`).

### §3.7 — Rule 7: justification chains MUST terminate

**Predicate:** a chain `work_product → justifiedByAssertion → assertion → hasJustification → justification → hasWarrant → warrant` MUST reach `hasAuthority` (or `derivesAuthorityFrom`) OR a `LocalAdoption` somewhere along the chain (including via warrant-side `derivesAuthorityFrom` hops).

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:UnterminatedJustificationChain`.

**Chain-walk depth:** unbounded by spec; runtime uses a visited-set to protect against cycles.

**Warrant↔Authority transition:** `rkaf:Authority` is a specialization of `rkaf:Warrant` (per `archive/v0.1/spec/rkaf-core-v0.1.md` §2 and the comment block at `constraints/core/authority.cue:1-8`). The chain walker treats every node typed `rkaf:Authority` as also satisfying the `rkaf:Warrant` type for chain-traversal purposes. `derivesAuthorityFrom` hops live on `Authority` nodes and the walker follows them transparently when present.

### §3.8 — Rule 8: bridge-emitted attestations for consumer-detected issues

**Predicate:** for every consumer with a `BridgeIssueAttestationContract` declaring `attestedIssueKinds = K`, every `BridgeValidationResult` from that consumer whose `detectedIssues[]` contains an issue of any kind in `K` MUST be referenced by at least one **effective** `rkaf:Attestation`, where "effective" and "references" are defined below.

**"References" — either path satisfies (ADR-0093):**

(a) **BVR-level match.** The Attestation's `targets` contains the BVR's `@id`. (Legacy path; predates ADR-0093.)

(b) **Finding-level match.** The Attestation's `targetFinding` points at the `@id` of one of the BVR's `findings` (where each entry is an `rkaf:Finding` IRI). This is the targeted-waiver pattern — preferred for new consumers because the Attestation states precisely which detection it is waiving.

**"Effective" — Plan 7e:** the Attestation MUST be in force at the BVR's `validatedAt`. That is:
- `revokedAt` is empty OR strictly after `validatedAt`, AND
- `hasEffectivePeriod` is empty OR its `EffectivePeriod` contains `validatedAt`.

A revoked Attestation, or one whose effective period ended before the BVR was emitted, no longer satisfies the contract — the BVR surfaces an issue without an in-force waiver. Implementations: `bridge.rs::effective_at`.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:UnattestedConsumerIssue`.

**Default attested-issue-kinds** (the closed enum): `staleDep`, `unresolvedConcept`, `brokenAuthority`, `unsupportedAnchor`. Consumers MAY declare a subset; rule fires only over the declared subset.

### §3.9 — Rule 9: bridgeContractVersion declared; unsupported versions refused

**Predicate:** every `BridgeValidationResult.bridgeContractVersion` matches at least one range in the consumer's `BridgeConsumerRegistration.supportsRegistryVersionRange`.

**Range syntax:** semver-range strings (`"^1.0"`, `">=1.0,<2.0"`). Runtime uses the `semver` crate.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:UnsupportedContractVersion`.

### §3.10 — Rule 10: generated artifacts preserve Rulespec justification metadata

**Predicate:** every `rkaf:GeneratedWorkProduct` carries `justifiedByAssertion`, AND the referenced Assertion's justification chain terminates per Rule 7.

**Verdict on violation:** `rkaf:rejected` with `errorClass: rkaf:MissingJustificationMetadata` (missing field) or `rkaf:UnterminatedJustificationChain` (chain incomplete; reuses Rule 7's error).

---

## §4 — PointInTimeException

A policy owner records the controlling `rkaf:evaluationAnchor`, the exclusive calendar cutoff `rkaf:anchorDateBefore`, and the prior rule in `rkaf:retainsAssertion`. An optional `rkaf:successorAssertion` identifies the version that applies from the cutoff onward. Both IDs in a pair resolve to distinct members of the Assertion family. The first exception in a connected history may declare an inclusive start with `rkaf:anchorDateOnOrAfter`. A successor begins at its predecessor’s cutoff. Only the first exception may declare this lower bound.

Every version in a linked succession requires a supporting source. The runtime follows each version's inverse `rkaf:bindsAssertion` link from an `rkaf:EvidenceBinding`, then `rkaf:bindsSourceFragment` and the fragment's `oa:hasSource` link to its Artifact. A citation requires the `rkaf:supports` function and a role of `rkaf:textualEvidence`, `rkaf:structuralEvidence`, `rkaf:authorityCitation` or `rkaf:officialSourceMetadata`. A declaration of absent evidence supplies no citation. Legacy behavior requests without EvidenceBindings can still supply a direct source list in `prov:wasDerivedFrom`. Graph validation still requires EvidenceBindings under Core §4.3.

The requesting case system supplies the following fields **on the evaluation request**. It determines which filing date the case record supports and sets `rkaf:caseDateVerified` to true only after verification. A disputed date can be supplied with false. The runtime compares calendar dates in `YYYY-MM-DD` format. The day a case is opened or reviewed (`rkaf:evaluationTime`) has no bearing on this choice.

| Field | Meaning |
|---|---|
| `rkaf:evaluationAnchor` | The event whose date the case system verified, such as `rkaf:applicationSubmissionTime` |
| `rkaf:caseDate` | The calendar date of that event for this case |
| `rkaf:caseDateVerified` | Whether the caller verified that date |

| Condition | Case decision | Effect on use |
|---|---|---|
| Verified date precedes the first exception’s declared start | `outsideWindow` with `beforeRuleHistoryStart` | The history supplies no applicable version. |
| Verified date falls in the retained window and precedes the first cutoff | `priorRule` | The prior assertion is retained for this case. Office approvals and other limits still apply. |
| Verified date reaches one or more cutoffs | `successorRule` if the last reached cutoff names one | That cutoff selects its successor. A later cutoff can retain that version even if it is stale for current use. |
| Verified date reaches a cutoff with no successor | `outsideWindow` | The retention ends and no linked version applies. |
| Date missing, disputed, unverified, or supplied for another anchor | `needsReview` with `verifyCaseDate` | The date provides no permission to use a version in the succession. |
| Cutoff absent, or nonempty `rkaf:exceptionScope` adds conditions in prose | `needsReview` with `reviewExceptionScope` | Human review is required before automatic use. This includes older prose-only exceptions. |
| Competing successors or predecessors, a cycle, cutoffs that fail to increase, a lower bound at or after its cutoff, or a lower bound on a later exception | `needsReview` with `reviewRuleTransitions` | Review the links and dates before using any version in the succession. |
| A version in the succession lacks supporting source references | `needsReview` with `reviewRuleSources` | Verify its sources before automatic use. |
| Consumer lacks an anchor on any connected exception | `rkaf:UnsupportedEvaluationAnchor` | Refuse the exception, including when the links require review for another reason. |

Invalid verified calendar dates and malformed date bounds yield `MalformedTestCase`. A point-in-time request starts at the exception retaining its named `rkaf:subjectAssertion`. A request can omit the subject when exactly one assertion exception is present. The runtime checks the connected versions and follows their linked cutoffs. A request naming a later subject receives `reviewRuleTransitions` if the case date belongs to an earlier version. Graph order and unrelated rule successions have no effect on selection. The reducer and bridge rule 2 use the same succession when evaluating use of any of its versions.

### §4.1 — Decision record

`Runtime::evaluate` returns the requested assertion's effective state for the anchor and for current use, plus `caseDecision`. The decision's `exception` and `cutoff` identify the exception retaining the requested assertion. Both fields are null if multiple exceptions retain that assertion. A chain with multiple cutoffs also records `transitions`, an ordered list of exception IDs and cutoffs from oldest to newest. When the first transition declares an inclusive start, the decision records it as `earliestCaseDate`. The `status` is relative to the requested assertion. A resolved selection includes `verifiedCaseDate`, `selectedAssertion`, and its `sourceReferences`. When the runtime uses EvidenceBindings, the source references are distinct Artifact IDs in lexical order. Legacy retention-only rules without source references report an empty list. A review decision records its reason and omits a selected rule. Save this decision with the case for notices and appeals. Use the reducer or bridge rule 2 to check whether the office may use the selected version.

This command prints the decision for an illustrative single claim from the Rulespec checkout.

```sh
cargo run --locked --manifest-path crates/Cargo.toml -p rkaf-runtime-cli --bin rkaf-behavior-validate -- \
  --evaluate fixtures/behavior/point-in-time-filing-date.jsonld
```

The fixture applies the Social Security Administration’s verified-filing-date guidance to the rule for evaluating medical opinions. A March 22, 2017 filing selects 20 CFR § 404.1527. A March 27 filing selects § 404.1520c. The example office has active official-use approval for both rules. The verified date controls which approval can apply. The decision cites the April 2018 annual edition of the Code of Federal Regulations from GovInfo. Each cited fragment records the SHA-256 digest of its source XML and its quoted text. The graph links the corresponding SSA pages as related resources. [Prior rule XML](https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1527.xml), [revised rule XML](https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1520c.xml), [SSA filing-date instructions](https://secure.ssa.gov/poms.nsf/lnx/0424503050)


---

## §5 — Stale transition

State machine on `Assertion.consumerLifecycleState`:

```
   [active]
       │
       │   LifecycleEvent.affectedSet includes assertion.@id
       │   AND event.safeAutomaticMigration ∉ consumer.supportedAutomaticMigrations
       ▼
[staleForCurrentUse]
       │
       │   RevalidationClosureEvent.closesRevalidation references the open
       │   RevalidationEvent for this assertion AND closureDecision is one of
       │   {rkaf:revalidated, rkaf:supersededBySuccessor, rkaf:retainedForPointInTime}
       ▼
[active or retired, per closureDecision]
```

The transition is deterministic. `closureDecision == rkaf:retired` moves the state to `retired` (a terminal state); other decisions return to `active`.

---

## §6 — Concept resolution with conflict

Concept resolution emits the complete portable
`rkaf:ConceptResolutionResult` defined in
`spec/rkaf-concept-registry.md` §8. The resolver first records whether it used
live data, a fresh cache, or a stale cache. It then evaluates a direct
registered-concept lookup or the set `M = {m₁, m₂, ...}` of
`ConceptMapping`s where `m.assertsSubject` equals the input concept.

A mapping participates only when:

1. it uses `skos:exactMatch`, `skos:closeMatch`, `skos:broadMatch`, or
   `skos:narrowMatch`; `skos:relatedMatch` remains discovery evidence but is
   not a resolution path;
2. both endpoint release pins identify `rkaf:completeMembership` releases and
   each endpoint is a `prov:hadMember` of its pinned release;
3. its applicability includes the requested purpose and excludes no requested
   purpose;
4. its publication Attestation and lifecycle state are effective at the
   resolution time; and
5. its trust or local-adoption evidence supports the proposed method and usage
   ceiling.

Mappings that fail those conditions may remain discoverable evidence, but they
do not silently authorize a resolution.

For executable conformance fixtures, the non-RDF `resolutionContext` harness
object supplies `cacheStatus`, `registryAvailable`, `requestedPurposes`, and
`consumerCapability`. It is test input, not a Rulespec graph record. Omitted
values mean `notCached`, registry available, no purpose restriction, and
`officialUse` capability respectively. Production runtimes obtain the same
facts from their registry, cache, request, and consumer configuration.

An effective registry-publication Attestation is required for every mapping
path. Exact and close mappings additionally require either a
`managedByRegistry` value trusted by the selected
`BridgeConsumerRegistration` or an active `LocalAdoption` targeting the
mapping. Broad and narrow mappings need no adoption because they remain
discovery-only and cannot exceed `searchOnly`.

```text
fn resolve_concept(input: IRI, graph: &Graph, context: ResolutionContext)
    -> ConceptResolutionResult:

    if input is a usable RegisteredConcept in an exact complete release:
        return result(
            status = resolved,
            method = context.direct_method,       // directRegistry/cacheServed/staleCacheServed
            resolvedConcept = input,
            mappingAssertion = absent,
            cacheStatus = context.cache_status,
            usageCeiling = context.direct_ceiling,
        )

    let mappings = eligible_mappings(input, graph, context)

    if mappings.is_empty():
        return result(
            status = context.unavailable ? registryUnavailable : unresolved,
            method = context.attempted_method,
            resolvedConcept = absent,
            mappingAssertion = absent,
            cacheStatus = context.cache_status,
            usageCeiling = context.failure_ceiling,
        )

    let unique_targets = mappings.iter().map(|m| m.assertsObject).unique().count()

    if unique_targets == 1:
        let selected = strongest_applicable_mapping(mappings)
        return result(
            status = selected.is_discovery_only ? unresolved : resolved,
            method = method_for(selected),
            resolvedConcept = selected.is_discovery_only ? absent : selected.assertsObject,
            mappingAssertion = selected.@id,
            cacheStatus = context.cache_status,
            usageCeiling = ceiling_for(selected, context),
        )

    // Multiple distinct targets → conflict
    let severity = if mappings.any(|m| m.assertsPredicate == "skos:exactMatch"):
                       rkaf:operationalConflict
                   else:
                       rkaf:informational

    let selected = strongest_applicable_mapping(mappings)
    return result(
        status = conflicting,
        method = method_for(selected),
        resolvedConcept = absent,
        mappingAssertion = selected.@id,
        cacheStatus = context.cache_status,
        usageCeiling = context.conflict_ceiling,
        registryConflict: RegistryConflict {
            conflictingEntries: mappings.iter().map(|m| m.@id).collect(),
            severity,
        }
    )
```

`strongest_applicable_mapping` ranks trusted `skos:exactMatch`, locally adopted
`skos:closeMatch`, close match awaiting adoption, and broad/narrow discovery in
that order. `skos:relatedMatch` is useful for discovery but does not resolve a
concept and has no resolution-method value. Equal-strength mappings to the same
target are equivalent for target selection; the implementation chooses the
lexically smallest mapping IRI so the emitted `rkaf:mappingAssertion` is
deterministic.

A mapped result MUST name its selected mapping assertion. A direct result MUST
not. Cached mapping resolution retains the underlying mapping method and
mapping assertion; `rkaf:cacheStatus` records whether the cached evidence is
fresh or stale. The `rkaf:cacheServed` and `rkaf:staleCacheServed` methods are
reserved for cached direct resolution.

Complete release membership proves direct concept identity; it does not by
itself authorize operational use. Without an effective trust input, direct
identity resolution is capped at `searchOnly`. A trusted registry or effective
publication Attestation may raise that ceiling only as far as consumer
capability and narrower policy allow.

The method supplies an upper bound before consumer-specific narrowing:

| Method | Maximum ceiling before narrower policy |
| --- | --- |
| `rkaf:directRegistry` / `rkaf:exactMatchTrusted` / `rkaf:cacheServed` | ceiling supported by the exact release, trust, and consumer capability |
| `rkaf:closeMatchLocallyAdopted` | `rkaf:localOperationalUse` |
| `rkaf:closeMatchAwaitingAdoption` | `rkaf:draftGenerationAllowed` |
| `rkaf:broadOrNarrowMatchDiscoveryOnly` | `rkaf:searchOnly` |
| `rkaf:staleCacheServed` | the fresh direct ceiling, narrowed by cache and risk policy |

The emitted `rkaf:usageCeiling` is the minimum of that method ceiling,
applicability, lifecycle, cache freshness, registry trust, local adoption, and
consumer capability. Resolution never broadens another eligibility input.

### §6.1 — Severity ladder

Decided in order, highest first:

1. **`rkaf:authorityCritical`** — fires when at least two mappings are
   publication-relevant, their targets differ, and at least one carries
   `rkaf:managedByRegistry` in the consumer's
   `BridgeConsumerRegistration.trustedRegistries`.
2. **`rkaf:publicationBlocking`** — fires when at least two mappings are
   publication-relevant and their targets differ.
3. **`rkaf:operationalConflict`** — at least one mapping uses
   `skos:exactMatch` and targets differ.
4. **`rkaf:informational`** — all mappings are non-exact and targets differ.

A mapping is publication-relevant only when it is a member of a
`rkaf:ReferenceResourceRelease`, an unrevoked `rkaf:Attestation` approves it
for `rkaf:registryPublication`, and its effective lifecycle is not stale,
retired, or withdrawn. There is no inline mapping-publication field.

`ConceptMapping.managedByRegistry` is a registry identity and trust input, not
approval. The consumer's `trustedRegistries` field is defined in
`constraints/core/bridge-consumer-registration.cue`. The reference
implementation is `crates/rkaf-runtime/src/concept.rs::compute_severity`.

### §6.2 — Output shape

```
{
  conceptResolutionResult: {
    inputConcept: "<@id>",
    resolutionStatus: "<rkaf:resolutionStatus>",
    resolutionMethod: "<rkaf:resolutionMethod>",
    resolvedConcept?: "<@id>",
    mappingAssertion?: "<@id>",
    cacheStatus: "rkaf:fresh" | "rkaf:stale" | "rkaf:notCached",
    usageCeiling: "<rkaf:usageEligibility>",
    resolvedAt: "<xsd:dateTime>",
    resolverId?: "<@id>"
  },
  registryConflict?: {
    conflictingEntries: ["<@id>", ...],
    severity: "<rkaf:severity>"
  }
}
```

The conditional presence rules for `resolvedConcept` and `mappingAssertion`
are normative even when a carrier does not use the compact key spelling shown
above. `registryConflict` supplements a conflicting result; it never replaces
the required `ConceptResolutionResult`.

---

## §7 — Expected-output format spec (per contract)

The runtime's `BehaviorVerdict` is compared deep-equal to `BehaviorTestCase.rkaf:expectedOutput`. Per-contract shapes:

| Contract | Output keys |
|---|---|
| `rkaf:UsageEligibilityReducer` | `byScope: { <scope>: <level> }` OR `effectiveUsageEligibility: <level>` + `rationale: <str>` |
| `rkaf:CascadeClosureV1` | `affectedSet: [<@id>, ...]` (set-equal) + `algorithm: "rkaf:CascadeClosureV1"` |
| `rkaf:BridgeContractRule` (per rule) | `bridgeValidationResult: <verdict>` + optional `errorClass: <iri>` + optional `rationale: <str>` |
| `rkaf:PointInTimeException` | `"<assertion-id>.effectiveStateForAnchor:<anchor-name>": <state>` + `"<assertion-id>.effectiveStateForCurrentUse": <state>` + `caseDecision` (§4.1), or `errorClass` for an unsupported anchor |
| `rkaf:ConceptResolutionWithConflict` | `conceptResolutionResult: { inputConcept, resolutionStatus, resolutionMethod, cacheStatus, usageCeiling, resolvedAt, ...conditional fields }` + optional `registryConflict: { conflictingEntries: [<@id>+], severity: <severity> }` |

### §7.1 — errorClass IRI registry (closed; extension via §13.4 RFC)

```
rkaf:UnauthorizedLegalInference      (Rule 1)
rkaf:UnauthorizedBroadening          (Rule 2)
rkaf:AuthorityKindSubstitution       (Rule 3)
rkaf:UnsupportedEvaluationAnchor     (Rule 4 / PIT contract)
rkaf:MissingStaleTransition          (Rule 5)
rkaf:ConceptUsedAsAuthority          (Rule 6)
rkaf:UnterminatedJustificationChain  (Rule 7)
rkaf:UnattestedConsumerIssue         (Rule 8)
rkaf:UnsupportedContractVersion      (Rule 9)
rkaf:MissingJustificationMetadata    (Rule 10)
```

---

## §8 — Open ambiguities resolved

Inherited from v0.1 descriptive prose; this document resolves them:

1. **Reducer applicability intersection** — §1.2 Step 1: if eval scope is not in the assertion's `hasApplicability` set, return `notEligible`.
2. **Bridge rule #7 chain-walk depth** — §3.7: no explicit bound; visited set protects against cycles.
3. **`RegistryConflict` severity assignment** — §6.1: canonical mapping
   predicate plus release membership, publication Attestation, lifecycle, and
   registry trust. Operational is the default.
4. **`closeMatch` vs `exactMatch` disagreement** — §6 algorithm: the same
   `assertsObject` is resolved regardless of predicate; different objects
   conflict.
5. **Consumer effective eligibility encoding** — `rkaf:ConsumerEffectiveDeclaration` (constraints/core/consumer-effective-declaration.cue).
6. **When a resolved concept becomes "authority-used"** — `BridgeValidationResult.usedAsAuthority` field.
7. **Which issues require bridge-emitted Attestations** — `BridgeIssueAttestationContract.attestedIssueKinds`; default kinds: `staleDep` / `unresolvedConcept` / `brokenAuthority` / `unsupportedAnchor`.
8. **`bridgeContractVersion` range syntax** — §3.9: semver-range strings parsed by the `semver` crate.

---

## §9 — Reference implementation

`crates/rkaf-runtime/` is the reference implementation. `rkaf-behavior-validate` is the CLI gate `tools/conformance_report.py` shells out to. Partner runtimes MUST produce identical outputs on all fixtures under `fixtures/behavior/`; cross-implementation parity is the L4 conformance contract.

Behavior fixtures live in `fixtures/behavior/`. Each is a `rkaf:BehaviorTestCase` carrying `behaviorContract` (one of the IRIs in §7) + `input` (a JSON-LD graph) + `expectedOutput` (the declared correct result). The runtime computes the contract on the input and deep-equals with the expected output.
