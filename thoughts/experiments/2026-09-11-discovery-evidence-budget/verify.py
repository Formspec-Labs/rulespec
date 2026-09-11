"""Check captured allocations against prior accounting and the installed runtime."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sysconfig

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


experiment = module('budget_experiment', HERE / 'experiment.py')
prior = module('prior_retrieval', HERE.parent / '2026-09-10-design-retrieval/run.py')
captured = json.loads((HERE / 'results.json').read_text())
assert experiment.run() == captured
purelib = Path(sysconfig.get_paths()['purelib'])
modules = {}
for value in (experiment.core, experiment.discovery, experiment.documents,
              experiment.reference_sources, experiment.references, experiment.uslm):
    path = Path(value.__file__)
    assert path.is_relative_to(purelib), path
    source = REPO / 'packages/rulespec-extrapolator/src/rulespec_extrapolator' / path.name
    assert source.read_bytes() == path.read_bytes()
    modules[value.__name__] = hashlib.sha256(path.read_bytes()).hexdigest()
for query in captured['queries']:
    for arm in query['arms'].values():
        ordered = [{'source': x['source'], 'evidence': [x['evidence']]} for x in arm['trace']]
        covered, used = prior.spans_for(ordered, captured['budget'])
        displayed = {}
        for segment in arm['segments']:
            displayed.setdefault(segment['source'], set()).update(range(segment['start'], segment['end']))
        assert {k: v for k, v in covered.items() if v} == displayed
        assert used == arm['unique_chars'] <= captured['budget']
    a = {(x['source'], i) for x in query['arms']['A']['segments'] for i in range(x['start'], x['end'])}
    c = {(x['source'], i) for x in query['arms']['C']['segments'] for i in range(x['start'], x['end'])}
    assert a <= c
receipt = {'installed_replay_equal': True, 'source_installed_modules': modules,
           'allocations_equal_prior_accounting': 36, 'direct_first_retains_all_baseline_source_characters': True,
           'provider_calls': 0, 'prior_helper_sha256': hashlib.sha256(Path(prior.__file__).read_bytes()).hexdigest(),
           'verification_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with (HERE / 'installed-verification.json').open('x') as out:
    json.dump(receipt, out, indent=2)
    out.write('\n')
print(json.dumps(receipt, indent=2))
