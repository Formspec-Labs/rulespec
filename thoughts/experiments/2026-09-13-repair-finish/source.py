"""Freeze four unseen excerpts and run ordinary extraction once per source."""
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.uslm import prepare_xml

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent / '2026-09-13-fresh-complete-reading/run.py'
spec = importlib.util.spec_from_file_location('capture_helpers', HELPER)
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
x.HERE = HERE
CASES = dict(foia='/us/usc/t5/s552/a/6/A', denial='/us/usc/t5/s555/e',
             benefits='/us/usc/t29/s1025/a', accommodation='/us/usc/t42/s12112/b/5')
x.NAMES = list(CASES)


def prepare():
    archive = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
    receipts = []
    with ZipFile(archive) as zipped:
        for name, address in CASES.items():
            title = int(address.split('/')[3][1:])
            member = f'usc{title:02d}.xml'
            raw = zipped.read(member)
            root = ET.fromstring(raw)
            node, = [n for n in root.iter() if n.get('identifier') == address]
            wrapper = ET.Element(root.tag, root.attrib)
            wrapper.append(node)
            xml = ET.tostring(wrapper, encoding='unicode')
            doc = prepare_xml(xml, title=f'{name}: {address}, archived release 119-102',
                source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
            assert len(e.plan_windows(doc)) == 1
            x.save(f'sources/{name}.json', doc)
            x.save(f'sources/{name}.xml.json', dict(xml=xml))
            receipts.append(dict(name=name, native_excerpt=address, member=member,
                member_sha256=sha256(raw).hexdigest(), serialized_sha256=sha256(xml.encode()).hexdigest(),
                characters=len(doc['text']), serialization='Complete native subtree in original uscDoc wrapper'))
    x.save('source-receipt.json', dict(archive=str(archive), archive_sha256=sha256(archive.read_bytes()).hexdigest(),
        release='119-102', cases=receipts))
    x.save('runtime.json', e._runtime_versions())
    x.freeze('source-pins.json', [p for p in HERE.rglob('*') if p.is_file()] +
        list(e._runtime_sources().values()) + [HELPER, x.OLD / 'run.py'])
    print('Four complete excerpts frozen; one ordinary extraction window each.')


if __name__ == '__main__':
    {'prepare': prepare, 'extract': x.extract}[sys.argv[1]]()
