"""Attribute every pinned note-citation delta to grammar or consumer changes."""
import hashlib
import json
import subprocess
import sys
import types
from collections import Counter
from pathlib import Path

ROOT = Path('/Users/mikewolfd/Work/RefSpec')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def module(name, source, path):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    sys.modules[name] = result
    exec(compile(source, str(path), 'exec'), result.__dict__)
    return result


def main():
    head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    inputs, sources = {}, {}
    for kind, filename in [('grammar', 'citation_grammar.py'), ('notes', 'cfr_authority_notes.py')]:
        relative = f'src/refspec/registry/{filename}'
        for version in ('old', 'new'):
            source = (subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{head}:{relative}'])
                      if version == 'old' else (ROOT / relative).read_bytes())
            path = OUT / f'{version}-{filename}'
            path.write_bytes(source)
            inputs[f'{version}_{kind}'] = {'path': str(path), 'sha256': digest(source)}
            sources[f'{version}_{kind}'] = source
    old_grammar = module('_cfr_old_grammar', sources['old_grammar'], OUT / 'old-citation_grammar.py')
    new_grammar = module('_cfr_new_grammar', sources['new_grammar'], OUT / 'new-citation_grammar.py')
    old_notes = module('_cfr_old_notes', sources['old_notes'], ROOT / 'src/refspec/registry/cfr_authority_notes.py')
    hybrid_notes = module('_cfr_hybrid_notes', sources['old_notes'], ROOT / 'src/refspec/registry/cfr_authority_notes.py')
    new_notes = module('_cfr_new_notes', sources['new_notes'], ROOT / 'src/refspec/registry/cfr_authority_notes.py')
    old_notes.parse_authority_citation = old_grammar.parse_authority_citation
    hybrid_notes.parse_authority_citation = new_grammar.parse_authority_citation
    new_notes.parse_authority_citation = new_grammar.parse_authority_citation
    arms = {'old': old_notes, 'grammar_only': hybrid_notes, 'new': new_notes}
    cache_path = ROOT / new_notes.CFR_AUTHORITY_NOTES_ARTIFACT
    payload, cache_digest = new_notes._verify(cache_path)
    records = [json.loads(line) for line in payload.decode().splitlines() if line.strip()]
    oracle = new_notes._default_oracle(cache_path)
    assert oracle is not None
    results, totals = [], {mode: {arm: Counter() for arm in arms} for mode in ('gated', 'no_oracle')}
    memo = {}
    for index, record in enumerate(records):
        text = record['authority_note']
        modes = {}
        for mode, instance in [('gated', oracle), ('no_oracle', None)]:
            readings = {}
            for arm, reader in arms.items():
                key = arm, mode, text
                if key not in memo:
                    memo[key] = sorted((c.family, c.identity, c.span_end or '')
                                       for c in reader.read_note_citations(text, oracle=instance))
                readings[arm] = memo[key]
                totals[mode][arm].update(c[0] for c in readings[arm])
            if readings['old'] != readings['new'] or readings['old'] != readings['grammar_only']:
                modes[mode] = readings
        if modes:
            results.append({'record_index': index, 'record': record, 'readings': modes})
    output = {'head': head, 'inputs': inputs, 'notes_sha256': cache_digest,
              'population': 'All rows in the verified pinned CFR authority-note cache; identity sets per note.',
              'record_count': len(records), 'changed_records': len(results),
              'totals': {mode: {arm: {'families': dict(count), 'total': sum(count.values())}
                                for arm, count in values.items()} for mode, values in totals.items()}}
    (OUT / 'summary.json').write_text(json.dumps(output, indent=2) + '\n')
    (OUT / 'changed-records.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(output, indent=2), flush=True)


if __name__ == '__main__':
    main()
