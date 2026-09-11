"""Process pinned provider answers; no model calls or edits to original captures."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from rulespec_extrapolator import extraction as ex, core

HERE = Path(__file__).resolve().parent
arm = sys.argv[1]
destination = HERE / arm
destination.mkdir(exist_ok=False)
source = Path(ex._load(HERE / 'input.json')['source_experiment'])
assert ex._digest((source / 'manifest.json').read_bytes()) == ex._load(HERE / 'input.json')['manifest_sha256']
for name, digest in ex._load(source / 'manifest.json')['files'].items():
    assert ex._digest((source / name).read_bytes()) == digest, name
for name, digest in ex._load(HERE / 'baseline-pins.json').items():
    assert ex._digest((HERE / name).read_bytes()) == digest, name

report = []
for cell in ex._load(source / 'cells.json'):
    directory = source / 'cells' / cell['id']
    doc, run = ex._load(directory / 'document.json'), ex._load(directory / 'run.json')
    window = ex._load(source / 'contexts' / (cell['case'] + '.json'))[cell['arm']]
    attempt = ex._load(directory / f"attempt-{window['index']:04d}.json")
    parsed = ex._attempt_result(attempt, directory, doc, window)
    book = core.compile_candidates(doc, parsed['candidates'], run)
    original = ex._load(directory / 'rulebook.json')
    if arm == 'baseline-result':
        assert parsed['candidates'] == ex._load(directory / 'candidates.json')
        assert parsed['refusals'] == ex._load(directory / 'refusals.json')
        assert {**book, 'extraction_refusals': parsed['refusals']} == original
    else:
        ex._save(destination / (cell['id'] + '.parsed.json'), parsed)
        ex._save(destination / (cell['id'] + '.rulebook.json'), book)
    report.append({'cell': cell['id'], 'parsed': len(parsed['candidates']),
                   'accepted': len(book['accepted']), 'rejected': len(book['rejected']),
                   'parse_reasons': dict(Counter(r['code'] for r in parsed['refusals'])),
                   'core_reasons': dict(Counter(r['reason'] for r in book['rejected'])),
                   'parsed_sha256': ex._digest(parsed), 'book_sha256': ex._digest(book)})

ex._save(destination / 'report.json', report)
ex._save(destination / 'runtime.json', {'modules': {
    name: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    for name, module in sorted(sys.modules.items())
    if name.startswith('rulespec_extrapolator') and getattr(module, '__file__', None)}})
print(json.dumps({'arm': arm, 'cells': len(report),
                  'parsed': sum(r['parsed'] for r in report),
                  'accepted': sum(r['accepted'] for r in report),
                  'passage_refusals': sum(r['parse_reasons'].get('passage_not_in_request', 0) for r in report)}))
