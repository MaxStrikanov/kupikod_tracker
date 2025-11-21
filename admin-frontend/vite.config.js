import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/bloggers': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/integrations': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
