"""Six bounded fresh calls using native CUE and the existing capture/Core path."""
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import time
from unittest.mock import patch

from jsonschema import Draft202012Validator
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, audit as a
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
ACTOR = '''
    // Responsible source-supported actor, not the approving authority or a
    // definition's subject. Null when unstated; retain literal you when needed.
    actor!: *null | #Actor
    actor_quote!: *null | #ActorQuote
'''
LINKS = '''
    // Index ID of the term this unit explicitly defines. Null on a use or mention.
    defines_term?: *null | #NonemptyText
    // IDs of defined terms discussed by this unit, including a definition's own
    // subject. Reuse the index; do not invent equivalence from shared wording.
    term_refs?: *null | [...#NonemptyText]
'''
TERM = '''
// Only terms explicitly defined by this supplied document. This is a local
// definition index, not a list of all nouns, actors or external references.
// Keep different senses separate; never expand an acronym from world knowledge.
#DefinedTerm: {
    id!: #NonemptyText
    // Exact source name for the defined sense, preferably its supplied full name.
    label!: #NonemptyText
    // Exact alternative names/acronyms explicitly equated in the source.
    aliases!: #EvidenceQuotes
    // Passage IDs supporting definition, name and every alias. Introductory
    // acronym expansions may need an additional passage beyond the definition.
    source_refs!: [...#SourceRef]
}
'''


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fingerprint():
    return {name: e._digest(path.read_bytes()) for name, path in e._runtime_sources().items()}


