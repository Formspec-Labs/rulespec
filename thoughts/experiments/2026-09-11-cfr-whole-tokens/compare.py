"""Test whole native tokens against exact publisher XML and shape controls."""
from collections import Counter
from contextlib import ExitStack
import csv
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import types
from unittest.mock import patch
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT.parent
sys.path[:0] = [str(WORK/'RefSpec/src'), str(WORK/'spicysearch/src')]
from refspec.registry.iri_minting import mint_cfr_iri
from spicysearch import cfr_citations as spicy

baseline = subprocess.check_output(['git', '-C', str(WORK/'RefSpec'), 'show',
                                   '566df1d4:src/refspec/registry/citation_grammar.py'])
with (HERE/'baseline.py').open('xb') as f:
    f.write(baseline)
grammar = types.ModuleType('frozen_cfr_grammar')
sys.modules[grammar.__name__] = grammar
exec(compile(baseline, str(HERE/'baseline.py'), 'exec'), grammar.__dict__)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(name, data):
    with (HERE/name).open('x') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def native(text, whole=False):
    with ExitStack() as stack:
        if whole:
            # Reuse the strict token boundary, allowing RefSpec's existing
            # plausibility verdict to judge length instead of clipping it.
            token = spicy._CFR_PART_TOKEN.replace(r'\d{1,4}', r'\d+')
            for name in ('_CFR_STANDARD', '_CFR_TITLE_PART', '_CFR_LIST_ITEM'):
                pattern = getattr(grammar, name)
                stack.enter_context(patch.object(grammar, name, re.compile(
                    pattern.pattern.replace(grammar._CFR_PART_CAPTURE, token), pattern.flags)))
        rows = []
        for occurrence in grammar.find_cfr_citations(text):
            row = asdict(occurrence)
            c = occurrence.citation
            row['minted'] = (asdict(value) if (value := mint_cfr_iri(c.cfr_title, c.cfr_part, c.cfr_section)) else None)
            row['experimental_meaning'] = (
                'title_only' if c.cfr_part is None else
                'compound_part' if c.cfr_title == 41 and '-' in c.cfr_part else
                'ambiguous_hyphen' if '-' in c.cfr_part else 'single_part')
            rows.append(row)
        return rows


def readings(text):
    return {'baseline': native(text), 'whole_token_title_rule': native(text, True),
            'spicy_strict': [asdict(row) for row in spicy.extract_citations(text, strict=True, keep_rejected=True)]}


xml_root = WORK/'RefSpec/output/ecfr-title-xml-2026-08-24'
manifest = json.loads((xml_root/'manifest.json').read_text())
specimens = [
    ('compound_singular', 41, '41 CFR Part 60-3', {'parts': ['60-3']}),
    ('compound_list', 41, '41 CFR parts 102-193 and 102-194', {'parts': ['102-193', '102-194']}),
    ('compound_list_three', 41, '41 CFR parts 300-3, 301-10, and 301-70', {'parts': ['300-3', '301-10', '301-70']}),
    ('compound_section_range', 41, '41 CFR 101-19.600 to 101-19.607', {'range_start': '101-19.600', 'range_end': '101-19.607'}),
    ('numeric_part_range', 40, '40 CFR parts 1500 through 1508', {'range_start': '1500', 'range_end': '1508'}),
    ('compound_cross_title', 48, '41 CFR part 102-38', {'parts': ['102-38']}),
    ('compound_cross_title_list', 48, '41 CFR parts 60-300 and 61-300', {'parts': ['60-300', '61-300']}),
    ('five_digit_part', 5, '5 CFR part 10001', {'parts': ['10001']}),
]
captures, structure, sources = [], [], []
for title in (41, 40, 48, 5, 16):
    pin = next(r for r in manifest['titles'] if r['title'] == title)
    raw = (xml_root/pin['path']).read_bytes()
    assert sha(raw) == pin['sha256']
    sources.append(pin)
    tree = ET.fromstring(raw)
    for part in tree.iter():
        if part.get('TYPE') != 'PART':
            continue
        head = ''.join(part.find('HEAD').itertext()).strip() if part.find('HEAD') is not None else ''
        structure.append({'title': title, 'number': part.get('N'), 'head': head,
                          'section_count': sum(e.get('TYPE') == 'SECTION' for e in part.iter())})
    pending = [s for s in specimens if s[1] == title]
    for match in re.finditer(rb'<P(?:\s[^>]*)?>.*?</P>|<PSPACE(?:\s[^>]*)?>.*?</PSPACE>', raw, re.S):
        text = ''.join(ET.fromstring(match[0]).itertext())
        for item in list(pending):
            name, _, focus, expected = item
            if focus not in text:
                continue
            captures.append({'id': name, 'source_title': title, 'start_byte': match.start(), 'end_byte': match.end(),
                             'xml': match[0].decode(), 'raw_context': raw[max(0, match.start()-200):match.end()+200].decode(),
                             'text': text, 'focus': focus, 'focus_start': text.index(focus), 'expected': expected})
            pending.remove(item)
        if not pending:
            break
    assert not pending, pending
