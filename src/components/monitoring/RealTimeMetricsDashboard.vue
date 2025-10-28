<template>
  <div class="real-time-metrics-dashboard">
    <div class="dashboard-header">
      <h2 class="dashboard-title">
        <i class="fas fa-chart-line"></i>
        Métricas em Tempo Real
      </h2>
      <div class="dashboard-controls">
        <div class="machine-selector">
          <label for="machine-select">Máquina:</label>
          <select 
            id="machine-select"
            v-model="selectedMachine" 
            @change="onMachineChange"
            class="form-select"
          >
            <option value="">Selecione uma máquina</option>
            <option 
              v-for="machine in machines" 
              :key="machine.id" 
              :value="machine.id"
            >
              {{ machine.hostname }} ({{ machine.ip_address }})
            </option>
          </select>
        </div>
        
        <div class="refresh-controls">
          <button 
            @click="toggleAutoRefresh" 
            :class="['btn', autoRefresh ? 'btn-success' : 'btn-outline-secondary']"
            :title="autoRefresh ? 'Desativar atualização automática' : 'Ativar atualização automática'"
          >
            <i :class="autoRefresh ? 'fas fa-pause' : 'fas fa-play'"></i>
            {{ autoRefresh ? 'Pausar' : 'Iniciar' }}
          </button>
          
          <button 
            @click="refreshAllData" 
            class="btn btn-primary"
            :disabled="isLoading"
            title="Atualizar dados manualmente"
          >
            <i :class="['fas', isLoading ? 'fa-spinner fa-spin' : 'fa-sync-alt']"></i>
            Atualizar
          </button>
        </div>
      </div>
    </div>

    <div v-if="!selectedMachine" class="no-machine-selected">
      <div class="empty-state">
        <i class="fas fa-desktop fa-3x"></i>
        <h3>Selecione uma máquina</h3>
        <p>Escolha uma máquina na lista acima para visualizar as métricas em tempo real.</p>
      </div>
    </div>

    <div v-else-if="isLoading && !hasData" class="loading-state">
      <div class="spinner-container">
        <div class="spinner"></div>
        <p>Carregando métricas...</p>
      </div>
    </div>

    <div v-else class="charts-grid">
      <!-- CPU Chart -->
      <div class="chart-card">
        <RealTimeChart
          ref="cpuChart"
          title="CPU (%)"
          :data="cpuData"
          unit="%"
          color="#ef4444"
          :warning-threshold="70"
          :critical-threshold="90"
          @update-data="updateCpuData"
        />
      </div>

      <!-- Memory Chart -->
      <div class="chart-card">
        <RealTimeChart
          ref="memoryChart"
          title="Memória (%)"
          :data="memoryData"
          unit="%"
          color="#3b82f6"
          :warning-threshold="80"
          :critical-threshold="95"
          @update-data="updateMemoryData"
        />
      </div>

      <!-- Disk Chart -->
      <div class="chart-card">
        <RealTimeChart
          ref="diskChart"
          title="Disco (%)"
          :data="diskData"
          unit="%"
          color="#f59e0b"
          :warning-threshold="85"
          :critical-threshold="95"
          @update-data="updateDiskData"
        />
      </div>

      <!-- Network Chart -->
      <div class="chart-card">
        <RealTimeChart
          ref="networkChart"
          title="Rede (Mbps)"
          :data="networkData"
          unit=" Mbps"
          color="#10b981"
          :warning-threshold="80"
          :critical-threshold="95"
          @update-data="updateNetworkData"
        />
      </div>
    </div>

    <!-- Machine Status -->
    <div v-if="selectedMachine && currentMetrics" class="machine-status">
      <div class="status-header">
        <h3>Status da Máquina</h3>
        <span :class="['status-badge', getOverallStatusClass()]">
          {{ getOverallStatus() }}
        </span>
      </div>
      
      <div class="status-grid">
        <div class="status-item">
          <div class="status-icon cpu">
            <i class="fas fa-microchip"></i>
          </div>
          <div class="status-info">
            <span class="status-label">CPU</span>
            <span class="status-value">{{ currentMetrics.cpu?.usage_percent?.toFixed(1) || 0 }}%</span>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-icon memory">
            <i class="fas fa-memory"></i>
          </div>
          <div class="status-info">
            <span class="status-label">Memória</span>
            <span class="status-value">{{ currentMetrics.memory?.usage_percent?.toFixed(1) || 0 }}%</span>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-icon disk">
            <i class="fas fa-hdd"></i>
          </div>
          <div class="status-info">
            <span class="status-label">Disco</span>
            <span class="status-value">{{ getAverageDiskUsage() }}%</span>
          </div>
        </div>
        
        <div class="status-item">
          <div class="status-icon network">
            <i class="fas fa-network-wired"></i>
          </div>
          <div class="status-info">
            <span class="status-label">Rede</span>
            <span class="status-value">{{ getNetworkSpeed() }} Mbps</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import RealTimeChart from './RealTimeChart.vue'
