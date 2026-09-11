# Manual review of retained meaning and remaining defects

This review reads selected complete source quotations and generated statements
from the unchanged saved outputs. The earlier full raw-response review remains in
the [context experiment](../2026-09-11-fresh-reference-context/raw-review.md).
These cases explain the retention result; they are not an independent accuracy set.

| Saved cell and source positions | What the output preserves | Remaining limitation |
| --- | --- | --- |
| `title-29-ch4B.1.A`, `[18612, 19046)` | The Secretary's authorization to assist States retains consultation, both delivery-system alternatives and the Secretary's discretion. Three original-source fragments support one complete quotation. | Added support prevents a mechanical rejection; it does not resolve the cited provision's meaning. |
| `title-38-ch7.1.A`, `[80279, 81414)` | The repayment permission retains fraud/malfeasance, notice, ten business days to respond, and the five/fifteen-business-day branches. Five original-source fragments support the whole quotation. | The literal actor quote `the Secretary` is ambiguous. The actor is retained, with `component_evidence_unresolved`; the fix does not fabricate a unique actor location. |
| `title-20-ch6A.1.A`, `[11855, 12387)` | The evidence includes the indefinite-license sentence and its conditional termination language. It is already one original-source fragment. | The statement says only that each license shall be issued for an indefinite period. Its standalone wording omits possible termination. More complete evidence does not repair that semantic omission. |

Main statement support uses the existing evidence field `summary`. Distinct
source fragments exclude inserted formatting; they are not additional model
answers. The full quotation remains readable in prepared-text coordinates. The
verification checks every supporting piece against original-source intervals.

The third example is a useful unchanged control: this delivery improves retention,
not statement composition. Keep the seven kind/modality contradictions and optional
component refusals visible. The failed context-selector adoption remains deferred.

The added review-boundary controls are explicitly constructed. Their first attempt
used a single newline and incorrectly assumed two passage IDs; the actual request
contained one paragraph and correctly refused `F001`. The original fixture is
saved in `control-history/review-single-newline.py`, with the failed run under
`cli-isolated`. The corrected fixture uses a blank paragraph boundary and asserts
the supplied catalog before testing review behavior. No production parser change
was made to accommodate the incorrect fixture.
