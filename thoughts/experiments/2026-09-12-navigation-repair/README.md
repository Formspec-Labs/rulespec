# Navigation did not make the current repair pass act

**Keep production unchanged.** Four live recovery calls returned no edits and no
observations. Adding the new reference navigation did not repair either saved IEP
omission or the constructed request-content omission. The existing schema and
review code can represent the repairs; this test did not make the model propose
them. This is a result on selected development data, not a general accuracy rate.

## Existing capabilities are sufficient for the tested representation

| Capability | Current owner and code | Result |
|---|---|---|
| State the complete default meaning | CUE `summary`; `core.revise_claim` | Already implemented. Two constructed edits preserve each original attendance statement and explicitly add the parent's writing requirement. |
| Preserve the additional clause as evidence | `context_quotes`; `EvidenceBinding` with `providesContext` | Already implemented. Exact writing-clause evidence survives compilation and preview without expanding the main quote. |
| Record applicability conditions | `scope_text`, `scope_quotes`; `ApplicabilityScope`, `definesScope` | Available, but not needed for the representation proof. Do not imply that a writing defect necessarily invalidates an attendance exemption, or turn purpose text into applicability. |
| Preserve the separate writing requirement | Existing `requirement` / `must` record | Unchanged in both constructed previews. No companion record or new relation type was needed. |
| Relate requirements using `target_ids` | Application qualification guard; Core `RelationshipAssertion` / `qualifies` evidence | The application deliberately limits qualifiers to conditions, exceptions and exemptions. This experiment leaves that guard intact. |
| Supply source-to-claim navigation to a model | `context-export` produces it; recovery does not consume it automatically | Experiment B adds those rows to the existing recovery input. No production wiring was adopted. |
| Decide when the current statement needs repair | Existing recovery generation | The missing behavior on these cases: all responses were empty. |

The [representation proof](representation-proof.json) is explicitly constructed,
not model output. It uses temporary `ReviewStore` previews, retains kind and modal
force, preserves main source coordinates and the separate writing record, creates
a new revision, and leaves the original snapshot/history untouched. A supporting
quote alone does not prove the model has preserved its meaning.

## Controlled result

Both arms received the current recovery prompt, complete source, all current
claims, an empty audit inventory and the same navigation explanation. B alone
received deterministic reference-to-current-claim associations; the native lookup
still made no semantic governing assertion. The response schema came unchanged
from the CUE-based recovery profile. There was no preceding audit or relationship
generation call and no production review action.

| Source and criterion | A: ordinary recovery | B: recovery + navigation |
|---|---|---|
| Actual IEP: written parental agreement in C0004's default statement | Not repaired | Not repaired |
| Actual IEP: written parental consent in C0005, distinct from member input | Not repaired | Not repaired |
| Constructed electronic request: name/reference-number requirement in permission's default reading | Not repaired | Not repaired |
| Wrong reporting prerequisites, wrong native branch, unrelated IEP targets | No change | No change |

Every response was substantively:

```json
{"proposals":[],"observations":[]}
```

All responses finished normally and parsed. There were no provider, schema,
source-resolution or proposal-validation failures. With no proposals, the model
produced no replacement fields to validate or apply. Inactivity in the negative
cases is not evidence of correct discrimination: it also did nothing in every
positive case. The separate preview proof is not a successful model repair.

The [anonymous raw review](ANONYMOUS-REVIEW.md) was saved and hashed before the arm
key was opened. Original books, raw captures and request/runtime pins remain
unchanged. [Request verification](request-verification.json) confirms exact
prompts, schema, model and settings; all four responses replay through the current
decoder and preview route with model creation blocked.

## Interpretation and next diagnostic

H1 was not supported: explicit navigation did not improve this recovery pass.
H2 was not supported either: ordinary recovery did not independently fix the
omissions. H3 remains plausible, but the empty answers contain no rationale that
establishes the cause. Treating whole-book retention as sufficient, a conservative
optional-edit policy, and the effort of regenerating complete fields are different
possible explanations; this test cannot distinguish them.

Stop this comparison without a prompt patch or another default pass. The next
small diagnostic should require decisions rather than invite optional edits:
use the existing challenge schema on fixed, source-checked candidate repairs,
mixed with false reporting-prerequisite and wrong-branch repairs. Require a
verdict and source evidence for each candidate. That separates failure to select
a repair from failure to recognize a correct repair. Keep the constructed nature
explicit. A positive result would still need fresh real documents before wiring
a new routine into production. Do not claim a new complete-rule schema is needed
when the current representation already passes its narrow mechanical proof.

## Cost, bounds and reproduction

Four calls used **37,287 reported tokens**: 31,511 prompt, 5,720 thinking and 56
visible response tokens. Recorded cached input was 9,127 tokens. A used 18,279
total tokens; B used 19,008, about 4% more, without a measured repair gain.
Recorded provider-call time totaled 22.67 seconds. Model: `gemini-3.8-flash`,
temperature 0, medium thinking, no numeric thinking budget, 32,768 output cap.
Each case/arm has one sample. The four-call bound was reached; there were no
provider retries. Two local harness setup errors occurred before any provider
request and are retained in [preflight.json](preflight.json).

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src \
  .tools/document-poc-venv/bin/python \
  thoughts/experiments/2026-09-12-navigation-repair/run.py verify
```

[Plan](PLAN.md), [usage](usage.json), [requests and responses](captures/),
[decoded outputs](decoded/), [source books](books.json).
