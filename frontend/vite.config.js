import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'   // or react(), etc.
import { resolve } from 'path'

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
  plugins: [vue()],
})