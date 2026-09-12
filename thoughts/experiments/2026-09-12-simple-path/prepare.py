"""Acquire three frozen inputs through existing readers, without model calls."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from docspec.processing.visible_text import HtmlVisibleTextExtractor, XmlVisibleTextExtractor
from rulespec_extrapolator import documents, extraction as e
from rulespec_extrapolator.uslm import prepare_xml

HERE = Path(__file__).resolve().parent


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')


def visible(name, raw, reader):
    result = reader.extract(raw)
    data = asdict(result)
    data['content'] = result.content.decode()
    save(f'sources/{name}.acquisition.json', data)
    return data['content']


def main():
    (HERE / 'sources').mkdir(exist_ok=False)
    records = []
    for name in ('manual', 'annual'):
        raw = Path('/tmp/rulespec-simple-' + name).read_bytes()
        suffix = 'html' if name == 'manual' else 'xml'
        (HERE / f'sources/{name}.raw.{suffix}').write_bytes(raw)
        if name == 'manual':
            utf8 = raw.decode('cp1252').encode()
            (HERE / 'sources/manual.utf8.html').write_bytes(utf8)
            text = visible(name, utf8, HtmlVisibleTextExtractor())
            start = re.search(r'7 FAM 1453\s+ROLE OF CONSULAR OFFICER', text).start()
            end = re.search(r'7 FAM 1454\s+INFORMATION ON MARRIAGE ABROAD', text).start()
            selected = text[start:end]
            title, url = '7 FAM 1453 — Role of consular officer', 'https://fam.state.gov/FAM/07FAM/07FAM1450.html'
        else:
            text = visible(name, raw, XmlVisibleTextExtractor())
            start, end, selected = 0, len(text), text
            title, url = '40 CFR 262.15 — 2025 annual edition', 'https://www.govinfo.gov/content/pkg/CFR-2025-title40-vol28/xml/CFR-2025-title40-vol28-sec262-15.xml'
            paragraphs = [''.join(n.itertext()) for n in ET.fromstring(raw).findall('.//SECTION/P')]
            normalize = lambda s: ' '.join(s.split())
            assert all(normalize(p) in normalize(text) for p in paragraphs)
            save('annual-paragraph-check.json', {'retained': len(paragraphs), 'total': len(paragraphs), 'comparison': 'whitespace-normalized paragraph inclusion'})
        (HERE / f'sources/{name}.txt').write_text(selected)
        doc = documents.prepare_document(selected, title=title, source_url=url)
        save(f'sources/{name}.document.json', doc)
        records.append(dict(id=name, url=url, raw_sha256=sha256(raw).hexdigest(),
                            selected_rendition_span=[start, end], chars=len(selected),
                            windows=len(e.plan_windows(doc)), native_xml=False))

    archive = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
    with ZipFile(archive) as zipped:
        raw = zipped.read('usc05.xml')
    original = ET.fromstring(raw)
    selected = [n for n in original.iter() if n.get('identifier') == '/us/usc/t5/s6323']
    assert len(selected) == 1
    root = ET.Element(original.tag, original.attrib)
    root.append(selected[0])
    xml = ET.tostring(root, encoding='unicode')
    (HERE / 'sources/uslm.xml').write_text(xml)
    doc = prepare_xml(xml, title='5 USC 6323 — release 119-102',
                      source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
    save('sources/uslm.document.json', doc)
    (HERE / 'sources/uslm.txt').write_text(doc['text'])
    records.append(dict(id='uslm', archive=str(archive), archive_sha256=sha256(archive.read_bytes()).hexdigest(),
                        member='usc05.xml', member_sha256=sha256(raw).hexdigest(),
                        selection='/us/usc/t5/s6323', serialization='ElementTree subtree inside uscDoc',
                        chars=len(doc['text']), windows=len(e.plan_windows(doc)), native_xml=True))
    save('source-receipts.json', records)
    assert sum(r['windows'] for r in records) <= 6
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
