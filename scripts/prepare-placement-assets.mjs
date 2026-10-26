import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';

const root = new URL('../', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('packages/core/src/embedding-contract.json', root), 'utf8'));
const output = resolve(process.argv[2] ?? '.cache/placement-assets');
await mkdir(output, { recursive: true });
for (const [name, expected] of Object.entries(manifest.assets)) {
  const target = resolve(output, name);
  let bytes;
  try { bytes = await readFile(target); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  if (!bytes) {
    const response = await fetch(`https://huggingface.co/${manifest.model}/resolve/${manifest.revision}/${name}`);
    if (!response.ok) throw new Error(`Could not download public asset ${name}: HTTP ${response.status}`);
    bytes = Buffer.from(await response.arrayBuffer());
    await new Promise(done => setTimeout(done, 3000));
  }
  if (bytes.length !== expected.bytes || createHash('sha256').update(bytes).digest('hex') !== expected.sha256) throw new Error(`Integrity check failed for ${name}; no substitution is allowed.`);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, bytes);
}
await mkdir(resolve(output, 'runtime'), { recursive: true });
for (const [name, expected] of Object.entries(manifest.runtime_assets)) {
  const source = new URL(`node_modules/onnxruntime-web/dist/${name}`, root);
  const bytes = await readFile(source);
  if (bytes.length !== expected.bytes || createHash('sha256').update(bytes).digest('hex') !== expected.sha256) throw new Error(`The installed WASM runtime changed: ${name}.`);
  await copyFile(source, resolve(output, 'runtime', name));
}
console.log(`Verified private-placement assets in ${output}. Model and runtime: ${Object.values({ ...manifest.assets, ...manifest.runtime_assets }).reduce((sum, value) => sum + value.bytes, 0)} bytes, excluding application JavaScript.`);
