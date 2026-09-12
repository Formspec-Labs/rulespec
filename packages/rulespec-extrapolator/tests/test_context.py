"""Request coverage is separate from the governing context it makes available."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from test_extraction import row

from rulespec_extrapolator.documents import prepare_document, source_passages
from rulespec_extrapolator.extraction import plan_windows, parse_response_text, _window_prompt


def test_source_passages_preserve_every_character_and_nested_list_parent():
    text = "a. Provide one or more documents:\n\n(1) Court records:\n\n(a) A name order; or\n\n(b) A divorce decree.\n\nb. A different case."
    doc = prepare_document(text)
    passages = source_passages(doc)
    assert ''.join(text[p['start']:p['end']] for p in passages) == text
    assert passages[1]['parent_id'] == passages[0]['id']
    assert passages[2]['parent_id'] == passages[1]['id']
    assert passages[3]['parent_id'] == passages[1]['id']
    assert passages[4]['parent_id'] is None


def test_note_is_structural_metadata_without_invented_rule_scope():
    text = 'b. Language rules.\n\n(1) Agencies must request approval.\n\nNOTE : Letters are not adjudicative guidance.'
    doc = prepare_document(text)
    passages = source_passages(doc)
    assert passages[1]['parent_id'] == passages[0]['id']
    assert passages[2]['kind'] == 'note' and passages[2]['parent_id'] is None
    assert ''.join(text[p['start']:p['end']] for p in passages) == text


def test_condition_outside_focus_is_present_as_context_and_can_support_child():
    text = "a. If a card is lost, the service pauses.\n\n(1) The visitor must request a replacement."
    doc = prepare_document(text)
    windows = plan_windows(doc, 45)
    target = next(w for w in windows if 'must request' in text[w['start']:w['end']])
    class Generator:
        def render(self, text, additional_context):
            return text + '\n' + additional_context
    prompt = _window_prompt(Generator(), doc, target)
    assert 'If a card is lost' in prompt
    quote = 'The visitor must request a replacement.'
    payload = {'terms': [], 'extractions': [row(statement='If a card is lost, the visitor must request a replacement.',
        scope_text='If a card is lost', scope_quotes=['C000'])]}
    parsed = parse_response_text(json.dumps(payload), doc, target)
    assert len(parsed['candidates']) == 1
    assert not parsed['refusals']
    assert 'If a card is lost' in parsed['candidates'][0]['scope_quotes'][0]
    without_context = deepcopy(target)
    without_context['context_spans'] = []
    partial = parse_response_text(json.dumps(payload), doc, without_context)
    assert len(partial['candidates']) == 1
    assert partial['status'] == 'partial'
    assert partial['candidates'][0]['scope_quotes'] == []
    assert partial['candidates'][0]['scope_text'] == 'If a card is lost'
    assert partial['refusals'][0]['code'] == 'component_reference_unresolved'
    assert partial['refusals'][0]['raw'] == payload['extractions'][0]


def test_context_limit_is_recorded_without_claiming_complete_context():
    text = 'a. ' + 'An extended governing lead-in. ' * 100 + '\n\n(1) A child statement.'
    doc = prepare_document(text)
    windows = plan_windows(doc, 40)
    last = windows[-1]
    assert sum(s['end'] - s['start'] for s in last['context_spans']) <= 2400
    assert last['context_omitted_passage_ids']


@pytest.mark.parametrize('sample,expected', [
    ('baggage', {1: None, 2: 1, 3: 1, 4: 1, 5: None, 6: 5, 7: 5, 8: 5,
                 9: None, 10: 9, 11: 9, 12: 11, 13: 11, 14: 11, 15: 11,
                 16: 9, 17: None}),
    ('leave', {1: None, 2: 1, 3: 1, 4: 1, 5: None, 6: 5, 7: 5,
               8: 7, 9: 7, 10: 5, 11: 5}),
])
def test_saved_cfr_lists_keep_siblings_and_roman_children(sample, expected):
    root = Path(__file__).resolve().parents[3]
    doc = json.loads((root / 'examples/document_understanding/composed-extraction-experiment' /
                      (sample + '.json')).read_text())
    passages = source_passages(doc)
    assert ''.join(doc['text'][p['start']:p['end']] for p in passages) == doc['text']
    for child, parent in expected.items():
        assert passages[child]['parent_id'] == (None if parent is None else passages[parent]['id'])


def test_cfr_split_roman_child_gets_both_governing_lead_ins():
    from rulespec_extrapolator.documents import with_context
    doc = prepare_document('(c) In checked baggage:\n\n(1) Loaded firearms.\n\n'
        '(2) Unloaded firearms unless:\n\n(i) Declared.\n\n(ii) Unloaded.\n\n'
        '(iii) Hard-sided container.\n\n(iv) Locked container.\n\n(d) Other rules.')
    passages = source_passages(doc)
    child = passages[6]
    window = with_context(doc, {'start': child['start'], 'end': child['end']})
    supplied = {p['passage_id'] for p in window['context_spans']}
    assert passages[0]['id'] in supplied
    assert passages[2]['id'] in supplied
    assert passages[7]['parent_id'] is None


def test_top_level_i_and_section_reset_do_not_inherit_previous_number():
    text = '(h) First case.\n\n(1) Its child.\n\n(i) Next case.\n\n(1) Next child.'
    doc = prepare_document(text)
    passages = source_passages(doc)
    assert passages[2]['parent_id'] is None
    assert passages[3]['parent_id'] == passages[2]['id']
    split = text.index('(i)')
    doc = prepare_document(text, sections=[{'id':'one','label':'one','start':0,'end':split},
        {'id':'two','label':'two','start':split,'end':len(text)}])
    passages = source_passages(doc)
    assert passages[2]['parent_id'] is None


def test_fitting_cfr_group_moves_to_next_window_without_extra_requests():
    root = Path(__file__).resolve().parents[3]
    doc = json.loads((root / 'examples/document_understanding/composed-extraction-experiment/baggage.json').read_text())
    windows = plan_windows(doc, 1900)
    assert [(w['start'], w['end']) for w in windows] == [(0, 1376), (1376, len(doc['text']))]
    tail = doc['text'][windows[1]['start']:windows[1]['end']]
    for wording in ('(c) In checked baggage', '(i) The passenger declares', '(iv) The container'):
        assert wording in tail
    assert ''.join(doc['text'][w['start']:w['end']] for w in windows) == doc['text']


def test_oversized_list_keeps_hard_limit_and_exact_unicode_coverage():
    text = 'Intro ☃.\n\n(a) All following conditions:\n\n' + '\n\n'.join(
        f'({i}) ' + 'A source condition. ' * 8 for i in range(1, 8))
    doc = prepare_document(text)
    windows = plan_windows(doc, 100)
    assert all(0 < w['end'] - w['start'] <= 100 for w in windows)
    assert ''.join(text[w['start']:w['end']] for w in windows) == text
    assert windows == plan_windows(doc, 100)


def test_default_window_keeps_a_moderate_document_intact():
    text = 'A source paragraph.\n\n' * 400
    windows = plan_windows(prepare_document(text))
    assert len(text) > 6000
    assert [(w['start'], w['end']) for w in windows] == [(0, len(text))]


def test_section_windows_preserve_sections_preamble_gaps_and_global_offsets():
    text = 'Intro ☃.\n\nFirst section.\n\nGap text.\n\nSecond section.\n\n'
    first, second = text.index('First'), text.index('Second')
    doc = prepare_document(text, sections=[
        {'id': 'two', 'label': 'two', 'start': second, 'end': len(text) - 2},
        {'id': 'one', 'label': 'one', 'start': first, 'end': text.index('Gap')}])
    windows = plan_windows(doc, section_windows=True)
    assert [(w['start'], w['end']) for w in windows] == [(0, first), (first, second), (second, len(text))]
    assert ''.join(text[w['start']:w['end']] for w in windows) == text
    assert windows == plan_windows(doc, section_windows=True)
    assert len(plan_windows(doc)) == 1


def test_section_windows_respect_nested_starts_and_split_oversized_sections_with_context():
    text = '(a) If a card is lost:\n\n' + '(1) The visitor must request a replacement.\n\n' * 4
    nested = text.index('(1)')
    doc = prepare_document(text, sections=[
        {'id': 'parent', 'label': 'parent', 'start': 0, 'end': len(text)},
        {'id': 'child', 'label': 'child', 'start': nested, 'end': len(text)},
        {'id': 'duplicate-start', 'label': 'duplicate', 'start': nested, 'end': len(text) - 1}])
    windows = plan_windows(doc, 50, section_windows=True)
    assert windows[0]['end'] == nested
    assert windows[1]['start'] == nested
    assert all(0 < w['end'] - w['start'] <= 50 for w in windows)
    assert ''.join(text[w['start']:w['end']] for w in windows) == text
    assert all(w['context_version'] == 'document-context/1' for w in windows)
    # A single supplied section does not add another split policy to plain text.
    plain = prepare_document(text)
    assert plan_windows(plain, 50, section_windows=True) == plan_windows(plain, 50)


def test_combined_cfr_marker_starts_new_group_without_inheriting_previous_case():
    doc = prepare_document('(b) Prior case.\n\n(4) Prior child.\n'
        '(c)(1) A new case.\n\n(i) First detail.\n\n(ii) Second detail.\n\n'
        '(2) Another child of c.\n\n(d) Next case.')
    ps = source_passages(doc)
    assert [p['parent_id'] for p in ps] == [None, ps[0]['id'], None,
        ps[2]['id'], ps[2]['id'], ps[2]['id'], None]
