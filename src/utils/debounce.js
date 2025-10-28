/**
import logger from '@/utils/logger'
 * Utilitário de debounce para otimizar performance
 * Evita execuções excessivas de funções em intervalos curtos
 */

/**
 * Cria uma função debounced que atrasa a execução até que tenham passado
 * `delay` milissegundos desde a última vez que foi invocada
 * @param {Function} func - Função a ser debounced
 * @param {number} delay - Delay em milissegundos
 * @param {boolean} immediate - Se true, executa na primeira chamada
 * @returns {Function} Função debounced
 */
export function debounce(func, delay, immediate = false) {
  let timeoutId
  let lastArgs
  let lastThis

  const debounced = function(...args) {
    lastArgs = args
    lastThis = this

    const callNow = immediate && !timeoutId

    clearTimeout(timeoutId)

    timeoutId = setTimeout(() => {
      timeoutId = null
      if (!immediate) {
        func.apply(lastThis, lastArgs)
      }
    }, delay)

    if (callNow) {
      func.apply(lastThis, lastArgs)
    }
  }

  // Método para cancelar execução pendente
  debounced.cancel = function() {
    clearTimeout(timeoutId)
    timeoutId = null
  }

  // Método para executar imediatamente
  debounced.flush = function() {
    if (timeoutId) {
      clearTimeout(timeoutId)
      func.apply(lastThis, lastArgs)
      timeoutId = null
    }
  }

  return debounced
}

/**
 * Cria uma função throttled que executa no máximo uma vez por período
 * @param {Function} func - Função a ser throttled
 * @param {number} limit - Limite em milissegundos
 * @returns {Function} Função throttled
 */
export function throttle(func, limit) {
  let inThrottle
  let lastFunc
  let lastRan

  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      lastRan = Date.now()
      inThrottle = true
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(() => {
        if ((Date.now() - lastRan) >= limit) {
          func.apply(this, args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }
}

/**
 * Cria um debounce específico para atualizações de dados
 * com configurações otimizadas para dashboards
 * @param {Function} updateFunction - Função de atualização
 * @param {Object} options - Opções de configuração
 * @returns {Function} Função debounced otimizada
 */
export function createDataUpdateDebounce(updateFunction, options = {}) {
  const {
    delay = 1000,
    maxWait = 5000,
    immediate = false,
    onError = console.error
  } = options

  let timeoutId
  let maxTimeoutId
  let lastArgs
  let lastThis

  const debouncedUpdate = function(...args) {
    lastArgs = args
    lastThis = this

    const callNow = immediate && !timeoutId

    // Limpar timeouts existentes
    clearTimeout(timeoutId)
    
    // Se não há maxTimeout ativo, criar um
    if (!maxTimeoutId) {
      maxTimeoutId = setTimeout(() => {
        clearTimeout(timeoutId)
        executeUpdate()
        maxTimeoutId = null
      }, maxWait)
    }

    timeoutId = setTimeout(() => {
      executeUpdate()
      clearTimeout(maxTimeoutId)
      maxTimeoutId = null
    }, delay)

    if (callNow) {
      executeUpdate()
    }
  }

  const executeUpdate = async () => {
    try {
      await updateFunction.apply(lastThis, lastArgs)
    } catch (error) {
      onError('Erro na atualização de dados:', error)
    }
  }

  debouncedUpdate.cancel = function() {
    clearTimeout(timeoutId)
    clearTimeout(maxTimeoutId)
    timeoutId = null
    maxTimeoutId = null
  }

  debouncedUpdate.flush = function() {
    if (timeoutId || maxTimeoutId) {
      clearTimeout(timeoutId)
      clearTimeout(maxTimeoutId)
      executeUpdate()
      timeoutId = null
      maxTimeoutId = null
    }
  }

  return debouncedUpdate
}

/**
 * Utilitário para agrupar múltiplas atualizações em uma única execução
 * @param {Function} batchFunction - Função que processa o lote
 * @param {number} delay - Delay para agrupar chamadas
 * @returns {Function} Função que aceita itens para o lote
 */
export function createBatchProcessor(batchFunction, delay = 100) {
  let batch = []
  let timeoutId

  return function(item) {
    batch.push(item)

    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => {
      if (batch.length > 0) {
        const currentBatch = [...batch]
        batch = []
        batchFunction(currentBatch)
      }
    }, delay)
  }
}