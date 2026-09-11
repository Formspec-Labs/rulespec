"""Freeze bounded publisher paragraphs; selection does not call either parser."""
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORPUS = ROOT.parent / 'RefSpec/output/ecfr-title-xml-2026-08-24'
manifest = json.loads((CORPUS / 'manifest.json').read_text())
selected = []
needle = re.compile(r'\b\d+\s+CFR\b[^.;\n]{0,60}\bsubparts?\b', re.I)
for title in (21, 40, 49):
    source = next(x for x in manifest['titles'] if x['title'] == title)
    path = CORPUS / source['path']
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == source['sha256']
    seen = set()
    for _, section in ET.iterparse(path, events=('end',)):
        if section.get('TYPE') != 'SECTION':
            continue
        for p in section.iter('P'):
            text = ''.join(p.itertext())
            if not needle.search(text) or text in seen:
                continue
            seen.add(text)
            number = section.get('N')
            start = re.search(rb'<DIV8\b[^>]*\bN="' + re.escape(number.encode()) + rb'"[^>]*>', raw).start()
            end = raw.index(b'</DIV8>', start) + len(b'</DIV8>')
            relative = f'title-{title}-section-{number}.xml'
            capture = HERE / relative
            if not capture.exists():
                capture.write_bytes(raw[start:end])
            selected.append({'id': f'ecfr-{title}-{len(seen)}', 'raw': text,
                             'title': title, 'section': number,
                             'heading': section.findtext('HEAD'), 'section_capture': relative,
                             'xml_start': start, 'xml_end': end, 'source': source})
            if len(seen) == 2:
                break
        section.clear()
        if len(seen) == 2:
            break
    assert len(seen) == 2, (title, len(seen))
ohio = next(x for x in json.loads((HERE.parent / '2026-09-10-reference-real-positives/cases.json').read_text())
            if x['id'] == 'source-3')
selected.insert(0, {'id': 'ohio', 'raw': ohio['raw'], 'source_url': ohio['source_url'],
                    'source_sha256': ohio['text_sha256'], 'origin': 'saved development input'})
with (HERE / 'cases.json').open('x') as out:
    json.dump(selected, out, indent=2, ensure_ascii=False)
    out.write('\n')
for row in selected[1:]:
    print(row['id'], row['heading'], '\n', row['raw'])
