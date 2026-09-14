"""Offline verification and arm-masked packets; no model judgments or calls."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random
from tempfile import TemporaryDirectory
from unittest.mock import patch

from rulespec_extrapolator import discovery, documents, extraction as e
from run import BASE, HERE, verify_pins, save


def verify():
    verify_pins()
    results = {}
    for arm in ('A', 'B'):
        path = HERE / arm
        book = e._load(path / 'rulebook.json')
        run = e._load(path / 'run.json')
        doc = book['document']
        planned = e.plan_windows(doc, section_windows=arm == 'B')
        assert len(planned) == len(run['windows'])
        for expected, actual in zip(planned, run['windows'], strict=True):
            assert all(actual[k] == v for k,v in expected.items())
        generator = e._prompt_generator(e.invented_examples())
        for i, window in enumerate(planned):
            req = e._load(path / f'attempt-{i:04d}.request.json')
            assert req['contents'] == e._window_prompt(generator, doc, window)
            assert req['model'] == 'gemini-3.8-flash'
            assert req['config']['response_json_schema'] == e.provider_schema().schema_dict
            assert req['config']['max_output_tokens'] == 16384
            assert req['config']['thinking_config']['thinking_level'] == 'low'
            assert not {'temperature', 'top_p', 'top_k', 'candidate_count'} & req['config'].keys()
        with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected model call')):
            with TemporaryDirectory(prefix='rulespec-csbg-replay-') as temp:
                reproduced = e.replay_run(path, Path(temp) / 'replay')
                assert reproduced == book
            exported = discovery.export_discovery(book, include_references=True)
        expected_ids = {p['id'] for p in documents.source_passages(doc)}
        assert {p['id'] for p in exported['records']} == expected_ids
        save(f'{arm}-discovery.json', exported)
        results[arm] = dict(status=run['status'], windows=len(planned),
            window_statuses=dict(Counter(w['status'] for w in run['windows'])),
            candidates=len(e._load(path / 'candidates.json')), accepted=len(book['accepted']),
            rejected=len(book['rejected']), refusals=e._load(path / 'refusals.json'),
            component_issues=dict(Counter(i['code'] for c in book['accepted'] for i in c['issues'])),
            validation=e._load(path / 'validation.json'), usage=e.recorded_usage(path),
            source_characters=len(doc['text']), source_passages=len(expected_ids),
            requests_verified=True, replay_equal=True, source_passages_retained=True,
            process=e._load(HERE / f'{arm}-process.json'))
    save('verification.json', dict(arms=results, verification_model_calls=0))


def packets():
    order = ['A', 'B']
    random.SystemRandom().shuffle(order)
    key = {f'packet-{i}':arm for i,arm in enumerate(order, 1)}
    doc = e._load(BASE / 'sources/document.json')
    for label, arm in key.items():
        book = e._load(HERE / arm / 'rulebook.json')
        for section in doc['sections']:
            number = section['label'].split('/')[-1][1:]
            rows = [dict(index=i, **c) for i,c in enumerate(book['accepted'])
                if c['start'] < section['end'] and c['end'] > section['start']]
            save(f'review/{label}/{number}.json', dict(records=rows,
                rejected=book['rejected'], refusals=e._load(HERE / arm / 'refusals.json')))
            lines = [f'# {label}: {section["label"]}']
            for c in rows:
                lines += [f'\n## Record {c["index"]} [{c["start"]}:{c["end"]}]',
                    c['summary'], f'Kind/modality: {c["kind"]} / {c["modality"]}; actor: {c["actor"]}']
                for field in ('scope_text','choice_text','logic_text','action','object','jurisdiction','references','defined_terms','term_refs'):
                    if c.get(field):
                        lines.append(field + ': ' + json.dumps(c[field], ensure_ascii=False))
                if c['issues']:
                    lines.append('Issues: ' + json.dumps(c['issues'], ensure_ascii=False))
            p = HERE / f'review/{label}/{number}.md'
            with p.open('x') as stream:
                stream.write('\n\n'.join(line.rstrip() for line in lines) + '\n')
    save('review-key.json', key)
    print('Verified both runs and saved randomized arm-masked review packets.')


if __name__ == '__main__':
    verify()
    packets()
