// Exportar todos os componentes de gráficos
export { default as LineChart } from './LineChart.vue'
export { default as PieChart } from './PieChart.vue'
export { default as BarChart } from './BarChart.vue'

// Função utilitária para formatar valores monetários
export const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

// Função utilitária para formatar números
export const formatNumber = (value) => {
  return new Intl.NumberFormat('pt-BR').format(value)
}

// Função utilitária para formatar percentuais
export const formatPercentage = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value / 100)
}

// Paleta de cores padrão para gráficos
export const defaultColors = [
  '#3b82f6', // Blue
  '#ef4444', // Red
  '#10b981', // Green
  '#f59e0b', // Yellow
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#06b6d4', // Cyan
  '#84cc16', // Lime
  '#f97316', // Orange
  '#6366f1'  // Indigo
]

// Configurações padrão para diferentes tipos de gráficos
export const chartDefaults = {
  line: {
    strokeWidth: 2,
    showGrid: true,
    showPoints: false,
    animated: true
  },
  bar: {
    showGrid: true,
    showLabels: true,
    animated: true,
    horizontal: false
  },
  pie: {
    showLegend: true,
    animated: true,
    innerRadius: 0
  }
}