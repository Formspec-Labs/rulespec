"""Replay comparison captures with their own manifest, not an extraction manifest.

The original frozen runner mistakenly calls extraction._verify_manifest, which
requires extraction-specific run.json/configuration artifacts. Preserve that runner
and all captures; adapt only the verifier for these comparison-only directories.
"""
from unittest.mock import patch

from rulespec_extrapolator import extraction as e
import run


def verify_comparison(directory):
    manifest = e._load(directory / 'manifest.json')
    artifacts = manifest['artifacts_sha256']
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*')
              if p.is_file() and p != directory / 'manifest.json'}
    assert set(artifacts) == actual
    assert {'attempts.json', 'attempt-0000.json', 'result.json'} <= actual
    for name, digest in artifacts.items():
        assert e._digest((directory / name).read_bytes()) == digest, name
    return manifest


if __name__ == '__main__':
    with patch.object(e, '_verify_manifest', verify_comparison):
        run.execute('replay', None)
