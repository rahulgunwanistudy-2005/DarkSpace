import { readFile, writeFile } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { loadEmbedder, EMBEDDING_CONTRACT } from './embed.ts';

const [inputPath, outputPath, assetDirectory = '.cache/placement-assets'] = process.argv.slice(2);
if (!inputPath || !outputPath) throw new Error('Usage: node embed-public.ts <public-sentences.json> <vectors.json> [asset-directory]');
const sentences: unknown = JSON.parse(await readFile(inputPath, 'utf8'));
if (!Array.isArray(sentences) || !sentences.every(value => typeof value === 'string')) throw new Error('Expected a JSON list of public sentences. Do not supply personal profiles or answers to the public pipeline.');
const directory = resolve(assetDirectory);
const embedder = await loadEmbedder(async path => new Uint8Array(await readFile(resolve(directory, path))), resolve(directory, 'runtime') + sep);
try {
  const vectors = [];
  for (const sentence of sentences) vectors.push(await embedder.embed(sentence));
  await writeFile(outputPath, JSON.stringify({ contract: EMBEDDING_CONTRACT, vectors }) + '\n');
  console.log(`Embedded ${vectors.length} public sentences with contract ${EMBEDDING_CONTRACT.digest}.`);
} finally {
  await embedder.close();
}
