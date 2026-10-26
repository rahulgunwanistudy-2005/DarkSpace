import { test } from 'node:test';
import assert from 'node:assert/strict';
import { place, densityReference, validateRun, validateIdea, startInterview, saveAnswerDraft, answerQuestion, skipQuestion, saveIdeaDraft, recordPlacement, stopInterview, confirmAvoided, exportHandoff, isCurrentPlacement, rebaseInterview } from '../src/index.ts';
import type { ForecastRun, Placement, SharedDefault } from '../src/contracts.ts';

function forecast(defaults?: readonly SharedDefault[]): ForecastRun {
  const points = Array.from({ length: 11 }, (_, index) => ({ id: `p-${index.toString().padStart(2, '0')}`, idea: 'Synthetic point', vector: index < 5 ? [1, 0] : [0, 1], clusterId: 'c', x: index < 5 ? 0 : 1, y: 0 }));
  return {
    runId: 'synthetic-test', event: 'Synthetic test, no model samples', evidenceKind: 'synthetic-fixture',
    contract: { id: 'test', digest: 'test-contract', dimensions: 2 }, points,
    clusters: [{ id: 'c', name: 'Test cluster', memberIds: points.map(point => point.id), assignmentRadius: 0.1, defaultsStatus: 'complete', defaults: defaults ?? [{ id: 'd', label: 'Test default', count: 8, denominator: 11, unknown: 1, question: 'What does your experience add?' }] }],
  };
}

function placed(run = forecast(), vector: readonly number[] = [1, 0]): Placement {
  return place(run, { idea: 'I help people test their ideas.', vector, contract: run.contract, kind: 'personal' });
}

test('known arithmetic excludes only self and retains independent duplicate samples', () => {
  const run = forecast();
  assert.deepEqual(densityReference(run), [...Array<number>(5).fill(0.6), ...Array<number>(6).fill(0.5)]);
  const result = placed(run);
  assert.equal(result.density?.k, 10);
  assert.equal(result.density?.meanDistance, 0.5);
  assert.equal(result.density?.percentile, 100 * 3 / 11);
  assert.deepEqual(result.neighbors.slice(0, 5).map(value => value.id), ['p-00', 'p-01', 'p-02', 'p-03', 'p-04']);
  assert.deepEqual(result.position, { x: 0, y: 0, approximate: true });
  const novel = placed(run, [-1, 0]);
  assert.equal(novel.density?.meanDistance, 1.4);
  assert.equal(novel.density?.percentile, 100);
  assert.equal(novel.assignedClusterId, null);
  assert.equal(novel.nearbyClusters[0]?.id, 'c');
});

test('all equal distances use a midrank rather than reward a tie', () => {
  const run = forecast();
  const points = run.points.map(point => ({ ...point, vector: [1, 0] }));
  const result = placed({ ...run, points });
  assert.equal(result.density?.meanDistance, 0);
  assert.equal(result.density?.percentile, 50);
});

test('small and partially annotated runs disclose missing components without inventing numbers', () => {
  const run = forecast();
  const points = run.points.slice(0, 4);
  const cluster = { ...run.clusters[0]!, memberIds: points.map(point => point.id), defaultsStatus: 'missing' as const, defaults: [] };
  const result = placed({ ...run, points, clusters: [cluster] });
  assert.equal(result.density, null);
  assert.equal(result.neighbors.length, 4);
  assert.equal(result.missing.length, 2);
  assert.deepEqual(result.defaults, []);
  const noClusters = placed({ ...run, clusters: [], points: run.points.map(point => ({ ...point, clusterId: null })) });
  assert.equal(noClusters.density?.percentile, 100 * 3 / 11);
  assert.equal(noClusters.missing.length, 1);
});

test('malformed runs and mixed runtime contracts are refused before measurement', () => {
  const run = forecast();
  assert.throws(() => place(run, { idea: 'A long enough sentence here.', vector: [1, 0], contract: { ...run.contract, digest: 'other' }, kind: 'personal' }), /different model or runtime/u);
  assert.throws(() => placed(run, [2, 0]), /normalized/u);
  assert.throws(() => placed(run, [Number.NaN, 0]), /non-finite/u);
  assert.throws(() => placed(run, [1]), /dimensions/u);
  assert.throws(() => validateRun({ ...run, points: [run.points[0]!, run.points[0]!] }), /unique/u);
  assert.throws(() => validateRun({ ...run, clusters: [{ ...run.clusters[0]!, defaults: [{ ...run.clusters[0]!.defaults[0]!, count: 12 }] }] }), /counts/u);
  assert.throws(() => validateRun({ ...run, clusters: [{ ...run.clusters[0]!, memberIds: ['unknown'] }] }), /membership/u);
});

test('input rules are actionable and never alter the supplied sentence', () => {
  assert.throws(() => validateIdea('a     b     c'), /three words and 12/u);
  assert.throws(() => validateIdea('A'.repeat(1001)), /1,001/u);
  const idea = '  My sentence keeps its spaces.  ';
  const run = forecast();
  assert.equal(place(run, { idea, vector: [1, 0], contract: run.contract, kind: 'personal' }).idea, idea);
});

