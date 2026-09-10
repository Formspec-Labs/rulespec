"""Exemption connections preserve meaning, review history and target identity."""
from copy import deepcopy

import pytest

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.core import compile_candidates, resolve_links
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore


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
    original = packet['claims']['C0001']
    properties = r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
    fields = {key: deepcopy(original[key]) for key in properties}
    fields['relation'] = 'exception'
    item = {'operation': 'edit', 'target': 'C0001', 'qualifies': ['C0000'],
            'rationale': 'Connect the explicit exemption without changing its meaning.',
            'quote': original['quote'], 'fields': fields}
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
        item['fields'].update(kind='exception', modality='not_stated')
    elif change == 'rewrite':
        item['fields']['summary'] = 'Volunteers must carry a badge.'
    elif change == 'evidence':
        item['quote'] = 'not required'
    elif change == 'modality':
        item['fields']['modality'] = 'must'
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
