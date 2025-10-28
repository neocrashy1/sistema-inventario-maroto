import { ref, computed, watch, unref, isRef, onUnmounted } from 'vue'

/**
 * Composable para otimizar computed properties com cache e invalidação inteligente
 */
export function useOptimizedComputed() {
  const cache = new Map()
  const watchers = new Set()
  const timers = new Map()

  /**
   * Cria um computed property com cache personalizado
   * @param {Function} getter - Função getter do computed
   * @param {Object} options - Opções de configuração
   * @returns {ComputedRef} Computed property otimizado
   */
  const cachedComputed = (getter, options = {}) => {
    const {
      cacheKey = Symbol('computed'),
      ttl = 0, // Time to live em ms (0 = sem expiração)
      dependencies = [], // Array de refs para invalidar cache
      debounce = 0 // Debounce em ms
    } = options

    let lastComputedTime = 0
    let debouncedGetter = getter

    // Aplicar debounce se especificado
    if (debounce > 0) {
      debouncedGetter = debounceFunction(getter, debounce)
    }

    const computedRef = computed(() => {
      const now = Date.now()
      
      // Verificar se o cache ainda é válido
      if (cache.has(cacheKey)) {
        const cached = cache.get(cacheKey)
        if (ttl === 0 || (now - cached.timestamp) < ttl) {
          return cached.value
        }
      }

      // Calcular novo valor
      const value = debouncedGetter()
      
      // Armazenar no cache
      cache.set(cacheKey, {
        value,
        timestamp: now
      })
      
      lastComputedTime = now
      return value
    })

    // Configurar watchers para invalidar cache quando dependências mudarem
    dependencies.forEach(dep => {
      if (isRef(dep)) {
        const stopWatcher = watch(dep, () => {
          cache.delete(cacheKey)
        }, { flush: 'sync' })
        watchers.add(stopWatcher)
      }
    })

    return computedRef
  }

  /**
   * Cria um watcher otimizado com debounce e throttle
   * @param {WatchSource} source - Fonte para observar
   * @param {Function} callback - Callback do watcher
   * @param {Object} options - Opções do watcher
   * @returns {Function} Função para parar o watcher
   */
  const optimizedWatch = (source, callback, options = {}) => {
    const {
      debounce = 0,
      throttle = 0,
      immediate = false,
      deep = false,
      flush = 'pre',
      maxWait = 0 // Máximo tempo de espera para debounce
    } = options

    let optimizedCallback = callback

    // Aplicar debounce
    if (debounce > 0) {
      optimizedCallback = debounceFunction(callback, debounce, { maxWait })
    }
    // Aplicar throttle
    else if (throttle > 0) {
      optimizedCallback = throttleFunction(callback, throttle)
    }

    const stopWatcher = watch(
      source,
      optimizedCallback,
      { immediate, deep, flush }
    )

    watchers.add(stopWatcher)
    return stopWatcher
  }

  /**
   * Cria um computed property que só recalcula quando valores específicos mudam
   * @param {Function} getter - Função getter
   * @param {Array} deps - Array de dependências
   * @param {Function} compareFn - Função de comparação customizada
   * @returns {ComputedRef} Computed property otimizado
   */
  const memoizedComputed = (getter, deps = [], compareFn = Object.is) => {
    const lastDeps = ref([])
    const lastResult = ref()
    let hasResult = false

    return computed(() => {
      const currentDeps = deps.map(dep => unref(dep))
      
      // Verificar se as dependências mudaram
      const depsChanged = !hasResult || 
        currentDeps.length !== lastDeps.value.length ||
        currentDeps.some((dep, index) => !compareFn(dep, lastDeps.value[index]))

      if (depsChanged) {
        lastResult.value = getter()
        lastDeps.value = currentDeps
        hasResult = true
      }

      return lastResult.value
    })
  }

  /**
   * Cria um computed property que agrupa múltiplas operações
   * @param {Object} computedMap - Mapa de computed properties
   * @returns {ComputedRef} Computed property agrupado
   */
  const batchedComputed = (computedMap) => {
    return computed(() => {
      const result = {}
      
      // Executar todos os computeds em batch
      Object.keys(computedMap).forEach(key => {
        result[key] = computedMap[key]()
      })
      
      return result
    })
  }

  /**
   * Cria um watcher que executa callbacks em lote
   * @param {Array} sources - Array de fontes para observar
   * @param {Function} callback - Callback que recebe todas as mudanças
   * @param {Object} options - Opções do watcher
   * @returns {Function} Função para parar todos os watchers
   */
  const batchedWatch = (sources, callback, options = {}) => {
    const { batchDelay = 0 } = options
    const changes = new Map()
    let batchTimer = null

    const processBatch = () => {
      if (changes.size > 0) {
        const batchedChanges = Array.from(changes.entries()).map(([source, change]) => ({
          source,
          ...change
        }))
        
        callback(batchedChanges)
        changes.clear()
      }
      batchTimer = null
    }

    const stopWatchers = sources.map((source, index) => {
      return watch(source, (newVal, oldVal) => {
        changes.set(index, { newVal, oldVal })
        
        if (batchDelay > 0) {
          if (batchTimer) {
            clearTimeout(batchTimer)
          }
          batchTimer = setTimeout(processBatch, batchDelay)
        } else {
          // Processar no próximo tick
          nextTick(processBatch)
        }
      }, options)
    })

    watchers.add(() => {
      stopWatchers.forEach(stop => stop())
      if (batchTimer) {
        clearTimeout(batchTimer)
      }
    })

    return () => {
      stopWatchers.forEach(stop => stop())
      if (batchTimer) {
        clearTimeout(batchTimer)
      }
    }
  }

  /**
   * Limpa o cache de computed properties
   * @param {Symbol|String} cacheKey - Chave específica ou 'all' para limpar tudo
   */
  const clearCache = (cacheKey = 'all') => {
    if (cacheKey === 'all') {
      cache.clear()
    } else {
      cache.delete(cacheKey)
    }
  }

  /**
   * Limpa caches expirados
   */
  const clearExpiredCache = () => {
    const now = Date.now()
    
    for (const [key, cached] of cache.entries()) {
      if (cached.ttl && (now - cached.timestamp) >= cached.ttl) {
        cache.delete(key)
      }
    }
  }

  /**
   * Obtém estatísticas do cache
   * @returns {Object} Estatísticas do cache
   */
  const getCacheStats = () => {
    const stats = {
      size: cache.size,
      entries: [],
      totalMemory: 0
    }

    for (const [key, cached] of cache.entries()) {
      const entry = {
        key: key.toString(),
        timestamp: cached.timestamp,
        age: Date.now() - cached.timestamp,
        size: JSON.stringify(cached.value).length
      }
      
      stats.entries.push(entry)
      stats.totalMemory += entry.size
    }

    return stats
  }

  // Cleanup automático
  const cleanupInterval = setInterval(clearExpiredCache, 60000) // A cada minuto

  // Cleanup ao desmontar
  onUnmounted(() => {
    // Parar todos os watchers
    watchers.forEach(stopWatcher => {
      if (typeof stopWatcher === 'function') {
        stopWatcher()
      }
    })
    watchers.clear()

    // Limpar todos os timers
    timers.forEach(timer => clearTimeout(timer))
    timers.clear()

    // Limpar cache
    cache.clear()

    // Limpar interval de cleanup
    clearInterval(cleanupInterval)
  })

  return {
    cachedComputed,
    optimizedWatch,
    memoizedComputed,
    batchedComputed,
    batchedWatch,
    clearCache,
    clearExpiredCache,
    getCacheStats
  }
}

