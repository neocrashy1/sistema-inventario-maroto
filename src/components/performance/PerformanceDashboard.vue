<template>
  <div class="performance-dashboard" :class="{ 'is-monitoring': isMonitoring }">
    <!-- Header com controles -->
    <div class="dashboard-header">
      <div class="header-left">
        <h3 class="dashboard-title">
          <span class="title-icon">⚡</span>
          Performance Monitor
        </h3>
        <div class="status-indicator" :class="performanceStatus.level">
          <span class="status-dot"></span>
          <span class="status-text">{{ performanceStatus.text }}</span>
        </div>
      </div>
      
      <div class="header-right">
        <div class="controls">
          <button
            @click="toggleMonitoring"
            :class="['control-btn', { 'active': isMonitoring }]"
            :title="isMonitoring ? 'Parar monitoramento' : 'Iniciar monitoramento'"
          >
            <span v-if="isMonitoring">⏸️</span>
            <span v-else>▶️</span>
          </button>
          
          <button
            @click="clearHistory"
            class="control-btn"
            title="Limpar histórico"
            :disabled="!isMonitoring"
          >
            🗑️
          </button>
          
          <button
            @click="exportData"
            class="control-btn"
            title="Exportar dados"
          >
            📊
          </button>
        </div>
      </div>
    </div>

    <!-- Score geral de performance -->
    <div class="performance-score">
      <div class="score-circle" :style="{ '--score': performanceScore }">
        <div class="score-value">{{ performanceScore }}</div>
        <div class="score-label">Score</div>
      </div>
      
      <div class="score-details">
        <div class="score-breakdown">
          <div class="breakdown-item">
            <span class="breakdown-label">FPS:</span>
            <span class="breakdown-value" :class="getFPSClass(currentMetrics.fps)">
              {{ currentMetrics.fps }}
            </span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Memória:</span>
            <span class="breakdown-value" :class="getMemoryClass(currentMetrics.memory.percentage)">
              {{ currentMetrics.memory.percentage }}%
            </span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Render:</span>
            <span class="breakdown-value" :class="getRenderClass(currentMetrics.renderTime)">
              {{ currentMetrics.renderTime }}ms
            </span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Rede:</span>
            <span class="breakdown-value" :class="getNetworkClass(currentMetrics.networkLatency)">
              {{ currentMetrics.networkLatency }}ms
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Métricas em tempo real -->
    <div class="metrics-grid">
      <!-- FPS Monitor -->
      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">FPS</h4>
          <div class="metric-trend" :class="getFPSTrend()">
            <span class="trend-icon">{{ getTrendIcon(getFPSTrend()) }}</span>
          </div>
        </div>
        <div class="metric-content">
          <div class="metric-value" :class="getFPSClass(currentMetrics.fps)">
            {{ currentMetrics.fps }}
          </div>
          <div class="metric-subtitle">
            Média: {{ averageMetrics.fps }}
          </div>
          <div class="metric-chart">
            <canvas ref="fpsChart" width="200" height="60"></canvas>
          </div>
        </div>
      </div>

      <!-- Memory Monitor -->
      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">Memória</h4>
          <div class="metric-trend" :class="getMemoryTrend()">
            <span class="trend-icon">{{ getTrendIcon(getMemoryTrend()) }}</span>
          </div>
        </div>
        <div class="metric-content">
          <div class="metric-value" :class="getMemoryClass(currentMetrics.memory.percentage)">
            {{ currentMetrics.memory.used }}MB
          </div>
          <div class="metric-subtitle">
            {{ currentMetrics.memory.percentage }}% de {{ currentMetrics.memory.total }}MB
          </div>
          <div class="memory-bar">
            <div 
              class="memory-fill" 
              :style="{ width: currentMetrics.memory.percentage + '%' }"
              :class="getMemoryClass(currentMetrics.memory.percentage)"
            ></div>
          </div>
        </div>
      </div>

      <!-- Render Time Monitor -->
      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">Render Time</h4>
          <div class="metric-trend" :class="getRenderTrend()">
            <span class="trend-icon">{{ getTrendIcon(getRenderTrend()) }}</span>
          </div>
        </div>
        <div class="metric-content">
          <div class="metric-value" :class="getRenderClass(currentMetrics.renderTime)">
            {{ currentMetrics.renderTime }}ms
          </div>
          <div class="metric-subtitle">
            Média: {{ averageMetrics.renderTime }}ms
          </div>
          <div class="render-indicator">
            <div class="render-bar">
              <div 
                class="render-fill" 
                :style="{ width: Math.min((currentMetrics.renderTime / 50) * 100, 100) + '%' }"
                :class="getRenderClass(currentMetrics.renderTime)"
              ></div>
            </div>
            <div class="render-thresholds">
              <span class="threshold good">16ms</span>
              <span class="threshold warning">33ms</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Network Latency Monitor -->
      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">Latência de Rede</h4>
          <div class="metric-trend" :class="getNetworkTrend()">
            <span class="trend-icon">{{ getTrendIcon(getNetworkTrend()) }}</span>
          </div>
        </div>
        <div class="metric-content">
          <div class="metric-value" :class="getNetworkClass(currentMetrics.networkLatency)">
            {{ currentMetrics.networkLatency === -1 ? 'Erro' : currentMetrics.networkLatency + 'ms' }}
          </div>
          <div class="metric-subtitle">
            Média: {{ averageMetrics.networkLatency }}ms
          </div>
          <div class="network-status">
            <div class="status-dots">
              <div 
                v-for="i in 5" 
                :key="i"
                class="status-dot"
                :class="getNetworkDotClass(i, currentMetrics.networkLatency)"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- DOM Nodes Monitor -->
      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">DOM Nodes</h4>
          <div class="metric-trend" :class="getDOMTrend()">
            <span class="trend-icon">{{ getTrendIcon(getDOMTrend()) }}</span>
          </div>
        </div>
        <div class="metric-content">
          <div class="metric-value">
            {{ formatNumber(currentMetrics.domNodes) }}
          </div>
          <div class="metric-subtitle">
            Média: {{ formatNumber(averageMetrics.domNodes) }}
          </div>
          <div class="dom-complexity" :class="getDOMComplexityClass(currentMetrics.domNodes)">
            {{ getDOMComplexityText(currentMetrics.domNodes) }}
          </div>
        </div>
      </div>

      <!-- Alerts Panel -->
      <div class="metric-card alerts-card">
        <div class="metric-header">
          <h4 class="metric-title">Alertas Recentes</h4>
          <div class="alerts-count" :class="{ 'has-alerts': recentAlerts.length > 0 }">
            {{ recentAlerts.length }}
          </div>
        </div>
        <div class="metric-content">
          <div v-if="recentAlerts.length === 0" class="no-alerts">
            <span class="no-alerts-icon">✅</span>
            <span class="no-alerts-text">Nenhum alerta</span>
          </div>
          <div v-else class="alerts-list">
            <div 
              v-for="alert in recentAlerts.slice(0, 3)" 
              :key="alert.id"
              class="alert-item"
              :class="alert.severity"
            >
              <div class="alert-icon">
                <span v-if="alert.severity === 'critical'">🔴</span>
                <span v-else-if="alert.severity === 'warning'">🟡</span>
                <span v-else>🔵</span>
              </div>
              <div class="alert-content">
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Gráfico de histórico -->
    <div class="history-chart" v-if="showHistoryChart">
      <div class="chart-header">
        <h4 class="chart-title">Histórico de Performance</h4>
        <div class="chart-controls">
          <select v-model="selectedMetric" class="metric-selector">
            <option value="fps">FPS</option>
            <option value="memory.percentage">Memória (%)</option>
            <option value="renderTime">Render Time (ms)</option>
            <option value="networkLatency">Latência (ms)</option>
          </select>
          <button @click="toggleHistoryChart" class="toggle-chart-btn">
            {{ showHistoryChart ? '📉' : '📈' }}
          </button>
        </div>
      </div>
      <div class="chart-container">
        <canvas ref="historyChart" width="800" height="200"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { usePerformanceMonitor } from '@/composables/usePerformanceMonitor'

