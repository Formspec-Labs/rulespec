"""Field-specific explanations: isolated native CUE schemas, existing capture/Core."""
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

from jsonschema import Draft202012Validator
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, audit as a

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
SOURCE = Path(e.__file__).parent / 'schema_data'
GUIDANCE = {
    'actor_explanation': 'Explain who this specific rule addresses or permits to act, using explicit source wording or a supported antecedent. Distinguish neighboring actors and an institution from its management. Preserve literal you when no role is named; do not infer a duty bearer from a title, citation or neighboring paragraph. Null when actor attribution is straightforward or unstated.',
    'modality_explanation': 'Explain the source wording that determines whether this unit is an obligation, recommendation, permission, prohibition, absence of duty, descriptive possibility or factual statement. Preserve negation, generally, examples and uncertainty; may not be required does not by itself establish an unconditional exemption. Null when modal force is straightforward and unambiguous.',
    'logic_explanation': 'Explain the relationship between this rule\'s logical components: what must hold together, which alternatives suffice, what an exception changes, and which event starts a deadline. Preserve nested choices, thresholds, units and all qualifying branches. Distinguish grammatical category lists from cumulative requirements. Do not invent executable logic or fill missing referenced provisions. Null when the logical relationship is simple and needs no explanation.',
    'applicability_explanation': 'Explain which surrounding lead-in, parent case, example relationship or exception governs this specific unit and why that attachment follows from the source. Identify every inherited limit that the standalone statement must retain, and distinguish neighboring cases whose limits do not apply. A preceding rule may govern a later example even if the example does not repeat its conditions. Null only when no contextual attachment or scope ambiguity needs interpretation.',
}
COMMON = 'Write at most two concise, source-grounded sentences about this field\'s interpretive decision, not a transcript of deliberation. Do not copy the entire passage or restate the final statement. The statement must still be independently complete. This note is model interpretation, not source evidence. '


def attributes(schema):
    return schema['properties']['extractions']['items']['properties']['unit_attributes']


def ordered_digest(value):
    return e._digest(json.dumps(value, ensure_ascii=False, separators=(',', ':')))


def prepare():
    assert not (ROOT / 'design.json').exists()
    spec = importlib.util.spec_from_file_location('native_builder', REPO / 'tools/build_extraction_schemas.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    canonical = (SOURCE / 'document-understanding.cue').read_text()
    schemas = {}
    with tempfile.TemporaryDirectory(prefix='rulespec-field-schema-') as tmp:
        binary = Path(tmp) / 'export'
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath', '-o', str(binary), '.'],
            cwd=REPO / 'tools/cue_schema_export', check=True, capture_output=True)
        module = Path(tmp) / 'module'
        shutil.copytree(SOURCE, module)
        shutil.copytree(REPO / 'constraints/core', module / 'cue.mod/pkg/rulespec.invalid/core')
        for field in ['baseline', *GUIDANCE]:
            cue = canonical
            if field != 'baseline':
                declaration = ('    // ' + COMMON + GUIDANCE[field] + '\n'
                    + '    ' + field + '!: *null | #NonemptyText @title(' + json.dumps(field.replace('_', ' ').capitalize()) + ')\n')
                cue = cue.replace('#FirstMeaning: {\n', '#FirstMeaning: {\n' + declaration, 1)
            (module / 'document-understanding.cue').write_text(cue)
            result = subprocess.run([str(binary), '-definition', '#ExtractionResponse', str(module)],
                check=True, capture_output=True, text=True)
            native = json.loads(result.stdout)
            schema = builder.model_schema(native['schema'], native['metadata'])
            if field == 'baseline':
                assert schema == e.load_schema('provider')
            else:
                assert list(attributes(schema)['properties'])[0] == field
                assert field in attributes(schema)['required']
                stripped = deepcopy(schema)
                del attributes(stripped)['properties'][field]
                attributes(stripped)['required'].remove(field)
                assert stripped == schemas['baseline']
            schemas[field] = schema
            e._save(ROOT / 'schemas' / (field + '.json'), schema)
            (ROOT / 'schemas' / (field + '.cue')).write_text(cue)
    docs = {case: e._load(ROOT.parent / 'sparse-meaning-check/fixtures' / (case + '.json'))['book']['document']
            for case in ['passport', 'notice', 'waste']}
    trials = [(case, field) for case in docs for field in schemas]
    rng = random.Random(202609093)
    rng.shuffle(trials)
    names = [f'R{i:02d}' for i in range(1, 16)]
    rng.shuffle(names)
    cells = {}
    for name, (case, field) in zip(names, trials):
        window, = e.plan_windows(docs[case])
        cells[name] = {'case': case, 'field': field, 'window': window,
            'prompt': e._window_prompt(e._prompt_generator([]), docs[case], window)}
    for case, doc in docs.items():
        e._save(ROOT / 'sources' / (case + '.json'), doc)
    sources = e._runtime_sources()
    build_sources = [REPO / 'tools/build_extraction_schemas.py', *list((REPO / 'tools/cue_schema_export').glob('*.go')),
        *list((REPO / 'tools/cue_schema_export').glob('go.*')), *list((REPO / 'constraints/core').glob('*.cue'))]
    for name, path in {**sources, **{'build/' + str(p.relative_to(REPO)): p for p in build_sources}}.items():
        dest = ROOT / 'frozen' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    inputs = [ROOT / 'PLAN.md', ROOT / 'REVIEW.md', *list((ROOT / 'sources').glob('*.json')), *list((ROOT / 'schemas').glob('*'))]
    e._save(ROOT / 'design.json', {'trials': cells, 'max_calls': 15, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': e.MAX_OUTPUT_TOKENS,
        'runtime_sha256': {k: e._digest(p.read_bytes()) for k, p in sources.items()},
        'inputs_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs},
        'ordered_schema_sha256': {k: ordered_digest(v) for k, v in schemas.items()}})
    print('Prepared 15 calls; native CUE verified that each variant adds only its one nullable field.')


