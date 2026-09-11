# Pipeline I would build now

I would build one durable source-and-evidence foundation, then two different products on top: source-first discovery with inexpensive meaning extraction, and a deliberate conversion of selected rules into reviewed workflow decisions. I would stop making discovery pay the cost of proving workflow applicability. I would also stop treating a richer graph as evidence that a document is better understood.

This recommendation follows my independent raw-artifact review in `2026-09-10-blind-process-a.md`. I have not read other reviewers' recommendations. Observations below come from the two supplied sections and four relationship-pass cells; the replacement design and claimed benefits remain hypotheses. No model calls or production changes were made.

## What the observed data tells me

The first extraction retained the material meaning in these short sections: four phone statements and 15 rail statements. The expensive subsequent work mostly added one phone link or five rail links. It also introduced a duplicate phone permission/exception, a disagreement over the carrier target, and no way to say that a rail exemption changes only the stopping part of a combined rule. The source locations, captured requests/responses, revision history, and honest pending-review status worked well. Those are the capabilities I would keep.

The examples do not establish retrieval quality, tagging accuracy, large-document coverage, workflow correctness, acceptable reviewer effort, or a best model configuration. I would measure those directly rather than infer them from the existing tests or model verdicts.

## Shared foundation: source, locations, and individually reviewable interpretations

**What goes in:** an immutable document capture, its source identity and retrieval metadata, and an explicitly identified version. Keep the original file alongside extracted text. Preserve the mapping between source locations and extracted text, especially where tables, formatting, OCR, or footnotes affect meaning. Missing or uncertain structure should remain visible.

**What happens:** build a source tree with headings, paragraphs, list lead-ins/items, tables, and references. These are navigation and context aids, not automatic assertions about legal scope. Assign short local aliases for model requests. Store the source once; later requests select the passages they need. Keep full raw requests/responses in the evidence store, rather than repeatedly including them in every working record.

**What comes out:** source passages; extracted meaning records; separately stored relationships; and a history of machine and human decisions. Each meaning record needs an identity, a complete readable statement, its kind/modal force when applicable, exact evidence references, optional useful actors/terms, and provenance. Do not require action, object, normalized dates, topic concepts, scope text, choice text, and logical text on every row. Add structure when a consumer needs it. A source statement is allowed to have multiple features, such as a permission that also qualifies another rule; that should not force duplicate statements.

Relationships are claims too. Give each relationship an identity, source and target, relationship type, exact evidence, and an interpretation note when needed. A target may identify an action or clause within a grouped rule when the distinction matters. Preserve supported, disputed, unresolved, and human-reviewed states per interpretation. A challenge call's agreement is evidence about the proposal, not human approval or a calibrated probability.

**How checked:** deterministic checks establish valid structure, existing target IDs, exact evidence locations, compatible versions, and retained original records. They do not establish that an interpretation follows from the text. Keep failed proposals and their reasons attached to the affected records, so exporting the final draft does not erase what was disputed.

## Product 1: discovery, tags, embeddings, and an evolving knowledge graph

I would index source passages first and add extracted statements as another way to find them. A source passage remains discoverable even if the extractor misses it. Search results should lead back to the original material and show enough governing context to read the selected statement correctly.

Run one compact extraction pass per coherent section, with selected parent context. The first-pass goal is useful complete meaning, not maximum field population. Avoid cutting through a list proviso merely to meet a fixed character budget; use bounded windows with explicit continuation/context when a section is too large. Some repeated governing wording in statements is worth its embedding cost. A source reference alone cannot make an isolated statement self-contained.

Build embeddings from readable source text and/or complete statements with informative titles and applicable context. Do not embed internal IDs, repeated evidence quotes, empty fields, or audit narratives. I would initially keep source and statement search results distinguishable, then deduplicate them to the same source result. Whether using two indexes beats one is an experiment, not a requirement.

Generate a small number of suggested tags from the text, mapped to a controlled vocabulary only where that vocabulary exists and the mapping is defensible. Keep unmatched labels and uncertain mappings. A tag should aid discovery; it should not silently narrow the truth of a rule or become a restrictive search filter. Actor names such as “driver” and “drivers of a CMV” may share a useful search label without asserting universal entity identity.

The initial graph should be modest: document hierarchy, source references, terms and definitions, actor mentions, topic suggestions, and clearly evidenced relationships. Ambiguous exceptions can be present as disputed relationship candidates, rather than omitted or asserted as settled facts. Export that graph from stored records when needed; do not make the graph's full serialization the model's working language.

Collect gradual feedback where users already act: irrelevant result, wrong tag, missing governing context, wrong actor, mistaken relationship, or corrected wording. Preserve who changed what and the source/version affected. A local correction should not automatically become a global rule. Promote recurring corrections into evaluation examples or vocabulary changes through a separate review. Distinguish user preference from correction of source meaning.

The current extraction command already defaults to one pass; audit and refinement are optional. I would preserve that inexpensive entrypoint. For the optional full-refinement route, I would replace its chained inventory/comparison audit, recovery, relationship proposals/challenges, and final audit with selectively invoked checks for expensive or consequential uncertainties, plus sampled audits for monitoring. The observed data supports questioning the value of running that full chain routinely; it does not prove that all audits are unnecessary.

