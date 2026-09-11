"""Use RefSpec's publisher reader with Rulespec's existing document evidence."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path

from .core import NS, _evidence, digest, sparse
from .documents import prepare_document, validate_document


def _read(xml):
    try:
        from refspec.registry.xml_text import read_text
    except ImportError as error:
        raise RuntimeError('XML preparation requires the verified RefSpec wheel; see the extractor README.') from error
    result = read_text(xml.encode('utf-8'))
    source_id = NS + 'document:' + digest(result['source_text'])
    for part in result['source_map']:
        if part['kind'] == 'source':
            part['source_id'] = source_id
    return result


def prepare_xml(xml, *, title=None, source_url=''):
    """Pin original XML once; models receive the prepared text and passage catalog."""
    prepared = _read(xml)
    title = title or ('eCFR document' if prepared['method'].startswith('ecfr-') else 'USLM document')
    sha = digest(xml)
    sections = [{'id': NS + 'section:' + digest([sha, path]),
                 'label': node.get('identifier', node.get('attributes', {}).get('N', node['tag'])),
                 'start': node['start'], 'end': node['end']}
                for path, node in prepared['nodes'].items()
                if _is_unit(node) and 'start' in node]
    document = prepare_document(prepared['text'], title=title, source_url=source_url,
                                sections=sorted(sections, key=lambda s: (s['start'], -s['end'])))
    document['source_map'] = prepared['source_map']
    key = 'ecfr_source' if prepared['method'].startswith('ecfr-') else 'uslm_source'
    document[key] = {'xml': xml, 'sha256': sha, 'preparation': prepared['method']}
    return validate_document(document)


def _is_unit(node):
    from refspec.registry.uslm import UNIT_TAGS
    return node['tag'] in UNIT_TAGS or node.get('attributes', {}).get('TYPE') == 'SECTION'


def xml_source(document):
    sources = [document[key] for key in ('uslm_source', 'ecfr_source') if key in document]
    if len(sources) != 1:
        raise ValueError('Expected one pinned USLM or eCFR XML source')
    return sources[0]


def read_xml(document):
    """Replay the saved transformation before trusting publisher coordinates."""
    source = xml_source(document)
    if not isinstance(source.get('xml'), str) or digest(source['xml']) != source.get('sha256'):
        raise ValueError('XML source does not match its pinned digest')
    prepared = _read(source['xml'])
    if ('ecfr_source' in document) != prepared['method'].startswith('ecfr-'):
        raise ValueError('XML source format differs from its saved field')
    if source.get('preparation') != prepared['method']:
        raise ValueError('XML preparation version differs from the installed reader')
    if document['text'] != prepared['text'] or document.get('source_map') != prepared['source_map']:
        raise ValueError('Prepared text or source map differs from the pinned XML source')
    return prepared


class SourceIndex:
    """One verified native XML source, shared by links and external lookup."""

    def __init__(self, document):
        self.document = validate_document(document)
        self.prepared = read_xml(document)
        self.source = xml_source(document)
        self.source_id = NS + 'xml:' + self.source['sha256']
        self.fragments, self.targets = {}, {}
        self.identifiers = defaultdict(list)
        self.unit_paths = {path for path, node in self.prepared['nodes'].items() if _is_unit(node)}
        self.addresses, self.issues = {}, []
        for path, node in self.prepared['nodes'].items():
            if node.get('identifier'):
                self.addresses[path] = node['identifier']
        if 'ecfr_source' in document:
            from refspec.registry.ecfr import section_addresses
            self.addresses, self.issues = section_addresses(self.prepared)
        for path, identifier in self.addresses.items():
            self.identifiers[identifier].append((path, self.prepared['nodes'][path]))
        self.source_parts = [p for p in document['source_map'] if p['kind'] == 'source']
        self.starts = [p['start'] for p in self.source_parts]
        self.ends = [p['end'] for p in self.source_parts]

    def artifact(self):
        return {'@id': self.source_id, '@type': 'rkaf:Artifact',
                'rkaf:hasArtifactIdentifier': self.source_id,
                'rkaf:artifactIdentifierScheme': 'rkaf:hash-sha256',
                'rkaf:hasContentDigest': 'sha256:' + self.source['sha256'],
                'dcterms:format': 'application/xml'}

    def support(self, path, node, field, *, include_text=True):
        document, prepared, source = self.document, self.prepared, self.source
        source_id, fragments = self.source_id, self.fragments
        source_parts, starts, ends = self.source_parts, self.starts, self.ends
        fragment_id = NS + 'xml-fragment:' + digest([source_id, path])
        fragments.setdefault(fragment_id, {'@id': fragment_id, '@type': 'rkaf:SourceFragment',
            'oa:hasSource': source_id, 'oa:hasSelector': [{'@type': 'oa:XPathSelector', 'rdf:value': path}],
            'rkaf:selectorKind': ['oa:XPathSelector'], 'rkaf:sourceArtifactDigest': 'sha256:' + source['sha256'],
            'rkaf:fragmentContentDigest': 'sha256:' + digest(prepared['source_text'][node['source_start']:node['source_end']])})
        evidence = []
        if include_text and 'start' in node:
            for part in source_parts[bisect_right(ends, node['start']):bisect_left(starts, node['end'])]:
                start, end = max(part['start'], node['start']), min(part['end'], node['end'])
                exact = _evidence(document, document['text'][start:end], field, start, end)
                if exact is None:
                    raise ValueError('Publisher text evidence does not resolve in the prepared source')
                evidence.append(exact)
        return fragment_id, evidence

    def target(self, path, node):
        identity = NS + 'reference-target:' + digest([self.source_id, path])
        if identity not in self.targets:
            fragment, evidence = self.support(path, node, 'reference_target')
            self.targets[identity] = {'id': identity, 'value': self.addresses[path],
                **{k: node[k] for k in ('start', 'end') if k in node},
                'xml_evidence_refs': [fragment], 'evidence': evidence,
                'text_status': 'available' if evidence else 'no_visible_text'}
        return self.targets[identity]


def attach_publisher_links(document, scan, passages):
    """Add native XML occurrences and shared targets to the existing scan result."""
    from refspec.registry import uslm, xml_text
    publisher = SourceIndex(document)
    prepared, source, fragments, targets = publisher.prepared, publisher.source, publisher.fragments, publisher.targets
    identifiers, support = publisher.identifiers, publisher.support
    passage_starts, passage_ends = [p['start'] for p in passages], [p['end'] for p in passages]
    publisher_rows, anchors = [], []

    root_id = prepared['nodes']['/*[1]'].get('identifier', '')
    title = root_id.removeprefix('/us/usc/t').split('/')[0] if root_id.startswith('/us/usc/t') else ''
    skipped = Counter()
    for native in uslm.iter_edges(source['xml'].encode('utf-8'), title, skipped, include_source_path=True):
        path = native['sourceXPath']
        node = prepared['nodes'][path]
        xml_fragment, evidence = support(path, node, 'reference')
        target_ids = []
        for target_path, target in identifiers.get(native['href'], ()):
            target_ids.append(publisher.target(target_path, target)['id'])
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
            anchors.append((node, row))

    # XML text intervals are nested or disjoint. Index enclosing anchors once;
    # each lookup follows only the source's nesting, not every publisher link.
    anchors.sort(key=lambda item: (item[0]['start'], -item[0]['end']))
    anchor_starts = [node['start'] for node, _ in anchors]
    ancestors, stack = [], []
    for index, (node, _) in enumerate(anchors):
        while stack and anchors[stack[-1]][0]['end'] <= node['start']:
            stack.pop()
        ancestors.append(stack[-1] if stack else -1)
        stack.append(index)

    # Associate only unique full containment. Keep the text reading's own target,
    # evidence and disposition; association does not assert target agreement.
    for group in ('candidates', 'rejected'):
        remaining = []
        for row in scan[group]:
            evidence = row.get('evidence', [])
            primary = evidence[0] if evidence else None
            matches = []
            index = bisect_right(anchor_starts, primary['start']) - 1 if primary else -1
            while index >= 0 and len(matches) < 2:
                node, parent = anchors[index]
                if primary['end'] <= node['end']:
                    matches.append(parent)
                index = ancestors[index]
            if len(matches) != 1:
                remaining.append(row)
                continue
            parent = matches[0]
            parent.setdefault('text_readings', []).append({'disposition': group,
                **{k: v for k, v in row.items() if k not in {'id', 'record_ids'}}})
        scan[group] = remaining
    scan['candidates'].extend(publisher_rows)
    scan['candidates'].sort(key=lambda row: (row['evidence'][0]['start'] if row.get('evidence') else len(document['text']), row['id']))
    scan['publisher_source'] = publisher.artifact()
    scan['xml_fragments'], scan['targets'], scan['publisher_skipped'] = fragments, targets, dict(skipped)
    scan['parsers'].extend({'name': name, 'version': version('refspec'),
                            'module_sha256': digest(Path(module.__file__).read_bytes())}
                           for name, module in (('refspec.registry.uslm.iter_edges', uslm),
                                                ('refspec.registry.xml_text.read_text', xml_text)))
    scan['supported_kinds'] = sorted(set(scan['supported_kinds']) | {'publisher_reference'})
    scan['target_resolution'] = 'publisher_targets_and_named_act_identity' if scan.get('indexes') else 'publisher_targets_in_supplied_xml'
    scan['limitation'] += (' Publisher links retain their native reading and context; text readings are separate observations, '
                          'not agreement checks. Targets are looked up only in the supplied XML, not the whole law or another edition. '
                          'Readable text preserves source order and cell boundaries, not full visual table layout.')
    return scan
