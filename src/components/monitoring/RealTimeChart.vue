<template>
  <div class="real-time-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-controls">
        <button 
          @click="togglePause" 
          :class="['btn', 'btn-sm', isPaused ? 'btn-success' : 'btn-warning']"
          :title="isPaused ? 'Retomar atualizações' : 'Pausar atualizações'"
        >
          <i :class="isPaused ? 'fas fa-play' : 'fas fa-pause'"></i>
          {{ isPaused ? 'Retomar' : 'Pausar' }}
        </button>
        <button 
          @click="clearData" 
          class="btn btn-sm btn-outline-secondary"
          title="Limpar dados do gráfico"
        >
          <i class="fas fa-trash"></i>
          Limpar
        </button>
      </div>
    </div>
    
    <div class="chart-container">
      <Line
        :data="chartData"
        :options="chartOptions"
        :key="chartKey"
        ref="chartRef"
      />
    </div>
    
    <div class="chart-stats">
      <div class="stat-item">
        <span class="stat-label">Atual:</span>
        <span class="stat-value" :class="getValueClass(currentValue)">
          {{ formatValue(currentValue) }}{{ unit }}
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Média:</span>
        <span class="stat-value">{{ formatValue(averageValue) }}{{ unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Máximo:</span>
        <span class="stat-value">{{ formatValue(maxValue) }}{{ unit }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Mínimo:</span>
        <span class="stat-value">{{ formatValue(minValue) }}{{ unit }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  unit: {
    type: String,
    default: '%'
  },
  color: {
    type: String,
    default: '#3b82f6'
  },
  maxDataPoints: {
    type: Number,
    default: 50
  },
  warningThreshold: {
    type: Number,
    default: 70
  },
  criticalThreshold: {
    type: Number,
    default: 90
  },
  updateInterval: {
    type: Number,
    default: 5000
  }
})

// Emits
const emit = defineEmits(['update-data'])

// Estado reativo
const chartRef = ref(null)
const chartKey = ref(0)
const isPaused = ref(false)
const dataPoints = ref([])
const timeLabels = ref([])
const updateTimer = ref(null)

// Valores calculados
const currentValue = computed(() => {
  return dataPoints.value.length > 0 ? dataPoints.value[dataPoints.value.length - 1] : 0
})

const averageValue = computed(() => {
  if (dataPoints.value.length === 0) return 0
  const sum = dataPoints.value.reduce((acc, val) => acc + val, 0)
  return sum / dataPoints.value.length
})

const maxValue = computed(() => {
  return dataPoints.value.length > 0 ? Math.max(...dataPoints.value) : 0
})

const minValue = computed(() => {
  return dataPoints.value.length > 0 ? Math.min(...dataPoints.value) : 0
})

// Configuração do gráfico
const chartData = computed(() => ({
  labels: timeLabels.value,
  datasets: [
    {
      label: props.title,
      data: dataPoints.value,
      borderColor: props.color,
      backgroundColor: `${props.color}20`,
      fill: true,
      tension: 0.4,
      pointRadius: 2,
      pointHoverRadius: 4,
      borderWidth: 2
    }
  ]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index'
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: props.color,
      borderWidth: 1,
      callbacks: {
        label: (context) => {
          return `${props.title}: ${formatValue(context.parsed.y)}${props.unit}`
        }
      }
    }
  },
  scales: {
    x: {
      display: true,
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      },
      ticks: {
        color: '#6b7280',
        maxTicksLimit: 10
      }
    },
    y: {
      display: true,
      beginAtZero: true,
      max: props.unit === '%' ? 100 : undefined,
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      },
      ticks: {
        color: '#6b7280',
        callback: (value) => `${formatValue(value)}${props.unit}`
      }
    }
  },
  animation: {
    duration: 750,
    easing: 'easeInOutQuart'
  }
}))

// Métodos
const formatValue = (value) => {
  if (typeof value !== 'number') return '0'
  return value.toFixed(1)
}

const getValueClass = (value) => {
  if (value >= props.criticalThreshold) return 'text-danger'
  if (value >= props.warningThreshold) return 'text-warning'
  return 'text-success'
}

const addDataPoint = (value) => {
  if (isPaused.value) return

  const now = new Date()
  const timeLabel = now.toLocaleTimeString('pt-BR', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })

  dataPoints.value.push(value)
  timeLabels.value.push(timeLabel)

  // Manter apenas os últimos N pontos
  if (dataPoints.value.length > props.maxDataPoints) {
    dataPoints.value.shift()
    timeLabels.value.shift()
  }

  // Forçar re-render do gráfico
  chartKey.value++
}

const togglePause = () => {
  isPaused.value = !isPaused.value
  
  if (isPaused.value) {
    clearInterval(updateTimer.value)
  } else {
    startUpdateTimer()
  }
}

const clearData = () => {
  dataPoints.value = []
  timeLabels.value = []
  chartKey.value++
}

const startUpdateTimer = () => {
  if (updateTimer.value) {
    clearInterval(updateTimer.value)
  }
  
  updateTimer.value = setInterval(() => {
    if (!isPaused.value) {
      emit('update-data')
    }
  }, props.updateInterval)
}

// Watchers
watch(() => props.data, (newData) => {
  if (newData && newData.length > 0) {
    const latestValue = newData[newData.length - 1]
    addDataPoint(latestValue)
  }
}, { deep: true })

// Lifecycle
onMounted(() => {
  startUpdateTimer()
  
  // Adicionar dados iniciais se fornecidos
  if (props.data && props.data.length > 0) {
    props.data.forEach(value => addDataPoint(value))
  }
})

onUnmounted(() => {
  if (updateTimer.value) {
    clearInterval(updateTimer.value)
  }
})

// Expor métodos para componente pai
defineExpose({
  addDataPoint,
  clearData,
  togglePause
})
</script>

<style scoped>
.real-time-chart {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.chart-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #374151;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-success {
  background-color: #10b981;
  border-color: #10b981;
  color: white;
}

.btn-success:hover {
  background-color: #059669;
  border-color: #059669;
}

.btn-warning {
  background-color: #f59e0b;
  border-color: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background-color: #d97706;
  border-color: #d97706;
}

.btn-outline-secondary {
  background-color: transparent;
  border-color: #6b7280;
  color: #6b7280;
}

.btn-outline-secondary:hover {
  background-color: #6b7280;
  color: white;
}

.chart-container {
  height: 300px;
  padding: 1rem;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  padding: 1rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.text-success {
  color: #10b981 !important;
}

.text-warning {
  color: #f59e0b !important;
}

.text-danger {
  color: #ef4444 !important;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
  
  .chart-controls {
    justify-content: center;
  }
  
  .chart-stats {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .stat-item {
    flex: 1;
    min-width: 120px;
  }
}
</style>