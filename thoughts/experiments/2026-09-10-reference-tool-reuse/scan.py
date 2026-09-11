"""Scan a pinned Rulespec document with the installed reference tools.

Produces optional reference candidates for inspection, not accepted rule links.
No source path injection, service, model call, or Rulespec validation dependency.
"""
import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from refspec.registry.citation_grammar import find_cfr_citations
from spicysearch.cfr_citations import extract_citations, extract_usc_citations


def scan(document):
    text = document['text']
    assert sha256(text.encode()).hexdigest() == document['sha256'], 'Source digest changed'
    readings = [asdict(c) for c in find_cfr_citations(text)]
    for reading in readings:
        assert text[reading['start']:reading['end']] == reading['text']
    return {
        'document': document,
        'reference_candidates': readings,
        'comparison_only': {
            'spicysearch_mode': 'strict',
            'spicysearch_cfr': [asdict(c) for c in extract_citations(text, strict=True, keep_rejected=True)],
            'spicysearch_usc': [asdict(c) for c in extract_usc_citations(text, strict=True, keep_rejected=True)],
        },
        'target_resolution': 'not_performed',
        'coverage': 'not_established',
        'limitation': 'Explicit citations only. Local paragraph addresses and missing titles remain unsupported. '
                      'SpicySearch readings are comparison data, not fallback identities. '
                      'A parsed reference does not establish target existence or applicability.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    document = json.loads(args.document.read_text())
    result = scan(document.get('document', document))
    with args.output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(args.output), 'candidates': len(result['reference_candidates'])}))
