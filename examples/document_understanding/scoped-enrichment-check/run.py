"""Retain the note; reuse the preceding trial's capture, parsing and replay."""
import argparse
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
HELPER = ROOT.parent / 'omit-empty-explanation-check/run.py'
spec = importlib.util.spec_from_file_location('omission_trial', HELPER)
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
trial.ROOT = ROOT
e, previous = trial.e, trial.previous


def prepare():
    assert not (ROOT / 'design.json').exists()
    builder = trial.module('native_builder', trial.REPO / 'tools/build_extraction_schemas.py')
    schemas = {}
    with tempfile.TemporaryDirectory(prefix='rulespec-scoped-enrichment-') as tmp:
        binary, profile = Path(tmp) / 'export', Path(tmp) / 'profile'
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath', '-o', str(binary), '.'],
            cwd=trial.REPO / 'tools/cue_schema_export', check=True, capture_output=True)
        shutil.copytree(previous.SOURCE, profile)
        shutil.copytree(trial.REPO / 'constraints/core', profile / 'cue.mod/pkg/rulespec.invalid/core')
        for field in ['logic_explanation', 'modality_explanation']:
            for arm in ['N', 'E']:
                original = (trial.PREVIOUS / 'schemas' / (field + '.cue')).read_text()
                cue = original
                if arm == 'E':
                    cue = trial.omission_cue(original, field)
                    # Restore the exact explanatory comment and declaration; all
                    # other optional fields retain the preceding omission policy.
                    start = original.index('#FirstMeaning: {')
                    original_note = original[start:original.index('    statement!:', start)]
                    start = cue.index('#FirstMeaning: {')
                    cue = cue[:start] + original_note + cue[cue.index('    statement!:', start):]
                (profile / 'document-understanding.cue').write_text(cue)
                raw = subprocess.run([str(binary), '-definition', '#ExtractionResponse', str(profile)],
                    check=True, capture_output=True, text=True)
                native = json.loads(raw.stdout)
                schema = builder.model_schema(native['schema'], native['metadata'])
                control = e._load(trial.PREVIOUS / 'schemas' / (field + '.json'))
                attrs, baseline = previous.attributes(schema), previous.attributes(control)
                assert attrs['required'] == baseline['required']
                assert list(attrs['properties'])[0] == field
                assert attrs['properties'][field] == baseline['properties'][field]
                if arm == 'N':
                    assert schema == control
                name = field + '-' + arm
                schemas[name] = schema
                e._save(ROOT / 'schemas' / (name + '.json'), schema)
                (ROOT / 'schemas' / (name + '.cue')).write_text(cue)
    cells = [(case, field, arm) for case in ['notice', 'waste']
        for field in ['logic_explanation', 'modality_explanation'] for arm in ['N', 'E']]
    rng = random.Random(202609095)
    rng.shuffle(cells)
    names = [f'T{i:02d}' for i in range(1, 9)]
    rng.shuffle(names)
    docs = {case: e._load(trial.PREVIOUS / 'sources' / (case + '.json')) for case in ['notice', 'waste']}
    trials = {}
    for name, (case, field, arm) in zip(names, cells):
        window, = e.plan_windows(docs[case])
        prompt = e.PROMPT if arm == 'N' else trial.omission_prompt()
        trials[name] = {'case': case, 'field': field, 'arm': arm, 'window': window,
            'prompt': e._window_prompt(e._prompt_generator([], prompt), docs[case], window)}
    for case, doc in docs.items():
        e._save(ROOT / 'sources' / (case + '.json'), doc)
    shutil.copytree(ROOT.parent / 'omit-empty-explanation-check/frozen', ROOT / 'frozen')
    shutil.copyfile(HELPER, ROOT / 'frozen/omission-trial.py')
    shutil.copyfile(trial.PREVIOUS / 'REVIEW.md', ROOT / 'REVIEW.md')
    inputs = [ROOT / 'PLAN.md', ROOT / 'REVIEW.md', *list((ROOT / 'sources').glob('*')), *list((ROOT / 'schemas').glob('*'))]
    e._save(ROOT / 'design.json', {'trials': trials, 'max_calls': 8, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': e.MAX_OUTPUT_TOKENS,
        'omission_helper_sha256': e._digest(HELPER.read_bytes()),
        'shared_helper_sha256': e._digest((trial.PREVIOUS / 'run.py').read_bytes()),
        'runtime_sha256': {k: e._digest(p.read_bytes()) for k, p in e._runtime_sources().items()},
        'inputs_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs},
        'ordered_schema_sha256': {k: previous.ordered_digest(v) for k, v in schemas.items()}})
    print('Prepared eight calls; explanation definitions exactly match fresh controls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    else:
        assert e._digest(HELPER.read_bytes()) == e._load(ROOT / 'design.json')['omission_helper_sha256']
        trial.execute(args.mode, args.env_file)
