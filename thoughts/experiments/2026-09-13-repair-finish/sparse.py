"""Experimental sparse edits; reuse every existing CUE field and native validator."""
from copy import deepcopy
from jsonschema import Draft202012Validator, ValidationError
from rulespec_extrapolator import refinement as r


def schema():
    result = r.proposal_schema()
    complete = result['properties']['proposals']['items']
    addition = deepcopy(complete)
    addition['properties']['operation']['enum'] = ['add']
    edit = deepcopy(complete)
    edit['properties']['operation']['enum'] = ['edit']
    edit['required'] = [k for k in edit['required'] if k not in {'quote', 'qualifies'}]
    edit['properties']['fields']['required'] = []
    result['properties']['proposals']['items'] = {'anyOf': [addition, edit]}
    return result


def expand(payload, packet):
    """Copy omitted edit fields; explicit values still face all native checks."""
    result = deepcopy(payload)
    issues = []
    if not isinstance(result, dict) or not isinstance(result.get('proposals'), list):
        return result, issues
    item_schema = schema()['properties']['proposals']['items']
    names = r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
    for i, item in enumerate(result['proposals']):
        try:
            Draft202012Validator(item_schema).validate(item)
            if item['operation'] != 'edit':
                continue
            old = packet['claims'][item['target']]
            item['fields'] = {**{k: deepcopy(old[k]) for k in names}, **item['fields']}
            item.setdefault('quote', old['quote'])
            item.setdefault('qualifies', deepcopy(old['target_ids']))
        except (KeyError, TypeError, ValidationError) as exc:
            issues.append(dict(index=i, code='sparse_proposal_refused', reason=str(exc)))
            # Preserve list positions so native proposal IDs still name the raw
            # proposal. An invalid item cannot become valid through expansion.
            result['proposals'][i] = {'invalid_sparse_proposal': True}
    return result, issues
