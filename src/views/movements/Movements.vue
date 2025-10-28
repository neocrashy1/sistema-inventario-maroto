<template>
  <div class="movements">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Movimentações</h1>
        <p class="page-subtitle">Histórico e controle de movimentações de ativos</p>
      </div>
      
      <div class="page-actions">
        <button class="btn btn-secondary" @click="exportMovements">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button class="btn btn-primary" @click="showAddModal = true">
          <i class="fas fa-plus"></i>
          Nova Movimentação
        </button>
      </div>
    </div>
    
    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary">
          <i class="fas fa-exchange-alt"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Total de Movimentações</div>
          <div class="stat-value">{{ movements.length }}</div>
          <div class="stat-change positive">
            <i class="fas fa-arrow-up"></i>
            +15% este mês
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Pendentes</div>
          <div class="stat-value">{{ pendingMovements }}</div>
          <div class="stat-change neutral">
            <i class="fas fa-minus"></i>
            Sem alteração
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="fas fa-check"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Concluídas</div>
          <div class="stat-value">{{ completedMovements }}</div>
          <div class="stat-change positive">
            <i class="fas fa-arrow-up"></i>
            +8% este mês
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Atrasadas</div>
          <div class="stat-value">{{ overdueMovements }}</div>
          <div class="stat-change negative">
            <i class="fas fa-arrow-down"></i>
            -5% este mês
          </div>
        </div>
      </div>
    </div>
    
    <!-- Filters Section -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <label>Buscar</label>
          <div class="search-input">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              placeholder="Buscar por ativo, responsável ou observações..."
              v-model="searchQuery"
              @input="applyFilters"
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label>Tipo</label>
          <select v-model="selectedType" @change="applyFilters">
            <option value="">Todos os tipos</option>
            <option value="Transferência">Transferência</option>
            <option value="Empréstimo">Empréstimo</option>
            <option value="Devolução">Devolução</option>
            <option value="Manutenção">Manutenção</option>
            <option value="Descarte">Descarte</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="selectedStatus" @change="applyFilters">
            <option value="">Todos os status</option>
            <option value="Pendente">Pendente</option>
            <option value="Em Andamento">Em Andamento</option>
            <option value="Concluída">Concluída</option>
            <option value="Cancelada">Cancelada</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Período</label>
          <select v-model="selectedPeriod" @change="applyFilters">
            <option value="">Todos os períodos</option>
            <option value="today">Hoje</option>
            <option value="week">Esta semana</option>
            <option value="month">Este mês</option>
            <option value="quarter">Este trimestre</option>
          </select>
        </div>
        
        <button class="btn btn-outline" @click="clearFilters">
          <i class="fas fa-times"></i>
          Limpar
        </button>
      </div>
    </div>
    
    <!-- Movements Table -->
    <div class="table-container">
      <div class="table-header">
        <div class="table-info">
          <span class="results-count">
            {{ filteredMovements.length }} de {{ movements.length }} movimentações
          </span>
        </div>
        
        <div class="table-actions">
          <button class="btn btn-outline btn-sm" @click="refreshData">
            <i class="fas fa-sync-alt"></i>
            Atualizar
          </button>
        </div>
      </div>
      
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Ativo</th>
              <th>Tipo</th>
              <th>Origem</th>
              <th>Destino</th>
              <th>Responsável</th>
              <th>Data</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="movement in paginatedMovements" :key="movement.id">
              <td>
                <span class="movement-id">#{{ movement.id }}</span>
              </td>
              <td>
                <div class="asset-info">
                  <span class="asset-name">{{ movement.asset.name }}</span>
                  <span class="asset-code">{{ movement.asset.code }}</span>
                </div>
              </td>
              <td>
                <span class="badge badge-secondary">{{ movement.type }}</span>
              </td>
              <td>{{ movement.origin }}</td>
              <td>{{ movement.destination }}</td>
              <td>
                <div class="user-info">
                  <span class="user-name">{{ movement.responsible.name }}</span>
                  <span class="user-email">{{ movement.responsible.email }}</span>
                </div>
              </td>
              <td>
                <div class="date-info">
                  <span class="date">{{ formatDate(movement.date) }}</span>
                  <span class="time">{{ formatTime(movement.date) }}</span>
                </div>
              </td>
              <td>
                <span class="badge" :class="getStatusClass(movement.status)">
                  {{ movement.status }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="viewMovement(movement)" title="Visualizar">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="movement.status === 'Pendente'"
                    class="btn-icon" 
                    @click="approveMovement(movement)" 
                    title="Aprovar"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button 
                    v-if="movement.status !== 'Concluída'"
                    class="btn-icon danger" 
                    @click="cancelMovement(movement)" 
                    title="Cancelar"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                  <button 
                    class="btn-icon" 
                    @click="openEditModal(movement)" 
                    title="Editar"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div class="pagination-container">
        <div class="pagination-info">
          Mostrando {{ (currentPage - 1) * itemsPerPage + 1 }} a 
          {{ Math.min(currentPage * itemsPerPage, filteredMovements.length) }} 
          de {{ filteredMovements.length }} resultados
        </div>
        
        <div class="pagination">
          <button 
            class="btn btn-outline btn-sm" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            <i class="fas fa-chevron-left"></i>
            Anterior
          </button>
          
          <div class="page-numbers">
            <button 
              v-for="page in visiblePages" 
              :key="page"
              class="btn btn-sm"
              :class="{ 'btn-primary': page === currentPage, 'btn-outline': page !== currentPage }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="btn btn-outline btn-sm" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            Próximo
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Add Movement Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Nova Movimentação</h2>
          <button class="btn-icon" @click="showAddModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="addMovement">
            <div class="form-group">
              <label>Ativo *</label>
              <select v-model="newMovement.assetId" required>
                <option value="">Selecione um ativo</option>
                <option v-for="asset in availableAssets" :key="asset.id" :value="asset.id">
                  {{ asset.name }} ({{ asset.code }})
                </option>
              </select>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="newMovement.type" required>
                  <option value="">Selecione o tipo</option>
                  <option value="Transferência">Transferência</option>
                  <option value="Empréstimo">Empréstimo</option>
                  <option value="Devolução">Devolução</option>
                  <option value="Manutenção">Manutenção</option>
                  <option value="Descarte">Descarte</option>
                </select>
              </div>
              <div class="form-group">
                <label>Data *</label>
                <input type="datetime-local" v-model="newMovement.date" required>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Origem *</label>
                <input type="text" v-model="newMovement.origin" required>
              </div>
              <div class="form-group">
                <label>Destino *</label>
                <input type="text" v-model="newMovement.destination" required>
              </div>
            </div>
            
            <div class="form-group">
              <label>Responsável *</label>
              <input type="text" v-model="newMovement.responsibleName" required>
            </div>
            
            <div class="form-group">
              <label>Observações</label>
              <textarea v-model="newMovement.notes" rows="3" placeholder="Observações sobre a movimentação..."></textarea>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showAddModal = false">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i>
                Registrar Movimentação
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Movement Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Editar Movimentação #{{ editMovement.id }}</h2>
          <button class="btn-icon" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="updateMovement">
            <div class="form-group">
              <label>Ativo *</label>
              <select v-model="editMovement.assetId" required>
                <option value="">Selecione um ativo</option>
                <option v-for="asset in availableAssets" :key="asset.id" :value="asset.id">
                  {{ asset.name }} ({{ asset.code }})
                </option>
              </select>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="editMovement.type" required>
                  <option value="Transferência">Transferência</option>
                  <option value="Empréstimo">Empréstimo</option>
                  <option value="Devolução">Devolução</option>
                  <option value="Manutenção">Manutenção</option>
                  <option value="Descarte">Descarte</option>
                </select>
              </div>
              <div class="form-group">
                <label>Data *</label>
                <input type="datetime-local" v-model="editMovement.date" required>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Origem *</label>
                <input type="text" v-model="editMovement.origin" required>
              </div>
              <div class="form-group">
                <label>Destino *</label>
                <input type="text" v-model="editMovement.destination" required>
              </div>
            </div>
            
            <div class="form-group">
              <label>Responsável *</label>
              <input type="text" v-model="editMovement.responsibleName" required>
            </div>
            
            <div class="form-group">
              <label>Status</label>
              <select v-model="editMovement.status">
                <option value="Pendente">Pendente</option>
                <option value="Em Andamento">Em Andamento</option>
                <option value="Concluída">Concluída</option>
                <option value="Cancelada">Cancelada</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Observações</label>
              <textarea v-model="editMovement.notes" rows="3" placeholder="Observações sobre a movimentação..."></textarea>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="closeEditModal">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i>
                Salvar Alterações
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted } from 'vue'
import { useAssetsStore } from '@/stores/assets'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const assetsStore = useAssetsStore()

