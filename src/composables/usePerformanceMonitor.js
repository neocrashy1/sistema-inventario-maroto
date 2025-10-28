import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

/**
 * Composable para monitoramento de performance em tempo real
 */
export function usePerformanceMonitor(options = {}) {
  const {
    enableFPSMonitoring = true,
    enableMemoryMonitoring = true,
    enableNetworkMonitoring = true,
    enableRenderMonitoring = true,
    sampleInterval = 1000, // 1 segundo
    maxSamples = 60, // Manter 60 amostras (1 minuto)
    thresholds = {
      fps: { warning: 30, critical: 15 },
      memory: { warning: 50, critical: 80 }, // MB
      renderTime: { warning: 16, critical: 33 } // ms
    }
  } = options

  // Estados reativos
  const isMonitoring = ref(false)
  const currentMetrics = ref({
    fps: 0,
    memory: { used: 0, total: 0, percentage: 0 },
    renderTime: 0,
    networkLatency: 0,
    domNodes: 0,
    timestamp: Date.now()
  })

  const metricsHistory = ref([])
  const alerts = ref([])
  const performanceScore = ref(100)

  // Variáveis internas
  let frameCount = 0
  let lastFrameTime = 0
  let animationFrameId = null
  let monitoringInterval = null
  let renderStartTime = 0
  let observer = null

  // Computed properties
  const averageMetrics = computed(() => {
    if (metricsHistory.value.length === 0) return currentMetrics.value

    const samples = metricsHistory.value.slice(-10) // Últimas 10 amostras
    const avg = {
      fps: 0,
      memory: { used: 0, total: 0, percentage: 0 },
      renderTime: 0,
      networkLatency: 0,
      domNodes: 0
    }

    samples.forEach(sample => {
      avg.fps += sample.fps
      avg.memory.used += sample.memory.used
      avg.memory.total += sample.memory.total
      avg.memory.percentage += sample.memory.percentage
      avg.renderTime += sample.renderTime
      avg.networkLatency += sample.networkLatency
      avg.domNodes += sample.domNodes
    })

    const count = samples.length
    return {
      fps: Math.round((avg.fps / count) * 100) / 100,
      memory: {
        used: Math.round((avg.memory.used / count) * 100) / 100,
        total: Math.round((avg.memory.total / count) * 100) / 100,
        percentage: Math.round((avg.memory.percentage / count) * 100) / 100
      },
      renderTime: Math.round((avg.renderTime / count) * 100) / 100,
      networkLatency: Math.round((avg.networkLatency / count) * 100) / 100,
      domNodes: Math.round(avg.domNodes / count)
    }
  })

  const performanceStatus = computed(() => {
    const score = performanceScore.value
    if (score >= 80) return { level: 'excellent', color: '#22c55e', text: 'Excelente' }
    if (score >= 60) return { level: 'good', color: '#3b82f6', text: 'Bom' }
    if (score >= 40) return { level: 'fair', color: '#f59e0b', text: 'Regular' }
    if (score >= 20) return { level: 'poor', color: '#ef4444', text: 'Ruim' }
    return { level: 'critical', color: '#dc2626', text: 'Crítico' }
  })

  const recentAlerts = computed(() => {
    return alerts.value.slice(-5) // Últimos 5 alertas
  })

  // Métodos de monitoramento
  const measureFPS = () => {
    if (!enableFPSMonitoring) return 0

    const now = performance.now()
    frameCount++

    if (lastFrameTime === 0) {
      lastFrameTime = now
      return 0
    }

    const deltaTime = now - lastFrameTime
    if (deltaTime >= 1000) { // Calcular FPS a cada segundo
      const fps = Math.round((frameCount * 1000) / deltaTime)
      frameCount = 0
      lastFrameTime = now
      return fps
    }

    return currentMetrics.value.fps
  }

  const measureMemory = () => {
    if (!enableMemoryMonitoring || !performance.memory) {
      return { used: 0, total: 0, percentage: 0 }
    }

    const memory = performance.memory
    const used = Math.round((memory.usedJSHeapSize / 1024 / 1024) * 100) / 100 // MB
    const total = Math.round((memory.totalJSHeapSize / 1024 / 1024) * 100) / 100 // MB
    const percentage = total > 0 ? Math.round((used / total) * 10000) / 100 : 0

    return { used, total, percentage }
  }

  const measureRenderTime = () => {
    if (!enableRenderMonitoring) return 0
    
    const now = performance.now()
    if (renderStartTime > 0) {
      return Math.round((now - renderStartTime) * 100) / 100
    }
    return 0
  }

  const measureNetworkLatency = async () => {
    if (!enableNetworkMonitoring) return 0

    try {
      const start = performance.now()
      await fetch('/api/ping', { 
        method: 'HEAD',
        cache: 'no-cache'
      })
      const end = performance.now()
      return Math.round((end - start) * 100) / 100
    } catch (error) {
      return -1 // Erro de rede
    }
  }

  const measureDOMNodes = () => {
    return document.querySelectorAll('*').length
  }

  const calculatePerformanceScore = (metrics) => {
    let score = 100
    const { fps, memory, renderTime, networkLatency } = metrics

    // Penalizar FPS baixo
    if (fps < thresholds.fps.critical) {
      score -= 30
    } else if (fps < thresholds.fps.warning) {
      score -= 15
    }

    // Penalizar uso alto de memória
    if (memory.percentage > thresholds.memory.critical) {
      score -= 25
    } else if (memory.percentage > thresholds.memory.warning) {
      score -= 10
    }

    // Penalizar tempo de renderização alto
    if (renderTime > thresholds.renderTime.critical) {
      score -= 20
    } else if (renderTime > thresholds.renderTime.warning) {
      score -= 10
    }

    // Penalizar latência alta de rede
    if (networkLatency > 1000) {
      score -= 15
    } else if (networkLatency > 500) {
      score -= 5
    }

    return Math.max(0, Math.min(100, score))
  }

  const checkThresholds = (metrics) => {
    const newAlerts = []

    // Verificar FPS
    if (metrics.fps < thresholds.fps.critical) {
      newAlerts.push({
        id: `fps-critical-${Date.now()}`,
        type: 'fps',
        severity: 'critical',
        message: `FPS crítico: ${metrics.fps} (< ${thresholds.fps.critical})`,
        timestamp: new Date().toISOString(),
        value: metrics.fps,
        threshold: thresholds.fps.critical
      })
    } else if (metrics.fps < thresholds.fps.warning) {
      newAlerts.push({
        id: `fps-warning-${Date.now()}`,
        type: 'fps',
        severity: 'warning',
        message: `FPS baixo: ${metrics.fps} (< ${thresholds.fps.warning})`,
        timestamp: new Date().toISOString(),
        value: metrics.fps,
        threshold: thresholds.fps.warning
      })
    }

    // Verificar memória
    if (metrics.memory.percentage > thresholds.memory.critical) {
      newAlerts.push({
        id: `memory-critical-${Date.now()}`,
        type: 'memory',
        severity: 'critical',
        message: `Uso crítico de memória: ${metrics.memory.percentage}% (> ${thresholds.memory.critical}%)`,
        timestamp: new Date().toISOString(),
        value: metrics.memory.percentage,
        threshold: thresholds.memory.critical
      })
    } else if (metrics.memory.percentage > thresholds.memory.warning) {
      newAlerts.push({
        id: `memory-warning-${Date.now()}`,
        type: 'memory',
        severity: 'warning',
        message: `Uso alto de memória: ${metrics.memory.percentage}% (> ${thresholds.memory.warning}%)`,
        timestamp: new Date().toISOString(),
        value: metrics.memory.percentage,
        threshold: thresholds.memory.warning
      })
    }

    // Verificar tempo de renderização
    if (metrics.renderTime > thresholds.renderTime.critical) {
      newAlerts.push({
        id: `render-critical-${Date.now()}`,
        type: 'render',
        severity: 'critical',
        message: `Tempo de renderização crítico: ${metrics.renderTime}ms (> ${thresholds.renderTime.critical}ms)`,
        timestamp: new Date().toISOString(),
        value: metrics.renderTime,
        threshold: thresholds.renderTime.critical
      })
    } else if (metrics.renderTime > thresholds.renderTime.warning) {
      newAlerts.push({
        id: `render-warning-${Date.now()}`,
        type: 'render',
        severity: 'warning',
        message: `Tempo de renderização alto: ${metrics.renderTime}ms (> ${thresholds.renderTime.warning}ms)`,
        timestamp: new Date().toISOString(),
        value: metrics.renderTime,
        threshold: thresholds.renderTime.warning
      })
    }

    // Adicionar novos alertas
    if (newAlerts.length > 0) {
      alerts.value.push(...newAlerts)
      
      // Manter apenas os últimos 50 alertas
      if (alerts.value.length > 50) {
        alerts.value = alerts.value.slice(-50)
      }
    }
  }

  const collectMetrics = async () => {
    const metrics = {
      fps: measureFPS(),
      memory: measureMemory(),
      renderTime: measureRenderTime(),
      networkLatency: await measureNetworkLatency(),
      domNodes: measureDOMNodes(),
      timestamp: Date.now()
    }

    currentMetrics.value = metrics

    // Adicionar ao histórico
    metricsHistory.value.push(metrics)
    if (metricsHistory.value.length > maxSamples) {
      metricsHistory.value = metricsHistory.value.slice(-maxSamples)
    }

    // Calcular score de performance
    performanceScore.value = calculatePerformanceScore(metrics)

    // Verificar thresholds
    checkThresholds(metrics)

    return metrics
  }

  const startFPSMonitoring = () => {
    if (!enableFPSMonitoring) return

    const updateFPS = () => {
      measureFPS()
      if (isMonitoring.value) {
        animationFrameId = requestAnimationFrame(updateFPS)
      }
    }

    animationFrameId = requestAnimationFrame(updateFPS)
  }

  const startRenderMonitoring = () => {
    if (!enableRenderMonitoring) return

    // Observer para mutações no DOM
    observer = new MutationObserver(() => {
      renderStartTime = performance.now()
      
      nextTick(() => {
        const renderTime = measureRenderTime()
        if (renderTime > 0) {
          currentMetrics.value.renderTime = renderTime
        }
      })
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true
    })
  }

  const startMonitoring = () => {
    if (isMonitoring.value) return

    isMonitoring.value = true

    // Iniciar monitoramento de FPS
    startFPSMonitoring()

    // Iniciar monitoramento de renderização
    startRenderMonitoring()

    // Iniciar coleta de métricas
    monitoringInterval = setInterval(collectMetrics, sampleInterval)

    // Coleta inicial
    collectMetrics()
  }

  const stopMonitoring = () => {
    isMonitoring.value = false

    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }

    if (monitoringInterval) {
      clearInterval(monitoringInterval)
      monitoringInterval = null
    }

    if (observer) {
      observer.disconnect()
      observer = null
    }
  }

  const clearHistory = () => {
    metricsHistory.value = []
    alerts.value = []
  }

  const exportMetrics = () => {
    return {
      current: currentMetrics.value,
      average: averageMetrics.value,
      history: metricsHistory.value,
      alerts: alerts.value,
      performanceScore: performanceScore.value,
      status: performanceStatus.value,
      timestamp: new Date().toISOString()
    }
  }

  const getMetricsTrend = (metric, samples = 10) => {
    const history = metricsHistory.value.slice(-samples)
    if (history.length < 2) return 'stable'

    const values = history.map(h => {
      if (metric.includes('.')) {
        const [parent, child] = metric.split('.')
        return h[parent][child]
      }
      return h[metric]
    })

    const first = values[0]
    const last = values[values.length - 1]
    const change = ((last - first) / first) * 100

    if (Math.abs(change) < 5) return 'stable'
    return change > 0 ? 'increasing' : 'decreasing'
  }

  // Lifecycle
  onMounted(() => {
    if (options.autoStart !== false) {
      startMonitoring()
    }
  })

  onUnmounted(() => {
    stopMonitoring()
  })

  return {
    // Estados
    isMonitoring,
    currentMetrics,
    averageMetrics,
    metricsHistory,
    alerts,
    recentAlerts,
    performanceScore,
    performanceStatus,

    // Métodos
    startMonitoring,
    stopMonitoring,
    clearHistory,
    exportMetrics,
    getMetricsTrend,
    collectMetrics
  }
}

