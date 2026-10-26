import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import adapter from '@sveltejs/adapter-static';

export default defineConfig({
  plugins: [sveltekit({ adapter: adapter(process.env.VITE_DARKSPACE_BUNDLE==='local'?{pages:'../.darkspace-local/site',assets:'../.darkspace-local/site'}:{}), csp: { mode: 'hash', directives: {
    'default-src': ['self'], 'script-src': ['self', 'wasm-unsafe-eval'],
    'connect-src': ['self'], 'worker-src': ['self'], 'object-src': ['none'],
    'base-uri': ['none'], 'style-src': ['self', 'unsafe-inline'],
  } } })],
  server: { fs: { allow: ['..'] } },
  resolve: { alias: [{ find: /^onnxruntime-web$/, replacement: 'onnxruntime-web/wasm' }] },
});
