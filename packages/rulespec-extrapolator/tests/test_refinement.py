"""Refinement preserves source/history and applies only supported proposals."""
from copy import deepcopy
from pathlib import Path

import pytest

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore
from test_audit import provider


TEXT = 'Visitors must carry a badge. Volunteers are not required to carry a badge.'


def workspace(tmp_path):
    path = tmp_path / 'workspace'
    path.mkdir()
    doc = prepare_document(TEXT)
    book = compile_candidates(doc, [{'kind': 'requirement', 'actor': 'Visitors', 'actor_quote': 'Visitors',
        'quote': 'Visitors must carry a badge.', 'summary': 'Visitors must carry a badge.',
        'modality': 'must', 'modality_quote': 'must'}], {})
    for name, value in [('document.json', doc), ('rulebook.json', book), ('run.json', {})]:
        e._save(path / name, value)
    return path


def proposal(*, kind='exemption', target='', qualifies=None, operation='add'):
    schema = r.proposal_schema()['properties']['proposals']['items']['properties']['fields']
    fields = {name: [] if spec.get('type') == 'array' else '' for name, spec in schema['properties'].items()}
    fields.update(kind=kind, modality='not_required', modality_quote='not required', relation='none',
                  actor='Volunteers', actor_quote='Volunteers', summary='Volunteers need not carry a badge.')
    if kind == 'exception':
        fields['relation'] = 'exception'
    return {'operation': operation, 'target': target, 'qualifies': qualifies or [],
            'rationale': 'The volunteer exemption is missing from the draft.',
            'quote': 'Volunteers are not required to carry a badge.', 'fields': fields}


def inventory():
    return {'units': [{'quote_ref': 'F000',
        'meaning': 'Volunteers need not carry a badge.', 'kind': 'exemption', 'scope_refs': []}]}


def empty():
    return {'proposals': [], 'observations': []}


def judgment(verdict='supported'):
    return {'judgments': [{'proposal_id': 'P0000', 'source_refs': ['F000'],
        'rationale': 'The source explicitly removes this duty for volunteers.', 'verdict': verdict}]}


def answers(verdict='supported', *, linked=False):
    p = proposal(kind='exception' if linked else 'exemption', qualifies=['C0000'] if linked else [])
    generated = {'proposals': [p], 'observations': []}
    comparison = {'claim_judgments': [], 'unit_judgments': []}
    return [inventory(), comparison, generated, judgment(verdict), empty(), inventory(), comparison]


def test_preview_uses_real_validation_without_changing_history(tmp_path):
    store = ReviewStore(workspace(tmp_path))
    before = store.snapshot()
    action = {'action': 'add', 'actor': 'test', 'actor_kind': 'aiAgent', 'expected_revision': 0,
        'targets': [], 'rationale': 'Restore exemption.', 'replacements': [{
            'kind': 'exemption', 'actor': 'Volunteers', 'actor_quote': 'Volunteers',
            'quote': TEXT[28:], 'summary': 'Volunteers need not carry a badge.',
            'modality': 'not_required', 'modality_quote': 'not required'}]}
    preview = store.preview(action)
    assert preview['revision'] == 1 and len(preview['accepted']) == 2
    assert store.snapshot() == before
    broken = deepcopy(action)
    broken['replacements'][0]['quote'] = 'Invented evidence'
    with pytest.raises(ValueError):
        store.preview(broken)
    assert store.snapshot() == before


