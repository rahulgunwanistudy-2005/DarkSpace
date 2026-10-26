import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
const root=resolve('web/build');
const bytes=await readFile(resolve(root,'data/current.json'));
const run=JSON.parse(bytes);
assert.equal(run.bundleKind,'fixture');assert.equal(run.dataLabel,'sample data');
assert.ok([...run.gallery,...run.points].every(card=>card.dataLabel==='sample data'));
assert.deepEqual(bytes,await readFile(resolve('data/runs',run.runId,'public-bundle.json')));
async function paths(directory){const found=[];for(const entry of await readdir(directory,{withFileTypes:true})){const path=resolve(directory,entry.name);if(entry.isDirectory())found.push(...await paths(path));else found.push(path);}return found;}
const files=await paths(root);
assert.ok(!files.some(path=>/\.sqlite|\.darkspace-local|corpus\.json|samples\.json/.test(path)));
console.log(JSON.stringify({publicBuild:'verified',dataLabel:'sample data',gallery:run.gallery.length,forecast:run.points.length,countersMatchRunArtifact:true,localCorpusFiles:0}));
