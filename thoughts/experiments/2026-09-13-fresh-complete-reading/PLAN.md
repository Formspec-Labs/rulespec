# Fresh-source validation of the complete-reading checker

Decision: determine whether the existing shared-task checker improves judgments
on previously untested source excerpts enough to carry forward to optional-path
integration. Do not change TASK.txt or CHECK_TASK during this experiment. The
prior notice failures remain separate development regressions.

Hypothesis: the improved task definition will correct the current checker's
record-boundary and optional-field assumptions across new topics without
increasing acceptance of substantively wrong edits. Alternatively the earlier
gain was specific to the selected pension/request cases. A third possibility is
that gain transfers for some relationships while incoming exceptions stay weak.

Arms: A is the current production checker after the committed API/identifier
fixes; it assesses edits only. B is the exact shared construction task and
selected-decision checker from `2026-09-13-complete-reading-check`, with unchanged
schema and wording. No further applicability hints. Report the shared edited
candidates separately from B's additional no-change coverage.

Fresh inputs: eight complete native units from eight different U.S. Code sections
in the pinned annual release 119-102: privacy-record access, bankruptcy dismissal,
free credit disclosures, regulatory inspection authority, juror qualification,
compensatory time, employment medical exams, and vehicle-recall repair remedies.
These are new source contexts for this experiment, not randomly sampled whole
statutes or a current-law interpretation. Outside provisions remain unavailable.
Sources and anticipated meaning obligations are recorded before extraction.

Procedure:
1. Run the current production extractor once per source, using its default low
   thinking and normal response schema. Preserve all failures and complete runs.
2. Read the raw source and outputs. Select the target specified in CASE-CRITERIA.md
   by its meaning, never by how a checker reacts. Preserve the original book.
3. Freeze three independent candidate decisions per source before any checker
   calls: a complete supported edit (or correct no-op if already complete), an
   edit with one named substantive error, and an incomplete no-op (or unnecessary
   optional-component edit if the original is already complete). Candidate edits
   are constructed diagnostic fixtures, not attributed to the extractor. Keep
   sound component fields intact, and ground retained/added evidence using
   existing Core and review APIs. Record uncertainty and baseline completeness.
   If one target cannot be identified reliably, report it rather than substitute
   an easier source or force a fabricated baseline omission.
4. Freeze both arms' actual prompts, schema, labels, source and runtime hashes.
   Use identical candidate order for each paired call, randomize order between
   repetitions, randomize arm scheduling and hide the key during raw review.
   Responses may reveal their task; do not claim independent human blinding.
5. Two repetitions per arm and source. Also repeat both arms on the exact saved
   notice candidate group twice. Old regressions never enter fresh-case totals.
6. Re-decode responses with the provider blocked, manually check raw judgments
   and selected passages, then open the arm key. Report source fidelity, complete
   meaning, necessity, false acceptance, abstention, no-op handling, tokens and
   time separately. No automatic semantic approval follows a schema-valid result.

Settings/bounds: Gemini 3.8 Flash; medium thinking for both checker arms; 32768
maximum output tokens; no sampling parameters, no retries. Eight low-thinking
production extraction calls + 32 fresh checker calls + four notice regression
calls = at most 44 requests. Bound recorded tokens at 500000 and summed provider
call time at 2400 seconds; do not start another call once a bound is reached.
Stop on provider error or a mechanical problem that invalidates the comparison;
retain the failure. A completed call may overshoot the token/time cap.

Labels/gate: classifications are revisable source-based agent labels. For known
wrong meanings, supported is a false acceptance; unknown is an abstention,
reported separately and not counted correct. On shared edited candidates, carry
B forward if its correctness is at least 85%, improves over A by at least 15
percentage points, improves at least three fresh source contexts, and has no
increase in substantively wrong-edit acceptance. If B assesses no-ops, report
its coverage and require at least 75% correctness for carrying that capability
forward. Existing notice regression misses do not erase a fresh comparative gain;
any newly introduced harmful behavior must be examined before integration.

This replaces the previous all-cases threshold for this new comparison, following
the user's observation that the substantial earlier gain was understated. It
does not retroactively pass the old gate. Passing supports bounded optional-path
integration work, not an accuracy guarantee or a new default extraction pass.
No production change is authorized solely by running this experiment.
