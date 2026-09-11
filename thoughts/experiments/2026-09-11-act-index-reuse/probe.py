"""Bounded source/index observations, retaining unsupported cases and raw fields."""
from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
import time

import pyarrow.parquet as pq
from refspec.registry import act_resolution as acts, citation_grammar as grammar
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
REFSPEC = Path('/Users/mikewolfd/Work/RefSpec')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=HERE/'observations.json')
args = parser.parse_args()
cases = json.loads((HERE / 'cases.json').read_text())
source = Path(cases['source'])
assert sha(source) == cases['sha256']
act_dir = REFSPEC / 'output/usc-act-index-2026-08-22'
credit_dir = REFSPEC / 'output/usc-source-credit-index-2026-08-02'
started = time.perf_counter()
index = acts.ActIndex.from_artifact(act_dir)
credits = acts.SourceCreditIndex.from_artifact(credit_dir)
load_seconds = time.perf_counter() - started
names = set(index.table3_key_by_name) | set(index.alias_by_name)
result = {'cases_sha256': sha(HERE / 'cases.json'), 'design_sha256': sha(HERE / 'design.md'),
    'modules': {m.__name__: {'path': m.__file__, 'sha256': sha(Path(m.__file__))} for m in (acts, grammar)},
    'inputs': {str(p): sha(p) for directory in (act_dir, credit_dir) for p in directory.iterdir() if p.suffix in ('.json', '.parquet')},
    'load_seconds': load_seconds, 'indexed_names': len(names), 'classification_laws': len(index.classifications),
    'source_credit_keys': len(credits.targets), 'network_calls': 0, 'provider_calls': 0, 'observations': []}
for case in [*({'id': f"publication-{n}", 'text': row['authority_text']} for n,row in enumerate(cases['rows'])), *cases['diagnostics']]:
    if case['id'] == 'missing-index':
        try:
            acts.ActIndex.from_artifact(Path(case['path']))
        except Exception as error:
            result['observations'].append({'id':case['id'], 'error':type(error).__name__, 'message':str(error)})
        else:
            result['observations'].append({'id':case['id'], 'unexpected_load':True})
        continue
    citations = grammar.find_act_relative_citations(case['text'], act_names=names)
    result['observations'].append({'id':case['id'], 'text':case['text'],
        'baseline':scan_references(prepare_document(case['text'])),
        'citations':[asdict(c) for c in citations],
        'occurrences':[asdict(c) for c in grammar.find_act_relative_occurrences(case['text'], act_names=names)],
        'resolutions':[asdict(acts.resolve_act_relative_citation(c, index=index, source_credits=credits)) for c in citations]})
# Read the actual classification rows supporting the known development control.
key = index.table3_key_by_name['clean air act']
result['clean_air_control_source'] = {'table3_key':key,
    'popular_names':pq.read_table(act_dir/'usc-popular-names.parquet', filters=[('name_key','=','clean air act')]).to_pylist(),
    'classifications':pq.read_table(act_dir/'usc-act-sections.parquet', filters=[('table3_key','=',key),('act_section','=','111')]).to_pylist()}
with args.output.open('x') as file:
    json.dump(result,file,indent=2,ensure_ascii=False)
    file.write('\n')
print(json.dumps({k:result[k] for k in ['load_seconds','indexed_names','classification_laws','source_credit_keys']}))
for row in result['observations']:
    print(json.dumps({k:v for k,v in row.items() if k!='baseline'},ensure_ascii=False))
print(json.dumps(result['clean_air_control_source'],ensure_ascii=False))
