"""Final full-section check through production extraction, audit and discovery export."""
import argparse
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.discovery import export_discovery

ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('run', 'replay'))
    p.add_argument('--env-file', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT, name).read_bytes()) == digest, name
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    if args.mode == 'run':
        book = e.extract_run(e._load(ROOT / 'document.json'), ROOT / 'extraction',
            env_file=args.env_file, max_chars=24000, temperature=0, max_output_tokens=None, thinking_level='low')
        print(e._canonical({'stage':'extraction', 'status':book['run']['status'], 'accepted':len(book['accepted']), 'rejected':len(book['rejected'])}), flush=True)
        report = a.audit_run(book, ROOT / 'audit', env_file=args.env_file, max_chars=24000,
                             max_output_tokens=None, thinking_level='medium')
        e._save(ROOT / 'discovery.json', export_discovery(book))
    else:
        if args.output is None:
            raise ValueError('Replay requires a new output directory')
        args.output.mkdir(parents=True, exist_ok=False)
        book = e.replay_run(ROOT / 'extraction', args.output / 'extraction')
        assert book == e._load(ROOT / 'extraction/rulebook.json')
        report = a.replay_audit(ROOT / 'audit', args.output / 'audit')
        assert report == e._load(ROOT / 'audit/report.json')
        assert export_discovery(book) == e._load(ROOT / 'discovery.json')
    print(e._canonical({'stage':'audit', 'mode':args.mode, 'status':report['status'], 'review_complete':report['review_complete'], 'semantic_completeness':report['semantic_completeness']}), flush=True)


if __name__ == '__main__':
    main()
