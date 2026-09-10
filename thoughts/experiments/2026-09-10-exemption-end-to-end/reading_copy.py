"""Shuffle before/after labels for manual reading; retain full source captures."""
import argparse
from pathlib import Path
from secrets import SystemRandom

from rulespec_extrapolator import extraction as e

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('case');args=parser.parse_args()
case=args.case
directory=ROOT/'reading'/case
directory.mkdir(parents=True,exist_ok=False)
versions=['before','after'];SystemRandom().shuffle(versions)
mapping={};outputs=[]
for number,version in enumerate(versions):
    label=f'version-{number+1}';mapping[label]=version
    book=e._load(ROOT/'cases'/case/'refinement'/f'{version}.json')
    aliases={c['id']:f'C{i:04d}' for i,c in enumerate(book['accepted'])}
    records=[]
    for claim in book['accepted']:
        fields={k:claim.get(k) for k in e.core.CANDIDATE_SCHEMA['properties']
                if k not in ['applies_to'] and claim.get(k) not in ('',[],None)}
        records.append(dict(alias=aliases[claim['id']],fields=fields,
            targets=[aliases.get(t,t) for t in claim['target_ids']],
            issues=claim.get('issues',[]),link_issues=claim.get('link_issues',[])))
    outputs.append(dict(label=label,claims=records,rejected=book.get('rejected',[])))
e._save(directory/'mapping.json',mapping)
e._save(directory/'outputs.json',outputs)
print('Saved blinded reading copy for',case)
