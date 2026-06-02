import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    // 同时监听 127.0.0.1 与 localhost，避免仅用 IP 访问时连不上
    host: true,
    port: 3001,
    proxy: {
      '/api': {
        // TODO: 改成你自己 VM 的 IP 地址
        target: 'http://localhost:8006',
        changeOrigin: true
      }
    }
  }
})
