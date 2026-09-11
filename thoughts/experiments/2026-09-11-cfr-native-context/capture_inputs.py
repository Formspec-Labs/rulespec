"""Select diagnostic paragraphs; no model calls or production mutations."""
import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from refspec.input_pin import read_verified_file_pin
from refspec.registry import ecfr

HERE = Path(__file__).resolve().parent
CORPUS = Path('/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/refspec-output/ecfr-title-xml-2026-08-24')
SELECTIONS = [
    ('driver-introduction', 49, '382.107', 'Words or phrases used in this part'),
    ('driver-knowledge', 49, '382.107', 'Actual knowledge for the purpose'),
    ('refrigerant-equipment', 40, '82.156', '82.158'),
    ('refrigerant-practices', 40, None, 'The applicable practices in §§ 82.155'),
    ('treasury-regulations', 40, None, 'resolved by § 1.169-2(b)(2)'),
    ('foreign-title-suffix', 41, None, '§ 1954.3(d)(1)(i) of title 29'),
    ('quoted-foreign-section', 41, None, 'governed by “§ 20.206”'),
    ('mixed-title-local-scope', 41, None, 'Immediate notification. Each employer'),
    ('compound-part', 41, None, 'minimum wage prescribed in § 50-202.2'),
    ('derivatives-definitions', 17, None, 'Self-regulatory organization. This term means a contract market'),
    ('derivatives-accounts', 17, None, 'A futures commission merchant may not commingle futures customer funds'),
]


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def walk(node, path='/*[1]', ancestors=()):
    yield node, path, ancestors
    for index, child in enumerate(node, 1):
        yield from walk(child, path + f'/*[{index}]', (*ancestors, (path, node)))


def main():
    out = HERE / 'inputs-complete'
    out.mkdir()
    manifest = json.loads((CORPUS / 'manifest.json').read_text())
    captures = []
    for title in sorted({row[1] for row in SELECTIONS}):
        pin = next(row for row in manifest['titles'] if row['title'] == title)
        path = CORPUS / pin['path']
        raw = read_verified_file_pin(path, expected_sha256='sha256:' + pin['sha256'], expected_byte_length=pin['bytes'])
        root = ET.fromstring(raw)
        wanted = {row[0]: row for row in SELECTIONS if row[1] == title}
        for node, xpath, ancestors in walk(root):
            if node.tag != 'P':
                continue
            text = ''.join(node.itertext())
            section = next((parent for _, parent in reversed(ancestors) if parent.get('TYPE') in {'SECTION', 'APPENDIX'}), None)
            if section is None:
                continue
            selected = [name for name, (_, _, number, phrase) in wanted.items()
                        if phrase in text and (number is None or number == section.get('N'))]
            for name in selected:
                del wanted[name]
                paragraph = ET.tostring(node, encoding='unicode')
                # Reader input is a declared materialized excerpt. Source XPath
                # and original native ancestry refer to the pinned full title.
                excerpt = ET.Element(section.tag, section.attrib)
                excerpt.append(ET.fromstring(paragraph))
                xml = ET.tostring(excerpt, encoding='unicode')
                (out / f'{name}.xml').write_text(xml)
                prepared = ecfr.read_text(xml.encode())
                (out / f'{name}.txt').write_text(prepared['text'])
                native = [{'source_path': p, 'tag': a.tag, 'attributes': dict(a.attrib),
                           'headings': [ET.tostring(c, encoding='unicode') for c in a if c.tag == 'HEAD']}
                          for p, a in ancestors]
                titles = [a for a in native if a['attributes'].get('TYPE') == 'TITLE']
                assert len(titles) == 1 and int(titles[0]['attributes']['N']) == title
                captures.append({'id': name, 'kind': 'actual_publisher_paragraph', 'text': prepared['text'],
                    'xml': paragraph, 'source_path': xpath, 'native_ancestors': native,
                    'source': {'local_path': str(path), **pin}, 'context': {'title': title,
                        'source_path': titles[0]['source_path'], 'source_sha256': pin['sha256']},
                    'excerpt_sha256': hashlib.sha256(xml.encode()).hexdigest(),
                    'excerpt_method': 'one original paragraph in a copied native section or appendix element; title evidence retained separately'})
            if not wanted:
                break
        if wanted:
            save(out / f'unmatched-{title}.json', wanted)
        del root, raw
    save(out / 'real-cases.json', captures)
    print(json.dumps({'real_cases': len(captures), 'ids': [r['id'] for r in captures]}))


if __name__ == '__main__':
    main()
