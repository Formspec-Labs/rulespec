"""Bounded live capture and frozen-output retrieval using existing operations."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time

from rulespec_extrapolator import audit, discovery, extraction as e
from prepare import save

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENV = Path('/Users/mikewolfd/Work/spicy-regs/.env')


def verify_pins():
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def call(name, requests, function):
    verify_pins()
    ledger = e._load(HERE / 'calls.json') if (HERE / 'calls.json').exists() else []
    usage = e.recorded_usage(HERE)
    assert sum(c['planned_requests'] for c in ledger) + requests <= 18
    assert sum(c['seconds'] for c in ledger) < 1800
    assert usage['tokens'].get('total_token_count', 0) < 300000
    start = time.monotonic()
    print('Capture', name, flush=True)
    try:
        return function()
    finally:
        ledger.append(dict(name=name, planned_requests=requests, seconds=time.monotonic() - start))
        e._save(HERE / 'calls.json', ledger)


def extract():
    assert not (HERE / 'extract').exists(), 'No retries or overwrites'
    for name in ('manual', 'annual', 'uslm'):
        doc = e._load(HERE / f'sources/{name}.document.json')
        call('extract/' + name, len(e.plan_windows(doc)),
             lambda: e.extract_run(doc, HERE / 'extract' / name, env_file=ENV))


def retrieval():
    path = REPO / 'packages/rulespec-extrapolator/evaluation/discovery_trial.py'
    spec = importlib.util.spec_from_file_location('existing_trial', path)
    trial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial)
    books = {n: e._load(HERE / f'extract/{n}/rulebook.json') for n in ('manual', 'annual', 'uslm')}
    questions = e._load(HERE / 'questions.json')
    for q in questions:
        assert all(quote in books[q['source']]['document']['text'] for quote in q['required_quotes'])
    result = trial.run(books, questions)
    for a, b in zip(result['source']['questions'], result['packets']['questions'], strict=True):
        assert [(h['id'], h['score']) for h in a['hits']] == [(h['id'], h['score']) for h in b['hits']]
    save('retrieval.json', result)
    for name, book in books.items():
        save(f'exports/{name}.json', discovery.export_discovery(book))
    print({mode: result[mode]['supported_at_3'] for mode in ('source', 'packets', 'summaries')})


def audit_cases():
    assert not (HERE / 'audit').exists(), 'No retries or overwrites'
    cases = e._load(HERE / 'audit-cases.json')
    assert sha256((HERE / 'audit-cases.json').read_bytes()).hexdigest() == e._load(HERE / 'audit-label-pin.json')['sha256']
    assert sum(len(e.plan_windows(e._load(HERE / f'extract/{c["source"]}/rulebook.json')['document'], 24000)) for c in cases) <= 6
    for case in cases:
        book = e._load(HERE / f'extract/{case["source"]}/rulebook.json')
        call('audit/' + case['source'], 2 * len(e.plan_windows(book['document'], 24000)),
             lambda: audit.audit_run(book, HERE / 'audit' / case['source'], env_file=ENV,
                                     max_chars=24000, max_output_tokens=32768, thinking_level='medium'))


if __name__ == '__main__':
    {'extract': extract, 'retrieval': retrieval, 'audit': audit_cases}[sys.argv[1]]()
