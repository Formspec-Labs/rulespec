"""Packaged CLI check on a constructed document containing three source fields."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,required=True)
directory = parser.parse_args().output_dir.resolve()
directory.mkdir()
rows = json.loads((HERE/'publication-fields.json').read_text())
text = '\n\n'.join(r['authority_text'] for r in rows)
doc = prepare_document(text,title='Constructed CLI fixture from three published authority fields')
doc['source_map'] = []
offset = 0
for n,row in enumerate(rows):
    if n:
        doc['source_map'].append({'kind':'inserted','start':offset,'end':offset+2,'text':'\n\n'})
        offset += 2
    size = len(row['authority_text'])
    doc['source_map'].append({'kind':'source','start':offset,'end':offset+size,
        'source_id':f"{row['rin']}/{row['publication_id']}/authority/{row['ordinal']}",
        'source_start':0,'source_end':size})
    offset += size
run = {'id':'urn:test:source-credit-cli'}
book = compile_candidates(doc,[],run)
for name,value in [('document',doc),('rulebook',book),('run',run)]:
    (directory/(name+'.json')).write_text(json.dumps(value,indent=2))
options = ['--act-index',str(WORK/'RefSpec/output/usc-act-index-2026-08-22'),
           '--source-credit-index',str(WORK/'RefSpec/output/usc-source-credit-index-2026-08-02')]
commands = []
for name,args in [('references',['references',*options]),('default',['discovery-export']),
                  ('discovery',['discovery-export',*options])]:
    argv = [str(Path(sys.executable).with_name('rulespec-understand')),*args,str(directory),
            '--output',str(directory/(name+'.json'))]
    proc = subprocess.run(argv,cwd='/tmp',capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
    (directory/'commands.json').write_text(json.dumps(commands,indent=2))
    proc.check_returncode()
read = lambda name:json.loads((directory/(name+'.json')).read_text())
scan,default,enriched = read('references'),read('default'),read('discovery')
shared = enriched.pop('reference_scan')
assert len(scan['candidates']) == 3 and not scan['rejected']
assert [r['resolution'].get('iri') for r in scan['candidates']] == [
    'urn:rkaf:us:usc:49:60303',None,'urn:rkaf:us:usc:29:1153']
assert len(scan['candidates'][1]['resolution']['source_credit_targets']) == 4
for original,exported in zip(scan['candidates'],shared['candidates'],strict=True):
    assert original['resolution'] == exported['resolution']
    assert 'evidence' not in exported
    support, = original['evidence']; ref, = exported['evidence_refs']
    assert (ref['id'],ref['roles']) == (support['fragment_id'],[support['field']])
    span = enriched['evidence'][ref['id']]
    assert text[span['start']:span['end']] == support['quote']
enriched['evidence'] = {key:enriched['evidence'][key] for key in default['evidence']}
assert enriched == default
print('Three installed commands passed outside the checkout; two mappings, four visible alternatives, shared evidence, unchanged default records.')
