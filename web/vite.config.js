import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        // 默认后端运行在 8000 端口
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('');
            console.log('⚠️  API 代理失败');
            console.log('   请确保后端已启动: python start_web.py');
            console.log('   当前目标:', options.target);
            console.log('   如后端运行在其他端口，请设置: VITE_API_URL=http://localhost:端口号 npm run dev');
            console.log('');
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            if (process.env.DEBUG) {
              console.log('🔄 [API]', req.method, req.url, '→', options.target);
            }
          });
        }
      }
    }
  }
})
