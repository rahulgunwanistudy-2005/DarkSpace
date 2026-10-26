import { validateRun } from '../../../packages/core/src/place.ts';
import type { ForecastRun, Placement } from '../../../packages/core/src/contracts.ts';
export interface GalleryCard { id:string; title:string; tagline:string; dataLabel:string; forecastMatched?:boolean; controlMatched?:boolean }
export interface ViewRun extends ForecastRun {
  bundleKind:'fixture'|'local'; dataLabel:string;
  samplePlacements?:readonly Placement[];
  provenance?:Record<string,unknown>;
  gallery?:readonly GalleryCard[];
  backtest?:{evidence:string;eligible:number;coverage:{matched:number;rate:number};control:{matched:number;rate:number};lift_pp:number;ci_pp:readonly number[]};
}
export async function loadRun():Promise<ViewRun>{
  const response=await fetch('/data/current.json',{cache:'no-cache'});
  if(!response.ok)throw new Error('The saved data bundle is unavailable. Your sentence has not been replaced.');
  const raw:unknown=await response.json();
  if(!raw||typeof raw!=='object'||!('bundleKind' in raw))throw new Error('The data bundle has no publication boundary.');
  const run=raw as ViewRun;
  const local=import.meta.env.VITE_DARKSPACE_BUNDLE==='local';
  if(local){if(run.bundleKind!=='local'||run.evidenceKind!=='model-forecast')throw new Error('This local recording build requires a real model forecast bundle.');}
  else if(run.bundleKind!=='fixture'||run.evidenceKind!=='sample-data'||run.dataLabel!=='sample data'||!run.runId.startsWith('fixture-'))throw new Error('The public demo accepts only labelled sample data. Local real-run bundles cannot load here.');
  if(run.bundleKind==='fixture'&&(!Array.isArray(run.gallery)||run.gallery.some(card=>card.dataLabel!=='sample data')||run.points.some(point=>!('dataLabel' in point)||point.dataLabel!=='sample data')))throw new Error('A public sample card is missing its sample data label.');
  validateRun(run);return run;
}
