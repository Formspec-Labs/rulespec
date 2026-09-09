"""Model judgments stay separate from processing and replay without providers."""
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.evaluation import MEANING_DIMENSIONS


def draft():
    text = 'Visitors must present one or more of: a receipt; or an invoice.'
    doc = prepare_document(text)
    c = {'kind': 'requirement', 'modality': 'must', 'modality_quote': 'must', 'summary': 'Visitors must present a receipt.',
         'quote': text, 'actor': 'Visitors', 'actor_quote': 'Visitors', 'alternative_quotes': ['a receipt'],
         'choice_text': 'one or more of: a receipt; or an invoice', 'choice_quote': 'one or more of: a receipt; or an invoice'}
    return compile_candidates(doc, [c], {})


def answers():
    inventory = {'units': [{'quote_ref': 'F000', 'meaning': 'An invoice is an acceptable alternative.',
                           'kind': 'alternative', 'scope_refs': []}]}
    comparison = {'claim_judgments': [{'claim_id': 'C0000', 'unit_ids': [], 'dimensions': {
        d: 'error' if d == 'alternatives' else 'correct' for d in MEANING_DIMENSIONS},
        'rationale': 'The meaning narrows the choice to a receipt; the quote alone does not restore the missing alternative.',
        'source_refs': ['F000']}],
        'unit_judgments': [{'unit_id': 'U0000', 'claim_ids': [], 'status': 'missing',
        'rationale': 'The draft meaning omits invoices despite their presence in the source quotation.', 'source_refs': ['F000']}]}
    return inventory, comparison


def provider(monkeypatch, tmp_path, responses):
    responses = iter(responses)
    requests = []
    class Model:
        def __init__(self, schema):
            self.schema = schema
            self._client = SimpleNamespace(models=SimpleNamespace(generate_content=self.generate))
        def generate(self, **kwargs):
            requests.append(deepcopy(kwargs))
            value = next(responses)
            if isinstance(value, Exception):
                raise value
            raw = {'candidates': [{'content': {'parts': [{'text': json.dumps(value)}]}, 'finish_reason': 'STOP'}],
                   'model_version': 'gemini-3.8-flash'}
            return SimpleNamespace(model_dump=lambda **_: raw)
        def infer(self, prompts, **config):
            for prompt in prompts:
                yield self._client.models.generate_content(model=e.DEFAULT_MODEL, contents=prompt,
                       config={**config, **self.schema.to_provider_config()})
    monkeypatch.setattr(e, '_create_model', lambda model, key, schema: Model(schema))
    env = tmp_path / 'test.env'
    env.write_text('GEMINI_API_KEY=synthetic-test-credential\n')
    return env, requests


@pytest.mark.parametrize("settings", [{}, *[{"thinking_level": v, "max_output_tokens": None} for v in (None, "low", "medium", "high")]])
def test_missing_alternative_is_visible_despite_complete_processing_and_exact_quote(monkeypatch, tmp_path, settings):
    book = draft()
    before = deepcopy(book)
    env, requests = provider(monkeypatch, tmp_path, answers())
    report = a.audit_run(book, tmp_path / 'audit', env_file=env, **settings)
    level = settings.get('thinking_level', 'medium')
    for request in requests:
        assert request['config'].get('thinking_config') == ({'thinking_level': level} if level is not None else None)
        assert 'thinking_budget' not in request['config'].get('thinking_config', {})
        assert request['config'].get('max_output_tokens') == settings.get('max_output_tokens', 32768)
    assert e._load(tmp_path / 'audit/audit.json')['thinking_level'] == level
    assert report['status'] == 'failed'
    assert report['coverage']['missing'] == 1
    assert report['dimensions']['alternatives']['error'] == 1
    assert report['semantic_completeness'] == 'not_established'
    assert e._load(tmp_path / 'audit/audit.json')['status'] == 'complete'
    assert 'C0000' not in requests[0]['contents']
    assert 'Draft and inventory:' not in requests[0]['contents']
    assert 'C0000' in requests[1]['contents']
    assert 'CUE-generated field definitions:' in requests[1]['contents']
    assert a.load_schema('meaning')['properties']['choice_text']['description'] in requests[1]['contents']
    assert 'CUE-generated field definitions:' not in requests[0]['contents']
    assert book == before
    findings = e._load(tmp_path / 'audit/findings.jsonld')
    nodes = [n for n in findings['@graph'] if n['@type'] == 'rkaf:Finding']
    assert len(nodes) == 2
    assert {n['rkaf:subject'] for n in nodes} == {book['document']['id'], book['accepted'][0]['id']}
    assert all(n['rkaf:findingKind'] == 'rkaf:warning' for n in nodes)
    assert all('Model-assisted audit' in n['rkaf:rationale'] for n in nodes)
    assert a.validate_graph(findings)['shacl_conforms']
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called a provider'))
    assert a.replay_audit(tmp_path / 'audit', tmp_path / 'replay') == report
    assert e._load(tmp_path / 'replay/findings.jsonld') == findings


