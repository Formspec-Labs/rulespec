"""CLI defaults and overrides reach the public workflow entry points."""
import pytest

from rulespec_extrapolator import audit as a, cli, extraction as e


@pytest.mark.parametrize('stage, expected_level, chars, cap', [
    ('extract', 'low', 24000, 16384), ('audit', 'medium', 3000, 32768),
])
@pytest.mark.parametrize('level', [None, 'low', 'medium', 'high'])
def test_cli_thinking_settings(monkeypatch, tmp_path, stage, expected_level, chars, cap, level):
    source = tmp_path / 'source.json'
    source.write_text('{}')
    monkeypatch.setattr(cli, 'load_document', lambda _: {})
    calls = []

    def run(*args, **kwargs):
        calls.append(kwargs)
        return {'accepted': [], 'rejected': [], 'unresolved': [], 'run': {},
                'status': 'passed', 'review_complete': True,
                'semantic_completeness': 'not_established'}

    monkeypatch.setattr(e if stage == 'extract' else a, stage + '_run', run)
    argv = [stage, str(source), '--output', str(tmp_path / 'output')]
    if level is not None:
        argv += ['--thinking-level', level]
    assert cli.main(argv) == 0
    assert len(calls) == 1
    assert calls[0]['thinking_level'] == (level or expected_level)
    assert calls[0]['max_chars'] == chars
    assert calls[0]['max_output_tokens'] == cap