def process(directory, design, trial, schema, document, attempt):
    payload, errors = a._read_response(directory, attempt)
    schema_errors = [list(err.absolute_path) for err in Draft202012Validator(schema).iter_errors(payload)]
    normalized = deepcopy(payload)
    notes = []
    for index, row in enumerate(normalized.get('extractions', [])):
        attrs = row.get('unit_attributes', {})
        if trial['field'] != 'baseline' and trial['field'] in attrs:
            notes.append({'row': index, 'unit': row.get('unit'), 'field': trial['field'], 'explanation': attrs.pop(trial['field'])})
    # Refuse a whole malformed experimental response instead of passing unchecked
    # extra content through the production parser. Original content stays saved.
    if errors or schema_errors:
        parsed = {'candidates': [], 'refusals': [{'code': 'invalid_trial_response'}], 'status': 'failed'}
    else:
        parsed = e.parse_response_text(json.dumps(normalized, ensure_ascii=False), document, trial['window'])
    run = {'id': 'field-explanation:' + directory.name, 'model': design['model'],
           'source_sha256': document['sha256'], 'temperature': 0, 'thinking_level': 'low'}
    book = e.core.compile_candidates(document, parsed['candidates'], run)
    raw = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
    return {'output': payload, 'normalized_output': normalized, 'notes': notes, 'parsed': parsed,
        'rulebook': book, 'validation': e._check_graph(book['graph']), 'schema_errors': schema_errors,
        'response_errors': errors, 'usage': raw.get('usage_metadata'), 'model_version': raw.get('model_version')}


def execute(mode, env_file):
    design = e._load(ROOT / 'design.json')
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
        schema = e._load(ROOT / 'schemas' / (trial['field'] + '.json'))
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
            assert ordered_digest(request['config']['response_json_schema']) == design['ordered_schema_sha256'][trial['field']]
        with patch.object(e, '_create_model', side_effect=AssertionError('Parsing called provider')):
            result = process(directory, design, trial, schema, document, attempt)
        if mode == 'run':
            e._save(directory / 'result.json', result)
            e._save(ROOT / 'blind' / (name + '.json'), json.loads(e._canonical({'case': trial['case'],
                'output': result['normalized_output'], 'refusals': result['parsed']['refusals']})))
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print(name, trial['case'], result['parsed']['status'], len(result['rulebook']['accepted']), flush=True)
    if mode == 'replay':
        print('All 15 requests verified and results replayed identically; zero provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode, args.env_file)
