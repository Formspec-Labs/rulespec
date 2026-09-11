"""Verify the existing calendar consumer against the preserved law alternatives."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
WORK=HERE.parents[3]
sys.path.insert(0,str(WORK/'RefSpec/tests'))
from refspec.registry.act_resolution import ActIndex, _PUBLIC_LAW_KEY
from refspec.registry.unified_agenda_parquet import (
    _act_enactment_years, _pl_roster, _act_name_spelling_closure,
    _act_name_resolver, resolvable_act_names,
)
from act_name_multiplicity_oracle import ActIndex as PriorIndex
from act_enactment_year_oracle import _act_enactment_years as prior_years

artifact=WORK/'RefSpec/output/usc-act-index-2026-08-22'
index=ActIndex.from_artifact(artifact)
previous=PriorIndex.from_artifact(artifact)
roster=_pl_roster()
before=prior_years(previous,roster)
after=_act_enactment_years(index,roster)
changes={}
for name in sorted(before.keys()|after.keys()):
    if before.get(name)==after.get(name): continue
    laws={r.table3_key for r in index.name_candidates[name]}
    changes[name]={'before':before.get(name),'after':after.get(name),
                   'source_laws':{law:roster[0].get(tuple(map(int,law.split('-')))) if _PUBLIC_LAW_KEY.fullmatch(law) else law for law in sorted(laws)}}
names=resolvable_act_names(artifact)
base=_act_name_spelling_closure(names,_act_name_resolver(index))
expanded=_act_name_spelling_closure(names,_act_name_resolver(index),after)
assert all(expanded.get(k)==v for k,v in base.items())
result={'before_years':len(before),'after_years':len(after),
        'new_spelling_variants':len(expanded.keys()-base.keys()),'changes':changes}
with (HERE/'enactment-years.json').open('x') as f:
    json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
