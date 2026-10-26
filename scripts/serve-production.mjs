import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { createHash } from 'node:crypto';

const root = resolve('web/build');
const port = Number(process.env.DARKSPACE_PORT ?? 4173);
const mime = { '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.mjs':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.json':'application/json; charset=utf-8', '.wasm':'application/wasm', '.onnx':'application/octet-stream', '.woff':'font/woff', '.woff2':'font/woff2', '.webp':'image/webp', '.svg':'image/svg+xml', '.png':'image/png' };
const commonPolicy = "connect-src 'self'; worker-src 'self'; frame-src 'none'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";
createServer(async (request,response) => {
  response.setHeader('X-Content-Type-Options','nosniff');
  response.setHeader('Referrer-Policy','no-referrer');
  response.setHeader('Cross-Origin-Resource-Policy','same-origin');
  response.setHeader('Content-Security-Policy',commonPolicy);
  if (!['GET','HEAD'].includes(request.method ?? '')) { response.writeHead(405);response.end();return; }
  try {
    const path = decodeURIComponent(new URL(request.url,'http://127.0.0.1').pathname);
    const target = resolve(root, '.'+path);
    if (target!==root && !target.startsWith(root+sep)) { response.writeHead(403);response.end();return; }
    let file = target;
    try { if((await stat(file)).isDirectory()) file=resolve(file,'index.html'); }
    catch { if(!extname(file)) file+='.html'; }
    const bytes = await readFile(file);
    const extension = extname(file);
    if(extension==='.js'||extension==='.mjs') response.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; "+commonPolicy);
    response.setHeader('Content-Type',mime[extension]??'application/octet-stream');
    response.setHeader('Cache-Control',path.includes('/immutable/')?'public, max-age=31536000, immutable':'no-cache');
    const etag='"'+createHash('sha256').update(bytes).digest('hex')+'"';
    response.setHeader('ETag',etag);
    if(request.headers['if-none-match']===etag){console.log(JSON.stringify({method:request.method,path,status:304}));response.writeHead(304);response.end();return;}
    response.setHeader('Content-Length',bytes.length);
    console.log(JSON.stringify({ method:request.method,path,status:200 }));
    response.writeHead(200);response.end(request.method==='HEAD'?undefined:bytes);
  } catch {
    console.log(JSON.stringify({ method:request.method,path:new URL(request.url,'http://127.0.0.1').pathname,status:404 }));
    response.writeHead(404);response.end('This file is unavailable.');
  }
}).listen(port,'127.0.0.1',()=>console.log(`Dark Space production preview: http://127.0.0.1:${port}`));
