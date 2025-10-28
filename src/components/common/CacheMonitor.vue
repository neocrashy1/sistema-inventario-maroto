<template>
  <div class="cache-monitor" v-if="showMonitor">
    <div class="cache-monitor__header">
      <h3>Cache Monitor</h3>
      <button @click="toggleExpanded" class="cache-monitor__toggle">
        {{ expanded ? '−' : '+' }}
      </button>
      <button @click="closeMonitor" class="cache-monitor__close">×</button>
    </div>
    
    <div v-if="expanded" class="cache-monitor__content">
      <!-- Estatísticas gerais -->
      <div class="cache-stats">
        <div class="stat-item">
          <span class="stat-label">Total de Entradas:</span>
          <span class="stat-value">{{ cacheStats.totalEntries }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Hit Rate:</span>
          <span class="stat-value">{{ cacheStats.hitRate }}%</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Tamanho do Cache:</span>
          <span class="stat-value">{{ formatBytes(cacheStats.totalSize) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Última Limpeza:</span>
          <span class="stat-value">{{ formatTime(cacheStats.lastCleanup) }}</span>
        </div>
      </div>

      <!-- Lista de entradas do cache -->
      <div class="cache-entries">
        <h4>Entradas do Cache</h4>
        <div class="cache-entry" v-for="entry in cacheEntries" :key="entry.key">
          <div class="entry-header">
            <span class="entry-key">{{ entry.key }}</span>
            <span class="entry-status" :class="entry.status">{{ entry.status }}</span>
          </div>
          <div class="entry-details">
            <span class="entry-detail">TTL: {{ formatTTL(entry.ttl) }}</span>
            <span class="entry-detail">Hits: {{ entry.hits }}</span>
            <span class="entry-detail">Tamanho: {{ formatBytes(entry.size) }}</span>
            <span class="entry-detail">Criado: {{ formatTime(entry.createdAt) }}</span>
          </div>
          <div class="entry-actions">
            <button @click="invalidateEntry(entry.key)" class="btn-invalidate">
              Invalidar
            </button>
          </div>
        </div>
      </div>

      <!-- Ações do cache -->
      <div class="cache-actions">
        <button @click="clearAllCache" class="btn-clear-all">
          Limpar Todo Cache
        </button>
        <button @click="refreshStats" class="btn-refresh">
          Atualizar Estatísticas
        </button>
        <button @click="exportCacheData" class="btn-export">
          Exportar Dados
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useApiCache } from '@/composables/useApiCache'
import { useCacheInvalidation } from '@/composables/useCacheInvalidation'
import logger from '@/utils/logger'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  position: {
    type: String,
    default: 'bottom-right',
    validator: (value) => ['top-left', 'top-right', 'bottom-left', 'bottom-right'].includes(value)
  }
})

// Emits
const emit = defineEmits(['close'])

// Composables
const { getCacheStats, getCacheEntries, invalidateCache } = useApiCache()
const { clearAllCache: clearCache } = useCacheInvalidation()

// Estado reativo
const showMonitor = ref(props.visible)
const expanded = ref(false)
const cacheStats = ref({
  totalEntries: 0,
  hitRate: 0,
  totalSize: 0,
  lastCleanup: null
})
const cacheEntries = ref([])
const refreshInterval = ref(null)

// Computed
const monitorClasses = computed(() => [
  'cache-monitor',
  `cache-monitor--${props.position}`
])

// Métodos
const toggleExpanded = () => {
  expanded.value = !expanded.value
  if (expanded.value) {
    refreshStats()
  }
}

const closeMonitor = () => {
  showMonitor.value = false
  emit('close')
}

const refreshStats = async () => {
  try {
    cacheStats.value = await getCacheStats()
    if (expanded.value) {
      cacheEntries.value = await getCacheEntries()
    }
  } catch (error) {
    logger.error('Failed to refresh cache stats', { error: error.message })
  }
}

const invalidateEntry = async (key) => {
  try {
    await invalidateCache(key)
    await refreshStats()
    logger.info('Cache entry invalidated', { key })
  } catch (error) {
    logger.error('Failed to invalidate cache entry', { key, error: error.message })
  }
}

const clearAllCache = async () => {
  if (confirm('Tem certeza que deseja limpar todo o cache?')) {
    try {
      await clearCache()
      await refreshStats()
      logger.info('All cache cleared')
    } catch (error) {
      logger.error('Failed to clear all cache', { error: error.message })
    }
  }
}

const exportCacheData = () => {
  const data = {
    stats: cacheStats.value,
    entries: cacheEntries.value,
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `cache-data-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  logger.info('Cache data exported')
}

// Formatação
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  return new Date(timestamp).toLocaleString('pt-BR')
}

const formatTTL = (ttl) => {
  if (!ttl) return 'Sem expiração'
  const seconds = Math.floor(ttl / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  return `${hours}h`
}

// Lifecycle
onMounted(() => {
  refreshStats()
  // Atualizar estatísticas a cada 5 segundos quando expandido
  refreshInterval.value = setInterval(() => {
    if (expanded.value) {
      refreshStats()
    }
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})

// Watchers
watch(() => props.visible, (newValue) => {
  showMonitor.value = newValue
})
</script>

<style scoped>
.cache-monitor {
  position: fixed;
  z-index: 9999;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 300px;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 12px;
}

.cache-monitor--top-left {
  top: 20px;
  left: 20px;
}

.cache-monitor--top-right {
  top: 20px;
  right: 20px;
}

.cache-monitor--bottom-left {
  bottom: 20px;
  left: 20px;
}

.cache-monitor--bottom-right {
  bottom: 20px;
  right: 20px;
}

.cache-monitor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e1e5e9;
}

.cache-monitor__header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.cache-monitor__toggle,
.cache-monitor__close {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: #718096;
}

.cache-monitor__toggle:hover,
.cache-monitor__close:hover {
  background: #e2e8f0;
  color: #2d3748;
}

.cache-monitor__content {
  max-height: 60vh;
  overflow-y: auto;
  padding: 16px;
}

.cache-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f7fafc;
  border-radius: 6px;
}

.stat-label {
  font-weight: 500;
  color: #4a5568;
}

.stat-value {
  font-weight: 600;
  color: #2d3748;
}

.cache-entries h4 {
  margin: 0 0 12px 0;
  font-size: 13px;
  font-weight: 600;
  color: #2d3748;
}

.cache-entry {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  margin-bottom: 8px;
  padding: 12px;
  background: #fafafa;
}

.entry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.entry-key {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #2d3748;
  font-weight: 500;
}

.entry-status {
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.entry-status.fresh {
  background: #c6f6d5;
  color: #22543d;
}

.entry-status.stale {
  background: #fed7d7;
  color: #742a2a;
}

.entry-status.expired {
  background: #e2e8f0;
  color: #4a5568;
}

.entry-details {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.entry-detail {
  font-size: 10px;
  color: #718096;
}

.entry-actions {
  display: flex;
  gap: 8px;
}

.btn-invalidate {
  background: #fed7d7;
  color: #742a2a;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  cursor: pointer;
}

.btn-invalidate:hover {
  background: #feb2b2;
}

.cache-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.cache-actions button {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #4a5568;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.cache-actions button:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}

.btn-clear-all {
  background: #fed7d7 !important;
  color: #742a2a !important;
  border-color: #feb2b2 !important;
}

.btn-clear-all:hover {
  background: #feb2b2 !important;
}
</style>