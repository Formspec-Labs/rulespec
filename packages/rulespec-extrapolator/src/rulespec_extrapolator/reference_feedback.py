"""Capture a reported reference reading through existing review observations."""
from copy import deepcopy

from .core import _evidence, digest
from .documents import validate_document


def reference_observation(document, scan, collection, index, *, message):
    """Pin what was challenged; do not rescan, approve or correct its meaning."""
    validate_document(document)
    if not isinstance(message, str) or not message.strip():
        raise ValueError('Describe what appears wrong, missing or disputed in this reading.')
    if not isinstance(scan, dict) or scan.get('schema_version') != 'document-references/2':
        raise ValueError('Use a saved references command output for reference feedback.')
    if any(scan.get('document', {}).get(key) != document[key] for key in ('id', 'sha256')):
        raise ValueError('The reference scan belongs to a different document.')
    if (collection not in {'candidates', 'rejected'} or type(index) is not int
            or not isinstance(scan.get(collection), list) or not 0 <= index < len(scan[collection])):
        raise ValueError('Select an existing candidate or rejected reference by its zero-based index.')
    row = scan[collection][index]
    if not isinstance(scan.get('parsers'), list) or not scan['parsers']:
        raise ValueError('The reference scan is missing its reader provenance.')
    readings = [row, *row.get('text_readings', [])]
    for reading in readings:
        for support in reading.get('evidence', []):
            if (not isinstance(support, dict)
                    or type(support.get('start')) is not int or type(support.get('end')) is not int
                    or not isinstance(support.get('field'), str) or not isinstance(support.get('quote'), str)
                    or support != _evidence(document, support.get('quote'), support.get('field'),
                                            support.get('start'), support.get('end'))):
                raise ValueError('Reference evidence differs from the pinned source or its positions.')

    # Keep the supplying reader/index pins and only the selected target bodies.
    # All selected source metadata matters when lookup found no target.
    context = {key: scan[key] for key in ('parsers', 'indexes', 'publisher_source') if key in scan}
    target_ids = {identity for reading in readings
                  for identity in reading.get('resolution', {}).get('target_ids', [])}
    try:
        targets = {identity: scan['targets'][identity] for identity in sorted(target_ids)}

        def fragments(bucket, values):
            identities = {identity for value in values for identity in value.get('xml_evidence_refs', [])}
            return {identity: bucket['xml_fragments'][identity] for identity in sorted(identities)}

        primary = fragments(scan, readings + [t for t in targets.values() if 'source_id' not in t])
        if primary:
            context['xml_fragments'] = primary
        if targets:
            context['targets'] = targets
        by_source = {}
        for target in targets.values():
            by_source.setdefault(target.get('source_id'), []).append(target)
        sources = {}
        for identity, source in scan.get('reference_sources', {}).items():
            selected = by_source.get(identity, [])
            records = {t['record_id']: source['records'][t['record_id']] for t in selected}
            entry = {key: source[key] for key in ('document', 'publisher_source', 'publication')}
            if source.get('issues'):
                entry['issues'] = source['issues']
            if records:
                entry['records'] = records
            linked = fragments(source, selected + list(records.values()) + source['publication'] + source.get('issues', []))
            if linked:
                entry['xml_fragments'] = linked
            sources[identity] = entry
        if any(t.get('source_id') not in sources for t in targets.values() if 'source_id' in t):
            raise KeyError('source_id')
        if sources:
            context['reference_sources'] = sources
    except KeyError as error:
        raise ValueError('The reference scan is missing linked target or source context.') from error
    return deepcopy({'code': 'reference_feedback', 'message': message.strip(), 'document': scan['document'],
                     'scan_sha256': digest(scan), 'disposition': collection,
                     'reference': row, 'context': context})
