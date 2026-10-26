import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { validateRun, place } from '../packages/core/src/place.ts';

const [input] = process.argv.slice(2);
if (!input) throw new Error('Usage: node scripts/export-web-run.mjs <public-analysis.json>');
const run = JSON.parse(await readFile(input, 'utf8'));
validateRun(run);
if (run.evidenceKind !== 'model-forecast') throw new Error('Only actual public model runs can become the production forecast.');
const models = [...new Set(run.points.map(point => point.model))].sort();
const samplePoints = models.map(model => run.points.find(point => point.model === model));
run.samplePlacements = samplePoints.map(point => place(run, { idea: point.idea, vector: point.vector, contract: run.contract, kind: 'sample' }));
const payload = JSON.stringify(run) + '\n';
const directory = resolve('data/runs', run.runId);
await mkdir(directory, { recursive: true });
const artifact = resolve(directory, 'forecast.json');
try {
  const previous = await readFile(artifact, 'utf8');
  if (previous !== payload) throw new Error('Refusing to overwrite a different completed forecast.');
} catch (error) { if (error.code !== 'ENOENT') throw error; await writeFile(artifact, payload, { flag: 'wx' }); }
const sha256 = createHash('sha256').update(payload).digest('hex');
await writeFile(resolve(directory, 'manifest.json'), JSON.stringify({ runId: run.runId, files: { 'forecast.json': sha256 }, sourceRunId: run.provenance.source_run_id, sourceSha256: run.provenance.sample_sha256 }, null, 2) + '\n');
const report = [
  '# Public forecast run', '',
  `Run: ${run.runId}`, `Forecast SHA-256: ${sha256}`, `Source run: ${run.provenance.source_run_id}`, `Source SHA-256: ${run.provenance.sample_sha256}`, '',
  `${run.provenance.attempted} attempts; ${run.points.length} valid embedded ideas; ${run.provenance.failures} failures; ${run.clusters.length} clusters; ${run.provenance.noise_points} unclustered points. Unclustered points remain in density measurements.`, '',
  'This is an exploratory model forecast, not actual entries, historical coverage, or validated entrant prediction. The current-event gallery was not collected.', '',
  'Defaults count explicit wording under literal-mechanisms-v1. The rules were revised after exact-text labels yielded no majority defaults. This is disclosed rather than described as a held-out test. No human semantic validation or judge-validation result exists.', '',
  '## Measured clusters', '',
  '| Cluster ID | Name | Members | Majority wording defaults |', '| --- | --- | ---: | --- |',
  ...run.clusters.map(cluster => `| ${cluster.id} | ${cluster.name} | ${cluster.memberIds.length} | ${cluster.defaults.filter(value=>value.count/value.denominator>0.5).map(value=>`${value.label}: ${value.count}/${value.denominator}`).join('; ')} |`), '',
  'Four saved examples are the first valid sample from each model family in frozen generation order, without selection for an attractive result. They are labeled samples and never replace personal text.', '',
  'All public vectors use the shared q8 WASM contract. Personal measurements use full-dimensional cosine distances; UMAP is display only. See forecast.json for the exact rules, per-item assignments, software versions and analysis fingerprints.', '',
];
await writeFile(resolve(directory, 'REPORT.md'), report.join('\n'));
await mkdir('web/static/data', { recursive: true });
await writeFile('web/static/data/current.json', payload);
console.log(JSON.stringify({ runId: run.runId, sha256, points: run.points.length, clusters: run.clusters.length, samples: run.samplePlacements.length, majorityDefaults: run.clusters.map(cluster => ({ id: cluster.id, members: cluster.memberIds.length, defaults: cluster.defaults.filter(value => value.count / value.denominator > 0.5).length })) }, null, 2));
