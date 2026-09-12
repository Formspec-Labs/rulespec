"""Bounded confidence experiment using existing capture, parser and Core code."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

from jsonschema import Draft202012Validator
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import audit as a, core, extraction as e

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INSTRUCTION = """
After each extracted unit, populate its confidence object as specified by the
schema. Assess this unit's independently usable statement, including its full
governing conditions and required details; exact supporting evidence alone does
not establish that the statement preserved them. Give a probability from 0 to 1
and a brief externally checkable basis. This is uncalibrated self-assessment,
not a claim that the extraction omitted no other units. Keep all ordinary
extraction instructions and preserve source meaning in the statement itself.
"""


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def confidence_schemas():
    sys.path.insert(0, str(ROOT / 'tools'))
    import build_extraction_schemas as b
    exports = {}
    with tempfile.TemporaryDirectory(prefix='confidence-schema-') as temporary:
        directory = Path(temporary)
        module = directory / 'profile'
        module.mkdir()
        shutil.copytree(b.SOURCE / 'cue.mod', module / 'cue.mod')
        shutil.copytree(ROOT / 'constraints/core', module / 'cue.mod/pkg/rulespec.invalid/core')
        shutil.copy(HERE / 'confidence.cue', module / 'confidence.cue')
        binary = directory / 'export'
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath', '-o', str(binary), '.'],
                       cwd=b.GENERATOR, check=True, capture_output=True)
        for name in ('SelfConfidence', 'NumericConfidence'):
            result = subprocess.run([str(binary), '-definition', '#' + name, str(module)],
                                    check=True, capture_output=True, text=True)
            exports[name] = json.loads(result.stdout)
    native = exports['NumericConfidence']['schema']
    # Native export retains the score bounds on the parent disjunction but
    # loses them on the indexed field. Reuse that generated branch verbatim.
    branches = native['$defs']['ConfidenceRecord']['anyOf']
    numeric = [v for v in branches if set(v.get('properties', {})) == {'rkaf:score'}]
    assert len(numeric) == 1
    score = numeric[0]['properties']['rkaf:score']
    assert score == {'type': 'number', 'minimum': 0, 'maximum': 1}
    exported = exports['SelfConfidence']
    model = b.model_schema(exported['schema'], exported['metadata'])
    model['properties']['score'].update(score)
    basis = model['properties']['basis']
    assert all(item == basis['items'] for item in basis['prefixItems'])
    del basis['prefixItems']  # Identical prefix/items constraints; equivalent.
    compiled = e._load(ROOT / 'compiled/json-schema/core/confidence-record.schema.json')
    compiled['$ref'] = '#/$defs/ConfidenceRecord'
    compiled['allOf'] = [numeric[0]]
    save('native-exports.json', exports)
    save('confidence.schema.json', model)
    save('core-confidence.schema.json', compiled)
    valid = {'score': 0.5, 'basis': ['Explicit source; all supplied conditions retained.']}
    validator = Draft202012Validator(model)
    validator.validate(valid)
    invalid = [dict(valid, score=-0.01), dict(valid, score=1.01), dict(valid, score='0.5'),
               dict(valid, score=True), dict(valid, basis=[]), {'score': 0.5},
               {'basis': ['source']}, dict(valid, extra='noise')]
    assert all(not validator.is_valid(row) for row in invalid)
    record = confidence_record(valid)
    core_validator = Draft202012Validator(compiled)
    core_validator.validate(record)
    for field in record:
        bad = {k: v for k, v in record.items() if k != field}
        assert not core_validator.is_valid(bad), field
    assert not core_validator.is_valid(dict(record, **{'rkaf:score': 1.01}))
    save('schema-checks.json', {'model_positive': 1, 'model_negative': len(invalid),
        'core_positive': 1, 'core_missing_field_negatives': len(record), 'core_score_bound_negative': 1,
        'limitation': 'Composes existing compiled Core metadata validation with its native-generated numeric branch. Not a general Core compiler fix.'})
    return model


def confidence_record(value):
    return {'@type': 'rkaf:ConfidenceRecord', 'rkaf:confidenceMethod': 'rkaf:model-inference',
        'rkaf:calibrationStatus': 'rkaf:uncalibrated', 'rkaf:generatedBy': 'urn:rulespec:model:' + e.DEFAULT_MODEL,
        'rkaf:score': value['score'], 'rkaf:confidenceBasis': value['basis']}


def prepare():
    schema = e.provider_schema().schema_dict
    variant = deepcopy(schema)
    unit = variant['properties']['extractions']['items']
    unit['properties']['confidence'] = confidence_schemas()
    unit['required'].append('confidence')
    save('schemas.json', {'A': schema, 'B': variant})
    save('runtime.json', e._freeze(HERE, e.invented_examples(), schema))
    cases = []
    old = e._load(HERE / '../2026-09-12-csbg-focus/cells.json')
    for case in ('csbg', 'iep', 'lea'):
        path = ('../2026-09-12-csbg/sources/document.json' if case == 'csbg' else
                f'../2026-09-12-subordinate-inventory/sources/{case}.json')
        doc = e._load(HERE / path)
        window = (next(c['window'] for c in old if c['id'] == 'plan') if case == 'csbg'
                  else e.plan_windows(doc)[0])
        cases.append({'id': case, 'source': path, 'window': window})
    cells, review_key = [], {}
    for case in cases:
        doc = e._load(HERE / case['source'])
        prompt = e._window_prompt(e._prompt_generator(e.invented_examples()), doc, case['window'])
        arms = ['A', 'B']
        random.SystemRandom().shuffle(arms)
        for i, arm in enumerate(arms, 1):
            identity = f"{case['id']}-{i}"
            cells.append({'id': identity, 'case': case['id'], 'arm': arm,
                          'prompt': prompt + (INSTRUCTION if arm == 'B' else '')})
            review_key[identity] = arm
    random.SystemRandom().shuffle(cells)
    save('cells.json', {'cases': cases, 'cells': cells})
    save('review-key.json', review_key)
    save('configuration.json', {'model': e.DEFAULT_MODEL, 'temperature': 0, 'thinking_level': 'low',
        'max_output_tokens': 16384, 'instruction': INSTRUCTION, 'max_attempts': 6,
        'max_capture_seconds': 900, 'max_total_tokens': 150000})
    paths = [p for p in HERE.rglob('*') if p.is_file()]
    paths += [HERE / c['source'] for c in cases]
    paths += [ROOT / 'tools/build_extraction_schemas.py', ROOT / 'tools/cue_schema_export/main.go',
              ROOT / 'tools/cue_schema_export/go.mod', ROOT / 'tools/cue_schema_export/go.sum']
    save('precall-pins.json', {str(p.relative_to(HERE)) if p.is_relative_to(HERE) else
        str(Path('../../../') / p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths})
    print('Six paired extraction requests pinned; confidence schema checks passed')


def pins():
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def decode(cell, case):
    directory = HERE / 'captures' / cell['id']
    attempt = e._load(directory / 'attempts.json')[0]
    payload, errors = a._read_response(directory, attempt)
    canonical = deepcopy(payload)
    records, confidence_errors = [], []
    validator = Draft202012Validator(e._load(HERE / 'confidence.schema.json'))
    core_validator = Draft202012Validator(e._load(HERE / 'core-confidence.schema.json'))
    for i, row in enumerate(canonical.get('extractions', [])):
        if not isinstance(row, dict):
            continue
        if cell['arm'] == 'B':
            value = row.pop('confidence', None)
            failures = list(validator.iter_errors(value))
            if failures:
                confidence_errors.append({'row_index': i, 'raw': value,
                    'errors': [{'path': list(x.absolute_path), 'validator': x.validator} for x in failures]})
            else:
                record = confidence_record(value)
                core_validator.validate(record)
                records.append({'row_index': i, 'confidence': record})
    doc = e._load(HERE / case['source'])
    parsed = e.parse_response_text(json.dumps(canonical, allow_nan=False), doc, case['window'])
    run = {'id': core.NS + 'run:' + e._digest([HERE.name, cell['id']]), 'model': e.DEFAULT_MODEL,
        'status': parsed['status'], 'scope': 'Experimental supplied window only; no whole-document completeness claim',
        'windows': [{**case['window'], 'status': parsed['status']}]}
    book = core.compile_candidates(doc, parsed['candidates'], run)
    return {'response_errors': errors, 'canonical_response': canonical, 'parsed': parsed,
            'confidence': records, 'confidence_errors': confidence_errors,
            'book': book, 'validation': e._check_graph(book['graph'])}


def capture():
    pins()
    assert not (HERE / 'captures').exists()
    config = e._load(HERE / 'cells.json')
    schemas = e._load(HERE / 'schemas.json')
    cases = {c['id']: c for c in config['cases']}
    key = e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    started = time.monotonic()
    for i, cell in enumerate(config['cells']):
        usage = e.recorded_usage(HERE).get('tokens', {}).get('total_token_count', 0)
        if i >= 6 or time.monotonic() - started >= 900 or usage >= 150000:
            save('stopped.json', {'calls': i, 'reason': 'predeclared_bound'}); break
        case = cases[cell['case']]
        directory = HERE / 'captures' / cell['id']
        start = time.monotonic()
        attempts = a._capture(directory, e._load(HERE / case['source']), [case['window']],
            [cell['prompt']], schemas[cell['arm']], e.DEFAULT_MODEL, key, None,
            max_output_tokens=16384, thinking_level='low')
        save(f"captures/{cell['id']}/attempts.json", attempts)
        save(f"captures/{cell['id']}/timing.json", {'seconds': time.monotonic() - start})
        result = decode(cell, case)
        save(f"decoded/{cell['id']}.json", result)
        # Do not expose scores, bases, arm names, or arm-specific response fields.
        save(f"review/{cell['id']}.json", {'rows': [dict(row_index=n, **row)
            for n, row in enumerate(result['canonical_response'].get('extractions', []))],
            'parsed_refusals': result['parsed']['refusals'], 'rejected': result['book']['rejected']})
        print(f'Captured {i + 1}/6', flush=True)
    save('usage.json', e.recorded_usage(HERE / 'captures'))
    save('capture-time.json', {'seconds': time.monotonic() - started})


def verify():
    pins()
    config = e._load(HERE / 'cells.json')
    schemas = e._load(HERE / 'schemas.json')
    stripped = deepcopy(schemas['B'])
    unit = stripped['properties']['extractions']['items']
    del unit['properties']['confidence']
    unit['required'].remove('confidence')
    assert stripped == schemas['A']
    cases = {c['id']: c for c in config['cases']}
    checks = []
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        for cell in config['cells']:
            directory = HERE / 'captures' / cell['id']
            if not directory.exists():
                continue
            attempt = e._load(directory / 'attempts.json')[0]
            expected = {'model': e.DEFAULT_MODEL, 'contents': cell['prompt'], 'config': {
                'temperature': 0, 'max_output_tokens': 16384, 'thinking_config': {'thinking_level': 'low'},
                'candidate_count': 1, **GeminiSchema(schemas[cell['arm']], _use_json_schema=True).to_provider_config()}}
            assert e._load(directory / attempt['request_file']) == expected
            result = decode(cell, cases[cell['case']])
            assert result == e._load(HERE / f"decoded/{cell['id']}.json")
            checks.append({'cell': cell['id'], 'request_equal': True, 'adapter_replay_equal': True,
                'response_errors': result['response_errors'], 'confidence_errors': result['confidence_errors'],
                'validation': result['validation']['status'], 'accepted': len(result['book']['accepted']),
                'rejected': len(result['book']['rejected']), 'refusals': len(result['parsed']['refusals'])})
    save('verification.json', {'provider_calls': 0, 'single_schema_addition': True, 'checks': checks})
    print('Actual requests and derived parser/Core replay verified without provider calls')


if __name__ == '__main__':
    {'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