test('majority means strictly more than half; fixed questions are ordered and capped at five', () => {
  const defaults = Array.from({ length: 8 }, (_, index) => ({ id: `d${index}`, label: `Default ${index}`, count: 11 - index, denominator: 11, unknown: 0, question: `What do you know about default ${index}?` }));
  const first = placed(forecast(defaults));
  const session = startInterview(first);
  assert.deepEqual(session.questions.map(question => question.default.id), ['d0', 'd1', 'd2', 'd3', 'd4']);
  const ten = forecast();
  const points = ten.points.slice(0, 10);
  const half = { ...ten.clusters[0]!, memberIds: points.map(point => point.id), defaults: [{ ...ten.clusters[0]!.defaults[0]!, count: 5, denominator: 10, unknown: 0 }] };
  assert.equal(startInterview(placed({ ...ten, points, clusters: [half] })).phase, 'complete');
});

test('an unchanged percentile does not finish the interview and new defaults do not extend it', () => {
  const run = forecast([{ id: 'd1', label: 'One', count: 8, denominator: 11, unknown: 0, question: 'What do you know?' }, { id: 'd2', label: 'Two', count: 7, denominator: 11, unknown: 0, question: 'What have you seen?' }]);
  const first = placed(run);
  let session = answerQuestion(saveAnswerDraft(startInterview(first), 'My own answer.'));
  session = recordPlacement(session, { ...first, defaults: [] });
  assert.equal(session.phase, 'question');
  assert.equal(session.questions.length, 2);
  assert.equal(session.current, 1);
  session = skipQuestion(session);
  assert.equal(session.phase, 'complete');
  assert.equal(session.questions[1]?.status, 'skipped');
  assert.deepEqual(session.confirmedAvoided, []);
});

test('drafts and raw answers survive export including Markdown fences and whitespace', () => {
  const rawAnswer = '  My exact words.\n```\n# still my answer\n```\n\n';
  let session = startInterview(placed());
  session = saveAnswerDraft(session, rawAnswer);
  session = answerQuestion(session);
  session = saveIdeaDraft(session, 'This draft has never been placed.');
  session = stopInterview(session);
  const output = exportHandoff(session);
  assert.ok(output.includes(rawAnswer));
  assert.ok(output.includes('````text\n' + rawAnswer + '\n````'));
  assert.ok(output.includes('Unplaced draft — no measurement'));
  assert.ok(output.includes('None confirmed.'));
  assert.ok(output.includes('synthetic-fixture'));
  assert.equal(session.placements.length, 1);
  assert.ok(output.includes('Measured percentile change: 0.00'));
  assert.equal(session.questions[0]?.status, 'answered');
});

test('a sample, changed run, or pending answer cannot silently become a measured rewrite', () => {
  const first = placed();
  const pending = startInterview(first);
  assert.throws(() => answerQuestion(pending), /Skip/u);
  assert.throws(() => recordPlacement(pending, first), /Answer/u);
  const session = answerQuestion(saveAnswerDraft(pending, 'My own answer.'));
  assert.throws(() => recordPlacement(session, { ...first, kind: 'sample' }), /sample/u);
  assert.throws(() => recordPlacement(session, { ...first, runId: 'updated' }), /forecast changed/u);
  assert.equal(isCurrentPlacement(first, first.runId, first.contractDigest), true);
  assert.equal(isCurrentPlacement(first, 'updated', first.contractDigest), false);
  assert.equal(isCurrentPlacement(first, first.runId, 'updated-contract'), false);
});

test('avoidance requires explicit confirmation and cannot introduce unknown defaults', () => {
  const session = stopInterview(startInterview(placed()));
  assert.ok(exportHandoff(session).includes('None confirmed.'));
  const confirmed = confirmAvoided(session, ['d', 'd']);
  assert.deepEqual(confirmed.confirmedAvoided, ['d']);
  assert.ok(exportHandoff(confirmed).includes('user-confirmed, not model-verified'));
  assert.throws(() => confirmAvoided(session, ['not-asked']), /considered/u);
});

test('explicit forecast recovery retains exact answers and question progress without comparing incompatible percentiles', () => {
  const first = placed();
  const answer = '  Keep this unfinished answer.\n';
  const old = saveAnswerDraft(startInterview(first), answer);
  const next = { ...first, runId: 'new-forecast', density: { meanDistance: 0.8, percentile: 99, k: 10 } };
  const recovered = rebaseInterview(old, next);
  assert.equal(recovered.questions[0]?.answer, answer);
  assert.equal(recovered.current, old.current);
  assert.equal(recovered.placements.length, 2);
  const output = exportHandoff(recovered);
  assert.ok(output.includes('no movement comparison is calculated'));
  assert.ok(!output.includes('Measured percentile change:'));
  assert.ok(output.includes('Last forecast run: new-forecast'));
});

test('explicit real-to-fixture recovery keeps words and permits later rewrites only on the active reference', () => {
  let session = saveAnswerDraft(startInterview(placed()), '  preserved across the data boundary  ');
  const fixtureRun = { ...forecast(), runId:'new-sample-data', evidenceKind:'sample-data' as const };
  const rebound = placed(fixtureRun);
  session = rebaseInterview(session,rebound);
  assert.equal(session.questions[0]?.answer,'  preserved across the data boundary  ');
  session = answerQuestion(session);
  session = recordPlacement(session,rebound);
  assert.equal(session.current,1);
  assert.match(exportHandoff(session),/Last evidence: sample-data/);
  assert.match(exportHandoff(session),/no movement comparison is calculated/);
});
