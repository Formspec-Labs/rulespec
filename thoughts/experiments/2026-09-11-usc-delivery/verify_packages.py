"""Verify installed package bytes and the two intended captured source changes."""
import hashlib
import json
import os
from pathlib import Path
import sys
import sysconfig
from zipfile import ZipFile

from refspec.registry import citation_grammar
from rulespec_extrapolator import extraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SITE = Path(sysconfig.get_paths()['purelib']).resolve()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert Path(extraction.__file__).resolve().is_relative_to(SITE)
assert Path(citation_grammar.__file__).resolve().is_relative_to(SITE)
checked = {}
inputs = Path(os.environ.get('RULESPEC_USC_WHEELS', HERE / 'wheel-inputs.json'))
wheels = json.loads(inputs.read_text())
for item in wheels:
    wheel = Path(item['path'])
    assert sha(wheel) == item['sha256']
    with ZipFile(wheel) as archive:
        names = [n for n in archive.namelist() if not n.endswith('/') and '.dist-info/' not in n and '.data/' not in n]
        for name in names:
            expected = hashlib.sha256(archive.read(name)).hexdigest()
            assert sha(SITE / name) == expected, name
            if name.startswith('rulespec_extrapolator/'):
                source = (ROOT / name.rsplit('/', 1)[-1] if name.startswith('rulespec_extrapolator/_data/')
                          else ROOT / 'packages/rulespec-extrapolator/src' / name)
                assert sha(source) == expected, name
            elif name.startswith('refspec/'):
                assert sha(ROOT.parent / 'RefSpec/src' / name) == expected, name
        checked[wheel.name] = len(names)

before = json.loads((HERE / 'baseline-runtime.json').read_text())
current = {name: sha(path) for name, path in extraction._runtime_sources().items()}
assert set(current) == set(before['source_hashes'])
changed = sorted(name for name in current if current[name] != before['source_hashes'][name])
assert changed == ['application/references.py', 'refspec/registry/citation_grammar.py'], changed
result = {'status': 'passed', 'site': str(SITE), 'package_file_counts': checked,
          'wheel_inputs': str(inputs), 'wheel_inputs_sha256': sha(inputs), 'wheels': wheels,
          'source_changes': changed, 'source_hashes': current,
          'runtime': extraction._runtime_versions()}
with (HERE / sys.argv[1]).open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'status': 'passed', 'package_file_counts': checked, 'source_changes': changed}))
