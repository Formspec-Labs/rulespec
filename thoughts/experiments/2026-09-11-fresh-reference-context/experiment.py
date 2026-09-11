"""Use the installed extraction path on paired, saved production windows."""
import json
import importlib
from pathlib import Path
import sys
import time
from uuid import uuid4

from rulespec_extrapolator import extraction as ex
from rulespec_extrapolator.discovery import export_discovery
from context import controls, select_context

HERE = Path(__file__).resolve().parent
load = ex._load
save = ex._save


def prepare():
    out = HERE / 'contexts'
    out.mkdir(exist_ok=False)
    save(out / 'controls.json', controls())
    for case in load(HERE / 'source-selection.json')['selected']:
        name = case['id']
        source = HERE / 'sources' / name
        document = load(source / 'document.json')
        scan = load(source / 'references.json')
        a = load(source / 'windows.json')[case['selected_window_index']]
        assert a == ex.plan_windows(document)[case['selected_window_index']]
        b, decisions = select_context(document, a, scan)
        save(out / (name + '.json'), {'A': a, 'B': b, 'selection': decisions})
        for arm, window in [('A',a),('B',b)]:
            save(out / (name + '.' + arm + '.passages.json'), ex.passage_catalog(document, window))
        print(json.dumps({'case':name, **{k:v for k,v in decisions.items() if k!='decisions'},
                          'additions':[d for d in decisions['decisions'] if d['status']=='added']}),flush=True)


