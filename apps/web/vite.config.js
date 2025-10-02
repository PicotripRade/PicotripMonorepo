import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import * as path from "node:path";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@picotrip/shared": path.resolve(__dirname, "../../packages/shared"),
        },
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                secure: false,
            },
        },
    },
})
