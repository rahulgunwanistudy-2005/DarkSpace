import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { place, startInterview, saveAnswerDraft, answerQuestion, saveIdeaDraft, recordPlacement, stopInterview, exportHandoff } from './index.ts';
import type { ForecastRun } from './contracts.ts';

const run: ForecastRun = {
  runId: 'synthetic-fixture-v1', event: 'Synthetic arithmetic fixture — not a hackathon forecast', evidenceKind: 'synthetic-fixture',
  contract: { id: 'synthetic-unit-vectors', digest: 'fixture-only-2d-v1', dimensions: 2 },
  points: Array.from({ length: 11 }, (_, index) => ({ id: `fixture-${index.toString().padStart(2, '0')}`, idea: 'Synthetic fixture point', vector: index < 5 ? [1, 0] : [0, 1], clusterId: 'fixture-cluster', x: index < 5 ? 0 : 1, y: 0 })),
  clusters: [{ id: 'fixture-cluster', name: 'Synthetic cluster', memberIds: Array.from({ length: 11 }, (_, index) => `fixture-${index.toString().padStart(2, '0')}`), assignmentRadius: 0.1, defaultsStatus: 'complete', defaults: [{ id: 'fixture-default', label: 'Synthetic shared default', count: 8, denominator: 11, unknown: 1, question: 'What do you know that this shared default leaves out?' }] }],
};

const initial = place(run, { idea: 'An example sentence for arithmetic verification.', vector: [1, 0], contract: run.contract, kind: 'sample' });
let session = startInterview(initial);
session = saveAnswerDraft(session, 'Fixture answer only.\n  Keep these spaces and my exact words.');
session = answerQuestion(session);
session = saveIdeaDraft(session, 'A revised example sentence for arithmetic verification.');
session = recordPlacement(session, place(run, { idea: session.draftIdea, vector: [-1, 0], contract: run.contract, kind: 'sample' }));
session = stopInterview(session);
const output = fileURLToPath(new URL('../../../darkspace-output/', import.meta.url));
await mkdir(output, { recursive: true });
await writeFile(`${output}FIXTURE-HANDOFF.md`, exportHandoff(session));
console.log(JSON.stringify({ evidence: run.evidenceKind, before: initial.density, after: session.placements.at(-1)?.density, output: `${output}FIXTURE-HANDOFF.md` }, null, 2));
