# Native eCFR source lookup delivered locally

**The existing `references` and `discovery-export` commands now locate exact CFR
sections in supplied eCFR XML.** They use the same optional source, target,
containing-section and evidence tables as USLM lookup. No model pass, new
dependency, lookup service or Core schema was added.

RefSpec owns the shared native XML traversal, readable boundaries and source
mapping. Its eCFR address helper reuses the citation grammar and native TITLE,
PART and SECTION fields. Rulespec uses those addresses in its existing source
index. Normal XML input detection supports USLM and eCFR; `prepare_xml`/`read_xml`
replace the application functions' USLM-specific names without compatibility
wrappers. Existing USLM prepared text, native nodes and source maps preserve
their behavior; reader provenance now names the shared implementation.

## Checks that changed the implementation

- A standalone eCFR SECTION prepares as readable input, but lacks a title for
  external lookup. Missing/ambiguous native title context and inconsistent
  part/section metadata refuse explicitly. Filenames never supply a title.
- The actual Title 49 contains a native SECTION numbered `11.105-11.106`.
  Combined native scopes remain source-backed issues while exact siblings stay
  usable. They are not expanded into endpoint targets. This replaces the first
  attempt's whole-input refusal; the observation remains in `design.md`.
- Independent tests caught `note` and `et seq.` being dropped by the CFR source
  reader. The [upstream fix](qualifiers/README.md) retains the full written scope
  with an unresolved refusal, reusing existing lexemes. The identity-only API is
  unchanged and is not used to authorize complete-body lookup.
- Distinct titles and XML versions stay separate; duplicate matching versions
  stay ambiguous. `390.5T` does not resolve to `390.5`. Unresolved paragraphs,
  ranges, appendices and source-edition correspondence remain visible limitations.

## Actual command comparison

The primary input is the pinned native `49 CFR 390.5` section, including its
suspension note. The supplied source is the complete pinned Title 49 capture
dated 2026-08-19. The same prepared primary input is used by the older installed
baseline, whose XML loader did not support eCFR. No text was added to create
explicit citations.

Four actual mentions locate exact source sections: `49 CFR 392.9a`, `49 CFR
386.72`, `49 CFR 393.93` and `49 CFR 390.32`. They share four containing records.
Independent XML tree traversal verifies all 89 retained fragments, including
84 unresolved native combined-section issues and the native title. The baseline
located none. These are source-location gains, not evidence that all citations
were found or that their provisions govern the primary document.

The reference output grows from 27,309 to 169,767 bytes. The discovery output is
422,000 bytes and stores external text/evidence under its own source. These are
local JSON sizes, not model output tokens. The discovery command uses a declared
empty test run over the actual input; it is not a new model extraction result.

The [scaling check](scaling/README.md) measured the standalone reader on full
titles: Title 49 used about 725 MB, Title 40 about 3.4 GB peak reader memory.
These are single-machine observations. Preparation and later verification are
separate reads; a scan shares one index across references in each distinct
supplied source. Primary full-title passage preparation still has a separate
section-search scaling concern. No new performance guarantee is made.

## Validation and delivery

- **641 application tests passed from final source; 641 passed in an isolated
  installed environment.** The earlier source log remains preserved separately.
- Final focused XML, address and qualifier checks: **444 passed**. The broader
  upstream CFR/USC qualifier gate separately passed **778**, with original and
  follow-up captures retained. Changed-file Ruff checks pass. The copied USLM
  oracle retains its original formatting and implementation.
- Source, isolated installed and working installed reference/discovery JSON
  agree exactly. **409 Python files** match the seven pinned wheels in each
  installed environment, and the tested entry points load from site-packages.
- RefSpec commits: `daa4e81a` (shared XML/address reading), `ecba8a98` (scope
  retention). Rulespec application commit: `52a57ce`. Installation uses the
  [pinned wheels](wheel-inputs.json), with recorded offline commands and dependency
  checks. No push, publication, deployment or model calls occurred.

[delivery.json](delivery.json) records command results, commits and installation
locations; `delivery-source-freeze.json` records final code hashes. Original
captures were preserved. `source-final/` is the final source comparison after
import/formatting cleanup; `source/` is the earlier successful development run.
R12's exact eCFR connection is delivered; historical correspondence and broader
scope remain open. The full reuse goal is still active.
