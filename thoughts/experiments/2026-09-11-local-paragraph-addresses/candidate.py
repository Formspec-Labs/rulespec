"""Experimental nearest-parent extension; never imported by production.

Reuse RefSpec's existing pinpoint lexer for this comparison. The private import
is a research probe, not a proposed public dependency or a new citation grammar.
Paths are structural guesses; the comparison tests when a unique lookup based
on those guesses would be wrong. No legal relationships are inferred here.
"""
import re

from refspec.registry.citation_grammar import _CFR_PINPOINT_LABEL
from rulespec_extrapolator.core import NS, digest
from rulespec_extrapolator.documents import validate_document

ROMAN = re.compile(r'x{0,3}(?:ix|iv|v?i{0,3})')
DOT = re.compile(r'\s*([a-z]|\d+)\.\s+')
LINE_MARKER = re.compile(r'(?m)^[ \t]*(?:' + _CFR_PINPOINT_LABEL.pattern + r'|[a-z]\.\s+|\d+\.\s+)')


def marker(text):
    dot = DOT.match(text)
    if dot:
        return [dot[1]], True
    labels, position = [], len(text) - len(text.lstrip())
    while match := _CFR_PINPOINT_LABEL.match(text, position):
        labels.append(match[1])
        position = match.end()
        while position < len(text) and text[position].isspace():
            position += 1
    return labels, False


def source_passages(document):
    validate_document(document)
    text = document['text']
    boundaries = {0, len(text)}
    boundaries.update(m.end() for m in re.finditer(r'\r?\n[ \t]*\r?\n', text))
    boundaries.update(m.start() for m in LINE_MARKER.finditer(text))
    boundaries.update(v for s in document['sections'] for v in (s['start'],s['end']))
    bounds = sorted(boundaries)
    parents, style, top, previous_section = {}, None, None, None
    passages = []
    for start,end in zip(bounds,bounds[1:]):
        containing = [s for s in document['sections'] if s['start'] <= start and end <= s['end']]
        section = min(containing, key=lambda s:(s['end']-s['start'],s['id']),default=None)
        section_id = section['id'] if section else ''
        if section_id != previous_section:
            parents,style,top = {},None,None
        previous_section = section_id
        content = text[start:end]
        labels,dotted = marker(content)
        parent_id,path = None,None
        if labels:
            label = labels[0]
            if dotted:
                style,level = 'dotted',0
            elif style == 'dotted':
                level = 1 if label.isdigit() else 2
            else:
                style = 'parenthesized'
                if label.isupper():
                    level = 3
                elif label.isdigit():
                    level = 4 if 3 in parents else 1
                else:
                    next_top = top is not None and len(label) == 1 and ord(label) == ord(top)+1
                    if ROMAN.fullmatch(label) and not next_top and 1 in parents:
                        level = 5 if 4 in parents else 2
                    else:
                        level = 0
                if level == 0:
                    top = label if len(label) == 1 else None
            parent = parents.get(level-1)
            parent_id = parent['id'] if parent else None
            prefix = parent['path'] if parent else ([] if level == 0 else None)
            path = prefix + labels if prefix is not None else None
            parents = {depth:p for depth,p in parents.items() if depth < level}
        identity = NS+'passage:'+digest([document['id'],start,end])
        passage = {'id':identity,'start':start,'end':end,'text_sha256':digest(content),
                   'section_id':section_id,'kind':'list_item' if labels else 'paragraph',
                   'parent_id':parent_id,'structure_method':'experimental-nearest-parent',
                   'path':path,'labels':labels}
        passages.append(passage)
        if labels:
            for offset,label in enumerate(labels):
                parents[level+offset] = {'id':identity,
                    'path':prefix+labels[:offset+1] if prefix is not None else None}
    return passages


def baseline_paths(passages, text):
    paths = {}
    for p in passages:
        labels,dotted = marker(text[p['start']:p['end']])
        path = None
        if p['kind'] == 'list_item' and labels:
            if p['parent_id']:
                prefix = paths.get(p['parent_id'])
            else:
                prefix = [] if dotted or (len(labels[0]) == 1 and labels[0].islower()) else None
            if prefix is not None:
                path = prefix + labels
        paths[p['id']] = path
    return [{**p,'path':paths[p['id']]} for p in passages]
