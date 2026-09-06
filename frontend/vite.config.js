import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端端口：默认 5050，换端口时 VITE_API_PORT=6000 npm run dev
const API_PORT = process.env.VITE_API_PORT || '5050'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: `http://127.0.0.1:${API_PORT}`,
        changeOrigin: true
      }
    }
  }
})
