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
    inventory = {'units': [{'quote': 'an invoice', 'meaning': 'An invoice is an acceptable alternative.',
                           'kind': 'alternative', 'scope_quotes': []}]}
    comparison = {'claim_judgments': [{'claim_id': 'C0000', 'unit_ids': [], 'dimensions': {
        d: 'error' if d == 'alternatives' else 'correct' for d in MEANING_DIMENSIONS},
        'rationale': 'The meaning narrows the choice to a receipt; the quote alone does not restore the missing alternative.',
        'quotes': ['a receipt; or an invoice']}],
        'unit_judgments': [{'unit_id': 'U0000', 'claim_ids': [], 'status': 'missing',
        'rationale': 'The draft meaning omits invoices despite their presence in the source quotation.', 'quotes': ['an invoice']}]}
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


def test_missing_alternative_is_visible_despite_complete_processing_and_exact_quote(monkeypatch, tmp_path):
    book = draft()
    before = deepcopy(book)
    env, requests = provider(monkeypatch, tmp_path, answers())
    report = a.audit_run(book, tmp_path / 'audit', env_file=env)
    assert report['status'] == 'failed'
    assert report['coverage']['missing'] == 1
    assert report['dimensions']['alternatives']['error'] == 1
    assert report['semantic_completeness'] == 'not_established'
    assert e._load(tmp_path / 'audit/audit.json')['status'] == 'complete'
    assert 'C0000' not in requests[0]['contents']
    assert 'Draft and inventory:' not in requests[0]['contents']
    assert 'C0000' in requests[1]['contents']
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
