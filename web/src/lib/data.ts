import { validateRun } from '../../../packages/core/src/place.ts';
import type { ForecastRun, Placement } from '../../../packages/core/src/contracts.ts';

export interface ViewRun extends ForecastRun {
  samplePlacements?: readonly Placement[];
  provenance?: Record<string, unknown>;
}

export async function loadRun(): Promise<ViewRun> {
  const fixture=import.meta.env.DEV && new URL(location.href).searchParams.get('fixture')==='engineering';
  const response = await fetch(fixture?'/__engineering-fixture.json':'/data/current.json', { cache: 'no-cache' });
  if (!response.ok) throw new Error('The saved public forecast is not available in this build. Your idea has not been placed.');
  const raw: unknown = await response.json();
  if (typeof raw !== 'object' || raw === null || !('points' in raw) || !Array.isArray(raw.points) || !('contract' in raw) || typeof raw.contract !== 'object' || !('clusters' in raw) || !Array.isArray(raw.clusters)) throw new Error('The saved forecast file is incomplete. No replacement numbers have been supplied.');
  const run = raw as ViewRun;
  if (run.evidenceKind !== 'model-forecast' && run.evidenceKind !== 'synthetic-fixture') throw new Error('The forecast has an unrecognized source.');
  if (run.evidenceKind === 'synthetic-fixture' && !import.meta.env.DEV) throw new Error('Synthetic fixtures are disabled in the production demo.');
  validateRun(run);
  return run;
}
