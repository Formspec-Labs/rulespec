"""Freeze the existing resolver's row-order behavior; no provider calls."""
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import hashlib
import json

import pyarrow.parquet as pq
from refspec.registry import act_resolution as a
from refspec.registry.citation_grammar import ActRelativeCitation

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[3]
ACT = WORK / 'RefSpec/output/usc-act-index-2026-08-22'
CREDIT = WORK / 'RefSpec/output/usc-source-credit-index-2026-08-02'
census = json.loads((HERE / 'census.json').read_text())
index = a.ActIndex.from_artifact(ACT)
credits = a.SourceCreditIndex.from_artifact(CREDIT)
reader = a._read_pinned_parquet

def reversed_names(directory, name):
    rows = reader(directory, name)
    return list(reversed(rows)) if name == 'usc-popular-names.parquet' else rows

with patch.object(a, '_read_pinned_parquet', reversed_names):
    reverse = a.ActIndex.from_artifact(ACT)

queries = set()
for name, rows in census['multi_scope_names'].items():
    for row in rows:
        sections = sorted(index.classifications.get(row['table3_key'], {}))[:20]
        for section in (*sections, '999999'):
            queries.add((name, section, ''))
    for row in rows:
        if row['division']:
            queries.add((name, '101', row['division']))
for name in ('clean air act', 'clean water act', 'ERISA', 'SECURE 2.0 Act of 2022'):
    for section in ('101', '111', '127', '999999'):
        queries.add((name, section, ''))
selected = sorted(queries)[:2000]
cases = []
for name, section, division in selected:
    citation = ActRelativeCitation(name, name, section, division or None)
    before = a.resolve_act_relative_citation(citation, index=index, source_credits=credits)
    reversed_result = a.resolve_act_relative_citation(citation, index=reverse, source_credits=credits)
    cases.append({'query': asdict(citation), 'original': asdict(before), 'reversed': asdict(reversed_result)})

publication = WORK / 'corpora/refspec-registry-unified-agenda-parquet/unified_agenda_legal_authorities.parquet'
fields = pq.read_table(publication, columns=['act_key', 'act_section', 'authority_text', 'rin', 'publication_id']).to_pylist()
fields = [r for r in fields if a.resolve_act_name(r['act_key'], index) in census['multi_scope_names'] if r['act_key']]
result = {
    'module_sha256': hashlib.sha256(Path(a.__file__).read_bytes()).hexdigest(),
    'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        ACT/'usc-popular-names.parquet', ACT/'usc-act-sections.parquet', ACT/'quarantine.parquet',
        CREDIT/'usc-source-credits.parquet', publication)},
    'eligible_queries': len(queries), 'examined_queries': len(cases), 'cases': cases,
    'affected_publication_fields': fields,
}
with (HERE/'baseline.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
changes = [c for c in cases if c['original'] != c['reversed']]
identifiers = [c for c in changes if c['original']['iri'] != c['reversed']['iri']]
print(f'{len(cases)}/{len(queries)} queries; {len(changes)} order-dependent results; {len(identifiers)} identifier changes; {len(fields)} affected publication fields')
for c in identifiers[:10]:
    print(c['query'], c['original']['table3_key'], c['original']['iri'], c['reversed']['table3_key'], c['reversed']['iri'])
