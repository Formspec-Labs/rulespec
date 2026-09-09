"""Bounded comparison of quote evidence, token alignment and passage references."""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime
import importlib.util
from pathlib import Path
import random
from unittest.mock import patch

from jsonschema import Draft202012Validator
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'minor-audit-improvements/fresh/audit'
LIB = ROOT.parent / 'library-fuzzy-evidence-experiment'
spec = importlib.util.spec_from_file_location('library_trial', LIB / 'experiment.py')
lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lib)
ORIGINAL_READ = a._read_response
ALIGN = lib.resolver.Resolver.align


def exact_align(self, *args, **kwargs):
    kwargs['enable_fuzzy_alignment'] = False
    kwargs['accept_match_lesser'] = False
    return ALIGN(self, *args, **kwargs)


def token_resolver(diagnostics):
    return lib.make_resolver(e._load(LIB / 'configuration.json')[-1], diagnostics)


def id_span(document, reference, window, *, focus=False):
    return a._source_span(document, e.resolve_passage(reference,
        e.passage_catalog(document, window), document, focus=focus))


def outcome(call):
    try:
        return {'accepted': True, 'span': call()}
    except ValueError as error:
        return {'accepted': False, 'reason': str(error)}


def prepare():
    assert not (ROOT / 'design.json').exists()
    lib.previous.verify(lib.previous.BASE)
    lib.previous.verify(LIB)
    book, labels = e._load(BASE / 'rulebook.json'), e._load(BASE / 'labels.json')
    window = e._load(BASE / 'audit.json')['windows'][0]
    e._save(ROOT / 'fixture.json', {'book': book, 'labels': labels, 'window': window})
    # Reuse the generated CUE #SourceRef definition exactly, without new schema semantics.
    ref = deepcopy(a.UNIT_SCHEMA['properties']['scope_refs']['items'])
    schema = deepcopy(a.COMPARISON_SCHEMA)
    for field in ('claim_judgments', 'unit_judgments'):
        item = schema['properties'][field]['items']
        item['properties'] = {('source_refs' if k == 'quotes' else k):
            ({'type': 'array', 'items': ref} if k == 'quotes' else v)
            for k, v in item['properties'].items()}
        item['required'] = ['source_refs' if k == 'quotes' else k for k in item['required']]
    q = a.comparison_prompt()
    p = q.replace('Every judgment needs rationale and exact source quotes.',
        'Every judgment needs rationale and source_refs selecting supplied passages or contiguous ranges. '
        'Select every passage needed to support the judgment, including governing conditions. '
        'The resolver retrieves their exact source text; do not copy quotations into source_refs.')
    p = p.replace('rationale, quotes}]', 'rationale, source_refs}]')
    config = {'Q': {'schema': a.COMPARISON_SCHEMA, 'prompt': q}, 'P': {'schema': schema, 'prompt': p}}
    for arm in config:
        config[arm]['request_prompt'] = e._window_prompt(e._prompt_generator([], config[arm]['prompt']),
            book['document'], window) + '\nDraft and inventory: ' + e._canonical(
            a._model_input(a._comparison_input(book, labels, window)[0]))
    e._save(ROOT / 'configuration.json', config)
    cases = e._load(LIB / 'cases.json')
    for c in cases:
        c['origin'] = 'prior constructed control'
        if c['name'] in ('repeated_exact', 'repeated_normalized'):
            c['selected_refs'] = ['F001']
        elif c['name'] == 'allowed_context':
            c['selected_refs'] = ['C000']
        elif c['name'] == 'out_of_focus':
            c['selected_refs'] = ['F999']
        elif c['name'] == 'inserted_separator':
            c['selected_refs'] = ['F000:F001']
    cases += [
        {'name': 'repeat_within_one_passage', 'source': 'Staff must file. Staff must file.',
         'quote': 'Staff must file.', 'selected_refs': ['F000'], 'expected_accept': False},
        {'name': 'valid_unrelated_id', 'source': 'Staff must file.\n\nManagers may waive fees.',
         'quote': 'Staff must file.', 'selected_refs': ['F001'], 'expected_accept': False},
        {'name': 'invalid_id', 'source': 'Staff must file.', 'quote': 'Staff must file.',
         'selected_refs': ['bogus'], 'expected_accept': False},
        {'name': 'unseen_context_gap', 'source': 'Staff\nMISSING\nmust file.\n\nFocus.',
         'quote': 'Staff must file.', 'start': 26, 'context_spans': [{'start': 0, 'end': 5}, {'start': 14, 'end': 24}],
         'selected_refs': ['C000:C001'], 'expected_accept': False},
        {'name': 'remote_governing_qualification', 'source': 'Only when no emergency prevents compliance.\n\nStaff must call a designated number.',
         'quote': 'Staff must call a designated number.', 'selected_refs': ['F000', 'F001'],
         'expected_accept': True, 'required_component_refs': ['F000', 'F001']},
    ]
    # Three saved failures: selection is hand-reviewed, not model-produced.
    historical = e._load(LIB / 'token-exact-result.json')['audit']['recoveries']
    unique = {r['model_quote']: r for r in historical}
    for i, (quote, receipt) in enumerate(unique.items()):
        span = receipt['source_span']
        refs = ['F002'] if span['start'] < 3315 else ['F003:F004']
        cases.append({'name': f'real_quote_{i}', 'source': book['document']['text'],
            'quote': quote, 'selected_refs': refs, 'expected_accept': True,
            'origin': 'saved provider quote', 'expected_source_span': span})
    e._save(ROOT / 'cases.json', cases)
    plan = Path('thoughts/plans/2026-09-09-comparison-passage-ids-and-token-alignment.md')
    (ROOT / 'PLAN.md').write_text(plan.read_text())
    e._save(ROOT / 'design.json', {'model': 'gemini-3.8-flash', 'temperature': 0,
        'thinking_level': 'medium', 'max_output_tokens': None, 'thinking_budget': None,
        'max_calls': 4, 'cells': ['Q1', 'P1', 'P2', 'Q2'],
        'library_versions': {'langextract': '1.6.0'},
        'runtime_sources_sha256': {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()},
        'inputs_sha256': {n: e._digest((ROOT / n).read_bytes()) for n in
            ('PLAN.md', 'experiment.py', 'fixture.json', 'configuration.json', 'cases.json')},
        'dependencies_sha256': {str(p.relative_to(ROOT.parent)): e._digest(p.read_bytes()) for p in
            (LIB / 'experiment.py', LIB / 'configuration.json', lib.previous.ROOT / 'experiment.py')}})
    print('Prepared frozen inputs and four-call bound.')


