<template>
  <div class="pie-chart">
    <canvas 
      ref="chartCanvas" 
      :width="size" 
      :height="size"
      @mousemove="handleMouseMove"
      @mouseleave="hideTooltip"
    ></canvas>
    
    <!-- Legend -->
    <div v-if="showLegend" class="chart-legend">
      <div 
        v-for="(item, index) in data" 
        :key="index"
        class="legend-item"
      >
        <div 
          class="legend-color" 
          :style="{ backgroundColor: getColor(index) }"
        ></div>
        <span class="legend-label">{{ item.label }}</span>
        <span class="legend-value">{{ formatValue(item.value) }}</span>
      </div>
    </div>
    
    <!-- Tooltip -->
    <div 
      v-if="tooltip.visible"
      class="chart-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-label">{{ tooltip.label }}</div>
        <div class="tooltip-value">{{ formatValue(tooltip.value) }}</div>
        <div class="tooltip-percentage">{{ tooltip.percentage }}%</div>
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
  size: {
    type: Number,
    default: 300
  },
  colors: {
    type: Array,
    default: () => ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  animated: {
    type: Boolean,
    default: true
  },
  innerRadius: {
    type: Number,
    default: 0
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
  value: 0,
  percentage: 0
})

let animationFrame = null
let currentProgress = 0
let slices = []

const drawChart = () => {
  if (!chartCanvas.value) return
  
  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  const { width, height } = canvas
  
  // Limpar canvas
  ctx.clearRect(0, 0, width, height)
  
  if (!props.data || props.data.length === 0) return
  
  const centerX = width / 2
  const centerY = height / 2
  const outerRadius = Math.min(centerX, centerY) - 20
  const innerRadius = props.innerRadius
  
  const total = props.data.reduce((sum, item) => sum + item.value, 0)
  let currentAngle = -Math.PI / 2 // Começar do topo
  
  slices = []
  
  props.data.forEach((item, index) => {
    const sliceAngle = (item.value / total) * 2 * Math.PI
    const endAngle = currentAngle + sliceAngle
    
    // Aplicar progresso da animação
    const progress = props.animated ? currentProgress : 1
    const animatedEndAngle = currentAngle + (sliceAngle * progress)
    
    if (progress > 0) {
      // Desenhar fatia
      ctx.fillStyle = getColor(index)
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, outerRadius, currentAngle, animatedEndAngle)
      
      if (innerRadius > 0) {
        ctx.arc(centerX, centerY, innerRadius, animatedEndAngle, currentAngle, true)
      }
      
      ctx.closePath()
      ctx.fill()
      
      // Adicionar borda
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.stroke()
    }
    
    // Armazenar informações da fatia para detecção de hover
    slices.push({
      startAngle: currentAngle,
      endAngle: endAngle,
      centerAngle: currentAngle + sliceAngle / 2,
      outerRadius,
      innerRadius,
      data: item,
      index
    })
    
    currentAngle = endAngle
  })
}

const getColor = (index) => {
  return props.colors[index % props.colors.length]
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
  
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  
  // Calcular distância e ângulo do centro
  const dx = x - centerX
  const dy = y - centerY
  const distance = Math.sqrt(dx * dx + dy * dy)
  const angle = Math.atan2(dy, dx) + Math.PI / 2
  
  // Normalizar ângulo para 0-2π
  const normalizedAngle = angle < 0 ? angle + 2 * Math.PI : angle
  
  // Encontrar fatia sob o cursor
  const hoveredSlice = slices.find(slice => {
    const inRadius = distance >= slice.innerRadius && distance <= slice.outerRadius
    const inAngle = normalizedAngle >= slice.startAngle && normalizedAngle <= slice.endAngle
    return inRadius && inAngle
  })
  
  if (hoveredSlice) {
    const total = props.data.reduce((sum, item) => sum + item.value, 0)
    const percentage = Math.round((hoveredSlice.data.value / total) * 100)
    
    tooltip.value = {
      visible: true,
      x: event.clientX,
      y: event.clientY - 10,
      label: hoveredSlice.data.label,
      value: hoveredSlice.data.value,
      percentage
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
watch(() => props.size, redraw)

onMounted(() => {
  animate()
})
</script>

<style scoped>
.pie-chart {
  display: flex;
  align-items: center;
  gap: 20px;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  color: var(--text-primary);
}

.legend-value {
  font-weight: 600;
  color: var(--text-secondary);
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

.tooltip-percentage {
  font-size: 12px;
  opacity: 0.8;
}

canvas {
  border-radius: 8px;
  cursor: pointer;
}
</style>