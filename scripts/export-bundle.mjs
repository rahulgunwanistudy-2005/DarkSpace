import {readFile,writeFile,mkdir,realpath} from 'node:fs/promises';
import {resolve,sep} from 'node:path';
import {createHash} from 'node:crypto';
import {validateRun,place} from '../packages/core/src/place.ts';
const [mode,input]=process.argv.slice(2);
if(!['fixture','local'].includes(mode)||!input)throw new Error('Usage: node scripts/export-bundle.mjs <fixture|local> <run.json>');
const source=JSON.parse(await readFile(input,'utf8'));validateRun(source);
let target;
if(mode==='fixture'){
 if(source.bundleKind!=='fixture'||source.dataLabel!=='sample data'||source.evidenceKind!=='sample-data'||!source.runId.startsWith('fixture-'))throw new Error('Public export accepts only the made-up fixture bundle.');
 const allowed=resolve('data/runs',source.runId,'bundle.json');
 if(await realpath(input)!==await realpath(allowed))throw new Error('Public export must use the recorded fixture artifact.');
 if([...source.points,...source.gallery].some(row=>row.dataLabel!=='sample data'))throw new Error('Every public card must be labelled sample data.');
 target=resolve('web/static/data');
}else{
 if(source.evidenceKind!=='model-forecast'||source.bundleKind==='fixture')throw new Error('Local real-run export refuses fixture data.');
 source.bundleKind='local';source.dataLabel='local recording';
 if(source.gallery){source.gallery=source.gallery.map((row,index)=>{if(typeof row.displaySummary!=='string')throw new Error('Local gallery cards require an anonymised displaySummary. Original titles/taglines are not copied to cards.');return {id:row.id,title:`Project ${index+1}`,tagline:row.displaySummary,dataLabel:'local recording',forecastMatched:row.forecastMatched,controlMatched:row.controlMatched};});}
 target=resolve('.darkspace-local/bundles/current/data');
 const localRoot=resolve('.darkspace-local');await mkdir(target,{recursive:true});if(!(await realpath(target)).startsWith((await realpath(localRoot))+sep))throw new Error('Local export escaped its ignored directory.');
}
source.samplePlacements??=[place(source,{idea:source.points[0].idea,vector:source.points[0].vector,contract:source.contract,kind:'sample'})];
const payload=JSON.stringify(source)+'\n';
if(mode==='fixture'){await writeFile(resolve('data/runs',source.runId,'public-bundle.json'),payload);await writeFile(resolve('data/runs',source.runId,'public-export.json'),JSON.stringify({runId:source.runId,dataLabel:'sample data',sha256:createHash('sha256').update(payload).digest('hex')})+'\n');}
await mkdir(target,{recursive:true});await writeFile(resolve(target,'current.json'),payload);
console.log(JSON.stringify({mode,target:resolve(target,'current.json'),runId:source.runId,sha256:createHash('sha256').update(payload).digest('hex'),dataLabel:source.dataLabel,points:source.points.length,realBacktest:source.backtest?.evidence==='real-validated'?'provided':'not validated'},null,2));
