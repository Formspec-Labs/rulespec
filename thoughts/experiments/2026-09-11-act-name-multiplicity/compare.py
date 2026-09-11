"""Compare fixed native questions; enumerate every allowed identity change."""
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
import argparse
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
WORK=HERE.parents[3]
sys.path.insert(0,str(WORK/'RefSpec/tests'))
import act_name_multiplicity_oracle as old
from refspec.registry import act_resolution as a
from refspec.registry.citation_grammar import ActRelativeCitation

args=argparse.ArgumentParser()
args.add_argument('--output',type=Path,required=True)
args=args.parse_args()
baseline=json.loads((HERE/'baseline.json').read_text())
for file,digest in baseline['input_sha256'].items():
    assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==digest,file
act=WORK/'RefSpec/output/usc-act-index-2026-08-22'
credit=WORK/'RefSpec/output/usc-source-credit-index-2026-08-02'
index=a.ActIndex.from_artifact(act)
previous=old.ActIndex.from_artifact(act)
credits=a.SourceCreditIndex.from_artifact(credit)
reader=a._read_pinned_parquet
with patch.object(a,'_read_pinned_parquet',lambda directory,name: list(reversed(reader(directory,name))) if name=='usc-popular-names.parquet' else reader(directory,name)):
    reverse=a.ActIndex.from_artifact(act)

ADDED={'act_division','name_sources','candidate_resolutions'}
def old_fields(result):
    return {k:v for k,v in result.items() if k not in ADDED}

def plain(result):
    return json.loads(json.dumps(asdict(result)))

def check(citation,before):
    oracle=plain(old.resolve_act_relative_citation(citation,index=previous,source_credits=credits))
    assert old_fields(oracle)==old_fields(before),citation
    outcome=a.resolve_act_relative_citation(citation,index=index,source_credits=credits)
    after=plain(outcome)
    assert after==plain(a.resolve_act_relative_citation(citation,index=reverse,source_credits=credits)),citation
    sources=index.name_candidates.get(outcome.act_key,())
    if not sources:
        assert old_fields(after)==old_fields(before),citation
    else:
        pairs={(r.table3_key,r.division or citation.division) for r in sources
               if not (citation.division and r.division and citation.division!=r.division)}
        assert set(outcome.name_sources)==set(sources)
        if len(pairs)>1:
            assert outcome.iri is None and outcome.unresolved_reason=='act_name_ambiguous'
            assert {(c.table3_key,c.act_division) for c in outcome.candidate_resolutions}==pairs
        elif len(pairs)==1:
            assert (outcome.table3_key,outcome.act_division)==next(iter(pairs))
            assert not outcome.candidate_resolutions
        else:
            assert outcome.unresolved_reason=='act_division_conflict'
    return after

diagnostics=[]
for item in baseline['cases']:
    after=check(ActRelativeCitation(**item['query']),item['original'])
    diagnostics.append({'query':item['query'],'before':item['original'],'after':after})
prior_combined=json.loads((HERE.parent/'2026-09-11-act-resolution-policy/comparison.json').read_text())
policy=[]
for item in prior_combined['combined_results']:
    before=item['resolution']
    after=check(ActRelativeCitation(**before['citation']),before)
    policy.append({'query':before['citation'],'before':before,'after':after})
with args.output.open('x') as f:
    json.dump({'provider_calls':0,'diagnostic_cases':diagnostics,'policy_cases':policy},f,indent=2);f.write('\n')
changed=[c for c in diagnostics if old_fields(c['before'])!=old_fields(c['after'])]
lost=[c for c in changed if c['before']['iri'] and c['before']['iri'] not in
      [c['after']['iri'],*[r['iri'] for r in c['after']['candidate_resolutions']]]]
print('diagnostic checked',len(diagnostics),'changed',len(changed),'old selected targets absent even from candidates',len(lost))
for c in lost[:5]:print(c['query'],c['before']['iri'])
policy_changed=[c for c in policy if old_fields(c['before'])!=old_fields(c['after'])]
print('prior policy checked',len(policy),'changed only for competing name identities',len(policy_changed))
