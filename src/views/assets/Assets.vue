<template>
  <div class="assets">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Gestão de Ativos</h1>
        <p class="page-subtitle">Controle e monitoramento de todos os ativos da empresa</p>
      </div>
      
      <div class="page-actions">
        <button class="btn btn-secondary" @click="exportAssets">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button class="btn btn-primary" @click="showAddModal = true">
          <i class="fas fa-plus"></i>
          Novo Ativo
        </button>
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
              placeholder="Buscar por código, nome ou descrição..."
              v-model="searchQuery"
              @input="applyFilters"
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label>Categoria</label>
          <select v-model="selectedCategory" @change="applyFilters">
            <option value="">Todas as categorias</option>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="selectedStatus" @change="applyFilters">
            <option value="">Todos os status</option>
            <option value="Ativo">Ativo</option>
            <option value="Manutenção">Manutenção</option>
            <option value="Inativo">Inativo</option>
            <option value="Emprestado">Emprestado</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Localização</label>
          <select v-model="selectedLocation" @change="applyFilters">
            <option value="">Todas as localizações</option>
            <option v-for="l in locations" :key="l" :value="l">{{ l }}</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Departamento</label>
          <select v-model="selectedDepartment" @change="applyFilters">
            <option value="">Todos os departamentos</option>
            <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        
        <button class="btn btn-outline" @click="clearFilters">
          <i class="fas fa-times"></i>
          Limpar
        </button>
      </div>
    </div>
    
    <!-- Assets Table -->
    <div class="table-container">
      <!-- Initial skeleton while first load and no assets loaded -->
      <SkeletonLoader 
        v-if="isLoading && assetsStore.assets.length === 0" 
        :rows="6" 
        :columns="viewMode === 'grid' ? 2 : 1" 
        :rowHeight="120"
        rowWidth="100%"
      />

      <!-- Loading State (overlay) -->
      <LoadingState 
        v-if="isLoading" 
        message="Carregando ativos..." 
        :overlay="true"
      />
      
      <div class="table-header">
        <div class="table-info">
          <span class="results-count">
            {{ filteredAssets.length }} de {{ assetsStore.totalAssets }} ativos
          </span>
        </div>
        
        <div class="table-actions">
          <div class="view-toggle">
            <button 
              class="btn-icon" 
              :class="{ active: viewMode === 'table' }"
              @click="viewMode = 'table'"
            >
              <i class="fas fa-list"></i>
            </button>
            <button 
              class="btn-icon" 
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Table View with Virtual Scrolling -->
      <div v-if="viewMode === 'table'" class="table-wrapper">
        <div class="table-header-fixed">
          <table class="table">
            <thead>
              <tr>
                <th>
                  <input 
                    type="checkbox" 
                    v-model="selectAll" 
                    @change="toggleSelectAll"
                  >
                </th>
                <th>Código</th>
                <th>Ativo</th>
                <th>Categoria</th>
                <th>Localização</th>
                <th>Responsável</th>
                <th>Data Entrada</th>
                <th>Garantia</th>
                <th>Valor</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
          </table>
        </div>
        
        <VirtualList
          :items="filteredAssets"
          :item-height="80"
          :container-height="600"
          :buffer="5"
          :show-search="false"
          :show-back-to-top="true"
          :show-performance-metrics="false"
          item-key="id"
          @item-click="viewAsset"
          @load-more="loadMoreAssets"
          class="assets-virtual-list"
        >
          <template #item="{ item: asset, index }">
            <div class="virtual-table-row" :class="{ 'selected': selectedAssets.includes(asset.id) }">
              <div class="virtual-table-cell checkbox-cell">
                <input 
                  type="checkbox" 
                  :value="asset.id" 
                  v-model="selectedAssets"
                >
              </div>
              <div class="virtual-table-cell code-cell">
                <span class="asset-code">{{ asset.tag }}</span>
              </div>
              <div class="virtual-table-cell asset-cell">
                <div class="asset-info">
                  <span class="asset-name">{{ asset.name }}</span>
                  <span class="asset-description">{{ asset.brand }} {{ asset.model }}</span>
                  <span class="asset-serial" v-if="asset.serialNumber">S/N: {{ asset.serialNumber }}</span>
                  <span class="asset-mac" v-if="asset.category === 'Informática' && asset.mac">MAC: {{ asset.mac }}</span>
                  <span class="asset-entry" v-if="asset.entryDate">Entrada: {{ formatDate(asset.entryDate) }}</span>
                </div>
              </div>
              <div class="virtual-table-cell category-cell">
                <span class="badge badge-outline">{{ asset.category }}</span>
                <small class="subcategory">{{ asset.subcategory }}</small>
              </div>
              <div class="virtual-table-cell location-cell">
                <div class="location-info">
                  <span>{{ asset.location }}</span>
                  <small>{{ asset.department }}</small>
                </div>
              </div>
              <div class="virtual-table-cell responsible-cell">{{ asset.responsible }}</div>
              <div class="virtual-table-cell date-cell">
                <span class="date-info">{{ formatDate(asset.entryDate) }}</span>
              </div>
              <div class="virtual-table-cell warranty-cell">
                <div class="warranty-info">
                  <span class="warranty-status" :class="getWarrantyStatusClass(asset.warranty)">
                    {{ asset.warranty?.status || 'N/A' }}
                  </span>
                  <small v-if="asset.warranty?.endDate">
                    {{ formatDate(asset.warranty.endDate) }}
                  </small>
                </div>
              </div>
              <div class="virtual-table-cell value-cell">
                <div class="value-info">
                  <span class="current-value">{{ formatCurrency(asset.depreciation?.currentValue || asset.value) }}</span>
                  <small v-if="asset.depreciation?.currentValue !== asset.value" class="original-value">
                    Original: {{ formatCurrency(asset.value) }}
                  </small>
                </div>
              </div>
              <div class="virtual-table-cell status-cell">
                <span class="badge" :class="getStatusClass(asset.status)">
                  {{ asset.status }}
                </span>
              </div>
              <div class="virtual-table-cell actions-cell">
                <div class="action-buttons">
                  <button class="btn-icon" @click.stop="viewAsset(asset)" title="Ver Detalhes">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn-icon" @click.stop="editAsset(asset)" title="Editar">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-icon" @click.stop="moveAsset(asset)" title="Movimentar">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
                  <button class="btn-icon danger" @click.stop="deleteAsset(asset)" title="Excluir">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </template>
          
          <template #loading>
            <div class="virtual-loading">
              <i class="fas fa-spinner fa-spin"></i>
              Carregando mais ativos...
            </div>
          </template>
          
          <template #empty>
            <div class="virtual-empty">
              <i class="fas fa-inbox"></i>
              <p>Nenhum ativo encontrado</p>
              <p class="text-muted">Tente ajustar os filtros ou adicionar novos ativos</p>
            </div>
          </template>
        </VirtualList>
      </div>
      
      <!-- Grid View -->
      <div v-else class="grid-view">
        <div v-for="asset in paginatedAssets" :key="asset.id" class="asset-card">
          <div class="asset-card-header">
            <input type="checkbox" v-model="selectedAssets" :value="asset.id">
            <span class="badge" :class="getStatusClass(asset.status)">
              {{ asset.status }}
            </span>
          </div>
          
          <div class="asset-card-body">
            <div class="asset-icon">
              <i :class="getCategoryIcon(asset.category)"></i>
            </div>
            
            <div class="asset-details">
              <h3 class="asset-name">{{ asset.name }}</h3>
              <p class="asset-code">{{ asset.tag }}</p>
              <p class="asset-brand">{{ asset.brand }} {{ asset.model }}</p>
              <p class="asset-serial">S/N: {{ asset.serialNumber }}</p>
              
              <div class="asset-meta">
                <div class="meta-item">
                  <i class="fas fa-tag"></i>
                  <span>{{ asset.category }} - {{ asset.subcategory }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-map-marker-alt"></i>
                  <span>{{ asset.location }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-building"></i>
                  <span>{{ asset.department }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-user"></i>
                  <span>{{ asset.responsible }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-calendar-plus"></i>
                  <span>Entrada: {{ formatDate(asset.entryDate) }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-shield-alt"></i>
                  <span class="warranty-status" :class="getWarrantyStatusClass(asset.warranty)">
                    Garantia: {{ asset.warranty?.status || 'N/A' }}
                    <span v-if="asset.warranty?.endDate"> - {{ formatDate(asset.warranty.endDate) }}</span>
                  </span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-dollar-sign"></i>
                  <span>
                    {{ formatCurrency(asset.depreciation?.currentValue || asset.value) }}
                    <small v-if="asset.depreciation?.currentValue !== asset.value" class="original-value">
                      (Original: {{ formatCurrency(asset.value) }})
                    </small>
                  </span>
                </div>
                <div v-if="asset.maintenance?.nextDate" class="meta-item">
                  <i class="fas fa-wrench"></i>
                  <span>Próxima Manutenção: {{ formatDate(asset.maintenance.nextDate) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="asset-card-footer">
            <button class="btn btn-sm btn-outline" @click="viewAsset(asset)">
              <i class="fas fa-eye"></i>
              Ver Detalhes
            </button>
            <div class="card-actions">
              <button class="btn-icon" @click="editAsset(asset)" title="Editar">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon" @click="moveAsset(asset)" title="Movimentar">
                <i class="fas fa-exchange-alt"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Virtual Scrolling Info -->
      <div class="virtual-info" v-if="viewMode === 'table'">
        <div class="results-summary">
          <span>
            Total de {{ filteredAssets.length }} ativos
            <span v-if="selectedAssets.length > 0">
              ({{ selectedAssets.length }} selecionados)
            </span>
          </span>
        </div>
      </div>
    </div>
    
    <!-- Add Asset Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Novo Ativo</h2>
          <button class="btn-icon" @click="showAddModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="addAsset">
            <div class="form-row">
              <div class="form-group">
                <label>Código *</label>
                <input type="text" v-model="newAsset.tag" required>
                <small class="form-error" v-if="validationErrors.tag">{{ validationErrors.tag }}</small>
              </div>
              <div class="form-group">
                <label>Nome *</label>
                <input type="text" v-model="newAsset.name" required>
                <small class="form-error" v-if="validationErrors.name">{{ validationErrors.name }}</small>
              </div>
            </div>
            
            <div class="form-group">
              <label>Descrição</label>
              <textarea v-model="newAsset.description" rows="3"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Categoria *</label>
                  <select v-model="newAsset.category" required>
                  <option value="">Selecione uma categoria</option>
                  <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
                </select>
                  <small class="form-error" v-if="validationErrors.category">{{ validationErrors.category }}</small>
              </div>
              <div class="form-group">
                <label>Localização *</label>
                  <input type="text" v-model="newAsset.location" required>
                  <small class="form-error" v-if="validationErrors.location">{{ validationErrors.location }}</small>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Valor *</label>
                  <input type="number" step="0.01" v-model.number="newAsset.value" required>
                  <small class="form-error" v-if="validationErrors.value">{{ validationErrors.value }}</small>
              </div>
              <div class="form-group">
                <label>Status</label>
                <select v-model="newAsset.status">
                  <option value="Ativo">Ativo</option>
                  <option value="Manutenção">Manutenção</option>
                  <option value="Inativo">Inativo</option>
                  <option value="Emprestado">Emprestado</option>
                </select>
              </div>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showAddModal = false">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i>
                Salvar Ativo
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Asset Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Editar Ativo</h2>
          <button class="btn-icon" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveEdit">
            <div class="form-row">
              <div class="form-group">
                <label>Código *</label>
                <input type="text" v-model="editForm.tag" required>
                <small class="form-error" v-if="validationErrors.tag">{{ validationErrors.tag }}</small>
              </div>
              <div class="form-group">
                <label>Nome *</label>
                <input type="text" v-model="editForm.name" required>
                <small class="form-error" v-if="validationErrors.name">{{ validationErrors.name }}</small>
              </div>
            </div>
            
            <div class="form-group">
              <label>Descrição</label>
              <textarea v-model="editForm.description" rows="3"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Categoria *</label>
                  <select v-model="editForm.category" required>
                  <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
                </select>
                  <small class="form-error" v-if="validationErrors.category">{{ validationErrors.category }}</small>
              </div>
              <div class="form-group">
                <label>Localização *</label>
                  <input type="text" v-model="editForm.location" required>
                  <small class="form-error" v-if="validationErrors.location">{{ validationErrors.location }}</small>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Valor *</label>
                <input type="number" step="0.01" v-model.number="editForm.value" required>
                <small class="form-error" v-if="validationErrors.value">{{ validationErrors.value }}</small>
              </div>
              <div class="form-group">
                <label>Status</label>
                <select v-model="editForm.status">
                  <option value="Ativo">Ativo</option>
                  <option value="Manutenção">Manutenção</option>
                  <option value="Inativo">Inativo</option>
                  <option value="Emprestado">Emprestado</option>
                </select>
              </div>
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
import { ref, computed, onMounted } from 'vue'
import useValidation from '@/composables/useValidation'
import { useAssetsStore } from '@/stores/assets'
import { usePageLoading } from '@/composables/useLoading'
import { useToast } from '@/composables/useToast'
import LoadingState from '@/components/common/LoadingState.vue'
import SkeletonLoader from '@/components/common/SkeletonLoader.vue'
import VirtualList from '@/components/common/VirtualList.vue'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const assetsStore = useAssetsStore()
const { isLoading, loadPage } = usePageLoading()
const { success, error: toastError } = useToast()

// Reactive data
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const selectedLocation = ref('')
const selectedDepartment = ref('')
const viewMode = ref('table')
const selectedAssets = ref([])
const selectAll = ref(false)
const showAddModal = ref(false)

// Edit modal state
const showEditModal = ref(false)
const editForm = ref({
  id: null,
  tag: '',
  name: '',
  description: '',
  category: '',
  location: '',
  value: 0,
  status: 'Ativo'
})

// Dynamic categories from existing assets
const categories = computed(() => {
  const unique = [...new Set(assetsStore.assets.map(a => a.category).filter(Boolean))]
  return unique.sort()
})

const locations = computed(() => {
  const unique = [...new Set(assetsStore.assets.map(a => a.location).filter(Boolean))]
  return unique.sort()
})

const departments = computed(() => {
  const unique = [...new Set(assetsStore.assets.map(a => a.department).filter(Boolean))]
  return unique.sort()
})

// New asset form
const newAsset = ref({
  tag: '',
  name: '',
  description: '',
  category: '',
  location: '',
  value: 0,
  status: 'Ativo'
})

// Validation
const { validationErrors, validateAsset, clearErrors } = useValidation()

// Computed properties
const filteredAssets = computed(() => {
  return assetsStore.filteredAssets
})

// Methods
const applyFilters = () => {
  assetsStore.setFilters({
    search: searchQuery.value,
    category: selectedCategory.value,
    status: selectedStatus.value,
    location: selectedLocation.value,
    department: selectedDepartment.value
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedStatus.value = ''
  selectedLocation.value = ''
  selectedDepartment.value = ''
  assetsStore.clearFilters()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedAssets.value = filteredAssets.value.map(asset => asset.id)
  } else {
    selectedAssets.value = []
  }
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

const formatDate = (date) => {
  return format(new Date(date), 'dd/MM/yyyy', { locale: ptBR })
}

const getStatusClass = (status) => {
  const statusClasses = {
    'Ativo': 'badge-success',
    'Manutenção': 'badge-warning',
    'Inativo': 'badge-danger',
    'Emprestado': 'badge-info'
  }
  return statusClasses[status] || 'badge-secondary'
}

const getCategoryIcon = (category) => {
  const categoryIcons = {
    'Informática': 'fas fa-laptop',
    'Móveis': 'fas fa-chair',
    'Equipamentos': 'fas fa-tools',
    'Veículos': 'fas fa-car',
    'Telefonia': 'fas fa-mobile-alt',
    'Mobiliário': 'fas fa-couch'
  }
  return categoryIcons[category] || 'fas fa-box'
}

const getWarrantyStatusClass = (warranty) => {
  if (!warranty || !warranty.endDate) return 'warranty-none'
  
  const today = new Date()
  const endDate = new Date(warranty.endDate)
  const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000))
  
  if (endDate < today) {
    return 'warranty-expired'
  } else if (endDate <= thirtyDaysFromNow) {
    return 'warranty-expiring'
  } else {
    return 'warranty-active'
  }
}

const isWarrantyExpiring = (warranty) => {
  if (!warranty || !warranty.endDate) return false
  
  const today = new Date()
  const endDate = new Date(warranty.endDate)
  const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000))
  
  return endDate <= thirtyDaysFromNow && endDate >= today
}

const isMaintenanceDue = (maintenance) => {
  if (!maintenance || !maintenance.nextDate) return false
  
  const today = new Date()
  const nextDate = new Date(maintenance.nextDate)
  const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000))
  
  return nextDate <= thirtyDaysFromNow && nextDate >= today
}

import logger from '@/utils/logger'

const viewAsset = (asset) => {
  // Navigate to asset details
  logger.userAction('view_asset', { id: asset.id, name: asset.name })
}

const editAsset = (asset) => {
  editForm.value = {
    id: asset.id,
    tag: asset.tag || '',
    name: asset.name || '',
    description: asset.description || '',
    category: asset.category || '',
    location: asset.location || '',
    value: typeof asset.value === 'number' ? asset.value : Number(asset.value || 0),
    status: asset.status || 'Ativo'
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const saveEdit = async () => {
  try {
    // Validate edit form
    if (!validateAsset(editForm.value)) {
      toastError('Por favor corrija os erros no formulário antes de salvar.')
      return
    }

    await assetsStore.updateAsset(editForm.value.id, {
      tag: editForm.value.tag,
      name: editForm.value.name,
      description: editForm.value.description,
      category: editForm.value.category,
      location: editForm.value.location,
      value: editForm.value.value,
      status: editForm.value.status,
      updatedAt: new Date()
    })
    showEditModal.value = false
    clearErrors()
    success('Ativo atualizado com sucesso')
  } catch (error) {
    logger.error('Error updating asset:', error)
    toastError('Erro ao atualizar ativo')
  }
}

const moveAsset = (asset) => {
  // Open movement modal
  logger.userAction('move_asset', { id: asset.id, name: asset.name })
}

const deleteAsset = (asset) => {
  if (confirm(`Tem certeza que deseja excluir o ativo ${asset.name}?`)) {
    assetsStore.deleteAsset(asset.id)
    success('Ativo excluído com sucesso')
  }
}

const addAsset = async () => {
  try {
    // Validate new asset
    if (!validateAsset(newAsset.value)) {
      toastError('Por favor corrija os erros no formulário antes de salvar.')
      return
    }

    await assetsStore.addAsset({
      ...newAsset.value,
      id: Date.now(), // Temporary ID generation
      createdAt: new Date(),
      updatedAt: new Date()
    })
    
    // Reset form
    newAsset.value = {
      tag: '',
      name: '',
      description: '',
      category: '',
      location: '',
      value: 0,
      status: 'Ativo'
    }
    
    showAddModal.value = false
    clearErrors()
    success('Ativo criado com sucesso')
  } catch (error) {
    logger.error('Error adding asset:', error)
    toastError('Erro ao adicionar ativo')
  }
}

const exportAssets = () => {
  // Export functionality
  logger.userAction('export_assets', { count: filteredAssets.value.length })
}

const loadMoreAssets = async () => {
  // Load more assets for virtual scrolling
  await assetsStore.loadMoreAssets()
}

onMounted(async () => {
  await loadPage(async () => {
    await assetsStore.fetchAssets()
  })
})
</script>

<style scoped>
.assets {
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

.table-actions {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.view-toggle {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.view-toggle .btn-icon {
  border: none;
  border-radius: 0;
  background-color: var(--bg-secondary);
}

.view-toggle .btn-icon.active {
  background-color: var(--primary-color);
  color: white;
}

.table-wrapper {
  overflow-x: auto;
  position: relative;
}

.table-header-fixed {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.assets-virtual-list {
  height: 600px;
  overflow-y: auto;
}

.virtual-table-row {
  display: grid;
  grid-template-columns: 50px 120px minmax(280px, 1fr) 150px 150px 150px 120px 120px 120px 100px 150px;
  align-items: center;
  padding: var(--spacing-md);
  gap: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
  user-select: text;
  cursor: default;
}

.virtual-table-row:hover {
  background-color: var(--bg-secondary);
  outline: 1px solid var(--border-color);
  outline-offset: -1px;
}

/* Zebra rows */
.assets-virtual-list .virtual-table-row:nth-child(odd) {
  background-color: var(--bg-primary);
}

.assets-virtual-list .virtual-table-row:nth-child(even) {
  background-color: var(--bg-primary);
}

.virtual-table-row.selected {
  background-color: var(--primary-color-light);
  outline: 2px solid var(--primary-color);
}

.virtual-table-cell {
  padding: var(--spacing-xs);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.virtual-table-cell.code-cell,
.virtual-table-cell.value-cell,
.virtual-table-cell.date-cell {
  text-align: right;
}

.virtual-table-cell.asset-cell {
  white-space: normal;
}

.virtual-table-cell.asset-cell {
  white-space: normal;
}

.virtual-table-cell.actions-cell {
  white-space: nowrap;
}

.virtual-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  color: var(--text-muted);
}

.virtual-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xxl);
  text-align: center;
  color: var(--text-muted);
}

.virtual-empty i {
  font-size: 3rem;
  margin-bottom: var(--spacing-lg);
  color: var(--text-muted);
}

.virtual-empty p {
  margin: var(--spacing-xs) 0;
}

.virtual-empty .text-muted {
  font-size: 0.875rem;
}

/* Responsive Virtual Scrolling */
@media (max-width: 1200px) {
  .virtual-table-row {
    grid-template-columns: 40px 100px minmax(240px, 1fr) 120px 120px 120px 100px 100px 100px 80px 120px;
  }
}

@media (max-width: 992px) {
  .virtual-table-row {
    grid-template-columns: 40px 80px minmax(200px, 1fr) 100px 100px 80px 80px 80px 60px 100px;
  }
}

@media (max-width: 768px) {
  .assets-virtual-list {
    height: 400px;
  }
  
  .virtual-table-row {
    grid-template-columns: 40px 1fr 80px 100px;
    gap: var(--spacing-xs);
  }
  
  .virtual-table-cell.code-cell,
  .virtual-table-cell.category-cell,
  .virtual-table-cell.location-cell,
  .virtual-table-cell.date-cell,
  .virtual-table-cell.value-cell {
    display: none;
  }
  
  .virtual-table-cell.asset-cell {
    white-space: normal;
    line-height: 1.4;
  }
  
  .asset-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .asset-description {
    font-size: 0.75rem;
    color: var(--text-muted);
  }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .virtual-table-row {
    border-bottom: 2px solid var(--border-color);
  }
  
  .virtual-table-row:hover {
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    outline: 2px solid var(--border-color);
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .virtual-table-row {
    transition: none;
  }
  
  .virtual-loading i {
    animation: none;
  }
}

.table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.table thead th {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Fix column widths to align header with virtual rows */
.table thead th:nth-child(1) { width: 50px; }
.table thead th:nth-child(2) { width: 120px; }
.table thead th:nth-child(3) { min-width: 280px; }
.table thead th:nth-child(4) { width: 150px; }
.table thead th:nth-child(5) { width: 150px; }
.table thead th:nth-child(6) { width: 150px; }
.table thead th:nth-child(7) { width: 120px; }
.table thead th:nth-child(8) { width: 120px; }
.table thead th:nth-child(9) { width: 120px; }
.table thead th:nth-child(10) { width: 100px; }
.table thead th:nth-child(11) { width: 150px; }

.table th,
.table td {
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.table tbody tr:nth-child(odd) {
  background-color: rgba(0, 0, 0, 0.02);
}

.table tbody tr:hover {
  background-color: var(--bg-secondary);
  outline: 1px solid var(--border-color);
  outline-offset: -1px;
}

.table tbody tr {
  user-select: text;
}

.table th {
  background-color: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.asset-code {
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

.asset-description {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.asset-serial {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.asset-mac {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.asset-entry {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.asset-brand {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.subcategory {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.location-info {
  display: flex;
  flex-direction: column;
}

.location-info small {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.date-info {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.warranty-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.warranty-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.warranty-active {
  background-color: #d4edda;
  color: #155724;
}

.warranty-expiring {
  background-color: #fff3cd;
  color: #856404;
}

.warranty-expired {
  background-color: #f8d7da;
  color: #721c24;
}

.warranty-none {
  background-color: #e2e3e5;
  color: #6c757d;
}

.value-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.current-value {
  font-weight: 600;
  color: var(--text-primary);
}

.original-value {
  font-size: 0.75rem;
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

.grid-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
}

.asset-card {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background-color: var(--bg-secondary);
}

.asset-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.asset-card-body {
  padding: var(--spacing-lg);
}

.asset-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-lg);
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin-bottom: var(--spacing-md);
}

.asset-details h3 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-primary);
}

.asset-details .asset-code {
  font-size: 0.875rem;
  margin-bottom: var(--spacing-sm);
}

.asset-details .asset-description {
  margin-bottom: var(--spacing-md);
}

.asset-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.meta-item i {
  width: 16px;
  color: var(--text-muted);
}

.asset-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  background-color: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

.card-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.virtual-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  margin-top: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.results-summary {
  font-size: 0.875rem;
  color: var(--text-muted);
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
  
  .grid-view {
    grid-template-columns: 1fr;
  }
}
</style>