"""Replay this experiment with its preserved application code, without model calls."""
from pathlib import Path
import runpy
import sys
import rulespec_extrapolator

ROOT = Path(__file__).resolve().parent
# Change this process's package search path only. Dependencies must still match
# the recorded runtime; experiment.py verifies all pinned sources before replay.
rulespec_extrapolator.__path__ = [str(ROOT / 'frozen/application')]
sys.argv = [str(ROOT / 'experiment.py'), 'replay']
runpy.run_path(str(ROOT / 'experiment.py'), run_name='__main__')
