"""Reconstruct the saved inputs, decoding and review/export simulation offline."""
from hashlib import sha256
from pathlib import Path
import tempfile
from unittest.mock import patch
import run as exp
from rulespec_extrapolator import audit as a, extraction as e, refinement as r


def main():
    exp.source.x.pins()
    exp.source.x.pins('execution-pins.json')
    before_fix=e._load(exp.HERE/'generation-pins.json')
    assert sha256((exp.HERE/'run-before-ledger-fix.py').read_bytes()).hexdigest()==before_fix[str(exp.HERE/'run.py')]
    books=e._load(exp.HERE/'books.json')
    report=dict(provider_calls=0,extractions=[],cells=[])
    with patch.object(e,'_create_model',side_effect=AssertionError('Provider access blocked')):
        with tempfile.TemporaryDirectory() as temp:
            for name in exp.source.CASES:
                assert e.replay_run(exp.HERE/'extract'/name,Path(temp)/name)==e._load(exp.HERE/f'extract/{name}/rulebook.json')
                report['extractions'].append(dict(source=name,replayed=True))
        for cell,info in e._load(exp.HERE/'arm-key.json').items():
            data=exp.make_input(books[info['source']],exp.SELECTED[info['source']],info['arm'])
            assert data==e._load(exp.HERE/f'inputs/{cell}.json')
            directory=exp.HERE/f'captures/{cell}/generation'
            attempt=e._load(directory/'attempt.json')
            assert e._load(directory/attempt['request_file'])==data['expected_request']
            payload,errors=a._read_response(directory,attempt)
            decoded=exp.decode_generation(cell,payload,errors)
            assert decoded==e._load(exp.HERE/f'decoded/{cell}-generation.json')
            assert not (exp.HERE/f'captures/{cell}/check').exists()
            # Explicit mechanical rehearsal, not invented provider judgments.
            selection={p['id']:{'verdict':'supported'} for p in decoded['prepared']}
            applied=exp.simulate(cell,selection)
            applied['selection_basis']='All structurally valid proposals for offline mechanical exercise; no checker or semantic approval.'
            assert applied==e._load(exp.HERE/f'applied/{cell}.json')
            report['cells'].append(dict(cell=cell,inputs_reconstructed=True,generation_redecoded=True,
                checker='not_run',review_export_reproduced=True,prepared=len(decoded['prepared'])))
    report['usage']=exp.source.x.usage()
    e._save(exp.HERE/'verification.json',report)
    print('Four native extractions and all 24 generation/review/export results reproduced offline; no checker calls.')


if __name__=='__main__':main()