save('sources.json', {'manifest': str(xml_root/'manifest.json'), 'manifest_sha256': sha((xml_root/'manifest.json').read_bytes()),
                      'titles': sources, 'baseline_sha256': sha(baseline)})
save('source-cases.json', captures)
save('xml-part-structure.json', structure)

out = []
for case in captures:
    variants = [('original', case['focus']), ('unicode_dash', case['focus'].replace('-', '–')),
                ('linebreak', case['focus'].replace(' ', '\n')), ('neighbor', case['focus']+'; 5 USC 552.')]
    out.append({'id': case['id'], 'expected': case['expected'],
                'variants': [{'mutation': name, 'text': text, **readings(text)} for name, text in variants]})
controls = ['40 CFR parts 60-63', '40 CFR 60-63', '41 CFR parts 50-1 through 50-200',
            '41 CFR 60-1.4(a)', '41 CFR 60-1-60-2', '7 CFR 15a', '17 CFR 15c3-3',
            '40 CFR part 37, 12 people attended.', '35 CFR 62', '1345 CFR 1370.31',
            '3 CFR 127 (1981 Comp.)', '41 CFR part 102-117, 15 USC 78c.']
save('source-results.json', out)
save('controls.json', [{'text': text, **readings(text)} for text in controls])

index = WORK/'RefSpec/research/evidence/cfr-subject-index-2026-08-20/part-subjects.csv'
keys = sorted({(r['cfr_title'], r['cfr_part']) for r in csv.DictReader(index.open())})
counts = {arm: Counter() for arm in ('baseline', 'whole_token_title_rule', 'spicy_strict')}
with gzip.open(HERE/'index-results.jsonl.gz', 'xt') as f:
    for title, part in keys:
        text = f'{title} CFR {part}'
        result = readings(text)
        for arm, rows in result.items():
            got = {str(r.get('citation', {}).get('cfr_part', r.get('part'))) for r in rows}
            counts[arm]['correct_complete_part' if got == {part} else 'wrong_or_missing_part'] += 1
            if arm != 'spicy_strict':
                counts[arm]['implausible_parts'] += sum(r['citation']['part_is_plausible'] is False for r in rows)
                counts[arm]['minted'] += sum(r['minted'] is not None for r in rows)
        f.write(json.dumps({'text': text, 'expected_part': part, **result}, ensure_ascii=False)+'\n')
save('summary.json', {'source_cases': len(captures), 'source_variants': len(out)*4, 'constructed_controls': len(controls),
                     'index_keys': len(keys), 'index_path': str(index), 'index_sha256': sha(index.read_bytes()),
                     'shape_results': {arm: dict(count) for arm, count in counts.items()},
                     'xml_parts': len(structure),
                     'xml_plural_headings': sum(r['head'].startswith('PARTS ') for r in structure),
                     'model_calls': 0, 'production_changes': False})
print((HERE/'summary.json').read_text())
