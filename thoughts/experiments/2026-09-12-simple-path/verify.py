"""Verify captured processing, current-workspace exports and original source pins."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from tempfile import mkdtemp
from unittest.mock import patch

from rulespec_extrapolator import audit, cli, discovery, extraction as e
from rulespec_extrapolator.documents import source_passages
from rulespec_extrapolator.review_store import ReviewStore

HERE = Path(__file__).resolve().parent


def main():
    out = Path(mkdtemp(prefix='rulespec-simple-check-'))
    results = {'provider_calls': 0, 'application_file': e.__file__, 'extraction': {}, 'audit': {}}
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    labels = e._load(HERE / 'audit-label-pin.json')
    assert sha256((HERE / 'audit-cases.json').read_bytes()).hexdigest() == labels['sha256']
    assert sha256((HERE / 'PRE-AUDIT-REVIEW.md').read_bytes()).hexdigest() == labels['review_sha256']
    books = {}
    # Requests must not be repeated by any of these operations.
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider setup')):
        for name in ('manual', 'annual', 'uslm'):
            source = HERE / 'extract' / name
            book = e._load(source / 'rulebook.json')
            assert e.replay_run(source, out / name) == book
            books[name] = book
            snapshot = ReviewStore(source).snapshot()
            exported = discovery.export_discovery(snapshot)
            destination = out / (name + '.json')
            cli.main(['discovery-export', str(source), '--output', str(destination)])
            assert e._load(destination) == exported
            for mode in ('source', 'packets', 'summaries'):
                assert discovery.records(book, name, mode) == discovery.records(snapshot, name, mode)
            original_export = e._load(HERE / f'exports/{name}.json')
            annotated = []
            for before, after in zip(original_export['statements'], exported['statements'], strict=True):
                if before != after:
                    assert {k:v for k,v in before.items() if k != 'issues'} == {k:v for k,v in after.items() if k != 'issues'}
                    assert all(issue in after.get('issues', []) for issue in before.get('issues', []))
                    extra = [i for i in after.get('issues', []) if i not in before.get('issues', [])]
                    assert all(i.get('code') == 'section_reference_unresolved' and i in book['unresolved'] for i in extra)
                    annotated.append({'id': after['id'], 'added_reference_issues': extra})
            assert {k:v for k,v in original_export.items() if k != 'statements'} == {
                k:v for k,v in exported.items() if k != 'statements'}
            assert len(exported['records']) == len(source_passages(book['document']))
            e._save(HERE / f'workspace-exports/{name}.json', exported)
            results['extraction'][name] = dict(replay_equal=True, installed_cli_export_equal=True,
                retrieval_rows_equal=True, passages=len(exported['records']),
                workspace_annotations=annotated, accepted=len(book['accepted']),
                raw_units=len(e._load(source / 'candidates.json')))
        for name in ('uslm', 'annual'):
            source = HERE / 'audit' / name
            report = audit.replay_audit(source, out / ('audit-' + name))
            assert report == e._load(source / 'report.json')
            results['audit'][name] = dict(replay_equal=True, status=report['status'],
                review_complete=report['review_complete'], semantic_completeness=report['semantic_completeness'])

    # Reuse the exact captured diagnostic and verify its current counterpart too.
    frozen = HERE / 'acquisition-runtime/discovery_trial.py'
    current = HERE.parents[2] / 'packages/rulespec-extrapolator/evaluation/discovery_trial.py'
    assert current.read_bytes() == frozen.read_bytes()
    spec = importlib.util.spec_from_file_location('retained_trial', frozen)
    trial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial)
    assert trial.run(books, e._load(HERE / 'questions.json')) == e._load(HERE / 'retrieval.json')
    results['retrieval_replay_equal'] = True
    results['capture_usage'] = {stage: {name: e.recorded_usage(HERE / stage / name)
        for name in names} for stage, names in (('extract', books), ('audit', ('uslm', 'annual')))}
    e._save(HERE / 'verification.json', results)
    print(json.dumps({k:v for k,v in results.items() if k not in ('capture_usage','extraction')}, indent=2))


if __name__ == '__main__':
    main()
