"""Task-definition comparison with unchanged source, schema and checking code."""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import time
from unittest.mock import patch
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.uslm import prepare_xml

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / '2026-09-12-fresh-focused-repair'
NAV = HERE.parent / '2026-09-12-navigation-repair'
spec = importlib.util.spec_from_file_location('navigation_helpers', NAV / 'run.py')
nav = importlib.util.module_from_spec(spec); spec.loader.exec_module(nav)
ENV = Path('/Users/mikewolfd/Work/spicy-regs/.env')
SELECTION = '\nREQUEST SCOPE: evaluate only the selected statement aliases for edits. Do not add records or edit other statements; keep other records available as context.\n'
CONSTRUCTION = """
TASK FOR THIS REQUEST: construct a self-contained default reading for each
selected statement from the supplied source and located reference provisions.
This includes a statement that faithfully quotes its own provision but leaves
its governing local meaning in another record. Incorporating that governing
meaning into the selected statement is a substantive improvement, not a duplicate
record or merely a stylistic rewrite. A local clause pointer or another record
does not substitute for the governing content in this statement's default reading.
Put the complete resulting meaning in fields.summary. Retain every correct
condition, actor, modal force, exception, alternative, threshold and time limit.
Determine whether each referenced provision actually governs this statement;
a related or independently applicable duty must not become an invented
prerequisite, different actor's duty or cancellation of a surviving obligation.
Keep separate records intact. Preserve correct other fields and use exact source
evidence for incorporated meaning. Do not invent contents of unavailable provisions.
Return an edit for a selected statement that needs this construction. If it is
already independently complete or the supplied source cannot resolve the issue,
return a source-based observation using that statement's quotation and an
appropriate disposition. Do not change a statement merely to produce an edit.
"""


def save(name, value):
    path = HERE / name; path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert e._load(path) == value, name
    else: e._save(path, value)


def freeze(name, paths):
    save(name, {os.path.relpath(p, HERE): sha256(p.read_bytes()).hexdigest() for p in paths})


def pins(name):
    for path, digest in e._load(HERE / name).items():
        assert sha256((HERE / path).read_bytes()).hexdigest() == digest, path


def call(name, function):
    pins('source-pins.json')
    ledger = e._load(HERE / 'calls.json') if (HERE / 'calls.json').exists() else []
    assert name not in {c['name'] for c in ledger}, 'No provider retry'
    assert len(ledger) < 17 and sum(c['seconds'] for c in ledger) < 1200
    assert e.recorded_usage(HERE)['tokens'].get('total_token_count', 0) < 220000
    start = time.monotonic()
    try: return function()
    finally:
        ledger.append(dict(name=name, seconds=time.monotonic() - start))
        e._save(HERE / 'calls.json', ledger)


