"""Bounded, capture-first comparison using existing extraction/audit helpers."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, context, core, documents, extraction as e

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / '2026-09-11-integrated-context-check'
MODEL = 'gemini-3.8-flash'
CONFIG = dict(max_output_tokens=32768, thinking_level='medium')
SCHEMA = deepcopy(a.COMPARISON_SCHEMA)
for name in ('claim_judgments', 'unit_judgments'):
    SCHEMA['properties'][name]['items']['properties']['source_refs']['items']['description'] = (
        'Select a supplied source alias and its passage or contiguous range, for example '
        'S0/F003 or S0/F003:F006. Never combine sources or focus/context prefixes in one range.')
GUIDANCE = '''
Source selection encoding: each source has an alias (S0, etc.), pinned document
metadata and a passage catalog. Cite source_refs as S0/F003 or S0/F003:F006,
using the actual supplied catalog. Unseen text and gaps between passages are not
available evidence. Focus positions identify the claims being assessed; additional
passages are evidence, not more claims to assess. Source roles and located references
do not establish governing scope. Feedback is an observation, not source authority.
Use no outside knowledge. An unconfirmed edition or unavailable target remains
unresolved. Draft quotation fields contain original text, not reference aliases.
'''


def save(name, value):
    e._save(ROOT / name, value)


def prepare():
    assert not (ROOT / 'cases.json').exists(), 'Frozen inputs already exist'
    cases = []
    for name in ('annual-14-91-213', 'annual-40-262-11'):
        book = e._load(ROOT / 'extract' / name / 'rulebook.json')
        window = e.plan_windows(book['document'], 3000)[0]
        cases.append(dict(id=name, inventory_group=name, book=book, window=window,
                          origin='fresh untouched extraction; first audit window'))
    old = next(c for c in e._load(PREVIOUS / 'cases.json') if c['id'] == 'label-scope')
    def selection(doc, start, end, identity):
        return documents.with_context(doc, dict(id=identity, index=0, start=start, end=end))
    cases.append(dict(id='saved-label', inventory_group='saved-label', book=old['book'],
        window=selection(old['book']['document'], old['focus']['start'], old['focus']['end'], 'saved-label-window'),
        origin=old['origin']))
    doc = old['book']['document']
    quote = "(A) The child is accompanied by a parent, guardian, or attendant designated by the child's parent or guardian to attend to the safety of the child during the flight;"
    start = doc['text'].index(quote)
    window = selection(doc, start, start + len(quote), 'companion-window')
    previous_answer = next(x['answer'] for x in e._load(PREVIOUS / 'cells/cell-02/decoded.json')['answers'] if x['question_id'] == 'q3')
    summaries = {
        'saved-adulthood': previous_answer,
        'faithful-companion': "Within the child-restraint permission in § 91.107(a)(3)(iii), one requirement is that the child be accompanied by a parent, guardian, or attendant designated by the child's parent or guardian to attend to the child's safety during the flight.",
    }
    for name, summary in summaries.items():
        book = core.compile_candidates(doc, [dict(kind='condition', actor='', quote=quote, summary=summary)],
            dict(id='constructed-control:' + name, model='constructed', started_at='2026-09-11T00:00:00+00:00'))
        assert len(book['accepted']) == 1 and not book['rejected'], book['rejected']
        cases.append(dict(id=name, inventory_group='companion', book=book, window=window,
            origin=dict(kind='constructed-profile-claim', summary_source=(
                'exact saved cell-02 q3 answer, including original opening No.' if name == 'saved-adulthood'
                else 'manually authored faithful control'), main_evidence='shared companion paragraph')))
    for case in cases:
        doc, window = case['book']['document'], case['window']
        sources = {'S0': dict(document={k:doc[k] for k in ('id','sha256','title','source_url')},
                             passages=e.passage_catalog(doc, window))}
        exported = context.export_context(case['book'], {k:window[k] for k in ('start','end')})
        assert list(exported['material']['sources']) == ['S0'], 'Unexpected external source: adapt source validation explicitly'
        case['materials'] = {'A': dict(sources=sources), 'B': exported['material']}
        save(f'contexts/{case["id"]}.json', exported)
        for arm, material in case['materials'].items():
            catalog = material['sources']['S0']['passages']
            for ref, span in catalog.items():
                assert e.resolve_passage(ref, catalog, doc)['quote'] == doc['text'][span['start']:span['end']]
    save('cases.json', cases)
    save('comparison-schema.json', SCHEMA)
    (ROOT / 'comparison-prompt.txt').write_text(a.comparison_prompt() + GUIDANCE)
    for name, path in e._runtime_sources().items():
        target = ROOT / 'runtime' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    save('runtime-versions.json', e._runtime_versions())
    print('Prepared', len(cases), 'cases; no provider calls')


def decode(case, arm, directory, attempts, labels):
    catalog = case['materials'][arm]['sources']['S0']['passages']
    original = e.resolve_passage
    def resolve(ref, unused_catalog, document, **kwargs):
        source, local = ref.split('/', 1)
        if source != 'S0':
            raise ValueError('Unknown supplied source')
        return original(local, catalog, document, **kwargs)
    with patch.object(e, 'resolve_passage', resolve):
        judgments, issues = a._judgments(directory, case['book'], labels, [case['window']], attempts, MODEL)
    report = a._assessment(case['book'], labels, judgments, issues)
    return dict(judgments=judgments, issues=issues, report=report)


def run():
    assert (ROOT / 'PRELABELS.md').exists(), 'Manual labels must precede calls'
    assert not (ROOT / 'inventory').exists(), 'No retries/overwriting captures'
    cases = e._load(ROOT / 'cases.json')
    deadline = time.monotonic() + 1800
    key = e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    inventory_inputs = {}
    for case in cases:
        group = case['inventory_group']
        inventory_inputs.setdefault(group, case)
    frozen = [ROOT / name for name in ('PLAN.md','PRELABELS.md','cases.json','comparison-schema.json','comparison-prompt.txt','run.py')]
    save('precall-pins.json', {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in frozen})
    for group, case in inventory_inputs.items():
        if time.monotonic() > deadline:
            save('stopped.json', {'reason':'time_bound','stage':'inventory','group':group}); break
        doc, window = case['book']['document'], case['window']
        prompt = e._window_prompt(e._prompt_generator([], a.INVENTORY_PROMPT), doc, window)
        save(f'inventory-inputs/{group}.json', dict(window=window, prompt=prompt, schema=a.INVENTORY_SCHEMA))
        directory = ROOT / 'inventory' / group
        print('Inventory', group, flush=True)
        attempts = a._capture(directory, doc, [window], [prompt], a.INVENTORY_SCHEMA, MODEL, key, None, **CONFIG)
        e._save(directory / 'attempts.json', attempts)
        inventory = a._inventory(directory, doc, [window], attempts)
        labels = a._labels(doc, inventory, MODEL)
        e._save(directory / 'inventory.json', inventory)
        e._save(directory / 'labels.json', labels)
    cells = []
    for index, case in enumerate(cases):
        group = ROOT / 'inventory' / case['inventory_group']
        if not (group / 'inventory.json').exists() or e._load(group / 'inventory.json')['issues']:
            cells.append(dict(case=case['id'], status='skipped_inventory_failure')); continue
        labels = e._load(group / 'labels.json')
        packet = a._model_input(a._comparison_input(case['book'], labels, case['window'])[0])
        for arm in (('A','B') if index % 2 == 0 else ('B','A')):
            if time.monotonic() > deadline:
                cells.append(dict(case=case['id'], arm=arm, status='skipped_time_bound')); continue
            name = f'cell-{len(cells):02d}'
            prompt = ((ROOT / 'comparison-prompt.txt').read_text()
                + '\nFocus positions: ' + e._canonical({k:case['window'][k] for k in ('start','end')})
                + '\nSource material: ' + e._canonical(case['materials'][arm])
                + '\nDraft and inventory: ' + e._canonical(packet))
            save(f'comparison-inputs/{name}.json', dict(case=case['id'], arm=arm, prompt=prompt, packet=packet))
            directory = ROOT / 'comparison' / name
            print('Comparison', name, flush=True)
            attempts = a._capture(directory, case['book']['document'], [case['window']], [prompt], SCHEMA, MODEL, key, None, **CONFIG)
            e._save(directory / 'attempts.json', attempts)
            payload, errors = a._read_response(directory, attempts[0])
            e._save(directory / 'raw-decoded.json', dict(payload=payload, errors=errors))
            result = decode(case, arm, directory, attempts, labels)
            e._save(directory / 'assessment.json', result)
            cells.append(dict(cell=name, case=case['id'], arm=arm, status='captured'))
    save('cells.json', cells)
    captured = [cell for cell in cells if cell['status'] == 'captured']
    random.SystemRandom().shuffle(captured)
    keymap = {}
    for index, cell in enumerate(captured):
        anonymous = f'review-{index:02d}'
        keymap[anonymous] = cell
        raw = e._load(ROOT / 'comparison' / cell['cell'] / 'raw-decoded.json')
        save(f'blind/{anonymous}.json', dict(case=cell['case'], **raw))
    save('arm-key.json', keymap)
    save('usage.json', {stage:e.recorded_usage(ROOT / stage) for stage in ('extract','inventory','comparison')})
    print('Capture complete. Review blind outputs before opening arm-key.json.', flush=True)


def replay():
    cases = {c['id']:c for c in e._load(ROOT / 'cases.json')}
    checked = []
    for cell in e._load(ROOT / 'cells.json'):
        if cell['status'] != 'captured': continue
        case = cases[cell['case']]
        labels = e._load(ROOT / 'inventory' / case['inventory_group'] / 'labels.json')
        directory = ROOT / 'comparison' / cell['cell']
        actual = decode(case, cell['arm'], directory, e._load(directory / 'attempts.json'), labels)
        assert actual == e._load(directory / 'assessment.json'), cell['cell']
        checked.append(cell['cell'])
    save('replay.json', dict(cells=checked, equal=True, provider_calls=0))
    print('Replayed', len(checked), 'captures, all identical')

if __name__ == '__main__':
    {'prepare':prepare, 'run':run, 'replay':replay}[sys.argv[1]]()
