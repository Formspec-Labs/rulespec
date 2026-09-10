"""Experimental reversible sharing of repeated exact source quotation strings."""
from collections import Counter
from copy import deepcopy
import importlib.util
from pathlib import Path

from rulespec_extrapolator import extraction as e

ROOT=Path(__file__).resolve().parent
KEYS={'quote','quotes','scope_quotes','context_quotes','alternative_quotes','source_quotes',
      'actor_quote','action_quote','object_quote','modality_quote','jurisdiction_quote',
      'choice_quote','logic_text'}
GUIDANCE='''\nQuoted-source encoding: source_quotes stores repeated exact quotation text.
An object {"$quote":"Q..."} in a quote field means the exact string in that catalog.
This shares text only: each original source position, role and identity still
applies independently, even when wording repeats. It does not select a source
occurrence or resolve ambiguous evidence. Read the referenced text as if written
in that field. Return ordinary literal quotation strings in the output schema,
never $quote objects or catalog keys. All other task instructions are unchanged.
'''


def encode(packet, source):
    counts=Counter()
    def count(value,key=''):
        if isinstance(value,dict):
            if '$quote' in value: raise ValueError('Reserved catalog reference key')
            for k,v in value.items(): count(v,k)
        elif isinstance(value,list):
            for v in value: count(v,key)
        elif isinstance(value,str) and key in KEYS and len(value)>=80 and value in source:
            counts[value]+=1
    count(packet)
    aliases={text:f'Q{i:04d}' for i,(text,n) in enumerate(counts.items()) if n>=2}
    def visit(value,key=''):
        if isinstance(value,dict): return {k:visit(v,k) for k,v in value.items()}
        if isinstance(value,list): return [visit(v,key) for v in value]
        if isinstance(value,str) and key in KEYS and value in aliases: return {'$quote':aliases[value]}
        return value
    return {'source_quotes':{alias:text for text,alias in aliases.items()},'packet':visit(packet)}


def decode(value):
    catalog=value['source_quotes']
    if not isinstance(catalog,dict) or any(not isinstance(v,str) for v in catalog.values()):
        raise ValueError('Invalid quote catalog')
    def visit(item):
        if isinstance(item,dict):
            if '$quote' in item:
                if set(item)!={'$quote'} or item['$quote'] not in catalog:
                    raise ValueError('Invalid quote reference')
                return catalog[item['$quote']]
            return {k:visit(v) for k,v in item.items()}
        if isinstance(item,list): return [visit(v) for v in item]
        return item
    return visit(value['packet'])


def checks():
    path=ROOT.parent/'2026-09-10-retrieval-context/compact.py'
    spec=importlib.util.spec_from_file_location('prior_compactor',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    passed=module.counterexamples()
    quote='Staff must retain A and B unless C or D applies. é🙂 '*3
    source=quote+' GAP '+quote
    packet={'focus':{'text':source},'claims':[
        {'id':'one','start':0,'end':len(quote),'quote':quote,'roles':['main'],'summary':'A and B unless C or D'},
        {'id':'two','start':len(quote)+5,'end':len(source),'quote':quote,'roles':['context'],
         'scope_quotes':[quote],'nested':{'quotes':[quote]}}]}
    original=deepcopy(packet);compact=encode(packet,source)
    assert decode(compact)==packet==original
    assert len(compact['source_quotes'])==1
    assert compact['packet']['claims'][0]['start']!=compact['packet']['claims'][1]['start']
    passed+=['nested-roundtrip','same-text-distinct-identities-and-roles','AND-OR-preserved','input-unchanged']
    for malformed in [{'source_quotes':{},'packet':{'$quote':'missing'}},
                      {'source_quotes':{'Q':quote},'packet':{'$quote':'Q','extra':1}},
                      {'source_quotes':{'Q':5},'packet':{'$quote':'Q'}}]:
        try: decode(malformed)
        except ValueError: pass
        else: raise AssertionError('Bad reference accepted')
    passed+=['missing-reference-refused','extra-reference-field-refused','non-string-catalog-refused']
    unknown={'quote':'Invented evidence '*10,'quotes':['Invented evidence '*10]}
    assert encode(unknown,source)['source_quotes']=={}
    passed+=['ungrounded-text-not-promoted']
    return passed
