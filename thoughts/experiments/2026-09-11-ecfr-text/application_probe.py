"""Replay one actual eCFR section against a pinned native full-title source."""
import hashlib
import json
from pathlib import Path
import re
import sys
import sysconfig
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from refspec.input_pin import read_verified_file_pin
from rulespec_extrapolator import cli
from rulespec_extrapolator.documents import load_document
from rulespec_extrapolator.core import compile_candidates

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODE = sys.argv[1]
OUT = HERE / MODE
OUT.mkdir()
INPUT = HERE.parent / '2026-09-11-reference-bodies/catalog-probe'
PREPARED = HERE / 'prepared-primary.json'
RAW_PRIMARY = INPUT / 'rail-definition-0.xml'
TITLE = Path('/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/refspec-output/ecfr-title-xml-2026-08-24/title-49.xml')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


if MODE != 'baseline':
    pins = json.loads((INPUT/'results.json').read_text())
    primary_pin = pins['references'][0]['section_matches'][0]
    assert sha(RAW_PRIMARY.read_bytes()) == primary_pin['raw_sha256']
    title_pin = next(p['receipt'] for p in pins['publisher_titles'] if p['receipt']['title'] == 49)
    data = read_verified_file_pin(TITLE, expected_sha256='sha256:'+title_pin['sha256'], expected_byte_length=title_pin['bytes'])
    del data
    document = load_document(RAW_PRIMARY)
    if MODE == 'source':
        with PREPARED.open('x') as stream:
            json.dump(document, stream, ensure_ascii=False)
    else:
        assert document == json.loads(PREPARED.read_text())

if MODE in {'isolated', 'working'}:
    site = Path(sysconfig.get_paths()['purelib'])
    from refspec.registry import ecfr
    assert Path(cli.__file__).is_relative_to(site)
    assert Path(ecfr.__file__).is_relative_to(site)
    verified = 0
    for pin in json.loads((HERE/'wheel-inputs.json').read_text()):
        wheel = Path(pin['path'])
        assert sha(wheel.read_bytes()) == pin['sha256']
        with ZipFile(wheel) as archive:
            for name in archive.namelist():
                if name.endswith('.py') and '.dist-info/' not in name:
                    assert (site/name).read_bytes() == archive.read(name), name
                    verified += 1
    (OUT/'wheel-verification.json').write_text(json.dumps({'verified_python_files': verified})+'\n')

# The baseline scans exactly the same prepared input; its installed XML loader
# predates eCFR support. Production source loading is checked above in other arms.
args = ['references', str(PREPARED), '--output', str(OUT/'references.json')]
if MODE != 'baseline':
    args += ['--reference-source', str(TITLE)]
cli.main(args)
scan = json.loads((OUT/'references.json').read_text())
summary = {'mode': MODE, 'primary_sha256': sha(RAW_PRIMARY.read_bytes()), 'model_calls': 0,
           'located': [r['value'] for r in scan['candidates'] if r.get('resolution', {}).get('status') == 'located'],
           'references_json_bytes': (OUT/'references.json').stat().st_size}
if MODE != 'baseline':
    assert summary['located'] and any(t['value'] == '49 CFR 392.9a' for t in scan['targets'].values())
    source, = scan['reference_sources'].values()
    assert source['publisher_source']['rkaf:hasContentDigest'] == 'sha256:'+title_pin['sha256']
    assert len(source['records']) == len(scan['targets'])
    root = ET.parse(TITLE).getroot()
    for fragment in source['xml_fragments'].values():
        node = root
        path = fragment['oa:hasSelector'][0]['rdf:value']
        for step in path.split('/')[2:]:
            node = node[int(re.fullmatch(r'\*\[(\d+)\]', step)[1])-1]
        assert fragment['rkaf:fragmentContentDigest'] == 'sha256:'+sha(''.join(node.itertext()).encode())
    summary.update(title_sha256=title_pin['sha256'], targets=len(scan['targets']),
                   records=len(source['records']), unresolved_native_sections=len(source.get('issues', [])),
                   xml_fragments_verified=len(source['xml_fragments']))
    # A constructed empty run exercises the normal export CLI on actual input;
    # it is not a model extraction result or evidence of extraction quality.
    run = OUT/'run'
    run.mkdir()
    book = compile_candidates(document, [], {})
    for name, value in {'document.json':document, 'run.json':{}, 'rulebook.json':book,
                        'candidates.json':[], 'graph.jsonld':book['graph']}.items():
        (run/name).write_text(json.dumps(value, ensure_ascii=False))
    cli.main(['discovery-export', str(run), '--reference-source', str(TITLE), '--output', str(OUT/'discovery.json')])
    exported = json.loads((OUT/'discovery.json').read_text())
    ext = exported['reference_scan']
    assert len(ext['targets']) == len(scan['targets'])
    for target in ext['targets'].values():
        own = ext['reference_sources'][target['source_id']]
        assert all(ref['id'] in own['evidence'] for ref in target['evidence_refs'])
    summary['discovery_json_bytes'] = (OUT/'discovery.json').stat().st_size
(OUT/'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False)+'\n')
print(json.dumps(summary, ensure_ascii=False))
