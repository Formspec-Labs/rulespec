"""Reader capture closes real replay gaps without requiring optional packages."""
import builtins
import importlib.metadata
from pathlib import Path

import pytest

from test_extraction import offline, raw
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document


def test_runtime_covers_the_readers_missing_from_the_context_experiment():
    pytest.importorskip('refspec')
    pytest.importorskip('spicysearch')
    sources = e._runtime_sources()
    for module in ('rulespec_extrapolator.uslm', 'rulespec_extrapolator.references',
                   'refspec.registry.uslm', 'refspec.registry.xml_text', 'refspec.registry.ecfr', 'refspec.registry.citation_grammar',
                   'refspec.registry.iri_minting', 'spicysearch.identifiers',
                   'spicy_docs.reading.xml', 'spicy_docs.reading.xml_observations',
                   'spicy_docs.sources.uscode', 'spicy_docs.sources.uscode.references'):
        key = module.replace('rulespec_extrapolator.', 'application.').replace('.', '/') + '.py'
        assert sources[key] == Path(e.importlib.util.find_spec(module).origin)
    versions = e._runtime_versions()['packages']
    assert versions['refspec'] == importlib.metadata.version('refspec')
    assert versions['spicysearch'] == importlib.metadata.version('spicysearch')
    assert versions['spicy-docs'] == importlib.metadata.version('spicy-docs')


@pytest.mark.parametrize('key', ['refspec/registry/uslm.py', 'refspec/registry/xml_text.py', 'refspec/registry/ecfr.py',
                                'spicysearch/identifier_normalization.py', 'spicy_docs/reading/xml.py',
                                'spicy_docs/sources/uscode/references.py'])
def test_reader_or_helper_drift_refuses_replay_and_restoring_it_recovers(
        offline, tmp_path, monkeypatch, key):
    pytest.importorskip(key.split('/')[0])
    sources = e._runtime_sources()
    original = sources[key].read_bytes()
    captured = tmp_path / 'reader.py'
    captured.write_bytes(original)
    sources[key] = captured
    monkeypatch.setattr(e, '_runtime_sources', lambda: sources)
    install, models = offline
    run = tmp_path / 'run'
    book = e.extract_run(prepare_document('Staff must log requests.'), run,
                         env_file=install([raw()]))
    monkeypatch.setattr(e, '_create_model', lambda *a, **kw: pytest.fail('Replay called a provider'))
    assert e.replay_run(run, tmp_path / 'unchanged') == book
    captured.write_bytes(original + b'\n# changed reader source\n')
    with pytest.raises(e.ReplayDriftError, match='sources_sha256'):
        e.replay_run(run, tmp_path / 'changed')
    captured.write_bytes(original)
    assert e.replay_run(run, tmp_path / 'restored') == book
    assert models[0].calls == 1


def test_plain_extraction_and_replay_work_without_optional_readers(offline, tmp_path, monkeypatch):
    find_spec, version, import_module = e.importlib.util.find_spec, e.importlib.metadata.version, builtins.__import__

    def without_reader(name, *args, **kwargs):
        root = name.split('.')[0]
        if root in {'refspec', 'spicysearch', 'spicy_docs'}:
            raise ModuleNotFoundError(name=root)
        return find_spec(name, *args, **kwargs)

    def without_version(name):
        if name in {'refspec', 'spicysearch', 'spicy-docs'}:
            raise importlib.metadata.PackageNotFoundError(name)
        return version(name)

    def refuse_reader_import(name, *args, **kwargs):
        assert name.split('.')[0] not in {'refspec', 'spicysearch', 'spicy_docs'}, name
        return import_module(name, *args, **kwargs)

    monkeypatch.setattr(e.importlib.util, 'find_spec', without_reader)
    monkeypatch.setattr(e.importlib.metadata, 'version', without_version)
    monkeypatch.setattr(builtins, '__import__', refuse_reader_import)
    assert not any(k.startswith(('refspec/', 'spicysearch/', 'spicy_docs/')) for k in e._runtime_sources())
    assert not {'refspec', 'spicysearch', 'spicy-docs'} & e._runtime_versions()['packages'].keys()
    install, models = offline
    run = tmp_path / 'plain'
    book = e.extract_run(prepare_document('Staff must log requests.'), run,
                         env_file=install([raw()]))
    assert len(book['accepted']) == 1
    assert e.replay_run(run, tmp_path / 'replayed') == book
    assert models[0].calls == 1


def test_broken_reader_dependency_is_not_reported_as_an_absent_optional_package(monkeypatch):
    find_spec = e.importlib.util.find_spec

    def broken_reader(name, *args, **kwargs):
        if name == 'refspec.registry.uslm':
            raise ModuleNotFoundError(name='broken_dependency')
        return find_spec(name, *args, **kwargs)

    monkeypatch.setattr(e.importlib.util, 'find_spec', broken_reader)
    with pytest.raises(ModuleNotFoundError) as raised:
        e._runtime_sources()
    assert raised.value.name == 'broken_dependency'
