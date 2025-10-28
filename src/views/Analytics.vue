<template>
  <div class="analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Analytics</h1>
          <p>Análise detalhada dos ativos e tendências</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline" @click="refreshData">
            <i class="fas fa-sync-alt"></i>
            Atualizar
          </button>
          <button class="btn btn-primary">
            <i class="fas fa-download"></i>
            Exportar Relatório
          </button>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-section">
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="fas fa-chart-line text-blue-500"></i>
          </div>
          <div class="kpi-content">
            <h3>{{ totalAssets }}</h3>
            <p>Total de Ativos</p>
            <span class="kpi-trend positive">
              <i class="fas fa-arrow-up"></i>
              +12% este mês
            </span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="fas fa-dollar-sign text-green-500"></i>
          </div>
          <div class="kpi-content">
            <h3>{{ formatCurrency(totalValue) }}</h3>
            <p>Valor Total</p>
            <span class="kpi-trend positive">
              <i class="fas fa-arrow-up"></i>
              +8% este mês
            </span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="fas fa-tools text-orange-500"></i>
          </div>
          <div class="kpi-content">
            <h3>{{ maintenanceCount }}</h3>
            <p>Em Manutenção</p>
            <span class="kpi-trend negative">
              <i class="fas fa-arrow-down"></i>
              -5% este mês
            </span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="fas fa-percentage text-purple-500"></i>
          </div>
          <div class="kpi-content">
            <h3>{{ utilizationRate }}%</h3>
            <p>Taxa de Utilização</p>
            <span class="kpi-trend positive">
              <i class="fas fa-arrow-up"></i>
              +3% este mês
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="charts-grid">
        <!-- Tendências Mensais -->
        <div class="chart-container full-width">
          <SimpleLineChart
            title="Tendências Mensais de Ativos"
            :datasets="trendsData"
            :labels="trendsLabels"
            :width="800"
            :height="300"
            :show-legend="true"
            :show-grid="true"
          />
        </div>

        <!-- Performance da Máquina -->
        <div class="chart-container full-width">
          <div class="chart-header" style="display:flex; justify-content:space-between; align-items:center; padding:16px;">
            <h3>Performance da Máquina</h3>
            <select v-model="selectedMachineId" class="select">
              <option v-for="m in machinesStore.machines" :key="m.id" :value="m.id">
                {{ m.name || m.hostname || m.id }}
              </option>
            </select>
          </div>
          <SimpleLineChart
            title="CPU ao longo do tempo"
            :datasets="machineCpuDataset"
            :labels="machineTimeseriesLabels"
            :width="800"
            :height="300"
            :show-legend="true"
            :show-grid="true"
          />
        </div>

        <!-- Status Distribution -->
        <div class="chart-container">
          <SimplePieChart
            title="Distribuição por Status"
            :data="statusData"
            :size="300"
            :donut="true"
            :show-center-text="true"
            :show-legend="true"
          />
        </div>

        <!-- Categorias -->
        <div class="chart-container">
          <SimpleBarChart
            title="Ativos por Categoria"
            :datasets="categoryData"
            :labels="categoryLabels"
            :width="400"
            :height="300"
            :show-legend="true"
            :show-grid="true"
          />
        </div>

        <!-- Departamentos -->
        <div class="chart-container">
          <SimpleBarChart
            title="Ativos por Departamento"
            :datasets="departmentData"
            :labels="departmentLabels"
            :width="400"
            :height="300"
            :show-legend="true"
            :show-grid="true"
            horizontal
          />
        </div>

        <!-- Valor por Categoria -->
        <div class="chart-container">
          <SimplePieChart
            title="Valor por Categoria"
            :data="valueByCategory"
            :size="300"
            :donut="false"
            :show-legend="true"
          />
        </div>

        <!-- Depreciação -->
        <div class="chart-container">
          <SimpleLineChart
            title="Depreciação Acumulada"
            :datasets="depreciationData"
            :labels="depreciationLabels"
            :width="400"
            :height="300"
            :show-legend="true"
            :show-grid="true"
          />
        </div>
      </div>
    </div>

    <!-- Summary Tables -->
    <div class="summary-section">
      <div class="summary-grid">
        <div class="summary-card">
          <h3>Top 5 Categorias</h3>
          <div class="summary-list">
            <div v-for="(category, index) in topCategories" :key="index" class="summary-item">
              <span class="summary-label">{{ category.name }}</span>
              <span class="summary-value">{{ category.count }} ativos</span>
            </div>
          </div>
        </div>

        <div class="summary-card">
          <h3>Alertas Importantes</h3>
          <div class="summary-list">
            <div class="summary-item alert">
              <i class="fas fa-exclamation-triangle text-red-500"></i>
              <span class="summary-label">Garantias Expiradas</span>
              <span class="summary-value">{{ expiredWarranties }}</span>
            </div>
            <div class="summary-item warning">
              <i class="fas fa-clock text-orange-500"></i>
              <span class="summary-label">Manutenção Próxima</span>
              <span class="summary-value">{{ nearingMaintenance }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted, watch } from 'vue'
