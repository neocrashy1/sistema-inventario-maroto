<template>
  <div class="sla-contracts-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>Contratos SLA</h1>
          <p>Gerenciamento de contratos de nível de serviço</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="exportContracts">
            <i class="fas fa-download"></i>
            Exportar
          </button>
          <button class="btn btn-primary" @click="openCreateModal">
            <i class="fas fa-plus"></i>
            Novo Contrato
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary">
          <i class="fas fa-file-contract"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">Total de Contratos</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.active }}</div>
          <div class="stat-label">Contratos Ativos</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">Pendentes</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon danger">
          <i class="fas fa-times-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.expired }}</div>
          <div class="stat-label">Expirados</div>
        </div>
      </div>
    </div>

    <!-- Expiring Contracts Alert -->
    <div v-if="expiringContracts.length > 0" class="expiring-alert">
      <div class="alert-header">
        <i class="fas fa-exclamation-triangle"></i>
        <span>Contratos próximos ao vencimento</span>
      </div>
      <div class="expiring-list">
        <div v-for="contract in expiringContracts" :key="contract.id" class="expiring-item">
          <span class="contract-title">{{ contract.title }}</span>
          <span class="expiry-date">Vence em {{ calculateDaysUntilExpiry(contract.endDate) }} dias</span>
          <button class="btn btn-sm btn-primary" @click="openRenewModal(contract)">
            Renovar
          </button>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Buscar contratos..."
            class="search-input"
          />
        </div>
        
        <div class="filter-group">
          <select v-model="filters.status" class="filter-select">
            <option value="">Todos os Status</option>
            <option value="active">Ativo</option>
            <option value="pending">Pendente</option>
            <option value="expired">Expirado</option>
            <option value="suspended">Suspenso</option>
          </select>
        </div>
        
        <div class="filter-group">
          <select v-model="filters.type" class="filter-select">
            <option value="">Todos os Tipos</option>
            <option value="preventive">Preventiva</option>
            <option value="corrective">Corretiva</option>
            <option value="predictive">Preditiva</option>
            <option value="emergency">Emergencial</option>
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
        
        <button class="btn btn-secondary" @click="clearFilters">
          <i class="fas fa-times"></i>
          Limpar
        </button>
      </div>
    </div>

    <!-- Contracts Table -->
    <div class="table-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Carregando contratos...</p>
      </div>
      
      <div v-else-if="filteredContracts.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fas fa-file-contract"></i>
        </div>
        <h3>Nenhum contrato encontrado</h3>
        <p>Não há contratos que correspondam aos filtros aplicados.</p>
      </div>
      
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Título</th>
              <th>Cliente</th>
              <th>Fornecedor</th>
              <th>Tipo</th>
              <th>Status</th>
              <th>Prioridade</th>
              <th>Vigência</th>
              <th>SLA</th>
              <th>Compliance</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="contract in filteredContracts" :key="contract.id">
              <td>
                <span class="contract-code">{{ contract.id }}</span>
              </td>
              <td>
                <div class="contract-title">
                  <div class="title">{{ contract.title }}</div>
                  <div class="description">{{ contract.description }}</div>
                </div>
              </td>
              <td>{{ contract.client }}</td>
              <td>{{ contract.provider }}</td>
              <td>
                <span :class="`badge badge-${contract.type}`">
                  {{ getTypeLabel(contract.type) }}
                </span>
              </td>
              <td>
                <span :class="`badge badge-${contract.status}`">
                  {{ getStatusLabel(contract.status) }}
                </span>
              </td>
              <td>
                <span :class="`badge badge-${contract.priority}`">
                  {{ getPriorityLabel(contract.priority) }}
                </span>
              </td>
              <td>
                <div class="date-info">
                  <div class="start-date">{{ formatDate(contract.startDate) }}</div>
                  <div class="end-date">até {{ formatDate(contract.endDate) }}</div>
                </div>
              </td>
              <td>
                <div class="sla-info">
                  <div class="response-time">Resp: {{ contract.responseTime }}h</div>
                  <div class="resolution-time">Res: {{ contract.resolutionTime }}h</div>
                  <div class="availability">Disp: {{ contract.availability }}%</div>
                </div>
              </td>
              <td>
                <div class="compliance-info">
                  <div class="response-compliance">
                    {{ contract.metrics.responseTimeCompliance.toFixed(1) }}%
                  </div>
                  <div class="resolution-compliance">
                    {{ contract.metrics.resolutionTimeCompliance.toFixed(1) }}%
                  </div>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn btn-sm btn-secondary" 
                    @click="viewContract(contract)"
                    title="Visualizar"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-primary" 
                    @click="editContract(contract)"
                    title="Editar"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    v-if="contract.status === 'active'"
                    class="btn btn-sm btn-success" 
                    @click="openRenewModal(contract)"
                    title="Renovar"
                  >
                    <i class="fas fa-redo"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-danger" 
                    @click="deleteContract(contract.id)"
                    title="Excluir"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Contract Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h3>{{ editingContract ? 'Editar Contrato' : 'Novo Contrato' }}</h3>
          <button class="modal-close" @click="closeCreateModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveContract">
            <div class="form-row">
              <div class="form-group">
                <label>Título *</label>
                <input
                  v-model="contractForm.title"
                  type="text"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="contractForm.type" class="form-select" required>
                  <option value="">Selecione o tipo</option>
                  <option value="preventive">Preventiva</option>
                  <option value="corrective">Corretiva</option>
                  <option value="predictive">Preditiva</option>
                  <option value="emergency">Emergencial</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label>Descrição</label>
              <textarea
                v-model="contractForm.description"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Cliente *</label>
                <input
                  v-model="contractForm.client"
                  type="text"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label>Fornecedor *</label>
                <input
                  v-model="contractForm.provider"
                  type="text"
                  class="form-input"
                  required
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Prioridade *</label>
                <select v-model="contractForm.priority" class="form-select" required>
                  <option value="">Selecione a prioridade</option>
                  <option value="low">Baixa</option>
                  <option value="medium">Média</option>
                  <option value="high">Alta</option>
                  <option value="urgent">Urgente</option>
                </select>
              </div>
              <div class="form-group">
                <label>Status *</label>
                <select v-model="contractForm.status" class="form-select" required>
                  <option value="">Selecione o status</option>
                  <option value="active">Ativo</option>
                  <option value="pending">Pendente</option>
                  <option value="suspended">Suspenso</option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Data de Início *</label>
                <input
                  v-model="contractForm.startDate"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label>Data de Fim *</label>
                <input
                  v-model="contractForm.endDate"
                  type="date"
                  class="form-input"
                  required
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Tempo de Resposta (horas) *</label>
                <input
                  v-model.number="contractForm.responseTime"
                  type="number"
                  class="form-input"
                  min="1"
                  required
                />
              </div>
              <div class="form-group">
                <label>Tempo de Resolução (horas) *</label>
                <input
                  v-model.number="contractForm.resolutionTime"
                  type="number"
                  class="form-input"
                  min="1"
                  required
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Disponibilidade (%) *</label>
                <input
                  v-model.number="contractForm.availability"
                  type="number"
                  class="form-input"
                  min="0"
                  max="100"
                  step="0.1"
                  required
                />
              </div>
              <div class="form-group">
                <label>Taxa de Penalidade (%) *</label>
                <input
                  v-model.number="contractForm.penaltyRate"
                  type="number"
                  class="form-input"
                  min="0"
                  step="0.1"
                  required
                />
              </div>
            </div>
            
            <div class="form-group">
              <label>Custo (R$) *</label>
              <input
                v-model.number="contractForm.cost"
                type="number"
                class="form-input"
                min="0"
                step="0.01"
                required
              />
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeCreateModal">
            Cancelar
          </button>
          <button type="submit" class="btn btn-primary" @click="saveContract">
            {{ editingContract ? 'Atualizar' : 'Criar' }} Contrato
          </button>
        </div>
      </div>
    </div>

    <!-- View Contract Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h3>Detalhes do Contrato</h3>
          <button class="modal-close" @click="closeViewModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="selectedContract" class="contract-details">
            <div class="details-grid">
              <div class="detail-item">
                <label>Código</label>
                <span>{{ selectedContract.id }}</span>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <span :class="`badge badge-${selectedContract.status}`">
                  {{ getStatusLabel(selectedContract.status) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Tipo</label>
                <span :class="`badge badge-${selectedContract.type}`">
                  {{ getTypeLabel(selectedContract.type) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Prioridade</label>
                <span :class="`badge badge-${selectedContract.priority}`">
                  {{ getPriorityLabel(selectedContract.priority) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Cliente</label>
                <span>{{ selectedContract.client }}</span>
              </div>
              <div class="detail-item">
                <label>Fornecedor</label>
                <span>{{ selectedContract.provider }}</span>
              </div>
              <div class="detail-item">
                <label>Data de Início</label>
                <span>{{ formatDate(selectedContract.startDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Data de Fim</label>
                <span>{{ formatDate(selectedContract.endDate) }}</span>
              </div>
            </div>
            
            <div class="detail-section">
              <label>Descrição</label>
              <p>{{ selectedContract.description }}</p>
            </div>
            
            <div class="detail-section">
              <label>Métricas de Performance</label>
              <div class="metrics-grid">
                <div class="metric-item">
                  <span class="metric-label">Compliance Tempo Resposta</span>
                  <span class="metric-value">{{ selectedContract.metrics.responseTimeCompliance.toFixed(1) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Compliance Tempo Resolução</span>
                  <span class="metric-value">{{ selectedContract.metrics.resolutionTimeCompliance.toFixed(1) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Disponibilidade Atingida</span>
                  <span class="metric-value">{{ selectedContract.metrics.availabilityAchieved.toFixed(1) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Total de Incidentes</span>
                  <span class="metric-value">{{ selectedContract.metrics.totalIncidents }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Incidentes Resolvidos</span>
                  <span class="metric-value">{{ selectedContract.metrics.resolvedIncidents }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">Penalidades Aplicadas</span>
                  <span class="metric-value">{{ formatCurrency(selectedContract.metrics.penaltiesApplied) }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <label>Termos do Contrato</label>
              <ul class="terms-list">
                <li v-for="term in selectedContract.terms" :key="term">{{ term }}</li>
              </ul>
            </div>
            
            <div class="detail-section">
              <label>Escalação</label>
              <div class="escalation-list">
                <div v-for="escalation in selectedContract.escalation" :key="escalation.level" class="escalation-item">
                  <span class="escalation-level">Nível {{ escalation.level }}</span>
                  <span class="escalation-time">{{ escalation.time }}h</span>
                  <span class="escalation-contact">{{ escalation.contact }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeViewModal">
            Fechar
          </button>
          <button type="button" class="btn btn-primary" @click="editContract(selectedContract)">
            Editar Contrato
          </button>
        </div>
      </div>
    </div>

    <!-- Renew Contract Modal -->
    <div v-if="showRenewModal" class="modal-overlay" @click="closeRenewModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Renovar Contrato</h3>
          <button class="modal-close" @click="closeRenewModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="renewingContract">
            <p><strong>Contrato:</strong> {{ renewingContract.title }}</p>
            <p><strong>Vencimento Atual:</strong> {{ formatDate(renewingContract.endDate) }}</p>
            
            <div class="form-group">
              <label>Nova Data de Vencimento *</label>
              <input
                v-model="renewForm.endDate"
                type="date"
                class="form-input"
                required
              />
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeRenewModal">
            Cancelar
          </button>
          <button type="button" class="btn btn-primary" @click="renewContract">
            Renovar Contrato
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
    
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useSLAContractsStore } from '@/stores/slaContracts'

// Store
const slaStore = useSLAContractsStore()

// Reactive state
const showCreateModal = ref(false)
const showViewModal = ref(false)
const showRenewModal = ref(false)
const editingContract = ref(null)
const selectedContract = ref(null)
const renewingContract = ref(null)
const successMessage = ref('')
const errorMessage = ref('')

// Form data
const contractForm = ref({
  title: '',
  description: '',
  type: '',
  client: '',
  provider: '',
  priority: '',
  status: '',
  startDate: '',
  endDate: '',
  responseTime: 4,
  resolutionTime: 24,
  availability: 99.5,
  penaltyRate: 0.1,
  cost: 0
})

const renewForm = ref({
  endDate: ''
})

// Computed properties from store
const loading = computed(() => slaStore.loading)
const error = computed(() => slaStore.error)
const contracts = computed(() => slaStore.contracts)
const filteredContracts = computed(() => slaStore.filteredContracts)
const expiringContracts = computed(() => slaStore.expiringContracts)
const stats = computed(() => slaStore.stats)

// Search and filters
const searchTerm = computed({
  get: () => slaStore.searchTerm,
  set: (value) => slaStore.setFilters({ searchTerm: value })
})

const filters = computed({
  get: () => slaStore.filters,
  set: (value) => slaStore.setFilters(value)
})

// Methods
const openCreateModal = () => {
  editingContract.value = null
  resetForm()
  showCreateModal.value = true
}

const openEditModal = (contract) => {
  editingContract.value = contract
  contractForm.value = {
    title: contract.title,
    description: contract.description,
    type: contract.type,
    client: contract.client,
    provider: contract.provider,
    priority: contract.priority,
    status: contract.status,
    startDate: contract.startDate,
    endDate: contract.endDate,
    responseTime: contract.responseTime,
    resolutionTime: contract.resolutionTime,
    availability: contract.availability,
    penaltyRate: contract.penaltyRate,
    cost: contract.cost
  }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
  editingContract.value = null
  resetForm()
}

const openViewModal = (contract) => {
  selectedContract.value = contract
  showViewModal.value = true
}

const closeViewModal = () => {
  showViewModal.value = false
  selectedContract.value = null
}

const openRenewModal = (contract) => {
  renewingContract.value = contract
  renewForm.value.endDate = ''
  showRenewModal.value = true
}

const closeRenewModal = () => {
  showRenewModal.value = false
  renewingContract.value = null
  renewForm.value.endDate = ''
}

const resetForm = () => {
  contractForm.value = {
    title: '',
    description: '',
    type: '',
    client: '',
    provider: '',
    priority: '',
    status: '',
    startDate: '',
    endDate: '',
    responseTime: 4,
    resolutionTime: 24,
    availability: 99.5,
    penaltyRate: 0.1,
    cost: 0
  }
}

const viewContract = (contract) => {
  openViewModal(contract)
}

const editContract = (contract) => {
  closeViewModal()
  openEditModal(contract)
}

const saveContract = async () => {
  try {
    if (editingContract.value) {
      await slaStore.updateContract(editingContract.value.id, contractForm.value)
      successMessage.value = 'Contrato atualizado com sucesso!'
    } else {
      await slaStore.createContract(contractForm.value)
      successMessage.value = 'Contrato criado com sucesso!'
    }
    closeCreateModal()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = 'Erro ao salvar contrato: ' + error.message
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  }
}

const deleteContract = async (contractId) => {
  if (confirm('Tem certeza que deseja excluir este contrato?')) {
    try {
      await slaStore.deleteContract(contractId)
      successMessage.value = 'Contrato excluído com sucesso!'
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } catch (error) {
      errorMessage.value = 'Erro ao excluir contrato: ' + error.message
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }
  }
}

const renewContract = async () => {
  try {
    await slaStore.renewContract(renewingContract.value.id, renewForm.value.endDate)
    successMessage.value = 'Contrato renovado com sucesso!'
    closeRenewModal()
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = 'Erro ao renovar contrato: ' + error.message
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  }
}

const exportContracts = () => {
  slaStore.exportContracts()
  successMessage.value = 'Dados exportados com sucesso!'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

const clearFilters = () => {
  slaStore.clearFilters()
}

// Label getters
const getStatusLabel = (status) => slaStore.getStatusLabel(status)
const getTypeLabel = (type) => slaStore.getTypeLabel(type)
const getPriorityLabel = (priority) => slaStore.getPriorityLabel(priority)

// Utility functions
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR')
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const calculateDaysUntilExpiry = (endDate) => {
  const today = new Date()
  const expiry = new Date(endDate)
  const diffTime = expiry - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

// Watchers
watch(error, (newError) => {
  if (newError) {
    errorMessage.value = newError
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  }
})

// Lifecycle
onMounted(() => {
  slaStore.fetchContracts()
})
</script>

<style scoped>
.sla-contracts-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.header-text h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  font-weight: 600;
}

.header-text p {
  margin: 0.5rem 0 0 0;
  color: #6b7280;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.primary {
  background-color: #dbeafe;
  color: #3b82f6;
}

.stat-icon.success {
  background-color: #dcfce7;
  color: #16a34a;
}

.stat-icon.warning {
  background-color: #fef3c7;
  color: #d97706;
}

.stat-icon.danger {
  background-color: #fee2e2;
  color: #dc2626;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Expiring Contracts Alert */
.expiring-alert {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 2rem;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #92400e;
  font-weight: 600;
  margin-bottom: 1rem;
}

.expiring-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.expiring-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #f59e0b;
}

.contract-title {
  font-weight: 500;
  color: #1f2937;
}

.expiry-date {
  color: #92400e;
  font-size: 0.875rem;
}

/* Filters */
.filters-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.filters-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.search-input,
.filter-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.search-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Table Section */
.table-section {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
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
  background-color: #f9fafb;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}

.data-table tr:hover {
  background-color: #f9fafb;
}

.contract-code {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.contract-title .title {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.contract-title .description {
  color: #6b7280;
  font-size: 0.875rem;
}

.date-info .start-date {
  color: #1f2937;
  font-size: 0.875rem;
}

.date-info .end-date {
  color: #6b7280;
  font-size: 0.75rem;
}

.sla-info {
  font-size: 0.75rem;
}

.sla-info > div {
  margin-bottom: 0.25rem;
}

.response-time {
  color: #059669;
}

.resolution-time {
  color: #dc2626;
}

.availability {
  color: #3b82f6;
}

.compliance-info {
  font-size: 0.75rem;
}

.compliance-info > div {
  margin-bottom: 0.25rem;
}

.response-compliance {
  color: #059669;
}

.resolution-compliance {
  color: #dc2626;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-active {
  background-color: #dcfce7;
  color: #166534;
}

.badge-pending {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-expired {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-suspended {
  background-color: #f3f4f6;
  color: #374151;
}

.badge-preventive {
  background-color: #dbeafe;
  color: #1e40af;
}

.badge-corrective {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-predictive {
  background-color: #e0e7ff;
  color: #5b21b6;
}

.badge-emergency {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-low {
  background-color: #f0fdf4;
  color: #166534;
}

.badge-medium {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-high {
  background-color: #fed7aa;
  color: #c2410c;
}

.badge-urgent {
  background-color: #fee2e2;
  color: #991b1b;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
  font-size: 0.875rem;
}

.btn-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover {
  background-color: #059669;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
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
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

/* Forms */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* Contract Details */
.contract-details {
  max-height: 60vh;
  overflow-y: auto;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-weight: 600;
  color: #374151;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-item span {
  color: #1f2937;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section > label {
  display: block;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-section p {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metric-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.metric-value {
  font-weight: 600;
  color: #1f2937;
}

.terms-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.terms-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
  color: #6b7280;
}

.terms-list li:last-child {
  border-bottom: none;
}

.escalation-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.escalation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f9fafb;
  padding: 0.75rem;
  border-radius: 0.5rem;
}

.escalation-level {
  font-weight: 600;
  color: #1f2937;
}

.escalation-time {
  color: #dc2626;
  font-size: 0.875rem;
}

.escalation-contact {
  color: #6b7280;
  font-size: 0.875rem;
}

/* Alerts */
.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  position: fixed;
  top: 2rem;
  right: 2rem;
  z-index: 1100;
  min-width: 300px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.alert-success {
  background-color: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sla-contracts-page {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-row {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: auto;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .expiring-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .escalation-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>