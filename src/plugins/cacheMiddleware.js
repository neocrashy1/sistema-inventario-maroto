/**
 * Middleware de Cache para interceptar requisições HTTP
 * Aplica cache automaticamente baseado em configurações
 */

import { useApiCache, CACHE_STRATEGIES } from '@/composables/useApiCache'
import logger from '@/utils/logger'

// Configurações de cache por rota
const CACHE_CONFIG = {
  // Dashboard - dados que mudam frequentemente
  '/dashboard/stats': {
    strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
    ttl: 2 * 60 * 1000, // 2 minutos
    enabled: true
  },
  '/dashboard/metrics': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 5 * 60 * 1000, // 5 minutos
    enabled: true
  },
  '/dashboard/alerts': {
    strategy: CACHE_STRATEGIES.NETWORK_FIRST,
    ttl: 1 * 60 * 1000, // 1 minuto
    enabled: true
  },

  // Usuários - dados relativamente estáticos
  '/users': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 10 * 60 * 1000, // 10 minutos
    enabled: true
  },
  '/users/:id': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 15 * 60 * 1000, // 15 minutos
    enabled: true
  },

  // Localizações - dados muito estáticos
  '/locations': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 30 * 60 * 1000, // 30 minutos
    enabled: true
  },
  '/locations/:id': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 30 * 60 * 1000,
    enabled: true
  },

  // Máquinas - dados dinâmicos
  '/machines': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 5 * 60 * 1000, // 5 minutos
    enabled: true
  },
  '/machines/:id/status': {
    strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
    ttl: 30 * 1000, // 30 segundos
    enabled: true
  },

  // Tickets - dados críticos
  '/tickets': {
    strategy: CACHE_STRATEGIES.NETWORK_FIRST,
    ttl: 2 * 60 * 1000, // 2 minutos
    enabled: true
  },
  '/tickets/:id': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 5 * 60 * 1000,
    enabled: true
  },

  // Relatórios - dados que podem ser cacheados por mais tempo
  '/reports': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 15 * 60 * 1000, // 15 minutos
    enabled: true
  },

  // Configurações - dados estáticos
  '/settings': {
    strategy: CACHE_STRATEGIES.CACHE_FIRST,
    ttl: 60 * 60 * 1000, // 1 hora
    enabled: true
  }
}

// Padrões de URL que não devem ser cacheadas
const NO_CACHE_PATTERNS = [
  /\/auth\//,           // Autenticação
  /\/upload\//,         // Upload de arquivos
  /\/download\//,       // Download de arquivos
  /\/export\//,         // Exportação
  /\/import\//,         // Importação
  /\/backup\//,         // Backup
  /\/restore\//,        // Restore
  /\/password\//,       // Operações de senha
  /\/logout/,           // Logout
  /\/session\//         // Sessão
]

// Métodos HTTP que não devem ser cacheados
const NO_CACHE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

/**
 * Verifica se uma URL deve ser cacheada
 */
function shouldCache(url, method) {
  // Não cachear métodos de modificação
  if (NO_CACHE_METHODS.includes(method.toUpperCase())) {
    return false
  }

  // Não cachear URLs que correspondem aos padrões de exclusão
  if (NO_CACHE_PATTERNS.some(pattern => pattern.test(url))) {
    return false
  }

  return true
}

/**
 * Encontra configuração de cache para uma URL
 */
function findCacheConfig(url) {
  // Busca exata primeiro
  if (CACHE_CONFIG[url]) {
    return CACHE_CONFIG[url]
  }

  // Busca por padrões com parâmetros
  for (const [pattern, config] of Object.entries(CACHE_CONFIG)) {
    if (pattern.includes(':')) {
      const regex = new RegExp('^' + pattern.replace(/:[\w]+/g, '[^/]+') + '$')
      if (regex.test(url)) {
        return config
      }
    }
  }

  return null
}

/**
 * Gera chave de cache baseada na URL e parâmetros
 */
function generateCacheKey(url, params = {}) {
  const baseKey = url.replace(/^\//, '').replace(/\//g, ':')
  const paramString = Object.keys(params).length > 0 ? `:${JSON.stringify(params)}` : ''
  return `api:${baseKey}${paramString}`
}

/**
 * Middleware de cache para Axios
 */
export function createCacheMiddleware() {
  const { cachedRequest } = useApiCache()

  return {
    /**
     * Interceptor de requisição
     */
    request: (config) => {
      // Adicionar metadados de cache à configuração
      const url = config.url
      const method = config.method || 'GET'
      
      if (shouldCache(url, method)) {
        const cacheConfig = findCacheConfig(url)
        if (cacheConfig && cacheConfig.enabled) {
          config.metadata = {
            ...config.metadata,
            cache: {
              ...cacheConfig,
              cacheKey: generateCacheKey(url, config.params)
            }
          }
          
          logger.debug('Cache middleware: request configured for caching', {
            url,
            method,
            cacheKey: config.metadata.cache.cacheKey,
            strategy: cacheConfig.strategy,
            ttl: cacheConfig.ttl
          })
        }
      }

      return config
    },

    /**
     * Interceptor de resposta
     */
    response: (response) => {
      const config = response.config
      
      if (config.metadata?.cache) {
        logger.debug('Cache middleware: response processed', {
          url: config.url,
          cacheKey: config.metadata.cache.cacheKey,
          status: response.status
        })
      }

      return response
    },

    /**
     * Interceptor de erro
     */
    error: (error) => {
      const config = error.config
      
      if (config?.metadata?.cache) {
        logger.warn('Cache middleware: request failed', {
          url: config.url,
          cacheKey: config.metadata.cache.cacheKey,
          error: error.message
        })
      }

      return Promise.reject(error)
    }
  }
}

/**
 * Função para aplicar cache automaticamente a uma requisição
 */
export async function applyCacheToRequest(requestFn, config) {
  const { cachedRequest } = useApiCache()
  
  if (!config.metadata?.cache) {
    // Sem cache, executar requisição normal
    return requestFn()
  }

  const cacheConfig = config.metadata.cache
  
  return cachedRequest(requestFn, {
    cacheKey: cacheConfig.cacheKey,
    strategy: cacheConfig.strategy,
    ttl: cacheConfig.ttl,
    params: config.params
  })
}

/**
 * Plugin para Vue
 */
export default {
  install(app) {
    // Disponibilizar middleware globalmente
    app.config.globalProperties.$cacheMiddleware = createCacheMiddleware()
    
    // Disponibilizar configurações
    app.provide('cacheConfig', CACHE_CONFIG)
    
    logger.info('Cache middleware plugin installed')
  }
}