@pytest.mark.parametrize("settings", [{"thinking_level": "extreme"}, {"thinking_level": True},
    {"max_output_tokens": 0}, {"max_output_tokens": True}])
def test_invalid_audit_settings_refused_before_creating_run(tmp_path, settings):
    with pytest.raises(ValueError):
        a.audit_run(draft(), tmp_path / 'invalid', **settings)
    assert not (tmp_path / 'invalid').exists()


def test_replay_rejects_changed_audit_thinking_metadata(monkeypatch, tmp_path):
    env, _ = provider(monkeypatch, tmp_path, answers())
    path = tmp_path / 'audit'
    a.audit_run(draft(), path, env_file=env, thinking_level='high', max_output_tokens=None)
    run = e._load(path / 'audit.json')
    run['thinking_level'] = 'low'
    e._save(path / 'audit.json', run)
    e._write_manifest(path)
    with pytest.raises(e.ReplayDriftError, match='request differs'):
        a.replay_audit(path, tmp_path / 'tampered')


def test_audit_provider_failure_retains_terminal_attempts_and_unknown_meaning(monkeypatch, tmp_path):
    env, requests = provider(monkeypatch, tmp_path, [RuntimeError('Unavailable'), {'claim_judgments': [], 'unit_judgments': []}])
    report = a.audit_run(draft(), tmp_path / 'failed', env_file=env)
    assert report['status'] == 'needs_review'
    assert report['review_complete'] is False
    run = e._load(tmp_path / 'failed/audit.json')
    assert run['status'] == 'partial'
    assert len(run['inventory_attempts']) == len(run['comparison_attempts']) == 1
    assert run['inventory_attempts'][0]['error_code'] == 'provider_request_failed'
    assert a.replay_audit(tmp_path / 'failed', tmp_path / 'replay-failed') == report


def test_changed_raw_audit_response_cannot_replay(monkeypatch, tmp_path):
    env, _ = provider(monkeypatch, tmp_path, answers())
    a.audit_run(draft(), tmp_path / 'audit', env_file=env)
    (tmp_path / 'audit/inventory/attempt-0000.response.json').write_text('{}')
    with pytest.raises(e.ReplayDriftError, match='capture changed'):
        a.replay_audit(tmp_path / 'audit', tmp_path / 'replay')


def test_unjudged_inventory_item_is_unknown_not_missing_or_covered(monkeypatch, tmp_path):
    inv, comparison = answers()
    comparison['unit_judgments'] = []
    env, _ = provider(monkeypatch, tmp_path, [inv, comparison])
    report = a.audit_run(draft(), tmp_path / 'audit', env_file=env)
    assert report['coverage']['unknown'] == 1
    assert report['coverage']['covered'] == report['coverage']['missing'] == 0
    assert not report['review_complete']


