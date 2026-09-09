# Sparse meaning and compact audit inputs

Implemented a complete default `statement` with optional enrichment, and removed
repeated quotations from audit requests using the existing passage catalog.
The bounded check used eight fresh Gemini 3.8 Flash calls: two low-thinking
extractions and three paired medium-thinking comparisons, all at temperature 0.
See the preregistered [plan](PLAN.md), exact [design](design.json), raw captures,
and [metrics](metrics.json). These are selected development cases, not an accuracy
benchmark or human-approved rules.

## What changed

Canonical CUE requires a nonempty `statement`, `kind` and `modality`. Other lean
extraction fields may be omitted or null. Their descriptions request useful
enrichment, rather than filling every role because the source passage exists.
The complete statement must retain every governing condition, exception and
alternative. Native CUE generation supplies the nullable JSON Schema directly;
no second schema or provider-specific nullable conversion was introduced.
[Gemini's structured-output guidance](https://ai.google.dev/gemini-api/docs/structured-output)
documents null and optional properties; both live extraction requests accepted
the generated schema.

Parser version 6 converts absent enrichment into Core's existing empty strings
and lists. Original raw omissions/nulls remain saved. Missing optional modal-word
evidence alone no longer creates a warning; main evidence and supplied component
evidence still undergo validation. Existing identifiers, provenance and review
history remain intact.

Audit version 5 omits empty request fields and expresses exact catalog quotations
as `{source_ref: ...}`. It retains all nonempty meaning fields, offsets, evidence
roles and diagnostics. `logic_text` references still mean retained verbatim logic;
evidence references still mean supporting source. Partial phrases, ambiguous
quotes without a matching locator and text outside the catalog remain verbatim.
Saved records and responses retain their full values. Expanding the references
reproduced the complete nonempty input exactly for all three fixtures.

## Measured audit results

Each arm used the same saved draft, inventory, source, comparison output schema
and settings. Only request encoding and its explanatory guidance changed.
The baseline requests were frozen before implementation; both arms were called
fresh in the recorded randomized order. There was one call per arm per case.

| Case | Baseline input tokens | Compact input tokens | Reduction | Target outcome |
| --- | ---: | ---: | ---: | --- |
| Passport | 18,528 | 7,933 | 57.2% | Wrong actor and inverted response exemption caught by both |
| Waste | 46,426 | 15,392 | 66.8% | AND-to-OR substitution and 3-to-30-day deadline caught by both |
| Notice | 45,194 | 9,706 | 78.5% | Standalone qualification omission missed by both |

The correct neighboring passport prohibition (C0012) and waste container-closure
exception tree (C0007) remained correct in both arms. The compact notice audit
additionally flagged `not_stated` modality for C0004 and C0010, whose source says
the employee/employer is "expected" to act. Those are plausible concerns about
normative force, but the auditor's proposed `should` classification is not an
established answer. The baseline accepted both. These two changed notice controls
leave the broad no-regression quality gate **unresolved**.

Notice thinking tokens rose from 3,046 to 11,918; input reduction does not imply
proportional cost or reasoning reduction. Its reported total tokens still fell
from 53,608 to 27,042. All detailed usage and original rationales are retained in
the per-arm results. Reports marked `failed` refer to detected semantic findings,
not failed API requests: all six comparisons parsed without audit issues.

The narrower adoption decision is a demonstrated input-token/noise reduction,
with all four planted errors retained on these cases. It is **not** a passed
general semantic-quality gate or a fix for the known qualification miss.

## Fresh extraction review

Passport produced 14 accepted records; waste produced 15. Both had zero refusals
and passed Core/SHACL checks. All 29 raw statements survived conversion unchanged.
Every row omitted scope, choice, alternatives, context and logic enrichment.
The model retained modal-word evidence on 22 rows and references on 14, showing
that optional did not mean all enrichment was disabled. No live row used explicit
null; omitted and null variants are both covered by parser tests.

Passport used 2,244 input and 1,410 output tokens. Waste used 3,589 input and 3,135
output tokens. These two runs have no contemporaneous extraction controls, so
they do not establish causal output-token savings or improved extraction accuracy.

Direct source/output review found:

- Passport C0004 and C0011 retained agency approval, management approval and
  extenuating-circumstance exceptions, including the examples. C0012 retained both
  no-response and no-personalization exemptions. C0013 retained "when tailoring"
  and both index consultation and email contact. C0005 retained the local-adaptation
  qualification in the statement itself.
- Waste C0000 retained quantity limits, operator control and the all-conditions
  proviso. C0001 retained exceptions referencing (A)(7)/(A)(8). C0004/C0005 retained
  the incompatible-waste exceptions. C0007 retained the complete nested venting
  exceptions. C0008 kept both required labels and the examples. C0009 retained
  the three-day deadline, compliance/removal alternatives and all destinations.
  C0010/C0011 retained the excess-accumulation case after splitting the paragraph.
- Some semantic overlap remains between passport C0005's complete duty with its
  qualification and C0006's separately referenceable modification permission.
  C0009 also combines an IN definition with an illustrative permission while
  classifying the unit `not_stated`. This implementation reduces repeated fields;
  it does not establish ideal rule boundaries or single-modality segmentation.
- Neither live extraction populated optional structured choice/scope even for
  the more complex waste rules. The statements retain the reviewed detail, but
  usefulness for downstream structured querying remains unmeasured. No automatic
  deletion or fuzzy merging of overlapping meanings was introduced.

These are revisable agent observations of the selected text, not proof that
every meaning was discovered. `semantic_completeness` remains `not_established`.

## Reproduce

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python \
  examples/document_understanding/sparse-meaning-check/run.py replay
```

All eight captures replay identically with zero provider calls. The design pins
runtime and fixture hashes; historical captures were not rewritten. The runtime
snapshot is under `frozen/`. Native CUE drift checks pass. The full package and
schema-generator suite passed 377 tests, followed by all 35 expanded audit tests
after adding ambiguous/outside-catalog and contiguous-range counterexamples.
No additional live calls, repairs, release or deployment are part of this check.
