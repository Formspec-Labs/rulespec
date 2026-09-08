"""Freeze three unused local source passages and expectations before extraction."""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.evaluation import validate_expected

ROOT = Path(__file__).resolve().parent
CACHE = Path('/Users/mikewolfd/Work/corpora/_preserved-2026-08-27/spicy-regs-output-complete/segmentation-source-cache-v2')


def main():
    output = ROOT / 'fresh-source'
    output.mkdir(exist_ok=False)
    selected = [
        ('slopes', 'cfr-xml-short.xml', list(range(5)), '30 CFR 716.2, introduction and (a)-(d)', [
            ([0], 'scope', 'Standards govern the permittee conducting surface coal mining/reclamation on natural slopes exceeding 20 degrees OR lesser slopes requiring protection measures as determined by the regulatory authority after considering soils, climate, method, geology and other regional characteristics. Preserve these inherited limits on the listed standards.'),
            ([0], 'exception', 'The section does not apply to flat/gently rolling terrain with an occasional steep slope where mining leaves a plain/predominantly flat area OR mining governed by 716.3. Preserve both alternatives and unresolved remote reference; do not exempt every slope below 20 degrees.'),
            ([0, 1], 'prohibition', 'Within the section applicability, spoil, waste/debris including clearing/grubbing material and abandoned/disabled equipment shall not be placed OR allowed to remain downslope.'),
            ([0, 2], 'requirement', 'Within the section applicability, completely cover the highwall with spoil AND grade the disturbed area to comply with 715.14. Keep the reference unresolved.'),
            ([0, 2], 'exception', 'Within the section applicability, do not disturb land above the highwall unless the authority finds disturbance will facilitate compliance. The exception qualifies this prohibition, not the duty to cover the highwall.'),
            ([0, 3], 'requirement', 'Dispose of material in excess of that required by 715.14 according to 715.15, within the section applicability; no invented amount or disposal method.'),
            ([0, 4], 'permission', 'Woody materials may be buried in backfill only when burial does not cause OR add to backfill instability, within the section applicability; no duty to bury them.'),
            ([0, 4], 'permission', 'Woody materials may be chipped AND distributed through backfill when the regulatory authority approves, within the section applicability; approval is not permission for burial that creates instability.'),
        ]),
        ('authorizations', 'cfr-xml-medium.xml', list(range(12, 20)), '45 CFR 164.508(b)(1)-(2)', [
            ([0], 'definition', 'A valid authorization meets (a)(3)(ii), (a)(4)(ii), (c)(1) and (c)(2), as applicable. Preserve all four unresolved references and the applicability qualification.'),
            ([1], 'permission', 'A valid authorization may contain additional elements/information provided they are not inconsistent with required elements. This is qualified permission, not a mandatory extra-information requirement.'),
            ([2, 3, 4, 5, 6, 7], 'condition', 'ANY of five listed defects invalidates authorization; do not require all five. Preserve each leaf, the nested expiration-date OR known-expiration-event alternatives, and each knowledge/applicability qualifier.'),
            ([2, 3], 'condition', 'Authorization is invalid when its expiration date has passed OR the covered entity knows its expiration event occurred; knowledge applies to the event, not a new universal knowledge requirement for both branches.'),
            ([2, 4], 'condition', 'Authorization is invalid when incomplete with respect to an element in paragraph (c), if applicable. Do not make any missing optional element fatal.'),
            ([2, 5], 'condition', 'Authorization is invalid when known by the covered entity to have been revoked; preserve the knowledge predicate.'),
            ([2, 6], 'condition', 'Authorization is invalid when it violates (b)(3) OR (b)(4), if applicable. The remote provisions remain unresolved.'),
            ([2, 7], 'condition', 'Authorization is invalid if ANY material information is known by the covered entity to be false. Retain both materiality and knowledge; no rule that all uncertainty invalidates it.'),
        ]),
        ('marketing', 'cfr-xml-medium.xml', list(range(7, 11)), '45 CFR 164.508(a)(3)', [
            ([0, 1, 2], 'requirement', 'A covered entity must obtain authorization for any use OR disclosure of protected health information for marketing, notwithstanding the subpart other than transition provisions in 164.532, subject to either of the two communication exceptions.'),
            ([0, 1], 'exception', 'Face-to-face communication by a covered entity to an individual is an exception to the marketing authorization requirement. Preserve its actor and recipient and explicit target.'),
            ([0, 2], 'exception', 'A promotional gift of NOMINAL value provided by the covered entity is an alternative exception to the marketing authorization requirement. Do not invent a monetary amount, require face-to-face delivery too, or exempt every gift.'),
            ([3], 'requirement', 'If marketing involves financial remuneration as defined by 164.501 from a third party to the covered entity, the authorization must state that remuneration is involved. Preserve direction, definition reference and conditional scope; do not transfer this to every communication or promise the source settles interaction with the exceptions.'),
        ]),
    ]
    receipts = []
    for name, filename, indices, citation, expectations in selected:
        native = CACHE / filename
        destination = output / filename
        if not destination.exists():
            shutil.copyfile(native, destination)
        tree = ET.parse(native)
        all_paragraphs = [' '.join(''.join(node.itertext()).split()) for node in tree.getroot().iter('P')]
        paragraphs = [all_paragraphs[i] for i in indices]
        text = '\n\n'.join(paragraphs)
        doc = prepare_document(text, title=citation + ' — retained local snapshot')
        spans, offset = [], 0
        for paragraph in paragraphs:
            spans.append({'source_id': doc['id'], 'start': offset, 'end': offset + len(paragraph), 'quote': paragraph})
            offset += len(paragraph) + 2
        expected = {'schema_version': 'rulespec-evaluation-labels/1', 'dataset_id': 'refinement-fresh-' + name,
                    'split': 'fresh-before-first-extraction', 'label_provenance': {
                        'reviewer': 'Codex pre-extraction source adjudication', 'reviewer_kind': 'aiAgent', 'method': 'source_review'},
                    'sources': [{'id': doc['id'], 'text': text, 'sha256': doc['sha256']}],
                    'expected_units': [{'id': name + f'-{i+1:02d}', 'kind': kind, 'meaning': meaning,
                                       'source_spans': [spans[p] for p in positions]}
                                      for i, (positions, kind, meaning) in enumerate(expectations)]}
        validate_expected(expected)
        e._save(output / (name + '.json'), doc)
        e._save(output / (name + '.labels.json'), expected)
        receipts.append({'name': name, 'citation': citation, 'native_path': str(native),
            'native_sha256': e._digest(native.read_bytes()), 'native_copy': filename, 'paragraph_indices_zero_based': indices,
            'conversion': 'ElementTree P itertext; collapse XML whitespace; join exact normalized paragraphs with two newlines.',
            'source_sha256': doc['sha256'], 'labels_sha256': e._digest(expected),
            'expected_units': len(expectations)})
    e._save(output / 'freeze.json', {'frozen_at': e._now(), 'sources': receipts,
        'prior_rulespec_extraction': False,
        'scope': 'Historical local source snapshots, newly used for this Rulespec extraction evaluation. Expectations stay outside extraction/refinement requests.'})
    e._write_manifest(output)
    print([(r['name'], r['expected_units']) for r in receipts])


if __name__ == '__main__':
    main()