import { useAssetsStore } from '@/stores/assets'
import { useDashboardStore } from '@/stores/dashboard'
import { useMachinesStore } from '@/stores/machines'
import { cachedAPI } from '@/services/api'
import SimpleLineChart from '@/components/charts/SimpleLineChart.vue'
import SimplePieChart from '@/components/charts/SimplePieChart.vue'
import SimpleBarChart from '@/components/charts/SimpleBarChart.vue'

// Stores
const assetsStore = useAssetsStore()
const dashboardStore = useDashboardStore()
const machinesStore = useMachinesStore()

// Analytics state
const analyticsOverview = ref(null)
const topCpu = ref([])
const selectedMachineId = ref(null)
const machineTimeseries = ref({ timestamps: [], cpu: [] })
const loadingAnalytics = ref(false)
const analyticsError = ref(null)

const machineTimeseriesLabels = computed(() => machineTimeseries.value?.timestamps || [])
const machineCpuDataset = computed(() => [{
  label: 'CPU (%)',
  data: machineTimeseries.value?.cpu || [],
  color: '#ef4444'
}])

const fetchAnalyticsOverview = async () => {
  loadingAnalytics.value = true
  try {
    const response = await cachedAPI.analytics.getOverview()
    analyticsOverview.value = response.data
  } catch (e) {
    analyticsError.value = 'Falha ao carregar overview'
  } finally {
    loadingAnalytics.value = false
  }
}

const fetchTopCpu = async () => {
  try {
    const response = await cachedAPI.analytics.getTopCpu({ limit: 5 })
    topCpu.value = response.data?.machines || response.data || []
  } catch (e) {}
}

const fetchMachineTimeseries = async (id) => {
  if (!id) return
  try {
    const response = await cachedAPI.analytics.getMachineTimeseries(id, { metric: 'cpu', window: '1h', interval: '1m' })
    machineTimeseries.value = response.data || { timestamps: [], cpu: [] }
  } catch (e) {}
}

watch(selectedMachineId, (id) => {
  fetchMachineTimeseries(id)
})

// Computed properties
const totalAssets = computed(() => assetsStore.totalAssets || 0)
const totalValue = computed(() => assetsStore.totalValue || 0)
const maintenanceCount = computed(() => assetsStore.maintenanceAssets?.length || 0)
const utilizationRate = computed(() => {
  const active = assetsStore.activeAssets?.length || 0
  const total = totalAssets.value
  return total > 0 ? Math.round((active / total) * 100) : 0
})

const expiredWarranties = computed(() => assetsStore.expiredWarranties?.length || 0)
const nearingMaintenance = computed(() => assetsStore.assetsNearingMaintenance?.length || 0)

// Chart data
const trendsData = computed(() => [
  {
    label: 'Ativos Totais',
    data: [120, 135, 142, 158, 165, 172, 180, 185, 192, 198, 205, 210],
    color: '#3b82f6'
  },
  {
    label: 'Ativos Ativos',
    data: [100, 115, 125, 140, 148, 155, 162, 168, 175, 182, 188, 195],
    color: '#10b981'
  },
  {
    label: 'Em Manutenção',
    data: [15, 12, 10, 8, 9, 7, 8, 6, 7, 5, 6, 4],
    color: '#f59e0b'
  }
])

const trendsLabels = computed(() => [
  'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
  'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
])

