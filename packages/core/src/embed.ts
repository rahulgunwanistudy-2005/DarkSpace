import { BertTokenizer } from '@huggingface/transformers';
import { InferenceSession, Tensor, env as onnxEnvironment } from 'onnxruntime-web/wasm';
import contract from './embedding-contract.json' with { type: 'json' };
import { PlacementError, validateIdea } from './place.ts';
import type { VectorContract } from './contracts.ts';

export const EMBEDDING_CONTRACT: VectorContract = Object.freeze({
  id: contract.id, digest: contract.digest, dimensions: contract.dimensions,
});

export interface Embedder {
  embed: (idea: string) => Promise<readonly number[]>;
  close: () => Promise<void>;
}

export type AssetReader = (path: string) => Promise<Uint8Array>;

async function checkedAsset(read: AssetReader, name: keyof typeof contract.assets): Promise<Uint8Array> {
  const bytes = await read(name);
  const expected = contract.assets[name];
  const buffer = Uint8Array.from(bytes).buffer;
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', buffer)), value => value.toString(16).padStart(2, '0')).join('');
  if (bytes.byteLength !== expected.bytes || hash !== expected.sha256) {
    throw new PlacementError('model_unavailable', `The downloaded model asset did not pass its integrity check: ${name}. Try downloading it again.`);
  }
  return bytes;
}

interface TokenTensor {
  data: BigInt64Array;
  dims: readonly number[];
}

function isTokenTensor(value: unknown): value is TokenTensor {
  return typeof value === 'object' && value !== null && 'data' in value && value.data instanceof BigInt64Array && 'dims' in value && Array.isArray(value.dims) && value.dims.every(Number.isSafeInteger);
}

export async function loadEmbedder(read: AssetReader, wasmDirectory: string): Promise<Embedder> {
  onnxEnvironment.wasm.numThreads = 1;
  onnxEnvironment.wasm.wasmPaths = wasmDirectory;
  const [model, vocabulary, configuration] = await Promise.all([
    checkedAsset(read, 'onnx/model_quantized.onnx'),
    checkedAsset(read, 'tokenizer.json'),
    checkedAsset(read, 'tokenizer_config.json'),
  ]);
  const decoder = new TextDecoder();
  const tokenizer = new BertTokenizer(JSON.parse(decoder.decode(vocabulary)), JSON.parse(decoder.decode(configuration)));
  const session = await InferenceSession.create(model, { executionProviders: ['wasm'] });
  let disposed = false;
  return {
    async embed(idea: string): Promise<readonly number[]> {
      if (disposed) throw new PlacementError('model_unavailable', 'The local model has been closed. Try loading it again.');
      validateIdea(idea);
      const encoded: unknown = tokenizer(idea, { padding: false, truncation: false });
      if (typeof encoded !== 'object' || encoded === null) throw new PlacementError('model_unavailable', 'The local tokenizer returned an invalid result.');
      const feeds: Record<string, Tensor> = {};
      for (const name of session.inputNames) {
        const token: unknown = Reflect.get(encoded, name);
        if (!isTokenTensor(token)) throw new PlacementError('model_unavailable', `A required local model input is missing: ${name}.`);
        if (token.dims.at(-1)! > contract.max_tokens) throw new PlacementError('long_input', 'This sentence exceeds the local model’s 512-token limit. Shorten it and try again.');
        feeds[name] = new Tensor('int64', token.data, token.dims);
      }
      const output = await session.run(feeds);
      const tensor = output.last_hidden_state;
      if (!tensor || !(tensor.data instanceof Float32Array) || tensor.dims.at(-1) !== contract.dimensions) throw new PlacementError('model_unavailable', 'The local model returned an incompatible embedding.');
      const firstToken = Array.from((tensor.data as Float32Array).slice(0, contract.dimensions));
      const norm = Math.sqrt(firstToken.reduce((sum, value) => sum + value * value, 0));
      if (!Number.isFinite(norm) || norm === 0) throw new PlacementError('model_unavailable', 'The local model returned an unusable vector. Try again.');
      return firstToken.map(value => Math.fround(value / norm));
    },
    async close(): Promise<void> {
      disposed = true;
      await session.release();
    },
  };
}
