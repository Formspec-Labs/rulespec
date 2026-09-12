"""Bounded inventory experiment; existing capture, grounding and judgment code."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch
import xml.etree.ElementTree as ET

from rulespec_extrapolator import audit as a, context, core, extraction as e
from rulespec_extrapolator.uslm import prepare_xml

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / '2026-09-11-context-audit-comparison'
spec = importlib.util.spec_from_file_location('prior_comparison', PRIOR / 'run.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
MODEL, CONFIG = previous.MODEL, previous.CONFIG
ENV = Path('/Users/mikewolfd/Work/spicy-regs/.env')


def save(name, value):
    e._save(ROOT / name, value)


def pins(paths):
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}


def timed(name, function):
    path = ROOT / 'calls.json'
    calls = e._load(path) if path.exists() else []
    usage = e.recorded_usage(ROOT)
    if (len(calls) >= 14 or sum(c['seconds'] for c in calls) >= 1800
            or usage['tokens'].get('total_token_count', 0) >= 300000):
        save('stopped.json', {'reason': 'bound_reached', 'next_call': name})
        raise SystemExit('Experiment bound reached')
    started = time.monotonic()
    print('Capture', name, flush=True)
    try:
        return function()
    finally:
        calls.append({'name': name, 'seconds': time.monotonic() - started})
        save('calls.json', calls)


def source_span(document, span):
    parts = core.evidence_parts(document, span['quote'], 'audit', span['start'], span['end'])
    if not parts:
        raise ValueError('Selected span lacks original source evidence')
    return {'source_id': document['id'], **span}


def evidence_receipt(document, value):
    spans = {}
    def visit(item):
        if isinstance(item, dict):
            if all(k in item for k in ('source_id', 'quote', 'start', 'end')):
                key = core.digest([item['start'], item['end'], item['quote']])
                spans[key] = {'span': item,
                    'parts': core.evidence_parts(document, item['quote'], 'audit', item['start'], item['end']),
                    'ordinary_audit_would_refuse': any(p['kind'] != 'source' and p['start'] < item['end']
                        and item['start'] < p['end'] for p in document.get('source_map', []))}
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
    visit(value)
    assert all(s['parts'] for s in spans.values())
    return spans


def prepare():
    assert not (ROOT / 'sources').exists(), 'Never overwrite frozen sources'
    source_root = Path('/Users/mikewolfd/Work/RefSpec/output/ecfr-title-xml-2026-08-24')
    manifest = e._load(source_root / 'manifest.json')
    records = []
    for title, section in ((14, '61.56'), (29, '1910.132')):
        record = next(r for r in manifest['titles'] if r['title'] == title)
        raw = (source_root / record['path']).read_bytes()
        assert sha256(raw).hexdigest() == record['sha256']
        tree = ET.fromstring(raw)
        selected = [n for n in tree.iter() if n.get('TYPE') == 'SECTION' and n.get('N') == section]
        assert len(selected) == 1
        xml = ET.tostring(selected[0], encoding='unicode')
        name = f'ecfr-{title}-{section.replace(".", "-")}'
        doc = prepare_xml(xml, title=f'{title} CFR {section} (captured {record["date"]})', source_url=record['url'])
        assert 3000 < len(doc['text']) < 12000
        save(f'sources/{name}.document.json', doc)
        (ROOT / f'sources/{name}.xml').write_text(xml)
        records.append({'id': name, 'capture': record, 'subtree_sha256': sha256(xml.encode()).hexdigest(),
                        'transformation': 'ElementTree section subtree serialization, not original title bytes'})
    save('source-receipts.json', records)
    save('pre-extraction-pins.json', pins([ROOT / 'PLAN.md', ROOT / 'run.py', ROOT / 'source-receipts.json',
                                          *sorted((ROOT / 'sources').iterdir())]))
    print('Prepared two new sections without provider calls')


def extract():
    assert not (ROOT / 'extract').exists(), 'No retries'
    for record in e._load(ROOT / 'source-receipts.json'):
        name = record['id']
        doc = e._load(ROOT / f'sources/{name}.document.json')
        timed('extract/' + name, lambda: e.extract_run(doc, ROOT / 'extract' / name, MODEL,
            env_file=ENV, max_output_tokens=32768, thinking_level='low'))


def freeze():
    assert not (ROOT / 'cases.json').exists()
    books = [('equipment', e._load(PRIOR / 'extract/annual-14-91-213/rulebook.json'), 'saved-provider-development-case')]
    for record in e._load(ROOT / 'source-receipts.json'):
        name = record['id']
        book = e._load(ROOT / 'extract' / name / 'rulebook.json')
        books.append((name, book, 'new-untouched-provider-extraction'))
    cases = []
    for name, book, origin in books:
        doc = book['document']
        focus = e.plan_windows(doc, 3000)[0]
        full = e.plan_windows(doc, 24000)[0]
        assert full['start'] == 0 and full['end'] == len(doc['text'])
        exported = context.export_context(book, {k: focus[k] for k in ('start', 'end')})
        sources = exported['material']['sources']
        assert list(sources) == ['S0']
        # Context renumbers passages after skipping whitespace-only entries.
        # Compare supplied source spans, not request-local alias spellings.
        assert list(sources['S0']['passages'].values()) == list(e.passage_catalog(doc, full).values())
        for ref in sources['S0']['passages']:
            context.resolve_context({'source': 'S0', 'passage': ref}, exported)
        save(f'contexts/{name}.json', exported)
        cases.append(dict(id=name, book=book, origin=origin, focus=focus, window=full,
                          materials={'A': exported['material'], 'B': exported['material']}))
    save('cases.json', cases)
    save('schemas.json', {'inventory': a.INVENTORY_SCHEMA, 'comparison': previous.SCHEMA})
    (ROOT / 'inventory-prompt.txt').write_text(a.INVENTORY_PROMPT)
    (ROOT / 'comparison-prompt.txt').write_text(a.comparison_prompt() + previous.GUIDANCE)
    sources = {**e._runtime_sources(), 'application/context.py': Path(context.__file__),
               'experiment/prior-adapter.py': PRIOR / 'run.py'}
    for name, path in sources.items():
        target = ROOT / 'runtime' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    save('runtime-sha256.json', {name: sha256(path.read_bytes()).hexdigest() for name, path in sources.items()})
    save('runtime-versions.json', e._runtime_versions())
    print('Frozen', len(cases), 'cases')


def decode(case, directory, labels):
    with patch.object(a, '_source_span', source_span):
        return previous.decode(case, 'A', directory, e._load(directory / 'attempts.json'), labels)


def run():
    assert (ROOT / 'PRELABELS.md').exists()
    assert not (ROOT / 'inventory').exists(), 'No retries'
    cases = e._load(ROOT / 'cases.json')
    key = e._credential(ENV)
    save('pre-audit-pins.json', pins([ROOT / n for n in ('PLAN.md', 'PRELABELS.md', 'run.py', 'cases.json',
        'schemas.json', 'inventory-prompt.txt', 'comparison-prompt.txt', 'runtime-sha256.json')]))
    cells = []
    for index, case in enumerate(cases):
        doc = case['book']['document']
        for arm in (('A', 'B') if index % 2 == 0 else ('B', 'A')):
            window = case['focus'] if arm == 'A' else case['window']
            prompt = e._window_prompt(e._prompt_generator([], a.INVENTORY_PROMPT), doc, window)
            name = case['id'] + '-' + arm
            directory = ROOT / 'inventory' / name
            save(f'inputs/{name}-inventory.json', {'window': window, 'prompt': prompt, 'schema': a.INVENTORY_SCHEMA})
            attempts = timed('inventory/' + name, lambda: a._capture(directory, doc, [window], [prompt],
                a.INVENTORY_SCHEMA, MODEL, key, None, **CONFIG))
            e._save(directory / 'attempts.json', attempts)
            with patch.object(a, '_source_span', source_span):
                inventory = a._inventory(directory, doc, [window], attempts)
            e._save(directory / 'inventory.json', inventory)
            labels = a._labels(doc, inventory, MODEL)
            # Schedule every generated unit for the shared full-book comparison.
            # Preserve original inventory window assignments in inventory.json.
            for unit in labels['expected_units']:
                unit['inventory_window_id'] = unit['window_id']
                unit['window_id'] = case['window']['id']
            e._save(directory / 'labels.json', labels)
            if inventory['issues']:
                cells.append({'case': case['id'], 'arm': arm, 'status': 'skipped_inventory_failure'})
                continue
            packet = a._model_input(a._comparison_input(case['book'], labels, case['window'])[0])
            prompt = ((ROOT / 'comparison-prompt.txt').read_text()
                + '\nFocus positions: ' + e._canonical({k: case['window'][k] for k in ('start', 'end')})
                + '\nSource material: ' + e._canonical(case['materials'][arm])
                + '\nDraft and inventory: ' + e._canonical(packet))
            save(f'inputs/{name}-comparison.json', {'prompt': prompt, 'packet': packet, 'schema': previous.SCHEMA})
            output = ROOT / 'comparison' / name
            attempts = timed('comparison/' + name, lambda: a._capture(output, doc, [case['window']], [prompt],
                previous.SCHEMA, MODEL, key, None, **CONFIG))
            e._save(output / 'attempts.json', attempts)
            payload, errors = a._read_response(output, attempts[0])
            e._save(output / 'raw-decoded.json', {'payload': payload, 'errors': errors})
            assessment = decode(case, output, labels)
            e._save(output / 'assessment.json', assessment)
            e._save(output / 'source-evidence.json', evidence_receipt(doc, [inventory, assessment['judgments']]))
            cells.append({'case': case['id'], 'arm': arm, 'name': name, 'status': 'captured'})
            save('cells.json', cells)
    shuffled = [c for c in cells if c['status'] == 'captured']
    random.SystemRandom().shuffle(shuffled)
    mapping = {}
    for index, cell in enumerate(shuffled):
        anonymous = f'review-{index:02d}'
        name = cell['name']
        labels = e._load(ROOT / 'inventory' / name / 'labels.json')
        inventory = {f'U{i:04d}': {k: u[k] for k in ('meaning', 'kind', 'source_spans')}
                     for i, u in enumerate(labels['expected_units'])}
        raw = e._load(ROOT / 'comparison' / name / 'raw-decoded.json')
        save(f'blind/{anonymous}.json', {'case': cell['case'], 'inventory': inventory, **raw})
        mapping[anonymous] = cell
    save('arm-key.json', mapping)
    save('cells.json', cells)
    save('usage.json', {stage: e.recorded_usage(ROOT / stage) for stage in ('extract', 'inventory', 'comparison')})
    print('Captures ready for anonymous review', flush=True)


def replay():
    cases = {c['id']: c for c in e._load(ROOT / 'cases.json')}
    checked = []
    for cell in e._load(ROOT / 'cells.json'):
        if cell['status'] != 'captured':
            continue
        case, name = cases[cell['case']], cell['name']
        directory = ROOT / 'inventory' / name
        window = case['focus'] if cell['arm'] == 'A' else case['window']
        with patch.object(a, '_source_span', source_span):
            inventory = a._inventory(directory, case['book']['document'], [window], e._load(directory / 'attempts.json'))
        assert inventory == e._load(directory / 'inventory.json')
        output = ROOT / 'comparison' / name
        assert decode(case, output, e._load(directory / 'labels.json')) == e._load(output / 'assessment.json')
        checked.append(name)
    save('replay.json', {'cells': checked, 'inventory_and_comparison_identical': True, 'provider_calls': 0})
    print('Replayed', len(checked), 'pairs without model calls')


if __name__ == '__main__':
    {'prepare': prepare, 'extract': extract, 'freeze': freeze, 'run': run, 'replay': replay}[sys.argv[1]]()
