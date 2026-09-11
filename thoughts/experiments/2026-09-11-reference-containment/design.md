# Associate text readings with their publisher occurrence

Preregistered 2026-09-11 before collecting this comparison's outputs.

**Decision:** whether unique source containment can replace the current same-start
association and remove redundant rows without erasing distinct readings.

**Hypotheses:** H1, the four observed duplicate rows remain because a short parsed
public-law mention begins inside a longer publisher label. Full containment should
associate them with the unique publisher occurrence. H2, source containment means
the two targets agree. Deliberately conflicting targets and a publisher label with
two parsed references should disprove that stronger claim. Association is about
the source occurrence; each reading keeps its own meaning and evidence.

**Arms:** A, current `uslm.attach_publisher_links` same-start association; B,
unique full containment. Reuse the existing publisher node index, text readings,
shared evidence and target tables. Do not add a second representation or XML scan.

**Cases:** the three sealed USLM source captures and their four residual public-law
overlaps; constructed distinct and repeated occurrences, nested publisher links,
two parsed references inside one link, conflicting publisher/text targets, rejected
text readings, empty links, adjacent links and a text reading crossing a link's
boundary. Use full source labels, not normalized-identifier equality.

**Held constant:** input bytes, prepared text, source maps, native parser output,
target resolution and model settings. One deterministic run per case/arm, zero
provider calls. Run the original and candidate policies with the same RIN behavior;
record any separately adopted RIN change as a new shared baseline, not an effect
of association. Stop at these three sources and the declared control categories.

**Decision rule:** all four unique contained occurrences associate; no distinct
source occurrence disappears; all readings, refusals and exact evidence survive
scan and discovery; ambiguous containment remains separate; no association implies
identifier agreement. Reject or revise the approach if any gate fails. Explain its
complexity and avoid comparing every reference with every XML node. No generic
interval framework unless an existing small primitive cannot meet these needs.

**If adopted:** add actual-source and counterexample regressions, run affected
application checks, rebuild the extractor wheel, and verify installed commands
outside the checkout. Keep the original captures and failed attempts. No commits
or releases are included. A reduction in repeated rows is not semantic accuracy.
