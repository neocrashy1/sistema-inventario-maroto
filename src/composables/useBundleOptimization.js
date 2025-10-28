import logger from '@/utils/logger'
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'

/**
 * Composable para otimização de bundle e análise de performance
 */
export function useBundleOptimization(options = {}) {
  const {
    enableAnalytics = true,
    enablePreloading = true,
    enablePrefetching = true,
    chunkSizeThreshold = 250000, // 250KB
    enableResourceHints = true,
    enableServiceWorker = false
  } = options

  // Estados reativos
  const bundleStats = reactive({
    totalSize: 0,
    gzippedSize: 0,
    chunks: [],
    loadedChunks: new Set(),
    failedChunks: new Set(),
    loadTimes: new Map(),
    cacheHits: 0,
    cacheMisses: 0
  })

  const loadingState = reactive({
    isLoading: false,
    loadingChunks: new Set(),
    queuedChunks: new Set(),
    preloadedChunks: new Set(),
    prefetchedChunks: new Set()
  })

  const performanceMetrics = reactive({
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    firstInputDelay: 0,
    cumulativeLayoutShift: 0,
    timeToInteractive: 0,
    totalBlockingTime: 0
  })

  const resourceHints = ref([])
  const criticalResources = ref([])
  const deferredResources = ref([])

  /**
   * Analisa chunks carregados
   */
  const analyzeLoadedChunks = () => {
    if (!window.performance) return

    const entries = performance.getEntriesByType('navigation')
    const resourceEntries = performance.getEntriesByType('resource')

    // Analisa recursos JavaScript
    const jsResources = resourceEntries.filter(entry => 
      entry.name.includes('.js') && !entry.name.includes('node_modules')
    )

    bundleStats.chunks = jsResources.map(resource => ({
      name: resource.name.split('/').pop(),
      url: resource.name,
      size: resource.transferSize || 0,
      loadTime: resource.responseEnd - resource.requestStart,
      cached: resource.transferSize === 0,
      critical: resource.name.includes('app.') || resource.name.includes('vendor.'),
      type: getChunkType(resource.name)
    }))

    // Calcula tamanho total
    bundleStats.totalSize = bundleStats.chunks.reduce((total, chunk) => total + chunk.size, 0)

    // Atualiza estatísticas de cache
    bundleStats.cacheHits = bundleStats.chunks.filter(chunk => chunk.cached).length
    bundleStats.cacheMisses = bundleStats.chunks.filter(chunk => !chunk.cached).length
  }

  /**
   * Determina o tipo do chunk
   */
  const getChunkType = (url) => {
    if (url.includes('vendor') || url.includes('node_modules')) return 'vendor'
    if (url.includes('app.') || url.includes('main.')) return 'app'
    if (url.includes('chunk')) return 'async'
    return 'unknown'
  }

  /**
   * Carrega chunk dinamicamente com otimizações
   */
  const loadChunk = async (chunkName, options = {}) => {
    const {
      priority = 'normal',
      preload = false,
      prefetch = false,
      timeout = 30000,
      retries = 3
    } = options

    if (bundleStats.loadedChunks.has(chunkName)) {
      return Promise.resolve()
    }

    if (loadingState.loadingChunks.has(chunkName)) {
      // Aguarda carregamento em andamento
      return new Promise((resolve, reject) => {
        const checkLoaded = () => {
          if (bundleStats.loadedChunks.has(chunkName)) {
            resolve()
          } else if (bundleStats.failedChunks.has(chunkName)) {
            reject(new Error(`Failed to load chunk: ${chunkName}`))
          } else {
            setTimeout(checkLoaded, 100)
          }
        }
        checkLoaded()
      })
    }

    loadingState.loadingChunks.add(chunkName)
    loadingState.isLoading = true

    const startTime = performance.now()

    try {
      let attempt = 0
      let lastError

      while (attempt < retries) {
        try {
          // Estratégias diferentes baseadas na prioridade
          if (priority === 'high') {
            await loadChunkWithHighPriority(chunkName)
          } else if (preload) {
            await loadChunkWithPreload(chunkName)
          } else if (prefetch) {
            await loadChunkWithPrefetch(chunkName)
          } else {
            await loadChunkNormal(chunkName)
          }

          // Sucesso
          bundleStats.loadedChunks.add(chunkName)
          bundleStats.loadTimes.set(chunkName, performance.now() - startTime)
          break

        } catch (error) {
          lastError = error
          attempt++
          
          if (attempt < retries) {
            // Aguarda antes de tentar novamente (backoff exponencial)
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000))
          }
        }
      }

      if (attempt >= retries) {
        bundleStats.failedChunks.add(chunkName)
        throw lastError
      }

    } finally {
      loadingState.loadingChunks.delete(chunkName)
      loadingState.isLoading = loadingState.loadingChunks.size > 0
    }
  }

  /**
   * Carrega chunk com alta prioridade
   */
  const loadChunkWithHighPriority = async (chunkName) => {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = getChunkUrl(chunkName)
      script.async = false // Carregamento síncrono para alta prioridade
      script.onload = resolve
      script.onerror = reject
      
      // Adiciona ao head para prioridade máxima
      document.head.appendChild(script)
    })
  }

  /**
   * Carrega chunk com preload
   */
  const loadChunkWithPreload = async (chunkName) => {
    if (loadingState.preloadedChunks.has(chunkName)) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      const link = document.createElement('link')
      link.rel = 'preload'
      link.as = 'script'
      link.href = getChunkUrl(chunkName)
      link.onload = () => {
        loadingState.preloadedChunks.add(chunkName)
        
        // Agora carrega o script
        const script = document.createElement('script')
        script.src = link.href
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      }
      link.onerror = reject
      
      document.head.appendChild(link)
    })
  }

  /**
   * Carrega chunk com prefetch
   */
  const loadChunkWithPrefetch = async (chunkName) => {
    if (loadingState.prefetchedChunks.has(chunkName)) {
      return loadChunkNormal(chunkName)
    }

    // Primeiro faz prefetch
    const link = document.createElement('link')
    link.rel = 'prefetch'
    link.href = getChunkUrl(chunkName)
    document.head.appendChild(link)
    
    loadingState.prefetchedChunks.add(chunkName)

    // Aguarda um pouco e então carrega
    await new Promise(resolve => setTimeout(resolve, 100))
    return loadChunkNormal(chunkName)
  }

  /**
   * Carrega chunk normalmente
   */
  const loadChunkNormal = async (chunkName) => {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = getChunkUrl(chunkName)
      script.async = true
      script.onload = resolve
      script.onerror = reject
      
      document.head.appendChild(script)
    })
  }

  /**
   * Obtém URL do chunk
   */
  const getChunkUrl = (chunkName) => {
    // Lógica para construir URL do chunk
    const baseUrl = import.meta.env.BASE_URL || '/'
    return `${baseUrl}assets/${chunkName}.js`
  }

  /**
   * Precarrega chunks críticos
   */
  const preloadCriticalChunks = async (chunkNames) => {
    const promises = chunkNames.map(chunkName => 
      loadChunk(chunkName, { preload: true, priority: 'high' })
    )
    
    try {
      await Promise.all(promises)
      logger.debug('Critical chunks preloaded successfully')
    } catch (error) {
      logger.warn('Some critical chunks failed to preload:', error)
    }
  }

  /**
   * Prefetch chunks não críticos
   */
  const prefetchNonCriticalChunks = async (chunkNames) => {
    // Aguarda idle time
    if (window.requestIdleCallback) {
      return new Promise(resolve => {
        window.requestIdleCallback(async () => {
          const promises = chunkNames.map(chunkName => 
            loadChunk(chunkName, { prefetch: true, priority: 'low' })
          )
          
          try {
            await Promise.allSettled(promises)
            logger.debug('Non-critical chunks prefetched')
          } catch (error) {
            logger.warn('Some non-critical chunks failed to prefetch:', error)
          }
          
          resolve()
        })
      })
    } else {
      // Fallback: aguarda 2 segundos
      setTimeout(async () => {
        const promises = chunkNames.map(chunkName => 
          loadChunk(chunkName, { prefetch: true, priority: 'low' })
        )
        
        await Promise.allSettled(promises)
      }, 2000)
    }
  }

  /**
   * Analisa performance web vitals
   */
  const analyzeWebVitals = () => {
    if (!window.performance) return

    // First Contentful Paint
    const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0]
    if (fcpEntry) {
      performanceMetrics.firstContentfulPaint = fcpEntry.startTime
    }

    // Largest Contentful Paint
    if (window.PerformanceObserver) {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        performanceMetrics.largestContentfulPaint = lastEntry.startTime
      })
      
      try {
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] })
      } catch (e) {
        // LCP não suportado
      }

      // First Input Delay
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach(entry => {
          performanceMetrics.firstInputDelay = entry.processingStart - entry.startTime
        })
      })
      
      try {
        fidObserver.observe({ entryTypes: ['first-input'] })
      } catch (e) {
        // FID não suportado
      }

      // Cumulative Layout Shift
      const clsObserver = new PerformanceObserver((list) => {
        let clsValue = 0
        const entries = list.getEntries()
        
        entries.forEach(entry => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        })
        
        performanceMetrics.cumulativeLayoutShift = clsValue
      })
      
      try {
        clsObserver.observe({ entryTypes: ['layout-shift'] })
      } catch (e) {
        // CLS não suportado
      }
    }
  }

  /**
   * Otimiza carregamento de recursos
   */
  const optimizeResourceLoading = () => {
    if (!enableResourceHints) return

    // Identifica recursos críticos
    criticalResources.value = bundleStats.chunks
      .filter(chunk => chunk.critical || chunk.type === 'app')
      .map(chunk => ({
        url: chunk.url,
        type: 'script',
        priority: 'high'
      }))

    // Identifica recursos diferidos
    deferredResources.value = bundleStats.chunks
      .filter(chunk => !chunk.critical && chunk.type === 'async')
      .map(chunk => ({
        url: chunk.url,
        type: 'script',
        priority: 'low'
      }))

    // Gera resource hints
    resourceHints.value = [
      ...criticalResources.value.map(resource => ({
        rel: 'preload',
        href: resource.url,
        as: resource.type
      })),
      ...deferredResources.value.map(resource => ({
        rel: 'prefetch',
        href: resource.url
      }))
    ]
  }

  /**
   * Aplica resource hints no DOM
   */
  const applyResourceHints = () => {
    resourceHints.value.forEach(hint => {
      const existingHint = document.querySelector(`link[href="${hint.href}"]`)
      if (existingHint) return

      const link = document.createElement('link')
      Object.assign(link, hint)
      document.head.appendChild(link)
    })
  }

  /**
   * Monitora chunks não utilizados
   */
  const detectUnusedChunks = () => {
    const loadedChunks = Array.from(bundleStats.loadedChunks)
    const unusedChunks = bundleStats.chunks.filter(chunk => 
      !loadedChunks.includes(chunk.name) && 
      Date.now() - performance.timing.navigationStart > 10000 // 10 segundos após carregamento
    )

    if (unusedChunks.length > 0) {
      logger.warn('Unused chunks detected:', unusedChunks.map(c => c.name))
    }

    return unusedChunks
  }

  /**
   * Calcula score de otimização
   */
  const calculateOptimizationScore = () => {
    let score = 100

    // Penaliza chunks grandes
    const largeChunks = bundleStats.chunks.filter(chunk => chunk.size > chunkSizeThreshold)
    score -= largeChunks.length * 10

    // Penaliza chunks não utilizados
    const unusedChunks = detectUnusedChunks()
    score -= unusedChunks.length * 15

    // Penaliza baixa taxa de cache
    const cacheRate = bundleStats.cacheHits / (bundleStats.cacheHits + bundleStats.cacheMisses) * 100
    if (cacheRate < 50) score -= 20

    // Penaliza métricas de performance ruins
    if (performanceMetrics.firstContentfulPaint > 2000) score -= 15
    if (performanceMetrics.largestContentfulPaint > 4000) score -= 15
    if (performanceMetrics.cumulativeLayoutShift > 0.1) score -= 10

    return Math.max(0, score)
  }

  // Computed properties
  const totalChunks = computed(() => bundleStats.chunks.length)
  const loadedChunksCount = computed(() => bundleStats.loadedChunks.size)
  const failedChunksCount = computed(() => bundleStats.failedChunks.size)
  const averageLoadTime = computed(() => {
    const times = Array.from(bundleStats.loadTimes.values())
    return times.length > 0 ? times.reduce((a, b) => a + b, 0) / times.length : 0
  })

  const cacheHitRate = computed(() => {
    const total = bundleStats.cacheHits + bundleStats.cacheMisses
    return total > 0 ? (bundleStats.cacheHits / total) * 100 : 0
  })

  const optimizationScore = computed(() => calculateOptimizationScore())

  const recommendations = computed(() => {
    const recs = []

    if (bundleStats.chunks.some(chunk => chunk.size > chunkSizeThreshold)) {
      recs.push('Considere dividir chunks grandes em pedaços menores')
    }

    if (cacheHitRate.value < 50) {
      recs.push('Melhore a estratégia de cache para aumentar a taxa de acerto')
    }

    if (performanceMetrics.firstContentfulPaint > 2000) {
      recs.push('Otimize o First Contentful Paint carregando recursos críticos primeiro')
    }

    if (performanceMetrics.cumulativeLayoutShift > 0.1) {
      recs.push('Reduza o Cumulative Layout Shift definindo dimensões de elementos')
    }

    const unusedChunks = detectUnusedChunks()
    if (unusedChunks.length > 0) {
      recs.push(`Remova ou otimize ${unusedChunks.length} chunks não utilizados`)
    }

    return recs
  })

  // Métodos de inicialização
  const initializeOptimization = async () => {
    if (enableAnalytics) {
      analyzeLoadedChunks()
      analyzeWebVitals()
    }

    await nextTick()

    if (enableResourceHints) {
      optimizeResourceLoading()
      applyResourceHints()
    }

    // Preload chunks críticos
    if (enablePreloading && criticalResources.value.length > 0) {
      const criticalChunkNames = criticalResources.value.map(r => 
        r.url.split('/').pop().replace('.js', '')
      )
      await preloadCriticalChunks(criticalChunkNames)
    }

    // Prefetch chunks não críticos
    if (enablePrefetching && deferredResources.value.length > 0) {
      const deferredChunkNames = deferredResources.value.map(r => 
        r.url.split('/').pop().replace('.js', '')
      )
      prefetchNonCriticalChunks(deferredChunkNames)
    }
  }

  // Lifecycle
  onMounted(() => {
    initializeOptimization()
  })

  return {
    // Estados
    bundleStats,
    loadingState,
    performanceMetrics,
    resourceHints,
    criticalResources,
    deferredResources,

    // Computed
    totalChunks,
    loadedChunksCount,
    failedChunksCount,
    averageLoadTime,
    cacheHitRate,
    optimizationScore,
    recommendations,

    // Métodos
    loadChunk,
    preloadCriticalChunks,
    prefetchNonCriticalChunks,
    analyzeLoadedChunks,
    analyzeWebVitals,
    optimizeResourceLoading,
    applyResourceHints,
    detectUnusedChunks,
    calculateOptimizationScore,
    initializeOptimization
  }
}

