"""Constructed review-boundary controls; not provider accuracy observations."""
from copy import deepcopy

import pytest

from test_extraction import offline, raw, row
from test_review_store import action
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore


@pytest.mark.parametrize('recover_earlier_candidate', [False, True])
def test_reprocessing_keeps_original_reviews_without_transferring_them(
        offline, tmp_path, monkeypatch, recover_earlier_candidate):
    install, models = offline
    document = prepare_document('Guests may borrow maps.\n\nStaff must log requests.')
    assert {k: v['text'] for k, v in e.passage_catalog(document, e.plan_windows(document)[0]).items()} == {
        'F000': 'Guests may borrow maps.', 'F001': 'Staff must log requests.',
    }
    response = raw([
        row('F000', kind='permission', statement='Guests may borrow maps.',
            modality='may', modality_quote='may'),
        row('F001'),
    ])
    env_file = install([response])
    original = tmp_path / 'original'
    parse = e.parse_raw_response

    def earlier_parser(*args, **kwargs):
        result = deepcopy(parse(*args, **kwargs))
        # Simulate an earlier parser omitting the first row from the same capture.
        # The false arm checks the unchanged-ID case, not just the known failure.
        if recover_earlier_candidate:
            result['candidates'] = result['candidates'][1:]
        return result

    with monkeypatch.context() as patch:
        patch.setattr(e, 'parse_raw_response', earlier_parser)
        base = e.extract_run(document, original, env_file=env_file)
    assert len(base['accepted']) == (1 if recover_earlier_candidate else 2)
    source_claim = next(c for c in base['accepted'] if c['quote'].startswith('Staff'))
    captures = {p.relative_to(original): p.read_bytes()
                for p in original.rglob('*') if p.is_file()}
    store = ReviewStore(original)
    approved = store.apply(action(store.snapshot(), 'approve', [source_claim['id']]))
    corrected = store.apply(action(approved, 'edit', [source_claim['id']], replacements=[
        {'summary': 'Staff are required to log requests.'},
    ]))
    assert corrected['attestations']
    assert any(c['summary'] == 'Staff are required to log requests.' for c in corrected['accepted'])

    monkeypatch.setattr(e, '_create_model', lambda *a, **kw: pytest.fail('Provider called during reprocessing'))
    output = tmp_path / 'reprocessed'
    processed = e.reprocess_run(original, output)
    assert len(processed['accepted']) == 2
    new_claim = next(c for c in processed['accepted'] if c['quote'].startswith('Staff'))
    assert (new_claim['rule_id'] != source_claim['rule_id']) is recover_earlier_candidate
    assert (new_claim['id'] != source_claim['id']) is recover_earlier_candidate
    assert new_claim['summary'] == source_claim['summary']
    assert processed['run']['reprocessing']['provider_calls'] == 0
    assert models[0].calls == 1
    assert e.replay_run(output, tmp_path / 'replay') == processed
    fresh = ReviewStore(output).snapshot()
    assert not fresh['attestations']
    assert all(c['review_status'] == 'pending' for c in fresh['accepted'])
    assert ReviewStore(original).snapshot() == corrected
    assert all((original / name).read_bytes() == value for name, value in captures.items())
