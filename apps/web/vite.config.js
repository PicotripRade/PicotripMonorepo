import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import * as path from "node:path"

export default defineConfig(({ mode }) => {
  // Load shared + web env
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@picotrip/shared": path.resolve(__dirname, "../../packages/shared"),
      },
    },
    server: {
      host: '0.0.0.0', // Listen on all network interfaces
      allowedHosts: ['picotrip.local.com', '.local'], // Allow local domains
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://picotrip.local.com:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    define: {
      __APP_NAME__: JSON.stringify(env.APP_NAME),
    }
  }
})