/**
 * Composable para monitoramento específico de componentes
 */
export function useComponentPerformance(componentName) {
  const renderTimes = ref([])
  const updateCount = ref(0)
  const lastRenderTime = ref(0)

  const startRender = () => {
    lastRenderTime.value = performance.now()
  }

  const endRender = () => {
    if (lastRenderTime.value > 0) {
      const renderTime = performance.now() - lastRenderTime.value
      renderTimes.value.push({
        time: renderTime,
        timestamp: Date.now(),
        component: componentName
      })

      // Manter apenas as últimas 20 renderizações
      if (renderTimes.value.length > 20) {
        renderTimes.value = renderTimes.value.slice(-20)
      }

      updateCount.value++
      lastRenderTime.value = 0

      return renderTime
    }
    return 0
  }

  const averageRenderTime = computed(() => {
    if (renderTimes.value.length === 0) return 0
    const total = renderTimes.value.reduce((sum, r) => sum + r.time, 0)
    return Math.round((total / renderTimes.value.length) * 100) / 100
  })

  const slowestRender = computed(() => {
    if (renderTimes.value.length === 0) return 0
    return Math.max(...renderTimes.value.map(r => r.time))
  })

  const fastestRender = computed(() => {
    if (renderTimes.value.length === 0) return 0
    return Math.min(...renderTimes.value.map(r => r.time))
  })

  return {
    renderTimes,
    updateCount,
    averageRenderTime,
    slowestRender,
    fastestRender,
    startRender,
    endRender
  }
}