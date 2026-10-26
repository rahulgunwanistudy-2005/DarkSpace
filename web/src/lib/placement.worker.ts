/// <reference lib="webworker" />
import { loadEmbedder, EMBEDDING_CONTRACT } from '../../../packages/core/src/embed.ts';
import { place, PlacementError, validateIdea } from '../../../packages/core/src/place.ts';
import type { ForecastRun } from '../../../packages/core/src/contracts.ts';

let model: ReturnType<typeof loadEmbedder> | null = null;
const worker = self as DedicatedWorkerGlobalScope;
async function prepareModel(): Promise<Awaited<ReturnType<typeof loadEmbedder>>> {
  model ??= loadEmbedder(async path => {
    const response = await fetch(`/models/${path}`);
    if (!response.ok) throw new PlacementError('model_unavailable', 'The local model files are unavailable. Try again or choose a saved sample.');
    return new Uint8Array(await response.arrayBuffer());
  }, '/models/runtime/');
  return model;
}

worker.onmessage = async ({ data }: MessageEvent<{ id: number; type?: 'warm'; idea: string; run: ForecastRun }>) => {
  if(data.type==='warm') {
    try { await prepareModel();worker.postMessage({id:data.id,type:'availability',available:true}); }
    catch { model=null;worker.postMessage({id:data.id,type:'availability',available:false}); }
    return;
  }
  const { id, idea, run } = data;
  const stage = (message: string): void => worker.postMessage({ id, type: 'stage', message });
  try {
    stage('Checking your sentence');
    validateIdea(idea);
    if (run.contract.digest !== EMBEDDING_CONTRACT.digest) throw new PlacementError('model_unavailable', 'This forecast uses a model that is not installed in this build. Use a saved sample or try again after the model is available.');
    stage('Loading the local model');
    const embedder = await prepareModel();
    stage('Reading your idea on this device');
    const vector = await embedder.embed(idea);
    stage('Finding nearby ideas and measuring crowding');
    const result = place(run, { idea, vector, contract: EMBEDDING_CONTRACT, kind: 'personal' });
    worker.postMessage({ id, type: 'result', result });
  } catch (error) {
    worker.postMessage({ id, type: 'error', code: error instanceof PlacementError ? error.code : 'model_unavailable', message: error instanceof Error ? error.message : 'The local model could not finish. Try again or use a saved sample.' });
    model = null;
  }
};
