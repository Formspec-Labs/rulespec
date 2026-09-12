# Fresh CSBG chapter stress test

Decision: determine what the unchanged installed Rulespec pipeline delivers on a
substantially longer, nested legal document, especially for CSBG State-plan
discovery and as a draft for later workflow preparation. No production adoption,
prompt tuning, or automatic repairs are part of this test.

Hypothesis: the current extraction retains important State-plan duties, actors,
conditions, alternatives, definitions, and source support across windows. A
plausible competing outcome is that individual sentences remain accurate while
parent assurances, optional examples, or cross-section qualifications are lost.
Compare complete statements, attached components, source evidence, and located
references separately; locating a citation does not attach its legal meaning.

Input: complete 42 USC Chapter 106, including notes and historical provisions,
from the existing official USLM release 119-102 archive. The source is pinned and
dated, not asserted to be the latest legal text. Preserve the complete selected
XML, source map, prepared text and archive/member digests. This is a statute;
section 676 of the CSBG Act corresponds to 42 USC 9908. We are not evaluating a
state's completed application, the entire grant compliance regime, or a CFR-only
document. The native existing reader yields 135,797 characters and 979 passages,
split into six production windows. No source content is removed to ease extraction.

Cases: save 24 manual meaning checks and 12 discovery questions before model calls.
They cover the complete thirteen-item State-plan content list and selected difficult
neighboring rules. Review every extracted item touching 9908 and those named checks,
plus all window outcomes/refusals. Whole-chapter semantic completeness is not claimed.
The labels are source-based assistant judgments and remain revisable. Historical
provisions must retain their time limits; examples must not become mandatory.

Arms: no new extraction treatment. One fresh run of the installed production
baseline. On its frozen output, compare source-only retrieval with identical
ranked hits plus existing linked evidence, using the existing BM25 top-three
diagnostic. Summaries-only is reported separately. Exact support retrieval is
not answer accuracy. Count full gains, partial gains, losses, and returned
evidence size without turning a small-sample threshold into a claim of no value.

Held constant: installed runtime, current generated CUE schemas and prompt,
gemini-3.8-flash, low thinking, temperature zero, 24,000-character windows,
16,384 output-token cap. One capture per window, no retries or follow-up audit.
All actual requests/settings and failures are retained. At most six model calls;
stop after this run, with a 20-minute wall-time bound on the capture process.
Zero temperature does not establish repeatability. No replication/general error
rate is claimed from one chapter.

Decision rule: report mechanical validity, source preservation, meaning checks,
reference location, retrieval benefit and token consumption independently.
Any material lost condition, invented obligation, missing required plan item, or
wrong actor prevents calling the output ready for unreviewed workflow generation.
Source-preserving discovery can still be useful with such draft gaps. Classify
each meaning check as faithful, partial, missing, or contradicted and cite the
specific source/output. Do not use schema validity or replay as semantic proof.

Verification: replay the original run with model setup disabled; verify source
passage retention and unchanged ranking across retrieval arms. Preserve original
captures and review history. Stop with saved findings, not another tuning cycle.
