"""Eight-call omission check; reuse the preceding field trial's processing."""
import argparse
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
from unittest.mock import patch

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, audit as a

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
PREVIOUS = ROOT.parent / 'field-explanation-check'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


previous = module('previous_field_trial', PREVIOUS / 'run.py')


def omission_cue(cue, field):
    start = cue.index('#FirstMeaning: {')
    end = cue.index('\n}', start)
    block = cue[start:end]
    block = block.replace(field + '!: *null |', field + '?:')
    block = block.replace('*null | ', '')
    block = block.replace('even when null', 'even when omitted')
    block = block.replace('Null when choice_text is null.', 'Omit when choice_text is absent.')
    block = block.replace('Null when', 'Omit when').replace('Null for', 'Omit for')
    block = block.replace('lead-ins. Null\n', 'lead-ins. Omit\n')
    cue = cue[:start] + block + cue[end:]
    for name in ['ScopeText', 'ChoiceText', 'ModalityQuote', 'SourceRef']:
        cue = cue.replace('#' + name + ': string @', '#' + name + ': #NonemptyText @')
    cue = cue.replace('#References: [...string] @', '#References: [...#NonemptyText] @')
    return cue


def omission_prompt():
    prompt = e.PROMPT.replace('Omit optional fields or use null', 'Omit optional fields')
    prompt = prompt.replace('Null choice_quote means no separate choice evidence.', 'Omit choice_quote when no separate choice evidence is recorded.')
    prompt = prompt.replace('Null scope_text', 'Omitted scope_text')
    prompt = prompt.replace('leave them null for a', 'omit them for a')
    return prompt + '\nFor optional fields, emit the key only when it has a useful nonempty value. Otherwise omit the key entirely. Do not substitute null, empty strings/lists, or literal null/N/A placeholders. Omission never permits dropping qualifications or options from statement.\n'


def prepare():
    assert not (ROOT / 'design.json').exists()
    builder = module('native_builder', REPO / 'tools/build_extraction_schemas.py')
    schemas = {}
    with tempfile.TemporaryDirectory(prefix='rulespec-omit-schema-') as tmp:
        binary = Path(tmp) / 'export'
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath', '-o', str(binary), '.'],
            cwd=REPO / 'tools/cue_schema_export', check=True, capture_output=True)
        profile = Path(tmp) / 'profile'
        shutil.copytree(previous.SOURCE, profile)
        shutil.copytree(REPO / 'constraints/core', profile / 'cue.mod/pkg/rulespec.invalid/core')
        for field in ['logic_explanation', 'modality_explanation']:
            for arm in ['N', 'O']:
                cue = (PREVIOUS / 'schemas' / (field + '.cue')).read_text()
                if arm == 'O':
                    cue = omission_cue(cue, field)
                (profile / 'document-understanding.cue').write_text(cue)
                raw = subprocess.run([str(binary), '-definition', '#ExtractionResponse', str(profile)],
                    check=True, capture_output=True, text=True)
                exported = json.loads(raw.stdout)
                schema = builder.model_schema(exported['schema'], exported['metadata'])
                if arm == 'N':
                    assert schema == e._load(PREVIOUS / 'schemas' / (field + '.json'))
                else:
                    assert previous.attributes(schema)['required'] == ['statement', 'kind', 'modality']
                    assert list(previous.attributes(schema)['properties'])[0] == field
                name = field + '-' + arm
                schemas[name] = schema
                e._save(ROOT / 'schemas' / (name + '.json'), schema)
                (ROOT / 'schemas' / (name + '.cue')).write_text(cue)
    cells = [(case, field, arm) for case in ['notice', 'waste']
             for field in ['logic_explanation', 'modality_explanation'] for arm in ['N', 'O']]
    rng = random.Random(202609094)
    rng.shuffle(cells)
    names = [f'S{i:02d}' for i in range(1, 9)]
    rng.shuffle(names)
    docs = {case: e._load(PREVIOUS / 'sources' / (case + '.json')) for case in ['notice', 'waste']}
    trials = {}
    for name, (case, field, arm) in zip(names, cells):
        window, = e.plan_windows(docs[case])
        trials[name] = {'case': case, 'field': field, 'arm': arm, 'window': window,
            'prompt': e._window_prompt(e._prompt_generator([], e.PROMPT if arm == 'N' else omission_prompt()), docs[case], window)}
    for case, doc in docs.items():
        e._save(ROOT / 'sources' / (case + '.json'), doc)
    shutil.copytree(PREVIOUS / 'frozen', ROOT / 'frozen')
    shutil.copyfile(PREVIOUS / 'run.py', ROOT / 'frozen/field-trial.py')
    shutil.copyfile(PREVIOUS / 'REVIEW.md', ROOT / 'REVIEW.md')
    inputs = [ROOT / 'PLAN.md', ROOT / 'REVIEW.md', *list((ROOT / 'sources').glob('*')), *list((ROOT / 'schemas').glob('*'))]
    e._save(ROOT / 'design.json', {'trials': trials, 'max_calls': 8, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': e.MAX_OUTPUT_TOKENS,
        'shared_helper_sha256': e._digest((PREVIOUS / 'run.py').read_bytes()),
        'runtime_sha256': {k: e._digest(p.read_bytes()) for k, p in e._runtime_sources().items()},
        'inputs_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs},
        'ordered_schema_sha256': {k: previous.ordered_digest(v) for k, v in schemas.items()}})
    print('Prepared eight calls with native CUE omission-only schemas.')