def freeze():
    assert (HERE / 'labels.json').is_file()
    assert not (HERE / 'frozen').exists()
    import context as selection
    checks = controls()
    original = selection.select_context
    selection.select_context = lambda *args, **kwargs: (args[1], {'added_ranges':[], 'added_chars':0})
    try:
        controls()
        raise RuntimeError('Controls failed to detect a no-op selector')
    except AssertionError:
        checks['no_op_mutation_detected'] = True
    finally:
        selection.select_context = original
    for case in load(HERE / 'source-selection.json')['selected']:
        source = HERE / 'sources' / case['id']
        document = load(source / 'document.json')
        saved = load(HERE / 'contexts' / (case['id']+'.json'))
        b, receipt = select_context(document,saved['A'],load(source / 'references.json'))
        assert json.loads(json.dumps({'B':b,'selection':receipt})) == {k:saved[k] for k in ('B','selection')}
        a_catalog = ex.passage_catalog(document,saved['A'])
        b_catalog = ex.passage_catalog(document,b)
        assert {k:v for k,v in a_catalog.items() if k.startswith('F')} == {k:v for k,v in b_catalog.items() if k.startswith('F')}
        assert receipt['added_chars'] <= 12000
    checks['source_context_replay'] = 'passed'
    save(HERE / 'final-controls.json',checks)
    examples, schema = ex.invented_examples(), ex.provider_schema()
    fingerprints = ex._freeze(HERE, examples, schema.schema_dict)
    # The installed generic freezer predates the new source/reference readers.
    # Pin those additional runtime inputs here without changing the experiment's
    # production baseline. Their general capture coverage belongs to R1/R4.
    additional = {}
    for name in ('rulespec_extrapolator.uslm','rulespec_extrapolator.references',
                 'refspec.registry.uslm','refspec.registry.citation_grammar',
                 'refspec.registry.iri_minting','spicysearch.identifiers'):
        path = Path(importlib.import_module(name).__file__)
        raw = path.read_bytes()
        destination = HERE / 'frozen' / 'additional' / (name + '.py')
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(raw)
        additional[name] = {'path':str(path),'sha256':ex._digest(raw)}
    fingerprints['additional_sources'] = additional
    save(HERE / 'fingerprints.json', fingerprints)
    generator = ex._prompt_generator(examples)
    prompts = HERE / 'prompts'; prompts.mkdir(exist_ok=False)
    cells = []
    for index, case in enumerate(load(HERE / 'source-selection.json')['selected']):
        name = case['id']
        document = load(HERE / 'sources' / name / 'document.json')
        windows = load(HERE / 'contexts' / (name + '.json'))
        for arm in 'AB':
            (prompts / (name + '.' + arm + '.txt')).write_text(ex._window_prompt(generator,document,windows[arm]))
        for repeat in range(2):
            order = 'AB' if (index + repeat) % 2 == 0 else 'BA'
            cells.extend({'id':f'{name}.{repeat+1}.{arm}', 'case':name,'arm':arm,'repeat':repeat+1} for arm in order)
    save(HERE / 'cells.json', cells)
    pins = {p.relative_to(HERE).as_posix():ex._digest(p.read_bytes())
            for p in sorted(HERE.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and not p.name.startswith('freeze-')}
    save(HERE / 'prerun-pins.json', pins)
    print(json.dumps({'frozen_files':len(pins),'cells':len(cells),'model':ex.DEFAULT_MODEL}),flush=True)


def run():
    for name, digest in load(HERE / 'prerun-pins.json').items():
        assert ex._digest((HERE / name).read_bytes()) == digest, name
    fingerprints = load(HERE / 'fingerprints.json')
    for name, path in ex._runtime_sources().items():
        assert ex._digest(path.read_bytes()) == fingerprints['sources_sha256'][name], name
    for name, pin in fingerprints['additional_sources'].items():
        assert ex._digest(Path(importlib.import_module(name).__file__).read_bytes()) == pin['sha256'], name
    out = HERE / 'cells'; out.mkdir(exist_ok=False)
    key = ex._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    model = ex._create_model('gemini-3.8-flash', key, ex.provider_schema())
    started = time.monotonic()
    results = []
    for cell in load(HERE / 'cells.json'):
        # Reserve the configured five-minute HTTP timeout inside the stop bound.
        if time.monotonic()-started >= 40*60:
            results.append({**cell,'status':'not_run_time_bound'})
            continue
        directory = out / cell['id']; directory.mkdir(exist_ok=False)
        document = load(HERE / 'sources' / cell['case'] / 'document.json')
        window = load(HERE / 'contexts' / (cell['case']+'.json'))[cell['arm']]
        prompt = (HERE / 'prompts' / (cell['case']+'.'+cell['arm']+'.txt')).read_text()
        save(directory / 'document.json',document)
        save(directory / 'cell.json',cell)
        run = {'id':'urn:rulespec:document-understanding:run:'+str(uuid4()),
               'model':'gemini-3.8-flash','source_sha256':document['sha256'],
               'prompt_sha256':ex._digest(ex.PROMPT),'profile':ex.core.SCHEMA_VERSION,
               'parser_version':ex.PARSER_VERSION,'fingerprints':fingerprints,
               'started_at':ex._now(),'max_chars':24000,'temperature':0,
               'max_output_tokens':16384,'thinking_level':'low','provider_retries':0,
               'experiment_scope':'one saved production window; not whole-document extraction',
               'windows':[{**window,'status':'planned','attempts':[]}]}
        save(directory / 'run.json',run)
        print(json.dumps({'cell':cell['id'],'event':'request_start'}),flush=True)
        attempt = ex._record_window(model,prompt,directory,window,key,thinking_level='low',temperature=0,max_output_tokens=16384)
        parsed = ex._attempt_result(attempt,directory,document,window)
        status = run['windows'][0]
        status.update(status=parsed['status'],attempts=[attempt['id']+'.json'],
                      candidate_count=len(parsed['candidates']),refusal_count=len(parsed['refusals']))
        if attempt['request_file']:
            status['request_sha256'] = ex._digest((directory / attempt['request_file']).read_bytes())
        if attempt['response_file']:
            status['model_version'] = load(directory / attempt['response_file']).get('model_version')
            run['model_version'] = status['model_version']
        run.update(finished_at=ex._now(),candidate_count=len(parsed['candidates']),refusal_count=len(parsed['refusals']))
        try:
            book = ex._finalize(directory,document,parsed['candidates'],parsed['refusals'],run)
            save(directory / 'discovery.json',export_discovery(book,include_references=True))
        except Exception as error:
            save(directory / 'processing-error.json',{'type':type(error).__name__})
        save(directory / 'usage.json',ex.recorded_usage(directory))
        ex._write_manifest(directory)
        result = {**cell,'status':run.get('status','processing_failed'),
                  'parsed_candidates':len(parsed['candidates']),'refusals':len(parsed['refusals']),
                  'usage':ex.recorded_usage(directory)}
        results.append(result)
        save(HERE / 'run-progress.json',results)
        print(json.dumps(result),flush=True)
    save(HERE / 'run-results.json',results)


if __name__ == '__main__':
    {'prepare':prepare,'freeze':freeze,'run':run}[sys.argv[1]]()
