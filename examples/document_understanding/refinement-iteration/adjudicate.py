"""Save Codex's source adjudication; this is not an automatic semantic scorer.

The reference cases and fresh expectations predate the measured runs. Authored
decisions stay outside extraction/refinement prompts. The script verifies their
claim references and pins the exact inputs assessed.
"""
from collections import Counter
from pathlib import Path

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.core import CANDIDATE_SCHEMA

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'quality-iteration'
SAMPLES = {'N': 'names', 'P': 'photos', 'E': 'names-excerpts'}
FAILED = {'01': {'R01', 'R05', 'R10', 'NREG-04'}, '02': {'R01', 'R03', 'R05', 'R15'}}
EXTRA = {
    '01': {'R03': 'P033', 'R09': 'P034', 'R15': 'P033', 'NREG-09': 'E032',
           'NREG-10': 'E028 E031', 'NREG-11': 'N011 E024', 'NREG-13': 'E021', 'NREG-14': 'E029 E030'},
    '02': {'R09': 'P033 P034', 'R10': 'P035', 'R11': 'P036', 'NREG-04': 'E029',
           'NREG-05': 'N012', 'NREG-09': 'E036', 'NREG-10': 'E032 E035',
           'NREG-11': 'N011 E027 E028', 'NREG-13': 'E024', 'NREG-14': 'E033 E034'},
}
REASONS = {
    'R01': ('Infant scope, newborn emphasis and partial OR complete closure survive, but neither revision creates an explicit infant exception record/link. Revision 2 reports the citation as remote despite local infant meaning being available elsewhere in the supplied sample.'),
    'R02': 'Discreet infant support, optional head tilt and the parent-face prohibition remain unchanged and distinct.',
    'R03': 'The baseline retains the coordinated six-month/likeness/identification standard, should force, separate must-request consequence and qualified hairstyle/facial-hair acceptance. Revision 1 adds the certificate timing caution. Revision 2 leaves that caution unresolved as practical guidance without a duty, so the case fails again.',
    'R04': 'Applicant not_required and the distinct hand-carry acceptance-agent instruction remain unchanged.',
    'R05': 'Both immaterial damage categories and acceptance remain present, but the capitalized AND in choice_text still makes independent category membership ambiguous. Neither revision corrects it.',
    'R06': 'Temporary medical need AND urgent OR emergency travel, should, limited validity and endorsement 46 remain intact; no duration is invented.',
    'R07': 'The mandatory signed medical statement remains distinct from should guidance for visible/open eyes, rare evidence and referral. Companion qualifications do not upgrade the baselines.',
    'R08': 'The DS-11 re-execution duty retains missing-photo AND acceptance-facility scope and its separate actor; the suspension duty remains current.',
    'R09': 'Both revisions add the four child links under medical acceptance of eyeglasses. Signed medical evidence, frames/glare/shadows rules and the additional dark/tint necessity remain. Revision 2 also adds the explicit medical exception to the glasses prohibition.',
    'R10': 'Revision 1 leaves the disability permission without a companion modifier. Revision 2 links the physical/mental-disability inability case to the natural-expression recommendation while preserving discretionary acceptance.',
    'R11': 'One OR both eyes with medical causation remains discretionary. The rare AND unlikely-medical-cause signed-statement recommendation remains separate. Revision 2 adds the medical-eye exception to the eyes recommendation without making the rare evidence recommendation universal.',
    'R12': 'The application remains the returned object, with printing-defect context and a new photograph as the purpose. The descriptive possibility remains unchanged.',
    'R13': 'The unresolved 8 FAM 1001.2 reference still specifically concerns DS-5504 photo importing; the separate missing-photo DS-5504 suspension survives.',
    'R14': 'DS-11 OR DS-82 counter refusal, DS-11 facility suspension, DS-82 OR DS-5504 suspension and both information-request references survive.',
    'R15': 'Revision 1 retains the certificate caution as descriptive possibility with the reuse note as context; reasonableness, signature explanation and printing-defect meaning remain non-mandatory. Revision 2 declines to restore the certificate note, so positive advisory/descriptive coverage fails.',
    'NREG-01': 'The contiguous grouped requirement retains all six leaf options, nested court-order grouping, one-or-more and 22 CFR 51.25. Both edits bring the married-name reference into summary/scope. Its extent remains governed by the unresolved external section; these records do not supply an exemption for every married applicant.',
    'NREG-02': 'The complete older-than-one-year/material-name-change/DS-11/unchanged-ID case and insufficient time before urgent OR emergency travel remain on discretionary limited-validity issuance in the requested name. The separate suspension duty survives.',
    'NREG-03': 'The recent DS-11 branch retains not_required for new-name ID and must for documentation if ID is unchanged. Neither is reassigned to the older-change duty.',
    'NREG-04': 'Revision 1 leaves the confidential-name exception missing. Revision 2 adds an exception with not_stated force targeting the court-document both-names requirement. Possible receipt is not a standalone legal permission. The application disclosure duty and additional nationality OR identity evidence permission under both citations remain unchanged.',
    'NREG-05': 'The original excerpt exception still targets previous-name use, not pending-name clearance. Revision 2 supplies another correct local example in the contiguous section. Separate deliberate-control results remain separate from these passes.',
    'NREG-06': 'Finality, passport and FS-240 new-name prohibitions, and mandatory clearance despite nonfinality/nonissuance remain. Revision 1 adds court-order context to three records without turning despite into an exemption; revision 2 leaves the baseline records intact.',
    'NREG-07': 'Mandatory appearance determination and both should spacing branches retain multipart scope, no-previous-passport where required, and the citizenship/nationality evidence OR ID alternatives.',
    'NREG-08': 'Clear verbal OR written preference and add OR remove spacing remain discretionary and correctly refer to spacing.',
    'NREG-09': 'Both revisions explicitly link the clear family preference exception to general-family consistency and leave the sponsor note separate. Revision 2 uses clearer recommendation-relaxing wording. Neither settles precedence over special-issuance guidance.',
    'NREG-10': 'Both revisions add separate spacing and suffix statements with generally-not-sufficient force, the Department-disregarded-clear-preference caveat and unresolved 8 FAM 1001.2. Neither mandates or guarantees a rewrite. The meaning passes without requiring a separately split exception record.',
    'NREG-11': 'Both revisions add independently referenceable generally-needs-documentation guidance as possible, preserving the existing might-require-ID statement, its purpose and citation. Revision 2 also restores the missing might statement in the excerpt input.',
    'NREG-12': 'DS-11 remains the form in the timing/application context; the applicant has the material name change, and the application is suspended. No filing duty is invented.',
    'NREG-13': 'Both revisions recover applicant including DS-2060. The existing minor definition retains under-18, un-emancipated and chapter scope.',
    'NREG-14': 'Both revisions recover Sr./Señor as descriptive possibility and the conditional ranks-and-titles referral with its antecedent and reference. Ordinal conversion and suffix section remain intact.',
    'NREG-15': 'All three original correction actions replay under the delivered code; prior graph nodes, AI attribution, current targets and reopened state are verified. This process test does not establish source completeness.',
}