// Props
const props = defineProps({
  autoStart: {
    type: Boolean,
    default: true
  },
  showHistoryChart: {
    type: Boolean,
    default: true
  },
  thresholds: {
    type: Object,
    default: () => ({
      fps: { warning: 30, critical: 15 },
      memory: { warning: 50, critical: 80 },
      renderTime: { warning: 16, critical: 33 }
    })
  }
})

// Emits
const emit = defineEmits(['alert', 'performance-change'])

// Performance monitor
const {
  isMonitoring,
  currentMetrics,
  averageMetrics,
  metricsHistory,
  recentAlerts,
  performanceScore,
  performanceStatus,
  startMonitoring,
  stopMonitoring,
  clearHistory: clearPerformanceHistory,
  exportMetrics,
  getMetricsTrend
} = usePerformanceMonitor({
  ...props.thresholds,
  autoStart: props.autoStart
})

// Refs para gráficos
const fpsChart = ref(null)
const historyChart = ref(null)
const selectedMetric = ref('fps')

// Estados locais
const showHistoryChart = ref(props.showHistoryChart)

// Métodos de classificação
const getFPSClass = (fps) => {
  if (fps >= props.thresholds.fps.warning) return 'good'
  if (fps >= props.thresholds.fps.critical) return 'warning'
  return 'critical'
}