/**
 * Função de debounce otimizada
 * @param {Function} func - Função para aplicar debounce
 * @param {Number} wait - Tempo de espera em ms
 * @param {Object} options - Opções adicionais
 * @returns {Function} Função com debounce aplicado
 */
function debounceFunction(func, wait, options = {}) {
  const { maxWait = 0, leading = false, trailing = true } = options
  
  let timeoutId
  let maxTimeoutId
  let lastCallTime
  let lastInvokeTime = 0
  let lastArgs
  let lastThis
  let result

  function invokeFunc(time) {
    const args = lastArgs
    const thisArg = lastThis

    lastArgs = lastThis = undefined
    lastInvokeTime = time
    result = func.apply(thisArg, args)
    return result
  }

  function leadingEdge(time) {
    lastInvokeTime = time
    timeoutId = setTimeout(timerExpired, wait)
    return leading ? invokeFunc(time) : result
  }

  function remainingWait(time) {
    const timeSinceLastCall = time - lastCallTime
    const timeSinceLastInvoke = time - lastInvokeTime
    const timeWaiting = wait - timeSinceLastCall

    return maxWait
      ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
      : timeWaiting
  }

  function shouldInvoke(time) {
    const timeSinceLastCall = time - lastCallTime
    const timeSinceLastInvoke = time - lastInvokeTime

    return (lastCallTime === undefined || (timeSinceLastCall >= wait) ||
            (timeSinceLastCall < 0) || (maxWait && timeSinceLastInvoke >= maxWait))
  }

  function timerExpired() {
    const time = Date.now()
    if (shouldInvoke(time)) {
      return trailingEdge(time)
    }
    timeoutId = setTimeout(timerExpired, remainingWait(time))
  }

  function trailingEdge(time) {
    timeoutId = undefined

    if (trailing && lastArgs) {
      return invokeFunc(time)
    }
    lastArgs = lastThis = undefined
    return result
  }

  function cancel() {
    if (timeoutId !== undefined) {
      clearTimeout(timeoutId)
    }
    if (maxTimeoutId !== undefined) {
      clearTimeout(maxTimeoutId)
    }
    lastInvokeTime = 0
    lastArgs = lastCallTime = lastThis = timeoutId = maxTimeoutId = undefined
  }

  function flush() {
    return timeoutId === undefined ? result : trailingEdge(Date.now())
  }

  function debounced(...args) {
    const time = Date.now()
    const isInvoking = shouldInvoke(time)

    lastArgs = args
    lastThis = this
    lastCallTime = time

    if (isInvoking) {
      if (timeoutId === undefined) {
        return leadingEdge(lastCallTime)
      }
      if (maxWait) {
        timeoutId = setTimeout(timerExpired, wait)
        return invokeFunc(lastCallTime)
      }
    }
    if (timeoutId === undefined) {
      timeoutId = setTimeout(timerExpired, wait)
    }
    return result
  }

  debounced.cancel = cancel
  debounced.flush = flush
  return debounced
}

