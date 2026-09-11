"""Optional navigation to exact targets in caller-supplied, pinned USLM sources."""
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path

from .core import NS, digest
from .uslm import SourceIndex


def _key(identifier):
    # Reuse the oracle's section spelling policy, preserving pinpoint case.
    from refspec.registry.usc_section_oracle import normalize_section
    parts = identifier.split('/')
    if len(parts) >= 5 and parts[1:3] == ['us', 'usc'] and parts[4].startswith('s'):
        parts[4] = normalize_section(parts[4])
    return tuple(parts)


def _identifier(row):
    if row['kind'] == 'publisher_reference':
        return row['value']
    reading = row.get('reading', {})
    fields = {key for key, value in reading.items() if value and key not in {'authority_type', 'parse_status'}}
    if row['kind'] == 'usc' and fields <= {'usc_title', 'usc_section', 'pinpoint'}:
        if reading.get('usc_title') and reading.get('usc_section'):
            return '/us/usc/t{usc_title}/s{usc_section}'.format(**reading) + ''.join(
                '/' + label for label in reading.get('pinpoint', ()))
    return None


def attach_reference_sources(scan, documents):
    from refspec.registry import uslm, usc_section_oracle
    indexes, by_identifier, sources = {}, defaultdict(list), {}
    for document in documents:
        if 'uslm_source' not in document:
            raise ValueError('Reference sources must be pinned USLM documents')
        source_id = NS + 'xml:' + document['uslm_source']['sha256']
        if source_id in indexes:
            if document != indexes[source_id].document:
                raise ValueError('Conflicting prepared documents for one XML source')
            continue
        index = SourceIndex(document)
        indexes[source_id] = index
        publication = []
        for path, node in index.prepared['nodes'].items():
            parent = index.prepared['nodes'].get(path.rsplit('/', 1)[0], {})
            if parent.get('tag') == 'meta' and 'start' in node:
                if node['tag'] in {'title', 'docNumber', 'docPublicationName', 'publisher', 'created'}:
                    fragment, _ = index.support(path, node, 'publication', include_text=False)
                    publication.append({'field': node['tag'], 'value': document['text'][node['start']:node['end']],
                                        'xml_evidence_refs': [fragment]})
        sources[source_id] = {'document': {k: document[k] for k in ('id', 'sha256', 'title', 'source_url')},
            'publisher_source': index.artifact(), 'publication': publication,
            'xml_fragments': index.fragments, 'records': {}}
        for identifier, nodes in index.identifiers.items():
            by_identifier[_key(identifier)].extend((index, path, node) for path, node in nodes)

    targets = scan.setdefault('targets', {})
    for row in scan['candidates']:
        identifier = _identifier(row)
        if identifier is None:
            continue
        target_ids = list(row.get('resolution', {}).get('target_ids', []))
        unsupported = False
        for index, path, node in by_identifier.get(_key(identifier), ()):
            # Structural context is navigation, not a claim of governing scope.
            container_path = path
            while container_path:
                container = index.prepared['nodes'][container_path]
                if container['tag'] in uslm.UNIT_TAGS:
                    break
                container_path = container_path.rsplit('/', 1)[0]
            if not container_path:
                unsupported = True
                continue  # Broad title/chapter bodies are outside this section lookup.
            target = index.target(path, node)
            target_ids.append(target['id'])
            if target['id'] in targets:
                continue
            record_id = NS + 'reference-record:' + digest([index.source_id, container_path])
            records = sources[index.source_id]['records']
            if record_id not in records:
                fragment, _ = index.support(container_path, container, 'reference_context', include_text=False)
                records[record_id] = {'id': record_id, 'xml_evidence_refs': [fragment],
                    **{k: container[k] for k in ('start', 'end') if k in container},
                    'text': index.document['text'][container['start']:container['end']] if 'start' in container else ''}
            targets[target['id']] = {**target, 'source_id': index.source_id, 'record_id': record_id}
        target_ids = list(dict.fromkeys(target_ids))
        row['resolution'] = {'status': 'target_scope_not_supported' if unsupported else 'located' if len(target_ids) == 1 else 'ambiguous' if target_ids else 'not_in_selected_sources',
                             'target_ids': target_ids, 'edition_match': 'not_established'}
    scan['reference_sources'] = sources
    scan['target_resolution'] = 'exact_targets_in_supplied_sources'
    scan['limitation'] += (' Supplied-source matches locate text, not the edition intended by a citation or its legal applicability. '
                          'Containing sections retain context and notes without asserting inherited conditions. '
                          'Ranges, notes and refused text readings are not reduced to section anchors; external links are not followed recursively.')
    for name, module in [('refspec.registry.uslm.read_text', uslm),
                         ('refspec.registry.usc_section_oracle.normalize_section', usc_section_oracle)]:
        if not any(p['name'] == name for p in scan['parsers']):
            scan['parsers'].append({'name': name, 'version': version('refspec'),
                                   'module_sha256': digest(Path(module.__file__).read_bytes())})
    return scan
