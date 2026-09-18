# Optional output omission: saves tokens, fails meaning gate

**Do not adopt this intervention.** Four fresh low-thinking extraction calls show that requiring substantive optional values or omission removes placeholder overhead. On the complete CSBG application section it also loses all thirteen plan contents. On the benefits control it loses useful term-use links and an explicitly supported actor. No production files changed.

## Comparison and actual settings

A is the current installed CUE-generated schema and production prompt. B keeps every field, title, order and domain description, makes optional attributes non-null/nonempty when emitted, and says to omit them otherwise. Absence wording changes from null to omitted. Required `actor` and `actor_quote` remain nullable. The intervention is the schema-and-wording bundle, not an isolated claim about a single sentence.

The [plan](PLAN.md) preceded calls. Both arms received identical full source documents, focus windows and context catalogs. CSBG used the exact section-9908 window from the whole-chapter retest. The other-source control is the full saved 29 USC1025(a) benefits excerpt. Both are previously studied development data; these are fresh calls, not fresh unseen sources. Order was CSBG A/B, benefits B/A. Each was run once.

All four actual SDK requests used `gemini-3.8-flash`, `thinking_level=low`, `max_output_tokens=16384`, no sampling override and no thinking budget. There were no retries, provider failures or truncations. Existing installed `_record_window` captured requests/responses, and `_attempt_result` parsed them. [Runtime](runtime.json), [actual metrics](metrics.json), schemas and prompt descriptions are retained. A setup-helper typo failed before any provider call and is documented separately.

## Observed costs and adherence

| Case | A current | B omit absent | Meaning result |
|---|---:|---:|---|
| CSBG records | 27 | 12 | B removes all 15 statements representing the 13 plan contents |
| CSBG visible answer tokens | 9,011 | 2,343 | Most savings coincide with deleted substantive content |
| CSBG total reported tokens | 16,536 | 9,947 | 39.8% lower, with major regression |
| Benefits records | 31 | 30 | B combines two duties and drops useful structure |
| Benefits visible answer tokens | 7,865 | 5,331 | 32.2% lower |
| Benefits total reported tokens | 12,469 | 10,014 | 19.7% lower |
| Empty optional values, both cases | 499 | 0 | Intervention was followed |

Total: **4 calls, 48,966 reported tokens**, including 24,416 input and 24,550 visible output tokens. Provider `thoughts_token_count` was null in all responses; the reported totals equal input plus visible output. We do not infer an unreported internal thinking count or an invoice price. Recorded per-request times sum to about 54.9 seconds; the runner's separate capture-wall receipt is in [run-receipt.json](run-receipt.json). No extra audit/checker calls were made.

All four outputs validate against the schema actually sent, all parse without refusals, and all reproduce native decoding. Thus neither schema validity nor instruction adherence exposed the content loss. Paired source catalog hashes match. Exact source and readable statements/fields are beside each raw capture.

## Manual source review

The reviewer read the full source focus and every generated statement from both arms, plus populated fields, actor assessments and term links. These are revisable agent judgments, not human ground truth.

### CSBG

A individually represents all thirteen required State-plan contents in fifteen statements (indices 6–20). B replaces those contents with this one broad requirement (index 5):

> Beginning with fiscal year 2000, to be eligible to receive a grant or allotment under section 9905 or 9906 of this title, a State shall prepare and submit to the Secretary an application and State plan covering a period of not less than 1 fiscal year and not more than 2 fiscal years, submitted not later than 30 days prior to the beginning of the first fiscal year covered by the plan, and containing such information as the Secretary shall require, including the assurances and descriptions specified in paragraphs (1) through (13).

B then jumps directly to the two definitions of funding-reduction/termination “cause.” Source paragraphs (1) through (13) are explicitly present in the identical input. Required community action plans, requested submission, investigations, funding protections, representation procedures and performance alternatives are not expressed anywhere in B's statements. This is the known dangerous generic-reference failure, not legitimate shortening of the same information.

A's social-service coordination record 12 retains **low-income individuals**, correcting the historical B run's omission without intervention. Its record 6 still compresses the urban-intervention/widespread-replication detail to “document best practices for urban replication.” It also omits the express transition-off-assistance detail from the self-sufficiency item and “immediate and urgent family and individual needs” from emergency assistance. These details all appear in the supplied source. Hence A is the better extraction, not perfect.

