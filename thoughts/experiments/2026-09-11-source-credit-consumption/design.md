# Exercise source-credit resolution through the application

Decision: whether the existing optional source-credit connection delivers its
additional mappings and preserves meaningful disagreement through Rulespec's
reference and discovery outputs; fix missing information upstream if needed.

Hypotheses:

- Earlier `no_key` results were a selection effect: those acts lacked a usable
  division key. The owner's PIPES Act / SECURE 2.0 specimens should supply real
  source-credit-only answers without a new parser or lookup implementation.
- The native resolver refuses conflicting source answers, but its current result
  exposes only `sources_disagree`, not the two competing identifiers. Compare
  native results, underlying source rows and exported application data to locate
  the loss before extending any shape.
- A consumer-only loss would instead leave the competing readings available in
  native output. If that is observed, fix only the adapter.

Arms: existing act-index-only lookup versus the same lookup with the pinned
source-credit index. If information is lost, compare the smallest upstream change
on the same inputs. Keep recognition, model outputs and evidence code fixed.

Cases: select at most two distinct existing Unified Agenda authority fields for
each PIPES Act of 2020 / SECURE 2.0 Act of 2022 specimen. Keep full fields and
source rows. Inspect a bounded set of existing named-act authority pairs (at most
2,000 distinct pairs) for a real native conflict; retain the inspection result
whether or not one exists. Include constructed agreeing, conflicting, absent,
multi-target and wrong-division controls, clearly labeled as such. Do not mutate
the published source artifacts to manufacture a real conflict.

Held constant: verified index receipts/files, all source bytes, current installed
reader settings and one deterministic scan per compared input. No provider calls,
new dependency, downloads or corpus rebuild. Load indexes once per diagnostic
scan; use existing callable loaders, readers and resolver.

Gate: actual positive source fields gain the source-credit-supported identifier;
conflicts and missing/ambiguous keys never become a selected target. Original
source, native uncertainty and source identity survive both commands and discovery.
If conflict details are added, keep them sparse and retain existing outcomes;
the old resolver remains a copied test-only oracle. Source/consumer tests and
rebuilt-wheel checks must pass before updating the working environment. If no
real conflict is present in the bounded population, say so and use the constructed
counterexample only to establish adapter behavior.

This does not establish the mapped provision's text, legal applicability or
historical edition. The broader reuse and local-reference work remains open.

## Baseline findings and next isolated change

The three selected fields confirm a real source-credit-only SECURE section 303
mapping, while section 127 remains unresolved and reports four source-credit
targets through the native `multi_target` status. None of the 608 existing
nonempty named-act/section pairs produces `sources_disagree`; a conflict check
therefore needs a labeled constructed counterexample, not a claim of real conflict.

The raw PIPES field writes `sec. 103 of the 2020 PIPES Act`. Its native key and
source-credit mapping work, but the occurrence reader does not recognize the
year-first spelling. RefSpec's existing Unified Agenda `_act_prose_recoveries`
already performs this exact reordering. Reuse that operator in the native grammar
and make both callers share it. Preserve the raw name and offsets; only admit the
reordered key when the supplied name set contains it. Exact indexed spellings take
precedence; wrong years, unknown names, name changes and sentence boundaries remain
controls. This is a recognition change, separate from changing resolution policy.

Further observed data gaps: native disagreement output omits both competing
identifiers, and a `multi_target` answer omits the existing `SourceCreditTarget`
rows. The SECURE 127 Table III row is on page 4660, outside its named division T
starting at 5275; the existing range exclusion only runs for multi-row lookups.
Keep these findings visible and test their changes separately from spelling reuse.

The evidence-only change reuses `SourceCreditTarget` for multi-target rows and
retains source-labeled conflicting identifiers only on `sources_disagree`.
Ordinary resolutions gain no populated fields. Rulespec's existing sparse-value
helper handles tuple sequences so absent fields inside these native records stay
absent in JSON. Compare all original resolution fields against a frozen resolver
on every selected pair; this intervention deliberately does not change resolution
policy. Constructed controls also expose the existing policy that a single Table
III answer may coexist with multi-target source credits; record whether the real
bounded population has that outcome before deciding a policy change.

## Isolated export-boundary repair

Decision: how to export source passages when preparation inserts separators.
The original `cli/commands.json` captures the failure before this change.

Hypothesis: source passages include inserted blank lines, while source evidence
correctly refuses them. The exporter assumes every exact prepared-text span is
original source. Intersecting passage evidence with the existing source map should
retain all original characters without changing passage text, IDs or hierarchy.
Merely skipping an unavailable whole-passage fragment would lose usable evidence;
removing the source map would falsely certify inserted text.

Arms: the saved failing exporter versus source-map-bounded source evidence,
with existing exact evidence verification shared by every discovery mode.
Do not relocate a supplied quotation or trust a preexisting fragment ID without
checking its coordinates/source support.

Cases: the actual three-field CLI fixture; original versus inserted whitespace;
inserted text inside a passage; adjacent source slices from different sources;
all-inserted passages; repeated Unicode text; incorrect quotation coordinates and
an inserted quotation with a supplied fragment ID. All controls are constructed.
Hold reference readers, indexes, statements and passage boundaries constant.

Gate: every original source character remains covered by source evidence, no
inserted character is cited, source text/passages/identities remain unchanged,
and existing ordinary exports retain their content. All three installed commands
must pass on the original fixture, followed by earlier reference replay checks.
No model calls. Stop this repair when those deterministic checks settle it; it
does not resolve either remaining named-act policy question.
