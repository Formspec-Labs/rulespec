"""Run one isolated saved or fresh sample; evaluation answers never enter prompts."""
import argparse
import json
import logging
from pathlib import Path

from rulespec_extrapolator import extraction as e, refinement as r

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('sample', choices=['names', 'photos', 'names-excerpts', 'slopes', 'authorizations', 'marketing'])
    parser.add_argument('--iteration', default='01')
    args = parser.parse_args()
    logging.getLogger('google_genai.models').setLevel(logging.ERROR)
    workspace = REPO / '.tools/refinement-live' / ('benchmark-' + args.iteration) / args.sample
    env_file = Path('/Users/mikewolfd/Work/spicy-regs/.env')
    saved = {'names': 'names-05', 'photos': 'photos-03', 'names-excerpts': 'names-excerpts-03'}
    if args.sample in saved:
        source = ROOT.parent / 'quality-iteration/runs' / saved[args.sample]
        book = e.reprocess_run(source, workspace)
        origin = {'kind': 'saved-extraction', 'source': str(source), 'source_manifest_sha256': e._digest((source / 'manifest.json').read_bytes())}
    else:
        doc = e._load(ROOT / 'fresh-source' / (args.sample + '.json'))
        book = e.extract_run(doc, workspace, env_file=env_file, temperature=0)
        origin = {'kind': 'fresh-extraction', 'source_sha256': doc['sha256'],
                  'expectations_frozen_at': e._load(ROOT / 'fresh-source/freeze.json')['frozen_at']}
    print(json.dumps({'sample': args.sample, 'initial_accepted': len(book['accepted'])}), flush=True)
    output = ROOT / ('runs-' + args.iteration) / args.sample
    result = r.refine_run(workspace, output, env_file=env_file)
    # This experiment receipt sits outside the sealed refinement itself.
    e._save(ROOT / ('receipts-' + args.iteration) / (args.sample + '.json'), {
        'sample': args.sample, 'origin': origin, 'workspace': str(workspace),
        'output': str(output), 'result': result['run'],
        'initial_accepted': len(book['accepted']), 'final_accepted': len(result['rulebook']['accepted'])})
    print(json.dumps({'sample': args.sample, 'status': result['run']['status'],
                     'applied': len(result['changes']), 'final_accepted': len(result['rulebook']['accepted']),
                     'usage': result['run']['usage']}), flush=True)


if __name__ == '__main__':
    main()
