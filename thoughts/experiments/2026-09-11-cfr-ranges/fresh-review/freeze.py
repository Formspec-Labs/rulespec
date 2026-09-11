"""Freeze six independently selected publisher paragraphs before parser use."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SOURCE = Path('/Users/mikewolfd/Work/RefSpec/output/ecfr-title-xml-2026-08-24')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    manifest_raw = (SOURCE / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    definitions = [
        ('controlled_substance_range', 2, '21 CFR 1308.11 through 1308.15',
         {'mode': 'range', 'title': 21, 'start': ['1308', '11'], 'end': ['1308', '15']},
         'high', 'The controlled-substance definition expressly names both sections with through. The surrounding text does not supply a list continuation.'),
        ('far_hyphenated_section', 2, '48 CFR 52.204-17',
         {'mode': 'single_or_explicit_refusal', 'title': 48, 'part': '52', 'section': '204-17'},
         'high', 'The highest-level-owner definition names one FAR provision. Preserve the complete hyphenated section or explicitly decline it; do not accept 52.204 alone or a range ending at part 17. Target existence is not checked.'),
        ('historical_aspr_ambiguity', 29, '32 CFR 1-403',
         {'mode': 'explicit_refusal', 'title': 32},
         'uncertain', 'This is a historical procurement reference after case citations. The paragraph does not establish that 1-403 is a range of CFR parts. Its precise historical address structure remains unresolved; neither part 1 alone nor parts 1 through 403 is justified from this context.'),
        ('walsh_healey_compound_part', 29, '41 CFR part 50-201',
         {'mode': 'single', 'title': 41, 'part': '50-201', 'section': None},
         'high', 'The Walsh-Healey overtime discussion names a single compound part. Neighboring overtime hours and fraction are prose; they are not range endpoints.'),
        ('fcc_hyphenated_section', 47, '47 CFR 19.735-203',
         {'mode': 'single_or_explicit_refusal', 'title': 47, 'part': '19', 'section': '735-203'},
         'high', 'The same paragraph earlier writes section 19.735-203(a) of this chapter, supporting one hyphenated section. Preserve the whole section or refuse explicitly; it is not 19.735 alone or a range to part 203.'),
        ('fee_collection_range', 47, '47 CFR 1.1901 through 1.1952',
         {'mode': 'range', 'title': 47, 'start': ['1', '1901'], 'end': ['1', '1952']},
         'high', 'The debt-collection paragraph names both endpoint sections with through. Nearby U.S.C., Statutes at Large, year, and Public Law numbers belong to separate citations.'),
    ]
    cases, pins = [], {}
    for case_id, title, focus, expected, certainty, reason in definitions:
        entry = next(row for row in manifest['titles'] if row['title'] == title)
        raw = (SOURCE / entry['path']).read_bytes()
        assert sha(raw) == entry['sha256'] and len(raw) == entry['bytes']
        pins[str(title)] = {**entry, 'path': str(SOURCE / entry['path'])}
        match = raw.find(focus.encode())
        assert match >= 0
        start = raw.rfind(b'<P>', 0, match)
        end = raw.index(b'</P>', match) + len(b'</P>')
        xml_raw = raw[start:end]
        assert focus.encode() in xml_raw
        text = ''.join(ET.fromstring(xml_raw).itertext())
        focus_start = text.index(focus)
        sections = list(re.finditer(rb'<DIV8\b[^>]*>', raw[:start]))
        section_tag = sections[-1].group().decode() if sections else None
        context_start, context_end = max(0, start - 1100), min(len(raw), end + 1100)
        cases.append({
            'id': case_id, 'source_title': title, 'source_path': str(SOURCE / entry['path']),
            'source_sha256': sha(raw), 'source_url': entry['url'], 'source_date': entry['date'],
            'start_byte': start, 'end_byte': end, 'xml_sha256': sha(xml_raw), 'xml': xml_raw.decode(),
            'raw_context_start_byte': context_start, 'raw_context_end_byte': context_end,
            'raw_context': raw[context_start:context_end].decode(), 'section_tag': section_tag,
            'text': text, 'text_sha256': sha(text.encode()), 'focus': focus,
            'focus_start': focus_start, 'focus_end': focus_start + len(focus),
            'expected': expected, 'label_certainty': certainty, 'assessment_before_parser': reason,
        })
    old = json.loads((HERE.parent.parent / '2026-09-11-cfr-whole-tokens/source-cases.json').read_text())
    assert not {(c['source_title'], c['start_byte'], c['end_byte']) for c in cases} & {
        (c['source_title'], c['start_byte'], c['end_byte']) for c in old}
    payload = {
        'schema': 'independent-cfr-range-source-cases/1',
        'selection': 'First two rg hits per title for CFR followed within 45 characters by digits and a hyphen, to, or through. Read exact surrounding XML; selected before current parser output.',
        'limitations': 'Six purposively located paragraphs; two explicit ranges, three compound-looking singles, one historical ambiguity. No fresh following-list-member case was selected. Reviewer labels are revisable judgments, not legal or target-existence gold.',
        'manifest_path': str(SOURCE / 'manifest.json'), 'manifest_sha256': sha(manifest_raw),
        'source_pins': pins, 'cases': cases,
    }
    path = HERE / 'source-cases.json'
    with path.open('x') as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'path': str(path), 'sha256': sha(path.read_bytes()), 'cases': len(cases)}))


if __name__ == '__main__':
    main()
