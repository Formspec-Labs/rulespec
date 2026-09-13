"""Fresh inputs and fixed positive policy, reusing the earlier bounded runner."""
import importlib.util
from pathlib import Path
import sys
from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / '2026-09-13-fresh-complete-reading'
spec = importlib.util.spec_from_file_location('fresh_runner', PREVIOUS / 'run.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
x.HERE = HERE
x.NAMES = ['leave', 'billing', 'hazard', 'debt', 'offset', 'workplace', 'jury_fee', 'religious']


def extract():
    if not (HERE / 'source-pins.json').exists():
        x.save('runtime.json', e._runtime_versions())
        paths = [p for p in HERE.rglob('*') if p.is_file()] + list(e._runtime_sources().values())
        paths += [PREVIOUS / 'run.py', x.OLD / 'run.py', x.OLD / 'TASK.txt',
                  HERE.parent / '2026-09-13-checker-instruction-isolation/instructions.json']
        x.freeze('source-pins.json', paths)
    x.extract()


if __name__ == '__main__':
    {'extract': extract, 'check': x.check}[sys.argv[1]]()
