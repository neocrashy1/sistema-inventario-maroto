import { ref, computed } from 'vue'
import logger from '@/utils/logger'

/**
 * Composable para gerenciar cache inteligente de requisições API
 * Implementa estratégias de cache com TTL, invalidação e otimização de memória
 */

// Cache global em memória
const cache = new Map()
const cacheMetadata = new Map()

// Configurações padrão
const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutos
const MAX_CACHE_SIZE = 100 // Máximo de entradas no cache
const CACHE_CLEANUP_INTERVAL = 10 * 60 * 1000 // Limpeza a cada 10 minutos

// Estratégias de cache
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first', // Retorna cache se disponível, senão faz requisição
  NETWORK_FIRST: 'network-first', // Tenta rede primeiro, fallback para cache
  CACHE_ONLY: 'cache-only', // Apenas cache
  NETWORK_ONLY: 'network-only', // Apenas rede
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate' // Retorna cache e atualiza em background
}

export function useApiCache() {
  const isLoading = ref(false)
  const error = ref(null)

  /**
   * Gera chave única para cache baseada na URL e parâmetros
   */
  function generateCacheKey(url, params = {}) {
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((result, key) => {
        result[key] = params[key]
        return result
      }, {})
    
    return `${url}:${JSON.stringify(sortedParams)}`
  }

  /**
   * Verifica se uma entrada do cache é válida
   */
  function isCacheValid(key) {
    const metadata = cacheMetadata.get(key)
    if (!metadata) return false
    
    const now = Date.now()
    return now < metadata.expiresAt
  }

  /**
   * Adiciona entrada ao cache
   */
  function setCacheEntry(key, data, ttl = DEFAULT_TTL) {
    // Limpar cache se exceder o tamanho máximo
    if (cache.size >= MAX_CACHE_SIZE) {
      cleanupOldEntries()
    }

    const now = Date.now()
    const metadata = {
      createdAt: now,
      expiresAt: now + ttl,
      accessCount: 0,
      lastAccessed: now,
      size: JSON.stringify(data).length
    }

    cache.set(key, data)
    cacheMetadata.set(key, metadata)

    logger.debug('Cache entry added', { key, ttl, size: metadata.size })
  }

  /**
   * Obtém entrada do cache
   */
  function getCacheEntry(key) {
    if (!cache.has(key) || !isCacheValid(key)) {
      return null
    }

    const data = cache.get(key)
    const metadata = cacheMetadata.get(key)
    
    // Atualizar metadados de acesso
    metadata.accessCount++
    metadata.lastAccessed = Date.now()
    cacheMetadata.set(key, metadata)

    logger.debug('Cache hit', { key, accessCount: metadata.accessCount })
    return data
  }

  /**
   * Remove entrada específica do cache
   */
  function invalidateCache(key) {
    const removed = cache.delete(key) && cacheMetadata.delete(key)
    if (removed) {
      logger.debug('Cache invalidated', { key })
    }
    return removed
  }

  /**
   * Remove entradas do cache por padrão
   */
  function invalidateCachePattern(pattern) {
    const regex = new RegExp(pattern)
    let removedCount = 0

    for (const key of cache.keys()) {
      if (regex.test(key)) {
        cache.delete(key)
        cacheMetadata.delete(key)
        removedCount++
      }
    }

    logger.debug('Cache pattern invalidated', { pattern, removedCount })
    return removedCount
  }

  /**
   * Limpa entradas antigas do cache
   */
  function cleanupOldEntries() {
    const now = Date.now()
    let removedCount = 0

    // Remover entradas expiradas
    for (const [key, metadata] of cacheMetadata.entries()) {
      if (now >= metadata.expiresAt) {
        cache.delete(key)
        cacheMetadata.delete(key)
        removedCount++
      }
    }

    // Se ainda exceder o limite, remover as menos acessadas
    if (cache.size >= MAX_CACHE_SIZE) {
      const entries = Array.from(cacheMetadata.entries())
        .sort((a, b) => {
          // Priorizar por frequência de acesso e recência
          const scoreA = a[1].accessCount * (now - a[1].lastAccessed)
          const scoreB = b[1].accessCount * (now - b[1].lastAccessed)
          return scoreA - scoreB
        })

      const toRemove = entries.slice(0, Math.floor(MAX_CACHE_SIZE * 0.2)) // Remove 20%
      toRemove.forEach(([key]) => {
        cache.delete(key)
        cacheMetadata.delete(key)
        removedCount++
      })
    }

    logger.debug('Cache cleanup completed', { removedCount, currentSize: cache.size })
  }

  /**
   * Executa requisição com cache inteligente
   */
  async function cachedRequest(
    requestFn,
    {
      cacheKey,
      strategy = CACHE_STRATEGIES.CACHE_FIRST,
      ttl = DEFAULT_TTL,
      params = {},
      forceRefresh = false
    } = {}
  ) {
    const key = cacheKey || generateCacheKey(requestFn.name, params)
    
    isLoading.value = true
    error.value = null

    try {
      // Estratégia CACHE_ONLY
      if (strategy === CACHE_STRATEGIES.CACHE_ONLY) {
        const cachedData = getCacheEntry(key)
        if (cachedData) {
          return cachedData
        }
        throw new Error('Dados não encontrados no cache')
      }

      // Estratégia NETWORK_ONLY
      if (strategy === CACHE_STRATEGIES.NETWORK_ONLY || forceRefresh) {
        const data = await requestFn(params)
        setCacheEntry(key, data, ttl)
        return data
      }

      // Estratégia CACHE_FIRST
      if (strategy === CACHE_STRATEGIES.CACHE_FIRST) {
        const cachedData = getCacheEntry(key)
        if (cachedData) {
          return cachedData
        }
        
        const data = await requestFn(params)
        setCacheEntry(key, data, ttl)
        return data
      }

      // Estratégia NETWORK_FIRST
      if (strategy === CACHE_STRATEGIES.NETWORK_FIRST) {
        try {
          const data = await requestFn(params)
          setCacheEntry(key, data, ttl)
          return data
        } catch (networkError) {
          const cachedData = getCacheEntry(key)
          if (cachedData) {
            logger.warn('Network failed, using cached data', { key, error: networkError.message })
            return cachedData
          }
          throw networkError
        }
      }

      // Estratégia STALE_WHILE_REVALIDATE
      if (strategy === CACHE_STRATEGIES.STALE_WHILE_REVALIDATE) {
        const cachedData = getCacheEntry(key)
        
        // Atualizar em background
        requestFn(params)
          .then(data => setCacheEntry(key, data, ttl))
          .catch(err => logger.warn('Background revalidation failed', { key, error: err.message }))
        
        if (cachedData) {
          return cachedData
        }
        
        // Se não há cache, aguardar a requisição
        const data = await requestFn(params)
        setCacheEntry(key, data, ttl)
        return data
      }

    } catch (err) {
      error.value = err
      logger.error('Cached request failed', { key, strategy, error: err.message })
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtém estatísticas do cache
   */
  function getCacheStats() {
    const now = Date.now()
    let totalSize = 0
    let expiredCount = 0
    let totalAccess = 0

    for (const [key, metadata] of cacheMetadata.entries()) {
      totalSize += metadata.size
      totalAccess += metadata.accessCount
      if (now >= metadata.expiresAt) {
        expiredCount++
      }
    }

    return {
      totalEntries: cache.size,
      totalSize,
      expiredCount,
      totalAccess,
      averageAccess: cache.size > 0 ? totalAccess / cache.size : 0,
      hitRate: computed(() => {
        // Calcular taxa de acerto baseada nos metadados
        return cache.size > 0 ? (totalAccess / cache.size) * 100 : 0
      })
    }
  }

  /**
   * Limpa todo o cache
   */
  function clearCache() {
    const size = cache.size
    cache.clear()
    cacheMetadata.clear()
    logger.info('Cache cleared', { entriesRemoved: size })
  }

  // Configurar limpeza automática
  if (typeof window !== 'undefined') {
    setInterval(cleanupOldEntries, CACHE_CLEANUP_INTERVAL)
  }

  return {
    // Estado
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    
    // Métodos principais
    cachedRequest,
    
    // Gerenciamento de cache
    setCacheEntry,
    getCacheEntry,
    invalidateCache,
    invalidateCachePattern,
    clearCache,
    
    // Utilitários
    generateCacheKey,
    getCacheStats,
    
    // Constantes
    CACHE_STRATEGIES
  }
}

// Export das estratégias para uso direto
export { CACHE_STRATEGIES }