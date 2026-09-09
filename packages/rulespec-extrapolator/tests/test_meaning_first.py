"""Source references and component isolation preserve meaning without inventing support."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.discovery import export_discovery
from test_extraction import row


@pytest.mark.parametrize('field,value', [('modality_quote', 'must always'), ('logic_quote', 'F999'),
    ('scope_quotes', ['C999']), ('alternative_quotes', ['F999']), ('choice_quote', 'F999')])
def test_bad_component_preserves_main_statement_and_original_suggestion(field, value):
    doc = prepare_document('Staff must log requests.')
    item = row(**{field: value})
    parsed = e.parse_response_text(json.dumps({'extractions': [item]}), doc, e.plan_windows(doc)[0])
    assert parsed['status'] == 'partial'
    assert parsed['candidates'][0]['summary'] == item['unit_attributes']['statement']
    assert parsed['candidates'][0]['logic_text' if field == 'logic_quote' else field] == ([] if isinstance(value, list) else '')
    assert parsed['refusals'][0]['raw'] == item
    assert parsed['refusals'][0]['disposition'] == 'component_withheld'
    book = compile_candidates(doc, parsed['candidates'], {})
    assert len(book['accepted']) == 1 and not book['rejected']
    assert 'unknown_actor' not in {i['code'] for i in book['accepted'][0]['issues']}


def test_context_range_cannot_bridge_unsupplied_text_and_focus_is_clipped():
    doc = prepare_document('Before.\n\nUnseen material.\n\nStaff must log requests.\n\nAfter.')
    start = doc['text'].index('Staff')
    window = {'start': start, 'end': start + len('Staff must log requests.'), 'context_spans': [
        {'start': 0, 'end': len('Before.')}, {'start': doc['text'].index('After'), 'end': len(doc['text'])}]}
    catalog = e.passage_catalog(doc, window)
    assert catalog['F000']['text'] == 'Staff must log requests.'
    assert 'Unseen' not in json.dumps(catalog)
    with pytest.raises(ValueError, match='unsupplied_text'):
        e.resolve_passage('C000:C001', catalog, doc)
    with pytest.raises(ValueError, match='invalid_passage_reference'):
        e.resolve_passage('C000', catalog, doc, focus=True)
    with pytest.raises(ValueError, match='passage_not_in_request'):
        e.resolve_passage('F0000', catalog, doc)


def test_unicode_and_crlf_ranges_resolve_original_text_without_normalization():
    doc = prepare_document('☃ First.\r\n\r\nSecond.\r\n\r\nThird.')
    catalog = e.passage_catalog(doc, e.plan_windows(doc)[0])
    span = e.resolve_passage('F000:F001', catalog, doc, focus=True)
    assert span['quote'] == '☃ First.\r\n\r\nSecond.'
    assert doc['text'][span['start']:span['end']] == span['quote']


@pytest.mark.parametrize('sample,index', [('names', 7), ('leave', 0), ('leave', 3)])
def test_saved_good_statements_survive_bad_optional_enrichment(sample, index):
    # Diagnostic selection of the same model's meanings, not a legacy runtime adapter.
    saved = Path(__file__).resolve().parents[3] / 'examples/document_understanding/composed-extraction-experiment'
    doc = e._load(saved / f'{sample}.json')
    original = e._load(saved / f'runs/{sample}/all/output.json')['extractions'][index]
    attrs = {k: deepcopy(original['unit_attributes'][k]) for k in e.PROVIDER_FIELDS if k != 'logic_quote'}
    attrs['logic_quote'] = original['unit'].replace('P', 'F') if original['unit_attributes']['logic_text'] else ''
    for field in ('scope_quotes', 'context_quotes', 'alternative_quotes'):
        attrs[field] = [ref.replace('P', 'F') for ref in attrs[field]]
    attrs['choice_quote'] = attrs['choice_quote'].replace('P', 'F')
    item = {'unit': original['unit'].replace('P', 'F'), 'unit_attributes': attrs}
    parsed = e.parse_response_text(json.dumps({'extractions': [item]}), doc, e.plan_windows(doc, len(doc['text']))[0])
    book = compile_candidates(doc, parsed['candidates'], {})
    assert not book['rejected'] and len(book['accepted']) == 1
    claim = book['accepted'][0]
    assert claim['summary'] == original['unit_attributes']['statement']
    assert claim['scope_text'] == original['unit_attributes']['scope_text']
    assert claim['modality'] == original['unit_attributes']['modality']
    assert not parsed['refusals']
    assert claim['logic_text'] == claim['quote']
    assert not claim['concepts'] and not claim['object']


def test_discovery_export_keeps_unlinked_source_and_pending_meaning_separate():
    doc = prepare_document('Staff must log requests.\n\nA substantive note not extracted.')
    window = e.plan_windows(doc)[0]
    parsed = e.parse_response_text(json.dumps({'extractions': [row()]}), doc, window)
    book = compile_candidates(doc, parsed['candidates'], {'windows': [{**window, 'status': 'complete'}]})
    export = export_discovery(book)
    assert export['accounting']['processed_passages'] == 2
    assert export['accounting']['passages_without_linked_statements'] == 1
    assert export['accounting']['semantic_completeness'] == 'not_established'
    assert ''.join(r['text'] for r in export['records']) == doc['text']
    assert export['statements'][0]['logic_text'] == book['accepted'][0]['logic_text']
    assert export['statements'][0]['review_status'] == 'pending'
    assert export['statements'][0]['statement'] == row()['unit_attributes']['statement']
