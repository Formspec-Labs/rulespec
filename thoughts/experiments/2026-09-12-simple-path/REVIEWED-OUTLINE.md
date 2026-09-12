# Preparing a military-leave decision outline from the draft

This is an agent-reviewed preparation example for 5 USC 6323(a), based only on the
pinned release 119-102 source. It is not an executable workflow, a human approval,
or a determination of anyone's eligibility under current law. Claim indexes below
are zero-based positions in the retained [rulebook](extract/uslm/rulebook.json).

| Decision/input | Existing record | Source check and required treatment |
|---|---|---|
| Covered employee and service? | C0000, entitlement | Retains employee/DC employment, qualifying military status and duties, and the exclusion for Space Force sustained duty. Referenced definitions remain unresolved; retain them as dependencies before determining eligibility. |
| Full-time or part-time career employment? | C0002, proration | Source paragraph (a)(2) governs accrual. This must precede the calculation; it cannot be treated as an unrelated search result. |
| Annual accrual | C0001 plus C0002 | Use 20 days per fiscal year as the stated base rate. For part-time career employment, multiply the base rate by scheduled weekly hours / 40. Attach this branch explicitly to the accrual statement. |
| Unused leave | C0001 | Preserve the succeeding-fiscal-year wording and stated 20-day opening accumulation limit. Do not substitute the historical 15-day allowance from amendment notes. |
| Charging leave | C0003 | Preserve one-hour minimum and additional one-hour multiples. Source does not supply a universal conversion of days to hours. |

One substantive assembly correction is needed for this outline: connect C0002's
proration to C0001's annual accrual before presenting the rate as a usable rule.
The formula already exists in the draft; it was not rediscovered or added by audit.
The source lead-in's `Subject to paragraph (2)` supports that connection.

For a future form, these records suggest employee category, military/service
category, part-time status and scheduled hours as inputs. Required legal definitions,
who approves the request, and any employment-specific day/hour conversion need
source-supported resolution. The extracted employee is the beneficiary of the
entitlement, not an instruction that the employee must perform military service.

Leave under subsections (b), (c) and (d) has separate conditions and limits and is
outside this outline. In particular, do not use the unresolved section 8401(30)
reference as a verified technician definition: the source's editorial note says it
no longer describes that class. A complete implementation needs that issue resolved.

No original claim, source capture or review history was changed. This exercise
demonstrates reuse and the necessary review decisions, not measured human time saved.
