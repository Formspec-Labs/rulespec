# Reuse publisher metadata for discovery

Decision: which existing reader is sufficient to attach useful publisher fields
to a source result without another normalizer or document-body parser?

Hypothesis: a verified DocSpec catalog already preserves publication date,
docket/RIN and native CFR/authority fields, with evidence and explicit missing or
unparseable outcomes. A thin consumer can retain those observations separately
from document-body readings. SpicySearch's metadata preparation may already be the
right operation for an indexing consumer; displaying a few fields may not need
its entire search policy. A false source association would invalidate either path.

Arms: A is the current Rulespec prepared-document/discovery metadata and reference
reading. B adds existing catalog observations through DocSpec's public located-row
reader. Inspect and directly exercise SpicySearch's public metadata preparation
only where the selected consumer needs its identifier/field representation. Keep
source text, extracted meaning, reader defaults and review status fixed. Do not
copy upstream normalization logic or pretend catalog values have body offsets.

Inputs: first admit the retained 93-row Federal Register slice through the current
public reader. Pin its artifact, producer, partition blobs and selected rows.
Locate held publisher bodies/renditions for a bounded selection before claiming
body-to-catalog parity. Prefer XML when supported. A declared locator is not a
captured body; missing input stays explicit. Do not fetch or rebuild a large corpus.
Select at most six real rows after inspecting source fields, plus at most six
constructed counterexamples. Freeze selected values and expected associations
before running the comparison. These cases diagnose mechanisms, not a population
accuracy rate.

Checks: absent fields, malformed identifiers, body/metadata disagreement,
wrong-document association, distinct versions and changed artifact members.
Retain both native and normalized values, interpretation outcomes, source paths,
record/partition/source pins and the reader version. A publisher date is not proof
of current currency, matching legal edition or applicability. Do not join by title
similarity or choose the first proceedings record. No automatic claim approval.

Bound: zero model calls, no network acquisition, one selected catalog and at most
six selected bodies. Stop for a bounded owner fix if the public reader or necessary
source association fails; preserve that failure rather than substituting an
unverified row stream. Source-only evidence may settle reader suitability while
leaving the consumer integration open.

Decision rule: connect only if a named consumer gains useful source-supported
fields, all identity/evidence/refusal checks pass, and the implementation reuses
the owning reader/normalizer. Then test direct imports, build/install the changed
wheel and verify its normal caller. If compatible inputs or a suitable public API
are missing, record the precise unmet requirement and fix the owner where
appropriate; a mere import or schema-valid record does not close R21.
