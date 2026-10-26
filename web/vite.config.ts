import { defineConfig, type Plugin } from 'vite';
import { readFileSync } from 'node:fs';
import { sveltekit } from '@sveltejs/kit/vite';
import adapter from '@sveltejs/adapter-static';

const engineeringFixture: Plugin = {
  name: 'explicit-development-fixture',
  configureServer(server) {
    server.middlewares.use((request,response,next)=>{
      if(request.url!=='/__engineering-fixture.json') return next();
      try {
        response.setHeader('Content-Type','application/json');
        response.end(readFileSync(new URL('../tests/fixtures/ui-engineering.json',import.meta.url)));
      } catch { response.statusCode=404;response.end('The explicit engineering fixture is unavailable.'); }
    });
  },
};

export default defineConfig({
  plugins: [engineeringFixture,sveltekit({ adapter: adapter(), csp: { mode: 'hash', directives: {
    'default-src': ['self'], 'script-src': ['self', 'wasm-unsafe-eval'],
    'connect-src': ['self'], 'worker-src': ['self'], 'object-src': ['none'],
    'base-uri': ['none'], 'style-src': ['self', 'unsafe-inline'],
  } } })],
  server: { fs: { allow: ['..'] } },
  resolve: { alias: [{ find: /^onnxruntime-web$/, replacement: 'onnxruntime-web/wasm' }] },
});