def test_live_pipeline_restores_omission_and_replays_without_provider(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    before = ReviewStore(path).snapshot()
    originals = {p.name: p.read_bytes() for p in path.glob('*.json')}
    env, requests = provider(monkeypatch, tmp_path, answers())
    result = r.refine_run(path, tmp_path / 'refine', env_file=env)
    assert result['run']['applied_actions'] == 1, result['issues']
    assert result['run']['status'] == 'complete'
    assert result['run']['usage']['recorded_requests'] == len(requests) == 7
    assert result['rulebook']['accepted'][0]['id'] == before['accepted'][0]['id']
    assert result['rulebook']['accepted'][1]['modality'] == 'not_required'
    assert result['rulebook']['history'][0]['actor_kind'] == 'aiAgent'
    assert originals == {p.name: p.read_bytes() for p in path.glob('*.json')}
    assert ReviewStore(path).snapshot() == result['rulebook']
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called provider'))
    assert r.replay_refinement(tmp_path / 'refine', tmp_path / 'replay')['provider_calls'] == 0
    (tmp_path / 'refine/recovery/window-0000/proposal/attempt-0000.response.json').write_text('{}')
    with pytest.raises(e.ReplayDriftError, match='capture changed'):
        r.replay_refinement(tmp_path / 'refine', tmp_path / 'bad-replay')


@pytest.mark.parametrize('verdict', ['unsupported', 'unknown'])
def test_source_challenge_keeps_withheld_assessment_without_changing_meaning(monkeypatch, tmp_path, verdict):
    path = workspace(tmp_path)
    before = ReviewStore(path).snapshot()
    env, _ = provider(monkeypatch, tmp_path, answers(verdict))
    result = r.refine_run(path, tmp_path / 'refused', env_file=env)
    after = result['rulebook']
    assert after['accepted'] == before['accepted']
    assert after['revision'] == before['revision'] + 1
    observation = after['enrichment_issues'][0]
    assert observation['code'] == 'refinement_withheld'
    assert observation['verdict'] == verdict
    assert observation['assessment_kind'] == 'model_assessment'
    assert observation['judgment']['source_refs'] == ['F000']
    assert observation['provenance']['request_sha256']
    assert ReviewStore(path).snapshot() == after
    from rulespec_extrapolator.discovery import export_discovery
    assert export_discovery(after)['enrichment_issues'] == after['enrichment_issues']
    assert result['run']['applied_actions'] == 0
    row = e._load(tmp_path / 'refused/recovery/window-0000/result.json')['outcomes'][0]
    assert row['status'] == 'not_applied' and row['judgment']['verdict'] == verdict
    assert r.replay_refinement(tmp_path / 'refused', tmp_path / 'replayed')['applied_actions'] == 0


def test_withheld_link_observation_preserves_approval_and_survives_target_revision(monkeypatch, tmp_path):
    store = ReviewStore(workspace(tmp_path))
    claim_id = store.snapshot()['accepted'][0]['id']
    store.apply({'action': 'approve', 'actor': 'reviewer', 'actor_kind': 'aiAgent',
        'expected_revision': 0, 'targets': [claim_id], 'rationale': 'Checked source.'})
    env, _ = provider(monkeypatch, tmp_path, answers('unsupported', linked=True))
    result = r.refine_run(tmp_path / 'workspace', tmp_path / 'refused', env_file=env)
    claim = result['rulebook']['accepted'][0]
    assert claim['review_status'] == 'approved' and claim['target_ids'] == []
    issue = next(i for i in claim['issues'] if i['code'] == 'refinement_withheld')
    assert issue['proposed_target_ids'] == [claim_id]
    from rulespec_extrapolator.discovery import export_discovery
    from rulespec_extrapolator.core import sparse
    assert sparse(issue) in export_discovery(result['rulebook'])['statements'][0]['issues']
    after = store.apply({'action': 'edit', 'actor': 'reviewer', 'actor_kind': 'aiAgent',
        'expected_revision': 2, 'targets': [claim_id], 'rationale': 'Clarify wording.',
        'replacements': [{'summary': 'All visitors must carry a badge.'}]})
    assert issue in after['enrichment_issues']
    assert issue not in after['accepted'][0]['issues']


def test_withheld_bundle_keeps_all_targets_without_choosing_one(tmp_path):
    book = ReviewStore(workspace(tmp_path)).snapshot()
    targets = [book['accepted'][0]['id'], 'another-target']
    rows = [{'reviewed_claim_id': None, 'proposed_target_ids': targets}]
    action = r._observation_action(rows, book, 'test')
    assert action['targets'] == []
    assert action['observations'][0]['proposed_target_ids'] == targets
    assert 'claim_id' not in action['observations'][0]


def test_unjudged_proposal_remains_visible_in_partial_run(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    responses = answers()
    responses[3] = {'judgments': []}
    env, _ = provider(monkeypatch, tmp_path, responses)
    result = r.refine_run(path, tmp_path / 'unjudged', env_file=env)
    assert result['run']['status'] == 'partial'
    assert result['run']['applied_actions'] == 0
    assert result['rulebook']['enrichment_issues'][0]['verdict'] == 'unjudged'
    assert r.replay_refinement(tmp_path / 'unjudged', tmp_path / 'replayed')['applied_actions'] == 0


def test_replay_rejects_altered_withheld_judgment_even_with_updated_manifest(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    env, _ = provider(monkeypatch, tmp_path, answers('unsupported'))
    output = tmp_path / 'refused'
    r.refine_run(path, output, env_file=env)
    record_path = output / 'recovery/window-0000/result.json'
    record = e._load(record_path)
    record['outcomes'][0]['judgment']['rationale'] = 'A different interpretation.'
    e._save(record_path, record)
    e._write_manifest(output)
    with pytest.raises(e.ReplayDriftError, match='outcome differs'):
        r.replay_refinement(output, tmp_path / 'replay')


def test_qualification_uses_exact_current_target_and_preserves_baseline(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    original = ReviewStore(path).snapshot()['accepted'][0]
    env, _ = provider(monkeypatch, tmp_path, answers(linked=True))
    result = r.refine_run(path, tmp_path / 'linked', env_file=env)
    assert result['run']['applied_actions'] == 1, result['issues']
    exception = result['rulebook']['accepted'][1]
    assert exception['target_ids'] == [original['id']]
    assert result['rulebook']['accepted'][0]['summary'] == original['summary']


def test_stale_audit_cannot_overwrite_prior_review(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    store = ReviewStore(path)
    env, _ = provider(monkeypatch, tmp_path, [inventory(), {'claim_judgments': [], 'unit_judgments': []}])
    a.audit_run(store.snapshot(), tmp_path / 'audit', env_file=env)
    store.apply({'action': 'approve', 'actor': 'earlier reviewer', 'actor_kind': 'aiAgent',
                 'expected_revision': 0, 'targets': [store.snapshot()['accepted'][0]['id']], 'rationale': 'Reviewed source.'})
    prior = store.snapshot()
    with pytest.raises(ValueError, match='stale'):
        r.refine_run(path, tmp_path / 'stale', audit_dir=tmp_path / 'audit', env_file=env)
    assert store.snapshot() == prior and not (tmp_path / 'stale').exists()


def test_invalid_row_keeps_valid_neighbor_and_forbids_outside_quote(tmp_path):
    book = ReviewStore(workspace(tmp_path)).snapshot()
    window = e.plan_windows(book['document'])[0]
    packet = r._packet(book, {'labels': {'expected_units': []}}, window)
    good = proposal()
    bad = deepcopy(good)
    bad['fields']['modality'] = 'invented-force'
    outside = deepcopy(good)
    outside['fields']['scope_quotes'] = ['unprovided condition']
    parsed, issues = r._decode_proposals({'proposals': [bad, good, outside], 'observations': []}, [], book['document'], window, packet, 'recovery')
    assert len(parsed) == 1 and parsed[0]['id'] == 'P0001'
    assert len(issues) == 2


def test_provider_failure_leaves_original_history_and_terminal_result(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    before = ReviewStore(path).snapshot()
    comparison = {'claim_judgments': [], 'unit_judgments': []}
    env, _ = provider(monkeypatch, tmp_path, [inventory(), comparison, RuntimeError('unavailable'), empty(), inventory(), comparison])
    result = r.refine_run(path, tmp_path / 'failed', env_file=env)
    assert result['run']['status'] == 'partial'
    assert result['rulebook'] == before
    assert (tmp_path / 'failed/manifest.json').exists()
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called provider'))
    assert r.replay_refinement(tmp_path / 'failed', tmp_path / 'replayed-failure')['provider_calls'] == 0


def test_repeated_exception_uses_selected_target_interval_not_first_occurrence():
    text = 'A badge is required unless the visitor is a child.\n\nA hat is required unless the visitor is a child.'
    doc = prepare_document(text)
    book = compile_candidates(doc, [{'kind': 'requirement', 'actor': '', 'quote': q, 'summary': q}
                                    for q in text.split('\n\n')], {})
    window = e.plan_windows(doc)[0]
    packet = r._packet(book, {'labels': {'expected_units': []}}, window)
    item = proposal(kind='exception', qualifies=['C0001'])
    item['quote'] = 'unless the visitor is a child'
    span = r._main_span(doc, item['quote'], window, packet, item)
    assert span['start'] == text.rindex(item['quote'])
    item['qualifies'] = ['C0000', 'C0001']
    with pytest.raises(ValueError, match='ambiguous'):
        r._main_span(doc, item['quote'], window, packet, item)


def test_refinement_keeps_existing_review_decision_and_replays_it(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    store = ReviewStore(path)
    prior = store.apply({'action': 'approve', 'actor': 'prior agent', 'actor_kind': 'aiAgent',
        'expected_revision': 0, 'targets': [store.snapshot()['accepted'][0]['id']], 'rationale': 'Verified against source.'})
    env, _ = provider(monkeypatch, tmp_path, answers())
    result = r.refine_run(path, tmp_path / 'refined', env_file=env)
    assert result['rulebook']['history'][:1] == prior['history']
    assert result['rulebook']['accepted'][0]['review_status'] == 'approved'
    assert result['rulebook']['revision'] == 2
    assert r.replay_refinement(tmp_path / 'refined', tmp_path / 'replayed')['applied_actions'] == 1


def test_replay_checks_recorded_action_against_proposal_and_saved_event(monkeypatch, tmp_path):
    path = workspace(tmp_path)
    env, _ = provider(monkeypatch, tmp_path, answers())
    output = tmp_path / 'refined'
    r.refine_run(path, output, env_file=env)
    result_path = output / 'recovery/window-0000/result.json'
    recorded = e._load(result_path)
    recorded['outcomes'][0]['action']['replacements'][0]['summary'] = 'Volunteers must carry a badge.'
    e._save(result_path, recorded)
    changes = e._load(output / 'changes.json')
    changes[0]['action'] = recorded['outcomes'][0]['action']
    e._save(output / 'changes.json', changes)
    # A self-consistent checksum manifest must not bypass semantic derivation.
    e._write_manifest(output)
    with pytest.raises(e.ReplayDriftError):
        r.replay_refinement(output, tmp_path / 'bad-replay')


def test_model_view_keeps_meaning_and_evidence_while_omitting_opaque_ids(tmp_path):
    book = ReviewStore(workspace(tmp_path)).snapshot()
    window = e.plan_windows(book['document'])[0]
    packet = r._packet(book, {'labels': {'expected_units': []}}, window)
    original = deepcopy(packet)
    view = r._model_packet(packet)
    assert packet == original
    assert view['focus'] == packet['focus']
    assert view['claims']['C0000']['id'] == 'C0000'
    old, new = packet['claims']['C0000'], view['claims']['C0000']
    for field in ('summary', 'scope_text', 'scope_quotes', 'context_quotes', 'choice_text',
                  'alternative_quotes', 'modality', 'references', 'reference_links', 'start', 'end'):
        assert new[field] == old[field]
    assert new['evidence'] == [{k: v for k, v in item.items() if k != 'fragment_id'} for item in old['evidence']]
    assert 'fragment_id' not in e._canonical(view)


def test_provider_array_bound_is_enforced_locally(tmp_path):
    book = ReviewStore(workspace(tmp_path)).snapshot()
    window = e.plan_windows(book['document'])[0]
    packet = r._packet(book, {'labels': {'expected_units': []}}, window)
    proposals, issues = r._decode_proposals({'proposals': [proposal()] * 9, 'observations': []},
        [], book['document'], window, packet, 'recovery')
    assert proposals == [] and issues == [{'code': 'invalid_proposal_schema'}]


def test_same_words_can_reconfirm_a_qualification_after_its_target_changes(tmp_path):
    store = ReviewStore(workspace(tmp_path))
    before = store.snapshot()
    window = e.plan_windows(before['document'])[0]
    packet = r._packet(before, {'labels': {'expected_units': []}}, window)
    item = proposal(kind='exception', qualifies=['C0000'])
    parsed, issues = r._decode_proposals({'proposals': [item], 'observations': []}, [],
        before['document'], window, packet, 'recovery')
    assert not issues
    linked = store.apply(r._action(parsed[0], before, 'test'))
    fields = {'summary': 'Every visitor must carry a badge.'}
    changed = store.apply({'action': 'edit', 'actor': 'test', 'actor_kind': 'aiAgent',
        'expected_revision': 1, 'targets': [linked['accepted'][0]['id']],
        'rationale': 'Clarify the baseline.', 'replacements': [fields]})
    assert changed['accepted'][0]['target_ids'] == []
    assert any(i['code'] == 'qualification_target_changed' for i in changed['accepted'][0]['link_issues'])
    packet = r._packet(changed, {'labels': {'expected_units': []}}, window)
    item.update(operation='edit', target='C0000', qualifies=['C0001'])
    parsed, issues = r._decode_proposals({'proposals': [item], 'observations': []}, [],
        changed['document'], window, packet, 'relationships')
    assert not issues
    action = r._action(parsed[0], changed, 'test')
    fixed = store.apply(action)
    assert fixed['accepted'][1]['target_ids'] == [fixed['accepted'][0]['id']]
    parsed[0]['target_id'] = fixed['accepted'][1]['id']
    with pytest.raises(ValueError, match='already represented'):
        r._action(parsed[0], fixed, 'test')
