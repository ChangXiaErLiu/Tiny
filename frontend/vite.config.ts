import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import type { Connect } from 'vite'

function setupSSEProxy(server: any) {
  server.middlewares.use('/api/v1/chat/stream', (req: any, res: any, next: any) => {
    res.setHeader('X-Accel-Buffering', 'no')
    res.setHeader('Cache-Control', 'no-cache')
    res.setHeader('Connection', 'keep-alive')
    next()
  })
}

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'sse-proxy-setup',
      configureServer(server) {
        setupSSEProxy(server)
      }
    }
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true
      }
    }
  }
})
