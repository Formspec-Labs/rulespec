# What the unchanged relationship pass actually proposed

Read after hashing the anonymous comparison review. Reviewed raw proposal payloads,
all populated meaning/evidence fields, target aliases, and observations against
the frozen source and original claims. Empty fields were hidden for reading only;
the unchanged decoder validated full payloads and retained original captures.
These are source-based, revisable judgments, not automatic acceptance decisions.

Fourteen proposals, nineteen target associations, zero refused proposals. Ten
proposals use existing exemption `link`; four add companion exceptions. None
proposes a condition/prerequisite or targets a main defect with its missing
qualification. No call reached the eight-proposal cap (three, five, six).

| Case / proposal | Proposed targets | Manual assessment |
| --- | --- | --- |
| Equipment P0000 | C0000 | Supported: the (d) exception to the (a) prohibition; already retained in C0000 prose |
| Equipment P0001 | C0008 | Supported: the airworthiness-directive exception to the corresponding MEL exclusion; does not remove the other two exclusions |
| Equipment P0002 | C0010 | Supported: operations under (a)/(c) excluded from the (d) permission |
| Flight P0000 | C0004 → C0003 | Supported: (d)(1) check/test exemption to required flight review |
| Flight P0001 | C0005 → C0003 | Supported: (d)(2) practical-test alternatives retained |
| Flight P0002 | C0006 → C0003 | Supported: (e) proficiency-program exemption |
| Flight P0003 | C0007 → C0000 | Supported with its retained meaning: only the ground-training hour is exempted; the target includes both hours, so the edge alone cannot be read as cancelling the full target |
| Flight P0004 | C0008 → C0003 | Supported: student-pilot exemption retains training plus current solo endorsement |
| PPE P0000 | C0016 → C0015, C0023 | Both supported by (h)(1)/(h)(6) references to (h)(2); off-site-wear permission remains required |
| PPE P0001 | C0017 → C0015, C0023 | Both supported by their (h)(3) exceptions, subject to the preserved employer-provided guards and employee-request conditions; not blanket authority to compel purchase |
| PPE P0002 | C0018 → C0015, C0023 | Both supported: logging-boots exemption |
| PPE P0003 | C0019 → C0015, C0023 | Both supported: everyday-clothing exemption |
| PPE P0004 | C0020 → C0015, C0023 | Both supported: ordinary items used solely for weather protection |
| PPE P0005 | C0021 | Supported: loss or intentional damage exception to replacement payment; not accidental damage or release from maintenance duties |

All populated quotations are supplied source text; deterministic replay confirms
the same grounding/decoding. `link` operations copy the original exemption meaning
and evidence while changing relation/targets. The four additions preserve limited
exceptions; their actor/action/object fields, where populated, match quoted source.
References remain references, not claims about unavailable external provisions.
No additional structured terms, numeric values, claimants or effective periods
were invented in these proposals. No hidden reasoning is inferred from rationales.

## What it omitted and why the result is informative

Equipment E1: no (e) → C0000 proposal. The generator explicitly says the
"Notwithstanding" lead-in is already represented in C0013 and "does not operate
as an independent exception excusing duties." That overlooks its effect on the
opening prohibition. Its otherwise supported P0000 is the already-present (d)
exception, not the missing special-flight-permit route.

Flight F1: five exemption links, but no (i)(2)/(i)(3) prerequisite links to C0010.
No observation acknowledges those missing connections. The schema and prompt
permit condition records, but that capability was not exercised here.

PPE P1: no (g) scope proposal. The observation says (g) is separately represented
in C0014 and "incorporated into the meaning of relevant rules." The original nine
claim meanings lack it; the shared inventory contains it. Confusing inventory
meaning or whole-book presence with current-claim completeness is a plausible
explanation, not a proven account of the model's hidden process.

PPE P2: no precedence → C0015 proposal. Again the observation cites standalone
C0025 as already represented. A separate description of precedence does not
establish which current claims preserve its effect.

The automatic discovery/selection step failed to supply the treatment needed to
test whether correct target aliases fix E1/F1/P2. Both PPE checkers nevertheless
found P1 from their shared inventory/source. Broad workflow failure is observed;
the efficacy of correctly supplied primary links is unresolved. The result does
not invalidate existing relationship IDs, schemas, or the production challenge
stage, which was deliberately not run here.
