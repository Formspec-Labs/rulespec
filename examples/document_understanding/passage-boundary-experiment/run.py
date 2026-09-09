"""Diagnose passage granularity using the normal extractor, capture and replay."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import random
import tempfile
from unittest.mock import patch

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent


def prepare():
    assert not (ROOT / 'design.json').exists()
    documents = {'notice': e._load(ROOT.parent / 'standalone-qualification-experiment/fixtures/notice.json'),
        'same_actor': prepare_document('Staff must sign each report.\n\nStaff may use a blue pen.',
            title='Constructed same-actor independent-rule control'),
        'different_actor': prepare_document('Visitors must file a notice on arrival.\n\nStaff may work remotely.',
            title='Constructed different-actor independent-rule control')}
    catalogs, prompts = {}, {}
    for case, document in documents.items():
        e._save(ROOT / 'fixtures' / (case + '.json'), document)
        window, = e.plan_windows(document, max_chars=24000)
        baseline = e.passage_catalog(document, window)
        left, right = ('F003', 'F004') if case == 'notice' else ('F000', 'F001')
        assert not document['text'][baseline[left]['end']:baseline[right]['start']].strip()
        treatment = deepcopy(baseline)
        start, end = baseline[left]['start'], baseline[right]['end']
        treatment[left] = {'start': start, 'end': end, 'text': document['text'][start:end]}
        del treatment[right]
        assert {k:v for k,v in baseline.items() if k not in (left,right)} == {
            k:v for k,v in treatment.items() if k != left}
        catalogs[case] = {'B': baseline, 'T': treatment}
        prompts[case] = {}
        for arm, catalog in catalogs[case].items():
            with patch.object(e, 'passage_catalog', lambda *_: catalog):
                prompts[case][arm] = e._window_prompt(e._prompt_generator(e.invented_examples()), document, window)
        assert prompts[case]['B'].replace(e._canonical(baseline), 'CATALOG') == prompts[case]['T'].replace(e._canonical(treatment), 'CATALOG')
    historical = e._load(ROOT.parent / 'standalone-qualification-experiment/runs/notice/B/attempt-0000.request.json')
    assert prompts['notice']['B'] == historical['contents']
    inputs = ['PLAN.md', 'run.py'] + ['fixtures/' + case + '.json' for case in documents]
    e._save(ROOT / 'design.json', {'catalogs': catalogs, 'prompts': prompts,
        'schema': e.load_schema('provider'), 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': None,
        'cells': ['notice/1/B','notice/1/T','notice/2/T','notice/2/B',
                  'same_actor/1/B','same_actor/1/T','different_actor/1/T','different_actor/1/B'],
        'max_provider_calls': 8,
        'inputs_sha256': {name:e._digest((ROOT / name).read_bytes()) for name in inputs},
        'runtime_sources_sha256': {name:e._digest(path.read_bytes()) for name,path in e._runtime_sources().items()}})
    print('Frozen eight-call diagnostic: source bytes unchanged; only catalog granularity varies.')


def execute(mode, env_file):
    design = e._load(ROOT / 'design.json')
    for name,digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    assert {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    assert e.load_schema('provider') == design['schema']
    results, packet, key = {}, {}, {}
    for cell in design['cells']:
        case, repeat, arm = cell.split('/')
        directory = ROOT / 'runs' / cell
        document = e._load(ROOT / 'fixtures' / (case + '.json'))
        catalog = design['catalogs'][case][arm]
        with patch.object(e, 'passage_catalog', lambda *_: catalog):
            if mode == 'run':
                book = e.extract_run(document, directory, model_id=design['model'],
                    env_file=env_file, max_chars=24000, temperature=0,
                    max_output_tokens=None, thinking_level='low')
            else:
                with tempfile.TemporaryDirectory(prefix='rulespec-boundary-replay-') as temporary:
                    book = e.replay_run(directory, Path(temporary) / 'replay')
                assert book == e._load(directory / 'rulebook.json')
        attempt = e._load(directory / 'attempt-0000.json')
        if attempt.get('request_file'):
            actual = e._load(directory / attempt['request_file'])
            assert actual == {'model':design['model'], 'contents':design['prompts'][case][arm],
                'config': {'temperature':0, 'candidate_count':1,
                    'thinking_config': {'thinking_level':'low'}, **e.provider_schema().to_provider_config()}}
        response = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
        # Processing failures remain visible; raw-content assessment follows capture.
        row = {'accepted':len(book['accepted']), 'rejected':len(book['rejected']),
            'refusals':book['extraction_refusals'], 'status':book['run']['status'],
            'issues':dict(Counter(issue['code'] for c in book['accepted'] for issue in c['issues'])),
            'usage':response.get('usage_metadata'),
            'attempt_seconds':(datetime.fromisoformat(attempt['finished_at']) -
                               datetime.fromisoformat(attempt['started_at'])).total_seconds()}
        results[cell] = row
        print(cell, row['status'], row['accepted'], 'accepted', len(row['refusals']), 'refusals', flush=True)
    if mode == 'replay':
        assert results == e._load(ROOT / 'results.json')
        print('Eight full replays and result metadata identical; zero provider calls.')
        return
    e._save(ROOT / 'results.json', results)
    for pair in dict.fromkeys(cell.rsplit('/',1)[0] for cell in design['cells']):
        packet[pair] = {}
        arms = ['B','T']; random.SystemRandom().shuffle(arms)
        for number,arm in enumerate(arms,1):
            label = 'R' + str(number)
            key[pair + '/' + label] = arm
            book = e._load(ROOT / 'runs' / pair / arm / 'rulebook.json')
            packet[pair][label] = [{field:c.get(field) for field in (
                'kind','summary','scope_text','logic_text','modality','choice_text')} for c in book['accepted']]
    e._save(ROOT / 'blind-review.json', packet)
    e._save(ROOT / 'review-key.json', key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare','run','replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    else:
        execute(args.mode, args.env_file)
