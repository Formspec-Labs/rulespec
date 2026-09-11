"""Compare the installed baseline and supplied-source consumer on pinned actual text."""
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sys
import sysconfig
import time
from zipfile import ZipFile

from xml.etree import ElementTree as etree
from refspec.input_pin import read_verified_file_pin
from rulespec_extrapolator.documents import load_document
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.uslm import prepare_uslm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode = sys.argv[1]
out = HERE / mode
out.mkdir()
base = json.loads((HERE/'refspec-probe/results.json').read_text())
pos = json.loads((HERE/'refspec-probe/explicit-positive.json').read_text())
original = Path(pos['source_reference']['path'])
assert hashlib.sha256(original.read_bytes()).hexdigest() == pos['source_reference']['sha256']
doc = load_document(original)
kwargs = {}
xml = None
if mode not in {'source', 'baseline'}:
    verified_files = 0
    site = Path(sysconfig.get_paths()['purelib'])
    for pin in json.loads((HERE/'wheel-inputs.json').read_text()):
        wheel = Path(pin['path'])
        assert hashlib.sha256(wheel.read_bytes()).hexdigest() == pin['sha256']
        with ZipFile(wheel) as z:
            for name in z.namelist():
                if name.endswith('.py') and '.dist-info/' not in name:
                    assert (site/name).read_bytes() == z.read(name), name
                    if name.startswith('rulespec_extrapolator/'):
                        assert (ROOT/'packages/rulespec-extrapolator/src'/name).read_bytes() == z.read(name), name
                    verified_files += 1
    (out/'wheel-verification.json').write_text(json.dumps({'verified_python_files':verified_files})+'\n')
if mode != 'baseline':
    pin = base['source_archive']['pin']
    data = read_verified_file_pin(Path(base['source_archive']['path']),
        expected_sha256='sha256:'+pin['sha256'], expected_byte_length=int(pin['bytes']))
    with ZipFile(BytesIO(data)) as z:
        xml = z.read('usc05.xml')
    assert hashlib.sha256(xml).hexdigest() == pos['member']['sha256']
    then = time.monotonic()
    supplied = prepare_uslm(xml.decode('utf-8'), title='Title 5, Online@119-102', source_url=pin['url'])
    preparation_seconds = time.monotonic()-then
    kwargs['reference_sources'] = [supplied]
then = time.monotonic()
scan = scan_references(doc, **kwargs)
scan_seconds = time.monotonic()-then
then = time.monotonic()
exported = export_discovery({'document': doc, 'accepted': []}, include_references=True, **kwargs)
export_seconds = time.monotonic()-then
for name, value in [('references', scan), ('discovery', exported)]:
    (out/(name+'.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
rows = [r for r in scan['candidates'] if r['kind']=='usc' and r['reading'].get('usc_section')=='553' and r['reading'].get('pinpoint')==['b','B']]
assert len(rows) == 3
summary = {'mode':mode, 'primary_source':pos['source_reference'], 'explicit_occurrences':len(rows),
           'located_occurrences':sum(r.get('resolution',{}).get('status')=='located' for r in rows),
           'scan_seconds':scan_seconds, 'discovery_seconds':export_seconds,
           'reference_json_bytes':(out/'references.json').stat().st_size,
           'discovery_json_bytes':(out/'discovery.json').stat().st_size, 'model_calls':0}
if mode != 'baseline':
    assert summary['located_occurrences'] == 3
    target = scan['targets'][rows[0]['resolution']['target_ids'][0]]
    assert supplied['text'][target['start']:target['end']] == pos['body']
    assert rows[0]['resolution']['edition_match']=='not_established'
    source = scan['reference_sources'][target['source_id']]
    record = source['records'][target['record_id']]
    assert 'Except when notice or hearing is required by statute' in record['text']
    assert any(p['field']=='docPublicationName' and p['value']=='Online@119-102' for p in source['publication'])
    root = etree.fromstring(xml)
    for fragment in source['xml_fragments'].values():
        node = root
        for step in fragment['oa:hasSelector'][0]['rdf:value'].split('/')[2:]:
            node = node[int(step.removeprefix('*[').removesuffix(']'))-1]
        assert fragment['rkaf:fragmentContentDigest'] == 'sha256:'+hashlib.sha256(''.join(node.itertext()).encode()).hexdigest()
    assert len(source['records']) == 1
    assert len(record['text']) < len(supplied['text']) / 100
    summary.update(preparation_seconds=preparation_seconds, source_xml_sha256=pos['member']['sha256'],
                   target_characters=len(pos['body']), context_characters=len(record['text']),
                   shared_context_records=len(source['records']), xpath_fragments_verified=len(source['xml_fragments']))
    # Existing preparation and lookup keep a real publisher specimen as a small
    # regression fixture; wrapper is constructed, section bytes are unchanged.
    text = xml.decode('utf-8')
    at = text.index('identifier="/us/usc/t5/s553"')
    lo, hi = text.rfind('<section',0,at), text.index('</section>',at)+len('</section>')
    meta_lo, meta_hi = text.index('<meta>'), text.index('</meta>')+len('</meta>')
    selection = text[lo:hi]
    fixture = ROOT/'packages/rulespec-extrapolator/tests/fixtures/uslm/reference-title5-s553.xml'
    wrapper = '<uscDoc xmlns="http://xml.house.gov/schemas/uslm/1.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/">'+text[meta_lo:meta_hi]+'<main>'+selection+'</main></uscDoc>'
    if mode == 'source':
        fixture.write_text(wrapper)
    else:
        assert fixture.read_text() == wrapper
    summary['fixture_selection'] = {'member':pos['member'], 'decoded_xml_start':lo, 'decoded_xml_end':hi,
                                     'sha256':hashlib.sha256(selection.encode()).hexdigest(), 'wrapper':'constructed; original section and metadata unchanged'}
    baseline = json.loads((HERE/'baseline/references.json').read_text())
    # Lookup must retain every native reading, rejection, occurrence and quote.
    for group in ('candidates','rejected'):
        def originals(values):
            return [{k:v for k,v in r.items() if k!='resolution'} for r in values]
        assert originals(scan[group]) == originals(baseline[group])
    before = json.loads((HERE/'baseline/discovery.json').read_text())
    for key in ('document','records','statements','terms','accounting','evidence'):
        assert exported[key] == before[key], key
    if mode != 'source':
        for name in ('references', 'discovery'):
            assert json.loads((out/(name+'.json')).read_text()) == json.loads((HERE/'source'/(name+'.json')).read_text())
(out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
