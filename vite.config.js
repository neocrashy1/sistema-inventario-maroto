import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// Plugin para remover console.log em produção
const removeConsolePlugin = () => {
  return {
    name: 'remove-console',
    transform(code, id) {
      if (process.env.NODE_ENV === 'production') {
        // Remove console.log, mas mantém console.error e console.warn
        return {
          code: code.replace(/console\.log\([^)]*\);?/g, ''),
          map: null
        }
      }
      return null
    }
  }
}

export default defineConfig({
  plugins: [
    vue(),
    removeConsolePlugin()
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: Number(process.env.PORT) || 3000,
    open: true,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/analytics': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Otimizações para produção
    minify: 'terser',
    terserOptions: {
      compress: {
        // Remove console.log em produção
        drop_console: ['log'],
        drop_debugger: true
      }
    },
    // Code splitting otimizado
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['chart.js', 'vue-chartjs'],
          'utils-vendor': ['axios', 'date-fns']
        }
      }
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000
  },
  // Variáveis de ambiente
  define: {
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false
  }
})