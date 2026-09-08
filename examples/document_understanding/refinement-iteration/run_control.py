"""Measure detection and correction of the two existing deliberate defects.

The saved defect description is experiment metadata; it never enters prompts.
"""
import argparse
import json
import logging
from pathlib import Path

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.core import compile_candidates

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('control', choices=['omitted-alternative', 'wrong-exception-target'])
    args = parser.parse_args()
    logging.getLogger('google_genai.models').setLevel(logging.ERROR)
    original = ROOT.parent / 'quality-iteration/negative-controls' / (args.control + '.input.json')
    data = e._load(original)
    workspace = REPO / '.tools/refinement-live/controls' / args.control
    workspace.mkdir(parents=True, exist_ok=False)
    book = compile_candidates(data['source'], data['candidates'], {})
    assert len(book['accepted']) == len(data['candidates']) and not book['rejected']
    for name, value in [('document.json', data['source']), ('rulebook.json', book), ('run.json', {})]:
        e._save(workspace / name, value)
    output = ROOT / 'controls' / args.control
    result = r.refine_run(workspace, output, env_file=Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    receipt = {'control': args.control, 'source_input_sha256': e._digest(original.read_bytes()),
               'result': result['run'], 'output': str(output), 'workspace': str(workspace)}
    e._save(ROOT / 'control-receipts' / (args.control + '.json'), receipt)
    print(json.dumps({'control': args.control, 'status': result['run']['status'],
                      'applied': result['run']['applied_actions'], 'usage': result['run']['usage']}), flush=True)


if __name__ == '__main__':
    main()
