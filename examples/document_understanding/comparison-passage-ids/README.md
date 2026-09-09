# Comparison passage IDs: bounded improvement, broader gate unmet

Passage IDs consistently produce usable, relevant citations on the saved notice
rule document. They retain the governing lead-in that one quote-only result failed
to cite. They do not solve field-specific semantic review. No production change is
adopted, and optional token narrowing remains experimental.

## Results

37 local cases plus one separately recorded fixture correction; four fresh
`gemini-3.8-flash` comparison calls, medium thinking, temperature 0, no numeric
thinking budget or application output cap, no retries. The same full 4,360-character
source, 18 draft claims and 18 inventory units were supplied to every call. Order:
Q1, P1, P2, Q2. Q-token reuses Q responses offline; it costs no additional call.

| Workflow | Repeat 1 accepted judgments | Repeat 2 accepted judgments | Key limitation |
|---|---:|---:|---|
| Current exact quotes | 32/36 | 36/36 | Formatting refusals in Q1; Q2 omits the cited governing lead-in for C0014 |
| Same quotes + existing token alignment | 36/36 | 36/36 | Cannot restore an unselected governing component; ambiguous/layout controls still align |
| Passage references | 36/36 | 36/36 | Broad citations; semantic assessment remains imperfect |

All four raw outputs follow their schemas and field order, use reciprocal C/U links,
and detect the overbroad phone-call permission. None explicitly acknowledges the
qualifications still present in its `logic_text`. All four retain the key notice
alternatives, first/subsequent-request distinction and emergency timing in their
assessments. The arms disagree about the classification of “may not be required”;
that is an unresolved modality judgment, not established improvement or regression.
Every derived report remains `failed` because it includes semantic findings;
`review_complete=true` means all expected judgments were accounted for.

Both ID runs cite F003:F004 for the phone-call rule, including its governing
conditions. Q2 cites only the illustrative phone-call sentence even while diagnosing
a lost lead-in. Thus Q2's perfect mechanical acceptance count hides weaker component
evidence. See the [masked meaning review](blind-review.md) and
[unmasked evidence review](evidence-review.md).

## Size and cost observations

| Measure | Quote runs | Passage-ID runs |
|---|---:|---:|
| Output tokens | 7,197 / 6,769 | 5,545 / 5,259 |
| Total reported tokens | 66,537 / 62,525 | 63,132 / 62,007 |
| Request duration | 57.39 / 50.29 sec | 50.09 / 45.80 sec |
| Resolved evidence, complete results | 8,560 / 8,064 chars | 55,292 / 55,292 chars |

IDs reduce mean output tokens by 22.6%, but mean total tokens by only 3.0%: both
arms retain about 45,000 input tokens. The complete experiment used 254,201 reported
tokens. These are token counts, not a dollar invoice. Provider metadata reports
implicit caching on P2 and Q2 (39,677 and 39,788 prompt tokens); no cached count was
reported on the first repeats. Timing/cache/thinking variation and two selected
repeats prohibit a general speed or cost-rate claim. Full selected paragraphs make
the resolved evidence larger despite shorter model output. No request deduplication
or human review-time intervention was tested.

## Local controls and limits

The three original failed quotation pairs recover at their recorded exact source
offsets. Hand-selected IDs distinguish repeated text across passages, but the
existing aligner still chooses one occurrence within a passage and joins constructed
table/list text. Invalid/unavailable IDs, unseen gaps and inserted text are refused.
A valid unrelated ID still resolves, and narrowing two selected passages can drop
the governing condition. See [local review](stage1-review.md), including the fixture
correction and correction of the earlier claim that C0014 retains a complete source
paragraph. Its logic actually omits the F003 lead-in while retaining F004 exceptions.

The strict adoption rule was not met: mechanical superiority did not repeat because
Q2 already passed, and explicit retained-logic recognition failed throughout.
Passage-only comparison is the simpler candidate for a separately scoped reliability
decision; that would narrow the gate, not satisfy this one. No further model calls,
matcher additions or fixture-specific prompt tuning are warranted by this trial.

## Reuse and reproduction

The experiment replaces quote fields with arrays of the existing CUE-generated
`#SourceRef` schema from inventory `scope_refs.items`; no new source-reference type
or parallel production schema is introduced. It reuses `passage_catalog`,
`resolve_passage`, `_source_span`, provider capture, comparison input, judgment
validation and assessment. LangExtract alignment runs with fuzzy matching and
lesser matches disabled. Raw captures remain unchanged; field translation and
resolver substitution occur only inside the experimental harness.

From the repository root, with no credentials or provider access needed:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/comparison-passage-ids/experiment.py replay
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/comparison-passage-ids/supplement.py replay
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/comparison-passage-ids/measure.py replay
```

All processing, controls and metrics replay identically. Native CUE generation
matches the checked-in schemas. The initial credential-file setup failure occurred
before any provider call and is retained under `setup/`; no response was retried.
The frozen [plan](PLAN.md), inputs, captures, refusals, review key, reviews, metrics
and verification are saved here. This is development data, with imperfect masked
primary-agent assessment and no independent semantic gold labels. No extraction,
inventory regeneration, runtime adoption, commit or push is part of this experiment.
