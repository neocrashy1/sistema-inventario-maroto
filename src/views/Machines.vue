<template>
  <div class="machines-monitoring" role="main" aria-labelledby="machines-title">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 id="machines-title">Monitoramento de Máquinas</h1>
        <div class="header-actions">
          <button 
            @click="refreshData" 
            :disabled="loading"
            class="btn btn-primary"
            :aria-label="loading ? 'Atualizando dados...' : 'Atualizar dados das máquinas'"
          >
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
            {{ loading ? 'Atualizando...' : 'Atualizar' }}
          </button>
          
          <button 
            @click="toggleAutoRefresh"
            class="btn btn-secondary"
            :class="{ 'active': monitoringConfig.autoRefresh }"
            :aria-label="monitoringConfig.autoRefresh ? 'Desativar atualização automática' : 'Ativar atualização automática'"
          >
            <i class="fas" :class="monitoringConfig.autoRefresh ? 'fa-pause' : 'fa-play'"></i>
            Auto-refresh
          </button>
        </div>
      </div>
      
      <!-- Status da última atualização -->
      <div class="last-update" v-if="lastUpdate">
        <i class="fas fa-clock"></i>
        Última atualização: {{ formatDateTime(lastUpdate) }}
        <span v-if="wsConnected" class="ws-status connected">
          <i class="fas fa-circle"></i> Tempo real ativo
        </span>
        <span v-else class="ws-status disconnected">
          <i class="fas fa-circle"></i> Tempo real inativo
        </span>
      </div>
    </div>

    <!-- Métricas Gerais -->
    <div class="metrics-grid">
      <div class="metric-card total">
        <div class="metric-icon">
          <i class="fas fa-desktop"></i>
        </div>
        <div class="metric-content">
          <h3>Total de Máquinas</h3>
          <div class="metric-value">{{ metrics.totalMachines }}</div>
        </div>
      </div>

      <div class="metric-card online">
        <div class="metric-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Online</h3>
          <div class="metric-value">{{ metrics.onlineMachines }}</div>
          <div class="metric-percentage">{{ getPercentage(metrics.onlineMachines, metrics.totalMachines) }}%</div>
        </div>
      </div>

      <div class="metric-card offline">
        <div class="metric-icon">
          <i class="fas fa-times-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Offline</h3>
          <div class="metric-value">{{ metrics.offlineMachines }}</div>
          <div class="metric-percentage">{{ getPercentage(metrics.offlineMachines, metrics.totalMachines) }}%</div>
        </div>
      </div>

      <div class="metric-card warning">
        <div class="metric-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="metric-content">
          <h3>Atenção</h3>
          <div class="metric-value">{{ metrics.warningMachines }}</div>
          <div class="metric-percentage">{{ getPercentage(metrics.warningMachines, metrics.totalMachines) }}%</div>
        </div>
      </div>

      <div class="metric-card critical">
        <div class="metric-icon">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        <div class="metric-content">
          <h3>Crítico</h3>
          <div class="metric-value">{{ metrics.criticalMachines }}</div>
          <div class="metric-percentage">{{ getPercentage(metrics.criticalMachines, metrics.totalMachines) }}%</div>
        </div>
      </div>

      <div class="metric-card performance">
        <div class="metric-icon">
          <i class="fas fa-tachometer-alt"></i>
        </div>
        <div class="metric-content">
          <h3>CPU Média</h3>
          <div class="metric-value">{{ metrics.avgCpuUsage.toFixed(1) }}%</div>
          <div class="performance-bar">
            <div class="performance-fill" :style="{ width: metrics.avgCpuUsage + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="metric-card performance">
        <div class="metric-icon">
          <i class="fas fa-memory"></i>
        </div>
        <div class="metric-content">
          <h3>Memória Média</h3>
          <div class="metric-value">{{ metrics.avgMemoryUsage.toFixed(1) }}%</div>
          <div class="performance-bar">
            <div class="performance-fill" :style="{ width: metrics.avgMemoryUsage + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="metric-card performance">
        <div class="metric-icon">
          <i class="fas fa-hdd"></i>
        </div>
        <div class="metric-content">
          <h3>Disco Médio</h3>
          <div class="metric-value">{{ metrics.avgDiskUsage.toFixed(1) }}%</div>
          <div class="performance-bar">
            <div class="performance-fill" :style="{ width: metrics.avgDiskUsage + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-section">
      <div class="filters-grid">
        <div class="filter-group">
          <label for="status-filter">Status:</label>
          <select 
            id="status-filter"
            v-model="filters.status" 
            @change="applyFilters"
            class="form-select"
          >
            <option value="all">Todos</option>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
            <option value="warning">Atenção</option>
            <option value="critical">Crítico</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="location-filter">Localização:</label>
          <input 
            id="location-filter"
            v-model="filters.location" 
            @input="applyFilters"
            type="text" 
            placeholder="Filtrar por localização..."
            class="form-input"
          />
        </div>

        <div class="filter-group">
          <label for="department-filter">Departamento:</label>
          <input 
            id="department-filter"
            v-model="filters.department" 
            @input="applyFilters"
            type="text" 
            placeholder="Filtrar por departamento..."
            class="form-input"
          />
        </div>

        <div class="filter-group">
          <label for="search-filter">Buscar:</label>
          <input 
            id="search-filter"
            v-model="filters.search" 
            @input="applyFilters"
            type="text" 
            placeholder="Nome, hostname, IP, usuário..."
            class="form-input"
          />
        </div>

        <div class="filter-actions">
          <button @click="clearFilters" class="btn btn-outline">
            <i class="fas fa-times"></i>
            Limpar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Lista de Máquinas -->
    <div class="machines-section">
      <div class="section-header">
        <h2>Máquinas ({{ filteredMachines.length }})</h2>
        <div class="view-options">
          <button 
            @click="viewMode = 'grid'" 
            :class="{ active: viewMode === 'grid' }"
            class="btn btn-sm"
            aria-label="Visualização em grade"
          >
            <i class="fas fa-th"></i>
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="{ active: viewMode === 'list' }"
            class="btn btn-sm"
            aria-label="Visualização em lista"
          >
            <i class="fas fa-list"></i>
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && machines.length === 0" class="loading-state">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p>Carregando máquinas...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error && machines.length === 0" class="error-state">
        <div class="error-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3>Erro ao carregar máquinas</h3>
        <p>{{ error }}</p>
        <button @click="refreshData" class="btn btn-primary">
          <i class="fas fa-retry"></i>
          Tentar Novamente
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredMachines.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-desktop"></i>
        </div>
        <h3>Nenhuma máquina encontrada</h3>
        <p v-if="hasActiveFilters">Tente ajustar os filtros para ver mais resultados.</p>
        <p v-else>Nenhuma máquina foi registrada ainda.</p>
      </div>

      <!-- Grid View -->
      <div v-else-if="viewMode === 'grid'" class="machines-grid">
        <div 
          v-for="machine in filteredMachines" 
          :key="machine.id"
          class="machine-card"
          :class="[`status-${machine.status}`, { selected: selectedMachine?.id === machine.id }]"
          @click="selectMachine(machine)"
          role="button"
          tabindex="0"
          :aria-label="`Máquina ${machine.name} - Status: ${machine.status}`"
          @keydown.enter="selectMachine(machine)"
          @keydown.space.prevent="selectMachine(machine)"
        >
          <div class="machine-header">
            <div class="machine-status">
              <i class="fas fa-circle" :class="`status-${machine.status}`"></i>
            </div>
            <div class="machine-name">
              <h3>{{ machine.name }}</h3>
              <p>{{ machine.hostname }}</p>
            </div>
          </div>

          <div class="machine-info">
            <div class="info-row">
              <span class="label">IP:</span>
              <span class="value">{{ machine.ip }}</span>
            </div>
            <div class="info-row">
              <span class="label">Usuário:</span>
              <span class="value">{{ machine.user }}</span>
            </div>
            <div class="info-row">
              <span class="label">Local:</span>
              <span class="value">{{ machine.location }}</span>
            </div>
            <div class="info-row">
              <span class="label">Depto:</span>
              <span class="value">{{ machine.department }}</span>
            </div>
          </div>

          <div v-if="machine.performance && machine.status === 'online'" class="machine-performance">
            <div class="performance-metric">
              <span class="metric-label">CPU</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: machine.performance.cpu + '%' }"></div>
              </div>
              <span class="metric-value">{{ machine.performance.cpu }}%</span>
            </div>
            <div class="performance-metric">
              <span class="metric-label">RAM</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: machine.performance.memory + '%' }"></div>
              </div>
              <span class="metric-value">{{ machine.performance.memory }}%</span>
            </div>
            <div class="performance-metric">
              <span class="metric-label">Disco</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: machine.performance.disk + '%' }"></div>
              </div>
              <span class="metric-value">{{ machine.performance.disk }}%</span>
            </div>
          </div>

          <div class="machine-footer">
            <span class="last-seen">
              <i class="fas fa-clock"></i>
              {{ formatRelativeTime(machine.lastSeen) }}
            </span>
            <span v-if="machine.uptime" class="uptime">
              <i class="fas fa-arrow-up"></i>
              {{ formatUptime(machine.uptime) }}
            </span>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="machines-table">
        <table class="table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Nome</th>
              <th>Hostname</th>
              <th>IP</th>
              <th>Usuário</th>
              <th>Localização</th>
              <th>Departamento</th>
              <th>CPU</th>
              <th>Memória</th>
              <th>Disco</th>
              <th>Última Conexão</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="machine in filteredMachines" 
              :key="machine.id"
              :class="[`status-${machine.status}`, { selected: selectedMachine?.id === machine.id }]"
              @click="selectMachine(machine)"
              role="button"
              tabindex="0"
              @keydown.enter="selectMachine(machine)"
              @keydown.space.prevent="selectMachine(machine)"
            >
              <td>
                <span class="status-badge" :class="`status-${machine.status}`">
                  <i class="fas fa-circle"></i>
                  {{ getStatusLabel(machine.status) }}
                </span>
              </td>
              <td>{{ machine.name }}</td>
              <td>{{ machine.hostname }}</td>
              <td>{{ machine.ip }}</td>
              <td>{{ machine.user }}</td>
              <td>{{ machine.location }}</td>
              <td>{{ machine.department }}</td>
              <td>
                <div v-if="machine.performance && machine.status === 'online'" class="performance-cell">
                  <span>{{ machine.performance.cpu }}%</span>
                  <div class="mini-bar">
                    <div class="mini-fill" :style="{ width: machine.performance.cpu + '%' }"></div>
                  </div>
                </div>
                <span v-else>-</span>
              </td>
              <td>
                <div v-if="machine.performance && machine.status === 'online'" class="performance-cell">
                  <span>{{ machine.performance.memory }}%</span>
                  <div class="mini-bar">
                    <div class="mini-fill" :style="{ width: machine.performance.memory + '%' }"></div>
                  </div>
                </div>
                <span v-else>-</span>
              </td>
              <td>
                <div v-if="machine.performance && machine.status === 'online'" class="performance-cell">
                  <span>{{ machine.performance.disk }}%</span>
                  <div class="mini-bar">
                    <div class="mini-fill" :style="{ width: machine.performance.disk + '%' }"></div>
                  </div>
                </div>
                <span v-else>-</span>
              </td>
              <td>{{ formatRelativeTime(machine.lastSeen) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click.stop="viewMachineDetails(machine)"
                    class="btn btn-sm btn-outline"
                    :aria-label="`Ver detalhes da máquina ${machine.name}`"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="machine.status === 'online'"
                    @click.stop="refreshMachineStatus(machine.id)"
                    class="btn btn-sm btn-outline"
                    :aria-label="`Atualizar status da máquina ${machine.name}`"
                  >
                    <i class="fas fa-sync-alt"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Machine Details Modal (será implementado posteriormente) -->
    <div v-if="selectedMachine && showDetails" class="machine-details-modal">
      <!-- Detalhes da máquina serão implementados -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMachinesStore } from '@/stores/machines'
import { formatDateTime, formatTimeAgo } from '@/utils/dateUtils'

// Store
const machinesStore = useMachinesStore()

// Estado local
const viewMode = ref('grid') // 'grid' ou 'list'
const showDetails = ref(false)

// Computed properties do store
const {
  machines,
  selectedMachine,
  loading,
  error,
  lastUpdate,
  wsConnected,
  filters,
  monitoringConfig,
  metrics,
  filteredMachines
} = machinesStore

// Computed properties locais
const hasActiveFilters = computed(() => {
  return filters.status !== 'all' || 
         filters.location !== '' || 
         filters.department !== '' || 
         filters.search !== ''
})

// Métodos
const refreshData = async () => {
  await machinesStore.fetchMachines(true)
}

const refreshMachineStatus = async (machineId) => {
  await machinesStore.fetchMachineStatus(machineId)
}

const selectMachine = (machine) => {
  machinesStore.selectMachine(machine)
}

const viewMachineDetails = (machine) => {
  machinesStore.selectMachine(machine)
  showDetails.value = true
}

const applyFilters = () => {
  // Os filtros são aplicados automaticamente via computed property
}

const clearFilters = () => {
  machinesStore.clearFilters()
}

const toggleAutoRefresh = () => {
  machinesStore.updateMonitoringConfig({
    autoRefresh: !monitoringConfig.autoRefresh
  })
}

const getPercentage = (value, total) => {
  return total > 0 ? Math.round((value / total) * 100) : 0
}

const getStatusLabel = (status) => {
  const labels = {
    online: 'Online',
    offline: 'Offline',
    warning: 'Atenção',
    critical: 'Crítico'
  }
  return labels[status] || status
}

const formatUptime = (hours) => {
  if (hours < 24) {
    return `${hours}h`
  } else {
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    return `${days}d ${remainingHours}h`
  }
}

// Lifecycle
onMounted(async () => {
  await refreshData()
  
  // Conecta ao WebSocket para dados em tempo real
  await machinesStore.connectWebSocket()
  
  if (machinesStore.autoRefresh) {
    machinesStore.startAutoRefresh()
  }
})

onUnmounted(() => {
  machinesStore.stopAutoRefresh()
  machinesStore.disconnectWebSocket()
})
</script>

<style scoped>
.machines-monitoring {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header-content h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.last-update {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.ws-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.ws-status.connected {
  color: var(--success-color);
}

.ws-status.disconnected {
  color: var(--warning-color);
}

/* Métricas */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.metric-card.total .metric-icon {
  background: var(--primary-color-light);
  color: var(--primary-color);
}

.metric-card.online .metric-icon {
  background: var(--success-color-light);
  color: var(--success-color);
}

.metric-card.offline .metric-icon {
  background: var(--error-color-light);
  color: var(--error-color);
}

.metric-card.warning .metric-icon {
  background: var(--warning-color-light);
  color: var(--warning-color);
}

.metric-card.critical .metric-icon {
  background: var(--error-color-light);
  color: var(--error-color);
}

.metric-card.performance .metric-icon {
  background: var(--info-color-light);
  color: var(--info-color);
}

.metric-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.metric-percentage {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.performance-bar {
  width: 100%;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  margin-top: 0.5rem;
  overflow: hidden;
}

.performance-fill {
  height: 100%;
  background: var(--info-color);
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Filtros */
.filters-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.form-select,
.form-input {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--input-background);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}

/* Seção de Máquinas */
.machines-section {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--background-secondary);
}

.section-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.view-options {
  display: flex;
  gap: 0.25rem;
}

.view-options .btn {
  padding: 0.5rem;
  min-width: auto;
}

.view-options .btn.active {
  background: var(--primary-color);
  color: white;
}

/* Estados */
.loading-state,
.error-state,
.empty-state {
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.loading-spinner,
.error-icon,
.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--text-tertiary);
}

.loading-spinner i {
  color: var(--primary-color);
}

.error-icon i {
  color: var(--error-color);
}

/* Grid de Máquinas */
.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
  padding: 1.5rem;
}

.machine-card {
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.machine-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.machine-card.selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-light);
}