/**
 * Composable para lazy loading inteligente
 */
export function useLazyLoading(options = {}) {
  const {
    rootMargin = '50px',
    threshold = 0.1,
    enablePreloading = true,
    preloadDistance = 2
  } = options

  const observer = ref(null)
  const observedElements = ref(new Map())
  const loadedElements = ref(new Set())

  const createObserver = () => {
    if (!window.IntersectionObserver) return null

    return new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target
          const callback = observedElements.value.get(element)
          
          if (callback && !loadedElements.value.has(element)) {
            callback(element)
            loadedElements.value.add(element)
            observer.value?.unobserve(element)
            observedElements.value.delete(element)
          }
        }
      })
    }, {
      rootMargin,
      threshold
    })
  }

  const observe = (element, callback) => {
    if (!observer.value) {
      observer.value = createObserver()
    }

    if (observer.value && element) {
      observedElements.value.set(element, callback)
      observer.value.observe(element)
    }
  }

  const unobserve = (element) => {
    if (observer.value && element) {
      observer.value.unobserve(element)
      observedElements.value.delete(element)
    }
  }

  const disconnect = () => {
    if (observer.value) {
      observer.value.disconnect()
      observedElements.value.clear()
      loadedElements.value.clear()
    }
  }

  return {
    observe,
    unobserve,
    disconnect,
    loadedElements: computed(() => loadedElements.value),
    observedCount: computed(() => observedElements.value.size)
  }
}