// Reactive data
const searchQuery = ref('')
const selectedType = ref('')
const selectedStatus = ref('')
const selectedPeriod = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editMovement = ref({
  id: '',
  assetId: '',
  type: '',
  origin: '',
  destination: '',
  responsibleName: '',
  date: '',
  status: 'Pendente',
  notes: ''
})

// Mock movements data
const movements = ref([
  {
    id: 1,
    asset: { id: 1, name: 'Notebook Dell Inspiron', code: 'LVT-001' },
    type: 'Transferência',
    origin: 'TI - Sala 101',
    destination: 'TI - Sala 102',
    responsible: { name: 'João Silva', email: 'joao@levitiis.com' },
    date: new Date('2024-01-15T10:30:00'),
    status: 'Concluída',
    notes: 'Transferência para novo colaborador'
  },
  {
    id: 2,
    asset: { id: 2, name: 'Monitor Samsung 24"', code: 'LVT-002' },
    type: 'Empréstimo',
    origin: 'Almoxarifado',
    destination: 'Administração',
    responsible: { name: 'Maria Santos', email: 'maria@levitiis.com' },
    date: new Date('2024-01-14T14:15:00'),
    status: 'Em Andamento',
    notes: 'Empréstimo temporário para apresentação'
  },
  {
    id: 3,
    asset: { id: 3, name: 'Impressora HP LaserJet', code: 'LVT-003' },
    type: 'Manutenção',
    origin: 'TI - Sala 102',
    destination: 'Oficina Externa',
    responsible: { name: 'Carlos Oliveira', email: 'carlos@levitiis.com' },
    date: new Date('2024-01-13T09:00:00'),
    status: 'Pendente',
    notes: 'Manutenção preventiva programada'
  },
  {
    id: 4,
    asset: { id: 4, name: 'Teclado Mecânico', code: 'LVT-004' },
    type: 'Devolução',
    origin: 'Home Office',
    destination: 'TI - Sala 101',
    responsible: { name: 'Ana Costa', email: 'ana@levitiis.com' },
    date: new Date('2024-01-12T16:45:00'),
    status: 'Concluída',
    notes: 'Retorno do home office'
  },
  {
    id: 5,
    asset: { id: 5, name: 'Cadeira Ergonômica', code: 'LVT-005' },
    type: 'Transferência',
    origin: 'Administração',
    destination: 'TI - Sala 103',
    responsible: { name: 'Pedro Lima', email: 'pedro@levitiis.com' },
    date: new Date('2024-01-11T11:20:00'),
    status: 'Cancelada',
    notes: 'Cancelada por mudança de planos'
  }
])

