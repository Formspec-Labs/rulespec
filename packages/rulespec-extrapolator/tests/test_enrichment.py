"""Core reuse must preserve source meaning, typed boundaries and review history."""
from copy import deepcopy
import json

import pytest
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.core import compile_candidates, validate_graph
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore

TEXT = ('The Office states: Applicants aged at least 18 years must file within 30 days after notice. '
        'This rule is in force from 2026-01-01T00:00:00Z until 2027-01-01T00:00:00Z.')


def candidate():
    return {'kind': 'requirement', 'summary': TEXT, 'actor': 'Applicants', 'actor_quote': 'Applicants',
        'quote': TEXT, 'modality': 'must', 'modality_quote': 'must',
        'scope_text': 'Applicants aged at least 18 years', 'scope_quotes': ['Applicants aged at least 18 years'],
        'concepts': [{'label': 'Filing', 'definition': 'Submitting an application after notice.',
                      'quote': 'must file within 30 days after notice', 'role': 'rkaf:assignmentSubstantive'}],
        'claimants': [{'text': 'The Office', 'quote': 'The Office states:', 'attribution': 'rkaf:claimantNamedInSource'}],
        'typed_values': [
            {'name': 'age', 'quote': 'at least 18 years', 'value': '18', 'datatype': 'xsd:integer',
             'comparator': 'at least', 'unit': 'years', 'anchor': ''},
            {'name': 'filing deadline', 'quote': 'within 30 days after notice', 'value': 'P30D',
             'datatype': 'xsd:duration', 'comparator': 'within', 'unit': 'days', 'anchor': 'after notice'}],
        'effective_periods': [{'quote': TEXT.split('This rule')[1],
                              'start': '2026-01-01T00:00:00Z', 'end': '2027-01-01T00:00:00Z'}]}


def book(c=None):
    return compile_candidates(prepare_document(TEXT), [candidate() if c is None else c], {'id': 'urn:test:run'})


def nodes(b, kind):
    return [n for n in b['graph']['@graph'] if n['@type'] == 'rkaf:' + kind]


def test_complete_source_meaning_uses_existing_core_records():
    b = book()
    assert not b['rejected'] and not b['accepted'][0]['issues']
    assert validate_graph(b['graph'])['shacl_conforms']
    claim = b['accepted'][0]
    by_id = {n['@id']: n for n in b['graph']['@graph']}
    meaning = by_id[claim['meaning_assertion_id']]
    claimant = by_id[meaning['rkaf:hasSourceClaimant']]
    assert claimant['rkaf:claimantText'] == 'The Office' != claim['actor']
    assert claimant['rkaf:claimsAssertion'] == meaning['@id']
    scope = by_id[meaning['rkaf:hasApplicability']]
    assert scope['rkaf:applicabilityCondition'] == claim['scope_text']
    assert by_id[scope['rkaf:hasEffectivePeriod']]['rkaf:effectivePeriodEnd'] == '2027-01-01T00:00:00Z'
    literals = [n['rkaf:assertsValue'] for n in nodes(b, 'ValueAssertion')]
    assert {'@value': '18', '@type': 'xsd:integer'} in literals
    assert {'@value': 'P30D', '@type': 'xsd:duration'} in literals
    assignment = nodes(b, 'ConceptAssignment')[0]
    release = by_id[assignment['rkaf:assignedConceptRelease']]
    assert assignment['rkaf:assertsObject'] in release['prov:hadMember']
    assert by_id[assignment['rkaf:assertsSubject']]['@type'] == 'rkaf:SourceFragment'
    assert assignment['@id'] in claim['assertion_ids']
    distribution = by_id[release['dcat:distribution'][0]]
    assert e._digest(distribution['dcterms:description']) == distribution['rkaf:hasContentDigest'].removeprefix('sha256:')
    assert json.loads(distribution['dcterms:description'])['@graph']


@pytest.mark.parametrize('role', ['Primary', 'Substantive', 'Mention', 'Contextual'])
def test_all_shared_assignment_roles_validate(role):
    c = candidate()
    c['concepts'][0]['role'] = 'rkaf:assignment' + role
    assert validate_graph(book(c)['graph'])['shacl_conforms']


@pytest.mark.parametrize('field,change', [
    ('typed_values', {'value': 'not-a-number'}),
    ('typed_values', {'comparator': 'less than'}),
    ('typed_values', {'unit': 'months'}),
    ('typed_values', {'anchor': 'after birth'}),
    ('claimants', {'attribution': 'rkaf:claimantNotStated'}),
    ('claimants', {'text': ''}),
    ('concepts', {'definition': ''}),
    ('effective_periods', {'start': '2026-01-01'}),
    ('effective_periods', {'end': '2025-01-01T00:00:00Z'}),
])
def test_invalid_structured_component_stays_visible_without_materialization(field, change):
    c = candidate()
    c[field][0].update(change)
    b = book(c)
    assert not b['rejected']
    assert any(issue['code'] == 'structured_component_unresolved' and issue['field'] == field + ':0'
               for issue in b['accepted'][0]['issues'])
    assert b['accepted'][0][field][0] == c[field][0]
    if field == 'concepts':
        assert not nodes(b, 'ConceptAssignment')
    elif field == 'claimants':
        assert not nodes(b, 'SourceClaimant')
    elif field == 'effective_periods':
        assert not nodes(b, 'EffectivePeriod')
    else:
        assert {'@value': c[field][0]['value'], '@type': 'xsd:integer'} not in [n['rkaf:assertsValue'] for n in nodes(b, 'ValueAssertion')]
    assert validate_graph(b['graph'])['shacl_conforms']


