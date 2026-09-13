"""Replay captures using their saved preview event identities; never call a model."""
from unittest.mock import patch

from rulespec_extrapolator import review_store
import run


def verify():
    original_decode = run.decode

    def decode_with_saved_events(cell, phase):
        saved = run.e._load(run.HERE / f'decoded/{cell["id"]}-{phase}.json')
        events = []
        for preview in saved.get('previews', []):
            replacements = preview['replacements']
            assert len(replacements) == 1
            event = replacements[0]['review_event_id']
            assert event.startswith('urn:rulespec:review-event:') and event.endswith(':0')
            events.append(event.removeprefix('urn:rulespec:review-event:').removesuffix(':0'))
        with patch.object(review_store, 'uuid4', side_effect=events) as identities:
            result = original_decode(cell, phase)
            assert identities.call_count == len(events)
            return result

    with patch.object(run, 'decode', side_effect=decode_with_saved_events):
        run.verify()


if __name__ == '__main__':
    verify()
