"""Fresh sources, unchanged checker treatment, immutable staged captures."""
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
import time
from rulespec_extrapolator import audit as a, extraction as e, refinement as r

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / '2026-09-13-complete-reading-check'
spec = importlib.util.spec_from_file_location('previous_check', OLD / 'run.py')
prior = importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
NAMES = ['privacy', 'bankruptcy', 'credit', 'inspection', 'jury', 'compensatory', 'medical', 'recall']
ENV = Path('/Users/mikewolfd/Work/spicy-regs/.env')


def save(name, value):
    path = HERE / name; path.parent.mkdir(parents=True, exist_ok=True)
    assert not path.exists(), name
    e._save(path, value)


def freeze(name, paths):
    save(name, {str(p.resolve()): sha256(p.read_bytes()).hexdigest() for p in paths})


def pins(name='source-pins.json'):
    for file, digest in e._load(HERE / name).items():
        assert sha256(Path(file).read_bytes()).hexdigest() == digest, file


def usage():
    return e.recorded_usage(HERE, exclude=('base-run', 'previous', 'frozen', 'verification-output'))


def call(name, fn):
    pins()
    ledger = e._load(HERE / 'calls.json') if (HERE / 'calls.json').exists() else []
    assert name not in {c['name'] for c in ledger}, 'No retries'
    assert len(ledger) < 44 and sum(c['seconds'] for c in ledger) < 2400
    assert usage()['tokens'].get('total_token_count', 0) < 500000
    ledger.append(dict(name=name, status='started', seconds=0)); e._save(HERE / 'calls.json', ledger)
    start = time.monotonic()
    try:
        result = fn(); ledger[-1]['status'] = 'returned'; return result
    finally:
        ledger[-1]['seconds'] = time.monotonic() - start; e._save(HERE / 'calls.json', ledger)


def extract():
    if not (HERE / 'source-pins.json').exists():
        save('runtime.json', e._runtime_versions())
        freeze('source-pins.json', [p for p in HERE.rglob('*') if p.is_file()] +
               list(e._runtime_sources().values()) + [OLD / 'TASK.txt', OLD / 'run.py'])
    for name in NAMES:
        directory = HERE / 'extract' / name
        if directory.exists(): continue
        book = call('extract/' + name, lambda: e.extract_run(e._load(HERE / f'sources/{name}.json'), directory, env_file=ENV))
        print(name, book['run']['status'], len(book['accepted']), 'claims;', len(book['rejected']), 'rejected', flush=True)
        assert book['run']['status'] in {'complete', 'partial'} and book['accepted'], book['run']['status']
        assert not any(i['code'] in {'provider_request_failed', 'response_recording_failed'} for i in book['extraction_refusals'])
    e._save(HERE / 'usage.json', usage())


def check():
    pins('check-pins.json'); key=e._credential(ENV)
    for name in e._load(HERE / 'cells.json'):
        directory=HERE / 'captures' / name
        if directory.exists(): continue
        data=e._load(HERE / f'inputs/{name}.json')
        attempt, = call(name, lambda: a._capture(directory, data['document'], [data['window']], [data['prompt']],
            r.CHECK_SCHEMA, e.DEFAULT_MODEL, key, None, max_output_tokens=32768, thinking_level='medium'))
        save(f'captures/{name}/attempt.json', attempt)
        assert attempt['status']=='response_received', attempt['error_code']
        expected=dict(model=e.DEFAULT_MODEL,contents=data['prompt'],config=dict(max_output_tokens=32768,
            response_mime_type='application/json',response_json_schema=r.CHECK_SCHEMA,thinking_config=dict(thinking_level='medium')))
        assert e._load(directory / attempt['request_file'])==expected
        payload,errors=a._read_response(directory,attempt)
        judgments,issues=r._decode_checks(payload,errors,data['candidates'],data['document'],data['packet'])
        save(f'decoded/{name}.json',dict(payload=payload,errors=errors,judgments=judgments,issues=issues))
        print(name,len(judgments),'judgments;',len(issues),'issues',flush=True)
        # Keep invalid judgments as failures, but do not silently replace them.
    e._save(HERE / 'usage.json', usage())


if __name__=='__main__':
    {'extract':extract,'check':check}[sys.argv[1]]()
