"""Locate Cargo output using its resolved metadata, including parent config."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def target_directory(root: Path = ROOT, cargo: str | None = None) -> Path:
    command = shlex.split(cargo or os.environ.get("CARGO", "cargo"))
    output = subprocess.check_output(
        command + ["metadata", "--manifest-path", str(root / "crates/Cargo.toml"),
                   "--no-deps", "--format-version", "1"],
        cwd=root,
        text=True,
    )
    return Path(json.loads(output)["target_directory"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cargo", default=None)
    args = parser.parse_args()
    print(target_directory(cargo=args.cargo))