def prepare():
    assert not (ROOT / 'design.json').exists(), 'Do not overwrite a prepared design'
    builder = load_module('native_builder', REPO / 'tools/build_extraction_schemas.py')
    source = Path(e.__file__).parent / 'schema_data'
    canonical = (source / 'document-understanding.cue').read_text()
    schemas = {}
    with tempfile.TemporaryDirectory(prefix='rulespec-actor-definition-') as tmp:
        binary, profile = Path(tmp) / 'export', Path(tmp) / 'profile'
        subprocess.run(['go', 'build', '-mod=readonly', '-trimpath', '-o', str(binary), '.'],
            cwd=REPO / 'tools/cue_schema_export', check=True, capture_output=True)
        shutil.copytree(source, profile)
        shutil.copytree(REPO / 'constraints/core', profile / 'cue.mod/pkg/rulespec.invalid/core')
        for arm in ['baseline', 'actor', 'index']:
            cue = canonical
            if arm != 'baseline':
                # Keep the complete statement first. Reuse the existing field
                # types and evidence instructions rather than replacing them.
                cue = cue.replace('    kind!: #Kind', ACTOR + '    kind!: #Kind', 1)
            if arm == 'index':
                cue = cue.replace('#FirstMeaning: {', '#FirstMeaning: {' + LINKS, 1)
                cue = cue.replace('\textractions!: [...#SemanticUnit]',
                    '\tterms!: [...#DefinedTerm]\n\textractions!: [...#SemanticUnit]', 1) + TERM
            (profile / 'document-understanding.cue').write_text(cue)
            native = json.loads(subprocess.run([str(binary), '-definition', '#ExtractionResponse', str(profile)],
                check=True, capture_output=True, text=True).stdout)
            schema = builder.model_schema(native['schema'], native['metadata'])
            if arm == 'baseline':
                assert schema == e.load_schema('provider')
            schemas[arm] = schema
            e._save(ROOT / 'schemas' / (arm + '.json'), schema)
            (ROOT / 'schemas' / (arm + '.cue')).write_text(cue)
    # Assert the actual model-facing differences, including optionality.
    def attrs(schema):
        return schema['properties']['extractions']['items']['properties']['unit_attributes']
    stripped = deepcopy(schemas['actor'])
    for field in ['actor', 'actor_quote']:
        del attrs(stripped)['properties'][field]
        attrs(stripped)['required'].remove(field)
    assert stripped == schemas['baseline']
    stripped = deepcopy(schemas['index'])
    del stripped['properties']['terms']
    stripped['required'].remove('terms')
    for field in ['defines_term', 'term_refs']:
        del attrs(stripped)['properties'][field]
    assert stripped == schemas['actor']
    assert list(schemas['index']['properties'])[0] == 'terms'
    docs = {
        'passport': e._load(REPO / '.tools/review-workspaces/sparse-meaning-passport/document.json'),
        'controls': prepare_document((ROOT / 'controls.txt').read_text(), title='Constructed actor and definition controls'),
    }
    for name, doc in docs.items():
        e._save(ROOT / 'sources' / (name + '.json'), doc)
    cells = [(case, arm) for case in docs for arm in schemas]
    rng = random.Random(202609097)
    rng.shuffle(cells)
    names = [f'V{i:02}' for i in range(1, 7)]
    rng.shuffle(names)
    trials = {}
    for name, (case, arm) in zip(names, cells):
        window, = e.plan_windows(docs[case])
        trials[name] = {'case': case, 'arm': arm, 'window': window,
            'prompt': e._window_prompt(e._prompt_generator([]), docs[case], window)}
    inputs = [ROOT / n for n in ['PLAN.md', 'REVIEW.md', 'controls.txt', 'run.py']]
    inputs += list((ROOT / 'schemas').glob('*')) + list((ROOT / 'sources').glob('*'))
    e._save(ROOT / 'design.json', {'trials': trials, 'max_calls': 6, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'low', 'max_output_tokens': 16384,
        'base_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'runtime_sha256': fingerprint(),
        'inputs_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs}})
    print('Prepared six calls; actual native schema differences verified.')


def process(directory, design, trial, schema, document, attempt):
    payload, errors = a._read_response(directory, attempt)
    schema_errors = [list(err.absolute_path) for err in Draft202012Validator(schema).iter_errors(payload)]
    rows = payload.get('extractions', []) if isinstance(payload, dict) else []
    candidates, refusals, components = [], [], []
    if not errors and not schema_errors:
        for i, row in enumerate(rows):
            normalized = deepcopy(row)
            attrs = normalized['unit_attributes']
            extra = {field: attrs.pop(field) for field in ['actor', 'actor_quote', 'defines_term', 'term_refs'] if field in attrs}
            components.append({'row': i, **extra})
            parsed = e.parse_response_text(json.dumps({'extractions': [normalized]}), document, trial['window'])
            for refusal in parsed['refusals']:
                refusal['row_index'] = i
                refusals.append(refusal)
            for candidate in parsed['candidates']:
                candidate.update({field: extra.get(field) or '' for field in ['actor', 'actor_quote']})
                candidates.append(candidate)
    else:
        refusals.append({'code': 'invalid_trial_response'})
    run = {'id': 'actor-definition:' + directory.name, 'model': design['model'],
        'source_sha256': document['sha256'], 'temperature': 0, 'thinking_level': 'low'}
    book = e.core.compile_candidates(document, candidates, run)
    terms = payload.get('terms', []) if isinstance(payload, dict) else []
    link_errors, term_evidence = [], []
    if not errors and not schema_errors:
        ids = [term['id'] for term in terms]
        if len(ids) != len(set(ids)):
            link_errors.append('duplicate_term_ids')
        catalog = e.passage_catalog(document, trial['window'])
        for term in terms:
            evidence = []
            for ref in term['source_refs']:
                try:
                    evidence.append(e.resolve_passage(ref, catalog, document))
                except ValueError as error:
                    link_errors.append({'term': term['id'], 'ref': ref, 'error': str(error)})
            text = '\n'.join(p['quote'] for p in evidence).casefold()
            for label in [term['label'], *term['aliases']]:
                if label.casefold() not in text:
                    link_errors.append({'term': term['id'], 'unsupported_label': label})
            term_evidence.append({'id': term['id'], 'evidence': evidence})
        defined = set()
        for item in components:
            target = item.get('defines_term')
            if target:
                defined.add(target)
                if rows[item['row']]['unit_attributes']['kind'] != 'definition':
                    link_errors.append({'row': item['row'], 'error': 'non_definition_defines_term'})
            for ref in ([target] if target else []) + (item.get('term_refs') or []):
                if ref not in ids:
                    link_errors.append({'row': item['row'], 'dangling_term': ref})
        for term_id in set(ids) - defined:
            link_errors.append({'term': term_id, 'error': 'missing_defining_row'})
    raw = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
    return {'output': payload, 'components': components, 'term_evidence': term_evidence,
        'link_errors': link_errors, 'response_errors': errors, 'schema_errors': schema_errors,
        'refusals': refusals, 'rulebook': book, 'validation': e._check_graph(book['graph']),
        'usage': raw.get('usage_metadata'), 'model_version': raw.get('model_version')}


def execute(mode, env_file):
    design = e._load(ROOT / 'design.json')
    assert fingerprint() == design['runtime_sha256'], 'Use pinned runtime; do not silently update the design'
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    if mode == 'replay':
        for name, digest in e._load(ROOT / 'manifest.json')['artifacts_sha256'].items():
            assert e._digest((ROOT / name).read_bytes()) == digest, name
    else:
        assert not (ROOT / 'runs').exists(), 'Do not overwrite or silently retry'
    key = e._credential(env_file) if mode == 'run' else None
    start = time.monotonic()
    for name, trial in design['trials'].items():
        directory = ROOT / 'runs' / name
        document = e._load(ROOT / 'sources' / (trial['case'] + '.json'))
        schema = e._load(ROOT / 'schemas' / (trial['arm'] + '.json'))
        if mode == 'run':
            if time.monotonic() - start >= 1200:
                print('Twenty-minute bound reached; remaining cells unattempted.', flush=True)
                break
            attempt, = a._capture(directory, document, [trial['window']], [trial['prompt']], schema,
                design['model'], key, None, max_output_tokens=16384, thinking_level='low')
        else:
            attempt = e._load(directory / 'attempt-0000.json')
        if attempt.get('request_file'):
            request = e._load(directory / attempt['request_file'])
            assert request['contents'] == trial['prompt'] and request['model'] == design['model']
            assert request['config'] == {'temperature': 0, 'candidate_count': 1,
                'max_output_tokens': 16384, 'thinking_config': {'thinking_level': 'low'},
                **GeminiSchema(schema, _use_json_schema=True).to_provider_config()}
        with patch.object(e, '_create_model', side_effect=AssertionError('Processing called provider')):
            result = process(directory, design, trial, schema, document, attempt)
        if mode == 'run':
            e._save(directory / 'result.json', result)
            e._save(ROOT / 'blind' / (name + '.json'), {'case': trial['case'],
                'statements': [{'unit': r['unit'], **{k: r['unit_attributes'][k] for k in ['statement', 'kind', 'modality']}}
                    for r in result['output'].get('extractions', [])], 'refusals': result['refusals']})
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json'), name
        print(name, trial['case'], attempt['status'], len(result['rulebook']['accepted']), 'accepted', flush=True)
    if mode == 'replay':
        print('Six exact requests and processing results replayed; zero provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode, args.env_file)
