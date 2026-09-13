"""Source navigation is useful without promoting a citation to governing logic."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references
from test_uslm import document


def clause(parent, label, text):
    return f'<clause identifier="{parent}/{label}"><num value="{label}">({label})</num><content>{text}</content></clause>'


def branch(name, target='A member need not attend.', writing='Agreement under clause (i) shall be in writing.', duplicate=False):
    parent = '/us/usc/t5/s1/' + name
    body = clause(parent, 'i', target) if target else ''
    if duplicate:
        body += clause(parent, 'i', 'Another candidate.')
    return f'<subparagraph identifier="{parent}">{body}{clause(parent, "iii", writing)}</subparagraph>'


def test_same_parent_locates_without_crossing_repeated_labels():
    doc = document(branch('A') + branch('B', target='Other rule.'))
    scan = scan_references(doc)
    rows = scan['candidates']
    assert len(rows) == 2
    for row, suffix in zip(rows, ('A/i', 'B/i')):
        assert row['resolution']['status'] == 'located'
        target = scan['targets'][row['resolution']['target_ids'][0]]
        assert target['value'].endswith(suffix)
        assert row['xml_evidence_refs'][0] in scan['xml_fragments']
        assert all(doc['text'][s['start']:s['end']] == s['quote'] for s in target['evidence'])


@pytest.mark.parametrize('target,duplicate,status,count', [
    ('', False, 'not_in_selected_scope', 0), ('Here.', True, 'ambiguous', 2),
])
def test_missing_and_duplicate_native_targets_preserve_uncertainty(target, duplicate, status, count):
    doc = document(branch('A', target=target, duplicate=duplicate) + branch('B', writing='No reference.'))
    row, = scan_references(doc)['candidates']
    assert row['resolution']['status'] == status
    assert len(row['resolution']['target_ids']) == count


@pytest.mark.parametrize('tag', ['note', 'sourceCredit', 'quotedContent', 'heading'])
def test_nonoperative_mentions_do_not_supply_local_scope(tag):
    doc = document(branch('A', writing=f'<{tag}>Example under clause (i).</{tag}>'))
    row, = scan_references(doc)['candidates']
    assert row['reading']['context'] == tag
    assert row['resolution'] == {'status': 'nonoperative_context', 'target_ids': []}


def test_plain_text_and_unscoped_xml_do_not_guess():
    for doc in (prepare_document('See clause (i).'), document('<p>See clause (i).</p>' + branch('A', writing='No reference.'))):
        row, = scan_references(doc)['candidates']
        assert row['resolution'] == {'status': 'local_scope_unavailable', 'target_ids': []}


def test_native_number_disagreement_and_duplicate_labels_do_not_choose():
    for duplicate, status, count in ((False, 'native_label_conflict', 1), (True, 'ambiguous', 2)):
        body = branch('A').replace('identifier="/us/usc/t5/s1/A/i"', 'identifier="/us/usc/t5/s1/A/ii"')
        if duplicate:
            body = body.replace('</subparagraph>', clause('/us/usc/t5/s1/A', 'i', 'Another target.') + '</subparagraph>')
        row, = scan_references(document(body))['candidates']
        assert row['resolution']['status'] == status
        assert len(row['resolution']['target_ids']) == count


def test_explicit_other_branch_is_refused_and_publisher_link_still_wins():
    doc = document(branch('A', writing='See clause (i) of subparagraph (B).') + branch('B', writing='No reference.'))
    scan = scan_references(doc)
    assert scan['candidates'] == []
    assert scan['rejected'][0]['code'] == 'local_clause_qualification_unsupported'
    doc = document(branch('A', writing='<ref href="/us/usc/t5/s1/B/i">clause (i)</ref>') + branch('B', writing='No reference.'))
    scan = scan_references(doc)
    row, = scan['candidates']
    assert row['kind'] == 'publisher_reference'
    assert scan['targets'][row['resolution']['target_ids'][0]]['value'].endswith('B/i')
    assert row['text_readings'][0]['kind'] == 'local_clause'
    assert row['text_readings'][0]['resolution']['status'] == 'local_scope_unavailable'


def book():
    doc = document(branch('A') + branch('B', writing='No reference.'))
    quotes = ['A member need not attend.', 'Agreement under clause (i) shall be in writing.']
    result = compile_candidates(doc, [{'kind': 'exemption' if i == 0 else 'requirement',
        'quote': q, 'summary': q, 'actor': '', 'modality': 'not_required' if i == 0 else 'must',
        'start': doc['text'].index(q), 'end': doc['text'].index(q) + len(q)} for i, q in enumerate(quotes)], {})
    assert len(result['accepted']) == 2
    return result


def test_incoming_navigation_shows_referring_claim_without_semantic_mutation():
    current = book()
    before = deepcopy(current)
    focus, referring = current['accepted']
    result = export_context(current, focus)
    incoming, = [r for r in result['material']['reference_readings'] if r.get('direction') == 'incoming']
    assert incoming['semantic_role'] == 'not_assessed'
    assert incoming['referring_claim_ids'] == [referring['id']]
    related, = result['material']['related_claims']
    assert related['id'] == referring['id'] and related['kind'] == 'requirement'
    assert related['reference_ids'] == [incoming['id']]
    assert related['target_ids'] == []
    assert any(r['role'] == 'referring_claim' for r in result['material']['source_roles'])
    assert current == before
    # A same-text rule in the other native branch is not an incoming target.
    start = current['document']['text'].rindex('A member need not attend.')
    other = export_context(current, {'start': start, 'end': start + len('A member need not attend.')})
    assert other['material']['related_claims'] == []
    assert other['material']['reference_readings'] == []
    outgoing = export_context(current, referring)
    reading, = outgoing['material']['reference_readings']
    assert reading['direction'] == 'outgoing' and reading['semantic_role'] == 'not_assessed'
    assert reading['referenced_claim_ids'] == [focus['id']]
    assert outgoing['material']['related_claims'][0]['id'] == focus['id']


def test_incoming_navigation_retains_multiple_current_claim_matches():
    current = book()
    referring = current['accepted'][1]
    current['accepted'].append(dict(referring, id='urn:fixture:another-current-claim'))
    result = export_context(current, current['accepted'][0])
    incoming, = result['material']['reference_readings']
    assert set(incoming['referring_claim_ids']) == {referring['id'], 'urn:fixture:another-current-claim'}
    assert len(result['material']['related_claims']) == 2


def test_incoming_target_requires_full_focus_containment():
    current = book()
    result = export_context(current, {'start': 0, 'end': len(current['document']['text'])})
    assert not any(r.get('direction') == 'incoming' for r in result['material']['reference_readings'])


def test_incoming_context_budget_and_uncaptured_owner_are_explicit():
    parent = '/us/usc/t5/s1/A'
    quote = 'A member need not attend.'
    writing = 'Agreement under clause (i) shall be in writing.'
    doc = document(f'<subparagraph identifier="{parent}">' + clause(parent, 'i', quote)
                   + clause(parent, 'ii', 'Intervening text. ' * 1200)
                   + clause(parent, 'iii', writing) + '</subparagraph>')
    current = compile_candidates(doc, [{'kind': 'requirement', 'quote': writing, 'summary': writing, 'actor': ''}], {})
    focus = {'start': doc['text'].index(quote), 'end': doc['text'].index(quote) + len(quote)}
    limited = export_context(current, focus, extra_chars=0)
    assert any(d['role'] == 'referring_claim' and d['status'] == 'over_budget' for d in limited['material']['selection_decisions'])
    assert limited['accounting']['unique_chars'] == limited['accounting']['baseline_chars']
    assert not any(r['role'] == 'referring_claim' for r in limited['material']['source_roles'])
    current['accepted'] = []
    no_owner = export_context(current, focus)
    assert no_owner['material']['reference_readings'][0]['referring_claim_ids'] == []
    assert no_owner['material']['related_claims'] == []
    assert any(r['role'] == 'reference_occurrence' for r in no_owner['material']['source_roles'])


def test_saved_iep_writing_rule_now_has_incoming_navigation():
    root = Path(__file__).resolve().parents[3]
    path = root / 'thoughts/experiments/2026-09-12-extractor-confidence/decoded/iep-1.json'
    current = json.loads(path.read_text())['book']
    before = deepcopy(current)
    scan = scan_references(current['document'])
    local = [r for r in scan['candidates'] if r['kind'] == 'local_clause']
    assert len(local) == 2
    assert [scan['targets'][r['resolution']['target_ids'][0]]['value'] for r in local] == [
        '/us/usc/t20/s1414/d/1/C/i', '/us/usc/t20/s1414/d/1/C/ii']
    for i in (3, 4, 5, 7):
        result = export_context(current, current['accepted'][i])
        related = result['material']['related_claims']
        assert [r['id'] for r in related] == ([current['accepted'][6]['id']] if i in (4, 5) else [])
    assert current == before
