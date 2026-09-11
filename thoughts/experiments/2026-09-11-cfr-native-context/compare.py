"""Diagnostic reuse of RefSpec's item/list/qualification code, in memory only.

The patched dispatcher is experimental. It adds section-label anchors to the
unchanged production scanner; production code, input text and wheels are not
edited. Source qualifications still run through find_cfr_citations' callback.
"""
from collections import Counter
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from unittest.mock import patch

from refspec.registry import citation_grammar as grammar, ecfr, xml_text

HERE = Path(__file__).resolve().parent
ANCHOR = re.compile(rf'{grammar._LEFT}(?P<label>{grammar._SECTION_MARKER})\s*', re.I)
LOCAL_SCOPE = re.compile(r'\s+of\s+this\s+(?:subchapter|chapter|title|part)\b', re.I)


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def key(title, part, section, *pinpoint, end=None, refusal=None):
    return {'title': title, 'part': part, 'section': section,
            'pinpoint': list(pinpoint), 'end': end, 'refusal': refusal}


EXPECTED = {
    'derivatives-definitions': [key(17, '1', '3', 'h'), key(17, '1', '3', 'rrrr')],
    'derivatives-accounts': [key(17, '30', '1'), key(17, '22', '1'), key(17, '39', '15', 'b', '2')],
    'refrigerant-equipment': [key(40, '82', '158')],
    'refrigerant-practices': [key(40, '82', n) for n in ('155', '156', '157', '158', '161', '164')],
    'treasury-regulations': [],
    'compound-part': [key(41, '50-202', '2')],
    'foreign-title-suffix': [],
    'quoted-foreign-section': [key(41, '50-204', '34', 'c')],
    'mixed-title-local-scope': [key(41, '50-204', '34', p) for p in ('b', 'c')],
    'driver-introduction': [key(49, '386', '2'), key(49, '390', '5T'), key(49, '40', '3')],
    'driver-knowledge': [key(49, '382', n) for n in ('121', '307')],
}


def controls():
    result = []
    def add(name, text, expected, titles=(40,), *, heading=None, metadata_title=None, section='82.156'):
        # These XML examples are constructed, not publisher outputs. Keep the
        # full source so the context admission can be checked independently.
        from xml.sax.saxutils import escape
        xml = f'<DIV8 N="{section}" TYPE="SECTION"><P>' + escape(text) + '</P></DIV8>'
        xml = f'<DIV5 N="{section.split(".")[0]}" TYPE="PART">{xml}</DIV5>'
        for title in reversed(titles):
            xml = f'<DIV1 N="{title}" TYPE="TITLE"><HEAD>Title {heading or title}</HEAD>{xml}</DIV1>'
        prepared = ecfr.read_text(xml.encode())
        paragraphs = [n for n in prepared['nodes'].values() if n['tag'] == 'P']
        assert len(paragraphs) == 1
        node = paragraphs[0]
        original = prepared['text'][node['start']:node['end']]
        assert original == text
        context = {'titles': list(titles), 'source_sha256': hashlib.sha256(xml.encode()).hexdigest(),
                   'source_path': '/*[1]', 'heading': heading}
        result.append({'id': name, 'kind': 'constructed_control', 'text': original,
                       'xml': xml, 'context': context, 'metadata_title': metadata_title, 'expected': expected})
    add('bare-local', 'See § 82.155.', [key(40, '82', '155')])
    add('stated-local-title', 'See § 82.155 of this title.', [key(40, '82', '155')])
    add('no-context', 'See § 82.155 of this title.', [], ())
    add('unverified-display-title', 'See § 82.155 of this title.', [], (), metadata_title=40)
    add('conflicting-native-titles', 'See § 82.155 of this title.', [], (40, 49))
    add('conflicting-heading', 'See § 82.155 of this title.', [], heading=49)
    add('other-title-explicit', 'See 17 CFR § 1.3 and § 1.4.', [])
    add('other-title-suffix', 'See § 1.3 of title 17, Code of Federal Regulations.', [])
    add('other-manual', 'See § 1.3 of the Operations Manual.', [])
    add('quoted-deictic-scope', 'The other agency regulation states: “§ 1.3 of this chapter applies.”', [])
    add('contradictory-local-part', 'See § 90.1 of this part.', [])
    add('local-list', 'See §§ 82.155(a), 82.156(b) of this part.',
        [key(40, '82', '155', 'a'), key(40, '82', '156', 'b')])
    add('repeated-local', 'See § 82.155 of this title; see § 82.155 of this title.',
        [key(40, '82', '155'), key(40, '82', '155')])
    add('local-range', 'See §§ 82.155 through 82.156 of this title.',
        [key(40, '82', '155', end={'title': 40, 'part': '82', 'section': '156'})])
    add('note-scope', 'See § 82.155 note of this title.', [key(40, '82', '155', refusal='note_target_unresolved')])
    add('open-ended-scope', 'See § 82.155 et seq. of this title.', [key(40, '82', '155', refusal='open_ended_reference_unresolved')])
    add('not-a-cfr-coordinate', 'See section 17 of the Act; the amount is 82.155 dollars.', [])
    add('paragraph-boundary', 'See § 82.155.\n\nReferences of this title follow.', [key(40, '82', '155')])
    add('explicit-usc', 'See 26 U.S.C. § 1 and 17 CFR § 1.3.', [])
    add('title-49-section', 'See § 40.3 of this title.', [key(49, '40', '3')], (49,))
    add('title-40-section', 'See § 40.3 of this title.', [key(40, '40', '3')])
    add('compound-local-part', 'See § 102-5.20 of this part.', [key(41, '102-5', '20')], (41,), section='102-5.1')
    return result


