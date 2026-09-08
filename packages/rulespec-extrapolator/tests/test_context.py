"""Request coverage is separate from the governing context it makes available."""
from copy import deepcopy
import json

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
    payload = {'extractions': [row(quote,
        summary='If a card is lost, the visitor must request a replacement.', actor='The visitor',
        actor_quote='The visitor', action='request', action_quote='request',
        object='a replacement', object_quote='a replacement', modality='must', modality_quote='must',
        scope_text='If a card is lost', scope_quotes=['If a card is lost'])]}
    parsed = parse_response_text(json.dumps(payload), doc, target)
    assert len(parsed['candidates']) == 1
    assert not parsed['refusals']
    assert parsed['candidates'][0]['scope_quotes'] == ['If a card is lost']
    without_context = deepcopy(target)
    without_context['context_spans'] = []
    refused = parse_response_text(json.dumps(payload), doc, without_context)
    assert not refused['candidates']
    assert refused['refusals'][0]['code'] == 'component_quote_outside_request'


def test_context_limit_is_recorded_without_claiming_complete_context():
    text = 'a. ' + 'An extended governing lead-in. ' * 100 + '\n\n(1) A child statement.'
    doc = prepare_document(text)
    windows = plan_windows(doc, 40)
    last = windows[-1]
    assert sum(s['end'] - s['start'] for s in last['context_spans']) <= 2400
    assert last['context_omitted_passage_ids']
