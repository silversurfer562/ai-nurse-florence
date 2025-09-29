import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  root: 'frontend',
  base: '/frontend/',

  build: {
    outDir: '../static/dist',
    emptyOutDir: false,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'frontend/src/main.js'),
        'wizard-base': resolve(__dirname, 'frontend/src/components/wizards/BaseWizard.js'),
        'wizard-sbar': resolve(__dirname, 'frontend/src/components/wizards/SbarWizard.js'),
      },
      output: {
        entryFileNames: '[name]-[hash].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash][extname]'
      }
    }
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  css: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },

  optimizeDeps: {
    include: ['alpinejs', 'htmx.org']
  }
})
