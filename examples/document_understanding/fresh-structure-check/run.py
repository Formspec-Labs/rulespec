"""Reuse the frozen fixed-enrichment experiment on new official source bundles."""
import argparse
import importlib.util
from pathlib import Path
import random
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
HELPER = ROOT.parent / 'fixed-enrichment-check/run.py'
spec = importlib.util.spec_from_file_location('fixed_trial', HELPER)
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
f.ROOT = ROOT
e = f.e


def prepare():
    assert not (ROOT / 'design.json').exists()
    shutil.copytree(HELPER.parent / 'schemas', ROOT / 'schemas')
    docs = {}
    for case in ['electronic', 'aviation']:
        text = (ROOT / 'sources' / (case + '.txt')).read_text()
        docs[case] = f.prepare_document(text, title='Official eCFR selected sections: ' + case,
            source_url='https://www.ecfr.gov/')
        e._save(ROOT / 'sources' / (case + '.json'), docs[case])
    rng = random.Random(202609099)
    cells = [(case, arm) for case in docs for arm in ['baseline', 'index']]
    rng.shuffle(cells)
    later = [(case, 'fixed') for case in docs]; rng.shuffle(later)
    names = [f'X{i:02}' for i in range(1, 7)]; rng.shuffle(names)
    trials = {}
    for name, (case, arm) in zip(names, cells + later):
        window, = e.plan_windows(docs[case], max_chars=20000)
        trials[name] = {'case':case, 'arm':arm, 'window':window,
            'prompt_prefix':e._window_prompt(e._prompt_generator([], f.PROMPT if arm=='fixed' else e.PROMPT),docs[case],window)}
    inputs = [ROOT / n for n in ['PLAN.md','REVIEW.md','run.py']]
    inputs += list((ROOT/'sources').glob('*')) + list((ROOT/'schemas').glob('*'))
    e._save(ROOT/'design.json', {'trials':trials,'max_calls':6,'model':e.DEFAULT_MODEL,
        'temperature':0,'thinking_level':'low','max_output_tokens':16384,
        'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'fixed_helper_sha256':e._digest(HELPER.read_bytes()),
        'helper_sha256':e._digest((f.PRIOR/'run.py').read_bytes()),'runtime_sha256':f.h.fingerprint(),
        'inputs_sha256':{str(p.relative_to(ROOT)):e._digest(p.read_bytes()) for p in inputs}})
    print('Prepared six new-source calls with unchanged experiment schemas and prompts.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['prepare','run','replay']);parser.add_argument('--env-file',type=Path)
    args=parser.parse_args()
    if args.mode=='prepare':prepare()
    else:
        assert e._load(ROOT/'design.json')['fixed_helper_sha256']==e._digest(HELPER.read_bytes())
        f.execute(args.mode,args.env_file)