def test_checker_receives_existing_reference_and_component_evidence():
    text = 'Visitors must present a receipt (see Part 2 for acceptable receipts).'
    book = compile_candidates(prepare_document(text), [{
        'kind': 'requirement', 'modality': 'must', 'modality_quote': 'must',
        'summary': 'Visitors must present a receipt; Part 2 describes acceptable receipts.',
        'quote': text, 'actor': 'Visitors', 'actor_quote': 'Visitors',
        'action': 'present', 'action_quote': 'present',
        'object': 'a receipt', 'object_quote': 'a receipt',
        'references': ['Part 2'],
    }], {})
    window = e.plan_windows(book['document'])[0]
    packet, _, _ = a._comparison_input(book, {'expected_units': []}, window)
    claim = book['accepted'][0]
    row = packet['claims']['C0000']
    # The checker previously accused a correctly retained citation of being
    # absent because the handoff dropped references and component anchors.
    assert row['references'] == ['Part 2']
    for field in ['reference_links', 'actor_quote', 'action_quote', 'object_quote', 'evidence', 'section_id', 'start', 'end']:
        assert row[field] == claim[field]


def inventory_capture(tmp_path, document, window, **changes):
    row = {'quote_ref': 'F000', 'scope_refs': [], 'kind': 'requirement', 'meaning': 'Staff must log requests.', **changes}
    raw = {'candidates': [{'content': {'parts': [{'text': json.dumps({'units': [row]})}]}, 'finish_reason': 'STOP'}]}
    e._save(tmp_path / 'response.json', raw)
    result = a._inventory(tmp_path, document, [window], [{'response_file': 'response.json'}])
    assert e._load(tmp_path / 'response.json') == raw
    return result


def test_inventory_passage_ids_disambiguate_repeated_text_and_preserve_scope(tmp_path):
    doc = prepare_document('For licensed staff:\n\nStaff must log requests.\n\nFor volunteers:\n\nStaff must log requests.')
    window = e.plan_windows(doc)[0]
    result = inventory_capture(tmp_path, doc, window, quote_ref='F003', scope_refs=['F002', 'F003', 'F002'])
    assert not result['issues'] and len(result['units']) == 1
    spans = result['units'][0]['source_spans']
    assert len(spans) == 2
    assert spans[0]['start'] == doc['text'].rindex('Staff must log requests.')
    assert spans[1]['quote'] == 'For volunteers:'
    assert all(doc['text'][s['start']:s['end']] == s['quote'] for s in spans)
    assert result['completeness'] == 'not_established'


@pytest.mark.parametrize('change', [{'quote_ref': 'F999'}, {'quote_ref': 'C000'},
    {'scope_refs': ['C000:C001']}, {'scope_refs': ['F999']}, {'quote_ref': 'F0000'}])
def test_inventory_refuses_unavailable_or_out_of_focus_evidence(tmp_path, change):
    doc = prepare_document('Before.\n\nUnseen material.\n\nStaff must log requests.\n\nAfter.')
    start = doc['text'].index('Staff')
    window = {'id': 'focus', 'start': start, 'end': start + len('Staff must log requests.'),
              'context_spans': [{'start': 0, 'end': len('Before.')},
                                {'start': doc['text'].index('After'), 'end': len(doc['text'])}]}
    result = inventory_capture(tmp_path, doc, window, **change)
    assert not result['units']
    assert result['issues'][0]['code'] == 'invalid_inventory_unit'
    assert result['issues'][0]['row_index'] == 0


def test_inventory_never_treats_inserted_text_as_source(tmp_path):
    doc = prepare_document('Staff must log requests.')
    doc['source_map'] = [{'kind': 'inserted', 'start': 0, 'end': len(doc['text']), 'text': doc['text']}]
    result = inventory_capture(tmp_path, doc, e.plan_windows(doc)[0])
    assert not result['units'] and result['issues'][0]['code'] == 'invalid_inventory_unit'


