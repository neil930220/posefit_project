import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'   // or react(), etc.
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/',
  build: {
    manifest: false,
    outDir: resolve(__dirname, 'dist'),
    rollupOptions: {
      input: {
        main: resolve('./index.html'),
      }
    }
  },
  define: {
    '__DEFINES__': JSON.stringify({}),
    '__BASE__': JSON.stringify('/'),
    '__SERVER_HOST__': JSON.stringify('http://localhost:8000'),
    '__WS_TOKEN__': JSON.stringify(null),
    '__HMR_CONFIG_NAME__': JSON.stringify('default'),
    '__HMR_PROTOCOL__': JSON.stringify('ws'),
    '__HMR_HOSTNAME__': JSON.stringify(null),
    '__HMR_PORT__': JSON.stringify(null),
    '__HMR_DIRECT_TARGET__': JSON.stringify(null),
    '__HMR_BASE__': JSON.stringify('/'),
    '__HMR_TIMEOUT__': JSON.stringify(30000),
    '__HMR_ENABLE_OVERLAY__': JSON.stringify(true),
    'process.env': {}
  },
  server: {
    https: false,   // disable HTTPS
    host: '0.0.0.0', // Allow external connections
    port: 5173,
    cors: true, // Enable CORS
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/accounts': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  plugins: [vue(), tailwindcss()],
})
