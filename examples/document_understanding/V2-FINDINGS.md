# Meaning and shared-scope experiment — 2026-09-07

## Result

The revised extraction design resolves the targeted structural failures on this
development example. With the same Gemini 3.8 Flash model, the Constitution output
matches **20/20 labeled checks**, compared with **11/20** for the earlier design.
Two separately authored synthetic tests match **12/12** and **7/7** checks.

These numbers measure agreement with explicit expectations about statement kinds,
separation and qualification links. They are not semantic accuracy percentages.
The assistant authored and source-reviewed the expectations before each respective
v2 inference. No human review or blind real-document holdout has occurred. The
synthetic tests exercise the same patterns illustrated in the prompt, with different
actors and actions; they are controlled transfer tests, not broad generalization.

## What changed

- `semantic_profile.py` defines an experimental vocabulary distinguishing authority,
  thresholds and definitions from requirements, permissions and prohibitions.
- Conditions identify their relationship as scope, prerequisite, or trigger;
  exceptions have a separate exception relationship. A sufficient trigger for an
  obligation is no longer expressed as a prerequisite for the underlying action.
- `applies_to` is a list of target quotations, allowing one condition to govern
  several distinct actions. Each target must resolve exactly and unambiguously.
  A qualifier with an unresolved target emits no partial relationship set.
- Negative wording remains explicit: “without consent” scopes a prohibition to the
  absence of consent, rather than becoming a blanket consent requirement.
- The HTML review shows every affected statement for a shared qualification.
- The evaluator tests expected complete target sets. It catches omitted links even
  when every supplied link resolves successfully. Missing or unexpected targets
  fail the check; it does not invent or repair model output.

The original v1 path remains available for replay and comparison. The new semantic
distinctions live in the experiment; they are not new normative Core classes or an
executable rule language. Main statements still use existing `ValueAssertion`
records and experimental predicates. Typed links use `RelationshipAssertion`.
Core JSON Schema and SHACL checks continue to validate the converted records.

## Observed runs

| Source | Grounded candidates | Core nodes | Labeled checks |
| --- | --- | --- | --- |
| Constitution, Article I Section 5 | 18/18 | 72 | 20/20 |
| Synthetic emergency operations passage | 8/8 | 36 | 12/12 |
| Synthetic scope counterexample | 5/5 | 23 | 7/7 |

All three graphs pass Core JSON Schema and SHACL checks with no unresolved
declared targets. Raw provider responses and candidate records are preserved.

In the Constitution run, the assistant's source review confirms:

- The House's judging role is classified as authority and quorum as a threshold.
- The two-thirds condition is a prerequisite for expulsion.
- The request of one-fifth of members present is a trigger for the recording duty.
- Session and absence-of-consent conditions both target both adjournment restrictions.
- The secrecy exception targets publication, not journal keeping.

One summary still says “Parts judged to require secrecy” without naming who judges.
The source quotation and actor metadata retain context, but summary fidelity still
requires review. Passing the labeled structure checks does not establish that all
summaries preserve every detail. Other parts of the chapter are not fully labeled.

The counterexample puts a maintenance prohibition beside an unconditional meter
inspection permission. The model correctly restricts the maintenance and missing-
permit conditions to the hatch-opening prohibition. It also emits an “at any time”
scope condition for inspection; this is not required by the current checklist and
should be evaluated as a representation choice in a future profile.

## What the comparison proves and does not prove

The old model output cannot express typed relations, so five of its nine failed
checks concern information missing from the old representation. Two concern
authority/threshold classification, and two concern lost shared scope. This is a
combined schema-and-prompt improvement, not a claim that model accuracy increased
from 55% to 100%.

The checks use distinctive source substrings to identify expected statements. They
are tailored to these fixtures and cannot score arbitrary paraphrases or general
document meaning. Extra claims and errors outside the labeled distinctions can
still pass. Human review and broader, independently labeled examples remain needed.

No PDF parser, long-document segmenter, RefSpec integration, editable review,
cross-document assembly or general Boolean condition engine was added.

## Replay and inspect

- [Constitution review](runs/gemini-3.8-flash-v2-constitution/review.html)
- [Synthetic shared-scope review](runs/gemini-3.8-flash-v2-shared-scope/review.html)
- [Counterexample review](runs/gemini-3.8-flash-v2-counterexample/review.html)
- `semantic_expectations.json`: expectations and source paths; never sent to the model.
- `semantic-checks.json` in each run: per-check results, expectation/source/output hashes.

Run another v2 extraction with `poc.py extract --profile v2 --model gemini-3.8-flash`.
The credential and new-output-directory options remain as documented in README.
Replay infers the profile from the saved run record and makes no provider call.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/evaluate_semantics.py examples/document_understanding/runs/gemini-3.8-flash-v2-constitution --case constitution --output .tools/semantic-checks.json
```

The evaluator writes results and returns a nonzero exit status for failed checks.
The v1 comparison intentionally fails the new checklist. Focused tests verify that
omitted shared scope fails evaluation even with zero unresolved declared targets.

## Next decision

Keep this richer meaning structure for the next experiment. Have a person review
the expected structures and add a real section with a distant exception, a shared
heading and mixed AND/OR conditions before treating this as a normative profile.
The immediate lesson is that clearer representations and explicit semantic checks
can fix defects that model substitution alone did not resolve.