const getMemoryClass = (percentage) => {
  if (percentage <= props.thresholds.memory.warning) return 'good'
  if (percentage <= props.thresholds.memory.critical) return 'warning'
  return 'critical'
}

const getRenderClass = (time) => {
  if (time <= props.thresholds.renderTime.warning) return 'good'
  if (time <= props.thresholds.renderTime.critical) return 'warning'
  return 'critical'
}

const getNetworkClass = (latency) => {
  if (latency === -1) return 'error'
  if (latency <= 100) return 'good'
  if (latency <= 500) return 'warning'
  return 'critical'
}

const getDOMComplexityClass = (nodes) => {
  if (nodes <= 1000) return 'good'
  if (nodes <= 5000) return 'warning'
  return 'critical'
}

// Métodos de tendência
const getFPSTrend = () => getMetricsTrend('fps')
const getMemoryTrend = () => getMetricsTrend('memory.percentage')
const getRenderTrend = () => getMetricsTrend('renderTime')
const getNetworkTrend = () => getMetricsTrend('networkLatency')
const getDOMTrend = () => getMetricsTrend('domNodes')

const getTrendIcon = (trend) => {
  switch (trend) {
    case 'increasing': return '📈'
    case 'decreasing': return '📉'
    default: return '➡️'
  }
}