.machine-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.machine-status i {
  font-size: 0.75rem;
}

.machine-name h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.machine-name p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.machine-info {
  margin-bottom: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.info-row .label {
  color: var(--text-secondary);
  font-weight: 500;
}

.info-row .value {
  color: var(--text-primary);
}

.machine-performance {
  margin-bottom: 1rem;
}

.performance-metric {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
}

.metric-label {
  width: 30px;
  color: var(--text-secondary);
  font-weight: 500;
}

.metric-bar {
  flex: 1;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: var(--success-color);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.metric-value {
  width: 35px;
  text-align: right;
  color: var(--text-primary);
  font-weight: 500;
}

.machine-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.last-seen,
.uptime {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Tabela de Máquinas */
.machines-table {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.table th {
  background: var(--background-secondary);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.table tbody tr:hover {
  background: var(--background-secondary);
}

.table tbody tr.selected {
  background: var(--primary-color-light);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.performance-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mini-bar {
  width: 40px;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.mini-fill {
  height: 100%;
  background: var(--success-color);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

/* Status Colors */
.status-online,
.status-badge.status-online {
  color: var(--success-color);
  background: var(--success-color-light);
}

.status-offline,
.status-badge.status-offline {
  color: var(--error-color);
  background: var(--error-color-light);
}

.status-warning,
.status-badge.status-warning {
  color: var(--warning-color);
  background: var(--warning-color-light);
}

.status-critical,
.status-badge.status-critical {
  color: var(--error-color);
  background: var(--error-color-light);
}

/* Responsividade */
@media (max-width: 768px) {
  .machines-monitoring {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .machines-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .view-options {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .metric-card {
    padding: 1rem;
  }
  
  .metric-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
  }
}
</style>