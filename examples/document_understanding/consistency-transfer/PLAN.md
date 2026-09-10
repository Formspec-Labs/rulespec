# Precise evidence references on fresh sources

Decision: whether to use LangExtract sentence boundaries to offer more precise
source references in the existing extraction workflow. This does not test a new
model, explanations, or independent effects of the preceding deterministic fixes.

Hypothesis: paragraph-sized evidence mixes several meanings, causing ambiguous
component locators and making independently retrieved claims harder to review.
Finer selectable spans should reduce unrelated evidence without losing governing
conditions. The hypothesis is weakened if evidence remains broad, locator errors
increase, or narrower spans encourage lost conditions/antecedents.

Competing explanations: (1) the model loses meaning regardless of evidence size;
(2) the supplied source has genuine ambiguity; (3) shared paragraphs only affect
presentation, not extraction accuracy. The comparison can distinguish observed
representation/accuracy differences, not the model's hidden reasoning.

Arms:
- P: current paragraph/list-item catalog and current CUE-generated request.
- S: the same request with selectable spans split using the installed LangExtract
  SentenceIterator. Preserve all source text and ordering, and permit contiguous
  ranges. No custom sentence rules or document-specific prompt patches.

Cases: three previously unused official 2025 CFR snapshots from govinfo.gov:
14 CFR 91.107 (seatbelts), 29 CFR 1910.151 including its nonmandatory appendix
(first aid), and 29 CFR 1904.7 (recording criteria and first-aid definitions).
Search of saved experiment text and PLAN files found no prior use of these section
numbers. These are selected diagnostic cases, not an independent benchmark.
Use the saved passport document as a development regression case, separately
reported. Include a clearly labeled constructed document with mixed-role
exemptions, an indivisible AND duty, literal you, passive requirements, descriptive
possibility, recommendations and a two-sense acronym counterexample.

Held constant: one call per case/arm (10 total), same model, temperature 0,
low thinking, 32768 output tokens, whole-document focus up to 24000 characters.
If a source exceeds that bound, record a scope decision before calling; do not
silently truncate it. Randomize call order with seed 20260910. Preserve actual
request bodies, responses, failures, provider usage and runtime/source hashes.
No retries or post-result prompt changes. Stop after ten calls or 30 minutes of
provider time. One call per cell does not establish within-case stability.

Assess each axis separately against raw source and output:
1. Evidence: exactness, extraneous material, ambiguous component matches.
2. Standalone meaning: governing conditions, exceptions and antecedents survive.
3. Boundaries: independent activities remain referenceable; AND obligations and
   coherent definitions are not mechanically split into misleading alternatives.
4. Actors: explicit source actor, approver versus actor, literal you, passive and
   multi-role cases; null is correct when the source does not establish an actor.
5. Modality: must, should, may, must not, not required and descriptive possibility.
6. Terms: exact names/aliases, correct sense, explicit uses versus topical context.
7. Noise/cost: redundant choice/logic fields, input/output/thinking tokens,
   independently reported local serialization size.

Named checks before calls:
- Seatbelts: retain Administrator authorization, aircraft exclusions, pilot versus
  pilot-in-command duties, ground movement/takeoff/landing distinctions, child age
  and restraint alternatives, and crew exception. Do not treat installed-shoulder-
  harness qualifications as requirements to install one.
- First aid: retain proximity condition for training, corrosive-exposure condition,
  should in the nonmandatory appendix, descriptive may need versus permission,
  and blood-exposure prerequisite for protective equipment. The second sentence
  about supplies has a potentially ambiguous inherited scope: record readings,
  not a forced gold judgment. An acronym expansion alone is not a full definition.
- Recording: retain medical-treatment exclusions, all enumerated first-aid
  alternatives and their qualifications, nonprescription/prescription-strength
  distinction, and the distinction between provider recommendation and an
  employer's recording duty. Review all retained raw statements for additional
  omissions; do not infer coverage from shared quotations or schema validity.
- Passport: the Posts requirement retains authorized local modifications; both
  IN exemptions remain available without assigning a single misleading actor;
  no new antecedent error in the communication statement; simple choice need
  not duplicate the full statement in choice_text.

Decision rule: adopt S only if evidence becomes more precise on at least two
fresh cases, with no observed material loss of meaning, actor/modality/sense
regression, or new source-grounding failures relative to P. Report token tradeoffs.
Otherwise retain P and record whether the outcome is no measured improvement,
tradeoff, regression or unresolved. Better evidence precision alone does not
establish semantic improvement. A broader gate failure cannot be relabeled a pass.

Manual assessment is a revisable agent judgment, not absolute gold. Review blind
cell labels where practical before opening the arm mapping. Preserve uncertainty,
including source ambiguities and omissions common to both arms. A field-specific
failure does not make all other fields equally bad or justify populating them all.

After the decision, separately verify the integrated extract → enrich → audit →
correct → export → reload/replay workflow using the actual provider. That is an
integration check, not another independent quality result.

Pre-call setup correction: the first attempt read RefSpec/.env, which contained
no Gemini key. No request was sent and no output was observed. Its failure,
original design and runner are retained under setup-failure/. The runner also
used the wrong result key (claims instead of accepted); corrected this reporting
error before any provider output. Use the already-authorized spicy-regs/.env.
The 10-call bound, cases, arms and outcome criteria are unchanged.