def source():
    archive = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
    with ZipFile(archive) as zipped: raw = zipped.read('usc15.xml')
    root = ET.fromstring(raw)
    nodes = [n for n in root.iter() if n.get('identifier') == '/us/usc/t15/s6504/a/2']
    assert len(nodes) == 1
    wrapper = ET.Element(root.tag, root.attrib); wrapper.append(nodes[0])
    xml = ET.tostring(wrapper, encoding='unicode')
    doc = prepare_xml(xml, title='15 USC 6504(a)(2) — pinned release 119-102',
        source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
    assert len(e.plan_windows(doc)) == 1
    save('notice-source.json', doc)
    save('source-receipt.json', dict(archive=str(archive), archive_sha256=sha256(archive.read_bytes()).hexdigest(),
        member='usc15.xml', member_sha256=sha256(raw).hexdigest(), serialized_sha256=sha256(xml.encode()).hexdigest(),
        native_excerpt='/us/usc/t15/s6504/a/2', release='119-102', serialization='Complete native paragraph inside original uscDoc wrapper'))
    save('runtime.json', e._runtime_versions())
    freeze('source-pins.json', [p for p in HERE.iterdir() if p.is_file()] + list(e._runtime_sources().values()) + [NAV / 'run.py'])
    print('New source and task instruction frozen; zero provider calls.')


def extract():
    assert not (HERE / 'notice-extract').exists()
    book = call('notice-extract', lambda: e.extract_run(e._load(HERE / 'notice-source.json'), HERE / 'notice-extract', env_file=ENV))
    print(book['run']['status'], len(book['accepted']), 'accepted;', len(book['rejected']), 'rejected')


def store(directory, case, book):
    path = {'pension': OLD / 'extract/pension', 'notice': HERE / 'notice-extract'}.get(case)
    if path:
        assert e._load(path / 'rulebook.json') == book
        shutil.copytree(path, directory, dirs_exist_ok=True)
        return ReviewStore(directory)
    return nav.temporary_store(directory, book)


def prepare():
    pins('source-pins.json')
    assert not (HERE / 'cells.json').exists()
    books = {'pension': e._load(OLD / 'extract/pension/rulebook.json'),
             'control': e._load(NAV / 'books.json')['control'],
             'notice': e._load(HERE / 'notice-extract/rulebook.json')}
    selected = e._load(HERE / 'selected.json')
    for case, book in books.items():
        with tempfile.TemporaryDirectory() as directory:
            assert len(store(directory, case, book).snapshot()['accepted']) == len(book['accepted'])
    combinations = [(case, repeat, arm) for case in books for repeat in range(2 if case == 'pension' else 1) for arm in ('A', 'B')]
    random.Random(91313).shuffle(combinations)
    cells, key = [], {}
    for index, (case, repeat, arm) in enumerate(combinations):
        name = f'cell-{index+1}'; book = books[case]
        window, packet = nav.packet(book); navigation = nav.navigation(book)
        description = r.RECOVERY + nav.GUIDANCE + SELECTION + (CONSTRUCTION if arm == 'B' else '')
        prompt = r._proposal_prompt(description, packet)
        prompt += '\nReference navigation: ' + json.dumps(navigation, ensure_ascii=False, separators=(',', ':'))
        prompt += '\nSelected statement aliases: ' + json.dumps(selected[case], separators=(',', ':'))
        save(f'inputs/{name}.json', dict(case=case, window=window, packet=packet, navigation=navigation, selected=selected[case], prompt=prompt))
        cells.append(dict(id=name, case=case, repeat=repeat)); key[name] = arm
    save('books.json', books); save('cells.json', cells); save('arm-key.json', key)
    save('schemas.json', dict(generation=r.proposal_schema(), check=r.CHECK_SCHEMA))
    paths = [HERE / n for n in ('books.json', 'cells.json', 'arm-key.json', 'schemas.json', 'selected.json', 'BASELINE-REVIEW.md')]
    freeze('generation-pins.json', paths + sorted((HERE / 'inputs').glob('*.json')))
    print('Eight paired generation requests frozen; identical data/schema and selected statements.')


def decode(cell, phase):
    data = e._load(HERE / f'inputs/{cell["id"]}.json'); book = e._load(HERE / 'books.json')[cell['case']]
    directory = HERE / 'captures' / cell['id'] / phase
    payload, errors = a._read_response(directory, e._load(directory / 'attempt.json'))
    if phase == 'check':
        proposals = e._load(HERE / f'decoded/{cell["id"]}-generation.json')['prepared']
        judgments, issues = r._decode_checks(payload, errors, proposals, book['document'], data['packet'])
        return dict(payload=payload, errors=errors, judgments=judgments, issues=issues)
    prepared, issues = r._decode_proposals(payload, errors, book['document'], data['window'], data['packet'], 'recovery')
    previews = []
    with tempfile.TemporaryDirectory() as directory:
        current = store(directory, cell['case'], book); before = current.snapshot()
        for p in prepared:
            if p['proposal']['operation'] != 'edit' or p['proposal']['target'] not in data['selected']:
                issues.append(dict(code='outside_selected_edit_scope', proposal_id=p['id']))
            try:
                preview = current.preview(r._action(p, before, e.DEFAULT_MODEL))
                changed = [c for c in preview['accepted'] if c['id'] not in {c['id'] for c in before['accepted']}]
                previews.append(dict(proposal_id=p['id'], replacements=changed))
            except ValueError as error:
                issues.append(dict(code='preview_refused', proposal_id=p['id'], reason=str(error)))
        assert current.snapshot() == before
    return dict(payload=payload, errors=errors, prepared=prepared, issues=issues, previews=previews)


def capture():
    pins('generation-pins.json'); key = e._credential(ENV)
    books = e._load(HERE / 'books.json')
    for cell in e._load(HERE / 'cells.json'):
        data = e._load(HERE / f'inputs/{cell["id"]}.json'); book = books[cell['case']]
        for phase in ('generation', 'check'):
            if phase == 'generation': prompt, schema = data['prompt'], r.proposal_schema()
            else:
                proposals = e._load(HERE / f'decoded/{cell["id"]}-generation.json')['prepared']
                if not proposals:
                    save(f'decoded/{cell["id"]}-check-skipped.json', dict(reason='no_decoded_proposals')); continue
                prompt, schema = r._challenge_prompt(data['packet'], proposals, book['document']), r.CHECK_SCHEMA
            expected = dict(model=e.DEFAULT_MODEL, contents=prompt, config=dict(temperature=0, max_output_tokens=32768,
                response_mime_type='application/json', candidate_count=1, response_json_schema=schema, thinking_config=dict(thinking_level='medium')))
            save(f'expected-requests/{cell["id"]}-{phase}.json', expected)
            directory = HERE / 'captures' / cell['id'] / phase
            if not (directory / 'attempt.json').exists():
                attempts = call(f'{cell["id"]}/{phase}', lambda: a._capture(directory, book['document'], [data['window']], [prompt],
                    schema, e.DEFAULT_MODEL, key, None, max_output_tokens=32768, thinking_level='medium'))
                save(str(directory.relative_to(HERE) / 'attempt.json'), attempts[0])
            result = decode(cell, phase); save(f'decoded/{cell["id"]}-{phase}.json', result)
            print(cell['id'], phase, len(result.get('prepared', result.get('judgments', []))), 'items;', len(result['issues']), 'issues/observations', flush=True)
    save('usage.json', e.recorded_usage(HERE))


def verify():
    pins('source-pins.json'); pins('generation-pins.json')
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        with tempfile.TemporaryDirectory() as directory:
            assert e.replay_run(HERE / 'notice-extract', Path(directory) / 'replay') == e._load(HERE / 'notice-extract/rulebook.json')
        for cell in e._load(HERE / 'cells.json'):
            for phase in ('generation', 'check'):
                output = HERE / f'decoded/{cell["id"]}-{phase}.json'
                if not output.exists(): continue
                assert decode(cell, phase) == e._load(output)
                directory = HERE / 'captures' / cell['id'] / phase
                attempt = e._load(directory / 'attempt.json')
                assert e._load(directory / attempt['request_file']) == e._load(HERE / f'expected-requests/{cell["id"]}-{phase}.json')
    print('Saved extraction, proposals, checks and previews replay exactly; requests match; originals unchanged.')


if __name__ == '__main__':
    {'source': source, 'extract': extract, 'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
