# Source-credit consumption: installed with exact source evidence

Completed this bounded integration on 2026-09-11. The source-credit reader adds
two supported mappings on the selected fields and preserves four alternative
targets for an unresolved reference. The initial packaged discovery check exposed
a source-map failure; that failure is now fixed and retained as a regression.
The rebuilt packages are installed and verified in the working environment.

## What changed

- RefSpec shares its existing year-first act-name reordering with the occurrence
  reader. A reordered name must exist in the supplied index; the original source
  spelling and coordinates remain intact. Exact indexed spellings take precedence.
- RefSpec retains existing `SourceCreditTarget` records for a multiple-target
  answer and both source-labeled identifiers on `sources_disagree`. Ordinary
  results keep those fields empty. Resolution policy is unchanged.
- Rulespec's existing `sparse` helper handles tuples as well as lists, so native
  target records serialize without empty optional fields. No model fields, Core
  schemas, additional model passes or new dependency were added.
- Discovery intersects passage evidence with original-source slices from the
  existing source map. Prepared text, passage boundaries and identities remain
  unchanged. Its shared verifier uses the existing exact-evidence function and
  checks supplied fragment identities rather than trusting them.

The [design](design.md) preserves the original comparison and the later, separately
recorded spelling and evidence changes. [Baseline captures](baseline.json) remain
unchanged.

## Selected source results

The three [publication fields](publication-fields.json) come from the local
Unified Agenda legal-authority table. They are published authority fields, not
complete source documents or a fresh general accuracy benchmark.

| Written reference | Observed result with source credits |
| --- | --- |
| `sec. 103 of the 2020 PIPES Act` | Now recognized; maps to `urn:rkaf:us:usc:49:60303` |
| `SECURE 2.0 Act of 2022, sec. 127` | Remains unresolved; retains USC 29 sections 1193, 1193a, 1193b and 1193c as four source-credit candidates |
| `SECURE 2.0 Act of 2022, sec. 303` | Retains the source-credit-supported mapping to `urn:rkaf:us:usc:29:1153` |

Both loaders verified the pinned act and source-credit artifacts. The captures
record input-file hashes, native index rows, source occurrences, refusals and
module identities. The mappings identify code sections in those indexes; they
do not establish target text, applicability or a matching historical edition.

The bounded census examined all **608 distinct, nonempty derived act/section
pairs** found in the selected table. It found **zero real source conflicts** and
**zero resolved table answers accompanied by multiple source-credit targets**.
Constructed controls cover those behaviors; they are not real-source examples.
The population is conditional on existing derived pairs, so it cannot establish
recognition recall.

## Verification observed

| Check | Recorded outcome |
| --- | --- |
| Initial [extractor suite](application-tests.log) | 485 passed; 9798 warnings |
| Export repair, [source suite](application-export-fixed.log) and [working installed suite](application-current.log) | 495 passed in each; 9798 warnings |
| [RefSpec parser/resolver selection](owner-tests.log) | 367 passed |
| [Selected downstream caller tests](caller-tests.log) | 40 passed; 110 deselected |
| [Direct-source capture](source-final.json) vs [isolated wheel](wheel-final.json) | All result data equal; paths differ as expected; all four recorded module hashes equal |
| Prior resolver comparison | Every original resolution field equal across all 608 pairs; added evidence fields excluded from this parity comparison |
| Initial packaged discovery check | Default export failed; enriched export not reached; [original traceback retained](cli/commands.json) |
| Fixed source vs rebuilt-wheel CLI artifacts | All six fixture/output JSON files equal without exclusions |
| Earlier reference regressions | All 7 qualifier, 9 general-family and 6 named-act cases retain their data; parser module hashes change as expected |
| Outside-checkout packaged commands | 12 passed in the isolated wheel environment; 3 more passed in the working environment |
| Dependency and module identity checks | Both environments pass; all six inspected working modules match the verified source/wheel hashes |

The [wheel receipt](verification.json) pins all six package files and records the
comparisons. [Current module identities](current-modules.json),
[current command records](cli-current/commands.json), and dependency checks for
the [isolated](dependency-final.log) and [working](dependency-current.log)
environments establish the local installation. No model calls were made.
Compatibility with previous output does not prove that previous policy was correct.

## Resolved export failure and remaining policy decisions

The constructed CLI document joins the three source fields with explicitly marked
inserted blank lines. Source passages include those separators. Discovery first
checks that passage evidence equals prepared text, then asks `_evidence` to ground
that span in original source. `_evidence` refuses spans crossing inserted text and
returns `None`; the old exporter then attempted to read `fragment_id` from that value.
The [original failure log](cli.log) and fixture are retained.

The repair separates the readable prepared passage from its source evidence.
The new controls went from [7 failed / 3 passed](export-red.log) to passing, and
the [focused suite](export-first.log) passed all 53 checks. Tests cover every
original character, exclude every inserted character, preserve passage IDs/text,
and reject quotation relocation or unverified fragment IDs. Source-map slicing
uses ordered spans and binary search; it does not scan every source slice for
every passage. Existing evidence verification still has its existing source-map
overlap check. No new evidence schema or source-preparation pipeline was needed.
This closes R4/R23's failure in the [canonical task list](../../plans/2026-09-10-reference-integration-task-list.md),
independently of the resolver's target decisions.

Two resolver-policy questions also remain open:

1. SECURE section 127 has one Table III row on page 4660, outside the named
   division T beginning on page 5275. The existing division exclusion only runs
   for multiple rows. Test single-row exclusion with appropriate controls before
   changing that policy upstream.
2. A single Table III answer can coexist with multiple source-credit targets
   under existing policy. The constructed control preserves that behavior; the
   608-pair census found no real instance. Determine the intended policy separately
   from retaining the additional evidence.

## Delivery receipt

- [x] Reproduce and fix the source/discovery boundary; pass default discovery,
  reference scanning and enriched discovery with original and inserted whitespace
  controls, including passages with no extracted claims.
- [x] Replay the earlier CFR, qualifier and named-act cases through rebuilt wheels.
- [x] Record exact wheel digests and dependency checks; update the intended working
  environment and verify its module identities and commands outside the checkout.
- [x] Synchronize installation instructions, upstream research notes and experiment
  receipts with that completed result. Preserve existing failures and captures.

The delivered wheels are under `dist/reference-tools-20260911-credits` and
`dist/reference-integration-20260911-credits-export`. The first application wheel
under `dist/reference-integration-20260911-credits` remains the failed-export
checkpoint. The final isolated environment is
`.tools/reference-integration-20260911-credits-final`; the working environment is
`.tools/document-poc-venv`. Installation instructions select the delivered files.
These changes remain uncommitted and unpublished. R13's policy questions and the
broader local-reference, corpus, vocabulary and quality work remain open.
