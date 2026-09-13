"""Bridge saved candidate comparisons to the actual selected-reading command."""
from copy import deepcopy
import contextlib
import importlib.util
import io
from pathlib import Path
import random
import shutil
import sys

from rulespec_extrapolator import audit as a, cli, extraction as e, refinement as r
from rulespec_extrapolator.review_store import ReviewStore

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / '2026-09-13-fresh-field-completeness'
spec = importlib.util.spec_from_file_location('capture_helpers', HERE.parent / '2026-09-13-fresh-complete-reading/run.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
x.HERE = HERE
SELECTION = dict(leave=2, hazard=0, billing=0, offset=0)


def workspace(source, path):
    r._copy_run(PRIOR / 'extract' / source, path)
    return ReviewStore(path).snapshot()


def prepare():
    assert not (HERE / 'cells.json').exists()
    keys = e._load(PRIOR / 'arm-key.json')
    labels = e._load(PRIOR / 'labels.json')
    cells = [(source, arm, rep) for source in SELECTION for arm in ('A', 'B') for rep in range(2)]
    random.Random(913510).shuffle(cells)
    names, arms, differences = [], {}, []
    for i, (source, arm, rep) in enumerate(cells, 1):
        name = f'cell-{i:02d}'
        prior_cell, = [c for c, v in keys.items() if v['source'] == source and v['arm'] == 'B' and v['repeat'] == rep]
        original = e._load(PRIOR / f'inputs/{prior_cell}.json')
        noop, = [p for p in original['candidates'] if p['proposal']['operation'] == 'no_change']
        if arm == 'A':
            data = deepcopy(original)
            identity = noop['id']
        else:
            book = workspace(source, HERE / 'workspaces' / name)
            selected = [book['accepted'][SELECTION[source]]['id']]
            window, = e.plan_windows(book['document'], 24000)
            packet = r._packet(book, {'book': book, 'labels': {'expected_units': []}}, window, selected)
            comparable = deepcopy(packet)
            for alias, claim in comparable['claims'].items():
                prior_links = original['packet']['claims'][alias]['link_issues']
                if claim['link_issues'] != prior_links:
                    differences.append(dict(cell=name, source=source, alias=alias,
                        field='link_issues', prior=prior_links, current=claim['link_issues']))
                    claim['link_issues'] = prior_links
            assert comparable == original['packet'], source
            aliases = [f'C{SELECTION[source]:04d}']
            candidates = r._reading_candidates(packet, aliases, book['document'])
            prompt = r._challenge_prompt(packet, candidates, book['document'], selected_aliases=aliases,
                navigation=r._reading_navigation(book, packet))
            data = dict(document=book['document'], window=window, packet=packet, candidates=candidates,
                prompt=prompt, selected_ids=selected)
            identity = candidates[0]['id']
        data['expected_request'] = dict(model=e.DEFAULT_MODEL, contents=data['prompt'], config=dict(
            max_output_tokens=32768, response_mime_type='application/json', response_json_schema=r.CHECK_SCHEMA,
            thinking_config=dict(thinking_level='medium')))
        x.save(f'inputs/{name}.json', data)
        arms[name] = dict(source=source, arm=arm, repeat=rep, candidate=identity,
            expected=labels[source + '/' + noop['id']]['expected'], prior_cell=prior_cell)
        names.append(name)
    x.save('arm-key.json', arms)
    x.save('cells.json', names)
    x.save('schema.json', r.CHECK_SCHEMA)
    x.save('runtime.json', e._runtime_versions())
    x.save('packet-differences.json', differences)
    x.freeze('source-pins.json', [p for p in HERE.rglob('*') if p.is_file() and '.sqlite' not in p.name]
        + list(e._runtime_sources().values()) + [Path(cli.__file__), Path(x.__file__)])
    print('Frozen sixteen actual requests; source and meaning match; current link-status differences recorded.')


def check():
    key = e._credential(x.ENV)
    arms = e._load(HERE / 'arm-key.json')
    for name in e._load(HERE / 'cells.json'):
        if (HERE / 'decoded' / f'{name}.json').exists():
            continue
        ledger = e._load(HERE / 'calls.json') if (HERE / 'calls.json').exists() else []
        assert len(ledger) < 16 and sum(c['seconds'] for c in ledger) < 1200
        assert x.usage()['tokens'].get('total_token_count', 0) < 200000
        data = e._load(HERE / f'inputs/{name}.json')
        output = HERE / 'captures' / name
        assert not output.exists(), 'No retries'
        if arms[name]['arm'] == 'A':
            payload, errors, attempt = x.call(name, lambda: r._call(output, data['prompt'], r.CHECK_SCHEMA,
                e.DEFAULT_MODEL, key, None, thinking_level='medium'))
            x.save(f'captures/{name}/attempt.json', attempt)
            capture = output
        else:
            args = ['check', str(HERE / 'workspaces' / name), '--claim', data['selected_ids'][0],
                '--max-chars', '24000', '--env-file', str(x.ENV), '--output', str(output)]
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                x.call(name, lambda: cli.main(args))
            x.save(f'captures/{name}/command.json', dict(args=args, result=stdout.getvalue()))
            step, = e._load(output / 'refinement.json')['steps']
            record = e._load(output / step / 'result.json')
            capture = output / step / 'challenge'
            attempt = record['challenge_attempt']
            payload, errors = a._read_response(capture, attempt)
        if attempt.get('request_file'):
            assert e._load(capture / attempt['request_file']) == data['expected_request']
        judgments, issues = r._decode_checks(payload, errors, data['candidates'], data['document'], data['packet'])
        x.save(f'decoded/{name}.json', dict(payload=payload, errors=errors, judgments=judgments, issues=issues,
            capture=str(capture.relative_to(HERE)), attempt=attempt))
        print(name, len(judgments), 'judgments;', len(issues), 'decode issues', flush=True)
    e._save(HERE / 'usage.json', x.usage())


if __name__ == '__main__':
    {'prepare': prepare, 'check': check}[sys.argv[1]]()
