# Does the simple path provide useful discovery evidence?

Decision: keep extraction plus source-preserving discovery as the main documented
route; determine the measured benefit of its evidence packets and whether an
optional audit earns its added cost on fresh cases. No model/default changes are
proposed. Documentation cleanup and CLI help are authorized independently.

Hypotheses and competing explanations:

- Linked extraction evidence improves recovery of governing source passages from
  the same search hits. Predict at least two additional fully supported questions
  without losing any supported answers. If source-only already finds everything,
  this sample cannot demonstrate a retrieval gain.
- Extraction makes individual meanings easier to use, but can lose qualifications
  while still retaining their source. Check statement meaning independently of
  evidence retrieval; finding a quote does not establish a correct draft.
- Medium audit detects consequential errors left by extraction. Predict specific
  supported findings on at least one failed case without allegations against the
  faithful control. More findings alone, or restating an existing correct rule,
  weakens rather than confirms the usefulness claim.

Arms: A uses existing `discovery.records(..., 'source')`; B uses existing
`discovery.records(..., 'packets')`. Both rank identical source text with the
existing `evaluation/discovery_trial.py` BM25 settings and top-three limit. B adds
linked claim/scope evidence after ranking. No new search service or ranking code.
Record the existing summaries-only diagnostic separately, not as a primary arm.
These are source-evidence packets, not a hybrid statement/source ranking system.

Cases: complete 7 FAM 1453 (consular marriage role), 2025 annual 40 CFR 262.15
(satellite waste accumulation), and complete 5 USC 6323 including its notes from
release 119-102. Source selection precedes model calls. Save twelve questions,
required exact source passages and revisable meaning expectations before calling
extraction. The manual is a complete bounded section of its retained parent page.
Existing report/receipt search found no prior evaluation of these selections;
this is a small selected fresh set, not a population accuracy benchmark.

Preparation: reuse DocSpec's existing visible-text readers for acquisition of the
manual and annual XML. The manual declares Latin-1 but contains Windows-1252
punctuation; retain original bytes and the explicitly transcoded UTF-8 rendition.
Annual XML remains outside native Rulespec/RefSpec preparation. Retain XML,
acquisition blocks/byte maps and the plain-text rendition separately; Rulespec's
evidence refers to that frozen text. No new production reader or dependency.
USLM uses the existing native reader on a complete section serialized inside its
original `uscDoc` element type; retain the source archive/member digest and exact
section selection. Distinguish this serialization from original publisher bytes.

Held constant: current source runtime, generated CUE schemas, extraction prompt,
Gemini `gemini-3.8-flash`, temperature 0, low extraction thinking, 24,000 focus
characters and 16,384 output tokens. One extraction per window, at most six
windows, no retries. One observation per source; zero temperature is not a
repeatability guarantee. No edits to extracted meanings before retrieval/audit.

Audit follow-up: after reading source and raw output, freeze at most two failed
cases and one faithful control, with specific defects and preservation criteria.
Run existing medium audit with 24,000 focus characters and 32,768 output tokens,
at most six audit windows (twelve requests), no retries. This explicit window
override is the documented optional recipe, not an audit-default change. If no
fresh faithful document exists, select a source-faithful claim as a named control
within a reviewed book; do not manufacture an error or silently revise a claim.

Stop bound: at most 18 provider requests total, 30 minutes of provider work, and
300,000 recorded tokens before starting a further stage. Check bounds before
each whole-document call using its planned window count. A final stage may cross
the token/time threshold; retain and report that overrun, then stop. Setup/provider
failures count as attempts. No automatic prompt tuning or further refinement.

Decision rule: claim bounded retrieval improvement only at two gains, zero losses
and verified source support; otherwise report no measured gain or regression.
Report semantic defects separately, including historical-note/current-rule
confusion, actor, modality, alternatives, scope and repetition. Audit remains
optional; consider it useful on this set only with a specific consequential
defect found and no false alarm on the named control. Otherwise defer a stronger
recommendation. Report unresolved judgments rather than forcing correct/incorrect.

Capture/check: preserve sources, request bodies, responses, refusals, runtime pins,
all review labels, discovery hits and usage. Verify ranking parity, evidence
positions and source-retention exports. Replay saved processing without calls.
Prepare one short reviewed decision outline using these records and report the
corrections needed; this is not an executable form or a measured human time study.
