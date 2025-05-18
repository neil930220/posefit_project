import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'   // or react(), etc.
import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '',
  build: {
    manifest: true,
    outDir: resolve(__dirname, '../assets'),  // match STATICFILES_DIRS below
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.js'),  // adjust to your entrypoint
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