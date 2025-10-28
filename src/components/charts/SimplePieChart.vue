<template>
  <div class="simple-pie-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
    </div>
    
    <div class="chart-container">
      <div class="chart-content">
        <svg :width="size" :height="size" class="pie-svg">
          <!-- Pie slices -->
          <g class="pie-slices" :transform="`translate(${center}, ${center})`">
            <path
              v-for="(slice, index) in pieSlices"
              :key="index"
              :d="slice.path"
              :fill="slice.color"
              :stroke="strokeColor"
              :stroke-width="strokeWidth"
              class="pie-slice"
              @mouseover="showTooltip($event, slice)"
              @mouseout="hideTooltip"
            />
          </g>
          
          <!-- Center circle (for donut style) -->
          <circle
            v-if="donut"
            :cx="center"
            :cy="center"
            :r="innerRadius"
            :fill="centerFill"
            class="center-circle"
          />
          
          <!-- Center text -->
          <g v-if="showCenterText" class="center-text" :transform="`translate(${center}, ${center})`">
            <text
              y="-5"
              text-anchor="middle"
              dominant-baseline="middle"
              class="center-value"
            >
              {{ totalValue.toLocaleString() }}
            </text>
            <text
              y="15"
              text-anchor="middle"
              dominant-baseline="middle"
              class="center-label"
            >
              Total
            </text>
          </g>
        </svg>
        
        <!-- Legend -->
        <div class="chart-legend">
          <div
            v-for="(item, index) in data"
            :key="index"
            class="legend-item"
            @mouseover="highlightSlice(index)"
            @mouseout="unhighlightSlice"
          >
            <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
            <div class="legend-content">
              <div class="legend-label">{{ item.label }}</div>
              <div class="legend-value">
                {{ item.value.toLocaleString() }} ({{ getPercentage(item.value) }}%)
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Tooltip -->
      <div
        v-if="tooltip.visible"
        class="chart-tooltip"
        :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      >
        <div class="tooltip-title">{{ tooltip.label }}</div>
        <div class="tooltip-value">{{ tooltip.value }} ({{ tooltip.percentage }}%)</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Gráfico de Pizza'
  },
  data: {
    type: Array,
    required: true,
    validator: (data) => {
      return data.every(item => 
        item.label && 
        typeof item.value === 'number' &&
        item.color
      )
    }
  },
  size: {
    type: Number,
    default: 300
  },
  donut: {
    type: Boolean,
    default: false
  },
  showCenterText: {
    type: Boolean,
    default: false
  },
  strokeColor: {
    type: String,
    default: '#ffffff'
  },
  strokeWidth: {
    type: Number,
    default: 2
  },
  centerFill: {
    type: String,
    default: '#ffffff'
  }
})

// State
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  label: '',
  value: '',
  percentage: ''
})

const highlightedSlice = ref(-1)

// Computed properties
const center = computed(() => props.size / 2)
const radius = computed(() => (props.size / 2) - 10)
const innerRadius = computed(() => props.donut ? radius.value * 0.6 : 0)

const totalValue = computed(() => {
  return props.data.reduce((sum, item) => sum + item.value, 0)
})

const pieSlices = computed(() => {
  let currentAngle = -Math.PI / 2 // Start at top
  
  return props.data.map((item, index) => {
    const percentage = item.value / totalValue.value
    const sliceAngle = percentage * 2 * Math.PI
    
    const startAngle = currentAngle
    const endAngle = currentAngle + sliceAngle
    
    const x1 = Math.cos(startAngle) * radius.value
    const y1 = Math.sin(startAngle) * radius.value
    const x2 = Math.cos(endAngle) * radius.value
    const y2 = Math.sin(endAngle) * radius.value
    
    const largeArcFlag = sliceAngle > Math.PI ? 1 : 0
    
    let path
    if (props.donut) {
      const innerX1 = Math.cos(startAngle) * innerRadius.value
      const innerY1 = Math.sin(startAngle) * innerRadius.value
      const innerX2 = Math.cos(endAngle) * innerRadius.value
      const innerY2 = Math.sin(endAngle) * innerRadius.value
      
      path = [
        `M ${x1} ${y1}`,
        `A ${radius.value} ${radius.value} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
        `L ${innerX2} ${innerY2}`,
        `A ${innerRadius.value} ${innerRadius.value} 0 ${largeArcFlag} 0 ${innerX1} ${innerY1}`,
        'Z'
      ].join(' ')
    } else {
      path = [
        'M 0 0',
        `L ${x1} ${y1}`,
        `A ${radius.value} ${radius.value} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
        'Z'
      ].join(' ')
    }
    
    currentAngle = endAngle
    
    return {
      path,
      color: item.color,
      label: item.label,
      value: item.value,
      percentage: Math.round(percentage * 100),
      index
    }
  })
})

// Methods
const getPercentage = (value) => {
  return Math.round((value / totalValue.value) * 100)
}

const showTooltip = (event, slice) => {
  const rect = event.target.closest('.chart-container').getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: event.clientX - rect.left + 10,
    y: event.clientY - rect.top - 10,
    label: slice.label,
    value: slice.value.toLocaleString(),
    percentage: slice.percentage
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

const highlightSlice = (index) => {
  highlightedSlice.value = index
}

const unhighlightSlice = () => {
  highlightedSlice.value = -1
}
</script>

<style scoped>
.simple-pie-chart {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.chart-header {
  margin-bottom: var(--spacing-lg);
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  text-align: center;
}

.chart-container {
  position: relative;
}

.chart-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.pie-svg {
  flex-shrink: 0;
}

.pie-slice {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.pie-slice:hover {
  opacity: 0.8;
}

.center-value {
  font-size: 1.25rem;
  font-weight: 700;
  fill: var(--text-primary);
  font-family: inherit;
}

.center-label {
  font-size: 0.875rem;
  fill: var(--text-secondary);
  font-family: inherit;
}

.chart-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.legend-item:hover {
  background-color: var(--bg-secondary);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.legend-content {
  flex: 1;
}

.legend-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.legend-value {
  font-size: 0.75rem;
  color: var(--text-secondary);
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
  .chart-content {
    flex-direction: column;
    gap: var(--spacing-lg);
  }
  
  .chart-legend {
    width: 100%;
  }
}
</style>