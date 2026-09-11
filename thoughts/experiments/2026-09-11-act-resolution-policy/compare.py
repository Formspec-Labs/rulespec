"""Compare the two native policy changes independently on frozen lookups."""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

from refspec.registry import act_resolution as a
from refspec.registry.citation_grammar import ActRelativeCitation

HERE=Path(__file__).resolve().parent
WORK=HERE.parents[3]
sys.path.insert(0,str(WORK/'RefSpec/tests'))
import act_resolution_evidence_oracle as prior

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
out=parser.parse_args().output
baseline=json.loads((HERE/'baseline.json').read_text())
for filename,digest in baseline['inputs'].items():
    assert hashlib.sha256(Path(filename).read_bytes()).hexdigest()==digest,filename
index=a.ActIndex.from_artifact(WORK/'RefSpec/output/usc-act-index-2026-08-22')
credits=a.SourceCreditIndex.from_artifact(WORK/'RefSpec/output/usc-source-credit-index-2026-08-02')
added={'source_credit_targets','conflicting_targets','table3_candidate_iri'}
main=lambda result:{key:value for key,value in result.items() if key not in added}
def run(resolver):
    return [asdict(resolver(ActRelativeCitation(c['name'],c['name'],c['section']),index=index,source_credits=credits))
            for c in baseline['cases']]
old=run(prior.resolve_act_relative_citation)
assert [main(r) for r in old]==[main(c['resolution']) for c in baseline['cases']]
with patch.object(prior,'_resolve_through_table3',a._resolve_through_table3):
    page_only=run(prior.resolve_act_relative_citation)
with patch.object(a,'_resolve_through_table3',prior._resolve_through_table3):
    plural_only=run(a.resolve_act_relative_citation)
combined=run(a.resolve_act_relative_citation)
result={'provider_calls':0,'population':baseline['populations'],
        'inputs':baseline['inputs'],'module_sha256':hashlib.sha256(Path(a.__file__).read_bytes()).hexdigest(),
        'rules':{'division':a.DIVISION_RULE,'composition':a.SOURCE_COMPOSITION_RULE},
        'prior_oracle_original_fields_equal':True,'arms':{},'violations':[]}
for arm,answers in [('page_only',page_only),('plural_only',plural_only),('combined',combined)]:
    changes=[]
    outcomes=Counter()
    for case,before,after in zip(baseline['cases'],old,answers,strict=True):
        outcomes[after['answered_by'] or after['unresolved_reason']]+=1
        if main(before)!=main(after):
            changes.append({'name':case['name'],'section':case['section'],
                            'before':case['resolution'],'after':after})
        if arm in ('plural_only','combined') and after['iri'] and after['source_credit_status']=='multi_target':
            result['violations'].append([arm,case['name'],case['section'],'plural_answer_selected'])
        if arm=='plural_only' and main(before)!=main(after):
            if not (before['iri'] and before['source_credit_status']=='multi_target'
                    and after['iri'] is None and after['table3_candidate_iri']==before['iri']):
                result['violations'].append([arm,case['name'],case['section'],'unexpected_verdict_change'])
        if arm=='page_only' and before['table3_reason']!=after['table3_reason']:
            key=(before['table3_key'],case['section'])
            rows=case['table3_rows']
            reliable=key not in index.narrowed_page_sections and all(r['statutes_at_large_page'] is not None for r in rows)
            outside=case['bounds'] is not None and reliable and all(
                not case['bounds'][0]<=r['statutes_at_large_page']<=case['bounds'][1] for r in rows)
            allowed=(len(rows)==1 and outside and after['table3_reason']=='act_section_outside_act') or (
                len(rows)>1 and not reliable and before['table3_reason']=='act_section_outside_act'
                and after['table3_reason']=='act_section_ambiguous')
            if not allowed:result['violations'].append([arm,case['name'],case['section'],'unjustified_page_change'])
    result['arms'][arm]={'outcomes':dict(outcomes),'changed_pairs':len(changes),
                        'selected_plural_answers':sum(bool(r['iri']) and r['source_credit_status']=='multi_target' for r in answers),
                        'changes':changes}
result['combined_results']=[{'name':c['name'],'section':c['section'],'resolution':r}
                            for c,r in zip(baseline['cases'],combined,strict=True)]
with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({arm:{k:v for k,v in data.items() if k!='changes'} for arm,data in result['arms'].items()},indent=2))
print('Violations:',result['violations'])
assert not result['violations']
