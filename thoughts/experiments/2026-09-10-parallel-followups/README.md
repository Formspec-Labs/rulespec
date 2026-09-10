# Parallel follow-ups: smaller link edits are the useful next candidate

**Keep the current production workflow. Consider integrating only the smaller
existing-exemption link-edit response next, with its normal source challenge and
review checks.** It preserved the five tested links with substantially less output.
The other treatments did not establish a production benefit.

The completed production changes were committed as `1426960`; prior research and
captures as `39f6c3f`. Three agents then ran separate experiments without changing
production. The third track tested link edits and actor evidence independently.

| Comparison | Observed result | Decision |
| --- | --- | --- |
| [Shared evidence compression](../2026-09-10-parallel-compression/README.md) | Input tokens −38.9%, total −5.0%; six expected applied links fell to five on two cases | Failed useful-output gate; remain experimental |
| [Explicit target enumeration](../2026-09-10-parallel-targets/README.md) | Both arms applied 7/8 primary expected links; enumeration used 23.1% more total tokens | No measured improvement; no adoption |
| [Smaller existing-exemption link edits](../2026-09-10-parallel-copying/README.md) | Both applied all five correct links; proposal answer tokens −85.8%, proposal plus challenge total −9.0% | Bounded efficiency improvement; next integration candidate |
| [Actor passage references](../2026-09-10-parallel-copying/README.md) | Current distinctive-quote guidance and references both grounded 4/4 fixed actors; references used 3.86× total tokens and selected excess context | No measured grounding gain over current advice; no adoption |

These percentages describe the stated comparisons, not overall production cost or
population accuracy. Smaller link edits made no observed accuracy improvement:
the full-field baseline also copied all five records correctly. The actor task
supplied the labels and assessed their support; it did not test actor discovery.

## Findings from source and output review

The primary agent read the fresh mobile-phone source, the refrigerant and seatbelt
sources/drafts, proposal targets, challenge explanations and application results.
These readings agree with the agents' principal conclusions and retain these limits:

- Compression preserved source information but changed model behavior in this
  sample. On the fresh mobile-phone source, B bundled a clear driver emergency
  exception with an uncertain carrier target. Its challenge explicitly recognized
  the driver exception but rejected the entire proposal. The certain edge was
  lost. Carrier applicability was uncertain before the run; this is not a legal
  determination that the carrier target is false. Both railroad arms retained
  all five links, including the earlier whitespace failure.
- Both target-enumeration arms still omitted the refrigerant exemption's link to
  the service duty. Both now succeed on the five seatbelt primary edges, so an
  improvement over older seatbelt captures cannot be credited to enumeration.
  The added matrix does not expose per-pair output; we cannot establish that every
  candidate was assessed merely because the prompt requested it.
- The actor track initially used a short-quote diagnostic rather than production's
  distinctive-quote guidance. We retained it and preregistered a separate fresh
  four-call comparison against the actual guidance. That comparison controls the
  production conclusion. The broader reference selections include the necessary
  possession context but also unrelated alcohol restrictions. Current quote-only
  actor fields still cannot preserve arbitrary multiple selected spans or identify
  identical repeated full passages by offset; the experiment does not implement
  that persistence path.
- Correctly resolving a source reference does not establish a correct target or
  complete meaning. The compact link adapter still admits a syntactically valid
  wrong target; semantic challenge remains necessary.

## What to do next

1. A narrow smaller-link-edit integration can reconstruct unchanged exemption
   fields deterministically from the selected current record, then reuse existing
   validation, challenge and review. Keep additions and substantive edits on their
   existing paths. Verify stale targets and revision handling before adoption.
2. Save **independent per-target judgments** as the next meaning hypothesis. The
   compression failure shows why a disputed target should not necessarily discard
   a separately supported edge; the target trial shows why a consideration prompt
   alone does not prove coverage. Test explicit supported/unsupported/unknown
   decisions using existing aliases and evidence references. This has not been
   tested here and must not silently alter multi-target application semantics.
3. Leave compression and actor reference fields out of production for now. Further
   trials need a specific unresolved case or a changed mechanism, rather than
   repeating these prompt treatments until a favorable response appears.

No new experimental variant was integrated. This report is a research decision,
not authorization for the proposed next implementation.

## Accounting and verification

The three tracks made **29 new live calls**, including the shared fresh extraction
and the actor comparator correction, using **466,628 reported total tokens**.
[usage.json](usage.json) independently totals original request/response pairs and
their hashes, excluding copied baseline/workspace captures. One extraction omitted
its thinking-token field; that absence is retained, not treated as measured zero.
No retries or full audits were added. Token totals are not dollar charges.

Each track retained plans, raw requests/responses, failures and decoding replay.
Source reconstruction and review reload/export checks passed; the target and link
tracks also reconstructed final review state from events. Compression's decoding
replay does not independently reconstruct every review event. The existing
production implementation had passed 427 package and six schema-generator tests
before these experiments; production files remained unchanged during the trials.

Samples are small, mostly development sources, with one fresh mobile-phone source
and a constructed actor/approver control. Agent assessments are revisable, with
partial blinding where possible. No general completeness or accuracy claim follows.
