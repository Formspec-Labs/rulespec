# Keep every source identity behind an act name

Implemented upstream in RefSpec and installed in Rulespec on 2026-09-11. A
popular act name no longer selects a law because its row appeared first. Each
compatible law/scope keeps its lookup result, including possible USC targets and
refusals. A stated division can narrow the alternatives when the source supports
that distinction. The extraction prompt and Core schemas are unchanged.

## What the evidence established

The [design](design.md) separates row-order dependence, duplicate records and
explicit division context. The [census](census.json) finds 34 normalized names
associated with multiple laws and 42 names with differing law/division/page
records. Forty-one have distinct law/division identities; a page-only difference
does not create a second identity. No competing alias edges were found in this
particular index. These findings do not establish that aliases are universally
unambiguous.

The existing RefSpec popular-name builder reproduces all **20,865** frozen rows
after the loader's existing normalization. Its captured publisher HTML is a
later capture of the same release point, not the original artifact's exact HTML
bytes. [Publisher context](publisher-context.json) records its digest, exact HTML
entry offsets, raw markup and visible surrounding text for 44 entries covering
the affected names.

- **Detainee Treatment Act of 2005:** the publisher lists PL 109-148, division A,
  title X, and PL 109-163, division A, title XIV. With section 1003, the old loader
  selected USC 42:2000dd in one row order and no classification in the other.
  The new result retains both source identities and the possible USC target.
- **Adult Education and Family Literacy Act:** the same entry states laws from
  1998 and 2014, with different USC title references. They are not duplicate rows.
- **CARES Act and 21st Century Cures Act:** entries separately cite an entire
  law and a division or narrower part of it. An unstated division is not evidence
  that a conflicting, more specific scope can be discarded.
- The saved publication table has 48 fields involving affected names but only
  four distinct written forms. Only one names a section: section 4116 of the Food,
  Conservation, and Energy Act of 2008. Both law candidates remain unclassified
  for that section in these tables; the new output makes the competing laws visible.

| Comparison | Examined queries | Changed original result fields | Previously selected USC targets lost from all candidates |
| --- | ---: | ---: | ---: |
| Old loader: original versus reversed row order | 1,056 | 889, including 335 selected-identifier changes | Not an adoption measure |
| New loader versus old, diagnostic queries | 1,056 | 1,012 | 0 |
| New loader versus the previous policy checkpoint | 8,174 | 26 | 0 |

Every new result is identical with original and reversed name-row order.
[The comparison](comparison.json) retains every before/after result. The 26
changes in the prior population all concern competing name identities. Other
original fields agree with the copied prior loader/resolver. The added fields
are explicitly excluded from old-field parity, then checked independently.
The two populations overlap and must not be added into an independent-case count.
These are deterministic lookup checks, not general document-accuracy estimates.

## What was reused and changed

- Move the existing builder's `PopularNameRecord` into the runtime module and
  import it from the builder. The producer and consumer use the same record type;
  no new popular-name parser, artifact schema or data rebuild is needed.
- The existing name-to-law map keeps a unique law or `None` for multiple laws.
  Only names with competing law/division identities retain extra source records.
  Law, division, volume and page remain paired. Duplicate records do not multiply
  candidates, and candidate ordering is deterministic.
- Reuse `ActResolution` for each candidate's lookup through the existing Table
  III and source-credit rules. The parent returns `act_name_ambiguous` instead of
  choosing a candidate. `name_sources`, `candidate_resolutions` and `act_division`
  expose the source alternatives and the scope used. Unknown division information
  cannot exclude a record; an explicitly stated division can combine compatible
  same-law records or rule out a contradictory record.
- Rulespec uses its existing sparse serialization and shared source evidence.
  The adapter removes the repeated written citation from child lookup results.
  Default discovery records and extracted statements remain unchanged.
- The existing calendar consumer now checks every possible law before supplying
  an enactment year. Three multi-law names retain their common year. Eight with
  differing years lose the previously arbitrary year: **3,999 → 3,991** dated
  names and **11,952 → 11,928** added spelling variants. Existing non-year
  spellings are unchanged. [The full difference list](enactment-years.json) retains
  the source law dates. This caller follow-up is separately identified in the design.

The added name processing is linear in popular-name rows apart from sorting the
small sets of competing records. Ordinary lookup remains a map lookup plus its existing
classification work; ambiguous names perform one lookup per compatible identity.
The new path shares the loaded classification and credit tables. It does not
reload them per candidate or traverse references recursively.

## Checks and delivery

- [448 upstream tests](owner-final.log) and [42 selected downstream tests](caller-final.log)
  pass, including builder reproduction, duplicate rows, unknown/conflicting division
  context, aliases, year spelling and the calendar consumer. The original failure
  logs remain. Copied prior checks are test-only oracles.
- [497 source extractor tests](application-source.log) and
  [497 installed extractor tests](application-current.log) pass. The existing
  deprecation warnings remain; these checks are not semantic completeness claims.
- [Wheel results](comparison-wheel.json) equal the source comparison exactly.
  Seven CLI fixture/output files match between source, isolated wheel and working
  installation. Three source commands, six isolated-wheel commands (including the
  earlier five-case policy fixture), and three working-installation commands pass
  outside the checkout. Both dependency checks pass.
- Three additional [installed-reader controls](division-consumer.json) confirm
  that a division explicitly attached to the act narrows the identity, while an
  absent division or a nearby division belonging to another provision does not.
  The first probe incorrectly expected the unstated native `reading.division`
  key to be omitted; it is JSON null. Correcting that assertion changed no code
  or output data. The retry capture preserves all three inputs and scans.
- [Package receipt](verification.json) pins six wheels and checks seven runtime
  modules against source. [Working installation receipt](current-verification.json)
  checks the same modules and command outputs in `.tools/document-poc-venv`.
  The isolated environment is `.tools/reference-integration-20260911-names`.

No model calls, downloads, corpus rebuilds, commits or publication occurred.
Changes are locally implemented and installed, with original captures preserved.

## Remaining limits

An explicit law number or enactment year could sometimes identify one candidate,
but this application does not yet bind that surrounding context to a named-act
mention. Missing table classifications cannot prove that a provision does not
exist. The index does not model every title/subtitle boundary, map an act pinpoint
to a USC pinpoint, or establish a target's edition or applicability. Even when
candidate lookups share a USC identifier, the competing act identities stay
visible; no identity is selected by agreement alone.

Those limits remain in R13 and the source/context tasks in the
[canonical task list](../../plans/2026-09-10-reference-integration-task-list.md).
Qualified USC, local paragraphs, vocabulary and fresh extraction-quality work
remain part of the wider reuse objective.