## Product 2: preliminary extraction for workflow and form construction

The user selects a task and source scope: for example, “build a crossing checklist for these vehicle categories.” The system retrieves the relevant source and meaning records, then creates a **decision draft**, not another generic extraction snapshot.

That draft identifies:

- Facts the workflow must obtain, their definitions, and where they come from.
- Applicability categories and conditions, including unknown facts and unresolved references.
- Required actions, allowed actions, prohibited actions, sequence, and outputs.
- Exceptions, precisely what they change, and what remains applicable.
- The source meaning behind every proposed form question and decision.

For rail, a reviewer should see “stop 15–50 feet away,” “listen/look,” “ascertain no approaching train,” and “do not change gear” as referenceable actions within one crossing procedure. The stopping exemption should name its proposed affected action. The vehicle categories should be a selectable applicability set, not six unrelated statements or six cumulative prerequisites. Whether other safety steps remain applicable needs an explicit reviewed interpretation; the software should not infer the answer from a broad edge.

For phone use, show one emergency provision that grants permission and proposes an exception to the driver prohibition. Show the possible effect on the carrier provision as a separate unresolved question. A disagreement about the carrier should not suppress the supported driver relationship. The driving definition should inform the facts/questions about traffic delays and safely stopping off the highway.

Only now introduce explicit decision expressions, normalized values, and executable operators. The complete source meaning remains authoritative; a workflow expression is a separate derived interpretation with its own review history. Unknown answers must remain unknown. Do not turn an unresolved definition or missing fact into false, inapplicable, or an empty default.

Human review should resolve specific decisions with the source beside them, then inspect the generated form and test realistic cases. Model assistance can suggest questions and counterexamples, but should not manufacture operational policy absent from the source. Final review covers the form-to-decision mapping as well as the decision-to-source mapping: a correct rule is useless if the form asks the wrong fact.

## Choices I would make, and their tradeoffs

**Grouped statements plus targeted action references, rather than universal atomization.** This preserves readable procedures and coherent lists. It makes the workflow conversion more deliberate, but avoids multiplying context-free fragments. Split where an exception, different actor, modal force, or review decision requires it.

**One extraction pass plus selective challenges, rather than a permanent model committee.** This reduces routine work and makes checks purpose-specific. It can miss unnoticed errors, so keep representative sampling and task-based regression cases. Escalate based on ambiguity or user impact, not merely the presence of a keyword such as “except.”

**Source-first retrieval, rather than extraction-only retrieval.** This protects against extractor omissions. It may produce more noisy candidates, which ranking and source-level deduplication must handle. Compare that cost against missed relevant source passages.

**Separate stored records with a graph export, rather than graph nodes for every internal fact.** Keep the graph rich enough for the queries users actually need. The existing immutable evidence and review machinery can support this without requiring users or models to read its storage representation.

I would not select a new model or build a complex router yet. Use the existing baseline configuration as one candidate, compare a bounded stronger configuration on difficult cases, and route only if the data reveals a reliable advantage. The current two examples cannot tell us the right model strategy.

## Small tests and realistic sequence

1. **Establish useful baselines.** Reuse the saved source and output. Add a small, deliberately varied set of sections containing nested lists, inherited conditions, exceptions, definitions, cross-references, tables, and explanatory text. Write concrete discovery questions and workflow scenarios before comparing pipelines. Preserve independently adjudicated uncertainty rather than forcing disputed readings into binary gold labels.
2. **Test discovery separately.** Compare source-only, statement-only, and combined retrieval on the same questions. Judge relevant-source retrieval, missing context, duplicate results, and time to find the answer. Separately assess tag usefulness; retrieval scores do not establish tagging quality.
3. **Test one design change at a time.** First compare the current optional full-refinement route against one baseline plus targeted questions. Measure new correct information, introduced errors, unresolved issues exposed, tokens, elapsed time, and reviewer correction time. Then test relationship records without duplicate statements and action-level targets on the phone and rail examples. Those two examples are regression cases, not a sufficient benchmark.
4. **Build the source-linked discovery interface and feedback path.** Reuse current captures, exact evidence resolution, document versioning, review events, and discovery exports where useful. Add visibility for rejected/disputed relationships. Keep optional rich graph output behind the same stored information.
5. **Build one complete reviewed workflow.** Convert a selected source into facts, decisions, form questions, and outcomes. Test ordinary, boundary, exception, and unknown cases with a reviewer. Expand the decision representation only when another real workflow requires it.
6. **Scale from measured failure modes.** Add selective audits, model escalation, or richer structure only where they reduce observed errors or user effort. Keep a fixed evaluation set plus newly adjudicated feedback cases to detect regressions.

The highest-value change is to make the next stage answer a specific user question. Discovery needs relevant source material; workflow construction needs reviewed decisions. A general sequence of models repeatedly describing and approving the same document is a costly substitute for specifying which of those outcomes we are trying to improve.
