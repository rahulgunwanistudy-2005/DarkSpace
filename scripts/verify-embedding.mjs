import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { loadEmbedder, EMBEDDING_CONTRACT } from '../packages/core/src/embed.ts';

const directory = resolve('.cache/placement-assets');
const read = async path => new Uint8Array(await readFile(resolve(directory, path)));
const embedder = await loadEmbedder(read, resolve(directory, 'runtime') + sep);
const sentence = 'A teacher turns class notes into adaptive revision quizzes for students.';
try {
  const first = await embedder.embed(sentence);
  const second = await embedder.embed(sentence);
  assert.equal(first.length, 384);
  assert.ok(Math.abs(Math.hypot(...first) - 1) < 1e-6);
  assert.deepEqual(first, second);
  await assert.rejects(() => embedder.embed('too short'), /three words/u);
  await assert.rejects(() => embedder.embed('中'.repeat(600) + ' new idea'), /512-token/u);
} finally {
  await embedder.close();
}
await assert.rejects(() => embedder.embed(sentence), /closed/u);
await assert.rejects(() => loadEmbedder(async () => new Uint8Array([1, 2, 3]), resolve(directory, 'runtime') + sep), /integrity/u);
console.log(`Embedding verified: 384 dimensions, normalized, repeat-identical, input/token/closed/integrity failures checked; contract ${EMBEDDING_CONTRACT.digest}. This is engineering verification, not semantic-quality validation.`);
