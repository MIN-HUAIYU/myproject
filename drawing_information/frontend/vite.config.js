import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
  // 环境变量配置（Vite会自动加载以VITE_为前缀的环境变量）
  define: {
    // 确保环境变量在构建时被正确注入
  }
})

