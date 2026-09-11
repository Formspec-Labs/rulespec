# Whole CFR tokens: useful reuse, complete-range gate still fails

The smallest token patch recovers all 189 compound part keys missed by RefSpec,
but it is not a complete production fix. It still loses explicit range endings,
flags five real compound parts as implausible, and leaves compound identifiers
unmintable. The production parser is unchanged by this experiment.

[Design](design.md), [exact publisher XML cases](source-cases.json),
[raw source results](source-results.json), [counterexamples](controls.json) and
[summary](summary.json) retain the evidence. `baseline.py` is copied from RefSpec
`566df1d4`; SpicySearch `10824d4` supplies the existing strict token. The probe
reuses that token in the existing RefSpec patterns and allows RefSpec to judge
digit length, instead of stopping at four digits. Its title-based meaning label
is experimental, not a production parser verdict.

## What the comparison showed

| Measure | Current RefSpec | Whole-token probe | SpicySearch strict |
| --- | ---: | ---: | ---: |
| Complete observed part token, 8,424 constructed OFR index strings | 8,235 | 8,424 | 8,414 |
| Wrong or missing complete token | 189 | 0 | 10 |

These counts include refused observations. In particular, SpicySearch retains
189 compound tokens but refuses their meaning. They are shape checks against
index keys, not accepted-reference or prose-accuracy rates. All raw results are
in `index-results.jsonl.gz`, with the index hash in `summary.json`.

Eight original XML citation cases have four formatting/neighbor variants each;
twelve additional controls are constructed. Manual review found:

- `41 CFR parts 102-193 and 102-194` names two compound parts. The existing
  plural-label rule returns no part; whole tokens recover both. But the
  plausibility check counts six digits across each hyphen and rejects them.
  The other affected index keys are `102-117`, `102-118` and `102-192`.
- `41 CFR parts 300-3, 301-10, and 301-70` needs RefSpec's existing list-context
  handling as well as whole tokens. SpicySearch alone returns only the first.
- `41 CFR 101-19.600 to 101-19.607` still loses `.607`; `40 CFR parts 1500
  through 1508` still becomes a mintable part 1500. Fixing a token does not fix
  the scope of the citation.
- `41 CFR 60-1-60-2` shows why a title-41 rule cannot simply bless every hyphen
  chain. The experimental label calls it a compound; the existing minter
  refuses it. An unresolved chain must not become a single accepted target.
- Five-digit `5 CFR part 10001` is retained by RefSpec and missed by the
  SpicySearch strict token. Invalid titles, historical title 35, lettered parts,
  neighboring USC citations and the compilation guard retain their behavior.

## XML supplies evidence, not automatic interpretation

All selected title XML hashes match their saved publisher manifest. The original
paragraph bytes, their file offsets and surrounding markup are retained. This
uses XML as source evidence; it does not claim Rulespec's USLM loader accepts the
different eCFR format.

The five inspected title files contain 2,210 `TYPE="PART"` nodes. Of these, 167
have plural `PARTS ...` headings, often reserved ranges such as `30-31` and
`50-1 - 50-200`. Indexing every node number as one part creates false identities.
Conversely, title 41 contains `PART 102—GENERAL [RESERVED]` with no sections:
requiring child sections would lose a stated singular part. Older minter prose
generalizes the OFR index when it says no hyphen head exists independently.
Preserve that historical claim as a correction target, not current authority.

The existing OFR index, original headings, source-note readers and source-target
inspection APIs can corroborate parts. None independently supplies complete
occurrence boundaries or proves the target governs a rule. Absence from one
edition does not invalidate a historical citation. No new index loader was added.

## Production sequence selected after independent assessment

[Range representation review](../../reviews/2026-09-11-cfr-range-representation.md)
and [consumer trace](../../reviews/2026-09-11-cfr-range-consumers.md) independently
confirm that grammar and consumers must change together. The first recommends a
small range object reusing two existing `CfrCitation` endpoints; the second maps
the field-copying paths that must preserve or explicitly refuse that scope.

1. Use one item-reading path for complete coordinates, pinpoints, explicit
   range endpoints and following list members. Preserve incomplete/ambiguous
   tails as refusals. Do not enumerate the interior of a range.
2. Give a range an explicit representation that cannot silently masquerade as
   its first endpoint. Reuse `CfrCitation` for endpoint coordinates; use no new
   Core identifier scheme for a whole range. Check mixed lists, cross-part
   sections, end pinpoints and following parentheticals.
3. Update live RefSpec consumers together: authority parsing, Unified Agenda
   typed rows and joins, part-note comparisons and term explanations. A range
   must not query, explain or mint only its first endpoint as the whole target.
4. Keep Rulespec's existing evidence/refusal machinery. Preserve `match.text`
   instead of reconstructing display text from the first part and section.
5. Then admit complete, supported compound parts in the existing minter and
   measure graph consumers before removing their duplicate parsers. No live
   `mint_cfr_iri` caller was found in the four source trees; existing graphs use
   other local helpers, so fixing this utility alone does not migrate them.

**Verdict:** bounded lexical improvement demonstrated; complete-range adoption
gate failed. No token/range production change, model call or deployment.
The independently discovered part-zero minter defect is tested and tracked in
[its own comparison](../2026-09-11-cfr-zero-parts/README.md); it does not satisfy
this range gate. R8 remains open.
