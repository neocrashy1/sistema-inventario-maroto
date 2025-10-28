<template>
  <div class="simple-line-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-legend">
        <div v-for="dataset in datasets" :key="dataset.label" class="legend-item">
          <div class="legend-color" :style="{ backgroundColor: dataset.color }"></div>
          <span class="legend-label">{{ dataset.label }}</span>
        </div>
      </div>
    </div>
    
    <div class="chart-container" ref="chartContainer">
      <svg :width="chartWidth" :height="chartHeight" class="chart-svg">
        <!-- Grid lines -->
        <g class="grid">
          <!-- Horizontal grid lines -->
          <line
            v-for="(line, index) in horizontalGridLines"
            :key="`h-${index}`"
            :x1="padding.left"
            :y1="line.y"
            :x2="chartWidth - padding.right"
            :y2="line.y"
            class="grid-line"
          />
          <!-- Vertical grid lines -->
          <line
            v-for="(line, index) in verticalGridLines"
            :key="`v-${index}`"
            :x1="line.x"
            :y1="padding.top"
            :x2="line.x"
            :y2="chartHeight - padding.bottom"
            class="grid-line"
          />
        </g>
        
        <!-- Data lines -->
        <g class="data-lines">
          <path
            v-for="dataset in datasets"
            :key="dataset.label"
            :d="getLinePath(dataset.data)"
            :stroke="dataset.color"
            :stroke-width="dataset.strokeWidth || 2"
            fill="none"
            class="data-line"
          />
        </g>
        
        <!-- Data points -->
        <g class="data-points">
          <circle
            v-for="(point, pointIndex) in allDataPoints"
            :key="`${point.datasetIndex}-${pointIndex}`"
            :cx="point.x"
            :cy="point.y"
            :r="point.radius || 4"
            :fill="point.color"
            class="data-point"
            @mouseover="showTooltip($event, point)"
            @mouseout="hideTooltip"
          />
        </g>
        
        <!-- Axes -->
        <g class="axes">
          <!-- X-axis -->
          <line
            :x1="padding.left"
            :y1="chartHeight - padding.bottom"
            :x2="chartWidth - padding.right"
            :y2="chartHeight - padding.bottom"
            class="axis-line"
          />
          <!-- Y-axis -->
          <line
            :x1="padding.left"
            :y1="padding.top"
            :x2="padding.left"
            :y2="chartHeight - padding.bottom"
            class="axis-line"
          />
        </g>
        
        <!-- Axis labels -->
        <g class="axis-labels">
          <!-- X-axis labels -->
          <text
            v-for="(label, index) in xAxisLabels"
            :key="`x-${index}`"
            :x="label.x"
            :y="chartHeight - padding.bottom + 20"
            class="axis-label"
            text-anchor="middle"
          >
            {{ label.text }}
          </text>
          <!-- Y-axis labels -->
          <text
            v-for="(label, index) in yAxisLabels"
            :key="`y-${index}`"
            :x="padding.left - 10"
            :y="label.y"
            class="axis-label"
            text-anchor="end"
            dominant-baseline="middle"
          >
            {{ label.text }}
          </text>
        </g>
      </svg>
      
      <!-- Tooltip -->
      <div
        v-if="tooltip.visible"
        class="chart-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        <div class="tooltip-title">{{ tooltip.label }}</div>
        <div class="tooltip-value">{{ tooltip.value }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Gráfico de Linha'
  },
  datasets: {
    type: Array,
    required: true,
    validator: (datasets) => {
      return datasets.every(dataset => 
        dataset.label && 
        dataset.data && 
        Array.isArray(dataset.data) &&
        dataset.color
      )
    }
  },
  labels: {
    type: Array,
    required: true
  },
  width: {
    type: Number,
    default: 600
  },
  height: {
    type: Number,
    default: 300
  }
})

// Refs
const chartContainer = ref(null)

// State
const chartWidth = ref(props.width)
const chartHeight = ref(props.height)
const padding = ref({
  top: 20,
  right: 20,
  bottom: 40,
  left: 60
})

