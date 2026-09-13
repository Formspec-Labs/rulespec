"""Bounded fresh-source focus diagnostic through existing extraction and recovery."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import time
from unittest.mock import patch
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.uslm import SourceIndex, prepare_xml

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / '2026-09-12-navigation-repair'
spec = importlib.util.spec_from_file_location('navigation_repair', PRIOR / 'run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
ARCHIVE = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
ENV = Path('/Users/mikewolfd/Work/spicy-regs/.env')
CASES = {
    'grants': ('usc15.xml', '/us/usc/t15/s9009a/d', '/us/usc/t15/s9009a/d/1'),
    'pension': ('usc29.xml', '/us/usc/t29/s1083/f/1', '/us/usc/t29/s1083/f/1/B'),
    'reporting': ('usc15.xml', '/us/usc/t15/s637/d/16', '/us/usc/t15/s637/d/16/B'),
}
FOCUS = {**{k: v[2] for k, v in CASES.items()}, 'iep': '/us/usc/t20/s1414/d/1/C'}


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert e._load(path) == value, name
    else:
        e._save(path, value)


def freeze(name, paths):
    save(name, {os.path.relpath(p, HERE): sha256(p.read_bytes()).hexdigest() for p in paths})


def pins(name):
    for path, digest in e._load(HERE / name).items():
        assert sha256((HERE / path).read_bytes()).hexdigest() == digest, path


def sources():
    receipts = []
    with ZipFile(ARCHIVE) as zipped:
        for case, (member, address, _) in CASES.items():
            raw = zipped.read(member)
            root = ET.fromstring(raw)
            nodes = [n for n in root.iter() if n.get('identifier') == address]
            assert len(nodes) == 1
            wrapper = ET.Element(root.tag, root.attrib)
            wrapper.append(nodes[0])
            xml = ET.tostring(wrapper, encoding='unicode')
            doc = prepare_xml(xml, title=address + ' — pinned release 119-102',
                source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
            assert len(e.plan_windows(doc)) == 1
            save(f'sources/{case}.json', doc)
            (HERE / f'sources/{case}.txt').write_text(doc['text'])
            receipts.append(dict(case=case, member=member, member_sha256=sha256(raw).hexdigest(),
                address=address, serialized_sha256=sha256(xml.encode()).hexdigest(), chars=len(doc['text'])))
    save('source-receipt.json', dict(archive=str(ARCHIVE), archive_sha256=sha256(ARCHIVE.read_bytes()).hexdigest(),
        release='119-102', selection='Complete native excerpt serialized within original uscDoc wrapper', cases=receipts))
    save('runtime.json', e._runtime_versions())
    paths = [p for p in HERE.rglob('*') if p.is_file()]
    freeze('pre-extraction-pins.json', paths + list(e._runtime_sources().values()) + [PRIOR / 'run.py'])
    print('Three complete source excerpts frozen; zero model calls.')


def call(name, function):
    pins('pre-extraction-pins.json')
    path = HERE / 'calls.json'
    ledger = e._load(path) if path.exists() else []
    assert name not in {c['name'] for c in ledger}, 'No retries'
    assert len(ledger) < 19 and sum(c['seconds'] for c in ledger) < 1200
    assert e.recorded_usage(HERE)['tokens'].get('total_token_count', 0) < 250000
    started = time.monotonic()
    try:
        return function()
    finally:
        ledger.append(dict(name=name, seconds=time.monotonic() - started))
        e._save(path, ledger)


def extract():
    assert not (HERE / 'extract').exists()
    for case in CASES:
        doc = e._load(HERE / f'sources/{case}.json')
        book = call('extract/' + case, lambda: e.extract_run(doc, HERE / 'extract' / case, env_file=ENV))
        print(case, book['run']['status'], len(book['accepted']), 'accepted', len(book['rejected']), 'rejected', flush=True)


def prepare():
    pins('pre-extraction-pins.json')
    assert not (HERE / 'cells.json').exists()
    books = e._load(HERE / 'books.json')  # Reviewed natural books or explicitly recorded diagnostic copies.
    combinations = [(case, arm) for case in books for arm in ('A', 'B')]
    random.Random(91261).shuffle(combinations)
    cells, arm_key = [], {}
    for index, (case, arm) in enumerate(combinations):
        book = books[case]; source = book['document']['text']; n = len(source)
        owner = SourceIndex(book['document'])
        matches = owner.identifiers[FOCUS[case]]
        assert len(matches) == 1
        _, node = matches[0]
        lo, hi = (0, n) if arm == 'A' else (node['start'], node['end'])
        context = [dict(start=x, end=y) for x, y in ((0, lo), (hi, n)) if x < y]
        window = dict(id=f'focus-{case}', index=0, start=lo, end=hi, context_spans=context)
        spans = sorted([(lo, hi)] + [(s['start'], s['end']) for s in context])
        assert ''.join(source[x:y] for x, y in spans) == source
        packet = r._packet(book, {'labels': {'expected_units': []}}, window)
        assert len(packet['claims']) == len(book['accepted'])
        nav = prior.navigation(book)
        prompt = r._proposal_prompt(r.RECOVERY + prior.GUIDANCE, packet)
        prompt += '\nReference navigation: ' + json.dumps(nav, ensure_ascii=False, separators=(',', ':'))
        name = f'cell-{index + 1}'
        save(f'inputs/{name}.json', dict(case=case, window=window, packet=packet, prompt=prompt, navigation=nav))
        cells.append(dict(id=name, case=case)); arm_key[name] = arm
    save('cells.json', cells); save('arm-key.json', arm_key)
    save('schemas.json', dict(recovery=r.proposal_schema(), check=r.CHECK_SCHEMA))
    paths = [HERE / n for n in ('books.json', 'BASELINE-REVIEW.md', 'case-labels.json', 'cells.json', 'arm-key.json', 'schemas.json')]
    paths += sorted((HERE / 'inputs').glob('*.json'))
    freeze('pre-recovery-pins.json', paths)
    print('Eight recovery requests frozen; full source retained in both arms.')


def decode(cell, phase):
    data = e._load(HERE / f'inputs/{cell["id"]}.json')
    book = e._load(HERE / 'books.json')[cell['case']]
    directory = HERE / 'captures' / cell['id'] / phase
    attempt = e._load(directory / 'attempt.json')
    payload, errors = a._read_response(directory, attempt)
    if phase == 'check':
        proposals = e._load(HERE / f'decoded/{cell["id"]}-recovery.json')['prepared']
        judgments, issues = r._decode_checks(payload, errors, proposals, book['document'], data['packet'])
        return dict(payload=payload, errors=errors, judgments=judgments, issues=issues)
    prepared, issues = r._decode_proposals(payload, errors, book['document'], data['window'], data['packet'], 'recovery')
    previews = []
    with tempfile.TemporaryDirectory() as directory:
        store = prior.temporary_store(directory, book); before = store.snapshot()
        for p in prepared:
            try:
                preview = store.preview(r._action(p, before, e.DEFAULT_MODEL))
                changed = [c for c in preview['accepted'] if c['id'] not in {c['id'] for c in before['accepted']}]
                previews.append(dict(proposal_id=p['id'], replacements=changed))
            except ValueError as error:
                issues.append(dict(code='preview_refused', proposal_id=p['id'], reason=str(error)))
        assert before == store.snapshot()
    return dict(payload=payload, errors=errors, prepared=prepared, issues=issues, previews=previews)


def capture():
    pins('pre-recovery-pins.json')
    assert not (HERE / 'captures').exists()
    key = e._credential(ENV)
    books = e._load(HERE / 'books.json')
    for cell in e._load(HERE / 'cells.json'):
        data = e._load(HERE / f'inputs/{cell["id"]}.json'); book = books[cell['case']]
        for phase in ('recovery', 'check'):
            if phase == 'recovery':
                prompt, schema = data['prompt'], r.proposal_schema()
            else:
                proposals = e._load(HERE / f'decoded/{cell["id"]}-recovery.json')['prepared']
                if not proposals:
                    save(f'decoded/{cell["id"]}-check-skipped.json', dict(reason='no_decoded_proposals')); continue
                prompt, schema = r._challenge_prompt(data['packet'], proposals, book['document']), r.CHECK_SCHEMA
            directory = HERE / 'captures' / cell['id'] / phase
            attempts = call(cell['id'] + '/' + phase, lambda: a._capture(directory, book['document'], [data['window']],
                [prompt], schema, e.DEFAULT_MODEL, key, None, max_output_tokens=32768, thinking_level='medium'))
            save(str(directory.relative_to(HERE) / 'attempt.json'), attempts[0])
            result = decode(cell, phase)
            save(f'decoded/{cell["id"]}-{phase}.json', result)
            print(cell['id'], phase, len(result.get('prepared', result.get('judgments', []))), 'items;', len(result['issues']), 'issues/observations', flush=True)
    save('usage.json', e.recorded_usage(HERE))


def verify():
    pins('pre-extraction-pins.json'); pins('pre-recovery-pins.json')
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected model call')):
        for cell in e._load(HERE / 'cells.json'):
            for phase in ('recovery', 'check'):
                path = HERE / f'decoded/{cell["id"]}-{phase}.json'
                if path.exists():
                    assert decode(cell, phase) == e._load(path)
    print('All recorded recovery/check responses replay exactly; pinned inputs unchanged.')


if __name__ == '__main__':
    {'sources': sources, 'extract': extract, 'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
