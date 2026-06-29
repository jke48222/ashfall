import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: { port: 5173, host: true, strictPort: false },
  build: { target: 'es2020', outDir: 'dist', assetsInlineLimit: 0 },
});
