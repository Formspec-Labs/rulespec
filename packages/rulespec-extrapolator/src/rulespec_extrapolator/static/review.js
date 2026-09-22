// Claim review client: shows claims with evidence and history; posts add, edit, split, merge, approve and reject.
"use strict";

// All source, model, and reviewer content enters the page as text, never HTML.
const $ = (id) => document.getElementById(id);
const state = {snapshot: null, selected: new Set(), active: null, csrf: "", action: null, actionRevision: null, saving: false};
const titles = {add: "Add rule", edit: "Edit claim", split: "Split claim", merge: "Merge claims", approve: "Approve claims", reject: "Reject claims"};
const kinds = ["requirement", "permission", "prohibition", "authority", "threshold", "definition", "condition", "exception", "recommendation", "exemption", "statement"];
const modalities = ["must", "should", "may", "must_not", "not_required", "possible", "not_stated", "uncertain"];
const quoteLists = ["scope_quotes", "context_quotes", "alternative_quotes"];
const relations = ["none", "scope", "prerequisite", "trigger", "exception"];
const readable = (value) => String(value ?? "").replaceAll("_", " ");
function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = String(text);
  if (className) element.className = className;
  return element;
}
function notice(message, error = false) { $("notice").textContent = message; $("notice").className = error ? "error" : ""; }
function reviewerKind(kind) { return kind === "aiAgent" ? "AI agent" : kind === "humanUser" ? "Human reviewer" : "Reviewer type not recorded"; }
function originLabel(origin) { return origin === "aiSuggested" ? "AI origin" : origin === "humanAsserted" ? "Human origin" : readable(origin); }
function issueText(issue) { return typeof issue === "string" ? issue : issue.message || `${readable(issue.code)}${issue.reference ? ": " + issue.reference : ""}`; }
function currentClaims() { return state.snapshot?.current || state.snapshot?.accepted || []; }
function selectedClaims() { return currentClaims().filter((claim) => state.selected.has(claim.id)); }
async function api(path, options) {
  const response = await fetch(path, {credentials: "same-origin", cache: "no-store", ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `The request failed (${response.status}).`);
  return data;
}
async function load() {
  try {
    const [session, snapshot] = await Promise.all([api("/api/session"), api("/api/snapshot")]);
    state.csrf = session.csrf_token;
    state.snapshot = snapshot;
    state.selected = new Set([...state.selected].filter((id) => currentClaims().some((c) => c.id === id)));
    if (!currentClaims().some((c) => c.id === state.active)) state.active = null;
    render();
    notice("");
  } catch (error) { notice(error.message, true); }
}
function render() {
  const snapshot = state.snapshot;
  $("document-title").textContent = snapshot.document.title || "Document review";
  document.title = `${snapshot.document.title || "Document"} · Rulespec review`;
  const run = snapshot.run || {};
  const windows = run.windows || [];
  const outcomes = windows.map((window) => window.status || window.outcome || window.terminal_outcome).filter(Boolean);
  const failures = outcomes.filter((status) => /fail|error|unresolved/i.test(typeof status === "string" ? status : JSON.stringify(status))).length;
  $("run-status").textContent = `Processing: ${readable(run.status || "status not recorded")}${windows.length ? ` · ${windows.length} processing windows${failures ? `, ${failures} need attention` : ""}` : ""}. Saved review revision ${snapshot.revision}.`;
  $("review-counts").replaceChildren();
  for (const [key, label] of [["pending", "need review"], ["approved", "approved"], ["rejected", "rejected"]]) {
    const count = node("div", undefined, "count");
    count.append(node("strong", snapshot.review_summary?.[key] ?? 0), node("span", label));
    $("review-counts").append(count);
  }
  $("history-count").textContent = snapshot.history.length;
  $("section-nav").replaceChildren();
  for (const section of snapshot.document.sections || []) {
    const button = node("button", section.label || "Section");
    button.type = "button";
    button.addEventListener("click", () => highlight([{start: section.start, end: section.end}], true));
    $("section-nav").append(button);
  }
  renderClaims(); renderDetail(); renderHistory(); renderProblems(); updateActions();
  highlight(selectedClaims().flatMap((c) => c.evidence || []));
}
function renderClaims() {
  $("claim-list").replaceChildren();
  const filter = $("status-filter").value;
  const claims = currentClaims().filter((c) => filter === "all" || c.review_status === filter);
  if (!claims.length) $("claim-list").append(node("p", "No claims match this view.", "empty"));
  for (const claim of claims) {
    const card = node("article", undefined, "claim-card" + (claim.id === state.active ? " selected" : ""));
    card.dataset.claimId = claim.id;
    const checkbox = node("input", undefined, "claim-check");
    checkbox.type = "checkbox"; checkbox.checked = state.selected.has(claim.id);
    checkbox.setAttribute("aria-label", "Select claim: " + claim.summary);
    checkbox.addEventListener("change", () => {
      checkbox.checked ? state.selected.add(claim.id) : state.selected.delete(claim.id);
      state.active = claim.id; renderClaims(); renderDetail(); updateActions(); highlight(selectedClaims().flatMap((c) => c.evidence || []), true);
    });
    const button = node("button", undefined, "claim-open"); button.type = "button";
    button.setAttribute("aria-expanded", String(state.active === claim.id));
    const meta = node("div", undefined, "claim-meta");
    meta.append(node("span", claim.kind), node("span", claim.review_status === "pending" ? "Needs review" : readable(claim.review_status), "badge " + claim.review_status), node("span", originLabel(claim.origin)));
    const issues = [...(claim.issues || []), ...(claim.link_issues || [])];
    if (issues.length) meta.append(node("span", `${issues.length} open ${issues.length === 1 ? "issue" : "issues"}`, "badge issue"));
    button.append(meta, node("p", claim.summary, "claim-summary"));
    if (claim.actor) button.append(node("p", claim.actor, "claim-actor"));
    button.addEventListener("click", () => { state.active = claim.id; state.selected = new Set([claim.id]); renderClaims(); renderDetail(); updateActions(); highlight(claim.evidence || [], true); });
    card.append(checkbox, button); $("claim-list").append(card);
  }
}
function evidenceLabel(field) {
  const name = field.split(":")[0];
  return ({summary: "Statement", actor: "Actor", action: "Action", object: "Object",
    logic_text: "Logic", modality: "Modal wording",
    scope_text: "Applicability", context: "Context", choice_text: "Choice",
    alternative: "Alternatives"})[name] || readable(name);
}
function evidenceGroups(evidence) {
  const groups = new Map();
  for (const item of evidence) {
    // Source positions matter: identical words at different locations stay separate.
    const key = JSON.stringify([item.source_id, item.start, item.end, item.quote]);
    if (!groups.has(key)) groups.set(key, {evidence: item, fields: new Set()});
    groups.get(key).fields.add(item.field);
  }
  return [...groups.values()];
}
function evidencePassages(evidence, source) {
  const text = Array.from(source.text);
  const groups = evidenceGroups(evidence), verified = [], other = [];
  for (const group of groups) {
    const item = group.evidence;
    const local = !item.source_id || item.source_id === source.id;
    const exact = Number.isInteger(item.start) && Number.isInteger(item.end)
      && item.start >= 0 && item.end > item.start && item.end <= text.length
      && text.slice(item.start, item.end).join("") === item.quote;
    (local && exact ? verified : other).push(group);
  }
  const passages = [];
  for (const group of verified.sort((a, b) => a.evidence.start - b.evidence.start)) {
    const last = passages.at(-1), item = group.evidence;
    if (last && item.start < last.evidence.end) {
      last.evidence.end = Math.max(last.evidence.end, item.end);
      last.evidence.quote = text.slice(last.evidence.start, last.evidence.end).join("");
      last.members.push(group);
    } else passages.push({evidence: {...item}, members: [group]});
  }
  // Never hide or rewrite evidence that could not be verified against this source.
  return [...passages, ...other.map((group) => ({evidence: group.evidence, members: [group]}))];
}
function renderEvidence(detail, evidence) {
  for (const group of evidencePassages(evidence, state.snapshot.document)) {
    const passage = node("section", undefined, "source-evidence");
    const roles = [...new Set(group.members.flatMap((member) => [...member.fields].map(evidenceLabel)))];
    passage.append(node("p", roles.join(" · "), "evidence-roles"));
    const quote = node("button", group.evidence.quote, "evidence-button"); quote.type = "button";
    quote.title = "Highlight this passage in the source";
    quote.addEventListener("click", () => highlight([group.evidence], true));
    passage.append(quote);
    const components = node("div", undefined, "evidence-components");
    for (const child of group.members.length > 1 ? group.members : []) {
      const label = [...new Set([...child.fields].map(evidenceLabel))].join(" / ");
      const button = node("button", label, "component-evidence"); button.type = "button";
      button.title = child.evidence.quote;
      button.setAttribute("aria-label", `${label}, source positions ${child.evidence.start}–${child.evidence.end}`);
      button.addEventListener("click", () => highlight([child.evidence], true)); components.append(button);
    }
    if (components.childElementCount) passage.append(components);
    detail.append(passage);
  }
}
function renderDetail() {
  for (const prior of $("claim-list").querySelectorAll("[data-claim-detail]")) prior.remove();
  const claim = currentClaims().find((c) => c.id === state.active);
  const card = [...$("claim-list").querySelectorAll(".claim-card")].find((item) => item.dataset.claimId === state.active);
  if (!claim || !card) return;
  const detail = node("section", undefined, "detail"); detail.dataset.claimDetail = "true";
  if (claim.scope_text) {
    const scope = node("p", undefined, "claim-scope");
    scope.append(node("strong", "Scope: "), document.createTextNode(claim.scope_text)); detail.append(scope);
  }
  const terms = state.snapshot.terms || {};
  for (const term of Object.values(terms).filter((t) => t.claim_id === claim.id)) {
    const line = node("p");
    line.append(node("strong", "Defines: "), document.createTextNode(term.label + (term.aliases.length ? ` (${term.aliases.join(", ")})` : "")));
    detail.append(line);
  }
  const uses = (claim.term_refs || []).filter((id) => terms[id]?.claim_id !== claim.id);
  if (uses.length) {
    const line = node("p"); line.append(node("strong", "Terms: "));
    for (const [index, id] of uses.entries()) {
      if (index) line.append(document.createTextNode(" · "));
      const term = terms[id];
      if (!term) {
        const prior = state.snapshot.term_lookup?.[id];
        line.append(node("span", `${prior?.label || "Unnamed term"}: ${prior?.reason || "definition unavailable"}`, "muted")); continue;
      }
      const button = node("button", term.label, "text-button"); button.type = "button";
      button.addEventListener("click", () => {
        state.active = term.claim_id; state.selected = new Set([term.claim_id]);
        $("status-filter").value = "all"; renderClaims(); renderDetail(); updateActions();
        highlight(term.evidence, true);
        const target = [...$("claim-list").querySelectorAll(".claim-card")].find((c) => c.dataset.claimId === term.claim_id);
        target?.querySelector(".claim-open")?.focus();
      }); line.append(button);
    }
    detail.append(line);
  }
  detail.append(node("h3", "Supporting source"));
  renderEvidence(detail, claim.evidence || []);
  const technical = node("details", undefined, "technical-details");
  technical.append(node("summary", "Field details and evidence links"));
  const fields = node("dl");
  for (const [key, label] of [["modality", "Source meaning"], ["actor", "Actor"], ["action", "Action"], ["object", "Object"], ["scope_text", "When this applies"], ["choice_text", "How the alternatives fit together"], ["logic_text", "Logic to review"], ["relation", "Qualification"]]) {
    if (claim[key] && claim[key] !== "none") fields.append(node("dt", label), node("dd", key === "modality" ? readable(claim[key]) : claim[key]));
  }
  technical.append(fields);
  if (claim.alternative_quotes?.length) {
    technical.append(node("h3", "Alternative source quotations"));
    const choices = node("ul");
    for (const option of claim.alternative_quotes) choices.append(node("li", option));
    technical.append(choices);
  }
  for (const evidence of claim.evidence || []) {
    const button = node("button", `${evidence.field} · characters ${evidence.start}–${evidence.end}`, "text-button"); button.type = "button";
    button.addEventListener("click", () => highlight([evidence], true)); technical.append(button);
  }
  detail.append(technical);
  if ((claim.applies_to || []).length) {
    detail.append(node("h3", "Affected rules"));
    for (const quote of claim.applies_to) detail.append(node("p", quote, "muted"));
    for (const id of claim.target_ids || []) {
      const target = currentClaims().find((c) => c.id === id);
      if (!target) continue;
      const link = node("button", target.summary, "text-button"); link.type = "button";
      link.addEventListener("click", () => { state.active = id; state.selected = new Set([id]); renderClaims(); renderDetail(); updateActions(); highlight(target.evidence, true); }); detail.append(link);
    }
  }
  if ((claim.reference_links || []).length) {
    detail.append(node("h3", "References"));
    for (const reference of claim.reference_links) {
      const section = state.snapshot.document.sections.find((s) => s.id === reference.section_id);
      if (section) {
        const button = node("button", `${reference.text} · source section`, "text-button"); button.type = "button";
        button.addEventListener("click", () => highlight([section], true)); detail.append(button);
      } else detail.append(node("p", `${reference.text} · unresolved`, "muted"));
    }
  }
  const issues = [...(claim.issues || []), ...(claim.link_issues || [])];
  if (issues.length) {
    detail.append(node("h3", "Still needs attention"));
    const list = node("ul", undefined, "issue-list"); for (const issue of issues) list.append(node("li", issueText(issue))); detail.append(list);
  }
  if (claim.review?.actor) {
    detail.append(node("p", `${readable(claim.review.status)} by ${claim.review.actor} (${reviewerKind(claim.review.actor_kind)}). ${claim.review.rationale}`, "muted"));
  }
  card.after(detail);
}
function highlight(evidence, scroll = false) {
  const text = Array.from(state.snapshot.document.text); // Evidence uses Unicode codepoints.
  const ranges = evidence.filter((e) => Number.isInteger(e.start) && Number.isInteger(e.end) && e.start >= 0 && e.end > e.start && e.end <= text.length).map((e) => [e.start, e.end]).sort((a, b) => a[0] - b[0]);
  const merged = [];
  for (const range of ranges) {
    if (merged.length && range[0] <= merged[merged.length - 1][1]) merged[merged.length - 1][1] = Math.max(range[1], merged[merged.length - 1][1]);
    else merged.push(range);
  }
  const fragment = document.createDocumentFragment(); let position = 0;
  for (const [start, end] of merged) { fragment.append(document.createTextNode(text.slice(position, start).join("")), node("mark", text.slice(start, end).join(""))); position = end; }
  fragment.append(document.createTextNode(text.slice(position).join(""))); $("source-text").replaceChildren(fragment);
  $("source-caption").textContent = merged.length ? `${merged.length} highlighted ${merged.length === 1 ? "passage" : "passages"}` : "Exact document text";
  if (scroll) $("source-text").querySelector("mark")?.scrollIntoView({behavior: "smooth", block: "nearest"});
}
function renderHistory() {
  $("history-panel").replaceChildren();
  if (!state.snapshot.history.length) $("history-panel").append(node("p", "Your saved edits and review decisions will appear here. The original extraction remains available throughout review.", "empty"));
  for (const event of [...state.snapshot.history].reverse()) {
    const entry = node("details", undefined, "history-entry");
    entry.append(node("summary", `${event.sequence}. ${titles[event.action] || readable(event.action)} · ${event.actor}`), node("div", `${reviewerKind(event.actor_kind)} · ${new Date(event.at).toLocaleString()}`, "history-meta"), node("p", event.rationale));
    for (const id of event.targets) {
      const old = state.snapshot.revisions.find((c) => c.id === id);
      if (!old) continue;
      const button = node("button", (event.action === "approve" || event.action === "reject" ? "Assessed: " : "Previous: ") + old.summary, "text-button"); button.type = "button";
      button.addEventListener("click", () => highlight(old.evidence, true)); entry.append(button);
    }
    for (const replacement of event.replacements || []) {
      const old = state.snapshot.revisions.find((c) => c.id === event.targets[0]);
      const changes = node("dl", undefined, "history-change");
      for (const key of ["summary", "kind", "modality", "actor", "action", "object", "quote", "scope_text", "choice_text", "logic_text", "defined_terms", "term_refs", "applies_to"]) {
        if (JSON.stringify(old?.[key]) === JSON.stringify(replacement[key])) continue;
        const describe = (value) => {
          if (key === "defined_terms") return (value || []).map((term) => {
            const previous = old?.defined_terms?.find((item) => item.id === term.id);
            const aliases = term.aliases.length ? ` (${term.aliases.join(", ")})` : "";
            const supportChanged = previous && JSON.stringify([previous.quote, previous.source_quotes]) !== JSON.stringify([term.quote, term.source_quotes]);
            return `${term.label}${aliases}${previous ? "" : " [new sense]"}${supportChanged ? " [source support changed]" : ""}`;
          }).join("; ") || "None";
          if (key === "term_refs") return (value || []).map((id) => state.snapshot.term_lookup?.[id]?.label || id).join(", ") || "None";
          if (key === "applies_to") return (value || []).map((id) => state.snapshot.revisions.find((c) => c.id === id)?.summary || "Unavailable rule").join("; ") || "None";
          return value || "None";
        };
        changes.append(node("dt", readable(key)), node("dd", `${describe(old?.[key])} → ${describe(replacement[key])}`));
      }
      entry.append(changes);
    }
    for (const issue of event.observations || []) entry.append(node('p', issueText(issue), 'history-change'));
    $("history-panel").append(entry);
  }
}
function renderProblems() {
  const originalRejections = (state.snapshot.rejected || []).filter((item) => item.candidate || item.reason);
  const audit = state.snapshot.source_audit;
  const refusals = [...(state.snapshot.extraction_refusals || []), ...(state.snapshot.enrichment_issues || []), ...(audit?.report?.audit_issues || []).map((issue) => typeof issue === "string" ? {code: issue} : issue)];
  const failure = state.snapshot.run?.failure_code;
  const gaps = audit?.report?.coverage?.missing_examples || [];
  const semanticErrors = Object.entries(audit?.report?.dimensions || {}).flatMap(([dimension, value]) => (value.error_examples || []).map((item) => ({...item, dimension})));
  const count = originalRejections.length + refusals.length + (failure ? 1 : 0) + gaps.length + semanticErrors.length;
  $("extraction-problems").hidden = !count && !audit;
  $("extraction-problems").querySelector("summary").textContent = count ? `${count} extraction ${count === 1 ? "issue" : "issues"}` : audit?.current ? "Source check · no recorded findings" : "Source check · earlier draft";
  $("extraction-problem-list").replaceChildren();
  if (audit) {
    $("extraction-problem-list").append(node("p", audit.current ? "Model-assisted source check. Its findings may need correction; completeness is not established." : "This source check assessed an earlier draft. Re-run the audit after corrections to refresh its findings.", "muted"));
    for (const gap of gaps) {
      const unit = audit.units.find((item) => item.id === gap.unit_id);
      const item = node("div", undefined, "extraction-issue");
      item.append(node("p", `${readable(gap.status)}: ${gap.meaning}`), node("p", gap.rationale || "", "muted"));
      if (unit) { const button = node("button", "Show source", "text-button"); button.type = "button"; button.addEventListener("click", () => highlight(unit.source_spans, true)); item.append(button); }
      $("extraction-problem-list").append(item);
    }
    for (const issue of semanticErrors) $("extraction-problem-list").append(node("p", `${readable(issue.dimension)}: ${issue.summary}. ${issue.rationale || ""}`));
  }
  if (failure) $("extraction-problem-list").append(node("p", `Processing could not finish: ${readable(failure)}.`));
  for (const refusal of refusals) {
    const item = node("div", undefined, "extraction-issue");
    item.append(node("p", refusal.message || refusal.reason || readable(refusal.code || "Extraction could not finish")));
    const details = [];
    if (refusal.window_id) details.push(`Window ${refusal.window_id}`);
    if (refusal.attempt_id) details.push(`Attempt ${refusal.attempt_id}`);
    if (refusal.code) details.push(`Reason: ${refusal.code}`);
    if (refusal.index !== undefined) details.push(`Candidate ${refusal.index}`);
    if (details.length) item.append(node("p", details.join(" · "), "history-meta"));
    $("extraction-problem-list").append(item);
  }
  for (const rejection of originalRejections) {
    const item = node("div", undefined, "extraction-issue");
    item.append(node("p", `${rejection.candidate?.summary || "Candidate could not be grounded"}: ${rejection.reason || "Needs review"}`));
    if (rejection.candidate && typeof rejection.candidate === "object" && !Array.isArray(rejection.candidate)) {
      const button = node("button", "Review as a new rule", "text-button"); button.type = "button";
      button.addEventListener("click", () => { openAction("add", rejection.candidate); $("rationale").value = `Recovering a candidate refused during extraction: ${rejection.reason || "evidence needs review"}`; }); item.append(button);
    }
    $("extraction-problem-list").append(item);
  }
}
function updateActions() {
  const count = state.selected.size;
  $("selection-count").textContent = count ? `${count} ${count === 1 ? "claim" : "claims"} selected` : "Select a claim to review.";
  $("edit").disabled = count !== 1; $("split").disabled = count !== 1; $("merge").disabled = count < 2;
  $("approve").disabled = !count; $("reject").disabled = !count;
}
function field(parent, key, label, value, {textarea = false, options, wide = false, required = false, type = "text"} = {}) {
  const wrapper = node("label", label, wide ? "field-wide" : "");
  let input;
  if (options) {
    input = node("select");
    for (const item of options) { const option = node("option", typeof item === "string" ? readable(item) : item.label); option.value = typeof item === "string" ? item : item.value; input.append(option); }
  } else { input = node(textarea ? "textarea" : "input"); if (textarea) input.rows = 3; else input.type = type; }
  input.dataset.field = key; input.value = value ?? ""; input.required = required;
  if (type === "number") { input.min = "0"; input.step = "1"; }
  wrapper.append(input); parent.append(wrapper); return input;
}
function targetRow(parent, id) {
  const row = node("div", undefined, "target-row"); const input = node("select");
  input.dataset.targetId = "true"; input.setAttribute("aria-label", "Affected rule");
  const choices = [{id: "", summary: "Choose an affected rule"}, ...currentClaims().filter((c) => !["condition", "exception"].includes(c.kind) && c.review_status !== "rejected")];
  if (id && !choices.some((c) => c.id === id)) choices.push({id, summary: "Previous target unavailable — choose its current rule"});
  for (const c of choices) { const option = node("option", c.summary); option.value = c.id; input.append(option); }
  input.value = id;
  const remove = node("button", "Remove"); remove.type = "button"; remove.addEventListener("click", () => row.remove()); row.append(input, remove); parent.append(row);
}
function blankClaim(prefill = {}) {
  const claim = {kind: "requirement", summary: "", actor: "", quote: "", action: "", object: "", actor_quote: "", action_quote: "", object_quote: "", logic_text: "", relation: "none", references: [], applies_to: [], start: null, end: null, section_id: "", modality: "uncertain", modality_quote: "", scope_text: "", choice_text: "", choice_quote: "", jurisdiction: "", jurisdiction_quote: "", scope_quotes: [], context_quotes: [], alternative_quotes: []};
  for (const key of Object.keys(claim)) {
    const value = prefill[key];
    if (["references", "applies_to", ...quoteLists].includes(key)) { if (Array.isArray(value) && value.every((item) => typeof item === "string")) claim[key] = [...value]; }
    else if (["start", "end"].includes(key)) { if (Number.isInteger(value) && value >= 0) claim[key] = value; }
    else if (typeof value === "string") claim[key] = value;
  }
  if (!kinds.includes(claim.kind)) claim.kind = "requirement";
  if (!relations.includes(claim.relation)) claim.relation = "none";
  return claim;
}
function termEditor(editor, claim) {
  const details = node('details', undefined, 'editor-details');
  details.open = Boolean(claim.defined_terms?.length || claim.term_refs?.length);
  details.append(node('summary', 'Defined terms and uses'));
  const definitions = node('div'); details.append(definitions);
  function addDefinition(term = {label: '', aliases: [], quote: claim.quote || '', source_quotes: []}) {
    const row = node('fieldset'); row.dataset.termDefinition = term.id || '';
    row.append(node('legend', 'Defined sense'));
    function input(key, label, value) {
      const wrapper = node('label', label); const control = node('textarea'); control.rows = 2;
      control.dataset.termField = key; control.value = value; wrapper.append(control); row.append(wrapper);
    }
    input('label', 'Defined name', term.label);
    input('aliases', 'Explicit aliases (one per line)', term.aliases.join('\n'));
    input('quote', 'Exact passage defining this term', term.quote);
    const sources = node('div'); row.append(sources);
    function addSource(text) {
      const wrapper = node('label', 'Additional name or alias evidence'); const control = node('textarea');
      control.dataset.termSource = 'true'; control.value = text; wrapper.append(control);
      const remove = node('button', 'Remove evidence'); remove.type = 'button'; remove.addEventListener('click', () => wrapper.remove());
      wrapper.append(remove); sources.append(wrapper);
    }
    for (const quote of term.source_quotes) addSource(quote);
    const add = node('button', 'Add name or alias evidence'); add.type = 'button'; add.addEventListener('click', () => addSource('')); row.append(add);
    const label = node('label', 'Replace this sense (existing uses will need relinking)');
    const replace = node('input'); replace.type = 'checkbox'; replace.dataset.newSense = 'true'; label.prepend(replace);
    label.hidden = !term.id; row.append(label);
    const remove = node('button', 'Remove definition'); remove.type = 'button'; remove.addEventListener('click', () => row.remove()); row.append(remove);
    definitions.append(row);
  }
  for (const term of claim.defined_terms || []) addDefinition(term);
  const add = node('button', 'Add defined term'); add.type = 'button'; add.addEventListener('click', () => addDefinition()); details.append(add);
  const uses = node('fieldset'); uses.append(node('legend', 'Terms explicitly used in this statement'));
  const lookup = state.snapshot.term_lookup || state.snapshot.terms || {};
  for (const [id, term] of Object.entries(lookup)) {
    if (term.status === 'unavailable' && !(claim.term_refs || []).includes(id)) continue;
    if ((claim.defined_terms || []).some((t) => t.id === id)) continue;
    const label = node('label', `${term.label || 'Unnamed term'}${term.status === 'unavailable' ? ` — ${term.reason}` : ''}`);
    const checkbox = node('input'); checkbox.type = 'checkbox'; checkbox.dataset.termRef = 'true'; checkbox.value = id;
    checkbox.checked = (claim.term_refs || []).includes(id); label.prepend(checkbox); uses.append(label);
  }
  details.append(uses); editor.append(details);
}
function addEditor(claim) {
  const editor = node("fieldset", undefined, "claim-editor");
  editor.append(node("legend", state.action === "add" ? "New rule" : "Replacement claim"));
  if (["add", "split"].includes(state.action)) { const remove = node("button", "Remove", "split-remove"); remove.type = "button"; remove.addEventListener("click", () => editor.remove()); editor.append(remove); }
  const grid = node("div", undefined, "field-grid"); editor.append(grid);
  field(grid, "kind", "Kind", claim.kind, {options: kinds});
  field(grid, "modality", "Source meaning", claim.modality || "uncertain", {options: modalities});
  field(grid, "actor", "Actor", claim.actor);
  field(grid, "summary", "Meaning in plain language", claim.summary, {textarea: true, wide: true, required: true});
  field(grid, "action", "Action", claim.action);
  field(grid, "object", "Object or subject of the action", claim.object);
  const quoteInput = field(grid, "quote", "Exact source quotation", claim.quote, {textarea: true, wide: true, required: true});
  termEditor(editor, claim);
  const evidence = node("details", undefined, "editor-details"); evidence.open = true; evidence.append(node("summary", "Component evidence and source position"));
  const evidenceGrid = node("div", undefined, "field-grid"); evidence.append(evidenceGrid);
  field(evidenceGrid, "actor_quote", "Exact words supporting the actor", claim.actor_quote, {textarea: true});
  field(evidenceGrid, "action_quote", "Exact words supporting the action", claim.action_quote, {textarea: true});
  field(evidenceGrid, "object_quote", "Exact words supporting the object", claim.object_quote, {textarea: true, wide: true});
  field(evidenceGrid, "modality_quote", "Exact words supporting this modal meaning", claim.modality_quote, {textarea: true, wide: true});
  const start = field(evidenceGrid, "start", "Quote starts at character (optional)", claim.start, {type: "number"});
  const end = field(evidenceGrid, "end", "Quote ends before character (optional)", claim.end, {type: "number"});
  const section = field(evidenceGrid, "section_id", "Source section", claim.section_id, {options: [{value: "", label: "Find from quotation"}, ...state.snapshot.document.sections.map((s) => ({value: s.id, label: s.label}))], wide: true});
  evidenceGrid.append(node("p", "Use source positions when the same quotation appears more than once. A changed quotation clears the old positions.", "field-help field-wide"));
  quoteInput.addEventListener("input", () => { start.value = ""; end.value = ""; section.value = ""; });
  editor.append(evidence);
  const qualifications = node("details", undefined, "editor-details"); qualifications.open = ["condition", "exception"].includes(claim.kind) || Boolean(claim.logic_text) || Boolean(claim.references?.length); qualifications.append(node("summary", "Qualifications, references, and unresolved logic"));
  const qualificationGrid = node("div", undefined, "field-grid"); qualifications.append(qualificationGrid);
  field(qualificationGrid, "relation", "How this qualifies a rule", claim.relation || "none", {options: relations});
  field(qualificationGrid, "references", "Referenced section labels (one per line)", (claim.references || []).join("\n"), {textarea: true});
  field(qualificationGrid, "logic_text", "Exact words for logic that needs review", claim.logic_text, {textarea: true, wide: true});
  field(qualificationGrid, "scope_text", "When this applies", claim.scope_text, {textarea: true, wide: true});
  field(qualificationGrid, "choice_text", "How alternatives fit together", claim.choice_text, {textarea: true, wide: true});
  field(qualificationGrid, "choice_quote", "Exact words supporting the choice", claim.choice_quote, {textarea: true, wide: true});
  for (const [key, label] of [["scope_quotes", "Governing conditions"], ["context_quotes", "Surrounding context"], ["alternative_quotes", "Alternatives"]]) {
    const group = node("div", undefined, "field-wide"); group.append(node("p", label + " · exact quotations"));
    const rows = node("div");
    function addQuote(quote) {
      const row = node("div", undefined, "target-row");
      const input = node("textarea"); input.rows = 3; input.value = quote; input.dataset.quoteList = key; input.setAttribute("aria-label", label + " quotation");
      const remove = node("button", "Remove"); remove.type = "button"; remove.addEventListener("click", () => row.remove()); row.append(input, remove); rows.append(row);
    }
    for (const quote of claim[key] || []) addQuote(quote);
    const add = node("button", "Add quotation"); add.type = "button"; add.addEventListener("click", () => addQuote(""));
    group.append(rows, add); qualificationGrid.append(group);
  }
  field(qualificationGrid, "jurisdiction", "Jurisdiction, if stated", claim.jurisdiction);
  field(qualificationGrid, "jurisdiction_quote", "Exact words supporting jurisdiction", claim.jurisdiction_quote, {textarea: true});
  const targetFields = node("div", undefined, "target-fields field-wide"); targetFields.append(node("p", "Affected rules"));
  const rows = node("div"); for (const quote of claim.applies_to || []) targetRow(rows, quote);
  const add = node("button", "Add affected rule"); add.type = "button"; add.addEventListener("click", () => targetRow(rows, ""));
  targetFields.append(rows, add); qualificationGrid.append(targetFields); editor.append(qualifications);
  $("replacements").append(editor);
}
function openAction(action, prefill) {
  state.action = action; state.actionRevision = state.snapshot.revision;
  $("dialog-title").textContent = titles[action]; $("dialog-context").textContent = action === "add" ? "Record a missing rule using exact words from this document. The original extraction stays available in history." : selectedClaims().map((c) => c.summary).join("\n");
  $("dialog-error").textContent = ""; $("rationale").value = ""; $("replacements").replaceChildren();
  $("save-action").textContent = action === "add" ? "Save new rules" : action === "approve" ? "Record approval" : action === "reject" ? "Record rejection" : "Save correction";
  $("add-replacement").hidden = !["add", "split"].includes(action);
  $("add-replacement").textContent = action === "add" ? "Add another rule" : "Add another claim";
  const issues = action === "add" ? 0 : selectedClaims().reduce((n, c) => n + (c.issues || []).length + (c.link_issues || []).length, 0);
  $("dialog-warning").hidden = !issues;
  $("dialog-warning").textContent = `${issues} open ${issues === 1 ? "issue remains" : "issues remain"} on the selected claims. Recording a decision keeps these issues visible.`;
  if (["edit", "split", "merge"].includes(action)) { addEditor(selectedClaims()[0]); if (action === "split") addEditor(selectedClaims()[0]); }
  if (action === "add") addEditor(blankClaim(prefill));
  $("review-dialog").showModal();
}
function replacements() {
  return [...$("replacements").querySelectorAll(".claim-editor")].map((editor) => {
    const result = {};
    for (const input of editor.querySelectorAll("[data-field]")) {
      const key = input.dataset.field;
      result[key] = ["start", "end"].includes(key) ? (input.value === "" ? null : Number(input.value)) : key === "references" ? input.value.split("\n").map((x) => x.trim()).filter(Boolean) : input.value;
    }
    result.applies_to = [...editor.querySelectorAll("[data-target-id]")].map((input) => input.value).filter(Boolean);
    result.term_refs = [...editor.querySelectorAll('[data-term-ref]:checked')].map((input) => input.value);
    result.defined_terms = [...editor.querySelectorAll('[data-term-definition]')].map((row) => {
      const term = Object.fromEntries([...row.querySelectorAll('[data-term-field]')].map((input) => [input.dataset.termField, input.value]));
      term.aliases = term.aliases.split('\n').map((x) => x.trim()).filter(Boolean);
      term.source_quotes = [...row.querySelectorAll('[data-term-source]')].map((input) => input.value).filter(Boolean);
      if (row.dataset.termDefinition && !row.querySelector('[data-new-sense]').checked) term.id = row.dataset.termDefinition;
      return term;
    });
    for (const key of quoteLists) result[key] = [...editor.querySelectorAll(`[data-quote-list="${key}"]`)].map((input) => input.value).filter((value) => value.trim());
    if ((result.start === null) !== (result.end === null)) throw new Error("Supply both source positions, or leave both empty.");
    return result;
  });
}
$("review-form").addEventListener("submit", async (event) => {
  event.preventDefault(); if (state.saving) return;
  const request = {expected_revision: state.actionRevision, actor: $("reviewer-name").value.trim(), actor_kind: $("reviewer-kind").value, action: state.action, targets: state.action === "add" ? [] : [...state.selected], rationale: $("rationale").value.trim()};
  try {
    if (["add", "edit", "split", "merge"].includes(state.action)) request.replacements = replacements();
    state.saving = true; $("save-action").disabled = true; $("dialog-error").textContent = "";
    state.snapshot = await api("/api/actions", {method: "POST", headers: {"Content-Type": "application/json", "X-CSRF-Token": state.csrf}, body: JSON.stringify(request)});
    const saved = state.snapshot.history[state.snapshot.history.length - 1];
    if (saved.replacements.length) { state.selected = new Set(saved.replacements.map((c) => c.id)); state.active = saved.replacements[0].id; }
    $("review-dialog").close(); render(); notice(`Saved ${readable(state.action)} by ${request.actor} (${reviewerKind(request.actor_kind)}). Review revision ${state.snapshot.revision}.`);
  } catch (error) { $("dialog-error").textContent = error.message; }
  finally { state.saving = false; $("save-action").disabled = false; }
});
for (const action of Object.keys(titles)) $(action).addEventListener("click", () => openAction(action));
for (const id of ["close-dialog", "cancel-dialog"]) $(id).addEventListener("click", () => { if (!state.saving) $("review-dialog").close(); });
$("review-dialog").addEventListener("cancel", (event) => { if (state.saving) event.preventDefault(); });
$("add-replacement").addEventListener("click", () => addEditor(state.action === "add" ? blankClaim() : selectedClaims()[0]));
$("refresh").addEventListener("click", load);
$("status-filter").addEventListener("change", () => { renderClaims(); renderDetail(); });
for (const tab of ["claims", "history"]) $(tab + "-tab").addEventListener("click", () => {
  for (const name of ["claims", "history"]) { $(name + "-tab").classList.toggle("active", name === tab); $(name + "-tab").setAttribute("aria-pressed", String(name === tab)); $(name + "-panel").hidden = name !== tab; }
  $("status-filter").parentElement.hidden = tab === "history";
});
load();
