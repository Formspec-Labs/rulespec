"""Capture the unchanged application commands using old/new RefSpec readers."""
import ast
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import sysconfig
from time import perf_counter
from zipfile import ZipFile

from refspec.registry import citation_grammar as grammar
from rulespec_extrapolator import cli
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import load_document

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UPSTREAM = Path('/Users/mikewolfd/Work/RefSpec')
INPUT = ROOT / 'packages/rulespec-extrapolator/tests/fixtures/cfr-reverse-title.xml'
MODE = sys.argv[1]
OUT = HERE / MODE
OUT.mkdir()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if MODE in {'isolated', 'working'}:
    site = Path(sysconfig.get_paths()['purelib'])
    assert Path(grammar.__file__).is_relative_to(site) and Path(cli.__file__).is_relative_to(site)
    checked = 0
    for pin in json.loads((HERE / 'wheel-inputs.json').read_text()):
        wheel = Path(pin['path'])
        assert sha(wheel) == pin['sha256']
        with ZipFile(wheel) as archive:
            for name in archive.namelist():
                if name.endswith('.py') and '.dist-info/' not in name:
                    assert (site / name).read_bytes() == archive.read(name), name
                    checked += 1
    save(OUT / 'wheel-verification.json', {'python_files': checked})

document = load_document(INPUT)
cli.main(['references', str(INPUT), '--output', str(OUT / 'references.json')])
# Constructed empty extraction run, solely to exercise normal discovery export.
# This is not a model result or evidence of semantic extraction improvement.
run = OUT / 'run'
run.mkdir()
book = compile_candidates(document, [], {})
for name, value in {'document.json': document, 'run.json': {}, 'rulebook.json': book,
                    'candidates.json': [], 'graph.jsonld': book['graph']}.items():
    save(run / name, value)
cli.main(['discovery-export', str(run), '--output', str(OUT / 'discovery.json')])
scan = json.loads((OUT / 'references.json').read_text())
rows = [r for r in scan['candidates'] if r['kind'] == 'cfr']
summary = {'mode': MODE, 'input_sha256': sha(INPUT), 'reader_sha256': sha(Path(grammar.__file__)),
           'model_calls': 0, 'readings': [r['reading'] for r in rows],
           'candidate_ids': [r['id'] for r in rows], 'evidence_count': [len(r['evidence']) for r in rows]}
if MODE != 'baseline':
    assert [(r['reading']['cfr_title'], r['reading']['cfr_part'], r['reading']['cfr_section']) for r in rows] == [
        (29, '1910', None), (29, '1954', '3'), (29, '1910', None)]
    assert rows[1]['reading']['pinpoint'] == ['d', '1', 'i']
    assert summary['evidence_count'] == [1, 1, 1]
save(OUT / 'summary.json', summary)

if MODE in {'source', 'source-final'}:
    sys.path.insert(0, str(UPSTREAM / 'tests'))
    import cfr_reverse_title_oracle as oracle
    freeze = HERE / 'source-freeze.json'
    baseline_commit = (json.loads(freeze.read_text())['upstream_baseline_commit'] if freeze.exists()
                       else subprocess.check_output(['git', '-C', str(UPSTREAM), 'rev-parse', 'HEAD'], text=True).strip())
    original = subprocess.check_output(['git', '-C', str(UPSTREAM), 'show', baseline_commit + ':src/refspec/registry/citation_grammar.py'], text=True)
    copied = Path(oracle.__file__).read_text()
    for name in ('find_cfr_citations', '_parse_cfr_citations'):
        old = next(n for n in ast.parse(original).body if isinstance(n, ast.FunctionDef) and n.name == name)
        new = next(n for n in ast.parse(copied).body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(old) == ast.dump(new), name
    cases = json.loads((UPSTREAM / 'tests/fixtures/cfr-reverse-title.json').read_text())
    comparison = []
    for case in cases:
        before = [asdict(r) for r in oracle.find_cfr_citations(case['text'])]
        after = [asdict(r) for r in grammar.find_cfr_citations(case['text'])]
        assert (before != after) == (case['id'] in {'foreign-title-suffix', 'other-title-suffix'})
        comparison.append({**case, 'before': before, 'after': after})
    save(OUT / 'reader-comparison.json', comparison)
    timings = []
    for count in (400, 800, 1600):
        text = ('§ 1.3 of title 17, Code of Federal Regulations; ' * count)
        for label, reader in [('before', oracle.find_cfr_citations), ('after', grammar.find_cfr_citations)]:
            elapsed = []
            for _ in range(3):
                started = perf_counter()
                assert len(reader(text)) == count
                elapsed.append(perf_counter() - started)
            timings.append({'count': count, 'arm': label, 'seconds': elapsed})
    save(OUT / 'timings.json', timings)
    paths = [UPSTREAM / 'src/refspec/registry/citation_grammar.py', Path(oracle.__file__),
             UPSTREAM / 'tests/test_cfr_reverse_title.py', UPSTREAM / 'tests/fixtures/cfr-reverse-title.json',
             ROOT / 'packages/rulespec-extrapolator/tests/test_reverse_cfr_references.py', INPUT,
             HERE / 'PLAN.md', HERE / 'capture.py']
    save(HERE / ('source-freeze-final.json' if MODE == 'source-final' else 'source-freeze.json'), {'files': {str(p): sha(p) for p in paths},
        'copied_functions_match_upstream_head': True,
        'upstream_baseline_commit': baseline_commit})
print(json.dumps(summary))
