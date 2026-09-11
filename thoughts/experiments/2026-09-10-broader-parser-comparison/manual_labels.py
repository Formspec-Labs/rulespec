"""Manual assessment entered after reading every blinded raw case; no parser logic."""
import json
from pathlib import Path

root=Path(__file__).parent
cases=json.loads(root.joinpath('cases.json').read_text())['cases']
# Zero-based expected-reference positions that the blinded output actually states.
correct={
 'X':{2:[0],4:[0],5:[0],6:[0],23:[0],24:[0,1]},
 'Y':{2:[0],**{i:[0] for i in range(4,25)},23:[0,1]},
 'W':{i:[0] for i in (2,5,6,10,11,13,19,20,23,24)},
 'Z':{**{i:[0] for i in (2,5,6,10,11,13,21,24)},23:[0,1]},
}
issues={
 ('X',9):('usc|42|1983','Loses note qualifier; section body and its statutory note are distinct targets.'),
 ('Y',27):('federal_register_document|5401-5405','Plausible shape promoted to an unqualified document candidate from an intentionally bare range; identity is ambiguous without context.'),
 ('Y',29):('usc|42|1983','Damaged token 1983affirmed becomes section 1983, with only whole-value partial status.'),
 ('W',9):('usc|42|1983','Loses note qualifier.'),
 ('W',27):('federal_register_document|5401-5405','Ambiguous bare number range becomes a document candidate.'),
 ('W',30):('cfr|1345|1370|','Impossible CFR title appears as an ordinary candidate without a title verdict.'),
 ('Z',4):('cfr|7|15|','15a is shortened to a different part.'),
 ('Z',9):('usc|42|1983','Loses note qualifier.'),
 ('Z',24):('cfr|40|82|','Second section 82.156 becomes an extra part-only reading; loss of requested specificity.'),
 ('Z',28):('cfr|17|15|','Unsupported 15c3-3 is shortened to part 15.'),
 ('Z',29):('usc|42|1983a','Damaged 1983affirmed is shortened to a different section token.'),
}
notes={
 ('X',28):'Title-only observation with exact source text; incomplete, not a parsed section.',
 ('Y',28):'Title-only partial observation; incomplete, not a parsed section.',
 ('X',30):'Invalid-title verdict / fused-digit rejection is retained; excluded from accepted identities.',
 ('Y',31):'Unknown act name and section retained as stated text in failed row, not resolved identity.',
}
duplicates={('X',2):1,('X',4):1,('X',24):1,('Y',12):1,('Y',22):1}
rows=[]
for n,case in enumerate(cases,1):
    row={'case_id':case['id'],'name':case['name'],'expected':case['expected'],'negative':case['negative'],'arms':{}}
    for label in 'WXYZ':
        found=[case['expected'][i] for i in correct[label].get(n,[])]
        row['arms'][label]={'correct':found,'missed':[v for v in case['expected'] if v not in found],
                           'misleading':[], 'duplicate_correct_observations':duplicates.get((label,n),0)}
        # These API families supply no occurrence offset; retain whole-input provenance separately.
        row['arms'][label]['correct_with_native_span']=(found if label in 'XW' or label=='Y' and n in (19,20) else [])
        if (label,n) in issues:
            observed,reason=issues[label,n]
            row['arms'][label]['misleading'].append({'observed':observed,'reason':reason})
        if (label,n) in notes:row['arms'][label]['note']=notes[label,n]
    rows.append(row)
with root.joinpath('blind-assessment.json').open('x') as f:json.dump(rows,f,indent=2)
root.joinpath('assessment-method.md').write_text('''All blinded case outputs were read before this assessment and before opening the arm key.
Labels are manual, revisable judgments about lexical meaning and source evidence.
Field shapes can reveal the implementation, so masking was partial, not an independent blind adjudication.
A missing or false verdict must be read in full raw.json, not inferred from the compact display, which omits false/null values.
Ambiguous bare ranges are not proven non-identifiers: they fail the negative control's no-unqualified-promotion criterion.
Note loss and part-only coarsening are counted as misleading readings separately from successful reference recognition.
Other/failed rows and explicit invalid-title verdicts are diagnostic records, not false accepted identities.
''')
