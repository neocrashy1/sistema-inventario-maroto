/**
 * Web Worker para processamento de dados pesados
 * Executa operações intensivas sem bloquear a UI principal
 */

// Cache para resultados de processamento
const cache = new Map()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutos

/**
 * Processa dados de máquinas para o dashboard
 * @param {Array} machines - Array de dados de máquinas
 * @param {Object} options - Opções de processamento
 * @returns {Object} Dados processados
 */
function processMachineData(machines, options = {}) {
  const {
    includeMetrics = true,
    includeAlerts = true,
    includePerformance = true,
    timeRange = '24h'
  } = options

  const startTime = performance.now()
  
  try {
    const result = {
      summary: {
        total: machines.length,
        online: 0,
        offline: 0,
        warning: 0,
        critical: 0
      },
      metrics: includeMetrics ? calculateMetrics(machines, timeRange) : null,
      alerts: includeAlerts ? processAlerts(machines) : null,
      performance: includePerformance ? calculatePerformance(machines) : null,
      processTime: 0
    }

    // Calcular status das máquinas
    machines.forEach(machine => {
      switch (machine.status?.toLowerCase()) {
        case 'online':
          result.summary.online++
          break
        case 'offline':
          result.summary.offline++
          break
        case 'warning':
          result.summary.warning++
          break
        case 'critical':
          result.summary.critical++
          break
      }
    })

    result.processTime = performance.now() - startTime
    return result

  } catch (error) {
    throw new Error(`Erro ao processar dados das máquinas: ${error.message}`)
  }
}

/**
 * Calcula métricas de performance das máquinas
 * @param {Array} machines - Array de máquinas
 * @param {String} timeRange - Período de análise
 * @returns {Object} Métricas calculadas
 */
function calculateMetrics(machines, timeRange) {
  const metrics = {
    cpu: { avg: 0, min: 100, max: 0, trend: [] },
    memory: { avg: 0, min: 100, max: 0, trend: [] },
    disk: { avg: 0, min: 100, max: 0, trend: [] },
    network: { avg: 0, min: 0, max: 0, trend: [] },
    uptime: { avg: 0, total: 0 }
  }

  if (machines.length === 0) return metrics

  let totalCpu = 0, totalMemory = 0, totalDisk = 0, totalNetwork = 0, totalUptime = 0
  const cpuTrend = [], memoryTrend = [], diskTrend = [], networkTrend = []

  machines.forEach(machine => {
    const { cpu, memory, disk, network, uptime } = machine.metrics || {}

    if (cpu !== undefined) {
      totalCpu += cpu
      metrics.cpu.min = Math.min(metrics.cpu.min, cpu)
      metrics.cpu.max = Math.max(metrics.cpu.max, cpu)
      cpuTrend.push(cpu)
    }

    if (memory !== undefined) {
      totalMemory += memory
      metrics.memory.min = Math.min(metrics.memory.min, memory)
      metrics.memory.max = Math.max(metrics.memory.max, memory)
      memoryTrend.push(memory)
    }

    if (disk !== undefined) {
      totalDisk += disk
      metrics.disk.min = Math.min(metrics.disk.min, disk)
      metrics.disk.max = Math.max(metrics.disk.max, disk)
      diskTrend.push(disk)
    }

    if (network !== undefined) {
      totalNetwork += network
      metrics.network.min = Math.min(metrics.network.min, network)
      metrics.network.max = Math.max(metrics.network.max, network)
      networkTrend.push(network)
    }

    if (uptime !== undefined) {
      totalUptime += uptime
    }
  })

  const count = machines.length
  metrics.cpu.avg = Math.round((totalCpu / count) * 100) / 100
  metrics.memory.avg = Math.round((totalMemory / count) * 100) / 100
  metrics.disk.avg = Math.round((totalDisk / count) * 100) / 100
  metrics.network.avg = Math.round((totalNetwork / count) * 100) / 100
  metrics.uptime.avg = Math.round((totalUptime / count) * 100) / 100
  metrics.uptime.total = totalUptime

  // Calcular tendências (últimos 10 pontos)
  metrics.cpu.trend = cpuTrend.slice(-10)
  metrics.memory.trend = memoryTrend.slice(-10)
  metrics.disk.trend = diskTrend.slice(-10)
  metrics.network.trend = networkTrend.slice(-10)

  return metrics
}

