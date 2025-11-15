import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  base: '/',
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
    host: 'localhost',
    port: 5173,
    open: false,
    cors: true,
    strictPort: true,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
    proxy: {
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve('./src/static/src'),
    },
  },
});
