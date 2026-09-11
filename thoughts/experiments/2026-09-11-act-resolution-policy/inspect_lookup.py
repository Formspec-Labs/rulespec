"""Bounded native lookups and retained source rows; no model calls or writes upstream."""
from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
from refspec.registry import act_resolution as a, citation_grammar as g

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[3]
ACT = WORK/'RefSpec/output/usc-act-index-2026-08-22'
CREDIT = WORK/'RefSpec/output/usc-source-credit-index-2026-08-02'
PUBLICATION = WORK/'corpora/refspec-registry-unified-agenda-parquet/unified_agenda_legal_authorities.parquet'
index = a.ActIndex.from_artifact(ACT)
credits = a.SourceCreditIndex.from_artifact(CREDIT)
by_division = defaultdict(list)
outside = []
for name, (division, _) in sorted(index.division_by_name.items()):
    key = index.table3_key_by_name.get(name)
    if key is None:
        continue
    by_division[key,division].append(name)
    bounds = index.act_page_range(name)
    if bounds is not None:
        for section, rows in sorted(index.classifications.get(key,{}).items()):
            if len(rows)==1 and rows[0].statutes_at_large_page is not None:
                if not bounds[0] <= rows[0].statutes_at_large_page <= bounds[1]:
                    outside.append((name,section))
credit_pairs = sorted({(name,section) for law,division,section in credits.targets
                       for name in by_division[law,division]})
publication_rows = pq.read_table(PUBLICATION,columns=['act_key','act_section','authority_text','rin','publication_id']).to_pylist()
publication_pairs = {}
for row in publication_rows:
    if row['act_key'] and row['act_section']:
        publication_pairs.setdefault((row['act_key'],row['act_section']),row)
selected = sorted(set(credit_pairs[:20000]) | set(outside[:1000]) | set(publication_pairs))
captures=[]
for name,section in selected:
    result=a.resolve_act_relative_citation(g.ActRelativeCitation(name,name,section),index=index,source_credits=credits)
    key=result.table3_key
    row={'name':name,'section':section,'bounds':index.act_page_range(result.act_key) if result.act_key else None,
         'table3_rows':[row._asdict() for row in index.classifications.get(key,{}).get(section,())],
         'resolution':asdict(result)}
    if (name,section) in publication_pairs:
        row['publication_field']=publication_pairs[name,section]
    captures.append(row)
quarantine=pq.read_table(ACT/'quarantine.parquet',filters=[('reason','=','statutes_at_large_page_span_narrowed')]).to_pylist()
selected_keys={(c['resolution']['table3_key'],c['section']) for c in captures}
retained_spans=[r for r in quarantine if (r['table3_key'],r['raw_value'].partition(' -> ')[0]) in selected_keys]
result={'provider_calls':0,'populations':{'credit_pairs_eligible':len(credit_pairs),'credit_pairs_examined':min(len(credit_pairs),20000),
        'single_outside_pairs_eligible':len(outside),'single_outside_pairs_examined':min(len(outside),1000),
        'publication_pairs':len(publication_pairs),'distinct_examined':len(selected)},
        'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (PUBLICATION,ACT/'receipt.json',ACT/'usc-popular-names.parquet',ACT/'usc-act-sections.parquet',ACT/'quarantine.parquet',CREDIT/'receipt.json',CREDIT/'usc-source-credits.parquet')},
        'module_sha256':hashlib.sha256(Path(a.__file__).read_bytes()).hexdigest(),
        'cases':captures,'retained_page_spans':retained_spans}
with (HERE/'baseline.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result['populations'],indent=2))
multi=[c for c in captures if c['resolution']['iri'] and c['resolution']['source_credit_status']=='multi_target']
print('Accepted despite multiple source-credit targets:',len(multi))
for c in multi[:8]:
    print(c['name'],c['section'],c['resolution']['iri'],c['bounds'],c['table3_rows'],
          [(t['usc_title'],t['usc_section']) for t in c['resolution']['source_credit_targets']])
print('Retained narrowed page rows:',len(retained_spans))
for r in retained_spans[:12]:print(r)
print('Native outcomes:',dict(Counter(c['resolution']['answered_by'] or c['resolution']['unresolved_reason'] for c in captures)))
