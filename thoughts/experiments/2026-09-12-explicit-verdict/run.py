"""Test the saved explicit narrative specification using the existing harness."""
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
PREVIOUS_RUN = HERE.parent / '2026-09-12-composed-verdict/run.py'
SPECIFICATION = HERE.parents[1] / 'plans/2026-09-12-assessment-narrative-format.md'


def module(name):
    spec = importlib.util.spec_from_file_location(name, PREVIOUS_RUN)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


control = module('composed_control')
harness = module('explicit_capture')
e = harness.e
instructions = SPECIFICATION.read_text().split('## Instructions sent once at the beginning\n', 1)[1].split('```text\n', 1)[1].split('\n```', 1)[0]


def compose(document, window, packet):
    catalog = e.passage_catalog(document, window)
    questions = []
    for item in packet['items']:
        attrs = item['unit_attributes']
        assert not set(attrs) - control.prior.FIELDS
        blocks = []

        def block(text):
            # Frozen inputs do not collide with this delimiter; stop rather than
            # silently changing data or extending a parser for an unseen case.
            assert '"""' not in text.splitlines()
            blocks.append(text)
            return '\n"""\n' + text + '\n"""\n'

        def inline(text):
            return block(text) if '"' in text or '\n' in text else '"' + text + '"'

        def evidence(ref):
            return f'({ref})' + block(e.resolve_passage(ref, catalog, document)['quote'])

        pieces = [f'### Item {item["item_id"]}\n\nGiven that the extraction cites main source text ',
                  evidence(item['unit'])]
        for ref, span in catalog.items():
            pieces.append(f'and the supplied source also says ({ref})' + block(span['text']))
        for term in packet['terms']:
            pieces.append('and the proposed term catalog names ' + inline(term['id']) + ' as ' + inline(term['label']))
            if term['aliases']:
                pieces.append(', also called ' + ', '.join(map(inline, term['aliases'])))
            for ref in term['source_refs']:
                pieces.append(', citing source ' + evidence(ref))
        pieces.append('does the extracted statement' + block(attrs['statement']))
        pieces.append('completely and faithfully describe the source meaning classified as '
                      + inline(attrs['kind']) + ' (kind), with force '
                      + inline(attrs['modality']) + ' (modality)')
        pieces.append(', for ' + inline(attrs['actor']) + ' (actor)' if attrs.get('actor')
                      else ', for which no actor was identified')
        labels = {'scope_text': 'representing applicability (scope text) as',
                  'choice_text': 'representing component and alternative grouping (choice text) as',
                  'defines_term': 'defining the proposed term', 'term_refs': 'using the proposed terms',
                  'references': 'retaining the references', 'actor_quote': 'citing actor wording',
                  'modality_quote': 'citing modality wording'}
        for field, label in labels.items():
            value = attrs.get(field)
            if value:
                pieces.append(', ' + label + ' ' + ', '.join(map(inline, value if isinstance(value, list) else [value])))
        supports = {'scope_quotes': 'scope', 'context_quotes': 'context',
                    'alternative_quotes': 'alternatives', 'choice_quote': 'choice', 'logic_quote': 'logic'}
        for field, label in supports.items():
            value = attrs.get(field)
            if value:
                for ref in value if isinstance(value, list) else [value]:
                    pieces.append(', with proposed ' + label + ' support ' + evidence(ref))
        pieces.append(', including every governing condition and required detail in the supplied source?')
        text = ''.join(pieces)
        assert text.startswith(f'### Item {item["item_id"]}\n\n')
        assert re.findall(r'^"""\n(.*?)\n"""$', text, re.M | re.S) == blocks
        assert all(line == '"""' for line in text.splitlines() if '"""' in line)
        assert all(span['text'] in text for span in catalog.values())
        for field, value in attrs.items():
            if value and field not in supports:
                assert all(v in text for v in (value if isinstance(value, list) else [value])), field
        questions.append(text)
    return instructions + '\n\n' + '\n\n'.join(questions)


# Two isolated imports preserve A's exact preceding prompt while letting the
# existing harness render/verify B. No changes to prior files or production code.
harness.HERE = HERE
harness.PROMPT = instructions
harness.compose = compose
harness.prior.narrative = lambda document, window, packet: (control.compose(document, window, packet), [])
harness.PRIOR_RUN = PREVIOUS_RUN


def prepare():
    harness.prepare()
    # The reused harness pins itself, inputs and runtime. Include its transitive
    # renderer and this exact instruction source in the final pre-call pins.
    pins = e._load(HERE / 'precall-pins.json')
    for path in (SPECIFICATION, control.PRIOR_RUN):
        pins[harness.os.path.relpath(path, HERE)] = harness.sha256(path.read_bytes()).hexdigest()
    e._save(HERE / 'precall-pins.json', pins)
    harness.pins()


if __name__ == '__main__':
    {'prepare': prepare, 'capture': harness.capture, 'verify': harness.verify}[sys.argv[1]]()
