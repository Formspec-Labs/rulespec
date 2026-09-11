# Reuse provision text for discovery

Decision: choose an existing source-reader path that can give a discovery user
the text behind a reference, or identify the exact missing component before
building it. Identity recognition alone does not pass this decision.

Hypotheses:

1. Existing section catalogs/oracles may already return a complete target body
   with a pinned source edition. If so, a thin Rulespec adapter should suffice.
2. They may only corroborate identity or location. Then reuse their location and
   an existing publisher reader rather than duplicate the parser or call a model.
3. The needed text may already be present through Rulespec's USLM target table;
   the missing piece could be access across supplied source documents or a useful
   discovery consumer, rather than another upstream reader.

Arms: current reference export versus direct imports of the existing RefSpec and
Spicy Regs/catalog paths, with the same frozen source references. This first
assessment selects a reader; it does not by itself authorize a claim of improved
extraction meaning.

Cases: up to three actual references per upstream probe, original publisher XML
context, and missing/ambiguous/edition-mismatch controls. Preserve source files,
hashes, dates, exact target text and API outputs. Catalog absence must remain
distinct from missing local data or a source-format limitation. These selected
cases are diagnostic, not a general retrieval benchmark.

Held constant: no network/model calls, new dependency, corpus rebuild, prompt or
extraction-default changes. Local pinned artifacts and the current installed
reader checkpoint. Stop each probe after its declared cases and record blockers.

Decision rule: a viable path supplies exact target text, source identity/version,
and a selector or occurrence that can be checked independently. Repeated labels,
multiple editions and unresolved readings cannot select an arbitrary winner.
Use current Rulespec evidence and upstream loaders; add no parallel catalog or
source schema. If multiple document sources are needed, evidence must be checked
against its own source rather than the requesting document's offsets.

Prior evidence: the R15/R16 expanded-context model comparison failed its meaning
gate. The combined retrieval index also regressed. This work evaluates useful
source navigation/context after retrieval; it does not revive either failed
intervention or equate more available text with better model understanding.

## Optional consumer comparison — declared before implementation

Decision: connect supplied USLM reference sources to the normal `references` and
`discovery-export` commands, using the existing reader and evidence records.

Hypothesis: explicit target lookup improves source navigation without a model
pass. Supplying the containing section once makes the parent condition available
without asserting that every nearby clause governs the cited provision.

Arms: installed CFR-range checkpoint with no external bodies versus the same
scan with explicitly supplied, pinned USLM sources. Defaults must agree apart
from recorded parser/module fingerprints when supporting code moves.

Cases: the saved actual 5 USC 553(b)(B) source and pinned title 5 release; the
38 USC 4301 et seq. refusal; constructed missing targets, duplicate identifiers,
multiple editions, same readable text in different XML, conflicting publisher
and text targets, qualified ranges/notes, altered pins and inserted whitespace.
Use the existing source probe pins and original XML. These are development
cases; no general extraction-accuracy claim follows.

Held constant: existing model output, source passages, extraction defaults,
reader grammar and dependencies; zero network/model calls. Parse each supplied
source once per scan, index once, and serialize each containing section once.
No whole-title output or automatic transitive expansion.

Decision rule: adopt only if both commands expose the exact target with its own
source identity, XML selector, digest and available publication metadata; preserve
parent context and ambiguity; reject altered source pins; leave unsupported or
refused qualifications unresolved; preserve existing default results and pass
source/installed tests. A located target remains edition_match=not_established.
Multiple supplied editions must not silently choose one. eCFR DIV input remains a
separate upstream-reader gap, not falsely accepted as USLM.

Observation correction: the first full-document comparison stopped on an
incorrect harness expectation of two 553(b)(B) mentions. Raw review found three
(two in the probe excerpt, one later in the same document), plus a section-only
553 mention. All original observations remain in *-02-incomplete/. The target,
context, preservation and ambiguity gates are unchanged; the corrected check
accounts for all three written pinpoint occurrences.
