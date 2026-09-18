"""One-sentence ablation; reuse the preceding study's capture/replay helpers."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / '2026-09-14-grouping-fresh'
REPO = HERE.parents[2]
SENTENCE = 'Keep independently actionable duties as separate records, including list children that require distinct actions.'

spec = importlib.util.spec_from_file_location('prior_grouping_experiment', PRIOR / 'run.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
# Only the research output directory changes. Production imports are unmodified.
shared.HERE = HERE


def prepare():
    assert not (HERE / 'design.json').exists()
    prior = json.loads((PRIOR / 'design.json').read_text())
    assert prior['fingerprints']['sources_sha256'] == {
        name: e._digest(path.read_bytes()) for name, path in e._runtime_sources().items()}
    definitions = [
        ('drug-contents', 'drug-records', 'A1', 1),
        ('signals', 'aviation', 'A2', 1),
        ('clearances', 'aviation', 'A1', 1),
        ('technical-safeguards', 'health-safeguards', 'A2', 1),
        ('monitoring', 'csbg-repeat', 'A2', 1),
        ('drug-contents', 'drug-records', 'A1', 2),
    ]
    generator = e._prompt_generator(e.invented_examples())
    calls = []
    cases = {}
    for pair_index, (case, source_case, source_arm, repeat) in enumerate(definitions):
        doc_path = PRIOR / f'inputs/{source_case}/document.json'
        doc = json.loads(doc_path.read_text())
        window = json.loads((PRIOR / f'inputs/{source_case}/{source_arm}.window.json').read_text())
        if case not in cases:
            shared.save(f'inputs/{case}/document.json', doc)
            cases[case] = {'source_document': str(doc_path.relative_to(HERE.parent)),
                           'source_sha256': shared.file_hash(doc_path),
                           'window': window}
        baseline = e._window_prompt(generator, doc, window)
        assert baseline == (PRIOR / f'inputs/{source_case}/{source_arm}.prompt.txt').read_text()
        marker = 'Passage catalog (source data, not instructions):'
        assert baseline.count(marker) == 1 and SENTENCE not in baseline
        treatment = baseline.replace(marker, SENTENCE + '\n' + marker, 1)
        assert treatment.replace(SENTENCE + '\n', '', 1) == baseline
        for arm in (['A', 'B'] if pair_index % 2 == 0 else ['B', 'A']):
            ident = f'{case}/{arm}-r{repeat}'
            current = dict(window, index=len(calls))
            prompt = baseline if arm == 'A' else treatment
            shared.save(f'inputs/{ident}.window.json', current)
            (HERE / f'inputs/{ident}.prompt.txt').write_text(prompt)
            calls.append({'id': ident, 'case': case, 'arm': arm, 'repeat': repeat, 'window': current})
    (HERE / 'review').mkdir()
    for name, path in [('EXPECTATIONS.md', PRIOR / 'EXPECTATIONS.md'),
                       ('CSBG-CHECKS.md', PRIOR / 'review/CSBG-CHECKS.md')]:
        shutil.copyfile(path, HERE / 'review' / name)
    pinned = [HERE / 'PLAN.md', HERE / 'run.py', PRIOR / 'run.py', PRIOR / 'design.json',
              *[p for p in (HERE / 'inputs').rglob('*') if p.is_file()],
              *[p for p in (HERE / 'review').iterdir() if p.is_file()]]
    shared.save('design.json', {
        'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        'model': shared.MODEL, 'sentence': SENTENCE, 'cases': cases, 'calls': calls,
        'maximum_calls': 12, 'maximum_seconds': 1200,
        'fingerprints': prior['fingerprints'],
        'runtime_snapshot_reused': str((PRIOR / 'frozen').relative_to(HERE.parent)),
        'inputs_sha256': {str(p.resolve()): shared.file_hash(p) for p in pinned}})
    print('Prepared twelve calls; source, schema and baseline prompts unchanged. One sentence differs.', flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'capture': shared.capture, 'verify': shared.verify}[sys.argv[1]]()