// New movement form
const newMovement = ref({
  assetId: '',
  type: '',
  origin: '',
  destination: '',
  responsibleName: '',
  date: '',
  notes: ''
})

// Computed properties
const filteredMovements = computed(() => {
  let filtered = movements.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(movement => 
      movement.asset.name.toLowerCase().includes(query) ||
      movement.asset.code.toLowerCase().includes(query) ||
      movement.responsible.name.toLowerCase().includes(query) ||
      movement.notes.toLowerCase().includes(query)
    )
  }

  if (selectedType.value) {
    filtered = filtered.filter(movement => movement.type === selectedType.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(movement => movement.status === selectedStatus.value)
  }

  if (selectedPeriod.value) {
    const now = new Date()
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const startOfWeek = new Date(startOfDay.getTime() - (startOfDay.getDay() * 24 * 60 * 60 * 1000))
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const startOfQuarter = new Date(now.getFullYear(), Math.floor(now.getMonth() / 3) * 3, 1)

    filtered = filtered.filter(movement => {
      const movementDate = new Date(movement.date)
      switch (selectedPeriod.value) {
        case 'today':
          return movementDate >= startOfDay
        case 'week':
          return movementDate >= startOfWeek
        case 'month':
          return movementDate >= startOfMonth
        case 'quarter':
          return movementDate >= startOfQuarter
        default:
          return true
      }
    })
  }

  return filtered
})

const paginatedMovements = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredMovements.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredMovements.value.length / itemsPerPage.value)
})

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const pendingMovements = computed(() => {
  return movements.value.filter(m => m.status === 'Pendente').length
})

const completedMovements = computed(() => {
  return movements.value.filter(m => m.status === 'Concluída').length
})

const overdueMovements = computed(() => {
  const now = new Date()
  return movements.value.filter(m => 
    m.status === 'Pendente' && new Date(m.date) < now
  ).length
})

const availableAssets = computed(() => {
  return assetsStore.assets.filter(asset => asset.status === 'Ativo')
})

// Methods
const applyFilters = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  selectedStatus.value = ''
  selectedPeriod.value = ''
  currentPage.value = 1
}

const formatDate = (date) => {
  return format(new Date(date), 'dd/MM/yyyy', { locale: ptBR })
}

const formatTime = (date) => {
  return format(new Date(date), 'HH:mm', { locale: ptBR })
}