ACTION_NOTES = {
 ('01', 'names'): ['clarification: married-name reference in scope; all choices preserved', 'new meaning: qualified need for ID-change documentation'],
 ('01', 'photos'): ['new meaning: certificate processing-date caution, no new duty', 'new links: medical acceptance governs all four child rules', 'new links: missing-photo heading governs the five local handling rules'],
 ('01', 'names-excerpts'): ['new definition: applicant including DS-2060', 'new definition: material discrepancy', 'new meaning: documentation duty with all six leaves; court parent/citation presentation is less complete than revision 2', 'new meaning: generally needs documentation', 'clarification: court context on pending-passport prohibition', 'clarification: court context on pending-FS-240 prohibition', 'clarification: court context without removing despite-clearance duty', 'new meaning: spacing rewrite caveat', 'new meaning: Sr./Señor descriptive possibility', 'new meaning: conditional ranks/titles referral', 'new meaning: suffix rewrite caveat', 'new link: general-family preference exception; not-required wording is less precise than revision 2'],
 ('02', 'names'): ['clarification: external married-name exception reference; no remote eligibility criteria supplied', 'new meaning: generally needs documentation', 'new link: previous-name documentation exception; summary leaks a request-local C alias'],
 ('02', 'photos'): ['new links: medical acceptance to four child rules', 'new link: medical exception to glasses prohibition', 'new link: disability inability to natural-expression recommendation', 'new link: medically closed eyes to eyes recommendation; rare-evidence duty remains separate'],
 ('02', 'names-excerpts'): ['new definition: applicant including DS-2060', 'new definition: material discrepancy', 'new meaning: documentation duty with all options, nested grouping and citations', 'new meaning: possible ID requirement and identity purpose', 'new meaning: generally needs documentation', 'new link: confidential former name to court-document requirement, preserving application disclosure and evidence permission', 'new meaning: uppercase printing as a descriptive statement', 'new meaning: multipart uppercase appearance and spacing explanation', 'new meaning: spacing rewrite caveat', 'new meaning: Sr./Señor descriptive possibility', 'new meaning: conditional ranks/titles referral', 'new meaning: suffix rewrite caveat', 'new link: family preference to general-family recommendation'],
}


