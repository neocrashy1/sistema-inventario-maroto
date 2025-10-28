import logger from '@/utils/logger'
import { ref, onUnmounted, computed } from 'vue'

/**
 * Composable para gerenciar Web Workers de forma eficiente
 */
export function useWebWorker() {
  const workers = ref(new Map())
  const activeJobs = ref(new Map())
  const workerPool = ref(new Map())
  const maxWorkers = ref(navigator.hardwareConcurrency || 4)
  
  // Estados reativos
  const isProcessing = computed(() => activeJobs.value.size > 0)
  const processingCount = computed(() => activeJobs.value.size)
  const availableWorkers = computed(() => {
    let available = 0
    for (const pool of workerPool.value.values()) {
      available += pool.available.length
    }
    return available
  })

  /**
   * Cria um pool de workers para um tipo específico
   * @param {String} workerType - Tipo do worker
   * @param {String} workerScript - Caminho do script do worker
   * @param {Number} poolSize - Tamanho do pool
   * @returns {Promise} Promise que resolve quando o pool estiver pronto
   */
  const createWorkerPool = async (workerType, workerScript, poolSize = 2) => {
    if (workerPool.value.has(workerType)) {
      return workerPool.value.get(workerType)
    }

    const pool = {
      script: workerScript,
      available: [],
      busy: [],
      total: poolSize,
      messageId: 0
    }

    // Criar workers
    for (let i = 0; i < poolSize; i++) {
      try {
        const worker = new Worker(workerScript, { type: 'module' })
        
        // Configurar worker
        worker.onmessage = (event) => handleWorkerMessage(workerType, worker, event)
        worker.onerror = (error) => handleWorkerError(workerType, worker, error)
        
        // Aguardar inicialização
        await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            reject(new Error('Worker initialization timeout'))
          }, 5000)

          const onReady = (event) => {
            if (event.data.type === 'ready') {
              clearTimeout(timeout)
              worker.removeEventListener('message', onReady)
              resolve()
            }
          }

          worker.addEventListener('message', onReady)
        })

        pool.available.push(worker)
      } catch (error) {
        logger.error(`Erro ao criar worker ${workerType}:`, error)
        throw error
      }
    }

    workerPool.value.set(workerType, pool)
    return pool
  }

  /**
   * Obtém um worker disponível do pool
   * @param {String} workerType - Tipo do worker
   * @returns {Worker|null} Worker disponível ou null
   */
  const getAvailableWorker = (workerType) => {
    const pool = workerPool.value.get(workerType)
    if (!pool || pool.available.length === 0) {
      return null
    }

    const worker = pool.available.pop()
    pool.busy.push(worker)
    return worker
  }

  /**
   * Retorna um worker para o pool
   * @param {String} workerType - Tipo do worker
   * @param {Worker} worker - Worker para retornar
   */
  const returnWorkerToPool = (workerType, worker) => {
    const pool = workerPool.value.get(workerType)
    if (!pool) return

    const busyIndex = pool.busy.indexOf(worker)
    if (busyIndex !== -1) {
      pool.busy.splice(busyIndex, 1)
      pool.available.push(worker)
    }
  }

  /**
   * Executa uma operação em um Web Worker
   * @param {String} workerType - Tipo do worker
   * @param {String} operation - Operação a executar
   * @param {*} data - Dados para processar
   * @param {Object} options - Opções adicionais
   * @returns {Promise} Promise com o resultado
   */
  const executeInWorker = async (workerType, operation, data, options = {}) => {
    const pool = workerPool.value.get(workerType)
    if (!pool) {
      throw new Error(`Pool de workers '${workerType}' não encontrado`)
    }

    // Aguardar worker disponível
    const worker = await waitForAvailableWorker(workerType, options.timeout || 10000)
    
    const messageId = `${workerType}-${++pool.messageId}-${Date.now()}`
    
    return new Promise((resolve, reject) => {
      const job = {
        id: messageId,
        workerType,
        worker,
        operation,
        startTime: Date.now(),
        resolve,
        reject,
        timeout: null
      }

      // Configurar timeout
      if (options.timeout) {
        job.timeout = setTimeout(() => {
          activeJobs.value.delete(messageId)
          returnWorkerToPool(workerType, worker)
          reject(new Error(`Timeout na operação ${operation} após ${options.timeout}ms`))
        }, options.timeout)
      }

      activeJobs.value.set(messageId, job)

      // Enviar mensagem para o worker
      worker.postMessage({
        id: messageId,
        operation,
        data,
        options
      })
    })
  }

  /**
   * Aguarda um worker disponível
   * @param {String} workerType - Tipo do worker
   * @param {Number} timeout - Timeout em ms
   * @returns {Promise<Worker>} Worker disponível
   */
  const waitForAvailableWorker = (workerType, timeout = 10000) => {
    return new Promise((resolve, reject) => {
      const checkAvailable = () => {
        const worker = getAvailableWorker(workerType)
        if (worker) {
          resolve(worker)
          return
        }

        // Aguardar um pouco e tentar novamente
        setTimeout(checkAvailable, 100)
      }

      // Configurar timeout
      const timeoutId = setTimeout(() => {
        reject(new Error(`Timeout aguardando worker ${workerType} após ${timeout}ms`))
      }, timeout)

      checkAvailable()
      
      // Limpar timeout quando resolver
      const originalResolve = resolve
      resolve = (worker) => {
        clearTimeout(timeoutId)
        originalResolve(worker)
      }
    })
  }

  /**
   * Manipula mensagens dos workers
   * @param {String} workerType - Tipo do worker
   * @param {Worker} worker - Worker que enviou a mensagem
   * @param {MessageEvent} event - Evento da mensagem
   */
  const handleWorkerMessage = (workerType, worker, event) => {
    const { id, success, result, error, fromCache, processingTime } = event.data
    
    // Ignorar mensagens de inicialização
    if (event.data.type === 'ready') {
      return
    }

    const job = activeJobs.value.get(id)
    if (!job) {
      logger.warn(`Job ${id} não encontrado`)
      return
    }

    // Limpar timeout
    if (job.timeout) {
      clearTimeout(job.timeout)
    }

    // Remover job ativo
    activeJobs.value.delete(id)
    
    // Retornar worker ao pool
    returnWorkerToPool(workerType, worker)

    // Resolver ou rejeitar a Promise
    if (success) {
      job.resolve({
        result,
        fromCache: fromCache || false,
        processingTime: processingTime || 0,
        totalTime: Date.now() - job.startTime
      })
    } else {
      job.reject(new Error(error || 'Erro desconhecido no worker'))
    }
  }

  /**
   * Manipula erros dos workers
   * @param {String} workerType - Tipo do worker
   * @param {Worker} worker - Worker que gerou o erro
   * @param {ErrorEvent} error - Evento de erro
   */
  const handleWorkerError = (workerType, worker, error) => {
    logger.error(`Erro no worker ${workerType}:`, error)
    
    // Encontrar jobs ativos deste worker
    const jobsToReject = []
    for (const [id, job] of activeJobs.value.entries()) {
      if (job.worker === worker) {
        jobsToReject.push({ id, job })
      }
    }

    // Rejeitar jobs ativos
    jobsToReject.forEach(({ id, job }) => {
      activeJobs.value.delete(id)
      if (job.timeout) {
        clearTimeout(job.timeout)
      }
      job.reject(new Error(`Worker error: ${error.message}`))
    })

    // Remover worker do pool e criar um novo
    const pool = workerPool.value.get(workerType)
    if (pool) {
      // Remover das listas
      const availableIndex = pool.available.indexOf(worker)
      const busyIndex = pool.busy.indexOf(worker)
      
      if (availableIndex !== -1) {
        pool.available.splice(availableIndex, 1)
      }
      if (busyIndex !== -1) {
        pool.busy.splice(busyIndex, 1)
      }

      // Terminar worker com erro
      worker.terminate()

      // Criar novo worker para substituir
      try {
        const newWorker = new Worker(pool.script, { type: 'module' })
        newWorker.onmessage = (event) => handleWorkerMessage(workerType, newWorker, event)
        newWorker.onerror = (error) => handleWorkerError(workerType, newWorker, error)
        pool.available.push(newWorker)
      } catch (createError) {
        logger.error(`Erro ao criar worker substituto:`, createError)
      }
    }
  }

  /**
   * Cancela um job ativo
   * @param {String} jobId - ID do job
   * @returns {Boolean} True se cancelado com sucesso
   */
  const cancelJob = (jobId) => {
    const job = activeJobs.value.get(jobId)
    if (!job) {
      return false
    }

    // Limpar timeout
    if (job.timeout) {
      clearTimeout(job.timeout)
    }

    // Remover job
    activeJobs.value.delete(jobId)
    
    // Retornar worker ao pool
    returnWorkerToPool(job.workerType, job.worker)
    
    // Rejeitar Promise
    job.reject(new Error('Job cancelado'))
    
    return true
  }

  /**
   * Cancela todos os jobs ativos
   */
  const cancelAllJobs = () => {
    const jobIds = Array.from(activeJobs.value.keys())
    jobIds.forEach(cancelJob)
  }

  /**
   * Obtém estatísticas dos workers
   * @returns {Object} Estatísticas
   */
  const getWorkerStats = () => {
    const stats = {
      pools: {},
      activeJobs: activeJobs.value.size,
      totalWorkers: 0,
      availableWorkers: 0,
      busyWorkers: 0
    }

    for (const [type, pool] of workerPool.value.entries()) {
      stats.pools[type] = {
        total: pool.total,
        available: pool.available.length,
        busy: pool.busy.length
      }
      
      stats.totalWorkers += pool.total
      stats.availableWorkers += pool.available.length
      stats.busyWorkers += pool.busy.length
    }

    return stats
  }

  /**
   * Termina todos os workers e limpa recursos
   */
  const cleanup = () => {
    // Cancelar jobs ativos
    cancelAllJobs()

    // Terminar todos os workers
    for (const pool of workerPool.value.values()) {
      [...pool.available, ...pool.busy].forEach(worker => {
        worker.terminate()
      })
    }

    // Limpar pools
    workerPool.value.clear()
    workers.value.clear()
  }

  // Cleanup automático ao desmontar
  onUnmounted(() => {
    cleanup()
  })

  return {
    // Estados reativos
    isProcessing,
    processingCount,
    availableWorkers,
    
    // Métodos principais
    createWorkerPool,
    executeInWorker,
    
    // Controle de jobs
    cancelJob,
    cancelAllJobs,
    
    // Utilitários
    getWorkerStats,
    cleanup
  }
}