def execute(mode, env_file):
    design = e._load(ROOT / 'design.json')
    assert e._digest((PREVIOUS / 'run.py').read_bytes()) == design['shared_helper_sha256']
    assert design['runtime_sha256'] == {k: e._digest(p.read_bytes()) for k, p in e._runtime_sources().items()}
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest
    if mode == 'replay':
        for name, digest in e._load(ROOT / 'manifest.json')['artifacts_sha256'].items():
            assert e._digest((ROOT / name).read_bytes()) == digest
    key = e._credential(env_file) if mode == 'run' else None
    for name, trial in design['trials'].items():
        directory = ROOT / 'runs' / name
        document = e._load(ROOT / 'sources' / (trial['case'] + '.json'))
        schema_name = trial['field'] + '-' + trial['arm']
        schema = e._load(ROOT / 'schemas' / (schema_name + '.json'))
        if mode == 'run':
            attempt, = a._capture(directory, document, [trial['window']], [trial['prompt']], schema,
                design['model'], key, None, max_output_tokens=design['max_output_tokens'], thinking_level='low')
        else:
            attempt = e._load(directory / 'attempt-0000.json')
        if attempt.get('request_file'):
            request = e._load(directory / attempt['request_file'])
            assert request['contents'] == trial['prompt'] and request['model'] == design['model']
            assert request['config'] == {'temperature': 0, 'candidate_count': 1,
                'max_output_tokens': design['max_output_tokens'], 'thinking_config': {'thinking_level': 'low'},
                **GeminiSchema(schema, _use_json_schema=True).to_provider_config()}
            assert previous.ordered_digest(request['config']['response_json_schema']) == design['ordered_schema_sha256'][schema_name]
        with patch.object(e, '_create_model', side_effect=AssertionError('Parsing called provider')):
            result = previous.process(directory, design, trial, schema, document, attempt)
        if mode == 'run':
            e._save(directory / 'result.json', result)
            e._save(ROOT / 'blind' / (name + '.json'), json.loads(e._canonical({'case': trial['case'],
                'output': result['normalized_output'], 'refusals': result['parsed']['refusals']})))
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print(name, trial['case'], result['parsed']['status'], len(result['rulebook']['accepted']), flush=True)
    if mode == 'replay':
        print('All eight requests verified and results replayed identically; zero provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode, args.env_file)