def claim_view(book, claim):
    ids = {c['id']: f'C{i:04d}' for i, c in enumerate(book['accepted'])}
    keys = set(CANDIDATE_SCHEMA['properties']) | {'id', 'rule_id', 'target_ids', 'evidence', 'reference_links', 'issues', 'link_issues'}
    return {'alias': ids.get(claim['id'], 'superseded'), 'target_aliases': [ids.get(t, 'superseded') for t in claim['target_ids']],
            'claim': {k: v for k, v in claim.items() if k in keys}}


def main():
    output = ROOT / 'assessment'
    output.mkdir(exist_ok=True)
    reference_path = OLD / 'reference-assessment/reference-cases.json'
    references = {c['case_id']: c for c in e._load(reference_path)['cases']}
    original = e._load(OLD / 'reference-assessment/results.json')['results']
    books = {it: {prefix: e._load(ROOT / f'runs-{it}' / name / 'after.json') for prefix, name in SAMPLES.items()} for it in ['01', '02']}
    rows, actions, pins = [], [], {}
    old_names = {'names-05': 'N', 'photos-03': 'P', 'names-excerpts-03': 'E'}
    for case in original:
        identity = case['case_id']
        row = {'case_id': identity, 'name': case['name'], 'expected_invariants': references[identity]['expected_invariants'],
               'source_evidence': references[identity]['source_evidence'], 'baseline': case['baseline']['status'],
               'rationale': REASONS[identity], 'scope': references[identity]['scope']}
        for it in ['01', '02']:
            selected = {}
            for old in case['baseline']['inspected_records']:
                prefix = old_names[old['run']]
                book = books[it][prefix]
                current = next(c for c in book['accepted'] if c['rule_id'] == old['claim']['rule_id'])
                selected[(prefix, current['id'])] = {'sample': SAMPLES[prefix], **claim_view(book, current)}
            for alias in EXTRA[it].get(identity, '').split():
                prefix, index = alias[0], int(alias[1:])
                book = books[it][prefix]
                claim = book['accepted'][index]
                selected[(prefix, claim['id'])] = {'sample': SAMPLES[prefix], **claim_view(book, claim)}
            row['revision_' + it] = {'status': 'fail' if identity in FAILED[it] else 'pass', 'inspected_records': list(selected.values())}
        rows.append(row)
    assert len(rows) == 30 and len(REASONS) == 30
    for it in ['01', '02']:
        for prefix, name in SAMPLES.items():
            directory = ROOT / f'runs-{it}' / name
            for filename in ['before.json', 'after.json', 'changes.json', 'manifest.json']:
                pins[f'runs-{it}/{name}/{filename}'] = e._digest((directory / filename).read_bytes())
            changes = e._load(directory / 'changes.json')
            notes = ACTION_NOTES[(it, name)]
            assert len(changes) == len(notes)
            for index, (change, note) in enumerate(zip(changes, notes, strict=True)):
                claim = change['event']['replacements'][0]
                text = books[it][prefix]['document']['text']
                assert text[claim['start']:claim['end']] == claim['quote']
                actions.append({'iteration': it, 'sample': name, 'action_index': index,
                    'operation': change['action']['action'], 'event_id': change['event']['id'],
                    'decision': 'source_supported', 'assessment': note, 'duplicate_meaning': False,
                    **claim_view(books[it][prefix], claim)})
    counts = {stage: dict(Counter(row['baseline'] if stage == 'baseline' else row[stage]['status']
                for row in rows if row['scope'] == 'automatic_extraction')) for stage in ['baseline', 'revision_01', 'revision_02']}
    assert counts == {'baseline': {'fail': 12, 'pass': 17}, 'revision_01': {'fail': 4, 'pass': 25}, 'revision_02': {'fail': 4, 'pass': 25}}
    assert all(row['revision_02']['status'] == 'pass' for row in rows if row['baseline'] == 'pass')
    metadata = {'created_at': e._now(), 'actor': 'Codex source adjudication', 'actor_kind': 'aiAgent',
        'reference_status': 'project_gold_versioned_and_correctable', 'provider_calls': 0,
        'boundary': 'Named source-meaning invariants, assessed with full meaning, explicit scope/context and links. Not general accuracy, human review, executable semantics or certification of every component anchor.',
        'original_reference_sha256': e._digest(reference_path.read_bytes()), 'inputs_sha256': pins}
    e._save(output / 'saved-cases.json', {**metadata, 'automatic_case_counts': counts, 'results': rows})
    e._save(output / 'applied-changes.json', {**metadata, 'changes': actions,
        'new_unsupported_normative_meanings_observed': 0, 'paraphrase_duplicate_duties_observed': 0,
        'limitations': ['Some component actors/objects remain unresolved or inferred; case passes concern the named complete meaning.', 'The contiguous previous-name exception summary contains request-local C0003; stable target_ids are separate.', 'Source checks sometimes refuse useful links or reject a whole repair because one optional component is unsupported.']})

    fresh, fresh_pins = [], {}
    matches = {'slopes': [[0], [1], [2], [3], [4, 5], [6], [7, 8], [9, 10]],
               'authorizations': [[0], [1], [2, 3, 4, 5, 6], [2], [3], [4], [5], [6]],
               'marketing': [[0, 2, 3], [2], [3], [1]]}
    for name, groups in matches.items():
        labels = e._load(ROOT / 'fresh-source' / (name + '.labels.json'))
        before = e._load(ROOT / 'runs-02' / name / 'before.json')
        after = e._load(ROOT / 'runs-02' / name / 'after.json')
        for relative in [f'fresh-source/{name}.labels.json', f'runs-02/{name}/before.json',
                         f'runs-02/{name}/after.json', f'runs-02/{name}/manifest.json']:
            fresh_pins[relative] = e._digest((ROOT / relative).read_bytes())
        for index, (unit, indices) in enumerate(zip(labels['expected_units'], groups, strict=True)):
            for span in unit['source_spans']:
                assert after['document']['text'][span['start']:span['end']] == span['quote']
            if name == 'slopes':
                reason = 'The complete section limits are supplied as explicit scope evidence/definesScope bindings on the child meanings, alongside the parent rule and its two-branch exception. Local duties, choices and correctly targeted highwall/burial/approval qualifications survive unchanged. This accepts the complete source-bound representation, not the short summary alone.'
            elif name == 'authorizations':
                reason = 'All named applicability/knowledge predicates and independent defects survive in the original meanings. The extra-information permission remains conditional; refinement adds its explicit prerequisite link without duplicating the duty or changing any baseline.'
            else:
                reason = 'The initial provider response exhausted its output budget and produced no usable candidates. Recovery creates the marketing duty, both alternative exceptions and the remuneration statement duty; the relationship pass connects both exceptions to the marketing duty. Direction, nominal value, actor/recipient, references and conditional scope survive.'
            fresh.append({'unit_id': unit['id'], 'sample': name, 'expected': unit['meaning'], 'source_spans': unit['source_spans'],
                'baseline': 'fail' if name == 'marketing' else 'pass', 'refined': 'pass', 'rationale': reason,
                'before_records': [] if name == 'marketing' else [claim_view(before, before['accepted'][i]) for i in indices],
                'after_records': [claim_view(after, after['accepted'][i]) for i in indices]})
    e._save(output / 'fresh-cases.json', {**metadata, 'inputs_sha256': fresh_pins,
        'freeze_sha256': e._digest((ROOT / 'fresh-source/freeze.json').read_bytes()),
        'before': {'pass': 16, 'fail': 4}, 'after': {'pass': 20, 'fail': 0}, 'results': fresh,
        'applied_changes': {'slopes': 'No changes; restraint on already represented meaning.', 'authorizations': 'One supported prerequisite link to the additional-information permission.',
            'marketing': 'Four grounded meaning additions, then two edits connecting the exceptions. All six actions inspected; no new unsupported obligation or permission observed.'},
        'remaining_component_issues': ['Marketing remuneration rule has an unresolved duty bearer and an awkward object field (the authorization). Full statement meaning is correct; this is not ready-made actor/action/object workflow data.', 'Two marketing exception logic_text values combine noncontiguous clauses; evidence issues remain visible. No executable logic is claimed.'],
        'sampling_boundary': 'Three historical local CFR passages, one run each; 20 overlapping expected meanings, not a general accuracy estimate. Labels were frozen before extraction and never included in model requests.'})

    controls = []
    for name in ['omitted-alternative', 'wrong-exception-target']:
        directory = ROOT / 'controls' / name
        first, last = [e._load(directory / stage / 'report.json') for stage in ['initial-audit', 'final-audit']]
        controls.append({'control': name, 'detected_initially': True, 'fully_repaired_in_measured_capture': False,
            'initial_alternatives_errors': first['dimensions']['alternatives']['error'], 'final_alternatives_errors': last['dimensions']['alternatives']['error'],
            'initial_links_errors': first['dimensions']['links']['error'], 'final_links_errors': last['dimensions']['links']['error'],
            'rationale': ('The omission is detected. Recovery proposes the missing alternative but also assigns an unsupported actor; the challenge refuses the complete edit. A separate married-name reference link is added, while customary usage remains absent.' if name == 'omitted-alternative' else
                'The wrong target is detected and redirected. Later edits change the target revision, so ReviewStore correctly requires reconfirmation and clears the current link. The relationship pass proposes reconfirmation, but an overly broad duplicate guard refuses it. The final audit reports the missing link. A final local guard fix and regression test permit reconfirmation; no new provider run is counted as a successful repair.'),
            'capture_manifest_sha256': e._digest((directory / 'manifest.json').read_bytes())})
    e._save(output / 'controls.json', {**metadata, 'results': controls,
        'post_measurement_fix': {'file': 'packages/rulespec-extrapolator/src/rulespec_extrapolator/refinement.py',
            'sha256': e._digest(Path(r.__file__).read_bytes()), 'provider_rerun': False,
            'test': 'test_same_words_can_reconfirm_a_qualification_after_its_target_changes',
            'test_receipt': '../test-verification.json'}})

    costs = []
    for pattern in ['runs-01/*/refinement.json', 'runs-02/*/refinement.json', 'controls/*/refinement.json', 'slice-*/refinement.json']:
        for path in sorted(ROOT.glob(pattern)):
            run = e._load(path)
            costs.append({'capture': path.parent.relative_to(ROOT).as_posix(), 'applied_actions': run['applied_actions'],
                'status': run['status'], 'elapsed_seconds': run['elapsed_seconds'], **run['usage']})
    fresh_initial = {name: r._usage(ROOT / 'runs-02' / name / 'base-run') for name in matches}
    e._save(output / 'processing-cost.json', {'refinements': costs, 'fresh_initial_extraction': fresh_initial,
        'baseline_total_tokens': 2055895, 'revision_02_total_tokens': 1026905,
        'baseline_prompt_tokens': 1695507, 'revision_02_prompt_tokens': 669067,
        'notes': ['Refinement includes its initial and final audits; original base-run extraction is excluded.', 'Cached content tokens are a subset of input tokens; do not add them again.', 'Wall times are per sample; independent samples ran concurrently.', 'Schema probes are retained separately and are not quality measurements.', 'These are tokens, not a dollar estimate.']})
    lines = ['# Source-adjudicated quality results', '',
        'The measured final process passes **25 of 29** saved automatic cases, up from **17**. It closes eight of twelve failures, including NREG-04 and NREG-10, and preserves all seventeen original passes. NREG-15 is a separate history check.', '',
        'Both measured revisions score 25, but close different cases. Revision 1 recovers the certificate guidance; revision 2 adds the confidential-name and disability links but declines that guidance. The gain is useful, but one run does not establish reliable recovery.', '',
        '| Case | Initial | Revision 1 | Revision 2 |', '| --- | --- | --- | --- |']
    lines.extend(f"| {row['case_id']} — {row['name']} | {row['baseline']} | {row['revision_01']['status']} | {row['revision_02']['status']} |" for row in rows)
    lines += ['', 'The remaining final failures are the infant exception link, certificate timing/advisory coverage (two overlapping cases), and the ambiguous immaterial-damage list. Full invariants, source passages, claim records and rationale are in [saved-cases.json](saved-cases.json). Every applied baseline change is adjudicated in [applied-changes.json](applied-changes.json).', '',
        'The three fresh historical CFR passages pass **16/20 initially and 20/20 after refinement**. Marketing accounts for all four recovered meanings after its initial response was truncated. Slope meanings remain unchanged; authorizations gain one explicit prerequisite link. [Fresh cases and component limitations](fresh-cases.json).', '',
        'Both deliberate defects are detected, but neither finishes fully repaired in its recorded run. The omission repair is refused because it also invents an actor. The corrected exception target later needs reconfirmation after a baseline edit; the duplicate guard blocks that reconfirmation. The guard is fixed and tested locally after the two measured revisions, without counting an unperformed provider rerun. [Control evidence](controls.json).', '',
        'Across the same three baseline sources, recorded refinement tokens fall from **2,055,895 to 1,026,905** (50.1%); input tokens fall 60.5%. Both use 37 requests, including initial/final audits. The revised runs take about 3.7, 5.1 and 6.6 minutes each, concurrently. These remain expensive passes for small source samples. [Processing cost](processing-cost.json).', '',
        'These are Codex-authored project reference decisions, with exact source and capture pins. They can be corrected by later evidence. They are not a general accuracy percentage, human validation or proof of executable rules.']
    (output / 'RESULTS.md').write_text('\n'.join(lines) + '\n')
    e._write_manifest(output)
    print({'saved_cases': counts, 'fresh_cases': {'before': 16, 'after': 20}, 'reviewed_baseline_actions': len(actions)})


if __name__ == '__main__':
    main()
