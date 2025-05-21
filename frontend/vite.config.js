import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'   // or react(), etc.
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: './',
  build: {
    manifest: true,
    outDir: resolve(__dirname, 'dist'),
    rollupOptions: {
      input: {
        main: resolve('./index.html'),
      }
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/accounts': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
      '/upload': 'http://localhost:8000',     
    }
  },
  plugins: [vue(),tailwindcss(),],
})
