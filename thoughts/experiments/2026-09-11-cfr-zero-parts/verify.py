"""Installed bytes and reference-output checks for the isolated minter fix."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import sysconfig
import zipfile

from refspec.registry import iri_minting
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
mode = sys.argv[1]
assert mode in {'isolated', 'working'}
assert Path(sys.prefix) in Path(iri_minting.__file__).parents
site = Path(sysconfig.get_paths()['purelib'])
verified = 0
for item in json.loads((HERE/'wheel-inputs.json').read_text()):
    wheel = Path(item['path'])
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == item['sha256']
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.endswith('.py') and '.dist-info/' not in name:
                assert (site/name).read_bytes() == archive.read(name), name
                if name.startswith('refspec/'):
                    assert (HERE.parents[3]/'RefSpec/src'/name).read_bytes() == archive.read(name), name
                verified += 1
before = json.loads((HERE/'baseline-references.json').read_text())
after = scan_references(prepare_document('16 CFR 0.1; 41 CFR 101-1; 3 CFR 127 (1981 Comp.); RIN 2060-AS32.'))
with (HERE/f'references-{mode}.json').open('x') as f:
    json.dump(after, f, ensure_ascii=False, indent=2)
    f.write('\n')
old_parsers, new_parsers = before.pop('parsers'), after.pop('parsers')
assert before == after
changed = [a['name'] for a, b in zip(old_parsers, new_parsers, strict=True) if a != b]
assert changed == ['refspec.registry.iri_minting.mint_rin_iri']
for a, b in zip(old_parsers, new_parsers, strict=True):
    assert {k: v for k, v in a.items() if k != 'module_sha256'} == {k: v for k, v in b.items() if k != 'module_sha256'}
mints = []
for case in json.loads((HERE/'source-cases.json').read_text())['cases']:
    value = iri_minting.mint_cfr_iri(case['title'], 0)
    assert value.iri == f"urn:rkaf:us:cfr:{case['title']}:0"
    mints.append(asdict(value))
result = {'python': sys.executable, 'status': 'passed', 'verified_wheel_python_files': verified,
          'reference_candidate_data_unchanged': True, 'changed_parser_provenance': changed,
          'source_mints': mints, 'model_calls': 0}
with (HERE/f'verified-{mode}.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(mode, 'passed;', verified, 'installed files verified; reference data unchanged')