// Métodos utilitários
const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('pt-BR', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

const getDOMComplexityText = (nodes) => {
  if (nodes <= 1000) return 'Simples'
  if (nodes <= 5000) return 'Moderado'
  return 'Complexo'
}

const getNetworkDotClass = (index, latency) => {
  const thresholds = [50, 100, 200, 500, 1000]
  if (latency === -1) return 'error'
  return latency <= thresholds[index - 1] ? 'active' : 'inactive'
}

// Métodos de controle
const toggleMonitoring = () => {
  if (isMonitoring.value) {
    stopMonitoring()
  } else {
    startMonitoring()
  }
}

const clearHistory = () => {
  clearPerformanceHistory()
}

const exportData = () => {
  const data = exportMetrics()
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `performance-metrics-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const toggleHistoryChart = () => {
  showHistoryChart.value = !showHistoryChart.value
}

// Gráficos
const drawFPSChart = () => {
  if (!fpsChart.value) return
  
  const canvas = fpsChart.value
  const ctx = canvas.getContext('2d')
  const width = canvas.width
  const height = canvas.height
  
  // Limpar canvas
  ctx.clearRect(0, 0, width, height)
  
  // Dados dos últimos 20 pontos
  const data = metricsHistory.value.slice(-20).map(m => m.fps)
  if (data.length < 2) return
  
  // Configurações
  const maxFPS = 60
  const minFPS = 0
  const stepX = width / (data.length - 1)
  
  // Desenhar linha
  ctx.strokeStyle = getFPSClass(currentMetrics.value.fps) === 'good' ? '#22c55e' : 
                   getFPSClass(currentMetrics.value.fps) === 'warning' ? '#f59e0b' : '#ef4444'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((fps, index) => {
    const x = index * stepX
    const y = height - ((fps - minFPS) / (maxFPS - minFPS)) * height
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
}

const drawHistoryChart = () => {
  if (!historyChart.value || !showHistoryChart.value) return
  
  const canvas = historyChart.value
  const ctx = canvas.getContext('2d')
  const width = canvas.width
  const height = canvas.height
  
  // Limpar canvas
  ctx.clearRect(0, 0, width, height)
  
  // Dados
  const data = metricsHistory.value.map(m => {
    if (selectedMetric.value.includes('.')) {
      const [parent, child] = selectedMetric.value.split('.')
      return m[parent][child]
    }
    return m[selectedMetric.value]
  })
  
  if (data.length < 2) return
  
  // Configurações
  const maxValue = Math.max(...data)
  const minValue = Math.min(...data)
  const range = maxValue - minValue || 1
  const stepX = width / (data.length - 1)
  
  // Desenhar grade
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1
  for (let i = 0; i <= 5; i++) {
    const y = (height / 5) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }
  
  // Desenhar linha
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((value, index) => {
    const x = index * stepX
    const y = height - ((value - minValue) / range) * height
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // Desenhar área
  ctx.fillStyle = 'rgba(59, 130, 246, 0.1)'
  ctx.lineTo(width, height)
  ctx.lineTo(0, height)
  ctx.closePath()
  ctx.fill()
}

// Watchers
watch(metricsHistory, () => {
  nextTick(() => {
    drawFPSChart()
    drawHistoryChart()
  })
}, { deep: true })

watch(selectedMetric, () => {
  nextTick(() => {
    drawHistoryChart()
  })
})

watch(recentAlerts, (newAlerts) => {
  if (newAlerts.length > 0) {
    const latestAlert = newAlerts[newAlerts.length - 1]
    emit('alert', latestAlert)
  }
}, { deep: true })

watch(performanceScore, (newScore, oldScore) => {
  if (Math.abs(newScore - oldScore) >= 10) {
    emit('performance-change', {
      score: newScore,
      status: performanceStatus.value,
      change: newScore - oldScore
    })
  }
})

// Lifecycle
onMounted(() => {
  nextTick(() => {
    drawFPSChart()
    drawHistoryChart()
  })
})
</script>

<style scoped>
.performance-dashboard {
  background: var(--background-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.title-icon {
  font-size: 1.5rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
}

.status-indicator.excellent {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-indicator.good {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.status-indicator.fair {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-indicator.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.status-indicator.critical {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.controls {
  display: flex;
  gap: var(--spacing-xs);
}

.control-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--background-color);
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: var(--hover-color);
}

.control-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.performance-score {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--background-secondary);
  border-radius: var(--border-radius);
}

.score-circle {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    var(--primary-color) 0deg,
    var(--primary-color) calc(var(--score) * 3.6deg),
    var(--border-light) calc(var(--score) * 3.6deg),
    var(--border-light) 360deg
  );
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: var(--background-color);
}

.score-value {
  position: relative;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.score-label {
  position: relative;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.score-details {
  flex: 1;
}

.score-breakdown {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm);
  background: var(--background-color);
  border-radius: var(--border-radius-sm);
}

.breakdown-label {
  font-weight: 500;
  color: var(--text-muted);
}

.breakdown-value {
  font-weight: 600;
}

.breakdown-value.good {
  color: #16a34a;
}

.breakdown-value.warning {
  color: #d97706;
}

.breakdown-value.critical {
  color: #dc2626;
}

.breakdown-value.error {
  color: #7c2d12;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.metric-card {
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.metric-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.metric-trend {
  font-size: 1.2rem;
}

.metric-content {
  text-align: center;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--spacing-xs);
}

.metric-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: var(--spacing-md);
}

.metric-chart {
  margin-top: var(--spacing-md);
}

.memory-bar {
  width: 100%;
  height: 8px;
  background: var(--border-light);
  border-radius: 4px;
  overflow: hidden;
  margin-top: var(--spacing-md);
}

.memory-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.memory-fill.good {
  background: #16a34a;
}

.memory-fill.warning {
  background: #d97706;
}

.memory-fill.critical {
  background: #dc2626;
}

.render-indicator {
  margin-top: var(--spacing-md);
}

.render-bar {
  width: 100%;
  height: 6px;
  background: var(--border-light);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: var(--spacing-xs);
}

.render-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.render-fill.good {
  background: #16a34a;
}

.render-fill.warning {
  background: #d97706;
}

.render-fill.critical {
  background: #dc2626;
}

.render-thresholds {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.network-status {
  margin-top: var(--spacing-md);
}

.status-dots {
  display: flex;
  justify-content: center;
  gap: var(--spacing-xs);
}

.status-dots .status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.status-dots .status-dot.active {
  background: #16a34a;
}

.status-dots .status-dot.inactive {
  background: var(--border-light);
}

.status-dots .status-dot.error {
  background: #dc2626;
}

.dom-complexity {
  margin-top: var(--spacing-md);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
}

.dom-complexity.good {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.dom-complexity.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.dom-complexity.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.alerts-card {
  grid-column: span 2;
}

.alerts-count {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  background: var(--border-light);
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 600;
}

.alerts-count.has-alerts {
  background: #dc2626;
  color: white;
}

.no-alerts {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  color: var(--text-muted);
}

.no-alerts-icon {
  font-size: 2rem;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.alert-item {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  border-left: 4px solid;
}

.alert-item.critical {
  background: rgba(239, 68, 68, 0.1);
  border-left-color: #dc2626;
}

.alert-item.warning {
  background: rgba(245, 158, 11, 0.1);
  border-left-color: #d97706;
}

.alert-item.info {
  background: rgba(59, 130, 246, 0.1);
  border-left-color: #2563eb;
}

.alert-icon {
  font-size: 1.2rem;
}

.alert-content {
  flex: 1;
}

.alert-message {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
}

.alert-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.history-chart {
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.chart-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.metric-selector {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--background-color);
  font-size: 0.875rem;
}

.toggle-chart-btn {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--background-color);
  cursor: pointer;
  font-size: 1rem;
}

.chart-container {
  margin-top: var(--spacing-md);
}

/* Responsividade */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .alerts-card {
    grid-column: span 1;
  }
  
  .performance-score {
    flex-direction: column;
    text-align: center;
  }
  
  .score-breakdown {
    grid-template-columns: 1fr;
  }
}

/* Animações */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.is-monitoring .status-dot {
  animation: pulse 2s infinite;
}

/* Acessibilidade */
@media (prefers-reduced-motion: reduce) {
  .memory-fill,
  .render-fill,
  .status-dots .status-dot {
    transition: none;
  }
  
  .is-monitoring .status-dot {
    animation: none;
  }
}
</style>