"""One controlled reference-granularity comparison; reuse production capture/replay."""
import argparse
from collections import defaultdict
from contextlib import nullcontext
from pathlib import Path
import random
import time
from unittest.mock import patch

from langextract import chunking
from langextract.core import tokenizer
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
PARAGRAPHS = e.passage_catalog


def sentences(document, window):
    catalog, counters = {}, defaultdict(int)
    for ref, span in PARAGRAPHS(document, window).items():
        tokenized = tokenizer.tokenize(span['text'])
        intervals = list(chunking.SentenceIterator(tokenized))
        parts = [(tokenized.tokens[i.start_index].char_interval.start_pos,
                  tokenized.tokens[i.end_index - 1].char_interval.end_pos) for i in intervals]
        if not parts:
            parts = [(0, len(span['text']))]
        # The library may trim whitespace, but must never omit source content.
        cursor = 0
        for start, end in parts:
            assert start >= cursor and not span['text'][cursor:start].strip()
            key = f'{ref[0]}{counters[ref[0]]:03d}'
            start, end = span['start'] + start, span['start'] + end
            catalog[key] = {'start': start, 'end': end, 'text': document['text'][start:end]}
            counters[ref[0]] += 1
            cursor = end - span['start']
        assert not span['text'][cursor:].strip()
    return catalog


def prepare():
    assert not (ROOT / 'design.json').exists()
    text = '''CONSTRUCTED COUNTEREXAMPLES — not an actual policy.

For library lending, an access record (AR) means the dated entry of a visitor's permission to borrow. An access record is not an annual report.

For finance reporting, an annual report (AR) means the signed yearly account of spending. In the following finance rules, AR always means annual report.

You must sign and date the AR before submitting it. Signing and dating are both required.

Visitors do not need an access record for a public tour, and librarians do not need an access record to enter the archive. These are separate exemptions for different activities.

If an access record is lost and remains unreported for more than a month, staff must request a replacement. If travel is imminent, a temporary pass may be issued.

Finance reviewers should check the AR for missing pages. Missing pages may indicate an incomplete submission.

An annual report must not be altered without the director's approval. The director approves alterations; this sentence does not identify who would perform an alteration.

Staff must file the access record. Staff must retain the access record for two years.
'''
    e._save(ROOT / 'sources/counterexamples.json', prepare_document(text, title='Constructed counterexamples'))
    (ROOT / 'sources/counterexamples.txt').write_text(text)
    passport = e._load(ROOT.parent / 'actor-term-integration/extract/document.json')
    e._save(ROOT / 'sources/passport.json', passport)
    (ROOT / 'sources/passport.txt').write_text(passport['text'])
    cases = ['seatbelts', 'first-aid', 'recording', 'passport', 'counterexamples']
    pairs = [(case, arm) for case in cases for arm in ('P', 'S')]
    random.Random(20260910).shuffle(pairs)
    cells = [{'id': f'cell-{i:02d}', 'case': case, 'arm': arm} for i, (case, arm) in enumerate(pairs)]
    for case in cases:
        document = e._load(ROOT / 'sources' / f'{case}.json')
        assert len(document['text']) <= 24000
        windows = e.plan_windows(document, 24000)
        assert len(windows) == 1
        for arm, factory in [('P', PARAGRAPHS), ('S', sentences)]:
            catalog = factory(document, windows[0])
            e._save(ROOT / 'catalogs' / f'{case}-{arm}.json', catalog)
            refs = list(catalog)
            selected = e.resolve_passage(refs[0] + ':' + refs[-1], catalog, document)
            assert selected['quote'] == document['text'].strip()
    inputs = [ROOT / 'PLAN.md', Path(__file__), *sorted((ROOT / 'sources').glob('*')), *sorted((ROOT / 'catalogs').glob('*'))]
    e._save(ROOT / 'design.json', {'cells': cells, 'model': e.DEFAULT_MODEL, 'temperature': 0,
        'thinking_level': 'low', 'max_output_tokens': 32768, 'max_chars': 24000,
        'max_calls': 10, 'max_provider_seconds': 1800,
        'runtime': e._runtime_versions(),
        'runtime_sources': {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()},
        'inputs': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs}})
    print('Prepared 10 cells; complete source coverage checked for both catalogs.', flush=True)


def verify():
    design = e._load(ROOT / 'design.json')
    assert all(e._digest((ROOT / p).read_bytes()) == sha for p, sha in design['inputs'].items())
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources']
    return design


def run(env):
    design = verify()
    elapsed = 0
    for cell in design['cells']:
        target = ROOT / 'cells' / cell['id']
        if target.exists():
            raise FileExistsError('Existing cell; this experiment does not retry or resume silently')
        if elapsed >= design['max_provider_seconds']:
            break
        document = e._load(ROOT / 'sources' / (cell['case'] + '.json'))
        started = time.monotonic()
        print('Starting', cell['id'], cell['case'], flush=True)
        with patch.object(e, 'passage_catalog', sentences) if cell['arm'] == 'S' else nullcontext():
            book = e.extract_run(document, target, env_file=env, max_chars=24000,
                temperature=0, max_output_tokens=32768, thinking_level='low')
            e.replay_run(target, ROOT / 'replay' / cell['id'])
        duration = time.monotonic() - started
        elapsed += duration
        e._save(ROOT / 'measurements' / (cell['id'] + '.json'), {'case': cell['case'],
            'elapsed_seconds': duration, 'usage': e.recorded_usage(target),
            'claims': len(book['claims']), 'rejections': len(book.get('rejected', [])),
            'refusals': len(e._load(target / 'refusals.json')), 'run': book.get('run')})
        print('Finished', cell['id'], len(book['claims']), 'claims,', round(duration, 1), 'seconds', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else run(args.env_file)
