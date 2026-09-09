"""Correct one scoped control's hand-selected passage; no model calls."""
import argparse
import importlib.util
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('passage_trial', ROOT / 'experiment.py')
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode', choices=('run', 'replay'))
args = parser.parse_args()
load = trial.e._load
case = deepcopy(next(c for c in load(ROOT / 'cases.json') if c['name'] == 'long_quote_inserted_negation'))
case['selected_refs'] = ['F002']

def inputs(path):
    return [case] if path == ROOT / 'cases.json' else load(path)

with patch.object(trial.e, '_load', inputs), patch.object(trial.lib.resolver.Resolver, 'align', trial.exact_align):
    result = {'reason': 'The original scoped control defaulted to F000, the heading. Select F002 containing the actual unmodified notice alternatives so refusal tests the negation change, not unrelated evidence.',
              'case': case, 'result': trial.stage1()[0]}
path = ROOT / 'stage1-supplement.json'
if args.mode == 'run':
    assert not path.exists()
    trial.e._save(path, result)
else:
    assert result == load(path)
print(result['result']['whole']['accepted'], result['result']['scoped']['accepted'])
