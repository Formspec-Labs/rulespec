"""Detect structured identifier candidates in free-text query strings.

``detect_identifiers`` scans one string (dash-normalized) for CFR, U.S.C.,
public law, executive order, Statutes at Large, RIN, Federal Register document,
and regulations.gov docket shapes, returning non-overlapping
``IdentifierCandidate`` values in query order. Detection is pure: no request or
engine state is mutated. CFR ``value`` is for exact comparison only (structure
lives in ``components``); unlabeled docket-shaped prose is refused unless it
has organization/year/sequence form. Helpers ``is_cfr_section`` and
``is_federal_register_document_number`` answer whole-string membership checks.
``unread_identifier_shapes`` identifies specific-looking query text that none
of those grammars can read, so a broad lexical fallback can explain its limits.

``classify_federal_register_document_number`` is a second, COLUMN-only
reader: the bare-legacy and X-family Federal Register forms RefSpec's
rulespec 0.2.0rc17/rc18 gave their own spaces (REF-064/065), mirrored
natively here -- no refspec import, per
``tests/search/test_metadata_package_boundary.py`` -- and reachable only
through a trusted ``document_number`` field paired with that same fact's
``publication_date``, never through free-text or a whole query string.

**SpicySearch mints no rkaf identity, and nothing in this module does.**
That is worth saying plainly because the surrounding names invite the
opposite reading. A "scheme" here is the NAME OF A SPACE, shared by every
document in it: ``09-19806`` and ``09-19807`` published the same day
classify identically, and so do ``X09-101207`` and ``X09-111207``. An
identity would be ``urn:rkaf:us:frdoc-legacy:09-19806:2009-08-19``, and no
production path in this repository emits one -- ``MetadataIdentifier``
carries a role-tagged raw value and its evidence, the served exact tables
key on the normalized string, and the query path never sees a scheme at
all. Minting stays RefSpec's, whose
``iri_minting.mint_federal_register_document_iri`` this repository calls in
exactly one place: ``experiments/identifier_census.py``, which is evidence,
not a serving path. Closing that gap needs a consumer that does not exist
yet; until one does, adding an IRI to a subject would be a column nothing
reads.

The classification IS consumed, at the catalog boundary and nowhere else:
``source_catalog_metadata.py``'s
``_validate_federal_register_document_identities`` reads each Federal
Register fact's OWN ``document_number`` together with its OWN
``publication_date`` -- the one column pair REF-052 calls trusted -- and
refuses an item whose two facts place ONE bare number in two different
qualified spaces. Consuming the answer is not storing it: nothing is
written, so nothing keys on a space, and a space is not an identity
anyway -- two documents sharing one still classify equal on purpose
(:class:`FederalRegisterDocumentClassification`). What that check can and
cannot see, including the cross-subject and cross-catalog collisions it
does NOT detect, is stated in its own docstring. See also
``classify_federal_register_document_number`` below.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from functools import lru_cache
from types import MappingProxyType
from typing import Any

from spicysearch.canonical import sha256_digest
from spicysearch.identifier_normalization import (
    IDENTIFIER_NORMALIZATION_POLICY_DIGEST,
    IDENTIFIER_NORMALIZATION_POLICY_ID,
    IDENTIFIER_NORMALIZATION_POLICY_VERSION,
    normalize_identifier,
)

#: Pins the conservative unread-identifier detector below. A pattern or label
#: change alters the warning shown to callers, so it must move this version.
IDENTIFIER_SHAPE_POLICY = "unread-identifier-shapes-v1"

_UNREAD_INSTRUMENT_LABELS = (
    "bulletin",
    "circular",
    "doc",
    "docket",
    "form",
    "publication",
)
_UNREAD_QUALIFIED_LABELS = ("code", "manual", r"no\.")
_UNREAD_QUERY_KEYWORDS = frozenset({"AND", "NOT", "OR"})
_UNREAD_NON_CITATION_ACRONYMS = frozenset({"DC", "EU", "IT", "UK", "UN", "US"})
_UNREAD_NEVER_A_LABEL = _UNREAD_QUERY_KEYWORDS | _UNREAD_NON_CITATION_ACRONYMS
_UNREAD_ACRONYM = r"[A-Z]{2,6}"
_UNREAD_DOTTED_ACRONYM = r"(?:[A-Z]\.){2,4}"
_UNREAD_ANY_NUMBER = r"\d+(?:[.-]\d+)*"
_UNREAD_STRUCTURED_NUMBER = r"\d+(?:[.-]\d+)+"
_UNREAD_GAP = r"[ \t]"
_UNREAD_LEAD = rf"(?:(?P<lead>{_UNREAD_ACRONYM}){_UNREAD_GAP})?"
_UNREAD_SHAPES: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?P<label>[A-Za-z]{2,}[A-Za-z0-9]*)"
        r"(?P<number>(?:[.-][A-Za-z0-9]+){2,})"
    ),
    re.compile(
        rf"\b{_UNREAD_LEAD}(?P<label>(?i:{'|'.join(_UNREAD_INSTRUMENT_LABELS)}))"
        rf"{_UNREAD_GAP}?(?P<number>{_UNREAD_ANY_NUMBER})\b"
    ),
    re.compile(
        rf"\b{_UNREAD_LEAD}(?P<label>(?i:{'|'.join(_UNREAD_QUALIFIED_LABELS)}))"
        rf"{_UNREAD_GAP}?(?P<number>{_UNREAD_STRUCTURED_NUMBER})\b"
    ),
    re.compile(
        rf"\b(?P<label>{_UNREAD_DOTTED_ACRONYM}){_UNREAD_GAP}?"
        rf"(?P<number>{_UNREAD_ANY_NUMBER})\b"
    ),
    re.compile(
        rf"\b{_UNREAD_LEAD}(?P<label>{_UNREAD_ACRONYM}){_UNREAD_GAP}?"
        rf"(?P<number>{_UNREAD_STRUCTURED_NUMBER})\b"
    ),
    re.compile(
        rf"\b\d+{_UNREAD_GAP}(?P<label>{_UNREAD_ACRONYM}){_UNREAD_GAP}"
        rf"(?P<number>{_UNREAD_ANY_NUMBER})\b"
    ),
)
_UNREAD_SHAPE_CACHE_SIZE = 512


class IdentifierKind(StrEnum):
    """Kinds of structured identifiers this module can detect."""

    CFR = "cfr"
    DOCKET = "docket"
    EXECUTIVE_ORDER = "executive_order"
    FEDERAL_REGISTER_DOCUMENT = "federal_register_document"
    PUBLIC_LAW = "public_law"
    REGULATIONS_GOV_DOCUMENT = "regulations_gov_document"
    RIN = "rin"
    STATUTES_AT_LARGE = "statutes_at_large"
    USC = "usc"


#: Which grammar wins when two of them claim exactly the same characters.  The
#: only real contest is a Federal Register correction number ("C1-2026-13078"),
#: whose shape a docket id also fits; the more specific grammar is listed first.
_KIND_PRECEDENCE = (
    IdentifierKind.CFR,
    IdentifierKind.USC,
    IdentifierKind.PUBLIC_LAW,
    IdentifierKind.STATUTES_AT_LARGE,
    IdentifierKind.EXECUTIVE_ORDER,
    IdentifierKind.RIN,
    IdentifierKind.FEDERAL_REGISTER_DOCUMENT,
    IdentifierKind.REGULATIONS_GOV_DOCUMENT,
    IdentifierKind.DOCKET,
)


@dataclass(frozen=True, slots=True)
class IdentifierCandidate:
    """One identifier a query appears to name.

    ``span`` indexes the *original* text, so a caller can highlight or excise
    exactly what it read.  ``value`` is the normalized surface form for exact
    comparison; ``components`` is the structure, and is authoritative whenever
    the two could disagree.
    """

    kind: IdentifierKind
    value: str
    span: tuple[int, int]
    components: Mapping[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": self.kind.value,
            "span": list(self.span),
            "value": self.value,
        }
        if self.components:
            payload["components"] = dict(self.components)
        return payload


#: Every dash spelling (hyphen, non-breaking hyphen, figure dash, en dash, em
#: dash, horizontal bar, minus sign) collapses to "-" before matching.  The
#: replacement is one character for one character, so a span computed against
#: the normalized text still selects the same characters of the original.
_DASHES = str.maketrans(dict.fromkeys("\u2010\u2011\u2012\u2013\u2014\u2015\u2212", "-"))

#: No identifier grammar here may start or end inside a longer token.
_LEFT = r"(?<![A-Za-z0-9_-])"
_RIGHT = r"(?![A-Za-z0-9_-])"

# RIN: four digits, dash, two letters, two alphanumerics (citations.py
# canonical_rin_iri validates the ``\d{4}-[A-Z]{2}\d{2}`` core after upcasing).
_RIN = re.compile(rf"{_LEFT}(?P<value>\d{{4}}-[A-Za-z]{{2}}[A-Za-z0-9]{{2}}){_RIGHT}")

# Federal Register document numbers (citations.py federal_register_identifier).
#: The one modern-form grammar this repository has.  ``canonical_frdoc_iri``
#: admits exactly this before it will mint ``rkaf:us-frdoc``, and it reads four
#: digits, not a year: the release adapter's link verification and identifier
#: mint import :func:`is_federal_register_document_number` rather than restate
#: it, so a document number cannot be modern-form for the query path and legacy
#: for the release path.
#: Tail widened from exactly five digits to three-to-five 2026-09-02, adopting
#: the platform contract (rulespec 0.2.0-pre.16, REF-056): the Office of the
#: Federal Register pads some years and not others, and a fixed five-digit
#: tail silently refused every shorter, equally real document number. ADOPTED
#: -- see docs/history/2026-09-02-identifier-divergences.md and tests/search/identifier_contract_exceptions.py.
FEDERAL_REGISTER_DOCUMENT_NUMBER = r"\d{4}-\d{3,5}"
_FR_STANDARD = re.compile(rf"{_LEFT}(?P<value>{FEDERAL_REGISTER_DOCUMENT_NUMBER}){_RIGHT}")
_FR_STANDARD_EXACT = re.compile(FEDERAL_REGISTER_DOCUMENT_NUMBER)
#: The LETTER-opening legacy form ("E7-21559"): a letter, one digit, a
#: hyphen, four or five digits.  Named ``_LETTER`` because it is not the only
#: "legacy" shape this module reads: :data:`_FR_BARE_LEGACY` below is a
#: DIFFERENT, unlettered family RefSpec calls "bare-legacy"
#: (``rkaf:us-frdoc-legacy``, REF-064) -- the two must never be conflated,
#: which is why this constant keeps its qualifier even though nothing else
#: in this module used to need one.  This form is safe in running text (the
#: leading letter disambiguates it from a docket or report number) and stays
#: read by both the prose detector and the exact-catalog query policy,
#: unchanged.
_FR_LEGACY_LETTER = re.compile(rf"{_LEFT}(?P<value>[A-Za-z]\d-\d{{4,5}}){_RIGHT}")
_FR_CORRECTION = re.compile(rf"{_LEFT}(?P<value>[Cc]\d-\d{{4}}-\d{{5}}){_RIGHT}")

# --------------------------------------------------------------------------- #
# Column-only Federal Register forms (rulespec 0.2.0rc17/rc18, REF-064/065).
#
# Everything above this point is what a QUERY may state -- typed as a whole
# search string via exact_catalog_identifier_value, or embedded in a sentence
# via detect_identifiers -- and neither reader gains a character from what
# follows. A bare pre-2010 number ("09-19806") is exactly as unreadable in a
# search box as it is in running text: unlabeled, it cannot be told apart
# from a docket number, a release number, "MM Docket No. 98-213". RefSpec
# reaches the identical ruling in its own prose reader and calls the fix
# "the column is the license" (REF-052): a value arriving from a TRUSTED
# document_number field needs no such inference, because the field already
# said what it holds. These two patterns are that column's license, mirrored
# natively here -- no refspec import, per test_metadata_package_boundary.py
# -- and reached only through source_catalog_metadata.py's per-fact field
# path (classify_federal_register_document_number below), never through a
# query.
#
#: The bare, unlettered pre-2010 form: a two-digit year, a hyphen, and a
#: one-to-six-digit sequence. "09-19806" and "00-1" are both real. Combines
#: RefSpec's own exported floor (``BARE_LEGACY_FEDERAL_REGISTER_DOCUMENT_
#: NUMBER``, three to six digits) with its sibling short-tail widening (one
#: to two digits) into the one range the ``rkaf:us-frdoc-legacy`` identifier
#: space itself admits.
_FR_BARE_LEGACY = re.compile(r"\A\d{2}-\d{1,6}\Z")
#: The self-dating X family, as ONE pattern rather than two.
#:
#: "X", a two-digit year, a hyphen, then a 5-to-7 digit tail read
#: RIGHT-ANCHORED -- the LAST FOUR digits are the month and day, everything
#: before them is the sequence -- a reading RefSpec verified against
#: 1,007,156 records with zero mismatches. The tail floor (5) and ceiling
#: (7) match rulespec's own ``rkaf:us-frdoc-x`` space
#: (``X[0-9]{2}-[0-9]{5,7}``) rather than only the shapes a corpus happened
#: to contain: a fixed five-digit tail would have stranded 206 real
#: six-digit-tail documents (REF-065). With month and day fixed at two
#: digits each, a 1-to-3-digit sequence IS a 5-to-7-digit tail, and the
#: split is unique for any tail length -- so the anchoring is a property of
#: the pattern, not of matching order.
#:
#: **One pattern on purpose.** This used to be two -- a bounded membership
#: regex beside an unbounded ``\d+`` spelling regex -- and they disagreed:
#: ``X09-12340101`` (eight-digit tail) was refused by
#: :func:`is_federal_register_document_number` and accepted by the scheme
#: decision, which with a mismatched date could then raise and break a
#: catalog build on a value the module says it cannot read. A single
#: pattern makes that class of disagreement unrepresentable.
_FR_X_SPELLING = re.compile(
    r"\AX(?P<year>\d{2})-(?P<sequence>\d{1,3})(?P<month>\d{2})(?P<day>\d{2})\Z"
)

#: The four rulespec schemes a Federal Register document number can be
#: CLASSIFIED into -- named once so
#: :func:`classify_federal_register_document_number` and the query-path
#: candidate builder below never spell them differently. A scheme names a
#: space, never a document: every value in one shares it.
FEDERAL_REGISTER_DOCUMENT_SCHEME_MODERN = "rkaf:us-frdoc"
FEDERAL_REGISTER_DOCUMENT_SCHEME_LEGACY = "rkaf:us-frdoc-legacy"
FEDERAL_REGISTER_DOCUMENT_SCHEME_X = "rkaf:us-frdoc-x"
FEDERAL_REGISTER_DOCUMENT_SCHEME_PARTNER = "rkaf:partner-defined"

# regulations.gov docket ids: an organization path plus the year and sequence
# that make a token recognizable as a docket rather than as any other
# hyphenated uppercase string.
#: The leading token is an agency code, so it is capped the way citations.py
#: ``_DOCKET_LABEL_PREFIX`` caps one: two to six letters ("EPA", "FSIS",
#: "USCIS", "DOC").  Without the cap "letter then anything" reads a hyphenated
#: English word as an agency, and "documentation-2021-0317" mints docket
#: DOCUMENTATION-2021-0317.  Later path segments keep the looser shape, because
#: a real docket writes office and program codes there ("EPA-HQ-OAR", "AMS-SC").
#:
#: **This constant is deliberately unfenced, and the bare-docket pattern does
#: not use it.** ``_DOCKET_BARE`` uses
#: :data:`_DOCKET_ORGANIZATION_NO_TRAILING_YEAR` below, which forbids a
#: trailing four-digit segment so a Regulations.gov document id cannot be read
#: as a docket.  The labelled forms keep this looser spelling because their
#: label already disambiguates them.  Grepping this name alone therefore shows
#: no fence and is not evidence that one is missing -- see the derived constant
#: and ``test_a_regulations_gov_document_id_is_not_also_a_full_span_docket``.
_DOCKET_ORGANIZATION = r"[A-Za-z]{2,6}(?:[-_][A-Za-z0-9]+)*"
#: An organization may not END with a bare four-digit segment: that segment is
#: a year, and the reading which absorbed it is a Regulations.gov *document*
#: misread as a docket.  Without this fence ``EPA-HQ-OAR-2006-0894-0021``
#: matches ``_DOCKET_BARE`` over its full span with
#: ``organization="EPA-HQ-OAR-2006"``, ``year="0894"`` -- the identical span
#: ``_REGULATIONS_GOV_DOCUMENT`` claims, which left ``_KIND_PRECEDENCE`` as
#: the only thing choosing between them.  Precedence is a tiebreaker, not a
#: correctness mechanism: if the document pattern ever narrowed relative to
#: this one, the docket candidate would survive and its ``components`` --
#: authoritative per :class:`IdentifierCandidate` where value and components
#: could disagree -- would state a year of "0894".  The fence makes the two
#: shapes disjoint, so precedence goes back to breaking ties.
#:
#: Bounded to the LAST segment deliberately, measured 2026-09-02 over the
#: 608,758 distinct pinned ``docket_ids_json`` values: it stops 161 values
#: matching, every one a Regulations.gov document id that was being read as a
#: docket, and costs no real docket.  The two tighter fences considered both
#: cost real data: letters-only organizations lose 6,805 (``EPA-R09-OAR-2009-0958``
#: -- region codes carry digits), and requiring every segment to contain a
#: letter still loses 168 (``CERCLA-04-2012-3766``).
#:
#: **Extended 2026-09-05 to also refuse a trailing ``FRDOC`` segment,
#: case-insensitively.** The digit fence alone does not cover a Regulations.gov
#: *document* under the year-less ``AGENCY_FRDOC_0001`` docket family (see
#: :data:`_DOCKET_FRDOC` below): ``NOAA_FRDOC_0001-5462`` backtracks past the
#: four-digit fence (its trailing ``0001`` IS a bare four-digit segment and is
#: already refused there) to ``organization="NOAA_FRDOC"``, which does not end
#: in digits and so was NOT refused -- producing ``year="0001"``,
#: ``sequence="5462"``, a docket claim over a document id, for exactly the
#: reason this whole fence exists.  "FRDOC" is not an office code any agency
#: writes for any other reason -- it is the literal anchor RefSpec's own
#: column reader (``_REGSGOV_DOCKET_SHAPE``) uses for the year-less family --
#: so refusing an organization that ends on it costs nothing a real docket
#: would state.  This repository has no production-scale docket population to
#: re-run the 608,758-value measurement above against; see
#: ``test_identifiers.py`` and the identifier-census receipt cited in the
#: commit message for what was actually measured this round.
_DOCKET_ORGANIZATION_NO_TRAILING_YEAR = (
    rf"{_DOCKET_ORGANIZATION}(?<![-_]\d{{4}})(?<![-_](?i:FRDOC))"
)
#: The office or program code an agency writes between the year and the
#: sequence: "FDA-2011-V-0020" (office "V"), "DOD-2008-OS-0081" (office
#: "OS"), "FDA-2026-N-0008" (office "N").  Ported from RefSpec's own
#: ``_DOCKET_OFFICE`` (``identifier_shapes.py``), mirrored natively here the
#: same way the Federal Register column forms above are -- no refspec import,
#: per ``tests/search/test_metadata_package_boundary.py``.
#:
#: This is the dominant docket shape this module could not read at all before
#: 2026-09-05: an office/program code sits between a real docket's year and
#: its sequence, and without anywhere for those letters to go, neither
#: ``_DOCKET_BARE`` nor ``_DOCKET_LABELED`` matched the docket -- not "matched
#: it wrong", simply refused it outright, the same silent gap
#: :data:`_DOCKET_FRDOC` closes for the year-less family below.
#:
#: LETTERS ONLY, and that is the whole of the fence, ported along with the
#: group: a segment that could carry digits reads
#: "EPA-HQ-OAR-2021-0317-0001" as organization-year-office-sequence, turning
#: every Regulations.gov *document* id into a docket claim, because letters
#: cannot spell "0317" -- digits can. The group is optional, so a docket that
#: states no office reports none in ``components`` rather than an empty
#: string.
_DOCKET_OFFICE = r"(?:(?P<office>[A-Za-z]+(?:[-_][A-Za-z]+)*)[-_])?"


def _docket_body(organization: str, year: str, sequence_group: str = "sequence") -> str:
    """Organization, year, office, sequence -- the shape ``_DOCKET_BARE``,
    ``_DOCKET_LABELED``, and ``_REGULATIONS_GOV_DOCUMENT`` all share.

    Extracted so :data:`_DOCKET_OFFICE` is read identically by every grammar
    that wants it rather than hand-copied into each -- the same drift this
    module's other shared fragments (``_LEFT``/``_RIGHT``, ``_DOCKET_LABEL``)
    already exist to prevent -- and named after RefSpec's own ``_docket_body``
    helper (``identifier_shapes.py``), which this mirrors for the same
    organization-year-office-sequence shape.  ``organization`` and ``year``
    stay parameters rather than folding into one shared constant because the
    two callers deliberately use DIFFERENT organization spellings
    (``_DOCKET_BARE``'s fenced one, everyone else's unfenced one) and
    different year widths (four digits bare, two-or-four under a label) --
    RefSpec does not need the fenced variant at all, so its helper has no
    equivalent parameter.
    """

    return (
        rf"(?P<organization>{organization})"
        rf"[-_](?P<year>{year})[-_]{_DOCKET_OFFICE}(?P<{sequence_group}>\d{{3,5}})"
    )


_DOCKET_BARE = re.compile(
    rf"{_LEFT}{_docket_body(_DOCKET_ORGANIZATION_NO_TRAILING_YEAR, r'\d{4}')}{_RIGHT}"
)
_REGULATIONS_GOV_DOCUMENT = re.compile(
    rf"{_LEFT}(?P<organization>{_DOCKET_ORGANIZATION})"
    rf"[-_](?P<year>\d{{4}})[-_](?P<docket_sequence>\d{{3,5}})"
    rf"[-_](?P<document_sequence>\d{{3,6}}){_RIGHT}"
)
#: "Docket No. FSIS-2025-0012", "Doc. No. AMS-SC-24-0046", "Docket Number
#: EPA-HQ-OAR-2021-0317" — ported from rkaf_projection.py
#: ``_DOCKET_LABEL_PREFIX``, which anchors at the start of a metadata value;
#: here the same label may appear anywhere in a sentence.  The label is
#: presentation, not identity, so it is never part of the candidate's span or
#: value.
_DOCKET_LABEL = r"\b(?:docket|doc\.?)\s*(?:nos?\.?|number|id)?\s*[:#]?\s*"
#: A label licenses the two-digit year form ("AMS-SC-24-0046") that is
#: otherwise indistinguishable from a report number ("GAO-26-9060"), and
#: nothing more: an unlabeled two-digit-year token stays undetected rather than
#: guessed.
_DOCKET_LABELED = re.compile(
    rf"{_DOCKET_LABEL}{_docket_body(_DOCKET_ORGANIZATION, r'\d{4}|\d{2}')}{_RIGHT}",
    re.IGNORECASE,
)
#: citations.py normalize_regsgov_identifier: the uppercase lexical space a
#: regulations.gov identifier has to live in before it is one at all.
_REGSGOV_VALID = re.compile(r"[A-Z0-9]+(?:[-_][A-Z0-9]+)*")
#: The year-less FRDOC docket family: every agency holds exactly one
#: "AGENCY_FRDOC_0001" docket on Regulations.gov for its Federal Register
#: documents (RefSpec's own docstring, web-verified 2026-08-22: ACF_FRDOC_0001
#: is real and navigable).  The literal "FRDOC" token is the anchor the
#: missing year would otherwise provide, so no office segment applies here --
#: there is no year for one to sit after.
#:
#: RefSpec's column reader (``_REGSGOV_DOCKET_SHAPE``,
#: ``r"[A-Z][A-Z0-9]{1,9}_FRDOC_\d{4}"``) already reads this shape, but only
#: under a trusted-column license (REF-052's "the column is the license");
#: RefSpec's own PROSE reader, ``detect_identifier_shapes``, does not read it
#: at all -- confirmed empirically against the vendored wheel,
#: ``refspec_identifier_shapes.detect_identifier_shapes("AOA_FRDOC_0001") ==
#: []``.  Reading it in PROSE here is therefore a genuine SpicySearch-specific
#: widening past RefSpec's prose grammar, adjudicated in
#: ``tests/search/identifier_contract_exceptions.py`` rather than silently
#: diverging: unlike a bare pre-2010 Federal Register number, "AOA_FRDOC_0001"
#: is not ambiguous prose -- the literal "FRDOC" token cannot appear in an
#: agency code, a report number, or any other identifier this module reads --
#: so there is no query-grammar reason to withhold it the way the bare-legacy
#: FR forms are withheld above.
#:
#: Kept underscore-only rather than accepting ``[-_]`` like every other docket
#: grammar here: every real value of this family is published with
#: underscores, and a hyphen variant would be a spelling this module invented
#: rather than one any publisher writes.
_DOCKET_FRDOC = re.compile(
    rf"{_LEFT}(?P<organization>[A-Za-z][A-Za-z0-9]{{1,9}})_(?i:FRDOC)_(?P<sequence>\d{{4}}){_RIGHT}"
)

# CFR citations (citations.py _CFR_STANDARD).  citations.py reads a metadata
# field it already believes is a citation; here the same characters arrive
# inside a sentence, so the grammar carries this module's boundary guards.
# Without them "040 CFR 060" matches at offset 1 and reports "40 CFR 60".
# The label is captured so a *plural* label ("parts", "sections", "§§") can
# license list expansion; a singular citation never expands a conjunction.
#: A section's inner dots and hyphens are part of its name ("60.5-1"); a
#: trailing one is the sentence's punctuation, not the section's.  A greedy
#: ``[A-Za-z0-9.-]*`` read "49 CFR 900.42." as section "900.42.", which
#: :func:`is_cfr_section` then refused — dropping the whole citation rather
#: than the period, for every question typed as a sentence.
_CFR_SECTION_CAPTURE = r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?"
_CFR_STANDARD = re.compile(
    rf"{_LEFT}(?P<title>[1-9]\d*)\s*C\.?\s*F\.?\s*R\.?"
    r"\s*(?P<label>parts?|pt\.?|§{1,2}|sections?|secs?\.?)?\s*"
    rf"(?P<part>\d+)(?:\.(?P<section>{_CFR_SECTION_CAPTURE}))?{_RIGHT}",
    re.IGNORECASE,
)
#: One more list item after a citation whose label was plural: ", 61",
#: ", and 63", "and 63".  Items keep the primary grammar's own shape and are
#: validated by it; the scan stops at the first token that is not one.
_CFR_LIST_ITEM = re.compile(
    rf"\s*(?:,\s*(?:and\s+)?|and\s+)(?P<part>\d+)(?:\.(?P<section>{_CFR_SECTION_CAPTURE}))?{_RIGHT}",
    re.IGNORECASE,
)
#: citations.py _cfr_section: a CFR section suffix without subsection detail.
#: Read through :func:`is_cfr_section` by everything in this repository that
#: has to decide whether a token is a section, so "42", "42a", and "5-1" are
#: one answer here rather than one per caller.
_CFR_SECTION = re.compile(r"\d+[a-z]{0,3}(?:-[0-9a-z]+)*")

# U.S.C. citations (citations.py _USC_STANDARD).  The dash spelling of a range
# tail is absent because dashes are normalized before matching, which folds it
# into the ``\s*-\s*`` alternative.  The label is captured for the same plural
# list-expansion rule the CFR grammar uses.
_USC_STANDARD = re.compile(
    r"(?P<title>[1-9]\d*)\s*U\.?\s*S\.?\s*C\.?"
    r"(?:\s*(?P<label>§{1,2}|sections?|secs?\.?))?\s*"
    # A section's letter suffix may run to THREE letters, not one, and the
    # match must end where its token ends -- ported from cfr_citations.py's
    # _USC_CITATION (identifiers.py:187 _RIGHT, already used by
    # _USC_LIST_ITEM below). The one-letter class silently truncated every
    # multi-letter section onto a DIFFERENT REAL SECTION: "42 U.S.C.
    # 300aa-11" (the Vaccine Act) read as "42 U.S.C. 300a", a food-additive
    # part with no rejection recorded. The bound is measured, not guessed:
    # across the Unified Agenda's 6,981 distinct U.S.C. sections the letter
    # suffixes run 1 (1,436 sections), 2 (150) and 3 (51) letters, and never
    # longer -- so three covers every real section while staying far short
    # of any English word. Without the trailing guard, "1983affirmed" would
    # backtrack to section "198" rather than matching nothing.
    rf"(?P<section>\d+[A-Za-z]{{0,3}}(?:-\d+[A-Za-z]{{0,3}})?)"
    rf"(?:(?:\s+(?:to|through)\s+|\s*-\s*)(?P<range_end>\d+[A-Za-z]{{0,3}}))?"
    rf"{_RIGHT}",
    re.IGNORECASE,
)
_USC_LIST_ITEM = re.compile(rf"\s*(?:,\s*(?:and\s+)?|and\s+)(?P<section>\d+[A-Za-z]?){_RIGHT}")
_USC_SECTION_ATOM = re.compile(r"(?P<number>\d+)(?P<suffix>[a-z]*)")

# Title-form U.S.C. citations — "section 553 of title 5" — the spelling
# statutes themselves use.  Native to this module (no citations.py analogue):
# the query grammar gap was found by the search-quality benchmark, 2026-08-01.
# A plural label licenses the section list; a bare "section 553" without the
# "of title" tail stays undetected rather than guessed.
_USC_TITLE_FORM = re.compile(
    rf"{_LEFT}(?P<label>§{{1,2}}|sections?|secs?\.?)\s*"
    r"(?P<first>\d+[A-Za-z]?)"
    r"(?P<items>(?:\s*(?:,\s*(?:and\s+)?|\s+and\s+)\d+[A-Za-z]?)*)"
    rf"\s+of\s+title\s+(?P<title>[1-9]\d*){_RIGHT}",
    re.IGNORECASE,
)
_USC_TITLE_FORM_ITEM = re.compile(r"\s*(?:,\s*(?:and\s+)?|\s+and\s+)(?P<section>\d+[A-Za-z]?)")

# Public laws, executive orders, and Statutes at Large.  Native to this module
# for the same reason as the title form: people cite enacted law by these
# names, and a detector that cannot read "Public Law 118-42" routes the whole
# query to lexical text.  Capitalization is load-bearing where an abbreviation
# is also an English word: bare "EO"/"E.O." must be uppercase and "Stat" must
# be capitalized, or prose would mint citations.
#
# Bare "PL 118-42" (no dots, measured 2026-09-05: 64.9% of a public-law
# population) was unreadable by either existing branch -- the first requires
# the literal "Pub"/"Public" opening, the second requires dotted "P. L." --
# so a query typed the way most public laws are actually written fell
# through to lexical text.  Ported the same defense the abbreviated
# Executive Order form already uses for the identical problem ("EO" is also
# not an English word, but IS two capital letters that could open a run of
# other capitalized prose): the bare form is matched CASE-SENSITIVELY
# (``(?-i:PL)``, a scoped flag turning this module's ``re.IGNORECASE`` back
# off for just this branch) while the rest of the alternation stays
# case-insensitive, so "pl 118-42" or "Pl 118-42" -- not how anyone spells
# the abbreviation -- stay unread rather than guessed.
_PUBLIC_LAW = re.compile(
    rf"{_LEFT}(?:Pub(?:lic)?\.?\s*L(?:aw)?\.?|P\.\s*L\.|(?-i:PL))"
    # Published prose also uses "Public Law (Pub. L.) 119-20"; retain its full span.
    r"(?:\s*\(Pub\.\s*L\.\))?\s*(?:No\.?\s*)?"
    rf"(?P<congress>\d{{1,3}})-(?P<law>\d{{1,4}}){_RIGHT}",
    re.IGNORECASE,
)
_EXECUTIVE_ORDER_SPELLED = re.compile(
    rf"{_LEFT}(?:Executive\s+Order|Exec\.?\s*(?:Order|Ord\.?))\s*(?:No\.?\s*)?(?P<number>\d{{4,5}}){_RIGHT}",
    re.IGNORECASE,
)
_EXECUTIVE_ORDER_ABBREVIATED = re.compile(
    rf"{_LEFT}(?:EO|E\.\s*O\.)\s*(?:No\.?\s*)?(?P<number>\d{{4,5}}){_RIGHT}"
)
_STATUTES_AT_LARGE = re.compile(
    rf"{_LEFT}(?P<volume>[1-9]\d{{0,3}})\s+Stat\.?\s+(?P<page>[1-9]\d{{0,4}}){_RIGHT}"
)

_EXACT_CATALOG_MATCHERS = (
    ("rin", IdentifierKind.RIN, _RIN),
    ("federal-register-correction", IdentifierKind.FEDERAL_REGISTER_DOCUMENT, _FR_CORRECTION),
    ("federal-register-standard", IdentifierKind.FEDERAL_REGISTER_DOCUMENT, _FR_STANDARD),
    ("federal-register-legacy", IdentifierKind.FEDERAL_REGISTER_DOCUMENT, _FR_LEGACY_LETTER),
    (
        "regulations-gov-document",
        IdentifierKind.REGULATIONS_GOV_DOCUMENT,
        _REGULATIONS_GOV_DOCUMENT,
    ),
    ("regulations-gov-docket", IdentifierKind.DOCKET, _DOCKET_BARE),
    ("regulations-gov-docket-frdoc", IdentifierKind.DOCKET, _DOCKET_FRDOC),
)
EXACT_CATALOG_IDENTIFIER_POLICY = MappingProxyType(
    {
        # Bumped v2 -> v3 2026-09-02 (REF-056 / rulespec 0.2.0-pre.16).  The
        # widened FEDERAL_REGISTER_DOCUMENT_NUMBER tail (\d{4}-\d{5} ->
        # \d{4}-\d{3,5}) changes what this policy *recognizes*: "2026-0322"
        # now enters the exact-identifier query path and short-circuits the
        # lexical lane, where before it was ordinary text.  That is observable
        # serving behavior, so the version moves with the digest rather than
        # leaving two different behaviors sharing one label.
        #
        # Bumped v3 -> v4 2026-09-05: the regulations.gov docket grammar
        # gained the office/program-code segment ("FDA-2011-V-0020",
        # "DOD-2008-OS-0081" -- see _DOCKET_OFFICE) and the year-less
        # "AGENCY_FRDOC_0001" family (see _DOCKET_FRDOC), both embedded in
        # "regulations-gov-docket"'s and the new "regulations-gov-docket-frdoc"
        # entry's pattern text above.  A whole-query search for either shape
        # now enters the exact-identifier path and short-circuits the lexical
        # lane, where before neither matched any grammar here at all.  The
        # docket organization fence (``_DOCKET_ORGANIZATION_NO_TRAILING_YEAR``)
        # also gained a "no trailing FRDOC segment" clause, which REMOVES a
        # match: a Regulations.gov document id shaped like
        # "NOAA_FRDOC_0001-5462" no longer full-matches "regulations-gov-docket"
        # with a bogus year of "0001".  Both directions are observable serving
        # behavior, so the version moves with the digest.
        #
        # STILL not bumped for REF-064/065's bare-legacy and X Federal
        # Register families, and that remains a decision rather than an
        # oversight -- unchanged by this round.  The bare-legacy and X
        # families were added to is_federal_register_document_number and to
        # classify_federal_register_document_number, both COLUMN readers, and
        # deliberately NOT to _EXACT_CATALOG_MATCHERS above.  So typing
        # "09-19806" or "X09-101207" into the search box still produces no
        # exact-identifier match and no lexical short-circuit; the query runs
        # as ordinary text, which is what it did before this change.
        #
        # Why not add them.  PLAN.md's accepted rule -- "when the filtered
        # catalog contains an exact identifier hit, return that exact set and
        # skip lexical retrieval" -- is about identifiers a QUERY may state,
        # and a bare pre-2010 number is the one shape a query cannot state
        # unambiguously: unlabeled, "94-12345" is a docket number, a release
        # number, "MM Docket No. 98-213".  Admitting it here would let those
        # queries skip lexical retrieval on a guess, which is the failure the
        # column-only design exists to prevent (see _FR_BARE_LEGACY above,
        # and RefSpec's identical ruling in its own prose reader).  The
        # year-less FRDOC family is admitted above DESPITE being unlabeled
        # prose, and that is not the same failure: "FRDOC" is a literal,
        # unambiguous anchor token, not a guess at which space a bare number
        # belongs to -- see _DOCKET_FRDOC's docstring.
        #
        # What the still-excluded forms cost, stated rather than discovered:
        # for a subject whose exact identifier is "X09-101207", a query of
        # that string returns it via lexical retrieval alongside any subject
        # whose prose merely contains it, rather than returning it alone with
        # the exact boost.  Pre-2010 documents stay findable -- exact lookup
        # remains additive for every normalized query -- and this is the
        # status quo, not a regression.  Adding those forms would require a
        # v5 and a new digest; the shape that would justify it is a labeled
        # query ("FR Doc. 09-19806"), which no grammar here reads yet and
        # which is a query grammar question, not an identifier-space one.
        "version": "spicysearch-exact-catalog-identifier-query-v4",
        "canonicalizerId": IDENTIFIER_NORMALIZATION_POLICY_ID,
        "canonicalizerVersion": IDENTIFIER_NORMALIZATION_POLICY_VERSION,
        "canonicalizerDigest": IDENTIFIER_NORMALIZATION_POLICY_DIGEST,
        "match": "first full grammar match over the complete canonical identifier key",
        "matchOrder": [name for name, _kind, _pattern in _EXACT_CATALOG_MATCHERS],
        "patterns": {
            name: pattern.pattern for name, _kind, pattern in _EXACT_CATALOG_MATCHERS
        },
        "recognizedKinds": sorted(
            {kind.value for _name, kind, _pattern in _EXACT_CATALOG_MATCHERS}
        ),
        "publisherPrefix": "preserved-and-never-parsed-or-dropped",
    }
)
EXACT_CATALOG_IDENTIFIER_POLICY_DIGEST = sha256_digest(
    dict(EXACT_CATALOG_IDENTIFIER_POLICY)
)


def _is_plural_label(label: str | None) -> bool:
    """Return whether a citation label licenses a list of parts or sections."""

    if not label:
        return False
    normalized = label.lower().rstrip(".")
    return normalized in {"parts", "sections", "secs"} or label == "§§"


def is_cfr_section(value: object) -> bool:
    """Return whether a string is a CFR section token, suffixes included.

    Sections are not numbers: 900.42a and 60.5-1 are ordinary section names, so
    a digits-only test silently refuses real citations.  Subsection detail
    ("(b)") is not part of a section and is not accepted here.
    """

    return isinstance(value, str) and _CFR_SECTION.fullmatch(value.strip().lower()) is not None


def is_federal_register_document_number(value: object, *, column_licensed: bool = False) -> bool:
    """Return whether a value is a Federal Register document number.

    The whole value must be the identifier — this answers "is this string one",
    not "does this string contain one". Prose-narrow by default
    (``column_licensed=False``, unchanged): only the modern form is ``True``.
    Legacy ("E7-21559") and correction ("C1-2026-13078") numbers are official
    and are deliberately ``False`` here — they are outside Rulespec's
    ``us-frdoc`` lexical space, not outside the corpus.

    ``column_licensed=True`` mirrors RefSpec's own parameter of the same name
    (REF-052 "the column is the license"): a value arriving from a TRUSTED
    ``document_number`` field, never from a query or from prose, is
    additionally recognised as the bare-legacy form (:data:`_FR_BARE_LEGACY`,
    "09-19806") or the X-family form (:data:`_FR_X_SPELLING`, "X09-101207").
    Neither is admitted here unlicensed, for the same reason the
    letter-opening legacy form above is admitted unconditionally and the
    bare one is not: unlabeled, "94-12345" cannot be told apart from a
    docket or a release number, so a caller must assert the value came from
    a column, not free text, before this answers ``True`` for it.

    **This is narrower than RefSpec's flag of the same name**, deliberately
    and by exactly the families this repository has a reason to read. RefSpec
    licenses four letter-opening families (E9-654, E10-11220, E3-2013-2261
    and their siblings) and the modern short tail ("2010-1") as well; those
    stay ``False`` here because nothing in SpicySearch asks about them, and
    a shape admitted with no consumer is a rule that can only drift. The
    complete list is checked in as adjudicated exceptions in
    ``tests/search/identifier_contract_exceptions.py``, where the contract
    test compares this function against RefSpec's on both flag settings.

    **Under the license this is :func:`classify_federal_register_document_
    number` asking a coarser question**, delegated rather than restated, so
    the two readers cannot disagree about which values they read. They once
    could: an earlier cut tested the modern form on the RAW value and the
    licensed forms on the dash-folded one, so ``2010-31094`` spelled with an
    EN DASH (U+2013) was ``False`` here and ``rkaf:us-frdoc`` there. No
    production caller guards then classifies today, but one would have
    refused a value the classifier reads. One grammar makes that class of
    disagreement unrepresentable, which is the same medicine the X tail got
    when its two spellings were merged into :data:`_FR_X_SPELLING`.

    Unlicensed, the folding the classifier does is NOT inherited and the raw
    value must be the modern form exactly: normalization for a query or a
    prose match lives upstream in
    ``identifier_normalization.normalize_identifier``, and folding again
    here would put one rule in two places. Under a license it is inherited,
    because a column reader is handed whatever the publisher's field spells
    -- which is RefSpec's posture for the same flag, and why the contract
    table records no dash-axis divergence on the licensed comparison. It
    still records the WHITESPACE axis there: neither reader strips, because
    ``normalize_identifier`` does, and
    ``source_catalog_metadata._exact_identifier_key`` is where the one
    production caller applies it.

    What this cannot see: whether the caller's licence claim is true. It
    takes ``column_licensed`` on trust -- there is no way to tell a trusted
    column value from a query string once it is a ``str`` -- so admitting a
    bare number is only as safe as the call site that asserts it.
    """

    if not column_licensed:
        return isinstance(value, str) and _FR_STANDARD_EXACT.fullmatch(value) is not None
    return classify_federal_register_document_number(value, column_licensed=True) is not None


@dataclass(frozen=True, slots=True)
class FederalRegisterDocumentClassification:
    """Which rulespec Federal Register SPACE (REF-064/065) a value belongs
    to, decided natively, plus the date that space qualifies its members by.

    **This is not an identity and cannot be mistaken for one by accident:**
    two instances compare equal whenever two documents share a space and a
    qualifying date. ``09-19806`` and ``09-19807``, both published
    2009-08-19, produce equal values here; so do ``X09-101207`` and
    ``X09-111207``. That is correct for a classification and fatal for an
    identity, which is why this type carries neither the document number nor
    an IRI: it answers "which space", and the caller already holds the value
    it asked about.

    ``qualifying_date`` is set only for
    :data:`FEDERAL_REGISTER_DOCUMENT_SCHEME_LEGACY`: that is the one space
    here whose members are not distinguished by their number alone --
    "00-111" names two different documents -- so a date is part of what an
    identity in that space would have to state, and the classification says
    which date that would be. Every other scheme leaves it ``None``.
    """

    scheme: str
    qualifying_date: str | None = None


def _publication_day(value: object) -> str:
    """The ISO calendar day a caller stated, or a loud refusal.

    Mirrors RefSpec's ``iri_minting._publication_day`` (REF-064): a caller
    who states ``publication_date`` has asserted a fact, and a value that
    does not name a real day is a broken assertion about THIS call, not
    ordinary data -- so it raises rather than silently falling back to the
    undated answer. Accepts a :class:`datetime.date` and any string
    :meth:`date.fromisoformat` reads, extended ("2009-08-19") or compact
    ("20090819") alike, since a source publisher's own field states either.
    A :class:`datetime.datetime` is refused rather than truncated: a
    date-qualified classification is not the place to drop a time silently.

    Because it raises on a value it cannot read, a caller reading a
    PUBLISHER's field rather than asserting its own fact must decide first
    whether that field states a day at all --
    ``source_catalog_metadata._validate_federal_register_document_identities``
    does exactly that, so an unreadable publisher date stays DocSpec's
    selection problem instead of becoming a build failure here.
    """

    if isinstance(value, datetime):
        raise ValueError(f"publication_date must name a day, not an instant: {value!r}")
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as error:
        raise ValueError(f"publication_date does not state a day: {value!r}") from error


def classify_federal_register_document_number(
    document_number: object,
    *,
    publication_date: object = None,
    column_licensed: bool = False,
) -> FederalRegisterDocumentClassification | None:
    """Which rulespec Federal Register space (REF-064/065) a value belongs
    to, decided natively -- no refspec import, per
    ``tests/search/test_metadata_package_boundary.py``.

    **A classification, not a mint.** The answer names a SPACE and, where
    that space is date-qualified, the date; it never names the document.
    Every document in one space and (for bare-legacy) one day gets the same
    answer -- see :class:`FederalRegisterDocumentClassification`. Nothing in
    this repository turns that answer into ``urn:rkaf:us:frdoc-legacy:...``
    or ``urn:rkaf:us:frdoc-x:...``, because no consumer reads such a value:
    SpicySearch's subjects, exact tables and query path all key on the
    normalized string. RefSpec's
    ``iri_minting.mint_federal_register_document_iri`` is the minter, and
    ``experiments/identifier_census.py`` is the one place this repository
    calls it -- as evidence about a corpus, not as a serving path.

    Two live consumers, and they are the reason this exists at all:
    ``source_catalog_metadata._validate_federal_register_document_identities``
    (which needs the fully-informed answer twice over -- to catch an X
    number that contradicts its own day, and to tell one bare number
    stated twice from two documents wearing one citation, which only the
    ``qualifying_date`` separates) and the drift contract in
    ``tests/search/test_identifier_contract.py``, which compares this
    function's scheme against RefSpec's minter's on a shared corpus.

    ``column_licensed=True`` is the same "the column is the license" gate
    :func:`is_federal_register_document_number` uses (REF-052): only a value
    that arrived from a trusted ``document_number`` field, never from a
    query or from prose, may be read as bare-legacy or X-shaped. Modern-form
    values need no license, matching that function.

    The X family (:data:`_FR_X_SPELLING`) needs no ``publication_date``
    because the number carries its own, read RIGHT-ANCHORED: the last four
    digits are the month and day. A caller who states one anyway gets it
    checked, and a CONTRADICTION raises -- RefSpec measured this agreeing
    1,007,156 times out of 1,007,156 over the pinned corpus, which is what
    makes a disagreement a detectable defect in one of the two statements
    rather than an ambiguity to paper over. Both statements must describe
    the SAME publication event for that to hold; pairing a number with a
    date from a different event is the caller's error, not the data's, and
    this function cannot see the difference.

    The bare-legacy family (:data:`_FR_BARE_LEGACY`) is the opposite case:
    the number alone never distinguishes a document ("00-111" names two), so
    the space is DATE-QUALIFIED BY CONSTRUCTION and is reached only when the
    caller states a ``publication_date``. Undated, the value is recognized
    but unplaceable and the scheme is
    :data:`FEDERAL_REGISTER_DOCUMENT_SCHEME_PARTNER` -- the same hatch the
    letter-opening legacy families already share -- rather than a
    half-qualified answer.

    Returns ``None`` when the value is not a Federal Register document
    number this module can read at all, or when ``column_licensed`` is
    required and absent.
    """

    if not isinstance(document_number, str):
        return None
    text = document_number.translate(_DASHES)
    if _FR_STANDARD_EXACT.fullmatch(text) is not None:
        return FederalRegisterDocumentClassification(FEDERAL_REGISTER_DOCUMENT_SCHEME_MODERN)
    if not column_licensed:
        return None
    upper = text.upper()
    x_match = _FR_X_SPELLING.fullmatch(upper)
    if x_match is not None:
        if publication_date is not None:
            stated = _publication_day(publication_date)
            encoded = f"{x_match['month']}-{x_match['day']}"
            if stated[5:] != encoded or stated[2:4] != x_match["year"]:
                raise ValueError(
                    f"{upper} encodes {x_match['year']}-{encoded} and the caller "
                    f"states {stated}: an X-family Federal Register document number "
                    "carries its own publication date, so a disagreement is a defect "
                    "rather than a spelling to choose between"
                )
        return FederalRegisterDocumentClassification(FEDERAL_REGISTER_DOCUMENT_SCHEME_X)
    if _FR_BARE_LEGACY.fullmatch(upper) is not None:
        if publication_date is None:
            return FederalRegisterDocumentClassification(
                FEDERAL_REGISTER_DOCUMENT_SCHEME_PARTNER
            )
        return FederalRegisterDocumentClassification(
            FEDERAL_REGISTER_DOCUMENT_SCHEME_LEGACY,
            qualifying_date=_publication_day(publication_date),
        )
    return None


def is_regulation_identifier_number(value: object) -> bool:
    """Return whether a value is, in whole, a regulation identifier number.

    Answers "is this string one", not "does this string contain one", so that
    a catalog field can be validated with the same grammar that reads a RIN
    out of free text and the two can never drift apart. This matters because
    56,364 of the catalog's 64,537 docket ``rin`` values are the literal
    string "Not Assigned"; admitted as an identifier it became the corpus's
    most common one by a factor of ten.
    """

    return isinstance(value, str) and _RIN.fullmatch(value) is not None


def _digits(value: str | None) -> str | None:
    text = (value or "").strip()
    return str(int(text)) if text.isdigit() else None


def _usc_section_key(section: str | None) -> tuple[int, str] | None:
    """Order a U.S.C. section by numeric stem, then letter suffix."""

    if not section:
        return None
    match = _USC_SECTION_ATOM.fullmatch(section)
    return (int(match["number"]), match["suffix"]) if match else None


def _usc_section_range(section: str | None, range_end: str | None = None) -> tuple[str | None, str | None]:
    """Split a U.S.C. section token into ``(section, range_end)``.

    Ported from citations.py ``_usc_section_range``.  A hyphen means two
    different things in the U.S. Code: part of one section's name in
    ``1831p-1``, and a range separator in ``7401-7671q``. As a lexical
    heuristic, read a pair as a range when its second endpoint sorts strictly
    after its first; this does not verify legal existence. An unordered or
    unparsable pair keeps the token whole rather than guessing, which is why
    ``1484-86`` stays one opaque section.
    """

    if not section:
        return (section, None)
    if range_end is not None:
        start, end = section, range_end
    elif section.count("-") == 1:
        start, end = section.split("-")
    else:
        return (section, None)
    low, high = _usc_section_key(start), _usc_section_key(end)
    if low is None or high is None or low >= high:
        return (section, None)
    return (start, end)


def _rin_candidate(match: re.Match[str]) -> IdentifierCandidate:
    return IdentifierCandidate(
        kind=IdentifierKind.RIN,
        value=match.group("value").upper(),
        span=match.span("value"),
    )


def _rin_candidates(text: str) -> list[IdentifierCandidate]:
    return [_rin_candidate(match) for match in _RIN.finditer(text)]


def _federal_register_candidate(
    match: re.Match[str],
    *,
    form: str,
) -> IdentifierCandidate:
    scheme = (
        FEDERAL_REGISTER_DOCUMENT_SCHEME_MODERN
        if form == "standard"
        else FEDERAL_REGISTER_DOCUMENT_SCHEME_PARTNER
    )
    return IdentifierCandidate(
        kind=IdentifierKind.FEDERAL_REGISTER_DOCUMENT,
        value=match.group("value").upper(),
        span=match.span("value"),
        components={"form": form, "rulespec_scheme": scheme},
    )


def _federal_register_candidates(text: str) -> list[IdentifierCandidate]:
    """Detect every Federal Register document form, tagging the ones Rulespec
    cannot express as ``rkaf:us-frdoc`` (citations.py federal_register_identifier).
    """

    found: list[IdentifierCandidate] = []
    for pattern, form in ((_FR_CORRECTION, "correction"), (_FR_STANDARD, "standard"), (_FR_LEGACY_LETTER, "legacy")):
        for match in pattern.finditer(text):
            found.append(_federal_register_candidate(match, form=form))
    return found


def _docket_candidate(match: re.Match[str]) -> IdentifierCandidate | None:
    organization = match.group("organization").upper()
    year = match.group("year")
    office = match.group("office")
    sequence = match.group("sequence")
    # The office segment, when the docket states one, is part of what makes
    # the value unique: "FDA-2011-V-0020" and "FDA-2011-N-0020" are two
    # different dockets, so dropping the office out of ``value`` would
    # collide them under one exact-lookup key. ``components`` omits the key
    # entirely rather than reporting ``office=None`` (RefSpec's own
    # convention for an optional group nobody stated).
    parts = [organization, year, *([office.upper()] if office else []), sequence]
    value = "-".join(parts)
    # The ported validity rule, applied after upcasing: junk never becomes an
    # identifier even if the shape above admitted it.
    if not _REGSGOV_VALID.fullmatch(value):
        return None
    components = {"organization": organization, "year": year, "sequence": sequence}
    if office:
        components["office"] = office.upper()
    return IdentifierCandidate(
        kind=IdentifierKind.DOCKET,
        value=value,
        span=(match.start("organization"), match.end("sequence")),
        components=components,
    )


def _docket_frdoc_candidate(match: re.Match[str]) -> IdentifierCandidate | None:
    """The year-less "AGENCY_FRDOC_0001" family -- see :data:`_DOCKET_FRDOC`."""

    organization = match.group("organization").upper()
    sequence = match.group("sequence")
    value = f"{organization}_FRDOC_{sequence}"
    if not _REGSGOV_VALID.fullmatch(value):
        return None
    return IdentifierCandidate(
        kind=IdentifierKind.DOCKET,
        value=value,
        span=match.span(),
        components={"organization": organization, "sequence": sequence, "family": "frdoc"},
    )


def _docket_candidates(text: str) -> list[IdentifierCandidate]:
    found: list[IdentifierCandidate] = []
    for pattern in (_DOCKET_BARE, _DOCKET_LABELED):
        for match in pattern.finditer(text):
            candidate = _docket_candidate(match)
            if candidate is not None and candidate not in found:
                found.append(candidate)
    for match in _DOCKET_FRDOC.finditer(text):
        candidate = _docket_frdoc_candidate(match)
        if candidate is not None and candidate not in found:
            found.append(candidate)
    return found


def _regulations_gov_document_candidates(text: str) -> list[IdentifierCandidate]:
    return [
        candidate
        for match in _REGULATIONS_GOV_DOCUMENT.finditer(text)
        if (candidate := _regulations_gov_document_candidate(match)) is not None
    ]


def _regulations_gov_document_candidate(
    match: re.Match[str],
) -> IdentifierCandidate | None:
    organization = match.group("organization").upper()
    year = match.group("year")
    docket_sequence = match.group("docket_sequence")
    document_sequence = match.group("document_sequence")
    value = f"{organization}-{year}-{docket_sequence}-{document_sequence}"
    if _REGSGOV_VALID.fullmatch(value) is None:
        return None
    return IdentifierCandidate(
        kind=IdentifierKind.REGULATIONS_GOV_DOCUMENT,
        value=value,
        span=match.span(),
        components={
            "organization": organization,
            "year": year,
            "docket_sequence": docket_sequence,
            "document_sequence": document_sequence,
        },
    )


def _cfr_candidate(
    title: str,
    part: str | None,
    raw_section: str | None,
    span: tuple[int, int],
) -> IdentifierCandidate | None:
    section = None
    if raw_section is not None:
        stripped = re.sub(r"\([^)]*\)", "", raw_section.strip().lower())
        section = stripped if _CFR_SECTION.fullmatch(stripped) else None
        if section is None:
            return None
    if not title or not part:
        return None
    components = {"title": title, "part": part}
    if section:
        components["section"] = section
    suffix = f".{section}" if section else ""
    return IdentifierCandidate(
        kind=IdentifierKind.CFR,
        # A normalized citation for exact comparison. Structure lives in
        # ``components``; this string is never a prefix to match on.
        value=f"{title} CFR {part}{suffix}",
        span=span,
        components=components,
    )


def _cfr_candidates(text: str) -> list[IdentifierCandidate]:
    found: list[IdentifierCandidate] = []
    for match in _CFR_STANDARD.finditer(text):
        title = _digits(match.group("title"))
        candidate = _cfr_candidate(title or "", _digits(match.group("part")), match.group("section"), match.span())
        if candidate is None:
            continue
        found.append(candidate)
        if not _is_plural_label(match.group("label")):
            continue
        position = match.end()
        while True:
            item = _CFR_LIST_ITEM.match(text, position)
            if item is None:
                break
            expanded = _cfr_candidate(
                title or "",
                _digits(item.group("part")),
                item.group("section"),
                (item.start("part"), item.end()),
            )
            if expanded is None:
                break
            found.append(expanded)
            position = item.end()
    return found


def _usc_section_candidate(title: str, section: str, span: tuple[int, int]) -> IdentifierCandidate:
    return IdentifierCandidate(
        kind=IdentifierKind.USC,
        value=f"{title} U.S.C. {section}",
        span=span,
        components={"title": title, "section": section},
    )


def _usc_candidates(text: str) -> list[IdentifierCandidate]:
    found: list[IdentifierCandidate] = []
    for match in _USC_STANDARD.finditer(text):
        title = _digits(match.group("title"))
        if not title:
            continue
        stated_end = match.group("range_end")
        section, section_end = _usc_section_range(
            match.group("section").strip().lower(),
            stated_end.strip().lower() if stated_end else None,
        )
        if section is None:
            continue
        # A range tail the ordering rule declined is not covered text, so the
        # span stops at the section — the same accounting citations.py does
        # when it downgrades such a parse to ``partial``.
        end = match.end("section") if stated_end is not None and section_end is None else match.end()
        components = {"title": title, "section": section}
        if section_end:
            components["section_end"] = section_end
        suffix = f"-{section_end}" if section_end else ""
        found.append(
            IdentifierCandidate(
                kind=IdentifierKind.USC,
                value=f"{title} U.S.C. {section}{suffix}",
                span=(match.start(), end),
                components=components,
            )
        )
        if section_end is not None or not _is_plural_label(match.group("label")):
            continue
        position = match.end()
        while True:
            item = _USC_LIST_ITEM.match(text, position)
            if item is None:
                break
            found.append(
                _usc_section_candidate(title, item.group("section").lower(), item.span("section"))
            )
            position = item.end()
    return found


def _usc_title_form_candidates(text: str) -> list[IdentifierCandidate]:
    """Read "section 553 of title 5" (and its plural list) as U.S.C. citations."""

    found: list[IdentifierCandidate] = []
    for match in _USC_TITLE_FORM.finditer(text):
        title = _digits(match.group("title"))
        if not title:
            continue
        found.append(
            _usc_section_candidate(title, match.group("first").lower(), match.span("first"))
        )
        if not _is_plural_label(match.group("label")):
            continue
        position = match.end("first")
        items_end = match.end("items")
        while position < items_end:
            item = _USC_TITLE_FORM_ITEM.match(text, position)
            if item is None or item.end() > items_end:
                break
            found.append(
                _usc_section_candidate(title, item.group("section").lower(), item.span("section"))
            )
            position = item.end()
    return found


def _public_law_candidates(text: str) -> list[IdentifierCandidate]:
    return [
        IdentifierCandidate(
            kind=IdentifierKind.PUBLIC_LAW,
            value=f"Public Law {match.group('congress')}-{match.group('law')}",
            span=match.span(),
            components={"congress": match.group("congress"), "law": match.group("law")},
        )
        for match in _PUBLIC_LAW.finditer(text)
    ]


def _executive_order_candidates(text: str) -> list[IdentifierCandidate]:
    found: list[IdentifierCandidate] = []
    for pattern in (_EXECUTIVE_ORDER_SPELLED, _EXECUTIVE_ORDER_ABBREVIATED):
        for match in pattern.finditer(text):
            candidate = IdentifierCandidate(
                kind=IdentifierKind.EXECUTIVE_ORDER,
                value=f"Executive Order {match.group('number')}",
                span=match.span(),
                components={"number": match.group("number")},
            )
            if candidate not in found:
                found.append(candidate)
    return found


def _statutes_at_large_candidates(text: str) -> list[IdentifierCandidate]:
    return [
        IdentifierCandidate(
            kind=IdentifierKind.STATUTES_AT_LARGE,
            value=f"{match.group('volume')} Stat. {match.group('page')}",
            span=match.span(),
            components={"volume": match.group("volume"), "page": match.group("page")},
        )
        for match in _STATUTES_AT_LARGE.finditer(text)
    ]


def _without_overlaps(candidates: list[IdentifierCandidate]) -> list[IdentifierCandidate]:
    """Keep the longest claim on any stretch of text, then the most specific.

    The sort states the rule — earliest start, then longest, then most specific
    — and a single sweep applies it.  Comparing each surviving claim against
    every earlier one is the same answer at quadratic cost, and the number of
    claims is bounded only by the length of the question, which nothing caps.

    The sweep is exact rather than approximate.  Every span here covers at
    least one character, and claims arrive in ascending start order, so a claim
    already kept starts no later than the one being read: it overlaps exactly
    when the new start falls before its end.  The furthest end reached is
    therefore the only thing a new claim can collide with.
    """

    ordered = sorted(
        candidates,
        key=lambda candidate: (
            candidate.span[0],
            -(candidate.span[1] - candidate.span[0]),
            _KIND_PRECEDENCE.index(candidate.kind),
        ),
    )
    kept: list[IdentifierCandidate] = []
    reach = 0
    for candidate in ordered:
        start, end = candidate.span
        if kept and start < reach:
            continue
        kept.append(candidate)
        reach = max(reach, end)
    return kept


#: One served query reads its own question four to six times: the planner
#: detects identifiers, the unread-shape scan detects them again to mask what
#: was read, and the engine detects them again per identifier it was handed.
#: Every read runs the same dozen-odd regexes over the same characters for the
#: same answer, so the second read is free — detection is pure, and a modest
#: window of recent questions is enough to cover one request's fan-out without
#: turning a shared cache into a place questions accumulate.
_DETECTION_CACHE_SIZE = 512


@lru_cache(maxsize=_DETECTION_CACHE_SIZE)
def _detected_identifiers(text: str) -> tuple[IdentifierCandidate, ...]:
    """Detect once per distinct question; the tuple is shared, so it is frozen."""

    scanned = text.translate(_DASHES)
    candidates = [
        *_cfr_candidates(scanned),
        *_usc_candidates(scanned),
        *_usc_title_form_candidates(scanned),
        *_public_law_candidates(scanned),
        *_executive_order_candidates(scanned),
        *_statutes_at_large_candidates(scanned),
        *_rin_candidates(scanned),
        *_federal_register_candidates(scanned),
        *_regulations_gov_document_candidates(scanned),
        *_docket_candidates(scanned),
    ]
    return tuple(_without_overlaps(candidates))


def detect_identifiers(text: str | None) -> list[IdentifierCandidate]:
    """Return the identifiers a query names, in the order the query names them.

    The scan itself is cached per question string; the list handed back is a
    fresh one over shared, frozen candidates, so a caller may still sort or
    filter what it got without another caller seeing it.
    """

    if not text:
        return []
    return list(_detected_identifiers(text))


def exact_catalog_identifier_value(text: str | None) -> str | None:
    """Return one canonical whole-query catalog identifier, or null for prose.

    The grammar only decides whether the complete query has a recognized
    identifier shape.  ``normalize_identifier`` alone creates the comparison
    key; this caller neither parses nor removes publisher prefixes.
    """

    if not isinstance(text, str):
        return None
    key = normalize_identifier(text)
    if key is None:
        return None
    for _name, _kind, pattern in _EXACT_CATALOG_MATCHERS:
        if pattern.fullmatch(key) is not None:
            return key
    return None


def identifier_values(text: str | None) -> tuple[str, ...]:
    """Return the detected identifier values, deduplicated, in query order."""

    return tuple(dict.fromkeys(candidate.value for candidate in detect_identifiers(text)))


def unread_identifier_shapes(text: str | None) -> tuple[str, ...]:
    """Return specific-looking substrings that no identifier grammar read.

    Results retain their original spelling and order. The detector stays
    conservative because a false positive turns an ordinary topical search
    into an alarming response; a false negative merely omits a warning.
    """

    if not isinstance(text, str) or not text:
        return ()
    return _unread_identifier_shapes(text)


@lru_cache(maxsize=_UNREAD_SHAPE_CACHE_SIZE)
def _unread_identifier_shapes(text: str) -> tuple[str, ...]:
    masked, read_spans = _mask_read_identifiers(text)
    found: list[tuple[int, int, str]] = []
    for pattern in _UNREAD_SHAPES:
        for match in pattern.finditer(masked):
            start, end = match.span()
            if "lead" in match.groupdict() and match.group("lead") in _UNREAD_QUERY_KEYWORDS:
                start = match.start("label")
            if _bare_unread_label(match.group("label")) in _UNREAD_NEVER_A_LABEL:
                continue
            if not any(character.isdigit() for character in match.group()):
                continue
            if any(start < read_end and read_start < end for read_start, read_end in read_spans):
                continue
            found.append((start, end, text[start:end]))
    return tuple(dict.fromkeys(value for _, _, value in sorted(_widest_unread(found))))


def _widest_unread(found: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """Drop a match contained by another match while preserving source order."""

    contained: set[tuple[int, int]] = set()
    reach: int | None = None
    for start, end in sorted(
        {(start, end) for start, end, _ in found},
        key=lambda span: (span[0], -span[1]),
    ):
        if reach is not None and end <= reach:
            contained.add((start, end))
        else:
            reach = end
    return [item for item in found if (item[0], item[1]) not in contained]


def _bare_unread_label(label: str) -> str:
    return label.replace(".", "").upper()


def _mask_read_identifiers(text: str) -> tuple[str, tuple[tuple[int, int], ...]]:
    """Blank every span a grammar claimed without changing other offsets."""

    masked = list(text)
    spans: list[tuple[int, int]] = []
    for candidate in detect_identifiers(text):
        start, end = max(candidate.span[0], 0), min(candidate.span[1], len(masked))
        for index in range(start, end):
            masked[index] = " "
        spans.append((start, end))
    return "".join(masked), tuple(spans)
