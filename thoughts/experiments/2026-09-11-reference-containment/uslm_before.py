"""Use RefSpec's publisher reader with Rulespec's existing document evidence."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path

from .core import NS, _evidence, digest, sparse
from .documents import prepare_document, validate_document


def _read(xml):
    try:
        from refspec.registry.uslm import read_text
    except ImportError as error:
        raise RuntimeError('USLM preparation requires the verified RefSpec wheel; see the extractor README.') from error
    result = read_text(xml.encode('utf-8'))
    source_id = NS + 'document:' + digest(result['source_text'])
    for part in result['source_map']:
        if part['kind'] == 'source':
            part['source_id'] = source_id
    return result


def prepare_uslm(xml, *, title='USLM document', source_url=''):
    """Pin original XML once; models receive the prepared text and passage catalog."""
    prepared = _read(xml)
    from refspec.registry.uslm import UNIT_TAGS
    sha = digest(xml)
    sections = [{'id': NS + 'section:' + digest([sha, path]),
                 'label': node.get('identifier', node['tag']),
                 'start': node['start'], 'end': node['end']}
                for path, node in prepared['nodes'].items()
                if node['tag'] in UNIT_TAGS and 'start' in node]
    document = prepare_document(prepared['text'], title=title, source_url=source_url,
                                sections=sorted(sections, key=lambda s: (s['start'], -s['end'])))
    document['source_map'] = prepared['source_map']
    document['uslm_source'] = {'xml': xml, 'sha256': sha, 'preparation': prepared['method']}
    return validate_document(document)


def read_uslm(document):
    """Replay the saved transformation before trusting publisher coordinates."""
    source = document['uslm_source']
    if not isinstance(source.get('xml'), str) or digest(source['xml']) != source.get('sha256'):
        raise ValueError('USLM source does not match its pinned digest')
    prepared = _read(source['xml'])
    if source.get('preparation') != prepared['method']:
        raise ValueError('USLM preparation version differs from the installed reader')
    if document['text'] != prepared['text'] or document.get('source_map') != prepared['source_map']:
        raise ValueError('Prepared text or source map differs from the pinned USLM source')
    return prepared


def attach_publisher_links(document, scan, passages):
    """Add native XML occurrences and shared targets to the existing scan result."""
    from refspec.registry import uslm
    prepared = read_uslm(document)
    source = document['uslm_source']
    source_id = NS + 'xml:' + source['sha256']
    source_parts = [p for p in document['source_map'] if p['kind'] == 'source']
    starts, ends = [p['start'] for p in source_parts], [p['end'] for p in source_parts]
    passage_starts, passage_ends = [p['start'] for p in passages], [p['end'] for p in passages]
    fragments, targets, publisher_rows = {}, {}, []
    identifiers, by_start = defaultdict(list), defaultdict(list)
    for path, node in prepared['nodes'].items():
        if node.get('identifier'):
            identifiers[node['identifier']].append((path, node))

    def support(path, node, field):
        fragment_id = NS + 'xml-fragment:' + digest([source_id, path])
        fragments.setdefault(fragment_id, {'@id': fragment_id, '@type': 'rkaf:SourceFragment',
            'oa:hasSource': source_id, 'oa:hasSelector': [{'@type': 'oa:XPathSelector', 'rdf:value': path}],
            'rkaf:selectorKind': ['oa:XPathSelector'], 'rkaf:sourceArtifactDigest': 'sha256:' + source['sha256'],
            'rkaf:fragmentContentDigest': 'sha256:' + digest(prepared['source_text'][node['source_start']:node['source_end']])})
        evidence = []
        if 'start' in node:
            for part in source_parts[bisect_right(ends, node['start']):bisect_left(starts, node['end'])]:
                start, end = max(part['start'], node['start']), min(part['end'], node['end'])
                exact = _evidence(document, document['text'][start:end], field, start, end)
                if exact is None:
                    raise ValueError('Publisher text evidence does not resolve in the prepared source')
                evidence.append(exact)
        return fragment_id, evidence

    root_id = prepared['nodes']['/*[1]'].get('identifier', '')
    title = root_id.removeprefix('/us/usc/t').split('/')[0] if root_id.startswith('/us/usc/t') else ''
    skipped = Counter()
    for native in uslm.iter_edges(source['xml'].encode('utf-8'), title, skipped, include_source_path=True):
        path = native['sourceXPath']
        node = prepared['nodes'][path]
        xml_fragment, evidence = support(path, node, 'reference')
        target_ids = []
        for target_path, target in identifiers.get(native['href'], ()):
            target_id = NS + 'reference-target:' + digest([source_id, target_path])
            target_ids.append(target_id)
            if target_id not in targets:
                fragment, target_evidence = support(target_path, target, 'reference_target')
                targets[target_id] = {'id': target_id, 'value': native['href'],
                    **{k: target[k] for k in ('start', 'end') if k in target},
                    'xml_evidence_refs': [fragment], 'evidence': target_evidence,
                    'text_status': 'available' if target_evidence else 'no_visible_text'}
        row = {'id': NS + 'reference:' + digest([xml_fragment, native['href']]),
               'kind': 'publisher_reference', 'value': native['href'],
               'reading': sparse({k: v for k, v in native.items() if k not in {'href', 'sourceXPath'}}),
               'xml_evidence_refs': [xml_fragment], 'evidence': evidence,
               'record_ids': [p['id'] for p in passages[bisect_right(passage_ends, node['start']):bisect_left(passage_starts, node['end'])]] if 'start' in node else [],
               'resolution': {'status': 'located' if len(target_ids) == 1 else 'ambiguous' if target_ids else 'not_in_selected_source',
                              'target_ids': target_ids},
               'text_status': 'available' if evidence else 'no_visible_text'}
        publisher_rows.append(row)
        if 'start' in node:
            by_start[node['start']].append((node, row))

    # Merge only a uniquely associated same-start reading. Prefix readings retain
    # their own exact evidence and qualifications. Other overlaps stay separate;
    # neither source proximity nor a normalized value proves they are one mention.
    for group in ('candidates', 'rejected'):
        remaining = []
        for row in scan[group]:
            evidence = row.get('evidence', [])
            primary = evidence[0] if evidence else None
            matches = [(node, parent) for node, parent in by_start.get(primary['start'], ())
                       if primary['end'] <= node['end']] if primary else []
            if len(matches) != 1:
                remaining.append(row)
                continue
            _, parent = matches[0]
            parent.setdefault('text_readings', []).append({'disposition': group,
                **{k: v for k, v in row.items() if k not in {'id', 'record_ids'}}})
        scan[group] = remaining
    scan['candidates'].extend(publisher_rows)
    scan['candidates'].sort(key=lambda row: (row['evidence'][0]['start'] if row.get('evidence') else len(document['text']), row['id']))
    scan['publisher_source'] = {'@id': source_id, '@type': 'rkaf:Artifact',
        'rkaf:hasArtifactIdentifier': source_id, 'rkaf:artifactIdentifierScheme': 'rkaf:hash-sha256',
        'rkaf:hasContentDigest': 'sha256:' + source['sha256'], 'dcterms:format': 'application/xml'}
    scan['xml_fragments'], scan['targets'], scan['publisher_skipped'] = fragments, targets, dict(skipped)
    scan['parsers'].extend({'name': 'refspec.registry.uslm.' + name, 'version': version('refspec'),
                            'module_sha256': digest(Path(uslm.__file__).read_bytes())}
                           for name in ('iter_edges', 'read_text'))
    scan['supported_kinds'] = sorted(set(scan['supported_kinds']) | {'publisher_reference'})
    scan['target_resolution'] = 'publisher_targets_and_named_act_identity' if scan.get('indexes') else 'publisher_targets_in_supplied_xml'
    scan['limitation'] += (' Publisher links retain their native reading and context; text readings are separate observations, '
                          'not agreement checks. Targets are looked up only in the supplied XML, not the whole law or another edition. '
                          'Readable text preserves source order and cell boundaries, not full visual table layout.')
    return scan
