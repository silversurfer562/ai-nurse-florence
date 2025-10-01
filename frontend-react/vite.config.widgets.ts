import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// Special build configuration for React widgets that can be embedded in existing HTML pages
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
    'process.env': '{}',
  },
  build: {
    outDir: '../static/widgets',
    lib: {
      // Build only SBAR wizard for now (IIFE doesn't support multiple entries)
      entry: resolve(__dirname, 'src/widgets/SbarWizard/index.tsx'),
      formats: ['iife'],
      name: 'SbarWizardWidget',
      fileName: 'sbar-wizard',
    },
    rollupOptions: {
      external: [],
      output: {
        // Ensure React and ReactDOM are bundled
        globals: {},
        assetFileNames: '[name].[ext]',
      },
    },
    sourcemap: true,
  },
})