import { machineMonitoringAPI } from '@/services/api'

// Estado reativo
const selectedMachine = ref('')
const machines = ref([])
const isLoading = ref(false)
const autoRefresh = ref(true)
const refreshTimer = ref(null)
const currentMetrics = ref(null)
const hasData = ref(false)

// Dados dos gráficos
const cpuData = ref([])
const memoryData = ref([])
const diskData = ref([])
const networkData = ref([])

// Referências dos gráficos
const cpuChart = ref(null)
const memoryChart = ref(null)
const diskChart = ref(null)
const networkChart = ref(null)

// Configurações
const REFRESH_INTERVAL = 5000 // 5 segundos
// Removido: const API_BASE_URL = 'http://localhost:8000/api/v1'

// Métodos
const transformMachinesFromBackend = (list) => list.map(m => ({
  id: m.id ?? m.machine_id ?? m.uuid ?? m._id ?? m.identifier ?? m.name,
  hostname: m.hostname ?? m.name ?? m.machine_id ?? `machine-${m.id ?? m.machine_id ?? Math.random().toString(36).slice(2, 8)}`,
  ip_address: m.ip_address ?? m.ip ?? m.last_known_ip ?? m.address ?? '0.0.0.0',
}))

const loadMachines = async () => {
  try {
    const response = await machineMonitoringAPI.getMachines()
    const backendMachines = Array.isArray(response.data?.machines)
      ? response.data.machines
      : Array.isArray(response.data)
        ? response.data
        : []
    machines.value = transformMachinesFromBackend(backendMachines)
  } catch (error) {
    logger.error('Erro ao carregar máquinas:', error)
  }
}

const loadMachineMetrics = async (machineId) => {
  if (!machineId) return

  try {
    isLoading.value = true
    const response = await machineMonitoringAPI.getMetrics(machineId)
    // Tratamento de erro do backend: quando NoneType await
    if (response.data?.detail) {
      logger.warn('Backend não retornou métricas válidas:', response.data.detail)
      currentMetrics.value = buildEmptyMetrics()
      hasData.value = false
    } else {
      currentMetrics.value = response.data
      hasData.value = true
    }
    
    // Atualizar dados dos gráficos
    updateChartData()
  } catch (error) {
    logger.error('Erro ao carregar métricas:', error)
    currentMetrics.value = buildEmptyMetrics()
    hasData.value = false
  } finally {
    isLoading.value = false
  }
}

const updateChartData = () => {
  if (!currentMetrics.value) return

  const metrics = currentMetrics.value

  // CPU
  if (metrics.cpu?.usage_percent !== undefined) {
    cpuData.value = [...cpuData.value, metrics.cpu.usage_percent]
  }

  // Memory
  if (metrics.memory?.usage_percent !== undefined) {
    memoryData.value = [...memoryData.value, metrics.memory.usage_percent]
  }

  // Disk (média de todos os discos)
  if (metrics.disk?.disks && Array.isArray(metrics.disk.disks)) {
    const avgDiskUsage = getAverageDiskUsage()
    diskData.value = [...diskData.value, avgDiskUsage]
  }

  // Network (velocidade total)
  if (metrics.network?.total_bytes_sent !== undefined && metrics.network?.total_bytes_recv !== undefined) {
    const totalSpeed = getNetworkSpeed()
    networkData.value = [...networkData.value, totalSpeed]
  }
}

const getAverageDiskUsage = () => {
  if (!currentMetrics.value?.disk?.disks) return 0
  
  const disks = currentMetrics.value.disk.disks
  if (disks.length === 0) return 0
  
  const totalUsage = disks.reduce((sum, disk) => sum + (disk.usage_percent || 0), 0)
  return (totalUsage / disks.length).toFixed(1)
}

