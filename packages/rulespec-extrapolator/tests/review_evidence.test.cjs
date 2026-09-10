const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');

const browser = vm.createContext({
  document: {getElementById: () => ({addEventListener() {}})},
  fetch: () => new Promise(() => {}),
});
vm.runInContext(readFileSync(join(__dirname, '../src/rulespec_extrapolator/static/review.js'), 'utf8'), browser);
const source = {id: 'document', text: '😀 Drivers must stop unless exempt. Drivers must stop unless exempt.'};
const span = (start, end, field) => ({start, end, field, quote: Array.from(source.text).slice(start, end).join('')});
const passages = (evidence) => browser.evidencePassages(evidence, source);

test('overlapping passages appear once while every role keeps its original interval', () => {
  const evidence = [span(2, 24, 'summary'), span(10, 33, 'logic_text'),
    span(2, 9, 'actor'), span(10, 33, 'alternative:0')];
  const original = JSON.stringify(evidence);
  const result = passages(evidence);
  assert.equal(result.length, 1);
  assert.equal(result[0].evidence.quote, Array.from(source.text).slice(2, 33).join(''));
  const roles = result[0].members.flatMap(m => [...m.fields].map(field => [field, m.evidence.start, m.evidence.end]));
  assert.deepEqual(JSON.parse(JSON.stringify(roles)).sort(), evidence.map(e => [e.field, e.start, e.end]).sort());
  assert.equal(JSON.stringify(evidence), original);
});

test('identical words at distinct positions stay separate; Unicode offsets remain exact', () => {
  const result = passages([span(0, 1, 'context:0'), span(2, 9, 'actor'), span(35, 42, 'actor')]);
  assert.equal(result.length, 3);
  assert.equal(result[0].evidence.quote, '😀');
  assert.equal(result[1].evidence.quote, 'Drivers');
  assert.equal(result[2].evidence.quote, 'Drivers');
  assert.notEqual(result[1].evidence.start, result[2].evidence.start);
});

test('adjacent evidence does not create a larger implied passage', () => {
  assert.equal(passages([span(2, 9, 'actor'), span(9, 14, 'modality')]).length, 2);
});

test('unverified and foreign evidence remains visible without rewriting it', () => {
  const bad = {...span(2, 9, 'actor'), quote: 'Wrong text'};
  const foreign = {...span(2, 9, 'actor'), source_id: 'another-document'};
  const result = passages([span(2, 24, 'summary'), bad, foreign]);
  assert.equal(result.length, 3);
  assert.equal(result[1].evidence.quote, bad.quote);
  assert.equal(result[2].evidence.source_id, foreign.source_id);
});
