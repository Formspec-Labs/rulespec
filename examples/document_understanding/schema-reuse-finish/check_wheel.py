"""Verify installed wheels outside the checkout, without Go or CUE."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
from rulespec_extrapolator import core, extraction, schemas
from rulespec_conformance.contract import resources

assert shutil.which('go') is None and shutil.which('cue') is None
assert 'site-packages' in core.__file__
assert 'site-packages' in str(resources.DATA_ROOT)
assert not (Path(core.__file__).parent / '_data/compiled').exists()
inputs = Path(sys.argv[1])
b = core.compile_candidates(json.loads((inputs/'control-document.json').read_text()),
                            [json.loads((inputs/'control-candidate.json').read_text())], {'id':'urn:test:wheel'})
assert not b['rejected']
result = core.validate_graph(b['graph'])
assert any(n['@type'] == 'rkaf:ReferenceResourceRelease' for n in b['graph']['@graph'])
with tempfile.TemporaryDirectory() as tmp:
    fp = extraction._freeze(Path(tmp), extraction.invented_examples(), schemas.load_schema('provider'))
    assert all((Path(tmp)/'frozen/sources'/name).is_file() for name in schemas.runtime_sources())
print(json.dumps({'status':'passed', 'go_or_cue_required':False, 'core_data':str(resources.DATA_ROOT),
                  'validation':result, 'freeze':'passed', 'provider_calls':0}, indent=2))
