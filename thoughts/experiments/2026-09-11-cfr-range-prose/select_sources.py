"""Pin the first eligible publisher paragraphs; selection is not a quality label."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree as etree
from refspec.registry.citation_grammar import find_cfr_citations

HERE = Path(__file__).resolve().parent
SOURCE = Path('/Users/mikewolfd/Work/RefSpec/output/ecfr-title-xml-2026-08-24')
manifest = json.loads((SOURCE / 'manifest.json').read_text())
selected, pins = [], []
for title in (21, 41, 49):
    pin = next(x for x in manifest['titles'] if x['title'] == title)
    raw = (SOURCE / pin['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin['sha256']
    pins.append(pin)
    for match in re.finditer(rb'<P\b[^>]*>.*?</P>', raw, re.DOTALL):
        xml = match.group().decode('utf-8')
        if not re.search(r'\bC\.?\s*F\.?\s*R\.?', xml):
            continue
        text = ''.join(etree.fromstring(match.group()).itertext())
        rows = find_cfr_citations(text)
        if not any(r.refusal == 'range_end_unread' and re.search(r'\b(?:to|through)\s+[A-Za-z]', r.text) for r in rows):
            continue
        selected.append({'id': f'publisher-{len(selected)+1}', 'title': title,
                         'source': pin['path'], 'start_byte': match.start(), 'end_byte': match.end(),
                         'xml': xml, 'raw_context': raw[max(0,match.start()-180):match.end()+180].decode('utf-8',errors='replace'),
                         'text': text, 'baseline': [asdict(r) for r in rows]})
        if len(selected) == 8:
            break
    if len(selected) == 8:
        break
with (HERE / 'publisher-selection.json').open('x') as stream:
    json.dump({'pins': pins, 'cases': selected}, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
for row in selected:
    print(json.dumps({'id':row['id'],'title':row['title'],'text':row['text'],'matches':row['baseline']},ensure_ascii=False))
