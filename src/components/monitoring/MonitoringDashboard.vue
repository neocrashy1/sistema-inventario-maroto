<template>
  <div class="monitoring-dashboard">
    <!-- Header do Dashboard -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-info">
          <h2 class="dashboard-title">
            <v-icon icon="mdi-monitor-dashboard" class="mr-2"></v-icon>
            Dashboard de Monitoramento
          </h2>
          <p class="dashboard-subtitle">
            Monitoramento em tempo real de {{ machines.length }} {{ machines.length === 1 ? 'máquina' : 'máquinas' }}
          </p>
        </div>
        
        <div class="header-actions">
           <v-btn
             variant="outlined"
             size="small"
             @click="toggleInventoryView"
             :color="showInventory ? 'info' : 'surface-variant'"
             class="mr-2"
           >
             <v-icon :icon="showInventory ? 'mdi-monitor-dashboard' : 'mdi-server-network'" class="mr-1"></v-icon>
             {{ showInventory ? 'Dashboard' : 'Inventário' }}
           </v-btn>
           
           <v-btn
             variant="outlined"
             size="small"
             @click="toggleAlertsView"
             :color="showAlerts ? 'error' : 'surface-variant'"
             class="mr-2"
           >
             <v-icon :icon="showAlerts ? 'mdi-monitor-dashboard' : 'mdi-alert-circle'" class="mr-1"></v-icon>
             {{ showAlerts ? 'Dashboard' : 'Alertas' }}
           </v-btn>
           
           <v-btn
             variant="outlined"
             size="small"
             @click="toggleTicketsView"
             :color="showTickets ? 'primary' : 'surface-variant'"
             class="mr-2"
           >
             <v-icon icon="mdi-ticket-confirmation" class="mr-1"></v-icon>
             {{ showTickets ? 'Dashboard' : 'Chamados' }}
           </v-btn>
           
           <v-btn
             variant="outlined"
             size="small"
             @click="togglePerformanceView"
             :color="showPerformance ? 'info' : 'surface-variant'"
             class="mr-2"
           >
             <v-icon icon="mdi-speedometer" class="mr-1"></v-icon>
             {{ showPerformance ? 'Dashboard' : 'Performance' }}
           </v-btn>
           
           <v-btn
             v-if="!showAlerts && !showInventory && !showTickets"
             variant="outlined"
             size="small"
             @click="toggleView"
             :color="showRealTimeCharts ? 'primary' : 'surface-variant'"
             class="mr-2"
           >
             <v-icon :icon="showRealTimeCharts ? 'mdi-view-grid' : 'mdi-chart-line'" class="mr-1"></v-icon>
             {{ showRealTimeCharts ? 'Cards' : 'Gráficos' }}
           </v-btn>
          
          <v-btn
            variant="outlined"
            size="small"
            @click="refreshAllData"
            :loading="isRefreshing"
            class="mr-2"
          >
            <v-icon icon="mdi-refresh" class="mr-1"></v-icon>
            Atualizar Tudo
          </v-btn>
          
          <v-btn
            variant="outlined"
            size="small"
            @click="toggleAutoRefresh"
            :color="autoRefresh ? 'success' : 'surface-variant'"
          >
            <v-icon :icon="autoRefresh ? 'mdi-pause' : 'mdi-play'" class="mr-1"></v-icon>
            {{ autoRefresh ? 'Pausar' : 'Auto Refresh' }}
          </v-btn>
        </div>
      </div>
      
      <!-- Status geral -->
      <div class="status-overview">
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <v-card variant="tonal" color="success">
              <v-card-text class="text-center">
                <v-icon icon="mdi-check-circle" size="large" class="mb-2"></v-icon>
                <div class="status-value">{{ healthyMachines }}</div>
                <div class="status-label">Saudáveis</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-card variant="tonal" color="warning">
              <v-card-text class="text-center">
                <v-icon icon="mdi-alert-circle" size="large" class="mb-2"></v-icon>
                <div class="status-value">{{ warningMachines }}</div>
                <div class="status-label">Atenção</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-card variant="tonal" color="error">
              <v-card-text class="text-center">
                <v-icon icon="mdi-alert" size="large" class="mb-2"></v-icon>
                <div class="status-value">{{ criticalMachines }}</div>
                <div class="status-label">Críticas</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6" md="3">
            <v-card variant="tonal" color="surface-variant">
              <v-card-text class="text-center">
                <v-icon icon="mdi-server-off" size="large" class="mb-2"></v-icon>
                <div class="status-value">{{ offlineMachines }}</div>
                <div class="status-label">Offline</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- Seletor de máquina -->
    <div class="machine-selector">
      <v-card>
        <v-card-text>
          <v-row align="center">
            <v-col cols="12" md="6">
              <v-select
                v-model="selectedMachine"
                :items="machineOptions"
                item-title="label"
                item-value="value"
                label="Selecionar Máquina"
                variant="outlined"
                density="compact"
                @update:model-value="onMachineChange"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-desktop-classic"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <div class="machine-info" v-if="currentMachineInfo">
                <div class="machine-details">
                  <div class="machine-name">{{ currentMachineInfo.hostname }}</div>
                  <div class="machine-meta">
                    <v-chip size="x-small" variant="outlined" class="mr-1">
                      {{ currentMachineInfo.os_name }}
                    </v-chip>
                    <v-chip size="x-small" variant="outlined" class="mr-1">
                      {{ currentMachineInfo.ip_address }}
                    </v-chip>
                    <v-chip 
                      :color="getMachineStatusColor(currentMachineInfo.status)"
                      size="x-small"
                      variant="flat"
                    >
                      {{ currentMachineInfo.status }}
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <!-- Sistema de Chamados -->
    <div v-if="showTickets">
      <TicketingSystem />
    </div>

    <!-- Sistema de Inventário -->
    <div v-else-if="showInventory">
      <InventorySystem />
    </div>

    <!-- Sistema de Alertas -->
    <div v-else-if="showAlerts">
      <AlertsSystem />
    </div>

    <!-- Dashboard de Performance -->
    <div v-else-if="showPerformance">
      <PerformanceDashboard 
        :auto-start="true"
        :show-history-chart="true"
        @alert="handlePerformanceAlert"
        @performance-change="handlePerformanceChange"
      />
    </div>

     <!-- Grid de métricas ou Gráficos em tempo real -->
     <div v-else-if="selectedMachine && currentMetrics">
       <!-- Visualização de Gráficos em Tempo Real -->
       <div v-if="showRealTimeCharts">
         <RealTimeMetricsDashboard />
       </div>
       
       <!-- Visualização de Cards (existente) -->
       <div v-else class="metrics-grid">
        <v-row>
          <!-- CPU Metrics -->
          <v-col cols="12" lg="6">
            <CpuMetricsCard
              :cpu-data="currentMetrics.cpu"
              :loading="isLoadingMetrics"
              @refresh="refreshCpuMetrics"
              @view-details="viewCpuDetails"
            />
          </v-col>

          <!-- Memory Metrics -->
          <v-col cols="12" lg="6">
            <MemoryMetricsCard
              :memory-data="currentMetrics.memory"
              :loading="isLoadingMetrics"
              @refresh="refreshMemoryMetrics"
              @view-details="viewMemoryDetails"
            />
          </v-col>

          <!-- Disk Metrics -->
          <v-col cols="12" lg="6">
            <DiskMetricsCard
              :disk-data="currentMetrics.disk"
              :io-stats="currentMetrics.disk_io"
              :loading="isLoadingMetrics"
              @refresh="refreshDiskMetrics"
              @cleanup="performDiskCleanup"
              @view-details="viewDiskDetails"
            />
          </v-col>

          <!-- Network Metrics -->
          <v-col cols="12" lg="6">
            <NetworkMetricsCard
              :network-data="currentMetrics.network"
              :activity-data="networkActivityData"
              :loading="isLoadingMetrics"
              @refresh="refreshNetworkMetrics"
              @test-connection="testNetworkConnection"
              @view-details="viewNetworkDetails"
            />
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- Estado vazio -->
    <div v-else-if="!selectedMachine" class="empty-state">
      <v-card>
        <v-card-text class="text-center py-12">
          <v-icon icon="mdi-monitor-dashboard" size="64" class="mb-4" color="surface-variant"></v-icon>
          <h3 class="text-h6 mb-2">Selecione uma máquina para monitorar</h3>
          <p class="text-body-2 text-medium-emphasis">
            Escolha uma máquina na lista acima para visualizar suas métricas em tempo real.
          </p>
        </v-card-text>
      </v-card>
    </div>

    <!-- Estado de carregamento -->
    <div v-else-if="isLoadingMetrics && !currentMetrics" class="loading-state">
      <v-card>
        <v-card-text class="text-center py-12">
          <v-progress-circular
            indeterminate
            size="64"
            class="mb-4"
          ></v-progress-circular>
          <h3 class="text-h6 mb-2">Carregando métricas...</h3>
          <p class="text-body-2 text-medium-emphasis">
            Coletando dados de monitoramento da máquina selecionada.
          </p>
        </v-card-text>
      </v-card>
    </div>

    <!-- Snackbar para notificações -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationColor"
      :timeout="3000"
      location="top right"
    >
      {{ notificationMessage }}
      <template #actions>
        <v-btn
          variant="text"
          @click="showNotification = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted, onUnmounted, watch, defineAsyncComponent } from 'vue'

