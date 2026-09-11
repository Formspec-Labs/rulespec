# Manual review of source and delivered evidence

I read the original text supporting all eight new questions, the four prior
controls, and every arm's delivered source intervals. The
[delivery transcript](raw-delivery-review.txt) prints A in full and exact additions
and removals for B/C; [results](results.json) retain complete spans and omission
decisions. No model judged these results. These are revisable source-support
assessments, not determinations of current law or complete legal answers.

| Case | What the raw evidence shows |
| --- | --- |
| N1, vending priority | A already supplies the licensed-blind-person priority. B/C add the income-assignment clause. A also retrieves congressional findings; an actual consumer must distinguish that passage's role from the operative provision. |
| N2, restriction review/publication | A already retains the Secretary's decision, binding effect and publication requirement. Extra evidence changes no selected support. A also supplies a separate licensee grievance procedure; exact source is not necessarily relevant source. |
| N3, license duration | All retain indefinite duration and conditional termination. B drops a direct licensing paragraph and substitutes a principal-agency paragraph plus the editorial “Commissioner” correction. C restores the direct paragraph. The selected answer does not improve, but the mechanism of crowding is visible. |
| N4, location selection | All retain authorization, required federal approval and the regulations qualification. No model-generated modality is needed to read the source. Another retrieved State-agency application clause concerns a different approval. |
| N5, bus passenger wine | A has the possession restriction and passenger exception. B/C add the shipment exception, which is real but unnecessary to this question. |
| N6, empty hazardous-material tank | A has the vehicle class but lacks the governing stopping sequence. B/C add it, including the exception reference, but the cap prevents all exceptions from appearing. Uncapped packets contain all selected support. The selected source passages themselves exceed the cap; this is a display limitation, not a new extraction failure. |
| N7, voluntary prior service | A already supplies the uniform-treatment condition. B/C add military-service material associated with another hit. It adds 525 source characters without helping the selected question. |
| N8, de minimis alternatives | A ends at “only if they occur when” and supplies neither compliance path. B/C add the full first path and the alternative subpart-B path. This is the single new-query complete-support gain under the cap. An irrelevant rail classification hit remains in all arms. |
| L1, nonconsecutive employment | All omit the paragraph containing the seven-year break qualification. B adds other service exceptions and drops the payroll-week paragraph; C keeps the direct payroll evidence. Neither reaches the missing paragraph even without the cap. This needs a different source/relationship or ranking decision. |
| A1, beer as cargo | B/C recover the shipment exception. B also expands an irrelevant rail result into 720 characters of crossing duties. C avoids that expansion within the cap, while retaining the same useful alcohol support. |
| R4, chlorine | B/C recover stopping and gear duties. B crowds out a direct green-signal exception to include a long placard list. C instead includes several exceptions, but still omits the final “Exempt” crossing item. The original labels count duties only; their passing score is not a complete crossing-rule answer. |
| F3, service equipment | B/C restore the practices and certified-equipment conjunction plus the start of an interrupted source sentence. The original short labels are satisfied. Those labels alone would not prove every applicable practice or exemption was resolved. |

## What explains the results

Ranking was identical in all three arms. Recovery comes from already verified
claim/context evidence attached after ranking, not better search or a new model
interpretation. When a short item belongs to a grouped rule, that evidence helps.
When a broad header or irrelevant result links many records, expansion can add
unhelpful provisions and editorial material. The cap chooses among complete
fragments; a complete fragment need not contain a complete rule or exception list.

C retains every source character A admitted, as independently verified. That is
useful allocation behavior, but it added no selected-support gain over B in these
cases. It does not identify which context is relevant. B/C each improve one of
eight new questions under the cap, below the required two; the gate fails.
Uncapped improvement on two questions is reported separately and does not change
the gate retrospectively.

Raw packet evidence repeats quotations under different roles and across hits.
The production `export_discovery` already uses a shared evidence table with roles,
so those repeated quote counts are not a measured duplication rate for its JSON
output. A consumer should use that table before adding another deduplicator.
The experiment's coalesced display intervals measure source text cost separately
from the raw evidence records and their serialized metadata. No provider tokens
were consumed or inferred from JSON size.

## Native references and limits

The existing RefSpec-backed lookup locates `20 USC 107a(b)` in the pinned chapter,
including the licensing paragraph, and leaves `(z)` unresolved. The selected
chapter has no retained publication fields; no date is inferred from a directory
or source URL. Two XML captures with identical text remain separate ambiguous
targets. A supplemental [edition-label control](edition-control.json) reuses the
existing title-5 fixture and a clearly constructed alternate publication label;
both labels and source identities remain visible, with edition correspondence
unestablished. This does not establish two actual historical legal editions.

Native target text was not added to lexical packets in this experiment. These
checks establish a separately available navigation path, not an additional
retrieval gain. The actual consumer's display, usefulness, reviewer effort and
broader document-family performance remain unmeasured.
