import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, mkdirSync, readdirSync, statSync } from 'fs'
import { join, resolve } from 'path'

// Plugin to copy locales to dist
function copyLocales() {
  return {
    name: 'copy-locales',
    closeBundle() {
      const src = 'public/locales'
      const dest = 'dist/locales'

      function copyRecursive(source: string, destination: string) {
        mkdirSync(destination, { recursive: true })
        const entries = readdirSync(source)

        for (const entry of entries) {
          const srcPath = join(source, entry)
          const destPath = join(destination, entry)

          if (statSync(srcPath).isDirectory()) {
            copyRecursive(srcPath, destPath)
          } else {
            copyFileSync(srcPath, destPath)
          }
        }
      }

      try {
        copyRecursive(src, dest)
        console.log('✅ Copied locales to dist/')
      } catch (err) {
        console.warn('⚠️ Could not copy locales:', err)
      }
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), copyLocales()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://ai-nurse-florence-development.up.railway.app',
        changeOrigin: true,
        secure: true,
      }
    }
  }
})