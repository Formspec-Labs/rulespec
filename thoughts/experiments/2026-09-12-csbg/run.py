"""One unchanged production extraction of the complete CSBG statutory chapter."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import mkdtemp
import time
from unittest.mock import patch
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from rulespec_extrapolator import discovery, extraction as e
from rulespec_extrapolator.documents import source_passages
from rulespec_extrapolator.uslm import prepare_xml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ARCHIVE = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')


def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def prepare():
    (HERE / 'sources').mkdir(exist_ok=False)
    with ZipFile(ARCHIVE) as z:
        raw = z.read('usc42.xml')
    original = ET.fromstring(raw)
    selected = [n for n in original.iter() if n.get('identifier') == '/us/usc/t42/ch106']
    assert len(selected) == 1
    root = ET.Element(original.tag, original.attrib)
    root.append(selected[0])
    xml = ET.tostring(root, encoding='unicode')
    (HERE / 'sources/csbg.xml').write_text(xml)
    doc = prepare_xml(xml, title='42 USC Chapter 106 — CSBG, release 119-102',
        source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
    save('sources/document.json', doc)
    (HERE / 'sources/csbg.txt').write_text(doc['text'])
    windows = e.plan_windows(doc)
    save('source-receipt.json', dict(archive=str(ARCHIVE),
        archive_sha256=sha256(ARCHIVE.read_bytes()).hexdigest(), member='usc42.xml',
        member_sha256=sha256(raw).hexdigest(), selected_identifier='/us/usc/t42/ch106',
        serialization='Complete ElementTree chapter inside original uscDoc element type; not original XML byte slice',
        source_version='Pinned release 119-102; not asserted to be latest legal text',
        chars=len(doc['text']), passages=len(source_passages(doc)), windows=len(windows),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
        application_file=e.__file__))
    save('windows.json', windows)
    assert len(windows) <= 10
    print(json.dumps({'chars': len(doc['text']), 'windows': len(windows), 'passages':len(source_passages(doc))}))


def verify_pins():
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def extract():
    verify_pins()
    doc = e._load(HERE / 'sources/document.json')
    assert len(e.plan_windows(doc)) <= 10
    start = time.monotonic()
    try:
        e.extract_run(doc, HERE / 'extract', env_file=Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    finally:
        save('capture-time.json', {'seconds':time.monotonic()-start})
    print(json.dumps(e.recorded_usage(HERE / 'extract'), indent=2))


def check():
    verify_pins()
    book = e._load(HERE / 'extract/rulebook.json')
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider setup')):
        replay = e.replay_run(HERE / 'extract', Path(mkdtemp(prefix='rulespec-csbg-')) / 'replay')
        assert replay == book
        exported = discovery.export_discovery(book, include_references=True)
    assert len(exported['records']) == len(source_passages(book['document']))
    save('discovery.json', exported)
    path = REPO / 'packages/rulespec-extrapolator/evaluation/discovery_trial.py'
    spec = importlib.util.spec_from_file_location('existing_trial', path)
    trial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial)
    (HERE / 'discovery_trial.py').write_bytes(path.read_bytes())
    questions = e._load(HERE / 'questions.json')
    for q in questions:
        assert all(s in book['document']['text'] for s in q['required_quotes']), q['id']
    result = trial.run({'csbg':book}, questions)
    for a,b in zip(result['source']['questions'], result['packets']['questions'],strict=True):
        assert [(h['id'],h['score']) for h in a['hits']] == [(h['id'],h['score']) for h in b['hits']]
    save('retrieval.json', result)
    save('verification.json', dict(replay_equal=True, source_passages_retained=len(exported['records']),
        provider_calls=0, pins_unchanged=True, usage=e.recorded_usage(HERE / 'extract')))
    print(json.dumps({m:result[m]['supported_at_3'] for m in ('source','packets','summaries')}))


if __name__ == '__main__':
    {'prepare':prepare, 'extract':extract, 'check':check}[sys.argv[1]]()