const getNetworkSpeed = () => {
  if (!currentMetrics.value?.network) return 0
  
  const sent = currentMetrics.value.network.total_bytes_sent || 0
  const recv = currentMetrics.value.network.total_bytes_recv || 0
  
  // Converter bytes para Mbps (aproximação)
  const totalMbps = ((sent + recv) / 1024 / 1024 * 8).toFixed(1)
  return totalMbps
}

const getOverallStatus = () => {
  if (!currentMetrics.value) return 'Desconhecido'
  
  const cpu = currentMetrics.value.cpu?.usage_percent || 0
  const memory = currentMetrics.value.memory?.usage_percent || 0
  const disk = parseFloat(getAverageDiskUsage())
  
  const maxUsage = Math.max(cpu, memory, disk)
  
  if (maxUsage >= 95) return 'Crítico'
  if (maxUsage >= 80) return 'Atenção'
  if (maxUsage >= 60) return 'Normal'
  return 'Ótimo'
}

const getOverallStatusClass = () => {
  const status = getOverallStatus()
  switch (status) {
    case 'Crítico': return 'status-critical'
    case 'Atenção': return 'status-warning'
    case 'Normal': return 'status-normal'
    case 'Ótimo': return 'status-good'
    default: return 'status-unknown'
  }
}

const onMachineChange = () => {
  // Limpar dados anteriores
  cpuData.value = []
  memoryData.value = []
  diskData.value = []
  networkData.value = []
  currentMetrics.value = null
  hasData.value = false
  
  if (selectedMachine.value) {
    loadMachineMetrics(selectedMachine.value)
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const refreshAllData = () => {
  if (selectedMachine.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  
  if (selectedMachine.value) {
    refreshTimer.value = setInterval(() => {
      if (autoRefresh.value) {
        loadMachineMetrics(selectedMachine.value)
      }
    }, REFRESH_INTERVAL)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

// Métodos de atualização dos gráficos (chamados pelos componentes RealTimeChart)
const updateCpuData = () => {
  if (selectedMachine.value && autoRefresh.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const updateMemoryData = () => {
  if (selectedMachine.value && autoRefresh.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const updateDiskData = () => {
  if (selectedMachine.value && autoRefresh.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

const updateNetworkData = () => {
  if (selectedMachine.value && autoRefresh.value) {
    loadMachineMetrics(selectedMachine.value)
  }
}

// Lifecycle
onMounted(() => {
  loadMachines()
})

onUnmounted(() => {
  stopAutoRefresh()
})

// Watchers
watch(selectedMachine, (newValue) => {
  if (newValue) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

const buildEmptyMetrics = () => ({
  cpu: { usage_percent: 0 },
  memory: { usage_percent: 0 },
  disk: { disks: [] },
  network: { total_bytes_sent: 0, total_bytes_recv: 0 }
})
</script>

<style scoped>
.real-time-metrics-dashboard {
  padding: 1.5rem;
  background: #f8fafc;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dashboard-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.machine-selector label {
  margin-right: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  min-width: 200px;
}

.refresh-controls {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
}

.btn-success {
  background-color: #10b981;
  border-color: #10b981;
  color: white;
}

.btn-success:hover {
  background-color: #059669;
  border-color: #059669;
}

.btn-outline-secondary {
  background-color: transparent;
  border-color: #6b7280;
  color: #6b7280;
}

.btn-outline-secondary:hover {
  background-color: #6b7280;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.no-machine-selected,
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-state {
  text-align: center;
  color: #6b7280;
}

.empty-state i {
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0.5rem 0;
  color: #374151;
}

.spinner-container {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.machine-status {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.status-header h3 {
  margin: 0;
  color: #1f2937;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-good {
  background-color: #d1fae5;
  color: #065f46;
}

.status-normal {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.status-critical {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-unknown {
  background-color: #f3f4f6;
  color: #374151;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 6px;
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.status-icon.cpu {
  background-color: #ef4444;
}

.status-icon.memory {
  background-color: #3b82f6;
}

.status-icon.disk {
  background-color: #f59e0b;
}

.status-icon.network {
  background-color: #10b981;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.status-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .dashboard-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>