def verify_design():
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    for name, digest in design['dependencies_sha256'].items():
        assert e._digest((ROOT.parent / name).read_bytes()) == digest, name
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    return design


def stage1():
    rows = []
    for case in e._load(ROOT / 'cases.json'):
        document = prepare_document(case['source'])
        # Complete the prior fixture's sparse source map so catalog validation also runs.
        if 'source_map' in case:
            parts, cursor = [], 0
            for part in case['source_map']:
                if cursor < part['start']:
                    parts.append({'kind': 'source', 'start': cursor, 'end': part['start'],
                        'source_start': cursor, 'source_end': part['start'], 'source_id': document['id']})
                parts.append({**part, 'text': document['text'][part['start']:part['end']]})
                cursor = part['end']
            if cursor < len(document['text']):
                parts.append({'kind': 'source', 'start': cursor, 'end': len(document['text']),
                    'source_start': cursor, 'source_end': len(document['text']), 'source_id': document['id']})
            document['source_map'] = parts
        window = {'start': case.get('start', 0), 'end': case.get('end', len(document['text'])),
                  'context_spans': case.get('context_spans', [])}
        catalog = e.passage_catalog(document, window)
        refs = case.get('selected_refs', [next(iter(catalog))])
        whole_diagnostics, scoped_diagnostics = [], []
        selected = [outcome(lambda ref=ref: id_span(document, ref, window)) for ref in refs]
        whole = outcome(lambda: token_resolver(whole_diagnostics)(document, case['quote'], window))
        if all(s['accepted'] for s in selected):
            spans = [s['span'] for s in selected]
            scoped_window = {'start': spans[0]['start'], 'end': spans[0]['end'], 'context_spans': spans[1:]}
            scoped = outcome(lambda: token_resolver(scoped_diagnostics)(document, case['quote'], scoped_window))
        else:
            scoped = {'accepted': False, 'reason': 'selected_reference_refused'}
        row = {'case': case['name'], 'origin': case.get('origin', 'new constructed control'),
            'catalog': catalog, 'selected_refs': refs, 'selected': selected, 'whole': whole,
            'scoped': scoped, 'whole_diagnostics': whole_diagnostics, 'scoped_diagnostics': scoped_diagnostics}
        if 'expected_source_span' in case:
            assert whole['span'] == scoped['span'] == case['expected_source_span']
        if case.get('required_component_refs'):
            row['narrowed_retains_all_components'] = scoped['accepted'] and all(
                scoped['span']['start'] <= catalog[ref]['start'] and catalog[ref]['end'] <= scoped['span']['end']
                for ref in case['required_component_refs'])
        rows.append(row)
    return rows