@pytest.mark.parametrize('field', ['concepts', 'claimants', 'typed_values', 'effective_periods'])
def test_nested_evidence_cannot_come_from_outside_the_request(field):
    c = candidate()
    c[field][0]['quote'] = 'Unseen source passage'
    b = book(c)
    assert any(i['field'] == field + ':0' and i['code'] == 'component_evidence_unresolved' for i in b['accepted'][0]['issues'])
    # Rich suggestions belong to Core/refinement, outside the first-pass schema.
    assert field not in e.PROVIDER_FIELDS
    if field == 'concepts':
        assert not nodes(b, 'ConceptAssignment')
    elif field == 'claimants':
        assert not nodes(b, 'SourceClaimant')
    elif field == 'effective_periods':
        assert not nodes(b, 'EffectivePeriod')


def test_relative_deadline_does_not_create_an_effective_period():
    c = candidate()
    c['effective_periods'] = []
    b = book(c)
    assert not nodes(b, 'EffectivePeriod')
    assert all('rkaf:hasEffectivePeriod' not in n for n in nodes(b, 'ApplicabilityScope'))


def test_release_digest_and_membership_are_checked_independently():
    b = book()
    assignment = nodes(b, 'ConceptAssignment')[0]
    assignment['rkaf:assertsObject'] = 'urn:test:unlisted-concept'
    with pytest.raises(ValueError, match='prov:hadMember'):
        validate_graph(b['graph'])
    b = book()
    nodes(b, 'ReferenceResourceRelease')[0]['dcat:version'] = 'tampered'
    with pytest.raises(ValueError, match='digest'):
        validate_graph(b['graph'])


def test_same_label_with_different_senses_does_not_merge_concepts():
    c = candidate()
    c['concepts'].append({**c['concepts'][0], 'definition': 'The act of filing within a specified period.'})
    b = book(c)
    assert len(nodes(b, 'LocalConcept')) == 2
    assert len(set(nodes(b, 'ReferenceResourceRelease')[0]['prov:hadMember'])) == 2


def test_review_corrections_preserve_old_concepts_values_attribution_and_periods(tmp_path):
    b = book()
    for name, value in [('document.json', b['document']), ('run.json', b['run']), ('rulebook.json', b)]:
        e._save(tmp_path / name, value)
    original_bytes = (tmp_path / 'rulebook.json').read_bytes()
    store = ReviewStore(tmp_path)
    before = store.snapshot()
    original = before['accepted'][0]
    edited = store.apply({'action': 'edit', 'actor': 'Test reviewer', 'actor_kind': 'humanUser',
        'expected_revision': 0, 'targets': [original['id']], 'rationale': 'Remove uncertain structured interpretations.',
        'replacements': [{'concepts': [], 'claimants': [], 'typed_values': [], 'effective_periods': []}]})
    current = edited['accepted'][0]
    assert current['meaning_assertion_id'] != original['meaning_assertion_id']
    assert not set(current['assertion_ids']) >= set(original['assertion_ids'])
    assert edited['revisions'][0]['concepts'] == original['concepts']
    assert edited['revisions'][0]['typed_values'] == original['typed_values']
    assert store.snapshot() == ReviewStore(tmp_path).snapshot()
    assert (tmp_path / 'rulebook.json').read_bytes() == original_bytes
    assert validate_graph(edited['graph'])['shacl_conforms']


def test_refinement_carries_and_checks_every_structured_component():
    from rulespec_extrapolator import refinement as r
    b = book()
    window = e.plan_windows(b['document'])[0]
    packet = r._packet(b, {'labels': {'expected_units': []}}, window)
    fields = {name: deepcopy(b['accepted'][0][name]) for name in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']}
    proposal = {'operation': 'edit', 'target': 'C0000', 'qualifies': [], 'rationale': 'Check source meaning.', 'quote': TEXT, 'fields': fields}
    parsed, issues = r._decode_proposals({'proposals': [proposal], 'observations': []}, [], b['document'], window, packet, 'recovery')
    assert not issues and len(parsed) == 1
    for field in ('concepts', 'claimants', 'typed_values', 'effective_periods'):
        assert parsed[0]['fields'][field] == candidate()[field]
    proposal['fields']['claimants'][0]['quote'] = 'An invented attribution'
    parsed, issues = r._decode_proposals({'proposals': [proposal], 'observations': []}, [], b['document'], window, packet, 'recovery')
    assert not parsed and issues[0]['code'] == 'proposal_refused'
