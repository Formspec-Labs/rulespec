"""Verify immutable captures and local review/export; provider blocked by default."""
from hashlib import sha256
from pathlib import Path
import sys
from unittest.mock import patch
import run as experiment
from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.review_store import ReviewStore, RevisionConflict

HERE = experiment.HERE


def smoke():
    # Freeze this supplementary smoke procedure before its single authorized call.
    experiment.save('smoke-procedure.json', {'sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'purpose': 'API/request compatibility and local processing only; not a quality comparison'})
    book = experiment.call('extraction-smoke', lambda: e.extract_run(e._load(HERE / 'books.json')['notice']['document'],
        HERE / 'smoke', env_file=experiment.ENV))
    assert book['run']['status'] in {'complete', 'partial'} and book['accepted']
    assert not book['extraction_refusals']
    request = e._load(HERE / 'smoke/attempt-0000.request.json')
    assert not {'temperature', 'top_p', 'top_k', 'candidate_count'} & request['config'].keys()
    assert request['config']['thinking_config'] == {'thinking_level': 'low'}
    assert book['run']['temperature'] is None
    with patch.object(e, '_create_model', side_effect=AssertionError('Provider blocked')):
        assert e.replay_run(HERE / 'smoke', HERE / 'smoke-replay') == book
    store = ReviewStore(HERE / 'smoke')
    before = store.snapshot()
    observation = {'action': 'observe', 'actor': 'Mechanical smoke harness', 'actor_kind': 'aiAgent',
        'expected_revision': before['revision'], 'targets': [before['accepted'][0]['id']],
        'rationale': 'Recorded API compatibility smoke; no semantic approval.',
        'observations': [{'code': 'api_smoke_only', 'claim_id': before['accepted'][0]['id']}]}
    first = store.apply(observation)
    try: store.apply(observation)
    except RevisionConflict: pass
    else: raise AssertionError('Stale review accepted')
    second = store.apply({**observation, 'expected_revision': first['revision']})
    assert second['revision'] == before['revision'] + 2
    assert [c['summary'] for c in second['accepted']] == [c['summary'] for c in before['accepted']]
    assert len(second['history']) == len(before['history']) + 2
    e._save(HERE / 'smoke-context.json', export_context(second, second['accepted'][0]))
    e._save(HERE / 'smoke-review.json', second)
    e._save(HERE / 'usage.json', e.recorded_usage(HERE, exclude=('smoke-replay', 'historical-reprocessed', 'historical-replay')))
    print('Fresh extraction, provider-blocked replay, sequential observations, stale refusal and context export verified.')


def verify():
    experiment.pins()
    books = e._load(HERE / 'books.json')
    with patch.object(e, '_create_model', side_effect=AssertionError('Provider blocked')):
        for name in e._load(HERE / 'cells.json'):
            data = e._load(HERE / f'inputs/{name}.json'); directory = HERE / 'captures' / name
            attempt = e._load(directory / 'attempt.json')
            payload, errors = a._read_response(directory, attempt)
            judgments, issues = r._decode_checks(payload, errors, data['candidates'], books[data['group']]['document'], data['packet'])
            assert dict(payload=payload, errors=errors, judgments=judgments, issues=issues) == e._load(HERE / f'decoded/{name}.json')
        original = experiment.OLD / 'notice-extract'
        reprocessed = HERE / 'historical-reprocessed'
        old = e._load(original / 'run.json')
        current = e.reprocess_run(original, reprocessed) if not reprocessed.exists() else e._load(reprocessed / 'rulebook.json')
        assert current['run']['temperature'] == old['temperature'] == 0
        assert not current['run']['reprocessing']['acquisition_matches_current']['requests']
        for suffix in ('request', 'response'):
            name = f'attempt-0000.{suffix}.json'
            assert (original / name).read_bytes() == (reprocessed / name).read_bytes()
        replay = HERE / 'historical-replay'
        if not replay.exists(): assert e.replay_run(reprocessed, replay) == current
    print('All checker decodes repeat without a provider; historical request/response bytes and settings preserved through reprocessing and replay.')


if __name__ == '__main__':
    {'smoke': smoke, 'verify': verify}[sys.argv[1]]()
