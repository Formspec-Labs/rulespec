"""Bounded existing index/consumer comparison; captures are never overwritten."""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

import pyarrow.parquet as pq
from refspec.registry import act_resolution as acts, citation_grammar as grammar
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator import references, core

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[3]
ACT = WORK / 'RefSpec/output/usc-act-index-2026-08-22'
CREDIT = WORK / 'RefSpec/output/usc-source-credit-index-2026-08-02'
PUBLICATION = WORK / 'corpora/refspec-registry-unified-agenda-parquet/unified_agenda_legal_authorities.parquet'
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(WORK / 'RefSpec/tests'))
from act_resolution_evidence_oracle import resolve_act_relative_citation as original
index, credits = acts.ActIndex.from_artifact(ACT), acts.SourceCreditIndex.from_artifact(CREDIT)
files = [PUBLICATION, *ACT.glob('*.json'), *ACT.glob('*.parquet'), *CREDIT.glob('*.json'), *CREDIT.glob('*.parquet')]
result = {'provider_calls': 0, 'inputs': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
          'modules': {m.__name__:{'path':m.__file__,'sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()}
                      for m in (acts,grammar,references,core)},
          'fields': [], 'diagnostics': [], 'conflicts': [], 'resolved_with_multi_target_credits': []}
for row in json.loads((HERE / 'publication-fields.json').read_text()):
    doc = prepare_document(row['authority_text'])
    result['fields'].append({'text': row['authority_text'],
        'without_credits': scan_references(doc, act_index=ACT),
        'with_credits': scan_references(doc, act_index=ACT, source_credit_index=CREDIT)})
    key = acts.resolve_act_name(row['act_key'], index)
    division = index.division_by_name.get(key)
    result['diagnostics'].append({'act_name': row['act_key'], 'section': row['act_section'],
        'popular_names': pq.read_table(ACT/'usc-popular-names.parquet', filters=[('name_key','=',key)]).to_pylist(),
        'classifications': pq.read_table(ACT/'usc-act-sections.parquet', filters=[
            ('table3_key','=',index.table3_key_by_name[key]),('act_section','=',row['act_section'])]).to_pylist(),
        'source_credits': pq.read_table(CREDIT/'usc-source-credits.parquet', filters=[
            ('public_law','=',index.table3_key_by_name[key]),('division','=',division[0] if division else ''),
            ('act_section','=',row['act_section'])]).to_pylist(),
        'native': asdict(acts.resolve_act_relative_citation(grammar.ActRelativeCitation(
            act_name=row['act_key'], act_key=row['act_key'], section=row['act_section']), index=index, source_credits=credits))})
rows = pq.read_table(PUBLICATION, columns=['act_key','act_section','authority_text','rin','publication_id']).to_pylist()
pairs = {}
for row in rows:
    if row['act_key'] and row['act_section']:
        pairs.setdefault((row['act_key'],row['act_section']), row)
census = Counter()
for (name, section), row in sorted(pairs.items())[:2000]:
    answer = acts.resolve_act_relative_citation(grammar.ActRelativeCitation(name, name, section), index=index, source_credits=credits)
    old = asdict(original(grammar.ActRelativeCitation(name,name,section),index=index,source_credits=credits))
    new = asdict(answer)
    for key in ('source_credit_targets','conflicting_targets'):
        old.pop(key,None);new.pop(key,None)
    assert old == new, (name, section, old, new)
    census[answer.answered_by or answer.unresolved_reason] += 1
    if answer.iri and answer.source_credit_status == 'multi_target':
        result['resolved_with_multi_target_credits'].append({'publication_row':row,'resolution':asdict(answer)})
    if answer.unresolved_reason == 'sources_disagree':
        result['conflicts'].append({'publication_row':row, 'resolution':asdict(answer),
            'classifications':{k:[asdict(x) for x in v] for k,v in index.classifications[answer.table3_key].items()
                               if k == section or k.startswith(section+'(')},
            'source_credits':[asdict(t) for t in credits.targets_for(answer.table3_key,index.division_by_name[answer.act_key][0],section)]})
result['population'] = {'distinct_derived_pairs':len(pairs),'examined':min(len(pairs),2000),
                        'outcomes':dict(census), 'original_resolution_fields_equal': True}
with args.output.open('x') as f: json.dump(result,f,indent=2);f.write('\n')
for row in result['fields']:
    print(row['text'])
    for arm in ('without_credits','with_credits'):
        print(arm,[(r['value'],r.get('resolution')) for r in row[arm]['candidates']])
print(json.dumps(result['population'],indent=2))
print('Conflicts:',len(result['conflicts']))
