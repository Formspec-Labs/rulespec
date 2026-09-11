"""Frozen, zero-model-call comparison of existing context dependencies."""
import hashlib
import json
import sys
from pathlib import Path

from rulespec_extrapolator.core import resolve_links
from rulespec_extrapolator.discovery import verified
from rulespec_extrapolator.documents import prepare_document, with_context

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def span(text, start, stop=None):
    lo = text.index(start)
    hi = text.index(stop, lo + len(start)) if stop else lo + len(start)
    return {'start': lo, 'end': hi, 'text': text[lo:hi]}


def manual_claim(text, quote, identity):
    s = span(text, quote)
    return {'id': identity, 'kind': 'requirement', 'start': s['start'], 'end': s['end'],
            'summary': quote, 'evidence': [dict(start=s['start'], end=s['end'], quote=quote, field='summary')],
            'applies_to': [], 'target_ids': [], 'references': [], 'reference_links': []}


def prepare():
    prior = load(ROOT.parent / '2026-09-10-design-context/cases.json')
    cases = []
    for c in prior[:3]:
        book = load(Path(c['origin']['book_path']))
        cases.append({'id': c['id'], 'origin': c['origin'], 'book': book, 'focus': c['claim']['id']})
    t = cases[0]['book']['document']['text']
    cases[0]['required'] = [span(t, '(1) No person', '\n\n(i)'), span(t, '(i) Carbon dioxide', '\n\n(2)'),
                            span(t, '(2) \n', '\n\n(3)'), span(t, '(b) No person', t[-1:])]
    # Include the last punctuation too: service/equipment requirement must be complete.
    cases[0]['required'][-1]['end'] = len(t)
    cases[0]['required'][-1]['text'] = t[cases[0]['required'][-1]['start']:]
    cases[0]['irrelevant'] = [span(t, '(3) The knowing release', '\n\n(b)')]
    for c in cases[1:]:
        t = c['book']['document']['text']
        c['required'] = [span(t, '(3) Except as provided', '\n\n(i)'),
                         span(t, '(iii) Notwithstanding', '\n\n(A)'),
                         span(t, '(b) Unless otherwise stated', '\n\n[Docket')]
        focus = next(x for x in c['book']['accepted'] if x['id'] == c['focus'])
        c['required'].append({'start': focus['start'], 'end': focus['end'], 'text': t[focus['start']:focus['end']]})
        c['irrelevant'] = [span(t, '(1) No pilot may take off', '\n\n(2)')]
        c['uncertainty'] = 'Deliver both notwithstanding and the Part135 exclusion; do not infer which governs.'
    for name, quote in [('fire-plan', '(4) The name or job title of employees responsible for maintaining equipment to prevent or control sources of ignition or fires; and'),
                        ('alarms', '(3) The employer shall maintain or replace power supplies as often as is necessary to assure a fully operational condition. Back-up means of alarm, such as employee runners or telephones, shall be provided when systems are out of service.')]:
        t = (ROOT / 'sources' / f'{name}.txt').read_text()
        doc = prepare_document(t, title=name, source_url=(ROOT / 'sources' / f'{name}.url').read_text().strip())
        claim = manual_claim(t, quote, name)
        c = {'id': name, 'origin': {'kind': 'new-natural-source-manual-focus', 'no_provider_extraction': True},
             'book': {'document': doc, 'accepted': [claim]}, 'focus': name}
        if name == 'fire-plan':
            c['required'] = [span(t, '(a)', '\n        '), span(t, '(c)', '\n        '), span(t, quote)]
            c['irrelevant'] = [span(t, '(d)', '\n        ')]
        else:
            c['required'] = [span(t, '(a)', '\n        '), span(t, '(2) The requirements in this section', '\n\n(3)'),
                             span(t, '(5) The employer shall establish', '\n        '), span(t, quote)]
            c['irrelevant'] = [span(t, '(e)', '\n        ')]
            c['uncertainty'] = 'The small-workplace backup exception is potentially relevant; delivery does not settle its interaction with out-of-service backup means.'
        cases.append(c)
    c = prior[3]
    claim = dict(c['claim'], id='constructed-parent', target_ids=[], reference_links=[])
    t = c['document']['text']
    cases.append({'id': 'constructed-parent', 'origin': {'kind': 'constructed'},
                  'book': {'document': c['document'], 'accepted': [claim]}, 'focus': claim['id'],
                  'required': [span(t, '(2) Visitors', '\n\n(b)'), span(t, '(b) The waiting room closes at 18:00.')],
                  'irrelevant': [span(t, '(a) Staff entering', '\n\n(1)'), span(t, '(1) Staff must sign', '\n\n(2)')]})
    t = ('Opening\n\nVisitors may enter the archive under the conditions in Annex. External Standard X governs laboratory access.\n\n'
         'Annex\n\nVisitors must be accompanied by an archivist and must leave bags outside.\n\n'
         'Laboratory\n\nLaboratory staff must wear goggles.')
    starts = [0, t.index('Annex\n'), t.index('Laboratory\n'), len(t)]
    sections = [dict(id=name.lower(), label=name, start=lo, end=hi) for name, lo, hi in zip(['Opening', 'Annex', 'Laboratory'], starts, starts[1:])]
    doc = prepare_document(t, title='Constructed resolved and external references', sections=sections)
    claim = manual_claim(t, 'Visitors may enter the archive under the conditions in Annex. External Standard X governs laboratory access.', 'reference-control')
    claim['references'] = ['Annex', 'External Standard X']
    issues = resolve_links(doc, [claim])
    cases.append({'id': 'reference-control', 'origin': {'kind': 'constructed', 'references': 'manual labels resolved by current core.resolve_links'},
                  'book': {'document': doc, 'accepted': [claim], 'unresolved': issues}, 'focus': claim['id'],
                  'required': [span(t, claim['summary']), span(t, 'Visitors must be accompanied by an archivist and must leave bags outside.')],
                  'irrelevant': [span(t, 'Laboratory staff must wear goggles.')],
                  'unavailable': ['External Standard X']})
    for c in cases:
        text = c['book']['document']['text']
        for s in c['required'] + c['irrelevant']:
            assert s['text'] == text[s['start']:s['end']] and s['end'] > s['start']
    save(ROOT / 'cases.json', cases)
    paths = [ROOT / 'PLAN.md', Path(__file__), ROOT / 'cases.json', *sorted((ROOT / 'sources').glob('*')),
             *[REPO / 'packages/rulespec-extrapolator/src/rulespec_extrapolator' / name for name in ('documents.py', 'discovery.py', 'core.py', 'terms.py')]]
    save(ROOT / 'freeze.json', {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    print('Seven cases and exact span expectations frozen; no selection scored.')


def select(c, arm):
    book = c['book']; doc = book['document']; claims = {x['id']: x for x in book['accepted']}; focus = claims[c['focus']]
    w = with_context(doc, {'start': focus['start'], 'end': focus['end']}, context_chars=2400)
    spans = [dict(start=focus['start'], end=focus['end'], reason='focus')]
    spans += [dict(start=e['start'], end=e['end'], reason='existing-evidence:' + e['field']) for e in verified(book, focus['evidence'])]
    spans += [dict(start=s['start'], end=s['end'], reason='current-context', truncated=s['truncated']) for s in w['context_spans']]
    unresolved = [dict(claim_id=focus['id'], **r) for r in focus.get('reference_links', []) if r['status'] != 'resolved']
    linked = []
    if arm == 'B':
        linked = [x for x in claims.values() if x['id'] in focus.get('target_ids', []) or focus['id'] in x.get('target_ids', [])]
        for x in linked:
            spans += [dict(start=e['start'], end=e['end'], reason='relationship:' + x['id']) for e in verified(book, x['evidence'])]
        for x in [focus, *linked]:
            for target in x.get('target_ids', []):
                if target not in claims:
                    unresolved.append({'claim_id': x['id'], 'target': target, 'status': 'missing_target'})
            for ref in x.get('reference_links', []):
                section = next((s for s in doc['sections'] if s['id'] == ref.get('section_id')), None)
                if ref['status'] == 'resolved' and section:
                    spans.append(dict(start=section['start'], end=section['end'], reason='resolved-reference:' + ref['text']))
                elif x is not focus or ref['status'] == 'resolved':
                    unresolved.append(dict(claim_id=x['id'], **ref))
    full_document = False
    if arm == 'C':
        containing = [s for s in doc['sections'] if s['start'] <= focus['start'] and focus['end'] <= s['end']]
        if containing:
            s = min(containing, key=lambda s: (s['end'] - s['start'], s['id']))
            spans.append(dict(start=s['start'], end=s['end'], reason='declared-section:' + s['id']))
            full_document = s['start'] == 0 and s['end'] == len(doc['text'])
        else:
            unresolved.append({'status': 'no_enclosing_section'})
    positions = set()
    for s in spans:
        assert 0 <= s['start'] < s['end'] <= len(doc['text'])
        s['text'] = doc['text'][s['start']:s['end']]
        positions.update(range(s['start'], s['end']))
    def present(s):
        return set(range(s['start'], s['end'])) <= positions
    return {'case': c['id'], 'arm': arm, 'spans': spans, 'required': list(map(present, c['required'])),
            'irrelevant': list(map(present, c['irrelevant'])), 'unique_chars': len(positions),
            'repeated_chars': sum(s['end'] - s['start'] for s in spans) - len(positions),
            'relationship_count': len(linked), 'unresolved': unresolved, 'full_document_fallback': full_document,
            'current_context_omitted_passage_ids': w['context_omitted_passage_ids']}


def run(replay=False):
    for name, sha in load(ROOT / 'freeze.json').items():
        assert hashlib.sha256((REPO / name).read_bytes()).hexdigest() == sha, name
    cases = load(ROOT / 'cases.json')
    rows = [select(c, arm) for c in cases for arm in 'ABC']
    totals = {arm: {'required_spans': sum(sum(r['required']) for r in rows if r['arm'] == arm),
                    'all_required_cases': sum(all(r['required']) for r in rows if r['arm'] == arm),
                    'unique_chars': sum(r['unique_chars'] for r in rows if r['arm'] == arm),
                    'irrelevant_spans': sum(sum(r['irrelevant']) for r in rows if r['arm'] == arm)} for arm in 'ABC'}
    result = {'provider_calls': 0, 'rows': rows, 'totals': totals,
              'required_count': sum(len(c['required']) for c in cases), 'case_count': len(cases)}
    if replay:
        assert result == load(ROOT / 'results.json')
        save(ROOT / 'replay.json', {'provider_calls': 0, 'status': 'exact selections, scores, and frozen hashes matched'})
    else:
        save(ROOT / 'results.json', result)
    print(json.dumps(totals, indent=2))


if __name__ == '__main__':
    {'prepare': prepare, 'run': run, 'replay': lambda: run(True)}[sys.argv[1]]()