// Lazy loading dos componentes de métricas
const CpuMetricsCard = defineAsyncComponent({
  loader: () => import('./CpuMetricsCard.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  delay: 100,
  timeout: 3000
})

const MemoryMetricsCard = defineAsyncComponent({
  loader: () => import('./MemoryMetricsCard.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  delay: 100,
  timeout: 3000
})

const DiskMetricsCard = defineAsyncComponent({
  loader: () => import('./DiskMetricsCard.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  delay: 100,
  timeout: 3000
})

const NetworkMetricsCard = defineAsyncComponent({
  loader: () => import('./NetworkMetricsCard.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  delay: 100,
  timeout: 3000
})

// Lazy loading dos componentes de dashboard e sistemas
const RealTimeMetricsDashboard = defineAsyncComponent({
  loader: () => import('./RealTimeMetricsDashboard.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  errorComponent: () => import('@/components/common/ErrorMessage.vue'),
  delay: 200,
  timeout: 5000
})

const AlertsSystem = defineAsyncComponent({
  loader: () => import('./AlertsSystem.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  errorComponent: () => import('@/components/common/ErrorMessage.vue'),
  delay: 200,
  timeout: 5000
})

const InventorySystem = defineAsyncComponent({
  loader: () => import('./InventorySystem.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  errorComponent: () => import('@/components/common/ErrorMessage.vue'),
  delay: 200,
  timeout: 5000
})

const TicketingSystem = defineAsyncComponent({
  loader: () => import('./TicketingSystem.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  errorComponent: () => import('@/components/common/ErrorMessage.vue'),
  delay: 200,
  timeout: 5000
})

const PerformanceDashboard = defineAsyncComponent({
  loader: () => import('@/components/performance/PerformanceDashboard.vue'),
  loadingComponent: () => import('@/components/common/LoadingSpinner.vue'),
  errorComponent: () => import('@/components/common/ErrorMessage.vue'),
  delay: 200,
  timeout: 5000
})

// Reactive data
const machines = ref([])
const selectedMachine = ref(null)
const currentMetrics = ref(null)
const networkActivityData = ref(Array(20).fill().map(() => ({ download: 0, upload: 0 })))
const isLoadingMetrics = ref(false)
const isRefreshing = ref(false)
const autoRefresh = ref(true)
const refreshInterval = ref(null)
const showRealTimeCharts = ref(false)
const showAlerts = ref(false)
const showInventory = ref(false)
const showTickets = ref(false)
const showPerformance = ref(false)

// Notification system
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationColor = ref('success')

// Computed properties
const machineOptions = computed(() => {
  return machines.value.map(machine => ({
    label: `${machine.hostname} (${machine.ip_address})`,
    value: machine.id
  }))
})

const currentMachineInfo = computed(() => {
  if (!selectedMachine.value) return null
  return machines.value.find(m => m.id === selectedMachine.value)
})

const healthyMachines = computed(() => {
  return machines.value.filter(m => m.status === 'online' && !hasHighUsage(m)).length
})

const warningMachines = computed(() => {
  return machines.value.filter(m => m.status === 'online' && hasHighUsage(m)).length
})

const criticalMachines = computed(() => {
  return machines.value.filter(m => m.status === 'critical').length
})

const offlineMachines = computed(() => {
  return machines.value.filter(m => m.status === 'offline').length
})

// Methods
const loadMachines = async () => {
  try {
    const response = await fetch('/api/v1/machine-monitoring/machines')
    if (response.ok) {
      machines.value = await response.json()
      
      // Seleciona a primeira máquina se não houver seleção
      if (machines.value.length > 0 && !selectedMachine.value) {
        selectedMachine.value = machines.value[0].id
      }
    }
  } catch (error) {
    showError('Erro ao carregar lista de máquinas')
    logger.error('Error loading machines:', error)
  }
}

const loadMachineMetrics = async (machineId) => {
  if (!machineId) return
  
  isLoadingMetrics.value = true
  
  try {
    const response = await fetch(`/api/v1/machine-monitoring/machines/${machineId}/metrics`)
    if (response.ok) {
      currentMetrics.value = await response.json()
      updateNetworkActivity()
    } else {
      showError('Erro ao carregar métricas da máquina')
    }
  } catch (error) {
    showError('Erro de conexão ao carregar métricas')
    logger.error('Error loading metrics:', error)
  } finally {
    isLoadingMetrics.value = false
  }
}

const updateNetworkActivity = () => {
  if (!currentMetrics.value?.network) return
  
  // Simula dados de atividade de rede (em um cenário real, viria da API)
  const newPoint = {
    download: currentMetrics.value.network.download_mbps || 0,
    upload: currentMetrics.value.network.upload_mbps || 0
  }
  
  networkActivityData.value = [
    ...networkActivityData.value.slice(1),
    newPoint
  ]
}

const refreshAllData = async () => {
  isRefreshing.value = true
  
  try {
    await loadMachines()
    if (selectedMachine.value) {
      await loadMachineMetrics(selectedMachine.value)
    }
    showSuccess('Dados atualizados com sucesso')
  } catch (error) {
    showError('Erro ao atualizar dados')
  } finally {
    isRefreshing.value = false
  }
}

const refreshCpuMetrics = () => {
  if (selectedMachine.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const refreshMemoryMetrics = () => {
  if (selectedMachine.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const refreshDiskMetrics = () => {
  if (selectedMachine.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const refreshNetworkMetrics = () => {
  if (selectedMachine.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const onMachineChange = (machineId) => {
  if (machineId) {
    loadMachineMetrics(machineId)
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    startAutoRefresh()
    showSuccess('Auto refresh ativado')
  } else {
    stopAutoRefresh()
    showSuccess('Auto refresh pausado')
  }
}

const toggleView = () => {
  showRealTimeCharts.value = !showRealTimeCharts.value
  showSuccess(showRealTimeCharts.value ? 'Visualização de gráficos ativada' : 'Visualização de cards ativada')
}

const toggleAlertsView = () => {
  showAlerts.value = !showAlerts.value
  showSuccess(showAlerts.value ? 'Sistema de alertas ativado' : 'Dashboard de monitoramento ativado')
}

const toggleInventoryView = () => {
  showInventory.value = !showInventory.value
  showSuccess(showInventory.value ? 'Sistema de inventário ativado' : 'Dashboard de monitoramento ativado')
}

const toggleTicketsView = () => {
  showTickets.value = !showTickets.value
  showSuccess(showTickets.value ? 'Sistema de chamados ativado' : 'Dashboard de monitoramento ativado')
}

const togglePerformanceView = () => {
  showPerformance.value = !showPerformance.value
  showSuccess(showPerformance.value ? 'Dashboard de performance ativado' : 'Dashboard de monitoramento ativado')
}

const handlePerformanceAlert = (alert) => {
  // Exibe alerta de performance
  if (alert.severity === 'critical') {
    showError(`Alerta Crítico: ${alert.message}`)
  } else if (alert.severity === 'warning') {
    showWarning(`Alerta: ${alert.message}`)
  } else {
    showInfo(`Info: ${alert.message}`)
  }
}

const handlePerformanceChange = (data) => {
  // Lida com mudanças de performance
  logger.debug('Performance change:', data)
  
  if (data.change < -20) {
    showWarning(`Performance degradou significativamente (Score: ${data.score})`)
  } else if (data.change > 20) {
    showSuccess(`Performance melhorou significativamente (Score: ${data.score})`)
  }
}

const startAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  
  refreshInterval.value = setInterval(() => {
    if (selectedMachine.value && !isLoadingMetrics.value) {
      loadMachineMetrics(selectedMachine.value)
    }
  }, 30000) // Atualiza a cada 30 segundos
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

const hasHighUsage = (machine) => {
  // Lógica para determinar se uma máquina tem uso alto
  // Em um cenário real, isso viria dos dados de métricas
  return false
}

const getMachineStatusColor = (status) => {
  switch (status) {
    case 'online': return 'success'
    case 'warning': return 'warning'
    case 'critical': return 'error'
    case 'offline': return 'surface-variant'
    default: return 'surface-variant'
  }
}

// Event handlers para detalhes
const viewCpuDetails = () => {
  showInfo('Funcionalidade de detalhes de CPU em desenvolvimento')
}

const viewMemoryDetails = () => {
  showInfo('Funcionalidade de detalhes de memória em desenvolvimento')
}

const viewDiskDetails = () => {
  showInfo('Funcionalidade de detalhes de disco em desenvolvimento')
}

const viewNetworkDetails = () => {
  showInfo('Funcionalidade de detalhes de rede em desenvolvimento')
}

const performDiskCleanup = () => {
  showInfo('Funcionalidade de limpeza de disco em desenvolvimento')
}

const testNetworkConnection = () => {
  showInfo('Teste de conexão de rede em desenvolvimento')
}

// Notification helpers
const showSuccess = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'success'
  showNotification.value = true
}

const showError = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'error'
  showNotification.value = true
}

const showInfo = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'info'
  showNotification.value = true
}

const showWarning = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'warning'
  showNotification.value = true
}

// Lifecycle hooks
onMounted(() => {
  loadMachines()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

// Watchers
watch(selectedMachine, (newValue) => {
  if (newValue) {
    loadMachineMetrics(newValue)
  }
})
</script>

<style scoped>
.monitoring-dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  min-height: 100vh;
  background: rgb(var(--v-theme-background));
}

.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.header-info {
  flex: 1;
}

.dashboard-title {
  display: flex;
  align-items: center;
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: rgb(var(--v-theme-on-background));
}

.dashboard-subtitle {
  color: rgb(var(--v-theme-on-background-variant));
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-overview {
  margin-top: 16px;
}

.status-value {
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
}

.status-label {
  font-size: 0.75rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.machine-selector {
  background: rgb(var(--v-theme-surface));
  border-radius: 8px;
}

.machine-info {
  display: flex;
  align-items: center;
  height: 100%;
}

.machine-details {
  flex: 1;
}

.machine-name {
  font-weight: 500;
  font-size: 0.875rem;
  margin-bottom: 4px;
}

.machine-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.metrics-grid {
  flex: 1;
}

.empty-state,
.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsividade */
@media (max-width: 960px) {
  .monitoring-dashboard {
    padding: 16px;
    gap: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
  
  .dashboard-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 600px) {
  .monitoring-dashboard {
    padding: 12px;
    gap: 12px;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .machine-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Animações */
.metrics-grid {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Tema escuro */
.v-theme--dark .monitoring-dashboard {
  background: rgb(var(--v-theme-background));
}
</style>