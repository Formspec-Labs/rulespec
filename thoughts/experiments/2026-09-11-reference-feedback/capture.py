"""Retain normal-command observations from constructed review runs, without models."""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys
import sysconfig
from tempfile import TemporaryDirectory

from rulespec_extrapolator import cli, reference_feedback
from rulespec_extrapolator.core import canonical, compile_candidates
from rulespec_extrapolator.documents import load_document, prepare_document

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODE = sys.argv[1]
SUFFIX = sys.argv[2] if len(sys.argv) > 2 else ''
if MODE != 'source':
    assert Path(reference_feedback.__file__).is_relative_to(Path(sysconfig.get_paths()['purelib']))
fixture = ROOT / 'packages/rulespec-extrapolator/tests/fixtures/cfr-reverse-title.xml'
selected = json.loads((HERE.parent / '2026-09-11-cfr-range-prose/publisher-selection.json').read_text())['cases'][0]
inputs = [('repeated', load_document(fixture), '--candidate', 2),
          ('refused', prepare_document(selected['text']), '--rejected', 0)]
results = []
for name, document, flag, index in inputs:
    with TemporaryDirectory(prefix='rulespec-reference-feedback-') as directory:
        run = Path(directory)
        book = compile_candidates(document, [], {})
        for filename, value in {'document.json':document,'run.json':{},'rulebook.json':book}.items():
            (run/filename).write_text(canonical(value))
        scan_file, discovery_file = run/'scan.json', run/'discovery.json'
        cli.main(['references', str(run), '--output', str(scan_file)])
        scan = json.loads(scan_file.read_text())
        stdout = StringIO()
        with redirect_stdout(stdout):
            cli.main(['reference-feedback', str(run), '--scan', str(scan_file), flag, str(index),
                      '--expected-revision', '0', '--actor', 'Experiment fixture reviewer',
                      '--rationale', 'Constructed feedback: check this selected reading.'])
        response = json.loads(stdout.getvalue())
        cli.main(['discovery-export',str(run),'--references','--output',str(discovery_file)])
        discovery = json.loads(discovery_file.read_text())
        reported, = response['event']['observations']
        exported, = discovery['enrichment_issues']
        assert {k:v for k,v in exported.items() if k!='event_id'} == reported
        assert exported['event_id'] == response['event']['id']
        assert not discovery['statements']
        entry={'case':name,'document':document,'scan':scan,'response':response,'discovery':discovery}
        if name == 'repeated':
            assert scan['candidates'][0]['value'] == scan['candidates'][2]['value']
            assert scan['candidates'][0]['id'] != reported['reference']['id']
            changed = deepcopy(scan)
            changed['candidates'][2]['reading']['cfr_part']='1911'
            other=reference_feedback.reference_observation(document,changed,'candidates',2,message='Constructed changed-reading control.')
            entry['id_only_control']={'before':reported['reference']['id'],'after':other['reference']['id']}
            assert entry['id_only_control']['before']==entry['id_only_control']['after']
            assert reported['reference']['reading'] != other['reference']['reading']
            entry['changed_reading_control']=other
        else:
            assert reported['reference']['code']=='cfr_range_end_unread'
        results.append(entry)
output={'mode':MODE,'python':sys.executable,'model_calls':0,
        'fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),
        'modules':{name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                   for name,module in [('cli',cli),('reference_feedback',reference_feedback)]},
        'cases':results}
with (HERE/(MODE+SUFFIX+'-commands.json')).open('x') as stream:
    json.dump(output,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'mode':MODE,'cases':len(results),'comments_exported':True,'model_calls':0}))
