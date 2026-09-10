"""Exemption connections preserve meaning, review history and target identity."""
from copy import deepcopy

import pytest

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.core import compile_candidates, resolve_links
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore, RevisionConflict
from test_audit import provider


def workspace(tmp_path):
    doc = prepare_document('Visitors must carry a badge.\n\nVolunteers are not required to carry a badge.')
    candidates = [
        {'kind': 'requirement', 'summary': 'Visitors must carry a badge.', 'actor': 'Visitors',
         'quote': 'Visitors must carry a badge.', 'modality': 'must'},
        {'kind': 'exemption', 'summary': 'Volunteers need not carry a badge.', 'actor': 'Volunteers',
         'quote': 'Volunteers are not required to carry a badge.', 'modality': 'not_required'},
    ]
    book = compile_candidates(doc, candidates, {})
    for name, value in [('document.json', doc), ('rulebook.json', book), ('run.json', {})]:
        e._save(tmp_path / name, value)
    return ReviewStore(tmp_path)


def link_proposal(book):
    window = e.plan_windows(book['document'])[0]
    packet = r._packet(book, {'labels': {'expected_units': []}}, window)
    item = {'operation': 'link', 'target': 'C0001', 'qualifies': ['C0000'],
            'rationale': 'Connect the explicit exemption without changing its meaning.'}
    return item, window, packet


def decode(book, item, window, packet):
    return r._decode_proposals({'proposals': [item], 'observations': []}, [],
                              book['document'], window, packet, 'relationships')


def test_link_exemption_preserves_meaning_and_records_evidenced_edge(tmp_path):
    store = workspace(tmp_path)
    before = store.snapshot()
    original = before['accepted'][1]
    item, window, packet = link_proposal(before)
    parsed, issues = decode(before, item, window, packet)
    assert not issues
    action = r._action(parsed[0], before, 'test')
    preview = store.preview(action)
    assert store.snapshot() == before
    after = store.apply(action)
    linked = next(c for c in after['accepted'] if c['rule_id'] == original['rule_id'])
    assert len(after['accepted']) == 2
    assert linked['id'] != original['id']
    assert linked['supersedes'] == [original['id']]
    assert linked['target_ids'] == [before['accepted'][0]['id']]
    for key in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']:
        if key != 'relation':
            assert linked[key] == original[key]
    assert linked['quote'] == original['quote']
    assert linked['kind'] == 'exemption' and linked['modality'] == 'not_required'
    assert linked['review_status'] == 'pending'
    graph = after['graph']['@graph']
    edge, = [n for n in graph if n.get('rkaf:assertsSubject') == linked['id']
             and n.get('rkaf:assertsObject') == before['accepted'][0]['id']]
    assert edge['@type'] == 'rkaf:RelationshipAssertion'
    assert edge['rkaf:assertsPredicate'].endswith(':exception')
    assert any(n.get('rkaf:bindsAssertion') == edge['@id']
               and n.get('rkaf:evidentiaryFunction') == 'rkaf:qualifies' for n in graph)
    assert export_discovery(after)['statements'][1]['qualification_targets'] == linked['target_ids']
    assert ReviewStore(tmp_path).snapshot() == after
    assert preview['accepted'][1]['summary'] == linked['summary']


@pytest.mark.parametrize('change', ['reclassify', 'rewrite', 'evidence', 'modality', 'ordinary_duty'])
def test_relationship_pass_refuses_changes_beyond_exemption_links(tmp_path, change):
    before = workspace(tmp_path).snapshot()
    item, window, packet = link_proposal(before)
    if change == 'reclassify':
        item['fields'] = {'kind': 'exception', 'modality': 'not_stated'}
    elif change == 'rewrite':
        item['fields'] = {'summary': 'Volunteers must carry a badge.'}
    elif change == 'evidence':
        item['quote'] = 'not required'
    elif change == 'modality':
        item['fields'] = {'modality': 'must'}
    else:
        item.update(target='C0000', qualifies=['C0001'])
    parsed, issues = decode(before, item, window, packet)
    assert not parsed and issues[0]['code'] == 'proposal_refused'


@pytest.mark.parametrize('operation', ['edit', 'reject'])
def test_changed_or_rejected_baseline_invalidates_exemption_target(tmp_path, operation):
    store = workspace(tmp_path)
    before = store.snapshot()
    item, window, packet = link_proposal(before)
    parsed, issues = decode(before, item, window, packet)
    after = store.apply(r._action(parsed[0], before, 'test'))
    action = {'action': operation, 'expected_revision': after['revision'], 'actor': 'test',
              'actor_kind': 'aiAgent', 'targets': [before['accepted'][0]['id']], 'rationale': 'Review baseline.'}
    if operation == 'edit':
        action['replacements'] = [{'summary': 'Every visitor must carry a badge.'}]
    changed = store.apply(action)
    exemption = next(c for c in changed['accepted'] if c['kind'] == 'exemption')
    assert exemption['target_ids'] == []
    assert any(i['code'] == 'qualification_target_changed' for i in exemption['link_issues'])
    assert changed['history'][0] == after['history'][0]


