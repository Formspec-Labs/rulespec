"""Prepared text stays readable; only original source becomes evidence."""
from copy import deepcopy

import pytest

from rulespec_extrapolator.core import _evidence
from rulespec_extrapolator.discovery import export_discovery, records, verified
from rulespec_extrapolator.documents import prepare_document, source_passages


def mapped_document(parts):
    doc = prepare_document(''.join(text for _, text in parts))
    doc['source_map'] = []
    start = 0
    for index, (kind, text) in enumerate(parts):
        end = start + len(text)
        part = {'kind': kind, 'start': start, 'end': end}
        if kind == 'source':
            part.update(source_id=f'urn:test:source:{index}', source_start=0, source_end=len(text))
        else:
            part['text'] = text
        doc['source_map'].append(part)
        start = end
    return doc


@pytest.mark.parametrize('parts', [
    [('source', 'sec. 103 of the 2020 PIPES Act'), ('inserted', '\n\n'),
     ('source', 'SECURE 2.0 Act of 2022, sec. 127'), ('inserted', '\n\n'),
     ('source', 'SECURE 2.0 Act of 2022, sec. 303')],
    [('source', 'First.\n\nSecond.')],
    [('source', 'First.'), ('inserted', '\n\n'), ('source', 'Second.')],
    [('source', 'First'), ('inserted', ' editorial addition '), ('source', 'Second')],
    [('source', 'First '), ('source', 'Second')],
    [('inserted', 'Entirely inserted.')],
    [('inserted', 'Heading\n\n'), ('source', 'Original.'), ('inserted', '\n\nFootnote')],
    [('source', 'Café § 😀.'), ('inserted', '\n\n'), ('source', 'Café § 😀.')],
], ids=['original-cli-failure', 'original-whitespace', 'inserted-whitespace',
        'inserted-within-passage', 'adjacent-sources', 'all-inserted',
        'inserted-first-last', 'unicode-repeated'])
def test_source_map_preserves_passages_and_exact_source_coverage(parts):
    doc = mapped_document(parts)
    book = {'document': doc, 'accepted': []}
    before = deepcopy(book)
    passages = source_passages(doc)
    exported = export_discovery(book)
    assert book == before
    assert exported['statements'] == []
    assert ''.join(row['text'] for row in exported['records']) == doc['text']
    assert [(row['id'], row['start'], row['end'], row['parent_id']) for row in exported['records']] == [
        (p['id'], p['start'], p['end'], p['parent_id']) for p in passages]
    expected = {i for p in doc['source_map'] if p['kind'] == 'source' for i in range(p['start'], p['end'])}
    spans = exported['evidence']
    assert {i for span in spans.values() for i in range(span['start'], span['end'])} == expected
    for mode in ('source', 'packets'):
        observed = set()
        for row in records(book, doc['id'], mode):
            for support in row['evidence']:
                assert _evidence(doc, support['quote'], support['field'], support['start'], support['end'])
                observed.update(range(support['start'], support['end']))
        assert observed == expected
    for row in exported['records']:
        for ref in row['evidence_refs']:
            assert ref['roles'] == ['source']
            assert row['id'] in spans[ref['id']]['record_ids']


def test_complete_source_map_keeps_the_existing_export():
    doc = prepare_document('A paragraph.\n\nA second paragraph.')
    ordinary = export_discovery({'document': doc, 'accepted': []})
    mapped = mapped_document([('source', doc['text'])])
    assert export_discovery({'document': mapped, 'accepted': []}) == ordinary


def test_verified_does_not_relocate_or_trust_a_supplied_fragment_id():
    doc = mapped_document([('source', 'Original. '), ('inserted', 'Inserted. '), ('source', 'Original.')])
    book = {'document': doc, 'accepted': []}
    real = {'field': 'summary', 'quote': 'Original.', 'start': 0, 'end': 9}
    wrong_position = {**real, 'start': 10, 'end': 19}
    inserted = {'field': 'summary', 'quote': 'Inserted.', 'start': 10, 'end': 19,
                'fragment_id': 'urn:test:unverified-fragment'}
    supported = verified(book, [real, wrong_position, inserted])
    assert len(supported) == 1
    assert (supported[0]['start'], supported[0]['end']) == (0, 9)
    assert supported[0]['fragment_id'] == _evidence(doc, 'Original.', 'summary', 0, 9)['fragment_id']
