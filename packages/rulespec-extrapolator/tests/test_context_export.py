"""Context selection preserves source, occurrence and review boundaries."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from rulespec_extrapolator import cli
from rulespec_extrapolator.context import export_context, resolve_context
from rulespec_extrapolator.core import canonical
from rulespec_extrapolator.documents import load_document, prepare_document
from rulespec_extrapolator.reference_feedback import reference_observation
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.uslm import prepare_xml
from test_discovery_source_map import mapped_document
from test_reference_feedback import make_run, action

FIXTURE = Path(__file__).with_name('fixtures') / 'uslm/reference-title5-s553.xml'


def export(text, sources=(), **kwargs):
    doc = prepare_document(text)
    return export_context({'document': doc, 'accepted': []}, {'start': 0, 'end': len(text)},
                          reference_sources=sources, **kwargs)


def test_repeated_external_target_is_supplied_once_with_distinct_occurrences():
    source = load_document(FIXTURE)
    result = export('See 5 USC 553(b)(B). Again, 5 USC 553(b)(B).', iter([source]))
    material = result['material']
    targets = [r for r in material['selection_decisions'] if r['role'] == 'reference_target']
    assert [t['status'] for t in targets] == ['added', 'already_supplied']
    assert targets[0]['occurrence_id'] != targets[1]['occurrence_id']
    assert all(t['edition_match'] == 'not_established' for t in targets)
    external = material['sources']['S1']
    text = '\n'.join(p['text'] for p in external['passages'].values())
    assert text.count('Except when notice or hearing is required by statute') == 1
    assert len(result['documents']) == 2
    for alias, row in material['sources'].items():
        for key in row['passages']:
            span = resolve_context({'source': alias, 'passage': key}, result)
            assert span['source_id'] == row['source_id']
            assert span['quote'] in result['documents'][span['source_id']]['text']


def test_missing_ambiguous_and_over_budget_targets_remain_explicit():
    source = load_document(FIXTURE)
    alternate = prepare_xml(source['uslm_source']['xml'].replace('</uscDoc>', '<!-- another capture --></uscDoc>'))
    assert source['text'] == alternate['text']
    missing = export('5 USC 553(b)(B).')
    ambiguous = export('5 USC 553(b)(B).', [source, alternate])
    limited = export('5 USC 553(b)(B).', [source], extra_chars=0)
    for result in (missing, ambiguous, limited):
        assert list(result['material']['sources']) == ['S0']
        assert result['accounting']['unique_chars'] == result['accounting']['baseline_chars']
        assert result['accounting']['semantic_completeness'] == 'not_established'
    assert ambiguous['material']['reference_readings'][0]['resolution']['status'] == 'ambiguous'
    assert len(ambiguous['material']['source_metadata']) == 2
    assert any(d['status'] == 'over_budget' for d in limited['material']['selection_decisions'])


def test_refused_reading_is_visible_without_guessing_target():
    result = export('(i) Authorized under their registration under 21 CFR 1301.13(e)(1)(iv) to prescribe the basic class of controlled substance specified on the prescription; or')
    refused = [r for r in result['material']['reference_readings'] if r['disposition'] == 'rejected']
    assert any(r['code'] == 'cfr_range_end_unread' for r in refused)
    assert list(result['material']['sources']) == ['S0']


def test_source_qualified_resolution_refuses_document_or_passage_substitution():
    result = export('5 USC 553(b)(B).', [load_document(FIXTURE)])
    selection = {'source': 'S1', 'passage': 'F000'}
    changed = deepcopy(result)
    source = changed['material']['sources']['S1']
    source['source_id'] = changed['material']['sources']['S0']['source_id']
    with pytest.raises(ValueError, match='identity'):
        resolve_context(selection, changed)
    changed = deepcopy(result)
    changed['material']['sources']['S1']['passages']['F000']['text'] = 'Fabricated provision.'
    with pytest.raises(ValueError, match='passage text'):
        resolve_context(selection, changed)
    with pytest.raises(KeyError):
        resolve_context({'source': 'S99', 'passage': 'F000'}, result)


def test_whitespace_parts_resolve_but_unseen_conditions_do_not():
    doc = mapped_document([('source', 'Staff must:'), ('inserted', '\n\n'), ('source', 'log requests.')])
    result = export_context({'document': doc, 'accepted': []}, {'start': 0, 'end': len(doc['text'])})
    keys = list(result['material']['sources']['S0']['passages'])
    span = resolve_context({'source': 'S0', 'passage': keys[0]+':'+keys[-1]}, result)
    assert span['quote'] == doc['text'] and len(span['evidence']) == 2
    result = export('First.\n\nUnless closed.\n\nLast.')
    rows = result['material']['sources']['S0']['passages']
    keys = list(rows); del rows[keys[1]]
    with pytest.raises(ValueError, match='unsupplied'):
        resolve_context({'source': 'S0', 'passage': keys[0]+':'+keys[-1]}, result)


@pytest.mark.parametrize('focus,allowance', [({'start': True, 'end': 4}, 20), ({'start': -1, 'end': 4}, 20),
    ({'start': 0, 'end': 999}, 20), ({'start': 0, 'end': 4}, -1), ({'start': 0, 'end': 4}, True)])
def test_invalid_focus_or_budget_is_refused(focus, allowance):
    with pytest.raises(ValueError):
        export_context({'document': prepare_document('Text.'), 'accepted': []}, focus, extra_chars=allowance)


def test_cli_reads_feedback_and_approval_from_current_review_without_editing(tmp_path):
    doc = prepare_document('Staff must keep records under 5 USC 553(b)(B).')
    run = make_run(tmp_path, doc, [{'kind': 'requirement', 'quote': doc['text'], 'summary': doc['text'],
                                  'actor': 'Staff', 'actor_quote': 'Staff', 'modality': 'must', 'modality_quote': 'must'}])
    store = ReviewStore(run)
    claim = store.snapshot()['accepted'][0]
    store.apply({'action': 'approve', 'actor': 'Fixture reviewer', 'actor_kind': 'humanUser',
                 'expected_revision': 0, 'targets': [claim['id']], 'rationale': 'Constructed approval.'})
    scan = scan_references(doc, reference_sources=[load_document(FIXTURE)])
    observation = reference_observation(doc, scan, 'candidates', 0, message='Constructed challenge; check this edition.')
    store.apply(action(observation, 1))
    before = store.snapshot(); original = (run/'rulebook.json').read_bytes()
    output = tmp_path/'context.json'
    assert cli.main(['context-export', str(run), '--claim', claim['id'], '--reference-source', str(FIXTURE), '--output', str(output)]) == 0
    result = json.loads(output.read_text())
    assert result['review_revision'] == 2
    assert result['focus']['review_status'] == 'approved'
    assert result['material']['recorded_feedback'][0]['scan_sha256'] == observation['scan_sha256']
    assert result['material']['recorded_feedback'][0]['reader_context']['parsers'] == scan['parsers']
    assert result['observations'][0]['context'] == observation['context']
    assert result['material']['recorded_feedback'][0]['event_id'] == before['history'][-1]['id']
    assert ReviewStore(run).snapshot() == before and (run/'rulebook.json').read_bytes() == original
    bad = dict(result['focus'], summary='Changed draft')
    with pytest.raises(ValueError, match='current claim'):
        export_context(before, bad)
    exported = export_context(before, before['accepted'][0])
    exported['documents'][next(iter(exported['documents']))]['title'] = 'Changed copy'
    assert canonical(before) == canonical(store.snapshot())


def test_cli_accepts_source_span_without_an_extraction_run(tmp_path):
    path = tmp_path/'source.txt'; path.write_text('Staff must retain records.')
    output = tmp_path/'context.json'
    assert cli.main(['context-export', str(path), '--span', '0', '26', '--output', str(output)]) == 0
    result = json.loads(output.read_text())
    assert result['material']['statement'] == path.read_text()
    assert result['review_revision'] is None