def test_invalid_link_modes_and_self_link_do_not_resolve(tmp_path):
    before = workspace(tmp_path).snapshot()
    original = before['accepted'][1]
    for relation, modality, targets in [('scope', 'not_required', [before['accepted'][0]['id']]),
                                         ('exception', 'not_stated', [before['accepted'][0]['id']]),
                                         ('exception', 'not_required', [])]:
        candidate = {k: original[k] for k in ('kind', 'summary', 'actor', 'quote')}
        candidate.update(relation=relation, modality=modality, applies_to=targets)
        assert compile_candidates(before['document'], [candidate], {})['rejected']
    self_link = deepcopy(original)
    self_link.update(relation='exception', applies_to=[self_link['id']])
    problems = resolve_links(before['document'], [self_link])
    assert not self_link['target_ids']
    assert problems[0]['code'] == 'missing_target'


@pytest.mark.parametrize('targets', [[], ['C0001'], ['C9999']])
def test_compact_link_rejects_missing_self_and_unknown_targets(tmp_path, targets):
    book = workspace(tmp_path).snapshot()
    item, window, packet = link_proposal(book)
    item['qualifies'] = targets
    parsed, issues = decode(book, item, window, packet)
    assert not parsed and issues[0]['code'] == 'proposal_refused'


def test_link_preserves_existing_targets_and_does_not_mutate_packet(tmp_path):
    store = workspace(tmp_path)
    book = store.snapshot()
    item, window, packet = link_proposal(book)
    packet['claims']['C0002'] = deepcopy(packet['claims']['C0000'])
    packet['claims']['C0002']['id'] = 'another-current-rule'
    packet['claims']['C0001']['target_ids'] = ['C0000']
    original = deepcopy(packet)
    item['qualifies'] = ['C0002', 'C0002']
    parsed, issues = decode(book, item, window, packet)
    assert not issues and packet == original
    assert parsed[0]['proposal']['operation'] == 'edit'
    assert parsed[0]['proposal']['qualifies'] == ['C0000', 'C0002']


def test_link_uses_current_alias_and_revision_checks(tmp_path):
    store = workspace(tmp_path)
    book = store.snapshot()
    item, window, packet = link_proposal(book)
    parsed, issues = decode(book, item, window, packet)
    assert not issues
    action = r._action(parsed[0], book, 'test')
    store.apply({'action': 'approve', 'actor': 'prior reviewer', 'actor_kind': 'aiAgent',
        'expected_revision': book['revision'], 'targets': [book['accepted'][0]['id']],
        'rationale': 'Concurrent review.'})
    with pytest.raises(RevisionConflict):
        store.apply(action)
    changed = store.apply({'action': 'edit', 'actor': 'reviewer', 'actor_kind': 'aiAgent',
        'expected_revision': store.snapshot()['revision'], 'targets': [book['accepted'][1]['id']],
        'rationale': 'Clarify meaning.', 'replacements': [{'summary': 'Volunteers have no badge-carrying duty.'}]})
    with pytest.raises(ValueError, match='targets changed'):
        r._action(parsed[0], changed, 'test')


def test_compact_link_is_relationship_only_and_bad_neighbor_does_not_hide_it(tmp_path):
    book = workspace(tmp_path).snapshot()
    item, window, packet = link_proposal(book)
    parsed, issues = r._decode_proposals({'proposals': [item], 'observations': []}, [],
        book['document'], window, packet, 'recovery')
    assert not parsed and issues
    bad = {**item, 'fields': {'summary': 'An attempted rewrite'}}
    parsed, issues = r._decode_proposals({'proposals': [bad, item], 'observations': []}, [],
        book['document'], window, packet, 'relationships')
    assert len(parsed) == 1 and parsed[0]['id'] == 'P0001'
    assert len(issues) == 1


def test_compact_link_through_capture_challenge_review_and_replay(monkeypatch, tmp_path):
    path = tmp_path / 'workspace'
    path.mkdir()
    before = workspace(path).snapshot()
    item, _, _ = link_proposal(before)
    empty = {'proposals': [], 'observations': []}
    comparison = {'claim_judgments': [], 'unit_judgments': []}
    answers = [{'units': []}, comparison, empty,
        {'proposals': [item], 'observations': []},
        {'judgments': [{'proposal_id': 'P0000', 'source_refs': ['F000:F001'],
            'rationale': 'The volunteer exemption qualifies the badge duty.', 'verdict': 'supported'}]},
        {'units': []}, comparison]
    env, requests = provider(monkeypatch, tmp_path, answers)
    output = tmp_path / 'refinement'
    result = r.refine_run(path, output, env_file=env)
    assert result['run']['applied_actions'] == 1, result['issues']
    assert len(requests) == 7
    proposal_request = e._load(output / 'relationships/window-0000/proposal/attempt-0000.request.json')
    assert proposal_request['config']['response_json_schema'] == r.proposal_schema('relationships')
    assert r.replay_refinement(output, tmp_path / 'replay')['applied_actions'] == 1