const statusData = computed(() => {
  const statusCounts = assetsStore.assetsByStatus || {}
  return [
    { label: 'Ativo', value: statusCounts.ativo || 195, color: '#10b981' },
    { label: 'Inativo', value: statusCounts.inativo || 8, color: '#6b7280' },
    { label: 'Manutenção', value: statusCounts.manutencao || 4, color: '#f59e0b' },
    { label: 'Descartado', value: statusCounts.descartado || 3, color: '#ef4444' }
  ].filter(item => item.value > 0)
})

const categoryData = computed(() => {
  const categoryCounts = assetsStore.assetsByCategory || {
    'Computadores': 45,
    'Móveis': 38,
    'Equipamentos': 32,
    'Veículos': 28,
    'Ferramentas': 25,
    'Outros': 22
  }
  return [{
    label: 'Quantidade',
    data: Object.values(categoryCounts),
    color: '#3b82f6'
  }]
})

const categoryLabels = computed(() => {
  const categoryCounts = assetsStore.assetsByCategory || {
    'Computadores': 45,
    'Móveis': 38,
    'Equipamentos': 32,
    'Veículos': 28,
    'Ferramentas': 25,
    'Outros': 22
  }
  return Object.keys(categoryCounts)
})

const departmentData = computed(() => [{
  label: 'Ativos',
  data: [42, 38, 35, 28, 25, 22],
  color: '#8b5cf6'
}])

const departmentLabels = computed(() => [
  'TI', 'Administrativo', 'Produção', 'RH', 'Financeiro', 'Marketing'
])

const valueByCategory = computed(() => [
  { label: 'Computadores', value: 450000, color: '#3b82f6' },
  { label: 'Veículos', value: 380000, color: '#10b981' },
  { label: 'Equipamentos', value: 320000, color: '#f59e0b' },
  { label: 'Móveis', value: 180000, color: '#8b5cf6' },
  { label: 'Ferramentas', value: 120000, color: '#ef4444' },
  { label: 'Outros', value: 80000, color: '#6b7280' }
])

const depreciationData = computed(() => [{
  label: 'Depreciação Acumulada',
  data: [50000, 95000, 135000, 170000, 200000, 225000, 245000, 260000, 270000, 275000, 280000, 285000],
  color: '#ef4444'
}])

const depreciationLabels = computed(() => trendsLabels.value)

const topCategories = computed(() => [
  { name: 'Computadores', count: 45 },
  { name: 'Móveis', count: 38 },
  { name: 'Equipamentos', count: 32 },
  { name: 'Veículos', count: 28 },
  { name: 'Ferramentas', count: 25 }
])

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const refreshData = async () => {
  try {
    loadingAnalytics.value = true
    await Promise.all([
      assetsStore.fetchAssets(),
      dashboardStore.fetchDashboardData(),
      machinesStore.fetchMachines(),
      fetchAnalyticsOverview(),
      fetchTopCpu()
    ])
    if (!selectedMachineId.value && machinesStore.machines?.length) {
      selectedMachineId.value = machinesStore.machines[0].id
    }
    if (selectedMachineId.value) {
      await fetchMachineTimeseries(selectedMachineId.value)
    }
  } catch (e) {
    logger.error('Erro ao atualizar dados de analytics', e)
  } finally {
    loadingAnalytics.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
.analytics-page {
  padding: 24px;
  background-color: #f8fafc;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-text h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.header-text p {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-outline {
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background-color: #f9fafb;
}

.kpi-section {
  margin-bottom: 32px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.kpi-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9;
  font-size: 20px;
}

.kpi-content h3 {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.kpi-content p {
  color: #6b7280;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.kpi-trend {
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.kpi-trend.positive {
  color: #10b981;
}

.kpi-trend.negative {
  color: #ef4444;
}

.charts-section {
  margin-bottom: 32px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-container.full-width {
  grid-column: 1 / -1;
}

.summary-section {
  margin-bottom: 32px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.summary-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.summary-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 16px 0;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-item.alert,
.summary-item.warning {
  gap: 8px;
}

.summary-label {
  color: #374151;
  font-weight: 500;
}

.summary-value {
  color: #6b7280;
  font-weight: 600;
}

.text-blue-500 { color: #3b82f6; }
.text-green-500 { color: #10b981; }
.text-orange-500 { color: #f59e0b; }
.text-purple-500 { color: #8b5cf6; }
.text-red-500 { color: #ef4444; }

@media (max-width: 768px) {
  .analytics-page {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container.full-width {
    grid-column: 1;
  }
}
</style>