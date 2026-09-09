"""Nine-call interpretation-order screen using existing capture/parser/Core code."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import random
import shutil
from unittest.mock import patch

from jsonschema import Draft202012Validator
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, audit as a
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
GUIDANCE = """
For this run, use the existing optional interpretation fields when the source
contains inherited conditions, exceptions, or nontrivial nested choices.
In scope_text, state the governing case and explain which opening condition or
exception applies to this particular unit. In choice_text, explain which elements
are jointly required and which are independently sufficient alternatives, including
nested grouping. Provide their existing supporting passage-reference fields.
Use concise, source-grounded explanations of these relationships rather than
copying an entire passage or merely restating the statement. Do not invent motives,
resolve missing remote provisions, or transfer another branch's condition.
Leave these fields omitted/null for simple meanings where they add no useful
interpretation. The final statement must independently retain the complete meaning;
an explanation elsewhere cannot substitute for a missing qualifier or option.
"""
CONTROL = """Visitor desk procedures

Visitors must wear badges, except infants. Guides may lend maps.

When a library card was lost more than a month ago and remains unreported, staff must request a replacement. If travel is imminent, a temporary pass may be issued while that replacement is pending.

When a lost library card is found and returned, staff should cancel its replacement request.

Employees and contractors may enter the reading room with either a day pass or a membership card.

The reading room contains two windows.
"""


def attrs(schema):
    return schema['properties']['extractions']['items']['properties']['unit_attributes']


def ordered_digest(value):
    return e._digest(json.dumps(value, ensure_ascii=False, separators=(',', ':')))


def prepare():
    assert not (ROOT / 'design.json').exists()
    baseline = e.load_schema('provider')
    early = deepcopy(baseline)
    properties = attrs(early)['properties']
    first = ['scope_text', 'scope_quotes', 'choice_text', 'choice_quote']
    attrs(early)['properties'] = {k: properties[k] for k in first + [k for k in properties if k not in first]}
    schemas = {'B': baseline, 'L': deepcopy(baseline), 'E': early}
    assert early == baseline and ordered_digest(early) != ordered_digest(baseline)
    assert GeminiSchema(baseline, _use_json_schema=True).to_provider_config() == e.provider_schema().to_provider_config()
    fixtures = ROOT.parent / 'sparse-meaning-check' / 'fixtures'
    docs = {case: e._load(fixtures / f'{case}.json')['book']['document'] for case in ['notice', 'waste']}
    docs['control'] = prepare_document(CONTROL)
    cells = [(case, arm) for case in docs for arm in schemas]
    rng = random.Random(202609092)
    rng.shuffle(cells)
    names = [f'R{i:02d}' for i in range(1, 10)]
    rng.shuffle(names)
    trials = {}
    for name, (case, arm) in zip(names, cells):
        window, = e.plan_windows(docs[case])
        prompt = e._window_prompt(e._prompt_generator([], e.PROMPT + (GUIDANCE if arm != 'B' else '')), docs[case], window)
        trials[name] = {'case': case, 'arm': arm, 'window': window, 'prompt': prompt}
    for case, doc in docs.items():
        e._save(ROOT / 'sources' / f'{case}.json', doc)
    for arm, schema in schemas.items():
        e._save(ROOT / 'schemas' / f'{arm}.json', schema)
    sources = e._runtime_sources()
    for name, path in sources.items():
        dest = ROOT / 'frozen' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    pinned = [ROOT / 'PLAN.md', *list((ROOT / 'sources').glob('*.json')), *list((ROOT / 'schemas').glob('*.json'))]
    e._save(ROOT / 'design.json', {'trials': trials, 'max_calls': 9, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': e.MAX_OUTPUT_TOKENS,
        'runtime_sha256': {k: e._digest(p.read_bytes()) for k, p in sources.items()},
        'inputs_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in pinned},
        'ordered_schema_sha256': {arm: ordered_digest(s) for arm, s in schemas.items()}})
    print('Prepared nine blinded run IDs; baseline is unchanged, E/L differ only in schema key order.')


def process(directory, design, trial, schema, document, attempt):
    parsed = e._attempt_result(attempt, directory, document, trial['window'])
    payload, errors = a._read_response(directory, attempt)
    schema_errors = [list(err.absolute_path) for err in Draft202012Validator(schema).iter_errors(payload)]
    run = {'id': 'interpretation-order:' + directory.name, 'model': design['model'],
           'source_sha256': document['sha256'], 'temperature': 0, 'thinking_level': 'low'}
    book = e.core.compile_candidates(document, parsed['candidates'], run)
    rows = payload.get('extractions', [])
    order = list(attrs(schema)['properties'])
    observed = [list(row.get('unit_attributes', {})) for row in rows]
    populated = [{k: v for k, v in row.get('unit_attributes', {}).items()
                  if k in {'scope_text', 'choice_text'} and v} for row in rows]
    response = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
    return {'parsed': parsed, 'rulebook': book, 'validation': e._check_graph(book['graph']),
        'output': payload, 'statistics': {'schema_errors': schema_errors, 'response_errors': errors,
        'observed_orders': observed, 'order_followed': [keys == [k for k in order if k in keys] for keys in observed],
        'interpretation_rows': sum(bool(v) for v in populated), 'rows': len(rows),
        'usage': response.get('usage_metadata'), 'model_version': response.get('model_version')}}


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
        schema = e._load(ROOT / 'schemas' / (trial['arm'] + '.json'))
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
            assert ordered_digest(request['config']['response_json_schema']) == design['ordered_schema_sha256'][trial['arm']]
        with patch.object(e, '_create_model', side_effect=AssertionError('Parsing called provider')):
            result = process(directory, design, trial, schema, document, attempt)
        if mode == 'run':
            e._save(directory / 'result.json', result)
            # Canonical field order and no usage/config prevent leaking the arm.
            e._save(ROOT / 'blind' / f'{name}.json', json.loads(e._canonical({'case': trial['case'],
                'output': result['output'], 'refusals': result['parsed']['refusals']})))
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print(name, trial['case'], result['parsed']['status'], 'rows', result['statistics']['rows'], flush=True)
    if mode == 'replay':
        print('All nine requests verified and results replayed identically; zero provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode, args.env_file)
