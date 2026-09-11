"""Select source cases and capture the unchanged passage reader once."""
import hashlib
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from rulespec_extrapolator.documents import prepare_document, source_passages

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORPUS = ROOT.parent / 'RefSpec/output/ecfr-title-xml-2026-08-24'


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


cases = []
prior = json.loads((HERE.parent / '2026-09-10-design-context/cases.json').read_text())
for row in prior[:2]:
    cases.append({'id': row['id'], 'origin': 'saved development source',
                  'document': row['document']})

manifest = json.loads((CORPUS / 'manifest.json').read_text())
previous = json.loads((HERE.parent / '2026-09-11-cfr-subparts/cases.json').read_text())
used = {(x.get('title'), x.get('section')) for x in previous}
for title in (21, 49):
    source = next(x for x in manifest['titles'] if x['title'] == title)
    path = CORPUS / source['path']
    raw = path.read_bytes()
    assert sha(raw) == source['sha256']
    selected = None
    for _, section in ET.iterparse(path, events=('end',)):
        if section.get('TYPE') != 'SECTION':
            continue
        number = section.get('N')
        paragraphs = [''.join(p.itertext()) for p in section.findall('P')]
        eligible = (8 <= len(paragraphs) <= 35
                    and (title, number) not in used
                    and any(re.match(r'\s*\([a-z]\)', p) for p in paragraphs)
                    and any(re.match(r'\s*(?:\([A-Z]\)|\([a-z]\)\s*\(\d+\))', p)
                            for p in paragraphs))
        if eligible:
            selected = (number, section.findtext('HEAD'), paragraphs)
            break
        section.clear()
    assert selected, f'No section satisfying registered selection for title {title}'
    number, heading, paragraphs = selected
    matches = list(re.finditer(rb'<DIV8\b[^>]*\bN="' + re.escape(number.encode()) + rb'"[^>]*>', raw))
    assert len(matches) == 1, (title, number, len(matches))
    start = matches[0].start()
    end = raw.index(b'</DIV8>', start) + len(b'</DIV8>')
    name = f'title-{title}-section-{number}.xml'
    with (HERE / name).open('xb') as stream:
        stream.write(raw[start:end])
    text = heading + '\n\n' + '\n\n'.join(paragraphs)
    case = {'id': f'ecfr-{title}-{number}', 'origin': 'new source selection',
            'source': source, 'xml_capture': name, 'xml_start': start, 'xml_end': end,
            'xml_sha256': sha(raw[start:end]),
            'preparation': 'HEAD and direct P itertext, joined by two newlines; not XML character offsets',
            'document': prepare_document(text, title=f'{title} CFR {number}')}
    cases.append(case)

controls = {
    'dotted-passport': 'a. Provide one or more documents:\n(1) Court records:\n(a) Name order.\n(b) Divorce decree.\nb. Different case.',
    'combined': '(b) First.\n(4) Older child.\n(c)(1) New child.\n(i) First item.\n(ii) Second item.\n(2) Next child.\n(d) Last.',
    'top-i': '(h) First rule.\n(1) Child.\n(i) Next rule.\n(1) Its child.',
    'duplicate': '(a) First label.\n(1) First child.\n(a) Repeated label.\n(1) Repeated child.',
    'missing-parent': '(B) A fragment with no parents.\n(4) A child of that fragment.',
    'roman-ambiguity': '(g) Earlier rule.\n(1) Its child.\n(i) Another item; level not stated.',
    'spaced-path': '(a) Top.\n(3) Child.\n(iii) Roman.\n(B) Upper.\n( 4 ) Spaced number.',
    'explicit-path': '(a)(3)(iii)(B)( 4 ) An explicit full address.',
}
for name, text in controls.items():
    cases.append({'id': name, 'origin': 'constructed control', 'document': prepare_document(text)})
text = '(a) First section.\n(1) First child.\n(a) Next section.\n(1) Next child.'
boundary = text.index('(a) Next')
for name, sections in (
    ('section-reset', [{'id': 'one', 'label': 'One', 'start': 0, 'end': boundary},
                       {'id': 'two', 'label': 'Two', 'start': boundary, 'end': len(text)}]),
    ('overlapping-sections', [{'id': 'outer', 'label': 'Outer', 'start': 0, 'end': len(text)},
                             {'id': 'inner', 'label': 'Inner', 'start': boundary, 'end': len(text)}]),
):
    cases.append({'id': name, 'origin': 'constructed control',
                  'document': prepare_document(text, sections=sections)})
text = 'First section ends here.Second section begins here.'
boundary = text.index('Second')
cases.append({'id': 'boundary-without-whitespace', 'origin': 'constructed control',
              'document': prepare_document(text, sections=[
                  {'id': 'one', 'label': 'One', 'start': 0, 'end': boundary},
                  {'id': 'two', 'label': 'Two', 'start': boundary, 'end': len(text)}])})
write('cases.json', cases)
write('baseline.json', [{'id': x['id'], 'passages': source_passages(x['document'])} for x in cases])
source_code = ROOT / 'packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py'
with (HERE / 'baseline-documents.py').open('xb') as stream:
    stream.write(source_code.read_bytes())
write('freeze.json', {'files': {p.name: sha(p.read_bytes()) for p in HERE.iterdir() if p.is_file()}})
for case in cases[:4]:
    print(case['id'], len(case['document']['text']), case['document']['title'])
    for i, p in enumerate(source_passages(case['document'])):
        text = case['document']['text'][p['start']:p['end']].strip()
        print(f'  {i}: {text[:120]}')