const getStatusClass = (status) => {
  const statusClasses = {
    'Pendente': 'badge-warning',
    'Em Andamento': 'badge-info',
    'Concluída': 'badge-success',
    'Cancelada': 'badge-danger'
  }
  return statusClasses[status] || 'badge-secondary'
}

const viewMovement = (movement) => {
  logger.debug('View movement:', movement)
}

const approveMovement = (movement) => {
  if (confirm(`Aprovar a movimentação #${movement.id}?`)) {
    movement.status = 'Em Andamento'
  }
}

const cancelMovement = (movement) => {
  if (confirm(`Cancelar a movimentação #${movement.id}?`)) {
    movement.status = 'Cancelada'
  }
}

const addMovement = () => {
  const selectedAsset = assetsStore.assets.find(a => a.id == newMovement.value.assetId)
  
  const movement = {
    id: movements.value.length + 1,
    asset: {
      id: selectedAsset.id,
      name: selectedAsset.name,
      code: selectedAsset.code
    },
    type: newMovement.value.type,
    origin: newMovement.value.origin,
    destination: newMovement.value.destination,
    responsible: {
      name: newMovement.value.responsibleName,
      email: `${newMovement.value.responsibleName.toLowerCase().replace(' ', '.')}@levitiis.com`
    },
    date: new Date(newMovement.value.date),
    status: 'Pendente',
    notes: newMovement.value.notes
  }
  
  movements.value.unshift(movement)
  
  // Reset form
  newMovement.value = {
    assetId: '',
    type: '',
    origin: '',
    destination: '',
    responsibleName: '',
    date: '',
    notes: ''
  }
  
  showAddModal.value = false
}

const openEditModal = (movement) => {
  editMovement.value = {
    id: movement.id,
    assetId: movement.asset.id,
    type: movement.type,
    origin: movement.origin,
    destination: movement.destination,
    responsibleName: movement.responsible.name,
    date: format(new Date(movement.date), "yyyy-MM-dd'T'HH:mm"),
    status: movement.status,
    notes: movement.notes || ''
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const updateMovement = () => {
  const idx = movements.value.findIndex(m => m.id === editMovement.value.id)
  if (idx !== -1) {
    const selectedAsset = assetsStore.assets.find(a => a.id == editMovement.value.assetId)
    movements.value[idx] = {
      id: editMovement.value.id,
      asset: {
        id: selectedAsset.id,
        name: selectedAsset.name,
        code: selectedAsset.code
      },
      type: editMovement.value.type,
      origin: editMovement.value.origin,
      destination: editMovement.value.destination,
      responsible: {
        name: editMovement.value.responsibleName,
        email: `${editMovement.value.responsibleName.toLowerCase().replace(' ', '.')}@levitiis.com`
      },
      date: new Date(editMovement.value.date),
      status: editMovement.value.status,
      notes: editMovement.value.notes
    }
  }
  showEditModal.value = false
}

const exportMovements = () => {
  logger.debug('Export movements')
}

const refreshData = () => {
  logger.debug('Refresh data')
}

onMounted(() => {
  assetsStore.fetchAssets()
})
</script>

<style scoped>
.movements {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.primary { background-color: var(--primary-color); }
.stat-icon.success { background-color: var(--success-color); }
.stat-icon.warning { background-color: var(--warning-color); }
.stat-icon.info { background-color: var(--info-color); }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: var(--spacing-xs);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs);
}

.stat-change {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-change.positive { color: var(--success-color); }
.stat-change.negative { color: var(--danger-color); }
.stat-change.neutral { color: var(--text-muted); }

.filters-section {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.filters-row {
  display: flex;
  gap: var(--spacing-lg);
  align-items: end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  min-width: 200px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.search-input {
  position: relative;
}

.search-input i {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input input {
  padding-left: 2.5rem;
}

.table-container {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.results-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.table-wrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.table th {
  background-color: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.movement-id {
  font-family: monospace;
  font-weight: 600;
  color: var(--primary-color);
}

.asset-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.asset-name {
  font-weight: 600;
  color: var(--text-primary);
}

.asset-code {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-family: monospace;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
}

.user-email {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.date {
  font-weight: 500;
  color: var(--text-primary);
}

.time {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-xs);
}

.action-buttons .btn-icon.danger {
  color: var(--danger-color);
}

.action-buttons .btn-icon.danger:hover {
  background-color: var(--danger-color);
  color: white;
}

.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.pagination {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.page-numbers {
  display: flex;
  gap: var(--spacing-xs);
}

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
}

.modal {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-lg);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.modal-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-end;
  margin-top: var(--spacing-xl);
}

@media (max-width: 768px) {
  .page-header {
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
  
  .table-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: flex-start;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>