def prototype(text, title, mode):
    original = grammar._parse_cfr_citations
    groups = []
    def dispatcher(source, *, list_expansion, record=None):
        occupied = []
        def explicit(item):
            end = record(item)
            occupied.append((item.start, end))
            return end
        result = original(source, list_expansion=list_expansion, record=explicit)
        normalized = grammar._excise_compilations(grammar._normalize_dashes(source))
        for match in ANCHOR.finditer(normalized):
            if any(start <= match.start() < end for start, end in occupied):
                continue
            coordinate = grammar._CFR_COORDINATE.match(normalized, match.end())
            if coordinate is None or coordinate.group('section') is None:
                continue
            plural = grammar._label_is_plural(match.group('label'))
            item = grammar._read_cfr_item(source, normalized, title, match.start(), match.end(), plural)
            start, position = item.start, record(item)
            anchor_end = position
            while plural and not item.refusal:
                separator = grammar._CFR_LIST_ITEM.match(normalized, position)
                if separator is None or grammar._CITATION_PARAGRAPH_BREAK.search(source, position, separator.end()):
                    break
                coordinate = grammar._CFR_COORDINATE.match(normalized, separator.end())
                if coordinate is None or coordinate.group('section') is None:
                    break
                item = grammar._read_cfr_item(source, normalized, title, position, separator.end(), plural, (start, anchor_end))
                position = record(item)
            scope = LOCAL_SCOPE.match(source, position)
            scope = scope if scope and not grammar._CITATION_PARAGRAPH_BREAK.search(source, position, scope.end()) else None
            groups.append({'start': start, 'end': position,
                           'scope': None if scope is None else {'start': position, 'end': scope.end(), 'text': source[position:scope.end()]}})
            occupied.append((start, position))
        return result
    with patch.object(grammar, '_parse_cfr_citations', dispatcher):
        readings = grammar.find_cfr_citations(text)
    rows = []
    for item in readings:
        group = next((g for g in groups if g['start'] <= item.start < g['end']), None)
        if mode == 'C' and group and not group['scope'] and not item.refusal:
            item = replace(item, refusal='local_scope_not_stated')
        rows.append({'occurrence': asdict(item), 'native_context_used': group is not None, 'scope_group': group})
    return rows


def reading_key(row):
    value = row['occurrence']
    citation = value['citation']
    start = citation.get('start', citation)
    end = citation.get('end')
    return key(start['cfr_title'], start['cfr_part'], start['cfr_section'], *value['pinpoint'],
               end=None if end is None else {'title': end['cfr_title'], 'part': end['cfr_part'], 'section': end['cfr_section']},
               refusal=value['refusal'])


def run():
    cases = json.loads((HERE / 'cases.json').read_text())
    output = {}
    for arm in ('A', 'B', 'C'):
        rows = []
        for case in cases:
            context = case.get('context', {})
            titles = context.get('titles', [context['title']] if 'title' in context else [])
            title = titles[0] if len(titles) == 1 and context.get('source_sha256') else None
            baseline = [{'occurrence': asdict(r), 'native_context_used': False, 'scope_group': None}
                        for r in grammar.find_cfr_citations(case['text'])]
            result = baseline if arm == 'A' or title is None else prototype(case['text'], title, arm)
            unchanged = [r for r in result if not r['native_context_used']] == baseline
            assert unchanged, case['id']
            for row in result:
                item = row['occurrence']
                assert case['text'][item['start']:item['end']] == item['text']
            derived = [r for r in result if r['native_context_used']]
            pack = lambda value: json.dumps(value, sort_keys=True)
            expected = Counter(map(pack, case['expected']))
            # A diagnostic abstention is not a wrong target, but may omit one.
            actual = Counter(pack(reading_key(r)) for r in derived if r['occurrence']['refusal'] != 'local_scope_not_stated')
            rows.append({'id': case['id'], 'kind': case['kind'], 'readings': result,
                         'matched': sum((actual & expected).values()),
                         'missing': list((expected - actual).elements()),
                         'unexpected': list((actual - expected).elements()),
                         'exact_source_slices': True, 'explicit_readings_unchanged': unchanged})
        output[arm] = rows
    save(HERE / 'results.json', output)
    summary = {arm: {kind: {'cases': len(selected), 'matched': sum(r['matched'] for r in selected),
                           'missing': sum(len(r['missing']) for r in selected),
                           'unexpected': sum(len(r['unexpected']) for r in selected)}
                    for kind in ('actual_publisher_paragraph', 'constructed_control')
                    if (selected := [r for r in rows if r['kind'] == kind])}
               for arm, rows in output.items()}
    save(HERE / 'summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    if sys.argv[1] == 'prepare':
        cases = json.loads((HERE / 'inputs-complete/real-cases.json').read_text())
        assert {r['id'] for r in cases} == set(EXPECTED)
        for row in cases:
            row['expected'] = EXPECTED[row['id']]
        save(HERE / 'cases.json', cases + controls())
        save(HERE / 'source-freeze.json', {'model_calls': 0, 'modules': {
            str(Path(m.__file__)): hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
            for m in (grammar, ecfr, xml_text)},
            'files': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                      for name in ('PLAN.md', 'capture_inputs.py', 'compare.py', 'cases.json')},
            'commits': {name: subprocess.check_output(['git', '-C', path, 'rev-parse', 'HEAD'], text=True).strip()
                        for name, path in [('rulespec', HERE.parents[2]), ('refspec', Path(grammar.__file__).parents[3])]}})
        print(json.dumps({'real': len(cases), 'constructed': len(controls())}))
    elif sys.argv[1] == 'run':
        run()
