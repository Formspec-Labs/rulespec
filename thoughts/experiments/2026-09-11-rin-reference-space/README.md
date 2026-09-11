# Reuse the existing RIN identifier-space check

**Decision: adopt RefSpec `mint_rin_iri` at the Rulespec reference consumer.**
The [preregistered comparison](design.md) passed its declared fixed-data checks.
The source adapter and wheels are installed and verified together with the
independent [reference-containment change](../2026-09-11-reference-containment/README.md).
There were no model calls, parser-default changes, schema changes or commits.

## Result and limits

Both existing narrow helpers refuse the real amendment heading `1998—Pars.`
and preserve supported RIN candidates. RefSpec's broad `normalize_rin` still
accepts `1998-PARS`, so whole-value normalization alone does not fix this failure.

The existing artifact verifier accepted the four local Unified Agenda tables'
hashes and their declared schema version. Its actions table contains 241,726 rows
and 46,562 distinct RIN values across 60 source editions, 199510 through 202510.
SpicySearch recognizes every distinct value; both narrow helpers accept all of
them and agree on the normalized identifier. This is compatibility with that
pinned artifact, not a RIN recall or issuance estimate. The older upstream
46,547-value measurement describes a different recorded population.

Fifteen constructed/source-excerpt controls and the three saved USLM sources
retain the intended distinctions. The full sources reproduce one RIN false
positive, the amendment heading. The five historically documented unusual RIN
values are already outside the scanner's shape; a downstream check cannot recover
them. The constructed product code `9999-ZZ99` still passes both narrow helpers.
That counterexample disproves the stronger claim that a matching shape establishes
an issued identifier or the meaning of its mention.

The two narrow helpers show no measured accuracy difference here. RefSpec's minter
was selected because the reference adapter already uses RefSpec and can reuse its
identifier-space validation and native provenance without another normalizer or
package dependency. Rulespec's existing projection normalizer remains available
to its current callers; consolidating those callers is separate R8 work.

## What changed

- Rulespec checks normalized RIN candidates with the existing minter and uses its
  existing rejection path for `rin_outside_supported_identifier_space`. Original
  spelling, exact spans and evidence survive ordinary and discovery output.
- Successful shapes remain reference candidates; no target lookup or existence
  claim is added. The helper joins the existing parser fingerprint list.
- RefSpec API/test explanations now distinguish supported syntax from issuance.
  A dated REF-054 clarification preserves the original decision while correcting
  the agency-specific format overstatement and nonexistent roster-lookup claim.
  Those upstream edits change prose only, not parser behavior.

The first post-integration source run passed 512 application tests and 50 RefSpec
minter tests. These are mechanical regressions, not semantic-accuracy scores.
The combined source and isolated-wheel runs each pass 523 application tests;
the RefSpec wheel passes the same 50 minter tests. The working installation passes
dependency and actual CLI checks. Across all seven pinned wheels, 1,318 package
files match both installations; all 187 Python files from the two rebuilt packages
also match their current sources. All 24 CLI artifacts agree across direct source,
isolated wheels and the working environment. These counts describe this verifier's
file population; they are not a change-size comparison with earlier receipts.

The three real sources retain 107 publisher links, 77 associated text readings,
zero residual overlapping text rows and one explicit RIN refusal. Their prepared
text, source evidence and target information remain intact. The
[delivery verification](delivery-verification.json), [wheel inputs](wheel-inputs.json),
[installation commands](install-commands.json), [working installation](working-install-commands.json)
and [final receipt](verification.json) identify the exact delivered build.

## Evidence and preserved failure

- [Declared checks](direct-retry/decision-checks.json), [raw controls](direct-retry/cases.json),
  [full-source candidates](direct-retry/sources.json), [verified corpus](direct-retry/corpus.json),
  and [actual imported modules](direct-retry/modules.json).
- [Application test log](application-source-tests.log), [native helper tests](refspec-owner-tests.log),
  and [recorded test commands](source-test-commands.json).
- [Independent source review](../../reviews/2026-09-11-rin-boundary-review.md).
- The first comparison used the wrong directory for two earlier captures. Its
  partial [control output](direct/cases.json), [failure log](direct.log), and
  [measurement record](measurement.json) remain intact. The corrected-path retry
  used the same declared inputs and criteria. Preflight load waits did not start
  comparisons; their observations remain with the experiment.

Only the deterministic reader behavior is adopted. Fresh context-assisted
extraction, qualified USC, general local paragraphs, metadata/vocabulary use and
the broader R1–R26 objective remain open.
