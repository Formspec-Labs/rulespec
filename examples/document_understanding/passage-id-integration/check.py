"""Verify integration against both saved passage-ID comparison responses."""
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent
EXPERIMENT = ROOT.parent / 'comparison-passage-ids'
config = e._load(EXPERIMENT / 'configuration.json')['P']
assert a.comparison_prompt() == config['prompt']
assert a.COMPARISON_SCHEMA == config['schema']
f = e._load(EXPERIMENT / 'fixture.json')
for cell in ('P1', 'P2'):
    directory = EXPERIMENT / 'runs' / cell
    attempts = e._load(directory / 'attempts.json')
    prompt = e._window_prompt(e._prompt_generator([], a.comparison_prompt()), f['book']['document'], f['window'])
    prompt += '\nDraft and inventory: ' + e._canonical(a._model_input(a._comparison_input(f['book'], f['labels'], f['window'])[0]))
    assert prompt == e._load(directory / attempts[0]['request_file'])['contents']
    judgments, issues = a._judgments(directory, f['book'], f['labels'], [f['window']], attempts, e.DEFAULT_MODEL)
    saved = e._load(directory / 'result.json')['workflows']['P-ID']
    assert judgments == saved['judgments'] and issues == saved['issues']
    assert a._assessment(f['book'], f['labels'], judgments, issues) == saved['report']
    print(cell, 'identical request and 36 judgments; no provider calls')
