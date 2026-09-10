"""Provider accounting excludes replay copies and keeps unknown usage explicit."""
import json

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.cli import main


def test_usage_counts_attempts_once_and_does_not_invent_missing_tokens(tmp_path, capsys):
    for i in range(4):
        e._save(tmp_path / f'attempt-{i:04d}.request.json', {})
    response = {'usage_metadata': {'prompt_token_count': 12, 'candidates_token_count': 0,
                 'thoughts_token_count': 4, 'cached': True},
                'candidates': [{'finish_reason': 'STOP'}]}
    e._save(tmp_path / 'attempt-0000.response.json', response)
    e._save(tmp_path / 'attempt-0000.parsed.json', response)
    e._save(tmp_path / 'attempt-0001.response.json', {'usage_metadata': {'prompt_token_count': None},
            'candidates': [{'finish_reason': 'MAX_TOKENS'}]})
    e._save(tmp_path / 'attempt-0002.response.json', {'usage_metadata': None})
    for copied in ('base-run', 'previous', 'frozen'):
        e._save(tmp_path / copied / 'attempt-0000.request.json', {})
        e._save(tmp_path / copied / 'attempt-0000.response.json', response)
    assert e.recorded_usage(tmp_path) == {
        'recorded_requests': 4, 'tokens': {'prompt_token_count': 12,
            'candidates_token_count': 0, 'thoughts_token_count': 4},
        'incomplete_responses': 1, 'responses_without_usage': 2, 'requests_without_response': 1}
    main(['usage', str(tmp_path)])
    result = json.loads(capsys.readouterr().out)
    assert result['recorded_requests'] == 4
    assert result['local_json_bytes'] == sum(p.stat().st_size for p in tmp_path.rglob('*.json'))
    assert 'not a billing invoice' in result['limitation']