def comparison_capture(tmp_path, document, window, refs):
    quote = document['text'][window['start']:window['end']]
    book = compile_candidates(document, [{'kind': 'statement', 'summary': quote, 'quote': quote, 'actor': ''}], {})
    assert len(book['accepted']) == 1
    row = {'claim_id': 'C0000', 'unit_ids': [], 'source_refs': refs,
           'rationale': 'Constructed evidence selection, not a semantic quality judgment.',
           'dimensions': {d: 'correct' for d in MEANING_DIMENSIONS}}
    raw = {'candidates': [{'content': {'parts': [{'text': json.dumps({
        'claim_judgments': [row], 'unit_judgments': []})}]}, 'finish_reason': 'STOP'}]}
    e._save(tmp_path / 'response.json', raw)
    result = a._judgments(tmp_path, book, {'expected_units': []}, [window],
                          [{'response_file': 'response.json'}], e.DEFAULT_MODEL)
    assert e._load(tmp_path / 'response.json') == raw
    return result


def test_comparison_passage_ids_preserve_scope_and_select_repeated_occurrence(tmp_path):
    doc = prepare_document('Only for licensed staff:\n\nStaff must file.\n\nOnly for volunteers:\n\nStaff must file.')
    result, issues = comparison_capture(tmp_path, doc, e.plan_windows(doc)[0], ['F002:F003'])
    assert not issues
    span = result['claim_judgments'][0]['source_spans'][0]
    assert span['start'] == doc['text'].index('Only for volunteers:')
    assert span['end'] == len(doc['text'])
    assert span['quote'] == 'Only for volunteers:\n\nStaff must file.'


@pytest.mark.parametrize('refs', [[], ['F999'], ['bogus'], ['F0000'], ['C000:C001']])
def test_comparison_refuses_missing_invalid_and_unseen_evidence(tmp_path, refs):
    doc = prepare_document('Before.\n\nUnseen.\n\nStaff must file.\n\nAfter.')
    start = doc['text'].index('Staff')
    window = {'id': 'focus', 'start': start, 'end': start + len('Staff must file.'),
              'context_spans': [{'start': 0, 'end': len('Before.')},
                                {'start': doc['text'].index('After'), 'end': len(doc['text'])}]}
    judgments, issues = comparison_capture(tmp_path, doc, window, refs)
    assert not judgments['claim_judgments']
    assert issues[0]['code'] == 'invalid_semantic_judgment'


def test_comparison_preserves_supplied_context_as_separate_component(tmp_path):
    doc = prepare_document('Only during emergencies.\n\nUnseen.\n\nStaff may call.')
    start = doc['text'].index('Staff')
    window = {'id': 'focus', 'start': start, 'end': len(doc['text']),
              'context_spans': [{'start': 0, 'end': len('Only during emergencies.')}]}
    judgments, issues = comparison_capture(tmp_path, doc, window, ['F000', 'C000'])
    assert not issues
    assert [s['quote'] for s in judgments['claim_judgments'][0]['source_spans']] == [
        'Staff may call.', 'Only during emergencies.']


def test_comparison_refuses_inserted_source_text(tmp_path):
    prefix = 'Staff must file.\n\n'
    doc = prepare_document(prefix + 'Inserted marker.')
    doc['source_map'] = [
        {'kind': 'source', 'start': 0, 'end': len(prefix), 'source_start': 0,
         'source_end': len(prefix), 'source_id': doc['id']},
        {'kind': 'inserted', 'start': len(prefix), 'end': len(doc['text']), 'text': 'Inserted marker.'}]
    window = {'id': 'focus', 'start': 0, 'end': len('Staff must file.'),
              'context_spans': [{'start': len(prefix), 'end': len(doc['text'])}]}
    judgments, issues = comparison_capture(tmp_path, doc, window, ['C000'])
    assert not judgments['claim_judgments']
    assert issues[0]['code'] == 'invalid_semantic_judgment'


def test_valid_comparison_id_does_not_prove_semantic_relevance(tmp_path):
    doc = prepare_document('Staff must file.\n\nThe sky is blue.')
    judgments, issues = comparison_capture(tmp_path, doc, e.plan_windows(doc)[0], ['F001'])
    assert not issues
    assert judgments['claim_judgments'][0]['source_spans'][0]['quote'] == 'The sky is blue.'
    assert judgments['review_provenance']['reviewer_kind'] == 'aiAgent'


