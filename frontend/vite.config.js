import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/',
  build: {
    manifest: false,
    outDir: resolve(__dirname, 'dist'),
    rollupOptions: { input: { main: resolve('./index.html') } }
  },
  server: {
    https: false,
    host: '0.0.0.0',   // listen on LAN
    port: 5173,
    cors: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization'
    },
    // only tweak HMR if you access via a custom host/proxy:
    hmr: {
      protocol: 'ws',   // or 'wss' if you serve over https
      // host: 'my.dev.host',   // set if you open via a domain/IP
      // clientPort: 5173,      // set if a reverse proxy changes ports
      overlay: true
    },
    proxy: {
      '/api':      { target: 'http://localhost:8000', changeOrigin: true, secure: false },
      '/accounts': { target: 'http://localhost:8000', changeOrigin: true, secure: false },
      '/media':    { target: 'http://localhost:8000', changeOrigin: true, secure: false },
      '/upload':   { target: 'http://localhost:8000', changeOrigin: true, secure: false }
    }
  },
  plugins: [vue(), tailwindcss()],
})
