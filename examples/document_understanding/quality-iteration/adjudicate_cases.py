"""Materialize source-adjudicated reference answers and the matched-run review.

DECISIONS are Codex's authored judgments, not an algorithmic semantic scorer.
The script verifies their source/claim references and pins every assessed input.
Original cases, model assessments, extractions and review history are read only.
"""
from collections import Counter
from pathlib import Path

from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
REVIEWS = REPO / 'thoughts/reviews/2026-09-07-document-understanding-adversarial'

# Case, baseline verdict, temperature verdict, baseline claim aliases,
# temperature claim aliases, source-based rationale. Aliases are zero based.
DECISIONS = [
    ('R01', 'fail', 'fail', 'P000 P025', 'P000',
     'Both preserve infant scope, newborn emphasis and partial OR complete closure. Neither supplies an explicit exception relationship or unresolved modifier relation. The baseline retains an infant reference in the eyes recommendation, but a reference does not identify the qualifying claim.'),
    ('R02', 'pass', 'fail', 'P001 P002 P003', 'P001 P002',
     'The baseline preserves discreet support, permitted head tilt and the parent-face prohibition. Temperature 0.2 omits head tilt. The car-seat example remains illustrative; neither draft invents an angle.'),
    ('R03', 'fail', 'fail', 'P004 P006 P007', 'P003 P005',
     'Both preserve the six-month, likeness, identification and application-time standard as should, with a separate must-request consequence. Both omit the certificate processing-date caution. Temperature 0.2 also omits hairstyle/facial-hair acceptance subject to likeness.'),
    ('R04', 'pass', 'pass', 'P012 P013', 'P009 P010',
     'The applicant signature exemption uses not_required. The separate acceptance-agent back-signature instruction retains its hand-carry condition. Neither becomes an applicant duty or a universal ban on signatures.'),
    ('R05', 'fail', 'fail', 'P008 P009 P010 P011', 'P006 P007 P008',
     'Either background damage or non-material facial damage is an immaterial category. Baseline choice_text capitalizes AND, leaving category membership ambiguous despite preserving both examples and acceptance. This is an ambiguity failure, not evidence of executable AND enforcement. Temperature 0.2 omits the explicit immaterial-damage acceptance.'),
    ('R06', 'pass', 'pass', 'P021', 'P018',
     'Both retain should, temporary medical need AND urgent OR emergency travel, limited validity and endorsement 46. Neither imports a one-year duration.'),
    ('R07', 'pass', 'fail', 'P016 P025 P027 P028', 'P013 P022 P023',
     'The baseline distinguishes must for the medical-glasses statement from should for open/visible eyes, rare evidence and supervisor referral. Temperature 0.2 preserves force on its surviving records but omits the eyes recommendation, so it fails this case\'s positive coverage requirement.'),
    ('R08', 'pass', 'pass', 'P030 P031', 'P025 P026',
     'The applicant re-execution duty retains missing photograph AND acceptance-facility scope, separate from the passport specialist suspension duty. An otherwise complete DS-11 is outside the stated case.'),
    ('R09', 'fail', 'fail', 'P015 P016 P017 P018 P019 P020', 'P011 P012 P013 P014 P015 P016 P017',
     'Medical circumstances, signed evidence, lens necessity and the four child conditions survive in meaning. Both omit the four explicit child relationships. Temperature 0.2 correctly links the medical-glasses exception to the glasses ban, but that does not restore the missing child edges. No existing resolved target is alleged to be corrupt.'),
    ('R10', 'fail', 'fail', 'P022 P024', 'P019 P020',
     'Both preserve the disability-related inability to produce the expression and discretionary acceptance. Neither connects this qualification to the expression baseline or explicitly marks an unresolved modifier relationship.'),
    ('R11', 'pass', 'pass', 'P026 P027', 'P021 P022',
     'Both preserve discretionary acceptance for medical inability to open one OR both eyes. The separate evidence recommendation keeps rare AND unlikely medical cause, should, and a signed statement. It is not a universal prerequisite.'),
    ('R12', 'pass', 'fail', 'P014', '',
     'The baseline retains the application as the returned object, printing-defect context and requesting a new photograph as the purpose. It uses descriptive possibility. Temperature 0.2 omits the proposition.'),
    ('R13', 'pass', 'pass', 'P029 P032', 'P024 P027',
     'Both preserve 8 FAM 1001.2 as an unresolved reference whose context specifically concerns DS-5504 photo importing. Both separately retain missing-photo DS-5504 suspension; neither invents remote import procedures.'),
    ('R14', 'pass', 'pass', 'P029 P030 P032', 'P024 P025 P027',
     'Both retain DS-11 OR DS-82 counter refusal, DS-11 acceptance-facility suspension, DS-82 OR DS-5504 suspension and both IRL references. No fixed record count or exclusive IRL mapping is required.'),
    ('R15', 'fail', 'fail', 'P014', '',
     'Both omit certificate-related advisory/descriptive material. The baseline correctly treats printing-defect return as possible; temperature 0.2 omits that too. Avoiding invented obligations does not satisfy the positive requirement to retain the supplied guidance.'),
    ('NREG-01', 'pass', 'pass', 'N002', 'N002',
     'The contiguous-section records retain all six leaf options, the nested court-order grouping, one-or-more choice, married-name exception reference and 22 CFR 51.25. This pass is specific to the contiguous input: both excerpt runs visibly refuse their list candidate for component evidence outside the supplied request.'),
    ('NREG-02', 'pass', 'pass', 'N006 N007', 'N007 N008',
     'Both final matched runs retain the more-than-one-year, DS-11 and unchanged-ID parent case, insufficient time before urgent OR emergency travel, discretionary limited validity and requested name. The suspension duty remains separate. Earlier names-04 failed this case; it is preserved and the improved checker detects its lost scope.'),
    ('NREG-03', 'pass', 'pass', 'N009 N010', 'N011 N012',
     'Both retain the within-one-year DS-11 exemption as not_required and the separate must-submit documentation duty if ID remains unchanged. The exemption does not target the older-change suspension or the documentation duty.'),
    ('NREG-04', 'fail', 'fail', 'E014 E015 E016', 'E015 E016 E017',
     'Both leave the court-document both-names baseline unqualified. The confidentiality-scoped application disclosure duty and additional-evidence permission survive, but the exception itself and correct target are absent. The separate saved correction adds the correct relationship without replacing those duties; that is corrected output, not automatic extraction success.'),
    ('NREG-05', 'pass', 'pass', 'E003 E004 E013', 'N004 N005 E014',
     'A positive local exception target exists in baseline excerpts and in the temperature contiguous run. In each, documentation permitting previous-name use targets that use prohibition, not pending-name clearance. The separate deliberately wrong-target audit tests whether the checker challenges a structurally valid but semantically unrelated edge.'),
    ('NREG-06', 'pass', 'pass', 'E010 E011 E012 E013', 'E011 E012 E013 E014',
     'Both preserve finality, distinct passport/FS-240 new-name prohibitions and clearance despite nonfinal change and nonissuance. Temperature 0.2 scope_text preserves even though/even if despite compressed summary wording. Its ellipsized logic_text remains uninterpreted; this semantic pass does not certify exact component anchoring or executable logic.'),
    ('NREG-07', 'pass', 'pass', 'E017 E018 E019', 'E018 E019 E020',
     'Both preserve the mandatory multipart-name appearance determination and the two should spacing branches. The second branch retains no previous passport AND a space in citizenship/nationality evidence OR ID.'),
    ('NREG-08', 'pass', 'pass', 'E020', 'E021',
     'Both preserve clear verbal OR written preference, add OR remove spacing, and discretionary may. The object remains spacing rather than an unrelated pronoun referent.'),
    ('NREG-09', 'fail', 'fail', 'E021 E022', 'E022 E023',
     'Both preserve the general-family recommendation with the preference caveat and the distinct special-issuance sponsor recommendation. Neither emits the required explicit preference-exception target. No unstated precedence between the notes is inferred.'),
    ('NREG-10', 'fail', 'fail', '', '',
     'Both omit the spacing and suffix generally-insufficient-rewrite statements, their clear-preference-disregard exceptions and associated reference. No adjacent spacing or ordinal duty substitutes for these qualified statements.'),
    ('NREG-11', 'fail', 'pass', 'N005 N008', 'N006 N009',
     'Both retain possible identity-evidence requirements with their purpose and citation. Baseline keeps generally-needs-documentation only as context for a notation duty; it supplies no independently referenceable meaning for it. Temperature 0.2 restores the explicit qualified statement without making it a universal duty.'),
    ('NREG-12', 'pass', 'pass', 'N006 N007', 'N007 N008',
     'Both keep DS-11 as the form in the application/timing context and the application as the suspension object. Neither represents the form as the thing that underwent a material name change or invents a filing duty from the condition.'),
    ('NREG-13', 'fail', 'pass', 'E000', 'E000 E001',
     'Baseline omits the applicant definition including DS-2060. Temperature 0.2 retains it. Both retain the chapter-scoped definition of minor applicants with under-18 and un-emancipated predicates.'),
    ('NREG-14', 'fail', 'fail', 'E023', 'E024',
     'Both retain ordinal conversion and the correct suffix section, fixing the earlier section-order defect. Both omit the Sr./Señor descriptive possibility and its conditional ranks-and-titles referral. Neither complete case passes on the strength of the ordinal rule alone.'),
    ('NREG-15', 'pass', 'pass', '', '',
     'Process demonstration only: all three original correction actions replay, prior graph nodes and attribution remain intact, current targets resolve, and reopening preserves the result. The pre-existing suspension and recent-ID exemption survive. Missing might-require-ID and generally-needs-documentation content remains disclosed; these actions do not establish complete source coverage.'),
]