def test_compact_input_preserves_meaning_and_source_offsets_without_repeating_quotes():
    book = draft()
    window = e.plan_windows(book['document'])[0]
    original = deepcopy(book)
    labels = {'expected_units': []}
    packet = a._comparison_model_input(book, labels, window)
    claim = packet['claims']['C0000']
    assert claim['summary'] == book['accepted'][0]['summary']
    assert claim['choice_text'] == book['accepted'][0]['choice_text']
    assert claim['quote'] == {'source_ref': 'F000'}
    assert claim['evidence'][0]['quote'] == {'source_ref': 'F000'}
    assert claim['evidence'][0]['start'] == 0
    assert claim['actor_quote'] == 'Visitors'  # partial words remain explicit
    assert 'logic_text' not in claim and 'scope_text' not in claim
    assert 'concepts' not in claim and 'relation' not in claim
    assert book == original


def test_compact_quotes_do_not_collapse_repeated_locations_or_change_logic_role():
    text = 'Staff may enter.\n\nStaff may enter.'
    doc = prepare_document(text)
    book = compile_candidates(doc, [{'kind': 'permission', 'modality': 'may',
        'summary': 'Staff may enter.', 'actor': '', 'quote': 'Staff may enter.',
        'logic_text': 'Staff may enter.', 'start': pos, 'end': pos + 16}
        for pos in [0, 18]], {})
    assert len(book['accepted']) == 2
    packet = a._comparison_model_input(book, {'expected_units': []}, e.plan_windows(doc)[0])
    for alias, ref in [('C0000', 'F000'), ('C0001', 'F001')]:
        claim = packet['claims'][alias]
        assert claim['summary'] == 'Staff may enter.'
        assert claim['quote'] == claim['logic_text'] == {'source_ref': ref}
        assert claim['evidence'][0]['quote'] == {'source_ref': ref}


def test_compact_input_keeps_unknown_values_false_and_zero():
    book = draft()
    # Synthetic diagnostics: false/zero are values, not absent enrichment.
    book['accepted'][0]['issues'] = [{'code': 'example', 'observed': False, 'count': 0}]
    packet = a._comparison_model_input(book, {'expected_units': []}, e.plan_windows(book['document'])[0])
    assert packet['claims']['C0000']['issues'] == [{'code': 'example', 'observed': False, 'count': 0}]


def test_compact_quotes_preserve_ambiguous_and_outside_catalog_text():
    doc = prepare_document('Staff may enter.\n\nStaff may enter.\n\nVisitors must wait.')
    book = compile_candidates(doc, [{'kind': 'permission', 'modality': 'may',
        'summary': 'Staff may enter.', 'actor': '', 'quote': 'Staff may enter.', 'start': 0, 'end': 16}], {})
    # One quote matches the main locator; the other lies outside the catalog.
    book['accepted'][0]['context_quotes'] = ['Staff may enter.', 'Visitors must wait.']
    window = {'id': 'focus', 'start': 0, 'end': 16, 'context_spans': []}
    claim = a._comparison_model_input(book, {'expected_units': []}, window)['claims']['C0000']
    assert claim['quote'] == {'source_ref': 'F000'}
    # The main locator disambiguates the identical context quote as well.
    assert claim['context_quotes'] == [{'source_ref': 'F000'}, 'Visitors must wait.']
    book['accepted'][0]['evidence'].append({'field': 'context', 'quote': 'Staff may enter.'})
    claim = a._comparison_model_input(book, {'expected_units': []}, window)['claims']['C0000']
    assert claim['evidence'][-1]['quote'] == 'Staff may enter.'


def test_compact_quotes_use_exact_contiguous_ranges():
    text = 'Staff must file.\n\nUnless exempt.'
    doc = prepare_document(text)
    book = compile_candidates(doc, [{'kind': 'requirement', 'modality': 'must',
        'summary': 'Staff must file unless exempt.', 'actor': '', 'quote': text, 'logic_text': text}], {})
    claim = a._comparison_model_input(book, {'expected_units': []}, e.plan_windows(doc)[0])['claims']['C0000']
    assert claim['quote'] == claim['logic_text'] == {'source_ref': 'F000:F001'}
    assert claim['summary'] == 'Staff must file unless exempt.'
