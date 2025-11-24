import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/static',
  css: {
    postcss: './postcss.config.js',
  },
  root: resolve('./src/static/src'),
  build: {
    manifest: 'manifest.json',
    outDir: resolve('./src/static/dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve('./src/static/src/main.ts'),
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    open: false,
    cors: true,
    strictPort: true,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
    origin: 'http://localhost:5173',
  },
  resolve: {
    alias: {
      '@': resolve('./src/static/src'),
    },
  },
});
