"""Pin two complete native subsections; use ordinary extraction unchanged."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.uslm import prepare_xml

HERE = Path(__file__).resolve().parent
ARCHIVE = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
CASES = {'iep': '/us/usc/t20/s1414/d/1', 'lea': '/us/usc/t20/s6312/b'}


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def prepare():
    with ZipFile(ARCHIVE) as z:
        raw = z.read('usc20.xml')
    original = ET.fromstring(raw)
    receipt = {'archive': str(ARCHIVE), 'archive_sha256': sha256(ARCHIVE.read_bytes()).hexdigest(),
        'member': 'usc20.xml', 'member_sha256': sha256(raw).hexdigest(), 'source_version': '119-102',
        'limitation': 'Pinned historical release, not asserted latest law. Serialized complete subsections inside original uscDoc type; not original XML byte slices.', 'cases': {}}
    for name, identifier in CASES.items():
        matches = [n for n in original.iter() if n.get('identifier') == identifier]
        assert len(matches) == 1
        wrapper = ET.Element(original.tag, original.attrib)
        wrapper.append(matches[0])
        xml = ET.tostring(wrapper, encoding='unicode')
        document = prepare_xml(xml, title=identifier + ' — pinned release 119-102',
            source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
        save(f'sources/{name}.json', document)
        (HERE / f'sources/{name}.xml').write_text(xml)
        (HERE / f'sources/{name}.txt').write_text(document['text'])
        assert len(e.plan_windows(document)) == 1
        receipt['cases'][name] = {'identifier': identifier, 'serialized_sha256': sha256(xml.encode()).hexdigest(),
            'prepared_sha256': document['sha256'], 'chars': len(document['text'])}
    save('source-receipt.json', receipt)
    save('runtime.json', e._freeze(HERE, e.invented_examples(), e.provider_schema().schema_dict))
    pins = {str(p.relative_to(HERE)): sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file()}
    for name in ['decoded/plan.json', 'cells.json']:
        relative = '../2026-09-12-csbg-focus/' + name
        pins[relative] = sha256((HERE / relative).read_bytes()).hexdigest()
    save('pre-extraction-pins.json', pins)
    print(receipt['cases'])


def extract():
    for name, digest in e._load(HERE / 'pre-extraction-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == digest
    started = time.monotonic()
    for name in CASES:
        book = e.extract_run(e._load(HERE / f'sources/{name}.json'), HERE / 'extract' / name,
                             env_file=Path('/Users/mikewolfd/Work/spicy-regs/.env'))
        print(name, book['run']['status'], len(book['accepted']), len(book['rejected']), flush=True)
    save('extraction-time.json', {'seconds': time.monotonic() - started})
    save('extraction-usage.json', e.recorded_usage(HERE / 'extract'))


if __name__ == '__main__':
    {'prepare': prepare, 'extract': extract}[sys.argv[1]]()
