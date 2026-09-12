"""Audit and refinement share Core's original-source evidence boundaries."""
from copy import deepcopy
from pathlib import Path

import pytest

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.core import compile_candidates, evidence_parts
from rulespec_extrapolator.evaluation import MEANING_DIMENSIONS
from rulespec_extrapolator.review_store import ReviewStore
from test_audit import provider
from test_discovery_source_map import mapped_document
from test_refinement import answers


@pytest.mark.parametrize('separator', [' ', '\n\n'])
def test_audit_accepts_original_pieces_across_formatting_and_replays(monkeypatch, tmp_path, separator):
    document = mapped_document([('source', 'Staff must'), ('inserted', separator), ('source', 'file.')])
    quote = document['text']
    book = compile_candidates(document, [{'kind': 'requirement', 'modality': 'must',
        'modality_quote': 'must', 'actor': '', 'summary': 'Staff must file.', 'quote': quote}], {})
    before = deepcopy(book)
    catalog = e.passage_catalog(document, e.plan_windows(document)[0])
    refs = list(catalog)
    selection = refs[0] if len(refs) == 1 else refs[0] + ':' + refs[-1]
    span = {'source_id': document['id'], 'quote': quote, 'start': 0, 'end': len(quote)}
    inventory = {'units': [{'quote_ref': selection, 'scope_refs': [], 'kind': 'requirement',
                            'meaning': 'Staff must file.'}]}
    comparison = {'claim_judgments': [{'claim_id': 'C0000', 'unit_ids': ['U0000'],
        'dimensions': {d: 'correct' for d in MEANING_DIMENSIONS}, 'source_refs': [selection],
        'rationale': 'Fixed response exercises evidence handling, not model accuracy.'}],
        'unit_judgments': [{'unit_id': 'U0000', 'claim_ids': ['C0000'], 'status': 'covered',
            'source_refs': [selection], 'rationale': 'The complete statement retains the duty.'}]}
    env, requests = provider(monkeypatch, tmp_path, [inventory, comparison])
    directory = tmp_path / 'audit'
    report = a.audit_run(book, directory, env_file=env)
    assert report['status'] == 'passed', report['audit_issues']
    assert report['semantic_completeness'] == 'not_established'
    assert len(requests) == 2
    assert e._load(directory / 'inventory.json')['units'][0]['source_spans'] == [span]
    assert e._load(directory / 'judgments.json')['claim_judgments'][0]['source_spans'] == [span]
    assert [p['quote'] for p in evidence_parts(document, quote, 'audit', 0, len(quote))] == ['Staff must', 'file.']
    assert book == before
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called provider'))
    assert a.replay_audit(directory, tmp_path / 'replay') == report


def test_refinement_recovers_compound_quote_preserves_history_and_replays(monkeypatch, tmp_path):
    document = mapped_document([('source', 'Visitors must carry a badge.'), ('inserted', '\n\n'),
        ('source', 'Volunteers are not required'), ('inserted', '\n\n'), ('source', 'to carry a badge.')])
    original = 'Visitors must carry a badge.'
    book = compile_candidates(document, [{'kind': 'requirement', 'actor': '',
        'quote': original, 'summary': original, 'modality': 'must', 'modality_quote': 'must'}], {})
    workspace = tmp_path / 'workspace'
    for name, value in [('document.json', document), ('rulebook.json', book), ('run.json', {})]:
        e._save(workspace / name, value)
    originals = {p.name: p.read_bytes() for p in workspace.glob('*.json')}
    responses = answers()
    for index in (0, 5):
        responses[index]['units'][0]['quote_ref'] = 'F001:F002'
    quote = document['text'][document['text'].index('Volunteers'):]
    responses[2]['proposals'][0]['quote'] = quote
    responses[3]['judgments'][0]['source_refs'] = ['F001:F002']
    env, requests = provider(monkeypatch, tmp_path, responses)
    output = tmp_path / 'refine'
    result = r.refine_run(workspace, output, env_file=env)
    assert result['run']['applied_actions'] == 1, result['issues']
    assert result['run']['status'] == 'complete'
    assert len(requests) == 7
    claim = result['rulebook']['accepted'][1]
    assert claim['quote'] == quote
    assert [p['quote'] for p in claim['evidence'] if p['field'] == 'summary'] == [
        'Volunteers are not required', 'to carry a badge.']
    assert originals == {p.name: p.read_bytes() for p in workspace.glob('*.json')}
    assert ReviewStore(workspace).snapshot() == result['rulebook']
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called provider'))
    assert r.replay_refinement(output, tmp_path / 'replay')['provider_calls'] == 0


@pytest.mark.parametrize('insertion', [' not ', ' editorial ', '\u200b'])
def test_audit_still_refuses_inserted_substantive_content(insertion):
    document = mapped_document([('source', 'Staff must'), ('inserted', insertion), ('source', 'file.')])
    with pytest.raises(ValueError):
        a._source_span(document, {'quote': document['text'], 'start': 0, 'end': len(document['text'])})


def test_audit_does_not_accept_formatting_alone_as_evidence():
    document = mapped_document([('source', 'Before.'), ('inserted', '\n\n'), ('source', 'After.')])
    with pytest.raises(ValueError):
        a._source_span(document, {'quote': '\n\n', 'start': 7, 'end': 9})


def test_saved_native_ppe_spans_use_the_same_original_evidence_parts():
    root = Path(__file__).resolve().parents[3] / 'thoughts/experiments/2026-09-11-expanded-inventory'
    document = e._load(root / 'sources/ecfr-29-1910-132.document.json')
    receipt = e._load(root / 'comparison/ecfr-29-1910-132-B/source-evidence.json')
    affected = [row for row in receipt.values() if row['ordinary_audit_would_refuse']]
    assert affected
    for row in affected:
        span = row['span']
        assert a._source_span(document, span) == span
        assert evidence_parts(document, span['quote'], 'audit', span['start'], span['end']) == row['parts']