def process(directory, arm, attempts, fixture, config, model):
    book, labels, window = fixture['book'], fixture['labels'], fixture['window']
    payload, errors = ORIGINAL_READ(directory, attempts[0])
    schema_valid = Draft202012Validator(config[arm]['schema']).is_valid(payload)
    results = {}
    for workflow in (['P-ID'] if arm == 'P' else ['Q-exact', 'Q-token']):
        diagnostics = []
        with ExitStack() as stack:
            if workflow == 'Q-token':
                stack.enter_context(patch.object(a, '_span', token_resolver(diagnostics)))
            elif workflow == 'P-ID':
                def translate(directory, attempt):
                    raw, issues = ORIGINAL_READ(directory, attempt)
                    raw = deepcopy(raw)
                    # Preserve malformed rows for production refusal; do not silently repair them.
                    for field in ('claim_judgments', 'unit_judgments'):
                        if isinstance(raw.get(field), list):
                            for row in raw[field]:
                                if isinstance(row, dict) and 'source_refs' in row and 'quotes' not in row:
                                    row['quotes'] = row.pop('source_refs')
                    return raw, issues
                stack.enter_context(patch.object(a, '_read_response', translate))
                stack.enter_context(patch.object(a, '_span', id_span))
            judgments, issues = a._judgments(directory, book, labels, [window], attempts, model)
            report = a._assessment(book, labels, judgments, issues)
        for field in ('claim_judgments', 'unit_judgments'):
            for row in judgments[field]:
                for span in row['source_spans']:
                    assert span['quote'] == book['document']['text'][span['start']:span['end']]
        results[workflow] = {'judgments': judgments, 'issues': issues, 'report': report,
            'diagnostics': diagnostics, 'source_evidence_chars': sum(len(s['quote'])
                for f in ('claim_judgments', 'unit_judgments') for j in judgments[f] for s in j['source_spans'])}
    raw = e._load(directory / attempts[0]['response_file']) if attempts[0].get('response_file') else {}
    return {'schema_valid': schema_valid, 'parse_issues': errors, 'workflows': results,
        'usage': raw.get('usage_metadata'), 'finish_reason': raw.get('candidates', [{}])[0].get('finish_reason')}


def run(mode, env_file):
    design = verify_design()
    with patch.object(lib.resolver.Resolver, 'align', exact_align):
        rows = stage1()
        if mode == 'run' and not (ROOT / 'stage1.json').exists():
            e._save(ROOT / 'stage1.json', rows)
        else:
            assert rows == e._load(ROOT / 'stage1.json')
        print('Stage 1:', len(rows), 'cases recorded' if mode == 'run' else 'cases replayed', flush=True)
        fixture, config = e._load(ROOT / 'fixture.json'), e._load(ROOT / 'configuration.json')
        key = e._credential(env_file) if mode == 'run' else None
        results = {}
        for cell in design['cells']:
            arm, directory = cell[0], ROOT / 'runs' / cell
            if mode == 'run':
                attempts = a._capture(directory, fixture['book']['document'], [fixture['window']],
                    [config[arm]['request_prompt']], config[arm]['schema'], design['model'], key, None,
                    max_output_tokens=None, thinking_level='medium')
                e._save(directory / 'attempts.json', attempts)
            else:
                lib.previous.verify(directory)
                attempts = e._load(directory / 'attempts.json')
            assert len(attempts) == 1
            expected = {'model': design['model'], 'contents': config[arm]['request_prompt'], 'config': {
                'temperature': 0, 'candidate_count': 1, 'thinking_config': {'thinking_level': 'medium'},
                **GeminiSchema(config[arm]['schema'], _use_json_schema=True).to_provider_config()}}
            if attempts[0].get('request_file'):
                request = e._load(directory / attempts[0]['request_file'])
                assert request == expected
                for field in ('claim_judgments', 'unit_judgments'):
                    assert list(request['config']['response_json_schema']['properties'][field]['items']['properties']) == list(
                        config[arm]['schema']['properties'][field]['items']['properties'])
            result = process(directory, arm, attempts, fixture, config, design['model'])
            if mode == 'run':
                e._save(directory / 'result.json', result)
                e._write_manifest(directory)
            else:
                assert result == e._load(directory / 'result.json'), cell
            results[cell] = result
            print(cell, result['finish_reason'], {k: (len(v['judgments']['claim_judgments']),
                len(v['judgments']['unit_judgments']), len(v['issues'])) for k,v in result['workflows'].items()}, flush=True)
        if mode == 'run':
            e._save(ROOT / 'results.json', results)
            shuffled = list(results)
            random.SystemRandom().shuffle(shuffled)
            mapping = {f'R{i+1}': cell for i,cell in enumerate(shuffled)}
            packet = {}
            for label, cell in mapping.items():
                raw, _ = ORIGINAL_READ(ROOT / 'runs' / cell, e._load(ROOT / 'runs' / cell / 'attempts.json')[0])
                packet[label] = {field: [{k:v for k,v in row.items() if k not in ('quotes','source_refs')}
                    for row in raw.get(field, [])] for field in ('claim_judgments', 'unit_judgments')}
            e._save(ROOT / 'blind-review-input.json', packet)
            e._save(ROOT / 'review-key.json', mapping)
        else:
            assert results == e._load(ROOT / 'results.json')
            print('All processing replays identically; no provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    else:
        run(args.mode, args.env_file)
