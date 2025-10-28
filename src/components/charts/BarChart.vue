<template>
  <div class="bar-chart">
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
  colors: {
    type: Array,
    default: () => []
  },
  showGrid: {
    type: Boolean,
    default: true
  },
  showLabels: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: true
  },
  horizontal: {
    type: Boolean,
    default: false
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
let bars = []

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
  
  const maxValue = Math.max(...props.data.map(d => d.value))
  const minValue = Math.min(0, Math.min(...props.data.map(d => d.value)))
  const valueRange = maxValue - minValue || 1
  
  // Desenhar grid
  if (props.showGrid) {
    drawGrid(ctx, padding, chartWidth, chartHeight, maxValue, minValue)
  }
  
  // Desenhar barras
  if (props.horizontal) {
    drawHorizontalBars(ctx, padding, chartWidth, chartHeight, maxValue, minValue, valueRange)
  } else {
    drawVerticalBars(ctx, padding, chartWidth, chartHeight, maxValue, minValue, valueRange)
  }
  
  // Desenhar labels
  if (props.showLabels) {
    drawLabels(ctx, padding, chartWidth, chartHeight)
  }
}

const drawGrid = (ctx, padding, chartWidth, chartHeight, maxValue, minValue) => {
  ctx.strokeStyle = '#e5e7eb'
  ctx.lineWidth = 1
  
  if (props.horizontal) {
    // Linhas verticais para gráfico horizontal
    for (let i = 0; i <= 5; i++) {
      const x = padding + (i / 5) * chartWidth
      ctx.beginPath()
      ctx.moveTo(x, padding)
      ctx.lineTo(x, padding + chartHeight)
      ctx.stroke()
    }
  } else {
    // Linhas horizontais para gráfico vertical
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i / 5) * chartHeight
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(padding + chartWidth, y)
      ctx.stroke()
    }
  }
}

const drawVerticalBars = (ctx, padding, chartWidth, chartHeight, maxValue, minValue, valueRange) => {
  const barWidth = chartWidth / props.data.length
  const barSpacing = barWidth * 0.1
  const actualBarWidth = barWidth - barSpacing
  
  bars = []
  
  props.data.forEach((item, index) => {
    const barHeight = Math.abs(item.value - minValue) / valueRange * chartHeight
    const x = padding + index * barWidth + barSpacing / 2
    const y = padding + chartHeight - barHeight
    
    // Aplicar progresso da animação
    const progress = props.animated ? currentProgress : 1
    const animatedHeight = barHeight * progress
    const animatedY = padding + chartHeight - animatedHeight
    
    // Cor da barra
    const barColor = props.colors.length > 0 
      ? props.colors[index % props.colors.length] 
      : props.color
    
    ctx.fillStyle = barColor
    ctx.fillRect(x, animatedY, actualBarWidth, animatedHeight)
    
    // Armazenar informações da barra
    bars.push({
      x,
      y,
      width: actualBarWidth,
      height: barHeight,
      data: item,
      index
    })
  })
}

const drawHorizontalBars = (ctx, padding, chartWidth, chartHeight, maxValue, minValue, valueRange) => {
  const barHeight = chartHeight / props.data.length
  const barSpacing = barHeight * 0.1
  const actualBarHeight = barHeight - barSpacing
  
  bars = []
  
  props.data.forEach((item, index) => {
    const barWidth = Math.abs(item.value - minValue) / valueRange * chartWidth
    const x = padding
    const y = padding + index * barHeight + barSpacing / 2
    
    // Aplicar progresso da animação
    const progress = props.animated ? currentProgress : 1
    const animatedWidth = barWidth * progress
    
    // Cor da barra
    const barColor = props.colors.length > 0 
      ? props.colors[index % props.colors.length] 
      : props.color
    
    ctx.fillStyle = barColor
    ctx.fillRect(x, y, animatedWidth, actualBarHeight)
    
    // Armazenar informações da barra
    bars.push({
      x,
      y,
      width: barWidth,
      height: actualBarHeight,
      data: item,
      index
    })
  })
}

const drawLabels = (ctx, padding, chartWidth, chartHeight) => {
  ctx.fillStyle = '#6b7280'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  
  if (props.horizontal) {
    // Labels para gráfico horizontal
    props.data.forEach((item, index) => {
      const barHeight = chartHeight / props.data.length
      const y = padding + index * barHeight + barHeight / 2
      
      ctx.textAlign = 'right'
      ctx.fillText(item.label, padding - 10, y + 4)
    })
  } else {
    // Labels para gráfico vertical
    props.data.forEach((item, index) => {
      const barWidth = chartWidth / props.data.length
      const x = padding + index * barWidth + barWidth / 2
      
      ctx.textAlign = 'center'
      ctx.fillText(item.label, x, padding + chartHeight + 20)
    })
  }
}

const animate = () => {
  if (!props.animated) {
    currentProgress = 1
    drawChart()
    return
  }
  
  currentProgress += 0.03
  
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
  
  // Encontrar barra sob o cursor
  const hoveredBar = bars.find(bar => {
    return x >= bar.x && 
           x <= bar.x + bar.width && 
           y >= bar.y && 
           y <= bar.y + bar.height
  })
  
  if (hoveredBar) {
    tooltip.value = {
      visible: true,
      x: event.clientX,
      y: event.clientY - 10,
      label: hoveredBar.data.label,
      value: hoveredBar.data.value
    }
  } else {
    hideTooltip()
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
.bar-chart {
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
  cursor: pointer;
}
</style>