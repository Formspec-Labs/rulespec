# Source and untouched-draft review before inventory/audit calls

Reviewer: this agent, manual raw-source/raw-output inspection. These are revisable
labels, not authoritative legal conclusions. No case-specific labels enter the
requests. The two new extractions are unedited provider outputs; neither is a
constructed fixture. All 13 flight-review and 26 PPE rows were read in raw output
against their full prepared source before this note.

## Equipment: saved development case, 14 claims

Primary known defect E1: C0000 preserves the (d) exception and (a)(1)-(a)(5)
conditions but omits paragraph (e)'s overriding special-flight-permit permission.
C0013 retains (e) separately. For this profile's complete standalone statement,
mere source availability or a separate unlinked C0013 does not repair C0000.
A useful finding must specifically identify (e)/special-flight-permit operation;
generic incompleteness, missing graph enrichment, or complaints about (d) alone
do not count. Preserve the exact saved source and all 14 claims. The new common
comparison includes all 14; the previous comparison assessed only C0000-C0009.
If both new arms detect E1, the inventory intervention has no unique benefit.

## 14 CFR 61.56: new source, 13 claims

- C0000 retains (a)'s explicit (b)/(f) exceptions and minimum hours. It is labelled
  statement/not_stated; normative-vs-definitional classification is uncertain,
  not the qualification experiment's primary outcome. Its explicit references
  need not reproduce the entire referenced paragraphs to count as retained limits.
- C0001 retains both required review components and instructor discretion. The
  (f) exemption concerns ground-training duration; do not automatically assert
  it cancels the rule-review content requirement. This point warrants uncertainty
  rather than a definitive false-negative label if the auditor disputes it.
- C0002 correctly permits three instructional glider flights, each to traffic
  pattern altitude, instead of the one flight-training hour only.
- C0003 retains the 24-calendar-month rule, rated aircraft, authorized instructor,
  logbook and (d)/(e)/(g) exceptions.
- C0004-C0006 retain the two (d) test/check alternatives and (e)'s proficiency
  program exemption, each with the time period. Their actors are unnecessarily
  long source clauses but source-supported, not invented actors.
- C0007 retains both (f) alternatives, time period and certificate-holder scope,
  and exempts the one hour of ground training only. **Counterexample F-C1:** no
  expansion to the full flight review or its flight-training hour.
- C0008 retains both student-pilot requirements: ongoing training and current
  solo-flight endorsement. Do not impose a flight-instructor certificate on it.
- C0009 retains combining requirements at the authorized instructor's discretion.
- **Primary defect F1, C0010:** the simulator/device permission states only the
  approved-course/training-center condition. It omits the (i)(2) landing-recency
  condition/approved-landings exception and the (i)(3) rated-aircraft condition.
  These are present separately in C0011/C0012, so whole-book retention is good
  while this standalone permission is incomplete. Count those two omitted
  conditions separately if the auditor finds only one; do not require duplicate
  parent records for whole-book coverage.
- C0011 retains simulator-use scope, the approved-landings exception, and the
  alternative § 61.57(a)/(b) references. **Counterexample F-C2:** approved landings
  do not remove C0010's approved-course or C0012's rated-aircraft requirements.
- C0012 retains simulator/device-use scope and the pilot's aircraft rating.

No parser refusals or rejected claims in this extraction. Qualifications are
largely retained; F1 is the new diagnostic defect without manufacturing a failure.

## 29 CFR 1910.132: new source, 26 claims

- C0000-C0002 retain general equipment provision/use/maintenance, employee-owned
  adequacy/maintenance/sanitation, and safe design. C0009 correctly prohibits use
  of defective/damaged equipment. **Counterexample P-C1:** paragraph (g)'s
  restriction on (d)/(f) must not be applied to these independent duties.
- **Primary defect P1:** C0003-C0006 (assessment/selection/communication/fit),
  C0008 (assessment certification) and C0010-C0013 (training/knowledge/use/retraining)
  omit paragraph (g)'s restricted section applicability. C0014 captures (g)
  separately, with no qualification targets; the affected standalone statements
  remain broader than their source. A finding must name the (g) limitation or its
  included/excluded sections, not just request more citations or concept links.
  C0007's non-mandatory appendix example is descriptive, not a mandatory method;
  treat any claim that it requires the appendix as a false positive.
- C0014 accurately states (g)'s included §§ 1910.133/.135/.136/.138/.140 and
  excluded §§ 1910.134/.137. Do not ask it to govern paragraph (h) payments.
- **Secondary defect P2:** C0015's employer-payment statement retains the explicit
  (h)(2)-(h)(6) exceptions but not the final note's precedence of another OSHA
  standard's payment provisions. C0025 preserves that precedence separately.
  This is the same standalone-meaning issue; count a specific precedence finding
  independently of P1. Do not infer what any unavailable external standard says.
- C0016 retains non-specialty footwear/prescription-eyewear and permission to wear
  the items off the job-site. C0017 retains employer-provided metatarsal guards,
  permission and employee request. C0018-C0020 retain all three (h)(4) alternatives,
  including use solely for weather protection in C0020.
- C0021 retains the replacement-payment duty and lost/intentionally-damaged
  exception. **Counterexample P-C2:** do not exempt accidental damage or remove
  adequacy/maintenance obligations merely because the employer need not pay.
- C0022 retains employee ownership/adequacy and both permission and nonreimbursement
  in one statement. A separate exemption record/modality field is optional; do
  not flag semantic loss solely because its main kind is permission.
- C0023 retains the prohibition on requiring employee payment and the (h)(2)-(h)(5)
  exception. The separate employee-volunteered-equipment rule must not turn this
  into unrestricted employer authority to compel purchase.
- C0024 retains the distinct 2008 effective and implementation dates. Its separate
  scope_text contains the implementation deadline only; event/time interpretation
  is secondary and any uncertainty must remain distinct from P1/P2.
- C0025 retains the other-standard payment precedence. Its statement/not_stated
  classification is debatable; the full precedence meaning is not missing.

Mechanical issue retained: 12 component refusals. The model attached the PPE
term definition to C0003, a requirement rather than a defining claim; existing
validation withheld the term and its references without losing the 26 statements.
This is shared input to both arms, not a failure of either inventory intervention.
Do not repair it or credit a term/alias complaint as a qualification finding.

## Assessment rules

Inspect all generated inventory meanings and every comparison rationale, including
correct judgments. For each primary defect record inventory presence, attachment
to affected meaning, comparison detection and false inheritance separately.
Preserve specific partial hits and label disagreements. Extra full-source units
are expected in B; their quantity alone is not a quality gain. In particular,
the whole-book presence of C0013 (equipment), C0011/C0012 (flight) or C0014/C0025
(PPE) must remain distinct from completeness of another standalone statement.


## Qualification-link experiment additions, before new calls

All cases above are now development data. Existing labels are retained, including
uncertainty; "new" above describes their original selection only.

Generation expectations: equipment (e) exception must target C0000 and preserve
the special-flight-permit limits. Flight (i)(2) and (i)(3) prerequisites must target
C0010; a grouped companion is acceptable if it retains both and the landings
exception. PPE (g) must target C0003-C0006/C0008/C0010-C0013 and preserve the exact
included/excluded sections. Payment precedence should target C0015, without
inventing another standard's content. Other targets require their own source
assessment; similarity or a correct primary target does not validate all targets.

Do not treat every equipment maintenance link as automatically false: (e)'s broad
notwithstanding language requires careful source assessment. Record uncertainty
if the supplied section cannot establish a target's exact effect. Do not count
mere presence of a qualifier elsewhere as fixing the baseline's standalone scope.