/**
 * Composable para code splitting dinâmico
 */
export function useCodeSplitting() {
  const loadedModules = ref(new Map())
  const loadingModules = ref(new Set())
  const failedModules = ref(new Set())

  const loadModule = async (moduleFactory, moduleName) => {
    if (loadedModules.value.has(moduleName)) {
      return loadedModules.value.get(moduleName)
    }

    if (loadingModules.value.has(moduleName)) {
      // Aguarda carregamento em andamento
      return new Promise((resolve, reject) => {
        const checkLoaded = () => {
          if (loadedModules.value.has(moduleName)) {
            resolve(loadedModules.value.get(moduleName))
          } else if (failedModules.value.has(moduleName)) {
            reject(new Error(`Failed to load module: ${moduleName}`))
          } else {
            setTimeout(checkLoaded, 100)
          }
        }
        checkLoaded()
      })
    }

    loadingModules.value.add(moduleName)

    try {
      const module = await moduleFactory()
      loadedModules.value.set(moduleName, module)
      return module
    } catch (error) {
      failedModules.value.add(moduleName)
      throw error
    } finally {
      loadingModules.value.delete(moduleName)
    }
  }

  const preloadModule = async (moduleFactory, moduleName) => {
    if (!loadedModules.value.has(moduleName) && !loadingModules.value.has(moduleName)) {
      try {
        await loadModule(moduleFactory, moduleName)
      } catch (error) {
        logger.warn(`Failed to preload module ${moduleName}:`, error)
      }
    }
  }

  const isModuleLoaded = (moduleName) => {
    return loadedModules.value.has(moduleName)
  }

  const isModuleLoading = (moduleName) => {
    return loadingModules.value.has(moduleName)
  }

  const isModuleFailed = (moduleName) => {
    return failedModules.value.has(moduleName)
  }

  return {
    loadedModules: computed(() => loadedModules.value),
    loadingModules: computed(() => loadingModules.value),
    failedModules: computed(() => failedModules.value),
    
    loadModule,
    preloadModule,
    isModuleLoaded,
    isModuleLoading,
    isModuleFailed
  }
}