/**
 * Processa alertas das máquinas
 * @param {Array} machines - Array de máquinas
 * @returns {Object} Alertas processados
 */
function processAlerts(machines) {
  const alerts = {
    critical: [],
    warning: [],
    info: [],
    total: 0
  }

  machines.forEach(machine => {
    const machineAlerts = machine.alerts || []
    
    machineAlerts.forEach(alert => {
      const processedAlert = {
        id: alert.id || `${machine.id}-${Date.now()}`,
        machineId: machine.id,
        machineName: machine.name,
        type: alert.type,
        severity: alert.severity?.toLowerCase() || 'info',
        message: alert.message,
        timestamp: alert.timestamp || new Date().toISOString(),
        acknowledged: alert.acknowledged || false
      }

      switch (processedAlert.severity) {
        case 'critical':
          alerts.critical.push(processedAlert)
          break
        case 'warning':
          alerts.warning.push(processedAlert)
          break
        default:
          alerts.info.push(processedAlert)
      }

      alerts.total++
    })
  })

  // Ordenar por timestamp (mais recentes primeiro)
  const sortByTimestamp = (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  alerts.critical.sort(sortByTimestamp)
  alerts.warning.sort(sortByTimestamp)
  alerts.info.sort(sortByTimestamp)

  return alerts
}

/**
 * Calcula métricas de performance geral
 * @param {Array} machines - Array de máquinas
 * @returns {Object} Métricas de performance
 */
function calculatePerformance(machines) {
  const performance = {
    healthScore: 0,
    efficiency: 0,
    availability: 0,
    responseTime: 0,
    throughput: 0,
    errorRate: 0
  }

  if (machines.length === 0) return performance

  let totalHealth = 0, totalEfficiency = 0, totalAvailability = 0
  let totalResponseTime = 0, totalThroughput = 0, totalErrors = 0, totalRequests = 0

  machines.forEach(machine => {
    const metrics = machine.metrics || {}
    const stats = machine.stats || {}

    // Health Score (baseado em CPU, Memory, Disk)
    const cpu = metrics.cpu || 0
    const memory = metrics.memory || 0
    const disk = metrics.disk || 0
    const health = 100 - ((cpu + memory + disk) / 3)
    totalHealth += Math.max(0, health)

    // Efficiency (baseado em uptime e performance)
    const uptime = metrics.uptime || 0
    const efficiency = (uptime / 100) * (health / 100) * 100
    totalEfficiency += efficiency

    // Availability
    const availability = stats.availability || uptime
    totalAvailability += availability

    // Response Time
    const responseTime = stats.responseTime || 0
    totalResponseTime += responseTime

    // Throughput
    const throughput = stats.throughput || 0
    totalThroughput += throughput

    // Error Rate
    const errors = stats.errors || 0
    const requests = stats.requests || 1
    totalErrors += errors
    totalRequests += requests
  })

  const count = machines.length
  performance.healthScore = Math.round((totalHealth / count) * 100) / 100
  performance.efficiency = Math.round((totalEfficiency / count) * 100) / 100
  performance.availability = Math.round((totalAvailability / count) * 100) / 100
  performance.responseTime = Math.round((totalResponseTime / count) * 100) / 100
  performance.throughput = Math.round((totalThroughput / count) * 100) / 100
  performance.errorRate = totalRequests > 0 ? 
    Math.round((totalErrors / totalRequests) * 10000) / 100 : 0

  return performance
}

/**
 * Processa dados para gráficos
 * @param {Array} data - Dados brutos
 * @param {Object} config - Configuração do gráfico
 * @returns {Object} Dados formatados para gráfico
 */
function processChartData(data, config) {
  const { type, timeRange, aggregation, metrics } = config
  
  try {
    switch (type) {
      case 'line':
        return processLineChartData(data, config)
      case 'bar':
        return processBarChartData(data, config)
      case 'pie':
        return processPieChartData(data, config)
      case 'area':
        return processAreaChartData(data, config)
      default:
        throw new Error(`Tipo de gráfico não suportado: ${type}`)
    }
  } catch (error) {
    throw new Error(`Erro ao processar dados do gráfico: ${error.message}`)
  }
}

/**
 * Processa dados para gráfico de linha
 */
function processLineChartData(data, config) {
  const { metrics, timeRange, aggregation = 'avg' } = config
  const result = {
    labels: [],
    datasets: []
  }

  // Agrupar dados por tempo
  const timeGroups = groupDataByTime(data, timeRange)
  result.labels = Object.keys(timeGroups).sort()

  // Processar cada métrica
  metrics.forEach(metric => {
    const dataset = {
      label: metric.label || metric.key,
      data: [],
      borderColor: metric.color || '#3b82f6',
      backgroundColor: metric.backgroundColor || 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }

    result.labels.forEach(timeLabel => {
      const timeData = timeGroups[timeLabel]
      const values = timeData.map(item => item[metric.key]).filter(v => v !== undefined)
      
      let aggregatedValue = 0
      if (values.length > 0) {
        switch (aggregation) {
          case 'avg':
            aggregatedValue = values.reduce((sum, val) => sum + val, 0) / values.length
            break
          case 'sum':
            aggregatedValue = values.reduce((sum, val) => sum + val, 0)
            break
          case 'max':
            aggregatedValue = Math.max(...values)
            break
          case 'min':
            aggregatedValue = Math.min(...values)
            break
        }
      }
      
      dataset.data.push(Math.round(aggregatedValue * 100) / 100)
    })

    result.datasets.push(dataset)
  })

  return result
}

/**
 * Processa dados para gráfico de barras
 */
function processBarChartData(data, config) {
  const { metrics, groupBy } = config
  const result = {
    labels: [],
    datasets: []
  }

  // Agrupar dados
  const groups = groupDataBy(data, groupBy)
  result.labels = Object.keys(groups)

  // Processar cada métrica
  metrics.forEach(metric => {
    const dataset = {
      label: metric.label || metric.key,
      data: [],
      backgroundColor: metric.color || '#3b82f6',
      borderColor: metric.borderColor || '#1d4ed8',
      borderWidth: 1
    }

    result.labels.forEach(label => {
      const groupData = groups[label]
      const values = groupData.map(item => item[metric.key]).filter(v => v !== undefined)
      const avg = values.length > 0 ? values.reduce((sum, val) => sum + val, 0) / values.length : 0
      dataset.data.push(Math.round(avg * 100) / 100)
    })

    result.datasets.push(dataset)
  })

  return result
}

/**
 * Processa dados para gráfico de pizza
 */
function processPieChartData(data, config) {
  const { groupBy, metric } = config
  const groups = groupDataBy(data, groupBy)
  
  const result = {
    labels: Object.keys(groups),
    datasets: [{
      data: [],
      backgroundColor: [
        '#ef4444', '#f97316', '#eab308', '#22c55e', 
        '#3b82f6', '#8b5cf6', '#ec4899', '#6b7280'
      ]
    }]
  }

  result.labels.forEach(label => {
    const groupData = groups[label]
    if (metric) {
      const values = groupData.map(item => item[metric]).filter(v => v !== undefined)
      const sum = values.reduce((sum, val) => sum + val, 0)
      result.datasets[0].data.push(sum)
    } else {
      result.datasets[0].data.push(groupData.length)
    }
  })

  return result
}

/**
 * Processa dados para gráfico de área
 */
function processAreaChartData(data, config) {
  const lineData = processLineChartData(data, config)
  
  // Adicionar configurações específicas para área
  lineData.datasets.forEach(dataset => {
    dataset.fill = true
    dataset.backgroundColor = dataset.backgroundColor || 'rgba(59, 130, 246, 0.2)'
  })

  return lineData
}

/**
 * Agrupa dados por tempo
 */
function groupDataByTime(data, timeRange) {
  const groups = {}
  const now = new Date()
  
  data.forEach(item => {
    const timestamp = new Date(item.timestamp || item.createdAt || now)
    let timeKey
    
    switch (timeRange) {
      case '1h':
        timeKey = `${timestamp.getHours()}:${timestamp.getMinutes().toString().padStart(2, '0')}`
        break
      case '24h':
        timeKey = `${timestamp.getHours()}:00`
        break
      case '7d':
        timeKey = timestamp.toLocaleDateString('pt-BR', { weekday: 'short' })
        break
      case '30d':
        timeKey = timestamp.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
        break
      default:
        timeKey = timestamp.toISOString().split('T')[0]
    }
    
    if (!groups[timeKey]) {
      groups[timeKey] = []
    }
    groups[timeKey].push(item)
  })
  
  return groups
}

/**
 * Agrupa dados por campo específico
 */
function groupDataBy(data, field) {
  const groups = {}
  
  data.forEach(item => {
    const key = item[field] || 'Outros'
    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(item)
  })
  
  return groups
}

/**
 * Gera chave de cache
 */
function getCacheKey(operation, data, options) {
  const dataHash = JSON.stringify(data).slice(0, 100) // Primeiros 100 chars como hash simples
  const optionsHash = JSON.stringify(options)
  return `${operation}-${dataHash}-${optionsHash}`
}

/**
 * Limpa cache expirado
 */
function cleanExpiredCache() {
  const now = Date.now()
  for (const [key, entry] of cache.entries()) {
    if (now - entry.timestamp > CACHE_TTL) {
      cache.delete(key)
    }
  }
}

// Limpar cache a cada 5 minutos
setInterval(cleanExpiredCache, 5 * 60 * 1000)

// Event listener para mensagens do thread principal
self.addEventListener('message', async (event) => {
  const { id, operation, data, options = {} } = event.data
  
  try {
    // Verificar cache primeiro
    const cacheKey = getCacheKey(operation, data, options)
    if (cache.has(cacheKey) && !options.skipCache) {
      const cached = cache.get(cacheKey)
      if (Date.now() - cached.timestamp < CACHE_TTL) {
        self.postMessage({
          id,
          success: true,
          result: cached.result,
          fromCache: true
        })
        return
      }
    }

    let result
    const startTime = performance.now()

    switch (operation) {
      case 'processMachineData':
        result = processMachineData(data, options)
        break
      
      case 'processChartData':
        result = processChartData(data, options)
        break
      
      case 'calculateMetrics':
        result = calculateMetrics(data, options.timeRange)
        break
      
      case 'processAlerts':
        result = processAlerts(data)
        break
      
      case 'calculatePerformance':
        result = calculatePerformance(data)
        break
      
      default:
        throw new Error(`Operação não suportada: ${operation}`)
    }

    const processingTime = performance.now() - startTime

    // Armazenar no cache
    cache.set(cacheKey, {
      result,
      timestamp: Date.now()
    })

    // Enviar resultado
    self.postMessage({
      id,
      success: true,
      result,
      processingTime,
      fromCache: false
    })

  } catch (error) {
    self.postMessage({
      id,
      success: false,
      error: error.message,
      stack: error.stack
    })
  }
})

// Enviar mensagem de inicialização
self.postMessage({
  type: 'ready',
  message: 'Data processor worker initialized'
})