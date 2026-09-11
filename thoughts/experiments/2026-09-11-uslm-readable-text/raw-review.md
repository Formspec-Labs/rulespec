# Application output review

Reviewed the three captured XML sources, prepared text, reference scans, shared
targets and discovery exports in `application-direct/`. The CLI fixture deliberately
has no extracted claims and no provider response: it tests source-only navigation
and export, not extraction completeness. `check_application.py` retains the steps.

| Capture | Publisher links | Present targets | Associated text readings | Other text rows |
| --- | --- | --- | --- | --- |
| Title 5 section 423 | 30 | 1, editorial note | 16 | 2 overlapping public-law readings |
| Title 42 section 242c | 40 | 1, editorial note | 33 | 1 overlapping public-law reading |
| Title 5 sections 302/5721 | 37 | 1, operative reference | 24 | 1 overlapping public-law reading; 1 false RIN candidate |

The 107 publisher links comprise 10 operative, 19 source-credit and 78 note
occurrences. Three targets exist within these selections; 104 remain explicitly
outside them. Target lookup does not establish applicability or absence elsewhere.
The exporter retains every decoded source character and excludes inserted formatting
from evidence. Original UTF-8 XML matches the capture bytes. The three XML-evidence
graphs validate through Core. Source and isolated-wheel runs produce 24 identical
JSON artifacts; parser module hashes also match. Test details remain in their logs.

## Meaningful source content survives navigation

The fresh reference in 302(a), “section 5721 of this title,” reaches the complete
supplied section. Its agency definition retains nine listed categories and the
exclusion “but does not include a Government controlled corporation.” The target
also contains other definitions, source credits and notes. A later context selector
must decide which parts are needed; locating the whole section does not make all
of those parts conditions on the referring sentence.

The two editorial links reach 423(a) and 242c(a), respectively. Their target text
retains the Inspector General pay provision, its notwithstanding lead-in and bonus
prohibition, and the CDC appointment/ATSDR duties. Note links remain labeled notes;
they are not promoted into operative relationships.

## Remaining observed defects and limits

- Four public-law text readings lie within publisher labels beginning with a
  section reference, such as “section 3 of Pub. L. 95–452.” The current association
  requires the same start position, so these remain separate rows. They preserve
  their evidence but repeat a mention. Broader containment-based association needs
  nested/overlapping-anchor and multiple-reading controls before replacing this
  rule. Do not merge based only on a normalized identity.
- The fresh amendment heading `1998—Pars.` yields SpicySearch RIN `1998-PARS`.
  This is a false identifier reading, not a publisher link. The existing RIN scanner
  admits a four-digit prefix and four-character letter/alphanumeric suffix after
  dash normalization. A bounded upstream comparison should examine its query versus
  extraction semantics and the stricter existing canonical RIN helpers. Preserve
  this real-source counterexample; do not hide the row only for USLM inputs or
  silently change permissive query behavior.
- No real rejected text readings occur in these three captures. The constructed
  `99 CFR 1.1` control verifies that association retains its native impossible-title
  refusal and that discovery shares its exact evidence. A constructed native/text
  law-number disagreement also retains both observations, without a selected winner.
- Original inter-element blank runs remain. Tables retain source order and cell
  boundaries, not a faithful visual table rendering. The native reader's documented
  skip/refusal behavior remains visible in `publisher_skipped`.

These limitations are separate from the source-preparation and navigation checks.
The next quality comparison needs fresh documents and fixed consumer questions;
these three sources are now development controls. No model accuracy or cost change
was measured here.
