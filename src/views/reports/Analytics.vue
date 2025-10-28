<template>
  <div class="analytics">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Analytics</h1>
        <p class="page-subtitle">Análises avançadas e indicadores de performance do sistema</p>
      </div>
      
      <div class="page-actions">
        <button 
          class="btn btn-outline"
          @click="exportAnalytics"
          :disabled="loading"
        >
          <i class="fas fa-download"></i>
          Exportar Dados
        </button>
        <button 
          class="btn btn-primary"
          @click="refreshData"
          :disabled="loading"
        >
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          Atualizar
        </button>
      </div>
    </div>

    <!-- Time Range Selector -->
    <div class="time-range-selector">
      <div class="time-range-buttons">
        <button 
          v-for="range in timeRanges" 
          :key="range.value"
          class="btn btn-sm"
          :class="{ 'btn-primary': selectedTimeRange === range.value, 'btn-outline': selectedTimeRange !== range.value }"
          @click="selectedTimeRange = range.value"
        >
          {{ range.label }}
        </button>
      </div>
      <div class="custom-date-range">
        <input 
          type="date" 
          v-model="customStartDate"
          class="form-input form-input-sm"
        >
        <span>até</span>
        <input 
          type="date" 
          v-model="customEndDate"
          class="form-input form-input-sm"
        >
        <button 
          class="btn btn-sm btn-outline"
          @click="applyCustomRange"
        >
          Aplicar
        </button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-section">
      <h2 class="section-title">Indicadores Principais</h2>
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon assets">
            <i class="fas fa-boxes"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatNumber(analyticsData.totalAssets) }}</div>
            <div class="kpi-label">Total de Ativos</div>
            <div class="kpi-change positive">
              <i class="fas fa-arrow-up"></i>
              +{{ analyticsData.assetsGrowth }}% este mês
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon value">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatCurrency(analyticsData.totalValue) }}</div>
            <div class="kpi-label">Valor Total</div>
            <div class="kpi-change positive">
              <i class="fas fa-arrow-up"></i>
              +{{ analyticsData.valueGrowth }}% este mês
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon utilization">
            <i class="fas fa-chart-pie"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ analyticsData.utilizationRate }}%</div>
            <div class="kpi-label">Taxa de Utilização</div>
            <div class="kpi-change negative">
              <i class="fas fa-arrow-down"></i>
              {{ analyticsData.utilizationChange }}% este mês
            </div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon maintenance">
            <i class="fas fa-tools"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ formatCurrency(analyticsData.maintenanceCosts) }}</div>
            <div class="kpi-label">Custos de Manutenção</div>
            <div class="kpi-change neutral">
              <i class="fas fa-minus"></i>
              {{ analyticsData.maintenanceChange }}% este mês
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="charts-grid">
        <!-- Assets Trend Chart -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Crescimento de Ativos</h3>
            <div class="chart-actions">
              <button class="btn btn-sm btn-outline" @click="exportChart('assets-trend')">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              <p>Gráfico de Crescimento de Ativos</p>
              <p>{{ analyticsData?.trends?.monthlyGrowth?.length || 0 }} pontos de dados</p>
            </div>
          </div>
        </div>

        <!-- Asset Categories Distribution -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Distribuição por Categoria</h3>
            <div class="chart-actions">
              <button class="btn btn-sm btn-outline" @click="exportChart('categories')">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              <p>Gráfico de Distribuição por Categoria</p>
              <p>{{ analyticsData?.categories?.length || 0 }} categorias</p>
            </div>
          </div>
        </div>

        <!-- Maintenance Costs -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Custos de Manutenção</h3>
            <div class="chart-actions">
              <button class="btn btn-sm btn-outline" @click="exportChart('maintenance')">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              <p>Gráfico de Custos de Manutenção</p>
              <p>{{ analyticsData?.maintenance?.costs?.length || 0 }} registros</p>
            </div>
          </div>
        </div>

        <!-- Asset Status -->
        <div class="chart-card">
          <div class="chart-header">
            <h3>Status dos Ativos</h3>
            <div class="chart-actions">
              <button class="btn btn-sm btn-outline" @click="exportChart('status')">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">
              <p>Gráfico de Status dos Ativos</p>
              <p>{{ analyticsData?.status?.length || 0 }} status</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Analytics -->
    <div class="detailed-analytics">
      <div class="analytics-grid">
        <!-- Top Assets by Value -->
        <div class="analytics-card">
          <h3>Ativos de Maior Valor</h3>
          <div class="analytics-list">
            <div 
              v-for="asset in analyticsData.topAssetsByValue" 
              :key="asset.id"
              class="analytics-item"
            >
              <div class="item-info">
                <div class="item-name">{{ asset.name }}</div>
                <div class="item-category">{{ asset.category }}</div>
              </div>
              <div class="item-value">{{ formatCurrency(asset.value) }}</div>
            </div>
          </div>
        </div>

        <!-- Most Used Assets -->
        <div class="analytics-card">
          <h3>Ativos Mais Utilizados</h3>
          <div class="analytics-list">
            <div 
              v-for="asset in analyticsData.mostUsedAssets" 
              :key="asset.id"
              class="analytics-item"
            >
              <div class="item-info">
                <div class="item-name">{{ asset.name }}</div>
                <div class="item-category">{{ asset.category }}</div>
              </div>
              <div class="item-usage">
                <div class="usage-bar">
                  <div 
                    class="usage-fill" 
                    :style="{ width: asset.usageRate + '%' }"
                  ></div>
                </div>
                <span>{{ asset.usageRate }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Maintenance Alerts -->
        <div class="analytics-card">
          <h3>Alertas de Manutenção</h3>
          <div class="analytics-list">
            <div 
              v-for="alert in analyticsData.maintenanceAlerts" 
              :key="alert.id"
              class="analytics-item alert-item"
              :class="alert.priority"
            >
              <div class="alert-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="item-info">
                <div class="item-name">{{ alert.asset }}</div>
                <div class="item-category">{{ alert.type }}</div>
              </div>
              <div class="alert-date">{{ formatDate(alert.dueDate) }}</div>
            </div>
          </div>
        </div>

        <!-- Financial Summary -->
        <div class="analytics-card">
          <h3>Resumo Financeiro</h3>
          <div class="financial-metrics">
            <div class="metric">
              <div class="metric-label">Valor Total dos Ativos</div>
              <div class="metric-value">{{ formatCurrency(analyticsData.financialSummary.totalValue) }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">Depreciação Acumulada</div>
              <div class="metric-value negative">{{ formatCurrency(analyticsData.financialSummary.depreciation) }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">Valor Líquido</div>
              <div class="metric-value">{{ formatCurrency(analyticsData.financialSummary.netValue) }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">ROI Médio</div>
              <div class="metric-value">{{ analyticsData.financialSummary.averageROI }}%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted, nextTick } from 'vue'
import { useReportsStore } from '@/stores/reports'
// import { LineChart, PieChart, BarChart } from '@/components/charts'

const reportsStore = useReportsStore()

// Estado local
const loading = ref(false)
const selectedTimeRange = ref('last-30-days')
const customStartDate = ref('')
const customEndDate = ref('')

// Referências dos canvas para os gráficos
const assetsTrendChart = ref(null)
const categoriesChart = ref(null)
const maintenanceChart = ref(null)
const statusChart = ref(null)

// Opções de período
const timeRanges = [
  { value: 'last-7-days', label: '7 dias' },
  { value: 'last-30-days', label: '30 dias' },
  { value: 'last-90-days', label: '90 dias' },
  { value: 'last-year', label: '1 ano' },
  { value: 'custom', label: 'Personalizado' }
]

// Dados de analytics do store
const analyticsData = computed(() => reportsStore.analyticsData)

// Métodos
const refreshData = async () => {
  loading.value = true
  try {
    // Simular carregamento de dados
    await new Promise(resolve => setTimeout(resolve, 1000))
    await initializeCharts()
  } finally {
    loading.value = false
  }
}

const exportAnalytics = () => {
  const data = {
    period: selectedTimeRange.value,
    kpis: analyticsData.value,
    exportedAt: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analytics-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const exportChart = (chartType) => {
  logger.debug(`Exportando gráfico: ${chartType}`)
  // Implementar exportação específica do gráfico
}

const applyCustomRange = () => {
  if (customStartDate.value && customEndDate.value) {
    selectedTimeRange.value = 'custom'
    // Aplicar filtro personalizado
  }
}

const formatNumber = (value) => {
  return new Intl.NumberFormat('pt-BR').format(value)
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('pt-BR')
}

// Inicialização dos gráficos (simulado)
const initializeCharts = async () => {
  await nextTick()
  
  // Simular criação de gráficos
  if (assetsTrendChart.value) {
    const ctx = assetsTrendChart.value.getContext('2d')
    drawLineChart(ctx, analyticsData.value.assetsTrend)
  }
  
  if (categoriesChart.value) {
    const ctx = categoriesChart.value.getContext('2d')
    drawPieChart(ctx, analyticsData.value.categoriesData)
  }
  
  if (maintenanceChart.value) {
    const ctx = maintenanceChart.value.getContext('2d')
    drawBarChart(ctx, analyticsData.value.maintenanceData)
  }
  
  if (statusChart.value) {
    const ctx = statusChart.value.getContext('2d')
    drawDoughnutChart(ctx, analyticsData.value.statusData)
  }
}

const updateCharts = () => {
  // Os gráficos são atualizados automaticamente pelos componentes
  logger.debug('Gráficos atualizados')
}

onMounted(() => {
  // Os componentes de gráficos se inicializam automaticamente
  logger.debug('Analytics view montada')
})
</script>

<style scoped>
.analytics {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.page-header-content h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.page-header-content p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.page-actions {
  display: flex;
  gap: var(--spacing-md);
}

.content-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--success-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin-bottom: var(--spacing-lg);
}

.content-placeholder h3 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.content-placeholder p {
  color: var(--text-muted);
  max-width: 400px;
}
</style>