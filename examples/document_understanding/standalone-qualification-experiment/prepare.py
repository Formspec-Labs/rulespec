"""Freeze fixtures and compile the one-description intervention with native CUE."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import shutil
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
assert not (ROOT/'design.json').exists()
source=REPO/'packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data'
trial=ROOT/'cue-source'
trial.mkdir()
(trial/'cue.mod').mkdir()
shutil.copyfile(source/'cue.mod/module.cue',trial/'cue.mod/module.cue')
text=(source/'document-understanding.cue').read_text()
old=next(line for line in text.splitlines() if line.startswith('// Complete meaning of this unit,'))
new="// Complete meaning for a reader who receives only this statement. Before finalizing a split unit, check whether that reader could mistake a qualified duty or permission for an unconditional one. State its governing conditions and permitted departures here, even when another unit also describes them; retain their scope in scope_text and complete source support in the existing reference fields. A nearby statement or a long quote does not repair this statement. Distinct modal forces may remain separate, but each statement must preserve the limits that govern it. Do not turn an optional method into a waiver of the duty, or copy a different actor's or an independent neighboring rule's conditions. Preserve timing, negation, alternatives and the source's descriptive or advisory force."
assert text.count(old)==1
(trial/'document-understanding.cue').write_text(text.replace(old,new))
spec=importlib.util.spec_from_file_location('native_builder',REPO/'tools/build_extraction_schemas.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
builder.SOURCE=trial
for name,content in builder.generate().items():
    path=ROOT/'generated'/name;path.parent.mkdir(exist_ok=True);path.write_text(content)
baseline=e.load_schema('provider');treatment=e._load(ROOT/'generated/provider.schema.json')
path=('properties','extractions','items','properties','unit_attributes','properties','statement','description')
def get(obj):
    for key in path:obj=obj[key]
    return obj
copy=deepcopy(treatment);cursor=copy
for key in path[:-1]:cursor=cursor[key]
cursor[path[-1]]=get(baseline)
assert copy==baseline, 'Intervention changed more than statement.description'
assert get(treatment)!=get(baseline)
e._save(ROOT/'B-schema.json',baseline);e._save(ROOT/'T-schema.json',treatment)
e._save(ROOT/'schema-change.json',{'field':'.'.join(path),'baseline':get(baseline),'treatment':get(treatment),
    'native_generation':True,'other_provider_fields_identical':True})
paths={'passport':ROOT.parent/'passage-id-transfer/passport/document.json',
       'notice':ROOT.parent/'minor-audit-improvements/fresh/document.json',
       'waste':ROOT.parent/'passage-id-transfer/waste/document.json'}
fixtures={name:e._load(path) for name,path in paths.items()}
fixtures['controls']=prepare_document('Scenario 1: Different actors and independent actions.\n\nVisitors must file a notice on arrival. Staff may work remotely.\n\nScenario 2: Independent duty and optional method.\n\nStaff must sign each report. Staff may use a blue pen.\n\nScenario 3: Different seasonal branches.\n\nIn winter, visitors must carry a ski pass. In summer, visitors may rent a bicycle.',title='Constructed independent-rule counterexamples')
prompts={}
for case,doc in fixtures.items():
    e._save(ROOT/'fixtures'/(case+'.json'),doc)
    windows=e.plan_windows(doc,24000);assert len(windows)==1
    prompts[case]=e._window_prompt(e._prompt_generator(e.invented_examples()),doc,windows[0])
    if case!='controls':
        original=(ROOT.parent/'minor-audit-improvements/fresh/extraction' if case=='notice' else ROOT.parent/'passage-id-transfer'/case/'extraction')
        assert prompts[case]==e._load(original/'attempt-0000.request.json')['contents']
cases=list(fixtures)
cells=[case+'/'+arm for i,case in enumerate(cases) for arm in (('B','T') if i%2==0 else ('T','B'))]
inputs=['PLAN.md','prepare.py','run.py','B-schema.json','T-schema.json','schema-change.json',
        'cue-source/document-understanding.cue','cue-source/cue.mod/module.cue']
inputs += ['fixtures/'+case+'.json' for case in cases]
inputs += [str(p.relative_to(ROOT)) for p in (ROOT/'generated').glob('*')]
e._save(ROOT/'design.json',{'model':e.DEFAULT_MODEL,'temperature':0,'thinking_level':'low',
    'max_output_tokens':None,'max_provider_calls':8,'cases':cases,'cells':cells,'prompts':prompts,
    'runtime_sources_sha256':{n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()},
    'inputs_sha256':{name:e._digest((ROOT/name).read_bytes()) for name in inputs},
    'historical_prompts_identical':True,'baseline_commit':'b27a182'})
print('Native CUE intervention frozen: one provider description changed; eight calls maximum.')
