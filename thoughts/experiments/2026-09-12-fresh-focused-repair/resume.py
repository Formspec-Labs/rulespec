"""Resume saved requests using complete extraction copies for temporary previews."""
from pathlib import Path
import shutil
import sys
import tempfile

import run as m
from rulespec_extrapolator.review_store import ReviewStore

original_store = m.prior.temporary_store


def preview_store(directory, book):
    for case in m.CASES:
        source = m.HERE / 'extract' / case
        if m.e._load(source / 'run.json')['id'] == book['run']['id']:
            assert m.e._load(source / 'rulebook.json') == book
            shutil.copytree(source, directory, dirs_exist_ok=True)
            return ReviewStore(directory)
    return original_store(directory, book)


m.prior.temporary_store = preview_store


def capture():
    m.pins('pre-extraction-pins.json'); m.pins('pre-recovery-pins.json'); m.pins('resume-pins.json')
    books = m.e._load(m.HERE / 'books.json')
    for book in books.values():
        with tempfile.TemporaryDirectory() as temporary:
            store = preview_store(temporary, book)
            assert len(store.snapshot()['accepted']) == len(book['accepted'])
    key = m.e._credential(m.ENV)
    for cell in m.e._load(m.HERE / 'cells.json'):
        data = m.e._load(m.HERE / f'inputs/{cell["id"]}.json'); book = books[cell['case']]
        for phase in ('recovery', 'check'):
            if phase == 'recovery':
                prompt, schema = data['prompt'], m.r.proposal_schema()
            else:
                proposals = m.e._load(m.HERE / f'decoded/{cell["id"]}-recovery.json')['prepared']
                if not proposals:
                    m.save(f'decoded/{cell["id"]}-check-skipped.json', dict(reason='no_decoded_proposals')); continue
                prompt, schema = m.r._challenge_prompt(data['packet'], proposals, book['document']), m.r.CHECK_SCHEMA
            m.save(f'expected-requests/{cell["id"]}-{phase}.json', dict(model=m.e.DEFAULT_MODEL, contents=prompt,
                config=dict(temperature=0, max_output_tokens=32768, candidate_count=1,
                    response_mime_type='application/json', response_json_schema=schema,
                    thinking_config=dict(thinking_level='medium'))))
            directory = m.HERE / 'captures' / cell['id'] / phase
            reused = (directory / 'attempt.json').exists()
            if not reused:
                attempts = m.call(cell['id'] + '/' + phase, lambda: m.a._capture(directory, book['document'], [data['window']],
                    [prompt], schema, m.e.DEFAULT_MODEL, key, None, max_output_tokens=32768, thinking_level='medium'))
                m.save(str(directory.relative_to(m.HERE) / 'attempt.json'), attempts[0])
            result = m.decode(cell, phase)
            m.save(f'decoded/{cell["id"]}-{phase}.json', result)
            print(cell['id'], phase, 'saved' if reused else 'new',
                len(result.get('prepared', result.get('judgments', []))), 'items;', len(result['issues']), 'issues/observations', flush=True)
    m.save('usage.json', m.e.recorded_usage(m.HERE))


if __name__ == '__main__':
    if sys.argv[1] == 'pin':
        m.freeze('resume-pins.json', [Path(__file__).resolve(), m.HERE / 'HARNESS-REPAIR.md'])
    elif sys.argv[1] == 'capture':
        capture()
    elif sys.argv[1] == 'verify':
        m.pins('resume-pins.json'); m.verify()
