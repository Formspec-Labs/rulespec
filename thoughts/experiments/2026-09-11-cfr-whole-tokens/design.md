# Whole CFR tokens and source-defined parts

Decision: determine which existing source signals let RefSpec retain a complete
CFR part or range without inventing a different identifier, before migrating the
remaining graph callers. Include the existing identifier minter in the trace.

Observed failures: RefSpec truncates `41 CFR 101-1` to part 101; SpicySearch's
strict reader retains the token but refuses its compound/range meaning. The
RefSpec minter deliberately refuses complete compound parts. The current XML
also uses `TYPE="PART"` for reserved *ranges*, so that attribute alone cannot
establish a single-part index.

Hypotheses:

1. Whole-token retention with a title-specific compound reading can recover the
   title 41 cases without an external lookup. Plural labels alone cannot distinguish
   a compound-part list from a range. Explicit range connectors must survive.
2. A source index can help, but indexing every XML `PART` value introduces false
   identities for reserved ranges. Source headings and child sections must agree
   with the claimed single-part meaning. A part absent from this dated source
   is unresolved, not proof of an invalid historical citation.
3. The stored OFR index can identify compound parts for tagging, but it cannot
   by itself recover source occurrence boundaries, section pinpoints or ranges.

Arms: RefSpec at `566df1d4`; SpicySearch strict reader at `10824d4`; an experiment
combining complete native tokens with the title 41 compound convention; the
existing OFR part index and publisher XML used separately as corroborating source
evidence, not silently merged into a production roster.

Cases: inspect original paragraphs and hierarchy from the pinned title 41, 40,
16 and 48 XML files. Include bare/singular/plural compound forms, actual numeric
ranges, compound-section ranges, ordinary lists, malformed tails, case/Unicode
spacing, historical-title controls and neighbors from other citation families.
Use all 8,424 stored OFR part keys only as constructed shape controls. Newly
selected cases and labels are development data, not independent accuracy rates.

Held constant: no model calls, no fetch or corpus rewrite. Verify source hashes,
retain exact XML selections and copied prior checks before any production edit.
Stop the comparison once each hypothesis is distinguished or an unresolved case
shows why a proposed representation cannot be adopted.

Decision rule: a production change must preserve complete source occurrences and
all stated endpoints, keep ordinary parts and list context unchanged, avoid
minting an ambiguous/range reading as a single identifier, and survive source plus
mutation checks. A title/index-only improvement does not pass that complete
representation gate. Record any narrower useful adoption as a separate decision,
with the full requirement still open. Reuse existing schemas, readers and source
evidence throughout; add no parallel index loader merely for this experiment.
