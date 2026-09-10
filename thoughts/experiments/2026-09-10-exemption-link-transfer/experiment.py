"""Six captured relationship calls on fixed drafts; no automatic adoption."""
import argparse
from copy import deepcopy
from pathlib import Path
import random
import subprocess
import time
from types import ModuleType

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def baseline():
    old = ModuleType('rulespec_extrapolator.baseline_refinement')
    old.__package__ = 'rulespec_extrapolator'
    exec(compile((ROOT / 'baseline/refinement.py').read_text(), 'baseline/refinement.py', 'exec'), old.__dict__)
    original_load = old.load_schema
    old.load_schema = lambda name: e._load(ROOT / 'baseline/meaning.schema.json') if name == 'meaning' else original_load(name)
    return old


def prepare():
    assert not (ROOT / 'design.json').exists()
    for name in ['refinement.py', 'schema_data/meaning.schema.json']:
        data = subprocess.check_output(['git', 'show', 'HEAD:packages/rulespec-extrapolator/src/rulespec_extrapolator/' + name], cwd=REPO)
        path = ROOT / 'baseline' / Path(name).name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    old = baseline()
    books, expected = {}, {}
    for case in ['recordkeeping', 'process-safety']:
        text = (ROOT / 'sources' / f'{case}.txt').read_text()
        # Preserve a contiguous prefix, including all applicability and definitions.
        if case == 'process-safety':
            text = text[:text.index('\n\n(d)')]
        (ROOT / 'sources' / f'{case}.selected.txt').write_text(text)
        doc = prepare_document(text, title=f'{case} official 2025 CFR source',
                               source_url=(ROOT / 'sources' / f'{case}.url').read_text().strip())
        paragraphs = text.split('\n\n')
        def para(needle):
            matches = [p for p in paragraphs if needle in p]
            assert len(matches) == 1, needle
            return matches[0]
        rows = []
        def add(summary, quote, kind, modality, actor=''):
            rows.append(dict(summary=summary, quote=quote, kind=kind, modality=modality, actor=actor))
        if case == 'recordkeeping':
            small = para('If your company had 10 or fewer employees')
            large = para('If your company had more than ten')
            add('Companies with more than ten employees at any time during the last calendar year must keep OSHA injury and illness records unless their establishment is a partially exempt industry under section 1904.2.', large, 'requirement', 'must', 'company')
            add('All employers covered by the OSH Act must report to OSHA work-related fatalities, in-patient hospitalizations of one or more employees, amputations and losses of an eye under section 1904.39.', small, 'requirement', 'must', 'employer')
            add('Companies with ten or fewer employees at all times during the last calendar year do not need to keep OSHA injury and illness records unless OSHA or BLS informs them in writing that records are required under section 1904.41 or 1904.42.', small, 'exemption', 'not_required', 'company')
            add('The recordkeeping requirement for companies with more than ten employees does not apply when their establishment is classified as a partially exempt industry under section 1904.2.', large, 'exemption', 'not_required', 'company')
            expected[case] = [dict(exemption='C0003', targets=['C0000'], forbidden=['C0001','C0002'], reason='Industry exception qualifies the >10 recordkeeping duty, not incident reporting or the different size exemption.'),
                              dict(exemption='C0002', targets=[], forbidden=['C0000','C0001','C0003'], reason='Small-company exemption does not relax the disjoint >10 duty or the expressly retained incident-reporting duty; its own unless condition is a separate supported relationship.')]
        else:
            for needle, summary in [
                ('Employers shall develop a written plan', 'For operations covered by section 1910.119, employers must develop a written plan of action for employee participation.'),
                ('Employers shall consult with employees', 'For operations covered by section 1910.119, employers must consult employees and their representatives on process hazard analyses and the other process safety management elements.'),
                ('Employers shall provide to employees', 'For operations covered by section 1910.119, employers must give employees and their representatives access to process hazard analyses and all other information required by this standard.')]:
                add(summary, para(needle), 'requirement', 'must', 'employer')
            add('Hot work means work involving electric or gas welding, cutting, brazing or similar flame or spark-producing operations.', para('Hot work'), 'definition', 'not_stated')
            start = text.index('(2) This section does not apply to:')
            end = text.index('\n\n(b)', start)
            add('Section 1910.119 does not apply to retail facilities, oil or gas well drilling or servicing operations, or normally unoccupied remote facilities.', text[start:end], 'exemption', 'not_required')
            expected[case] = [dict(exemption='C0004', targets=['C0000','C0001','C0002'], forbidden=['C0003'], reason='The explicit section exclusion governs all three employee-participation duties; the hot-work definition is not a duty relaxed by it.')]
        book = compile_candidates(doc, rows, {'id': 'urn:experiment:exemption-transfer:' + case})
        assert not book['rejected'], book['rejected']
        books[case] = book
        e._save(ROOT / 'inputs' / case / 'constructed-candidates.json', rows)
    books['extinguishers'] = e._load(ROOT.parent / '2026-09-10-relationship-audit/inputs/extinguishers/book.json')
    expected['extinguishers'] = [dict(exemption=alias, targets=['C0000'], forbidden=['C0001'], reason='Distribution-only exemption does not remove maintenance duty.') for alias in ['C0002','C0003']]
    for case, book in books.items():
        window, = e.plan_windows(book['document'], 24000)
        packet = r._packet(book, {'labels': {'expected_units': []}}, window)
        assert packet['omitted_claim_count'] == 0
        e._save(ROOT / 'inputs' / case / 'book.json', book)
        e._save(ROOT / 'inputs' / case / 'packet.json', packet)
        e._save(ROOT / 'inputs' / case / 'prompts.json', {arm: module._proposal_prompt(module.RELATIONSHIPS, packet) for arm,module in [('A',old),('B',r)]})
    for arm, module in [('A',old),('B',r)]:
        e._save(ROOT / 'inputs' / f'schema-{arm}.json', module.proposal_schema())
    e._save(ROOT / 'expected.json', expected)
    pairs = [(case, arm) for case in books for arm in ['A','B']]
    random.Random(20260912).shuffle(pairs)
    fingerprints = e._freeze(ROOT, [], r.proposal_schema())
    paths = [ROOT / 'PLAN.md', Path(__file__), ROOT / 'expected.json', *sorted((ROOT/'sources').glob('*')), *sorted((ROOT/'baseline').glob('*')), *sorted((ROOT/'inputs').rglob('*.json'))]
    e._save(ROOT / 'design.json', dict(cells=[dict(id=f'cell-{i:02d}',case=c,arm=arm) for i,(c,arm) in enumerate(pairs)],
        model=e.DEFAULT_MODEL, temperature=0, thinking_level='medium', max_output_tokens=32768,
        max_calls=6, max_seconds=1200, repeats=1, baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        inputs={str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in paths},
        runtime=e._runtime_versions(), fingerprints=fingerprints))
    print('Inputs, expectations and two arms frozen. No provider calls.', flush=True)


