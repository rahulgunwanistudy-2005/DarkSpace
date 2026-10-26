import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,sep} from 'node:path';
import {loadEmbedder,EMBEDDING_CONTRACT} from '../packages/core/src/embed.ts';
const raw=await readFile('data/fixtures/gallery-and-forecasts.json');
const data=JSON.parse(raw),assets=resolve('.cache/placement-assets');
const model=await loadEmbedder(async path=>new Uint8Array(await readFile(resolve(assets,path))),resolve(assets,'runtime')+sep);
try{const vectors={};for(const point of data.forecast)vectors[point.id]=await model.embed(point.idea);
await writeFile('data/fixtures/vectors.json',JSON.stringify({sourceSha256:createHash('sha256').update(raw).digest('hex'),contract:EMBEDDING_CONTRACT,vectors})+'\n');console.log(`Embedded ${data.forecast.length} made-up fixture sentences using the shared WASM contract.`);
}finally{await model.close();}
