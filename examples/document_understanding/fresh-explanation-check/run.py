"""Fresh-source four-arm comparison using existing native schemas/capture/Core."""
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
from unittest.mock import patch
import xml.etree.ElementTree as ET

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, audit as a
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
HELPER = ROOT.parent / 'field-explanation-check/run.py'
spec = importlib.util.spec_from_file_location('field_trial', HELPER)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def prepare():
    assert not (ROOT / 'design.json').exists()
    spec = importlib.util.spec_from_file_location('native_builder', REPO / 'tools/build_extraction_schemas.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    schemas = {}
    with tempfile.TemporaryDirectory(prefix='rulespec-fresh-schema-') as tmp:
        binary, profile = Path(tmp) / 'export', Path(tmp) / 'profile'
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath', '-o', str(binary), '.'],
            cwd=REPO / 'tools/cue_schema_export', check=True, capture_output=True)
        shutil.copytree(h.SOURCE, profile)
        shutil.copytree(REPO / 'constraints/core', profile / 'cue.mod/pkg/rulespec.invalid/core')
        for field in ['baseline', 'omit_only', 'logic_explanation', 'modality_explanation']:
            if field == 'baseline':
                cue = (h.SOURCE / 'document-understanding.cue').read_text()
            else:
                name = 'logic_explanation' if field == 'omit_only' else field
                cue = (ROOT.parent / 'scoped-enrichment-check/schemas' / (name + '-E.cue')).read_text()
                if field == 'omit_only':
                    start = cue.index('#FirstMeaning: {\n') + len('#FirstMeaning: {\n')
                    cue = cue[:start] + cue[cue.index('    statement!:', start):]
            (profile / 'document-understanding.cue').write_text(cue)
            raw = subprocess.run([str(binary), '-definition', '#ExtractionResponse', str(profile)],
                check=True, capture_output=True, text=True)
            native = json.loads(raw.stdout)
            schema = builder.model_schema(native['schema'], native['metadata'])
            if field == 'baseline':
                assert schema == e.load_schema('provider')
            elif field != 'omit_only':
                assert schema == e._load(ROOT.parent / 'scoped-enrichment-check/schemas' / (field + '-E.json'))
                stripped = deepcopy(schema)
                del h.attributes(stripped)['properties'][field]
                h.attributes(stripped)['required'].remove(field)
                assert stripped == schemas['omit_only']
                assert list(h.attributes(schema)['properties'])[0] == field
            schemas[field] = schema
            e._save(ROOT / 'schemas' / (field + '.json'), schema)
            (ROOT / 'schemas' / (field + '.cue')).write_text(cue)
    # All XML paragraph text is retained verbatim internally; only boundary
    # whitespace and markup are normalized. Non-normative citation metadata stays
    # in the saved XML. HEAD/P elements are joined with blank lines for passages.
    retrieval = e._load(ROOT / 'sources/retrieval.json')
    docs = {}
    for case in ['oxygen', 'alarms', 'procurement']:
        xml = ET.parse(ROOT / 'sources' / (case + '.xml')).getroot()
        blocks = [''.join(c.itertext()).strip() for c in xml if c.tag in ['HEAD', 'P']]
        text = '\n\n'.join(blocks) + '\n'
        docs[case] = prepare_document(text, title=blocks[0], source_url=retrieval[case]['url'])
        e._save(ROOT / 'sources' / (case + '.json'), docs[case])
        (ROOT / 'sources' / (case + '.txt')).write_text(text)
    old = e._load(ROOT.parent / 'scoped-enrichment-check/design.json')
    omit_prompt = next(t['prompt'] for t in old['trials'].values() if t['arm'] == 'E')
    # Reuse the exact prompt generator input from the preceding experiment.
    omission_path = ROOT.parent / 'omit-empty-explanation-check/run.py'
    spec = importlib.util.spec_from_file_location('omission_trial', omission_path)
    omission = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(omission)
    prompt = omission.omission_prompt()
    assert prompt in omit_prompt
    cells = [(case, field) for case in docs for field in schemas]
    rng = random.Random(202609096)
    rng.shuffle(cells)
    names = [f'U{i:02d}' for i in range(1, 13)]
    rng.shuffle(names)
    trials = {}
    for name, (case, field) in zip(names, cells):
        window, = e.plan_windows(docs[case])
        trials[name] = {'case': case, 'field': field, 'window': window,
            'prompt': e._window_prompt(e._prompt_generator([], e.PROMPT if field == 'baseline' else prompt), docs[case], window)}
    shutil.copytree(ROOT.parent / 'scoped-enrichment-check/frozen', ROOT / 'frozen')
    inputs = [ROOT / 'PLAN.md', ROOT / 'REVIEW.md', *list((ROOT / 'sources').glob('*')), *list((ROOT / 'schemas').glob('*'))]
    e._save(ROOT / 'design.json', {'trials': trials, 'max_calls': 12, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': e.MAX_OUTPUT_TOKENS,
        'shared_helper_sha256': e._digest(HELPER.read_bytes()),
        'runtime_sha256': {k: e._digest(p.read_bytes()) for k, p in e._runtime_sources().items()},
        'inputs_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs},
        'ordered_schema_sha256': {k: h.ordered_digest(v) for k, v in schemas.items()}})
    print('Prepared twelve calls; each note is the only schema difference from omission-only.')


def execute(mode, env_file):
    design = e._load(ROOT / 'design.json')
    assert e._digest(HELPER.read_bytes()) == design['shared_helper_sha256']
    assert design['runtime_sha256'] == {k: e._digest(p.read_bytes()) for k, p in e._runtime_sources().items()}
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest
    if mode == 'replay':
        for name, digest in e._load(ROOT / 'manifest.json')['artifacts_sha256'].items():
            assert e._digest((ROOT / name).read_bytes()) == digest
    elif (ROOT / 'runs').exists():
        raise ValueError('Captured runs already exist; do not overwrite or silently retry')
    key = e._credential(env_file) if mode == 'run' else None
    for name, trial in design['trials'].items():
        directory = ROOT / 'runs' / name
        doc = e._load(ROOT / 'sources' / (trial['case'] + '.json'))
        schema = e._load(ROOT / 'schemas' / (trial['field'] + '.json'))
        if mode == 'run':
            attempt, = a._capture(directory, doc, [trial['window']], [trial['prompt']], schema,
                design['model'], key, None, max_output_tokens=design['max_output_tokens'], thinking_level='low')
        else:
            attempt = e._load(directory / 'attempt-0000.json')
        if attempt.get('request_file'):
            request = e._load(directory / attempt['request_file'])
            assert request['contents'] == trial['prompt'] and request['model'] == design['model']
            assert request['config'] == {'temperature': 0, 'candidate_count': 1,
                'max_output_tokens': design['max_output_tokens'], 'thinking_config': {'thinking_level': 'low'},
                **GeminiSchema(schema, _use_json_schema=True).to_provider_config()}
            assert h.ordered_digest(request['config']['response_json_schema']) == design['ordered_schema_sha256'][trial['field']]
        with patch.object(e, '_create_model', side_effect=AssertionError('Parsing called provider')):
            result = h.process(directory, design, trial, schema, doc, attempt)
        if mode == 'run':
            e._save(directory / 'result.json', result)
            e._save(ROOT / 'blind' / (name + '.json'), json.loads(e._canonical({'case': trial['case'],
                'output': result['normalized_output'], 'refusals': result['parsed']['refusals']})))
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print(name, trial['case'], result['parsed']['status'], len(result['rulebook']['accepted']), flush=True)
    if mode == 'replay':
        print('All twelve requests verified and results replayed identically; zero provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode, args.env_file)
