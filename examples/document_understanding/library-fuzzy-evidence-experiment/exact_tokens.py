"""Isolate LangExtract token-exact matching after the configured fuzzy trial."""
import argparse
import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('library_experiment', ROOT / 'experiment.py')
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('run', 'replay'))
    args = p.parse_args()
    e = trial.e
    design = e._load(ROOT / 'token-exact-design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    config = e._load(ROOT / 'configuration.json')[-1]
    align = trial.resolver.Resolver.align

    def exact(self, *args, **kwargs):
        kwargs['enable_fuzzy_alignment'] = False
        return align(self, *args, **kwargs)

    diagnostics = []
    with patch.object(trial.resolver.Resolver, 'align', exact), patch.object(
            trial.previous, 'tolerant_span', trial.make_resolver(config, diagnostics)):
        controls = trial.previous.controls(e._load(ROOT / 'cases.json'))
        audit = trial.previous.run_audit('treatment')
    baseline = e._load(ROOT / 'results.json')[-1]
    result = {'enable_fuzzy_alignment': False, 'accept_match_lesser': False,
              'controls': controls, 'audit': audit, 'diagnostics': diagnostics,
              'same_controls_as_strict': controls == baseline['controls'],
              'same_audit_as_strict': audit['judgments'] == baseline['audit']['judgments']
                  and audit['report'] == baseline['audit']['report']}
    target = ROOT / 'token-exact-result.json'
    if args.mode == 'run':
        assert not target.exists()
        e._save(target, result)
    else:
        assert result == e._load(target)
    print('Recovered:', len(audit['recoveries']), 'same controls:', result['same_controls_as_strict'],
          'same audit:', result['same_audit_as_strict'])


if __name__ == '__main__':
    main()
