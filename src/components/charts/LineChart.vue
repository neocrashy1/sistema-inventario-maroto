<template>
  <div class="line-chart">
    <canvas 
      ref="chartCanvas" 
      :width="width" 
      :height="height"
      @mousemove="handleMouseMove"
      @mouseleave="hideTooltip"
    ></canvas>
    
    <!-- Tooltip -->
    <div 
      v-if="tooltip.visible"
      class="chart-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-label">{{ tooltip.label }}</div>
        <div class="tooltip-value">{{ formatValue(tooltip.value) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  labels: {
    type: Array,
    default: () => []
  },
  width: {
    type: Number,
    default: 400
  },
  height: {
    type: Number,
    default: 200
  },
  color: {
    type: String,
    default: '#3b82f6'
  },
  strokeWidth: {
    type: Number,
    default: 2
  },
  showGrid: {
    type: Boolean,
    default: true
  },
  showPoints: {
    type: Boolean,
    default: false
  },
  animated: {
    type: Boolean,
    default: true
  },
  valueFormatter: {
    type: Function,
    default: (value) => value.toString()
  }
})

const chartCanvas = ref(null)
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  value: 0
})

let animationFrame = null
let currentProgress = 0

const drawChart = () => {
  if (!chartCanvas.value) return
  
  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  const { width, height } = canvas
  
  // Limpar canvas
  ctx.clearRect(0, 0, width, height)
  
  if (!props.data || props.data.length === 0) return
  
  const padding = 40
  const chartWidth = width - padding * 2
  const chartHeight = height - padding * 2
  
  const maxValue = Math.max(...props.data)
  const minValue = Math.min(...props.data)
  const valueRange = maxValue - minValue || 1
  
  // Desenhar grid
  if (props.showGrid) {
    drawGrid(ctx, padding, chartWidth, chartHeight)
  }
  
  // Calcular pontos
  const points = props.data.map((value, index) => ({
    x: padding + (index / (props.data.length - 1)) * chartWidth,
    y: padding + chartHeight - ((value - minValue) / valueRange) * chartHeight
  }))
  
  // Desenhar linha
  drawLine(ctx, points)
  
  // Desenhar pontos
  if (props.showPoints) {
    drawPoints(ctx, points)
  }
}

const drawGrid = (ctx, padding, chartWidth, chartHeight) => {
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1
  
  // Linhas horizontais
  for (let i = 0; i <= 5; i++) {
    const y = padding + (i / 5) * chartHeight
    ctx.beginPath()
    ctx.moveTo(padding, y)
    ctx.lineTo(padding + chartWidth, y)
    ctx.stroke()
  }
  
  // Linhas verticais
  const verticalLines = Math.min(props.data.length, 10)
  for (let i = 0; i <= verticalLines; i++) {
    const x = padding + (i / verticalLines) * chartWidth
    ctx.beginPath()
    ctx.moveTo(x, padding)
    ctx.lineTo(x, padding + chartHeight)
    ctx.stroke()
  }
}

const drawLine = (ctx, points) => {
  if (points.length < 2) return
  
  ctx.strokeStyle = props.color
  ctx.lineWidth = props.strokeWidth
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  
  ctx.beginPath()
  
  // Usar progresso da animação se animado
  const progress = props.animated ? currentProgress : 1
  const visiblePoints = Math.floor(points.length * progress)
  
  if (visiblePoints < 2) return
  
  ctx.moveTo(points[0].x, points[0].y)
  
  for (let i = 1; i < visiblePoints; i++) {
    ctx.lineTo(points[i].x, points[i].y)
  }
  
  ctx.stroke()
}

const drawPoints = (ctx, points) => {
  ctx.fillStyle = props.color
  
  const progress = props.animated ? currentProgress : 1
  const visiblePoints = Math.floor(points.length * progress)
  
  for (let i = 0; i < visiblePoints; i++) {
    ctx.beginPath()
    ctx.arc(points[i].x, points[i].y, 4, 0, 2 * Math.PI)
    ctx.fill()
  }
}

const animate = () => {
  if (!props.animated) {
    currentProgress = 1
    drawChart()
    return
  }
  
  currentProgress += 0.02
  
  if (currentProgress >= 1) {
    currentProgress = 1
    drawChart()
    return
  }
  
  drawChart()
  animationFrame = requestAnimationFrame(animate)
}

const handleMouseMove = (event) => {
  if (!chartCanvas.value || !props.data.length) return
  
  const canvas = chartCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  const padding = 40
  const chartWidth = canvas.width - padding * 2
  
  // Encontrar o ponto mais próximo
  const relativeX = (x - padding) / chartWidth
  const index = Math.round(relativeX * (props.data.length - 1))
  
  if (index >= 0 && index < props.data.length) {
    tooltip.value = {
      visible: true,
      x: event.clientX,
      y: event.clientY - 10,
      label: props.labels[index] || `Ponto ${index + 1}`,
      value: props.data[index]
    }
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

const formatValue = (value) => {
  return props.valueFormatter(value)
}

const redraw = () => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  currentProgress = 0
  nextTick(() => {
    animate()
  })
}

// Watchers
watch(() => props.data, redraw, { deep: true })
watch(() => [props.width, props.height], redraw)

onMounted(() => {
  animate()
})
</script>

<style scoped>
.line-chart {
  position: relative;
  display: inline-block;
}

.chart-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  transform: translateX(-50%);
}

.tooltip-content {
  text-align: center;
}

.tooltip-label {
  font-weight: 500;
  margin-bottom: 2px;
}

.tooltip-value {
  font-size: 14px;
  font-weight: 600;
}

canvas {
  border-radius: 8px;
  cursor: crosshair;
}
</style>