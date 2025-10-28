<template>
  <div class="schedule-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Agendamentos</h1>
          <p class="page-subtitle">Gerencie agendamentos de manutenção preventiva e corretiva</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline" @click="exportSchedules" :disabled="loading">
            <i class="icon-download"></i>
            Exportar
          </button>
          <button class="btn btn-primary" @click="openCreateModal">
            <i class="icon-plus"></i>
            Novo Agendamento
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary">
          <i class="icon-calendar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalSchedules }}</div>
          <div class="stat-label">Total de Agendamentos</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="icon-play"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ activeSchedules.length }}</div>
          <div class="stat-label">Ativos</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="icon-pause"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pausedSchedules.length }}</div>
          <div class="stat-label">Pausados</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon danger">
          <i class="icon-alert"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ overdueSchedules.length }}</div>
          <div class="stat-label">Em Atraso</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <input
            type="text"
            placeholder="Buscar agendamentos..."
            v-model="searchTerm"
            class="search-input"
          />
        </div>
        <div class="filter-group">
          <select v-model="filters.status" class="filter-select">
            <option value="">Todos os Status</option>
            <option value="active">Ativo</option>
            <option value="paused">Pausado</option>
            <option value="inactive">Inativo</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="filters.type" class="filter-select">
            <option value="">Todos os Tipos</option>
            <option value="preventive">Preventiva</option>
            <option value="corrective">Corretiva</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="filters.frequency" class="filter-select">
            <option value="">Todas as Frequências</option>
            <option value="daily">Diário</option>
            <option value="weekly">Semanal</option>
            <option value="monthly">Mensal</option>
            <option value="quarterly">Trimestral</option>
            <option value="yearly">Anual</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="filters.priority" class="filter-select">
            <option value="">Todas as Prioridades</option>
            <option value="low">Baixa</option>
            <option value="medium">Média</option>
            <option value="high">Alta</option>
            <option value="urgent">Urgente</option>
          </select>
        </div>
        <div class="filter-group">
          <button class="btn btn-outline btn-sm" @click="clearFilters">
            <i class="icon-x"></i>
            Limpar
          </button>
        </div>
      </div>
    </div>

    <!-- Upcoming Executions -->
    <div class="upcoming-section" v-if="upcomingExecutions.length > 0">
      <h3 class="section-title">Próximas Execuções (7 dias)</h3>
      <div class="upcoming-list">
        <div 
          v-for="schedule in upcomingExecutions" 
          :key="schedule.id"
          class="upcoming-item"
        >
          <div class="upcoming-date">
            <div class="date-day">{{ formatDate(schedule.nextExecution, 'DD') }}</div>
            <div class="date-month">{{ formatDate(schedule.nextExecution, 'MMM') }}</div>
          </div>
          <div class="upcoming-content">
            <div class="upcoming-title">{{ schedule.title }}</div>
            <div class="upcoming-details">
              <span class="upcoming-asset">{{ schedule.assetCode }}</span>
              <span class="upcoming-tech">{{ schedule.assignedTo }}</span>
              <span class="upcoming-duration">{{ schedule.estimatedDuration }}h</span>
            </div>
          </div>
          <div class="upcoming-actions">
            <button 
              class="btn btn-sm btn-primary" 
              @click="executeSchedule(schedule.id)"
              :disabled="loading"
            >
              Executar Agora
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedules Table -->
    <div class="table-section">
      <div class="table-container">
        <table class="data-table" v-if="!loading && filteredSchedules.length > 0">
          <thead>
            <tr>
              <th>Código</th>
              <th>Título</th>
              <th>Tipo</th>
              <th>Frequência</th>
              <th>Prioridade</th>
              <th>Status</th>
              <th>Ativo</th>
              <th>Responsável</th>
              <th>Próxima Execução</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="schedule in filteredSchedules" :key="schedule.id">
              <td>
                <span class="schedule-code">#{{ schedule.id }}</span>
              </td>
              <td>
                <div class="schedule-title">
                  <div class="title">{{ schedule.title }}</div>
                  <div class="description">{{ schedule.description }}</div>
                </div>
              </td>
              <td>
                <span class="badge" :class="`badge-${schedule.type}`">
                  {{ getTypeLabel(schedule.type) }}
                </span>
              </td>
              <td>
                <span class="frequency">{{ getFrequencyLabel(schedule.frequency) }}</span>
              </td>
              <td>
                <span class="badge" :class="`badge-${schedule.priority}`">
                  {{ getPriorityLabel(schedule.priority) }}
                </span>
              </td>
              <td>
                <span class="badge" :class="`badge-${schedule.status}`">
                  {{ getStatusLabel(schedule.status) }}
                </span>
              </td>
              <td>
                <div class="asset-info">
                  <div class="asset-code">{{ schedule.assetCode }}</div>
                  <div class="asset-name">{{ schedule.assetName }}</div>
                </div>
              </td>
              <td>
                <span class="technician">{{ schedule.assignedTo }}</span>
              </td>
              <td>
                <div class="date-info">
                  <div class="next-date">{{ formatDate(schedule.nextExecution) }}</div>
                  <div class="last-date" v-if="schedule.lastExecution">
                    Última: {{ formatDate(schedule.lastExecution) }}
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn btn-sm btn-outline"
                    @click="viewSchedule(schedule)"
                    title="Visualizar"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline"
                    @click="editSchedule(schedule)"
                    title="Editar"
                  >
                    <i class="icon-edit"></i>
                  </button>
                  <button 
                    class="btn btn-sm"
                    :class="schedule.status === 'active' ? 'btn-warning' : 'btn-success'"
                    @click="toggleScheduleStatus(schedule.id)"
                    :title="schedule.status === 'active' ? 'Pausar' : 'Ativar'"
                    :disabled="loading"
                  >
                    <i :class="schedule.status === 'active' ? 'icon-pause' : 'icon-play'"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-primary"
                    @click="executeSchedule(schedule.id)"
                    title="Executar Agora"
                    :disabled="loading || schedule.status !== 'active'"
                  >
                    <i class="icon-play-circle"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Carregando agendamentos...</p>
        </div>

        <!-- Empty State -->
        <div v-if="!loading && filteredSchedules.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="icon-calendar"></i>
          </div>
          <h3>Nenhum agendamento encontrado</h3>
          <p>Não há agendamentos que correspondam aos filtros aplicados.</p>
          <button class="btn btn-primary" @click="clearFilters">
            Limpar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingSchedule ? 'Editar Agendamento' : 'Novo Agendamento' }}</h3>
          <button class="modal-close" @click="closeCreateModal">
            <i class="icon-x"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveSchedule">
            <div class="form-row">
              <div class="form-group">
                <label>Título *</label>
                <input
                  type="text"
                  v-model="scheduleForm.title"
                  required
                  class="form-input"
                  placeholder="Ex: Manutenção Preventiva - Servidores"
                />
              </div>
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="scheduleForm.type" required class="form-select">
                  <option value="">Selecione o tipo</option>
                  <option value="preventive">Preventiva</option>
                  <option value="corrective">Corretiva</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Frequência *</label>
                <select v-model="scheduleForm.frequency" required class="form-select">
                  <option value="">Selecione a frequência</option>
                  <option value="daily">Diário</option>
                  <option value="weekly">Semanal</option>
                  <option value="monthly">Mensal</option>
                  <option value="quarterly">Trimestral</option>
                  <option value="yearly">Anual</option>
                </select>
              </div>
              <div class="form-group">
                <label>Prioridade *</label>
                <select v-model="scheduleForm.priority" required class="form-select">
                  <option value="">Selecione a prioridade</option>
                  <option value="low">Baixa</option>
                  <option value="medium">Média</option>
                  <option value="high">Alta</option>
                  <option value="urgent">Urgente</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Ativo *</label>
                <select v-model="scheduleForm.assetId" required class="form-select">
                  <option value="">Selecione o ativo</option>
                  <option 
                    v-for="asset in availableAssets" 
                    :key="asset.id" 
                    :value="asset.id"
                  >
                    {{ asset.code }} - {{ asset.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Responsável *</label>
                <select v-model="scheduleForm.assignedTo" required class="form-select">
                  <option value="">Selecione o responsável</option>
                  <option 
                    v-for="tech in technicians" 
                    :key="tech.id" 
                    :value="tech.name"
                  >
                    {{ tech.name }} - {{ tech.specialties.join(', ') }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Data de Início *</label>
                <input
                  type="date"
                  v-model="scheduleForm.startDate"
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label>Duração Estimada (horas) *</label>
                <input
                  type="number"
                  v-model="scheduleForm.estimatedDuration"
                  required
                  min="0.5"
                  step="0.5"
                  class="form-input"
                  placeholder="Ex: 2.5"
                />
              </div>
            </div>
            <div class="form-group">
              <label>Descrição *</label>
              <textarea
                v-model="scheduleForm.description"
                required
                class="form-textarea"
                rows="3"
                placeholder="Descreva as atividades a serem realizadas..."
              ></textarea>
            </div>
            <div class="form-group">
              <label>Observações</label>
              <textarea
                v-model="scheduleForm.notes"
                class="form-textarea"
                rows="2"
                placeholder="Observações adicionais..."
              ></textarea>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline" @click="closeCreateModal">
            Cancelar
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="saveSchedule"
            :disabled="loading"
          >
            {{ editingSchedule ? 'Atualizar' : 'Criar' }} Agendamento
          </button>
        </div>
      </div>
    </div>

    <!-- View Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h3>Detalhes do Agendamento</h3>
          <button class="modal-close" @click="closeViewModal">
            <i class="icon-x"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="schedule-details" v-if="selectedSchedule">
            <div class="details-grid">
              <div class="detail-item">
                <label>Código</label>
                <span>#{{ selectedSchedule.id }}</span>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <span class="badge" :class="`badge-${selectedSchedule.status}`">
                  {{ getStatusLabel(selectedSchedule.status) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Título</label>
                <span>{{ selectedSchedule.title }}</span>
              </div>
              <div class="detail-item">
                <label>Tipo</label>
                <span class="badge" :class="`badge-${selectedSchedule.type}`">
                  {{ getTypeLabel(selectedSchedule.type) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Frequência</label>
                <span>{{ getFrequencyLabel(selectedSchedule.frequency) }}</span>
              </div>
              <div class="detail-item">
                <label>Prioridade</label>
                <span class="badge" :class="`badge-${selectedSchedule.priority}`">
                  {{ getPriorityLabel(selectedSchedule.priority) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Ativo</label>
                <span>{{ selectedSchedule.assetCode }} - {{ selectedSchedule.assetName }}</span>
              </div>
              <div class="detail-item">
                <label>Responsável</label>
                <span>{{ selectedSchedule.assignedTo }}</span>
              </div>
              <div class="detail-item">
                <label>Data de Início</label>
                <span>{{ formatDate(selectedSchedule.startDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Próxima Execução</label>
                <span>{{ formatDate(selectedSchedule.nextExecution) }}</span>
              </div>
              <div class="detail-item">
                <label>Última Execução</label>
                <span>{{ selectedSchedule.lastExecution ? formatDate(selectedSchedule.lastExecution) : 'Nunca' }}</span>
              </div>
              <div class="detail-item">
                <label>Duração Estimada</label>
                <span>{{ selectedSchedule.estimatedDuration }} horas</span>
              </div>
            </div>
            <div class="detail-section">
              <label>Descrição</label>
              <p>{{ selectedSchedule.description }}</p>
            </div>
            <div class="detail-section" v-if="selectedSchedule.notes">
              <label>Observações</label>
              <p>{{ selectedSchedule.notes }}</p>
            </div>
            
            <!-- Execution History -->
            <div class="detail-section" v-if="selectedSchedule.executionHistory.length > 0">
              <label>Histórico de Execuções</label>
              <div class="execution-history">
                <div 
                  v-for="execution in selectedSchedule.executionHistory" 
                  :key="execution.id"
                  class="execution-item"
                >
                  <div class="execution-header">
                    <span class="execution-date">{{ formatDateTime(execution.executedAt) }}</span>
                    <span class="badge badge-success">{{ execution.status }}</span>
                  </div>
                  <div class="execution-details">
                    <p><strong>Técnico:</strong> {{ execution.technician }}</p>
                    <p><strong>Duração:</strong> {{ calculateDuration(execution.executedAt, execution.completedAt) }}</p>
                    <p v-if="execution.notes"><strong>Observações:</strong> {{ execution.notes }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline" @click="closeViewModal">
            Fechar
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="editSchedule(selectedSchedule)"
          >
            Editar
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
    <div v-if="error" class="alert alert-error">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted, watch } from 'vue'
import { useSchedulesStore } from '@/stores/schedules'

// Store
const schedulesStore = useSchedulesStore()

// Reactive state
const showCreateModal = ref(false)
const showViewModal = ref(false)
const editingSchedule = ref(null)
const selectedSchedule = ref(null)
const successMessage = ref('')

// Form data
const scheduleForm = ref({
  title: '',
  description: '',
  type: '',
  frequency: '',
  priority: '',
  assetId: '',
  assignedTo: '',
  startDate: '',
  estimatedDuration: '',
  notes: ''
})

// Computed properties from store
const loading = computed(() => schedulesStore.loading)
const error = computed(() => schedulesStore.error)
const schedules = computed(() => schedulesStore.schedules)
const filteredSchedules = computed(() => schedulesStore.filteredSchedules)
const totalSchedules = computed(() => schedulesStore.totalSchedules)
const activeSchedules = computed(() => schedulesStore.activeSchedules)
const pausedSchedules = computed(() => schedulesStore.pausedSchedules)
const overdueSchedules = computed(() => schedulesStore.overdueSchedules)
const upcomingExecutions = computed(() => schedulesStore.upcomingExecutions)
const technicians = computed(() => schedulesStore.technicians)
const availableAssets = computed(() => schedulesStore.availableAssets)

// Search and filters
const searchTerm = computed({
  get: () => schedulesStore.searchTerm,
  set: (value) => schedulesStore.setSearchTerm(value)
})

const filters = computed({
  get: () => schedulesStore.filters,
  set: (value) => schedulesStore.setFilters(value)
})

// Methods
const openCreateModal = () => {
  editingSchedule.value = null
  resetForm()
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  editingSchedule.value = null
  resetForm()
}

const openViewModal = () => {
  showViewModal.value = true
}

const closeViewModal = () => {
  showViewModal.value = false
  selectedSchedule.value = null
}

const resetForm = () => {
  scheduleForm.value = {
    title: '',
    description: '',
    type: '',
    frequency: '',
    priority: '',
    assetId: '',
    assignedTo: '',
    startDate: '',
    estimatedDuration: '',
    notes: ''
  }
}

const viewSchedule = (schedule) => {
  selectedSchedule.value = schedule
  openViewModal()
}

const editSchedule = (schedule) => {
  editingSchedule.value = schedule
  
  // Populate form with schedule data
  const selectedAsset = availableAssets.value.find(asset => asset.id === schedule.assetId)
  
  scheduleForm.value = {
    title: schedule.title,
    description: schedule.description,
    type: schedule.type,
    frequency: schedule.frequency,
    priority: schedule.priority,
    assetId: schedule.assetId,
    assignedTo: schedule.assignedTo,
    startDate: schedule.startDate,
    estimatedDuration: schedule.estimatedDuration,
    notes: schedule.notes || ''
  }
  
  closeViewModal()
  showCreateModal.value = true
}

const saveSchedule = async () => {
  try {
    const selectedAsset = availableAssets.value.find(asset => asset.id === scheduleForm.value.assetId)
    
    const scheduleData = {
      ...scheduleForm.value,
      assetCode: selectedAsset?.code || '',
      assetName: selectedAsset?.name || '',
      department: 'TI',
      nextExecution: scheduleForm.value.startDate
    }

    if (editingSchedule.value) {
      await schedulesStore.updateSchedule(editingSchedule.value.id, scheduleData)
      successMessage.value = 'Agendamento atualizado com sucesso!'
    } else {
      await schedulesStore.createSchedule(scheduleData)
      successMessage.value = 'Agendamento criado com sucesso!'
    }

    closeCreateModal()
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    logger.error('Erro ao salvar agendamento:', error)
  }
}

const toggleScheduleStatus = async (id) => {
  try {
    await schedulesStore.toggleScheduleStatus(id)
    successMessage.value = 'Status do agendamento alterado com sucesso!'
    
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    logger.error('Erro ao alterar status:', error)
  }
}

const executeSchedule = async (id) => {
  try {
    const notes = prompt('Observações sobre a execução (opcional):')
    if (notes !== null) { // User didn't cancel
      await schedulesStore.executeSchedule(id, notes)
      successMessage.value = 'Agendamento executado com sucesso!'
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    }
  } catch (error) {
    logger.error('Erro ao executar agendamento:', error)
  }
}

const exportSchedules = async () => {
  try {
    await schedulesStore.exportSchedules()
    successMessage.value = 'Dados exportados com sucesso!'
    
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    logger.error('Erro ao exportar dados:', error)
  }
}

const clearFilters = () => {
  schedulesStore.clearFilters()
}

// Label methods
const getStatusLabel = (status) => schedulesStore.getStatusLabel(status)
const getTypeLabel = (type) => schedulesStore.getTypeLabel(type)
const getFrequencyLabel = (frequency) => schedulesStore.getFrequencyLabel(frequency)
const getPriorityLabel = (priority) => schedulesStore.getPriorityLabel(priority)

// Date formatting
const formatDate = (dateString, format = 'DD/MM/YYYY') => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  
  if (format === 'DD') {
    return date.getDate().toString().padStart(2, '0')
  }
  
  if (format === 'MMM') {
    const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return months[date.getMonth()]
  }
  
  return date.toLocaleDateString('pt-BR')
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR')
}

const calculateDuration = (startDate, endDate) => {
  if (!startDate || !endDate) return 'N/A'
  
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffMs = end - start
  const diffHours = Math.round(diffMs / (1000 * 60 * 60) * 10) / 10
  
  return `${diffHours}h`
}

// Watchers
watch(error, (newError) => {
  if (newError) {
    setTimeout(() => {
      schedulesStore.error = null
    }, 5000)
  }
})

// Lifecycle
onMounted(async () => {
  try {
    await schedulesStore.fetchSchedules()
  } catch (error) {
    logger.error('Erro ao carregar agendamentos:', error)
  }
})
</script>

<style scoped>
.schedule-page {
  padding: 0;
}

/* Header */
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

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.header-text h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.header-text p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--spacing-md);
  font-size: 1.25rem;
  color: white;
}

.stat-icon.primary { background-color: var(--primary-color); }
.stat-icon.success { background-color: var(--success-color); }
.stat-icon.warning { background-color: var(--warning-color); }
.stat-icon.danger { background-color: var(--danger-color); }

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: var(--spacing-xs);
}

/* Filters */
.filters-section {
  margin-bottom: var(--spacing-xl);
}

.filters-row {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  min-width: 200px;
}

.search-input,
.filter-select {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
}

.search-input:focus,
.filter-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Upcoming Executions */
.upcoming-section {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
}

.upcoming-list {
  display: flex;
  gap: var(--spacing-md);
  overflow-x: auto;
  padding-bottom: var(--spacing-sm);
}

.upcoming-item {
  display: flex;
  align-items: center;
  min-width: 350px;
  padding: var(--spacing-md);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--primary-color);
}

.upcoming-date {
  text-align: center;
  margin-right: var(--spacing-md);
  min-width: 60px;
}

.date-day {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  line-height: 1;
}

.date-month {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-top: var(--spacing-xs);
}

.upcoming-content {
  flex: 1;
  margin-right: var(--spacing-md);
}

.upcoming-title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.upcoming-details {
  display: flex;
  gap: var(--spacing-sm);
  font-size: 0.75rem;
  color: var(--text-muted);
}

.upcoming-asset,
.upcoming-tech,
.upcoming-duration {
  padding: 2px 6px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

/* Table */
.table-section {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background-color: var(--bg-secondary);
  padding: var(--spacing-md);
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
}

.data-table td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  vertical-align: top;
}

.data-table tr:hover {
  background-color: var(--bg-secondary);
}

.schedule-code {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--primary-color);
}

.schedule-title .title {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.schedule-title .description {
  font-size: 0.875rem;
  color: var(--text-muted);
  line-height: 1.4;
}

.asset-info .asset-code {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--text-primary);
}

.asset-info .asset-name {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: var(--spacing-xs);
}

.date-info .next-date {
  font-weight: 600;
  color: var(--text-primary);
}

.date-info .last-date {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: var(--spacing-xs);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
}

.action-buttons .btn {
  padding: var(--spacing-xs);
  min-width: auto;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge-active,
.badge-preventive { 
  background-color: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

.badge-paused,
.badge-corrective { 
  background-color: rgba(251, 191, 36, 0.1);
  color: rgb(251, 191, 36);
}

.badge-inactive { 
  background-color: rgba(107, 114, 128, 0.1);
  color: rgb(107, 114, 128);
}

.badge-low { 
  background-color: rgba(59, 130, 246, 0.1);
  color: rgb(59, 130, 246);
}

.badge-medium { 
  background-color: rgba(251, 191, 36, 0.1);
  color: rgb(251, 191, 36);
}

.badge-high { 
  background-color: rgba(249, 115, 22, 0.1);
  color: rgb(249, 115, 22);
}

.badge-urgent { 
  background-color: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
}

.badge-success { 
  background-color: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 2rem;
  margin-bottom: var(--spacing-lg);
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-lg);
}

.modal-content {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.modal-large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: var(--text-muted);
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  transition: background-color 0.2s ease;
}

.modal-close:hover {
  background-color: var(--bg-secondary);
}

.modal-body {
  padding: var(--spacing-lg);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

/* Form */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Schedule Details */
.schedule-details {
  max-width: 100%;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: var(--spacing-xs);
}

.detail-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.detail-section {
  margin-bottom: var(--spacing-lg);
}

.detail-section label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: var(--spacing-sm);
}

.detail-section p {
  color: var(--text-primary);
  line-height: 1.6;
  margin: 0;
}

/* Execution History */
.execution-history {
  space-y: var(--spacing-md);
}

.execution-item {
  padding: var(--spacing-md);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-md);
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.execution-date {
  font-weight: 600;
  color: var(--text-primary);
}

.execution-details p {
  margin: var(--spacing-xs) 0;
  font-size: 0.875rem;
  color: var(--text-primary);
}

/* Alerts */
.alert {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-weight: 500;
  z-index: 1001;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
}

.alert-success {
  background-color: rgba(34, 197, 94, 0.1);
  color: rgb(34, 197, 94);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: rgb(239, 68, 68);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    min-width: auto;
  }

  .upcoming-list {
    flex-direction: column;
  }

  .upcoming-item {
    min-width: auto;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    margin: var(--spacing-md);
    max-width: none;
  }
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