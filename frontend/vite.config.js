import { copyFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages serves 404.html for unknown paths, so a copy of index.html makes deep links like /stages/mcp work.
const spaFallback = () => ({
  name: 'spa-404-fallback',
  apply: 'build',
  writeBundle({ dir }) {
    copyFileSync(resolve(dir, 'index.html'), resolve(dir, '404.html'))
  },
})

export default defineConfig(({ command, mode, isPreview }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const deployed = command === 'build' || isPreview
  return {
    base: deployed ? env.VITE_BASE_PATH || '/ai-made-easy/' : '/',
    plugins: [react(), spaFallback()],
    server: {
      port: Number(env.VITE_DEV_PORT) || 5173,
      strictPort: true,
    },
  }
})