def run(replay=False):
    design = e._load(ROOT / 'design.json')
    for name,digest in design['inputs'].items():
        assert e._digest((ROOT/name).read_bytes()) == digest, name
    assert e._runtime_versions() == design['runtime']
    assert {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()} == design['fingerprints']['sources_sha256']
    old = baseline()
    key = '' if replay else e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    start = time.monotonic()
    for count,cell in enumerate(design['cells']):
        book = e._load(ROOT/'inputs'/cell['case']/'book.json')
        packet = e._load(ROOT/'inputs'/cell['case']/'packet.json')
        prompt = e._load(ROOT/'inputs'/cell['case']/'prompts.json')[cell['arm']]
        schema = e._load(ROOT/'inputs'/f'schema-{cell["arm"]}.json')
        window, = e.plan_windows(book['document'],24000)
        path = ROOT/'cells'/cell['id']
        if replay:
            attempts = e._load(path/'attempts.json')
        else:
            assert count < 6 and time.monotonic()-start < 1200, 'Experiment bound reached'
            attempts = a._capture(path,book['document'],[window],[prompt],schema,design['model'],key,None,max_output_tokens=32768,thinking_level='medium')
            e._save(path/'attempts.json',attempts)
            print(f'Call {count+1}/6: {cell["id"]} {attempts[0]["status"]}',flush=True)
        payload,errors = a._read_response(path,attempts[0])
        decoded = {}
        for arm,module in [('A',old),('B',r)]:
            proposals,issues = module._decode_proposals(payload,errors,book['document'],window,packet,'relationships')
            decoded[arm] = dict(proposals=proposals,issues=issues)
        if replay:
            assert e._load(path/'decoded.json') == decoded
        else:
            e._save(path/'decoded.json',decoded)
        if attempts[0].get('request_file'):
            request=e._load(path/attempts[0]['request_file'])
            assert request['contents'] == prompt
    if replay:
        e._save(ROOT/'replay-checks.json',dict(provider_calls=0,decoding='matched for all six captures and both decoders'))
    print('Replay matched.' if replay else 'Six calls complete; raw manual review pending.',flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['prepare','run','replay'])
    args=parser.parse_args()
    prepare() if args.mode=='prepare' else run(args.mode=='replay')
