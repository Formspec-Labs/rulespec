"""Check source/wheel integration on real fields and frozen diagnostic text."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from refspec.registry import act_resolution, citation_grammar
from rulespec_extrapolator import references
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

HERE = Path(__file__).resolve().parent
ACTS = Path('/Users/mikewolfd/Work/RefSpec/output/usc-act-index-2026-08-22')
CREDITS = Path('/Users/mikewolfd/Work/RefSpec/output/usc-source-credit-index-2026-08-02')


def save(path, value):
    with path.open('x') as file:
        json.dump(value, file, indent=2, ensure_ascii=False)
        file.write('\n')


args = argparse.ArgumentParser()
args.add_argument('--output-dir', type=Path, required=True)
args.add_argument('--cli', action='store_true')
args = args.parse_args()
out = args.output_dir.resolve()
out.mkdir()
cases = json.loads((HERE/'cases.json').read_text())
selected = [(f'publication-{n}', cases['rows'][n]['authority_text']) for n in (0,1,5,6)]
selected += [(c['id'],c['text']) for c in cases['diagnostics'] if c['id'] in ('repeat','unrelated-division')]
results = {}
for identity, text in selected:
    start = time.perf_counter()
    results[identity] = references.scan_references(prepare_document(text), act_index=ACTS, source_credit_index=CREDITS)
    print(identity, round(time.perf_counter()-start,3), 'seconds', flush=True)
    for item in results[identity]['candidates']:
        for support in item['evidence']:
            assert text[support['start']:support['end']] == support['quote']
        if item['kind']=='act_relative' and item['reading']['pinpoint']:
            assert item['resolution']['pinpoint_mapping']=='not_performed'
assert results['publication-0']['candidates'][0]['resolution']['iri']=='urn:rkaf:us:usc:16:3801'
crop, = results['publication-1']['candidates']
assert crop['reading']['pinpoint']==['b','7','A']
assert crop['resolution']['unresolved_reason']=='act_section_not_classified'
assert results['publication-5']['candidates'][0]['reading']['pinpoint']==['g']
assert not results['publication-6']['candidates']
first,second=results['repeat']['candidates']
assert first['id']!=second['id']
assert results['unrelated-division']['candidates'][0]['reading']['division'] is None
save(out/'scans.json',results)
meta={'provider_calls':0,'python':sys.executable,'cwd':str(Path.cwd()),
      'modules':{m.__name__:{'path':m.__file__,'sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()}
                 for m in (references,citation_grammar,act_resolution)}}
if args.cli:
    fixture=out/'fixture-run';fixture.mkdir()
    doc=prepare_document(cases['rows'][0]['authority_text'])
    run={'id':'urn:test:act-index-cli'}
    book=compile_candidates(doc,[],run)
    for name,value in [('document',doc),('run',run),('rulebook',book)]:save(fixture/(name+'.json'),value)
    options=['--act-index',str(ACTS),'--source-credit-index',str(CREDITS)]
    commands=[['references',str(fixture),*options,'--output',str(out/'cli-references.json')],
              ['discovery-export',str(fixture),*options,'--output',str(out/'cli-discovery.json')],
              ['discovery-export',str(fixture),'--output',str(out/'cli-default.json')]]
    meta['commands']=[]
    for command in commands:
        cmd=[str(Path(sys.executable).with_name('rulespec-understand')),*command]
        completed=subprocess.run(cmd,cwd='/tmp',text=True,capture_output=True,check=True)
        meta['commands'].append({'argv':cmd,'stdout':completed.stdout,'stderr':completed.stderr})
    assert json.loads((out/'cli-references.json').read_text())==results['publication-0']
    exported=json.loads((out/'cli-discovery.json').read_text())
    baseline=json.loads((out/'cli-default.json').read_text())
    row,=exported.pop('reference_scan')['candidates']
    assert row['resolution']==results['publication-0']['candidates'][0]['resolution']
    support,=row['evidence_refs']
    span=exported['evidence'][support['id']]
    assert doc['text'][span['start']:span['end']]=='Food Security Act of 1985, sec 1201'
    exported['evidence']={k:exported['evidence'][k] for k in baseline['evidence']}
    assert exported==baseline
    meta['cli_fixture_origin']='Real saved publication field with an empty manually compiled rulebook; no model extraction'
    meta['cli_checks']='Both commands preserve the mapping and exact evidence; default records/statements unchanged'
save(out/'verification.json',meta)
