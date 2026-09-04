import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api/v1': {
        target: 'http://ptc-backend:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
  },
})
