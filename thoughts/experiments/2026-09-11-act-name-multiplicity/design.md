# Preserve the laws behind a popular act name

Decision: whether RefSpec's existing act-name loader/resolver must retain more
than one source identity, and the smallest change that lets Rulespec consume it.

Observation: the producer documents names associated with two laws, while the
loader uses independent first-row selections for law and division/page data.
The frequency and actual lookup consequences have not yet been measured here.

Hypotheses:

- H1: changing source-row order changes selected law, scope or USC answer for
  some repeated names. Retaining the source alternatives should remove that
  order dependence without guessing which law a citation means.
- H2: duplicates sometimes repeat the same identity. Exact duplicate evidence
  should not create ambiguity; different laws or divisions must remain distinct.
- H3: a division explicitly stated in a citation can sometimes narrow the
  candidates. Missing division information cannot exclude a candidate, and a
  contradictory division must not become a selected answer.

Arms: current loader/resolver in original versus reversed name-row order; then
source-preserving loader/resolver on the same inputs and mutations. Retain the
replaced checks as a test-only oracle. Inspect raw publisher context before
choosing the final result fields; reuse existing types and source evidence.

Cases: census all pinned popular-name rows for multiple laws, scope differences,
duplicates and alias edges. Select up to 20 classified sections per affected law,
plus an absent section, bounded at 2,000 native queries. Include unique-name,
alias/year spelling, duplicated-row, unknown-division and conflicting-division
controls. Replay the saved 8,174 policy queries separately for compatibility.
Locate any affected real publication fields; source-derived diagnostic queries
are not attested document mentions or independent accuracy labels.

Held constant: pinned source artifacts, source-credit tables, classifier and
existing composition policies, model schemas and extracted statements. No model
calls, source downloads or index rebuilds are needed. Reuse existing loaders,
grammar, sparse application output and package verification paths.

Decision rule: adopt only if all declared alternatives retain their paired
law/division evidence, row order cannot select a winner, duplicate rows do not
invent ambiguity, unrelated results retain their prior fields, and source and
installed application output agree. Enumerate intended divergences. A resolved
identity is not proof of semantic completeness or target-edition applicability.
If existing data cannot settle an identity, preserve candidates and the reason;
do not narrow the requested outcome to suppressing every uncertain lookup.

## Source-informed implementation decision, before the intervention

The census found 34 multi-law names, 42 names with differing law/division/page
records, and no multiple alias edges. The existing popular-name builder
reproduces all 20,865 frozen rows after the loader's existing normalization.
Reuse its `PopularNameRecord` by moving that type into the runtime module and
importing it from the builder. No new parser or index artifact is needed.

Keep the existing unique-key lookup, but store no selected key for a multi-law
name. Retain competing source records and run the existing resolver separately
for each compatible law/division. Return their existing `ActResolution` results
as candidates when no source-supported discriminator selects one. This preserves
potential USC targets instead of replacing every ambiguous lookup with an empty
refusal. Ordinary results gain no populated candidate arrays. Same-law records
with only different page metadata are not different law/division identities.

Original versus reversed loading changed 889/1,056 diagnostic results, including
335 selected identifiers. The 48 relevant publication fields contain four unique
written forms, only one with a section. Keep those populations separate.

## Findings during consumer verification

The calendar consumer also used the first law to supply an enactment year.
Simply withholding the law key drops all multi-law names there, even when their
sources agree on the year. The follow-up reuses the existing date lookup for
each law and supplies a year only when every law has a known, identical year.
Retain the old helper as an oracle; enumerate changed names and keep ordinary
spelling controls. This follow-up was identified during caller verification,
not part of the original row-order comparison's preregistration.

The first ad hoc inspection of that consumer failed while displaying a session
law (`1914:255`) as a public-law pair: `ValueError: invalid literal for int()`.
No result file was written. The saved inspection script uses the existing
public-law key predicate to distinguish those source formats.