Both arms retain the conditional definitions of “cause,” lead-agency duties, hearing timing and historical fiscal-year transition. Both combine “may revise” and “shall submit” in one `permission/may` record instead of separating their distinct force. Both omit the supplied editorial effective-date explanation. B changes the Secretary's assigned assessment power from A's `authority/may` to `permission/may`; not central to the clear omission verdict, but retained.

A populates scope fields on 22 records; B on none. Dropping duplicated scope labels could be reasonable when the default meaning remains complete. It does not justify dropping the actual thirteen requirements.

### Benefits counterexample

Both retain quarterly/annual/written-request distinctions and the one-participant-plan exception; the three-year rule's nonforfeitable-benefit/employment limits; the disclosure list; the one-per-12-month limit; the complete conditional liability protection; and the annual-notice alternative as a separate statement. Both three-year default statements still fail to incorporate the supplied annual-notice alternative, so independent usability remains incomplete in both arms.

Both retain the definition of “lifetime income stream equivalent of the total benefits accrued” and correctly connect its defining statement. **A has five explicit term-use links; B has none**, despite the same term appearing in those generated meanings. This is loss of useful conceptual structure, not placeholder removal. B emits more ordinary citation references (28 versus 8 statements), so it did not simply stop all optional structure.

B also leaves the explicit administrator actor null on the annual-notice statement (record 27), where A supplies it (28). B combines the Secretary's duties to prescribe assumptions and issue interim final rules; A separates them. Both preserve the full text meaning of these duties. B changes one “may have a term certain or other features to the extent permitted” record from permission to descriptive possibility; its source supports an interpretation-sensitive classification, so that difference is flagged rather than used as the main failure label.

A's optional choice explanation also overstates the first alternative as updating “accrued and nonforfeitable” information where the cited rule targets nonforfeitable benefits. B omits that optional explanation while preserving the underlying two-way choice in its statement. This is a genuine narrow improvement from avoiding unnecessary extra prose; it does not offset the independent losses above.

## Historical measurement: what is actually redundant

Across all **282** raw CSBG B statements, every one of the sixteen attributes is emitted. Only five are required. There are **2,288 empty optional values**, including `logic_quote` null 282 times, `alternative_quotes` empty/null 280 times, and each choice field null 278 times. Required null actor assessments are excluded.

A fixed-response test removes only empty optional values from each of the 27 saved captures. Native candidates, statuses and refusal-code sequences remain identical. Minified complete response text drops from **233,240 to 186,871 characters (19.9%)**. This measures representation overhead and current parser compatibility. **Deleting captured values afterward saves no billed model tokens.** Expanded local source evidence is another storage concern: the model already emits short passage IDs, not those expanded copies.

## Recommendation and alternatives

Keep current production extraction. The cheap representation change failed its semantic gate, so the token savings do not justify integration. One repetition cannot prove that omission constraints caused the CSBG collapse; it is enough to reject adoption from this evidence. No more calls were spent tuning around the same failure.

Useful existing capabilities: CUE remains authoritative; actor assessments are required but may be unknown; other attributes are optional; null and omission already compile equivalently; source passage IDs avoid quoting whole evidence blocks; complete statements are already the required default. The failed sparse-repair work concerned a different stage and had higher total generation cost; it should not be cited as proof that all initial-output sparsity fails.

Potential next experiments, not new implementation tasks:

1. **Source-reuse statement mode:** for genuinely self-contained verbatim clauses, let the model select an existing passage as the statement; deterministic code materializes the normal complete statement. Keep generated prose for inherited conditions and split clauses. This could save meaningful copy tokens without suppressing optional fields. It needs adversarial tests for “such,” remote exceptions, fragments and source text that is not independently usable.
2. **A declared list-content accounting check:** because all thirteen supplied items vanished while output validated, test a small source-derived inventory of expected list items alongside extraction. A missing mapping triggers a visible gap, not assumed semantic failure or an automatic extra audit. This directly protects against apparent savings caused by omitted content. Do not equate one mapped passage with complete meaning.
3. **Compact storage/export views:** omit empty values and expand evidence/metadata on demand using existing IDs. This is deterministic and can improve readability and downstream prompt size, but must be separately described as downstream/storage optimization rather than provider-output savings.

No schema feature was adopted, no baseline history changed, and no production source was edited.