def main():
    output = ROOT / 'reference-assessment'
    output.mkdir(exist_ok=False)
    photos = e._load(REVIEWS / 'photos-coverage-claim-audit.json')
    names = e._load(REVIEWS / 'names-adversarial-regressions.json')
    pcases = {c['id']: c for c in photos['regression_cases']}
    nc = {c['case_id']: c for c in names['cases']}
    coverage = {c['unit_id']: c['source'] for c in photos['coverage']}
    run_names = {'baseline': {'P': 'photos-03', 'N': 'names-05', 'E': 'names-excerpts-03'},
                 't02': {'P': 'photos-t02', 'N': 'names-t02', 'E': 'names-excerpts-t02'}}
    books = {v: {p: e._load(ROOT / 'runs' / n / 'rulebook.json') for p, n in runs.items()}
             for v, runs in run_names.items()}
    pins = {f'runs/{name}/rulebook.json': e._digest((ROOT / 'runs' / name / 'rulebook.json').read_bytes())
            for runs in run_names.values() for name in runs.values()}
    references, results = [], []
    assert len(DECISIONS) == 30 and len({r[0] for r in DECISIONS}) == 30
    for case_id, baseline, t02, bids, tids, reason in DECISIONS:
        if case_id in pcases:
            case = pcases[case_id]
            title, expected = case['case'], [case['expected']]
            source = [coverage[u] for u in case['unit_ids']]
            text = books['baseline']['P']['document']['text']
            for s in source:
                assert text[s['start']:s['end']] == s['exact_text']
            controls = [{'criterion': case['negative_control']}]
        else:
            case = nc[case_id]
            title, expected = case['name'], case['expected_invariants']
            source = case['source_pieces']
            controls = case['negative_examples']
            for s in source:
                text = books['baseline']['N' if s['source_input'] == 'contiguous' else 'E']['document']['text']
                assert text[s['start']:s['end']] == s['text']
        references.append({'case_id': case_id, 'name': title, 'expected_invariants': expected,
                           'source_evidence': source, 'negative_controls': controls,
                           'scope': 'correction_process' if case_id == 'NREG-15' else 'automatic_extraction'})
        row = {'case_id': case_id, 'name': title, 'rationale': reason}
        for variant, status, aliases in [('baseline', baseline, bids), ('t02', t02, tids)]:
            evidence = []
            for alias in aliases.split():
                prefix, index = alias[0], int(alias[1:])
                book = books[variant][prefix]
                claim = book['accepted'][index]
                evidence.append({'alias': alias, 'run': run_names[variant][prefix],
                                 'claim_id': claim['id'], 'claim': claim})
            row[variant] = {'status': status, 'inspected_records': evidence}
        if case_id == 'NREG-15':
            assert e._load(ROOT / 'review-demo/verification.json')['status'] == 'verified'
            row['process_evidence'] = 'review-demo/verification.json'
        results.append(row)
    metadata = {
        'schema_version': 'document-understanding-reference-assessment/1',
        'created_at': e._now(), 'reference_status': 'adjudicated',
        'actor': 'Codex source adjudication', 'actor_kind': 'aiAgent',
        'purpose': 'Project gold reference set for these known development cases. Reference answers are versioned and correctable, not an assertion of infallibility or general extraction accuracy.',
        'judgment_boundary': 'A pass establishes the named meaning invariants. It does not certify every component anchor, remote rule, schema-semantic equivalence or executable logic. Inspected records can include nearby records that demonstrate an omission.',
        'temperature_boundary': 'Three source pairs have identical recorded requests except temperature 0 versus 0.2. One sample per source/temperature; cases overlap. NREG-15 is a separate process demonstration, not another extraction sample.',
        'inputs_sha256': pins,
        'negative_control_boundary': 'Retained synthetic examples define expected defects. Their presence is not proof of application detection. negative-controls/ contains the separate live checker demonstrations.',
    }
    counts = {v: dict(Counter(r[v]['status'] for r in results if r['case_id'] != 'NREG-15'))
              for v in ['baseline', 't02']}
    e._save(output / 'reference-cases.json', {**metadata, 'cases': references})
    e._save(output / 'results.json', {**metadata, 'automatic_case_counts': counts, 'results': results})
    lines = ['# Source-adjudicated case results', '',
             'These are the reference decisions for this iteration, authored by Codex from the saved source and full claim fields. The JSON pins every assessed rulebook and includes source evidence, expected invariants, original negative controls, claim IDs and rationale. Reference answers can be revised with evidence.', '',
             'Baseline means `names-05`, `photos-03` and `names-excerpts-03`, all at temperature 0. The paired `*-t02` runs differ only in temperature. A pass addresses the named case; component anchoring and uninterpreted logic can still need work.', '',
             f'Across 29 automatic-extraction cases: baseline {counts["baseline"]}; temperature 0.2 {counts["t02"]}. NREG-15 separately passes the correction-process checks. These overlapping development cases do not estimate general accuracy.', '',
             '| Case | Temperature 0 | Temperature 0.2 | Decision and evidence |',
             '| --- | --- | --- | --- |']
    for row in results:
        lines.append(f'| {row["case_id"]}: {row["name"]} | {row["baseline"]["status"]} | {row["t02"]["status"]} | {row["rationale"]} |')
    lines.extend(['', '## Differences from automatic assessment', '',
                  'The model assessment is supporting evidence, not the final verdict. Its baseline R01 explanation incorrectly treated newborn emphasis as absent; the actual failure is the missing explicit relation. R05 is an ambiguous category representation, not demonstrated executable conjunction. Its NREG-09 pass overlooks the required explicit preference edge. Temperature photo passes for R07 and R15 overlook required content that the extractor omitted. Both temperature names assessment batches exhausted their output budget and remain unknown; the source adjudication above supplies their reference decisions.', '',
                  'The first fresh audit also passed factual statements typed as descriptive possibility. Source review identified that error; the informed fresh-02 follow-up corrects the distinction. This disagreement is retained in [fresh assessment](../fresh-assessment/summary.json).', ''])
    (output / 'RESULTS.md').write_text('\n'.join(lines))
    e._write_manifest(output)
    print(counts)


if __name__ == '__main__':
    main()