const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  value: ''
})

// Computed properties
const dataRange = computed(() => {
  const allValues = props.datasets.flatMap(dataset => dataset.data)
  return {
    min: Math.min(...allValues),
    max: Math.max(...allValues)
  }
})

const xScale = computed(() => {
  const availableWidth = chartWidth.value - padding.value.left - padding.value.right
  return availableWidth / (props.labels.length - 1)
})

const yScale = computed(() => {
  const availableHeight = chartHeight.value - padding.value.top - padding.value.bottom
  const range = dataRange.value.max - dataRange.value.min
  return availableHeight / range
})

const horizontalGridLines = computed(() => {
  const lines = []
  const steps = 5
  const stepValue = (dataRange.value.max - dataRange.value.min) / steps
  
  for (let i = 0; i <= steps; i++) {
    const value = dataRange.value.min + (stepValue * i)
    const y = chartHeight.value - padding.value.bottom - ((value - dataRange.value.min) * yScale.value)
    lines.push({ y, value })
  }
  
  return lines
})

const verticalGridLines = computed(() => {
  const lines = []
  
  props.labels.forEach((label, index) => {
    const x = padding.value.left + (index * xScale.value)
    lines.push({ x, label })
  })
  
  return lines
})

const xAxisLabels = computed(() => {
  return props.labels.map((label, index) => ({
    x: padding.value.left + (index * xScale.value),
    text: label
  }))
})

const yAxisLabels = computed(() => {
  return horizontalGridLines.value.map(line => ({
    y: line.y,
    text: Math.round(line.value).toLocaleString()
  }))
})

const allDataPoints = computed(() => {
  const points = []
  
  props.datasets.forEach((dataset, datasetIndex) => {
    dataset.data.forEach((value, pointIndex) => {
      const x = padding.value.left + (pointIndex * xScale.value)
      const y = chartHeight.value - padding.value.bottom - ((value - dataRange.value.min) * yScale.value)
      
      points.push({
        x,
        y,
        value,
        label: props.labels[pointIndex],
        color: dataset.color,
        datasetIndex,
        pointIndex,
        datasetLabel: dataset.label
      })
    })
  })
  
  return points
})

// Methods
const getLinePath = (data) => {
  let path = ''
  
  data.forEach((value, index) => {
    const x = padding.value.left + (index * xScale.value)
    const y = chartHeight.value - padding.value.bottom - ((value - dataRange.value.min) * yScale.value)
    
    if (index === 0) {
      path += `M ${x} ${y}`
    } else {
      path += ` L ${x} ${y}`
    }
  })
  
  return path
}

const showTooltip = (event, point) => {
  const rect = chartContainer.value.getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: event.clientX - rect.left + 10,
    y: event.clientY - rect.top - 10,
    label: `${point.datasetLabel} - ${point.label}`,
    value: point.value.toLocaleString()
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

const handleResize = () => {
  if (chartContainer.value) {
    const rect = chartContainer.value.getBoundingClientRect()
    chartWidth.value = Math.max(300, rect.width)
  }
}

// Lifecycle
onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.simple-line-chart {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: var(--spacing-md);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.chart-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.chart-svg {
  width: 100%;
  height: auto;
}

.grid-line {
  stroke: var(--border-light);
  stroke-width: 1;
}

.axis-line {
  stroke: var(--border-dark);
  stroke-width: 2;
}

.axis-label {
  font-size: 0.75rem;
  fill: var(--text-secondary);
  font-family: inherit;
}

.data-line {
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.data-point {
  cursor: pointer;
  transition: r 0.2s ease;
}

.data-point:hover {
  r: 6;
}

.chart-tooltip {
  position: absolute;
  background-color: var(--bg-dark);
  color: white;
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  font-size: 0.75rem;
  pointer-events: none;
  z-index: 1000;
  box-shadow: var(--shadow-lg);
}

.tooltip-title {
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

.tooltip-value {
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .chart-legend {
    flex-wrap: wrap;
  }
}
</style>