import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
if(process.env.CI)throw new Error('Local recording builds cannot run in CI.');
const bundle=await readFile('.darkspace-local/bundles/current/data/current.json');
if(JSON.parse(bundle).bundleKind!=='local')throw new Error('Export a local real-run bundle first.');
const result=spawnSync('npm',['run','build','--workspace','web'],{stdio:'inherit',env:{...process.env,VITE_DARKSPACE_BUNDLE:'local'}});
if(result.status!==0)process.exit(result.status??1);
await mkdir('.darkspace-local/site/data',{recursive:true});await writeFile('.darkspace-local/site/data/current.json',bundle);
console.log('LOCAL RECORDING BUILD: ignored .darkspace-local/site; never publish this directory.');
