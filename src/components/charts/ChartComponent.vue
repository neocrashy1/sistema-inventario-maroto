<template>
  <div class="chart-container">
    <canvas :id="chartId" :width="width" :height="height"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'

// Registrar todos os componentes do Chart.js
Chart.register(...registerables)

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['line', 'bar', 'pie', 'doughnut', 'radar', 'polarArea'].includes(value)
  },
  data: {
    type: Object,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  },
  width: {
    type: Number,
    default: 400
  },
  height: {
    type: Number,
    default: 200
  },
  chartId: {
    type: String,
    default: () => `chart-${Math.random().toString(36).substr(2, 9)}`
  }
})

const chart = ref(null)

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 20,
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: '#333',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
      callbacks: {
        label: function(context) {
          if (props.type === 'pie' || props.type === 'doughnut') {
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = ((context.parsed * 100) / total).toFixed(1)
            return `${context.label}: ${context.parsed} (${percentage}%)`
          }
          return `${context.dataset.label}: ${context.parsed}`
        }
      }
    }
  },
  scales: props.type === 'pie' || props.type === 'doughnut' ? {} : {
    x: {
      grid: {
        display: false
      },
      ticks: {
        font: {
          size: 11
        }
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      },
      ticks: {
        font: {
          size: 11
        }
      }
    }
  }
}

const createChart = () => {
  const canvas = document.getElementById(props.chartId)
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  
  if (chart.value) {
    chart.value.destroy()
  }

  const mergedOptions = {
    ...defaultOptions,
    ...props.options
  }

  chart.value = new Chart(ctx, {
    type: props.type,
    data: props.data,
    options: mergedOptions
  })
}

const updateChart = () => {
  if (chart.value) {
    chart.value.data = props.data
    chart.value.update('none')
  }
}

onMounted(async () => {
  await nextTick()
  createChart()
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.destroy()
  }
})

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

watch(() => props.type, () => {
  createChart()
})
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 200px;
}

canvas {
  max-width: 100%;
  height: auto;
}
</style>