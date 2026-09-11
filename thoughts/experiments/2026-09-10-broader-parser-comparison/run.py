"""Offline comparison; preserves every native output and failure, with one replay."""
from __future__ import annotations
import dataclasses
from collections.abc import Mapping
from datetime import datetime, timezone
from enum import Enum
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys

from refspec.registry import citation_grammar as ref, identifier_shapes as shapes
from spicysearch import cfr_citations as narrow, identifiers as query

root = Path(__file__).resolve().parent
projection_path = root.parents[2] / 'packages/rulespec-projection/src/rulespec_projection/citations.py'
spec = importlib.util.spec_from_file_location('projection_citations_source', projection_path)
projection = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = projection
spec.loader.exec_module(projection)


def serialize(value):
    if dataclasses.is_dataclass(value):
        return {f.name: serialize(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {k: serialize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [serialize(v) for v in value]
    return value


def compact(value):
    if isinstance(value,dict):
        return {k:compact(v) for k,v in value.items() if v is not None and v is not False and v != []}
    if isinstance(value,list):
        return [compact(v) for v in value]
    return value


def capture(functions, text):
    results = {}
    for name, function in functions:
        try:
            results[name] = {'output': serialize(function(text))}
        except Exception as error:
            results[name] = {'error': {'type':type(error).__name__, 'message':str(error)}}
    return results


frozen = json.loads(root.joinpath('cases.json').read_text())
names = frozenset(frozen['act_names'])
arms = {
 'A-current': [('find_cfr',ref.find_cfr_citations),
               ('strict_cfr',lambda t:narrow.extract_citations(t,strict=True,keep_rejected=True)),
               ('strict_usc',lambda t:narrow.extract_usc_citations(t,strict=True,keep_rejected=True))],
 'B-refspec': [('authorities',ref.parse_authority_citation),('identifiers',shapes.detect_identifier_shapes),
               ('fr_pages',ref.parse_federal_register_citations),('compilations',ref.parse_eo_compilation_locators),
               ('acts',lambda t:ref.find_act_relative_citations(t,act_names=names))],
 'C-spicysearch': [('identifiers',query.detect_identifiers)],
 'D-rulespec': [('cfr',projection.parse_cfr_citation),('authorities',projection.parse_authority_citation),
               ('acts',lambda t:projection.find_act_relative_citations(t,act_names=names))],
}
metadata = {'started':datetime.now(timezone.utc).isoformat(), 'load_start':os.getloadavg(),
            'python':sys.executable,'model':None,'temperature':None,'network_calls':0,
            'case_sha256':hashlib.sha256(root.joinpath('cases.json').read_bytes()).hexdigest(),
            'design_sha256':hashlib.sha256(root.joinpath('design.md').read_bytes()).hexdigest(),
            'modules':{},'repos':{}}
for module in (ref,shapes,narrow,query,projection):
    path = Path(module.__file__).resolve()
    metadata['modules'][module.__name__] = {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
for repo in ('rulespec','RefSpec','spicysearch'):
    path = Path('/Users/mikewolfd/Work') / repo
    metadata['repos'][repo] = {key:subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
                              for key,args in [('head',['rev-parse','HEAD']),('dirty',['status','--short'])]}
print(json.dumps(metadata['modules']),flush=True)
lock = root / 'run.lock'
with lock.open('x') as f:
    json.dump({'holder':'rulespec-broader-parsers','start':metadata['started'],
               'purpose':'offline diagnostic reference comparison','load':metadata['load_start']},f)
try:
    rows=[]
    for case in frozen['cases']:
        assert hashlib.sha256(case['raw'].encode()).hexdigest()==case['text_sha256']
        rows.append({'case':case,'arms':{name:capture(functions,case['raw']) for name,functions in arms.items()}})
    with root.joinpath('raw.json').open('x') as f:json.dump(rows,f,indent=2,ensure_ascii=False)
    replay=[]
    for case in frozen['cases']:
        replay.append({'case':case,'arms':{name:capture(functions,case['raw']) for name,functions in arms.items()}})
    with root.joinpath('replay.json').open('x') as f:json.dump(replay,f,indent=2,ensure_ascii=False)
    metadata['replay_equal'] = rows == replay
    rng=random.Random(39184)
    labels=list('WXYZ'); rng.shuffle(labels)
    arm_labels=dict(zip(arms,labels))
    root.joinpath('blind-key.json').write_text(json.dumps(arm_labels,indent=2)+'\n')
    review=[]
    for row in rows:
        review.append(f"\n{row['case']['id']} {row['case']['name']}: {row['case']['raw']}")
        review.append('Expected: '+json.dumps(row['case']['expected']))
        order=list(row['arms']);rng.shuffle(order)
        for name in order:
            outputs=list(row['arms'][name].values())
            review.append(arm_labels[name]+': '+json.dumps(compact(outputs),ensure_ascii=False))
    root.joinpath('blind-review.txt').write_text('\n'.join(review)+'\n')
finally:
    metadata.update(finished=datetime.now(timezone.utc).isoformat(),load_end=os.getloadavg())
    root.joinpath('run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    lock.unlink()
print(json.dumps({'completed':True,'replay_equal':metadata.get('replay_equal')}))
