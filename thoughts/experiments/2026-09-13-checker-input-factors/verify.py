"""Reconstruct inputs and decode retained captures with provider access blocked."""
from unittest.mock import patch
import run as exp
from rulespec_extrapolator import audit as a, extraction as e, refinement as r


def main():
    exp.x.pins()
    prepared, checks = exp.make_inputs()
    assert checks == e._load(exp.HERE / 'input-checks.json')
    rows=[]
    with patch.object(e,'_create_model',side_effect=AssertionError('Provider access blocked')):
        for name,info in e._load(exp.HERE/'arm-key.json').items():
            data=e._load(exp.HERE/f'inputs/{name}.json')
            assert data==prepared[info['source'],info['arm']]
            directory=exp.HERE/'captures'/name
            attempt=e._load(directory/'attempt.json')
            assert e._load(directory/attempt['request_file'])==data['expected_request']
            payload,errors=a._read_response(directory,attempt)
            judgments,issues=r._decode_checks(payload,errors,data['candidates'],data['document'],data['packet'])
            assert dict(payload=payload,errors=errors,judgments=judgments,issues=issues)==e._load(exp.HERE/f'decoded/{name}.json')
            rows.append(dict(cell=name,judgments=len(judgments),issues=issues,redecoded=True))
    e._save(exp.HERE/'verification.json',dict(provider_calls=0,inputs_reconstructed=True,cells=rows))
    print('All sixteen inputs/requests reconstructed and responses re-decoded without provider calls.')


if __name__=='__main__':main()
