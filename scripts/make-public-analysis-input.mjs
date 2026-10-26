import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, sep } from 'node:path';
import { loadEmbedder, EMBEDDING_CONTRACT } from '../packages/core/src/embed.ts';

const [source, target] = process.argv.slice(2);
if (!source || !target) throw new Error('Usage: node scripts/make-public-analysis-input.mjs <samples.json> <analysis-input.json>');
const raw = await readFile(source);
const report = JSON.parse(raw);
if (report.attempted !== 384 || report.samples.length !== 384) throw new Error('The public run must contain every frozen attempt.');
const tags = report.config.models.map(model => model.tag);
for (const tag of tags) if (report.samples.filter(row => row.attempt.model.tag === tag).length !== 96) throw new Error('Model allocation differs from the frozen protocol.');
const parsed = report.samples.filter(row => row.parsed !== null);
if (parsed.length !== report.valid) throw new Error('Parsed count does not match the counted report.');
const assets = resolve('.cache/placement-assets');
const embedder = await loadEmbedder(async path => new Uint8Array(await readFile(resolve(assets, path))), resolve(assets, 'runtime') + sep);
const points = [];
const embeddingFailures = [];
try {
  for (const row of parsed) {
    try {
      points.push({ id: row.attempt.id, ...row.parsed, model: `Model ${String.fromCharCode(65 + tags.indexOf(row.attempt.model.tag))}`, vector: await embedder.embed(row.parsed.idea) });
    } catch (error) {
      embeddingFailures.push({ id: row.attempt.id, reason: String(error) });
    }
    if ((points.length + embeddingFailures.length) % 48 === 0) console.log(`Public embeddings ${points.length + embeddingFailures.length}/${parsed.length}`);
  }
} finally { await embedder.close(); }
const payload = {
  source_run_id: report.run_id,
  sample_sha256: createHash('sha256').update(raw).digest('hex'),
  event: report.config.event,
  contract: { id: EMBEDDING_CONTRACT.id, digest: EMBEDDING_CONTRACT.digest, dimensions: EMBEDDING_CONTRACT.dimensions },
  attempted: report.attempted,
  failures: report.attempted - points.length,
  points,
};
await writeFile(target, JSON.stringify(payload) + '\n', { flag: 'wx' });
await writeFile(target + '.failures.json', JSON.stringify({ sampling: { invalid: report.invalid, provider_errors: report.provider_errors, repair_attempts: report.repair_attempts, repair_failures: report.repair_failures }, embeddingFailures }, null, 2) + '\n', { flag: 'wx' });
console.log(`Preserved ${points.length} public vectors; ${payload.failures} total failures (${embeddingFailures.length} embedding failures).`);
