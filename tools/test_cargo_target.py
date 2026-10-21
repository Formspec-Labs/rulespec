"""Exercise real Cargo resolution without compiling or editing shared config."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.cargo_target import target_directory


class CargoTargetTests(unittest.TestCase):
    def test_standalone_and_parent_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            root = parent / "repository"
            (root / "crates").mkdir(parents=True)
            (root / "crates/Cargo.toml").write_text('[workspace]\nmembers = []\n')
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("CARGO_TARGET_DIR", None)
                self.assertEqual(target_directory(root), root / "crates/target")
                (parent / ".cargo").mkdir()
                (parent / ".cargo/config.toml").write_text(
                    '[build]\ntarget-dir = "shared-target"\n'
                )
                self.assertEqual(target_directory(root), parent / "shared-target")
                os.environ["CARGO_TARGET_DIR"] = str(parent / "override-target")
                self.assertEqual(target_directory(root), parent / "override-target")
