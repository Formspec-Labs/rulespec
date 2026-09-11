# Parallel tests of pipeline redesign hypotheses

User authorized hypothesis-driven tests in parallel after three independent pipeline
recommendations. Use the current local runtime, including the verified but uncommitted
compact link operation. No production edits, automatic adoption, commits or changes
to earlier captures. Each track owns a separate experiment directory and freezes its
criteria before scoring or calling a model.

| Track | Narrow decision | Planned comparison | Call bound |
| --- | --- | --- | --- |
| Retrieval | Does generated meaning/context improve relevant-source retrieval under the existing lexical ranker? | Source paragraphs vs summaries vs source plus linked meanings/context; same ranker and fixed questions | Zero calls planned, maximum 4 if needed |
| Context | Does automatically selected context improve interpretation of incomplete standalone statements? | Same statement/questions with and without existing deterministic context/evidence selection | 8 calls, no retries |
| Targeted checks | Do explicit per-target judgments retain clear links while exposing bad/disputed ones? | Same supplied candidate proposals: whole-proposal challenge vs per-target judgments | 6 calls planned, maximum 8 |

The retrieval design uses historical real-document books and newly frozen authored
queries, not the sealed evaluation holdout or real users. It reuses the existing
search function; its results cannot establish embedding performance.

The context design includes actual refrigerant/seatbelt failures and a constructed
negative where a structural parent does not govern the next duty. Known source
ambiguity stays uncertain. A model answering comprehension questions is a proxy for
interpretation, not measured human review effort. Automatic context selection must
not receive the expected answers or handpicked governing passages.

The relationship design includes the actual bundled driver/carrier failure and
constructed candidate-target negatives. Candidate targets are supplied. This tests
judgment granularity, not discovering omitted candidates. Any partially supported
addition remains a recommendation unless the existing application path can represent
and validate it without inventing a new interpretation.

The original broad redesign questions remain open. These are inexpensive probes
that can reject or motivate a larger comparison; they are not a full workflow/form
trial, full optional-refinement replacement, retrieval benchmark, or demonstration
of production readiness. Preserve failed/noncompliant output, actual indexed/request
text, source identities, schema/configuration, and per-call usage. No retuning on
scored questions or retries. Parent reviews raw outcomes and totals new calls only,
excluding copied historical captures.