/**
 * Função de throttle otimizada
 * @param {Function} func - Função para aplicar throttle
 * @param {Number} wait - Tempo de espera em ms
 * @param {Object} options - Opções adicionais
 * @returns {Function} Função com throttle aplicado
 */
function throttleFunction(func, wait, options = {}) {
  const { leading = true, trailing = true } = options
  return debounceFunction(func, wait, {
    leading,
    trailing,
    maxWait: wait
  })
}

/**
 * Hook para otimizar re-renderizações de listas
 * @param {Array} items - Array de itens
 * @param {Function} keyFn - Função para extrair chave única
 * @param {Function} compareFn - Função de comparação customizada
 * @returns {Object} Objeto com itens otimizados e métodos de controle
 */
export function useOptimizedList(items, keyFn = (item, index) => index, compareFn = Object.is) {
  const { memoizedComputed, optimizedWatch } = useOptimizedComputed()
  
  const itemsMap = ref(new Map())
  const lastKeys = ref(new Set())

  const optimizedItems = memoizedComputed(() => {
    const newMap = new Map()
    const newKeys = new Set()
    
    items.value.forEach((item, index) => {
      const key = keyFn(item, index)
      newKeys.add(key)
      
      // Reutilizar item existente se não mudou
      if (itemsMap.value.has(key)) {
        const existing = itemsMap.value.get(key)
        if (compareFn(existing.item, item)) {
          newMap.set(key, existing)
          return
        }
      }
      
      // Criar novo item
      newMap.set(key, {
        key,
        item,
        index,
        timestamp: Date.now()
      })
    })
    
    itemsMap.value = newMap
    lastKeys.value = newKeys
    
    return Array.from(newMap.values())
  }, [items])

  const addedItems = computed(() => {
    const added = []
    for (const key of lastKeys.value) {
      if (!itemsMap.value.has(key)) {
        added.push(key)
      }
    }
    return added
  })

  const removedItems = computed(() => {
    const removed = []
    for (const key of itemsMap.value.keys()) {
      if (!lastKeys.value.has(key)) {
        removed.push(key)
      }
    }
    return removed
  })

  return {
    optimizedItems,
    addedItems,
    removedItems,
    itemsMap: readonly(itemsMap)
  }
}