/**
 * Composable específico para processamento de dados
 */
export function useDataProcessor() {
  const { createWorkerPool, executeInWorker, ...workerMethods } = useWebWorker()
  
  // Inicializar pool de workers de dados
  const initializeDataProcessor = async () => {
    try {
      await createWorkerPool(
        'dataProcessor', 
        '/src/workers/dataProcessor.worker.js',
        Math.min(navigator.hardwareConcurrency || 2, 4)
      )
    } catch (error) {
      logger.error('Erro ao inicializar processador de dados:', error)
      throw error
    }
  }

  /**
   * Processa dados de máquinas
   * @param {Array} machines - Array de máquinas
   * @param {Object} options - Opções de processamento
   * @returns {Promise} Dados processados
   */
  const processMachineData = (machines, options = {}) => {
    return executeInWorker('dataProcessor', 'processMachineData', machines, options)
  }

  /**
   * Processa dados para gráficos
   * @param {Array} data - Dados brutos
   * @param {Object} config - Configuração do gráfico
   * @returns {Promise} Dados formatados
   */
  const processChartData = (data, config) => {
    return executeInWorker('dataProcessor', 'processChartData', data, config)
  }

  /**
   * Calcula métricas de performance
   * @param {Array} machines - Array de máquinas
   * @param {String} timeRange - Período de análise
   * @returns {Promise} Métricas calculadas
   */
  const calculateMetrics = (machines, timeRange = '24h') => {
    return executeInWorker('dataProcessor', 'calculateMetrics', machines, { timeRange })
  }

  /**
   * Processa alertas
   * @param {Array} machines - Array de máquinas
   * @returns {Promise} Alertas processados
   */
  const processAlerts = (machines) => {
    return executeInWorker('dataProcessor', 'processAlerts', machines)
  }

  /**
   * Calcula performance geral
   * @param {Array} machines - Array de máquinas
   * @returns {Promise} Métricas de performance
   */
  const calculatePerformance = (machines) => {
    return executeInWorker('dataProcessor', 'calculatePerformance', machines)
  }

  return {
    // Inicialização
    initializeDataProcessor,
    
    // Métodos de processamento
    processMachineData,
    processChartData,
    calculateMetrics,
    processAlerts,
    calculatePerformance,
    
    // Métodos herdados do useWebWorker
    ...workerMethods
  }
}