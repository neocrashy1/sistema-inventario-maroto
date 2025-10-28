<template>
  <div class="physical-inventory">
    <!-- Cabeçalho -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Inventário Físico</h1>
          <p class="page-subtitle">Gerencie contagens e verificações físicas de ativos</p>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-outline"
            @click="exportInventories"
            :disabled="loading"
          >
            <i class="fas fa-download"></i>
            Exportar
          </button>
          <button 
            class="btn btn-primary"
            @click="showNewInventoryModal = true"
          >
            <i class="fas fa-plus"></i>
            Novo Inventário
          </button>
        </div>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-clipboard-list"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalInventories }}</div>
          <div class="stat-label">Total de Inventários</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-play-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ inventoriesInProgress }}</div>
          <div class="stat-label">Em Andamento</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon counted">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalAssetsCount }}</div>
          <div class="stat-label">Ativos Contados</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon discrepancy">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalDiscrepancies }}</div>
          <div class="stat-label">Discrepâncias</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon assets">
          <i class="fas fa-boxes"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalAssets }}</div>
          <div class="stat-label">Ativos Disponíveis</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warranty-active">
          <i class="fas fa-shield-alt"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ assetsByWarrantyStatus['Ativa'] || 0 }}</div>
          <div class="stat-label">Garantias Ativas</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warranty-expiring">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ assetsByWarrantyStatus['Próxima ao Vencimento'] || 0 }}</div>
          <div class="stat-label">Garantias Expirando</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon value">
          <i class="fas fa-dollar-sign"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ formatCurrency(totalAssetsValue) }}</div>
          <div class="stat-label">Valor Total</div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-section">
      <div class="filters-grid">
        <div class="filter-group">
          <label>Buscar</label>
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="Código, descrição, responsável..."
            class="form-input"
          >
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="statusFilter" class="form-select">
            <option value="">Todos os Status</option>
            <option value="Planejado">Planejado</option>
            <option value="Em Andamento">Em Andamento</option>
            <option value="Concluído">Concluído</option>
            <option value="Cancelado">Cancelado</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Localização</label>
          <select v-model="locationFilter" class="form-select">
            <option value="">Todas as Localizações</option>
            <option 
              v-for="location in locations" 
              :key="location.id"
              :value="location.id"
            >
              {{ location.name }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Período</label>
          <div class="date-range">
            <input 
              type="date" 
              v-model="dateRangeStart"
              class="form-input"
            >
            <span>até</span>
            <input 
              type="date" 
              v-model="dateRangeEnd"
              class="form-input"
            >
          </div>
        </div>
        
        <div class="filter-actions">
          <button 
            class="btn btn-outline btn-sm"
            @click="clearFilters"
          >
            Limpar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Contador de Resultados -->
    <div class="results-info">
      <span>{{ filteredInventories.length }} inventário(s) encontrado(s)</span>
    </div>

    <!-- Tabela de Inventários -->
    <div class="table-container">
      <table class="data-table">
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
            <th>Descrição</th>
            <th>Localização</th>
            <th>Responsável</th>
            <th>Data Início</th>
            <th>Data Fim</th>
            <th>Status</th>
            <th>Progresso</th>
            <th>Discrepâncias</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inventory in paginatedInventories" :key="inventory.id">
            <td>
              <input 
                type="checkbox" 
                v-model="selectedInventories"
                :value="inventory.id"
              >
            </td>
            <td>
              <span class="code">{{ inventory.code }}</span>
            </td>
            <td>
              <div class="inventory-info">
                <div class="description">{{ inventory.description }}</div>
                <div class="type">{{ inventory.type }}</div>
              </div>
            </td>
            <td>
              <div class="location-info">
                <div class="name">{{ inventory.location.name }}</div>
                <div class="code">{{ inventory.location.code }}</div>
              </div>
            </td>
            <td>
              <div class="responsible-info">
                <div class="name">{{ inventory.responsible.name }}</div>
                <div class="email">{{ inventory.responsible.email }}</div>
              </div>
            </td>
            <td>{{ formatDate(inventory.startDate) }}</td>
            <td>{{ formatDate(inventory.endDate) }}</td>
            <td>
              <span 
                class="status-badge"
                :class="getStatusClass(inventory.status)"
              >
                {{ inventory.status }}
              </span>
            </td>
            <td>
              <div class="progress-container">
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :style="{ width: inventory.progress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ inventory.progress }}%</span>
              </div>
            </td>
            <td>
              <span 
                class="discrepancy-badge"
                :class="inventory.discrepancies > 0 ? 'has-discrepancy' : 'no-discrepancy'"
              >
                {{ inventory.discrepancies }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  class="btn btn-sm btn-primary"
                  @click="viewInventoryDetails(inventory)"
                  title="Ver Detalhes"
                >
                  <i class="fas fa-eye"></i>
                </button>
                <button 
                  v-if="inventory.status === 'Em Andamento'"
                  class="btn btn-sm btn-success"
                  @click="openCountingModal(inventory)"
                  title="Registrar Contagem"
                >
                  <i class="fas fa-calculator"></i>
                </button>
                <button 
                  v-if="inventory.status !== 'Concluído'"
                  class="btn btn-sm btn-outline"
                  @click="editInventory(inventory)"
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

    <!-- Paginação -->
    <div class="pagination-container">
      <div class="pagination-info">
        Mostrando {{ startIndex + 1 }} a {{ endIndex }} de {{ filteredInventories.length }} registros
      </div>
      <div class="pagination">
        <button 
          class="btn btn-sm btn-outline"
          @click="currentPage--"
          :disabled="currentPage === 1"
        >
          Anterior
        </button>
        <span class="page-info">{{ currentPage }} de {{ totalPages }}</span>
        <button 
          class="btn btn-sm btn-outline"
          @click="currentPage++"
          :disabled="currentPage === totalPages"
        >
          Próxima
        </button>
      </div>
    </div>

    <!-- Modal Novo Inventário -->
    <div v-if="showNewInventoryModal" class="modal-overlay" @click="closeNewInventoryModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Novo Inventário Físico</h3>
          <button class="modal-close" @click="closeNewInventoryModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="createInventory">
            <div class="form-grid">
              <div class="form-group">
                <label>Descrição *</label>
                <input 
                  type="text" 
                  v-model="newInventory.description"
                  class="form-input"
                  required
                  placeholder="Descrição do inventário"
                >
              </div>
              
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="newInventory.type" class="form-select" required>
                  <option value="">Selecione o tipo</option>
                  <option value="Geral">Inventário Geral</option>
                  <option value="Parcial">Inventário Parcial</option>
                  <option value="Cíclico">Inventário Cíclico</option>
                  <option value="Emergencial">Inventário Emergencial</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Localização *</label>
                <select v-model="newInventory.locationId" class="form-select" required>
                  <option value="">Selecione a localização</option>
                  <option 
                    v-for="location in locations" 
                    :key="location.id"
                    :value="location.id"
                  >
                    {{ location.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Responsável *</label>
                <select v-model="newInventory.responsibleId" class="form-select" required>
                  <option value="">Selecione o responsável</option>
                  <option 
                    v-for="user in responsibles" 
                    :key="user.id"
                    :value="user.id"
                  >
                    {{ user.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Data de Início *</label>
                <input 
                  type="date" 
                  v-model="newInventory.startDate"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group">
                <label>Data de Fim *</label>
                <input 
                  type="date" 
                  v-model="newInventory.endDate"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group full-width">
                <label>Observações</label>
                <textarea 
                  v-model="newInventory.notes"
                  class="form-textarea"
                  rows="3"
                  placeholder="Observações sobre o inventário..."
                ></textarea>
              </div>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="closeNewInventoryModal">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Criando...' : 'Criar Inventário' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal Registrar Contagem -->
    <div v-if="showCountingModal" class="modal-overlay" @click="closeCountingModal">
      <div class="modal large" @click.stop>
        <div class="modal-header">
          <h3>Registrar Contagem - {{ selectedInventory?.code }}</h3>
          <button class="modal-close" @click="closeCountingModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="counting-section">
            <div class="section-header">
              <h4>Ativos para Contagem</h4>
              <div class="counting-stats">
                <span class="stat">
                  <strong>{{ countingAssets.filter(a => a.counted).length }}</strong> / {{ countingAssets.length }} contados
                </span>
              </div>
            </div>
            
            <div class="assets-list">
              <div 
                v-for="asset in countingAssets" 
                :key="asset.id"
                class="asset-item"
                :class="{ 'counted': asset.counted, 'discrepancy': asset.hasDiscrepancy }"
              >
                <div class="asset-info">
                  <div class="asset-header">
                    <div class="asset-code">{{ asset.tag }}</div>
                    <div class="asset-name">{{ asset.name }}</div>
                  </div>
                  <div class="asset-details">
                    <div class="detail-row">
                      <span class="label">Marca/Modelo:</span>
                      <span class="value">{{ asset.brand }} {{ asset.model }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Série:</span>
                      <span class="value">{{ asset.serialNumber }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Localização:</span>
                      <span class="value">{{ asset.location }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Departamento:</span>
                      <span class="value">{{ asset.department }}</span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Garantia:</span>
                      <span class="warranty-status" :class="getWarrantyStatusClass(asset.warranty)">
                        {{ asset.warranty?.status || 'N/A' }}
                        <small v-if="asset.warranty?.endDate"> - {{ formatDate(asset.warranty.endDate) }}</small>
                      </span>
                    </div>
                    <div class="detail-row">
                      <span class="label">Valor:</span>
                      <span class="value">{{ formatCurrency(asset.value) }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="counting-controls">
                  <div class="form-group">
                    <label>Status</label>
                    <select 
                      v-model="asset.countStatus"
                      class="form-select"
                      @change="updateAssetCount(asset)"
                    >
                      <option value="not_counted">Não Contado</option>
                      <option value="found">Encontrado</option>
                      <option value="not_found">Não Encontrado</option>
                      <option value="damaged">Danificado</option>
                      <option value="wrong_location">Local Incorreto</option>
                    </select>
                  </div>
                  
                  <div v-if="asset.countStatus === 'wrong_location'" class="form-group">
                    <label>Local Atual</label>
                    <input 
                      type="text" 
                      v-model="asset.actualLocation"
                      class="form-input"
                      placeholder="Onde foi encontrado"
                    >
                  </div>
                  
                  <div class="form-group">
                    <label>Observações</label>
                    <input 
                      type="text" 
                      v-model="asset.countNotes"
                      class="form-input"
                      placeholder="Observações da contagem"
                    >
                  </div>
                </div>
                
                <div class="counting-status">
                  <i 
                    v-if="asset.counted"
                    class="fas fa-check-circle"
                    :class="asset.hasDiscrepancy ? 'text-warning' : 'text-success'"
                  ></i>
                  <i v-else class="fas fa-clock text-muted"></i>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeCountingModal">
              Fechar
            </button>
            <button 
              type="button" 
              class="btn btn-success"
              @click="saveCountingProgress"
              :disabled="loading"
            >
              {{ loading ? 'Salvando...' : 'Salvar Progresso' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mensagens -->
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
    
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { usePhysicalInventoryStore } from '@/stores/physicalInventory'
import { useAssetsStore } from '@/stores/assets'
import { formatDate } from '@/utils/dateUtils'
import { getWarrantyStatus, formatWarrantyStatus, getWarrantyStatusMessage } from '@/utils/warrantyUtils'
import logger from '@/utils/logger'

export default {
  name: 'PhysicalInventory',
  setup() {
    const store = usePhysicalInventoryStore()
    const assetsStore = useAssetsStore()
    const { 
      inventories, 
      locations,
      responsibles,
      loading, 
      error
    } = storeToRefs(store)

    // Estatísticas da store de inventário
    const { totalInventories, inventoriesInProgress, totalAssetsCount, totalDiscrepancies } = store

    // Estatísticas da store de ativos
    const { assetsByWarrantyStatus, totalValue: totalAssetsValue, totalAssets } = assetsStore

    // Estado local
    const searchQuery = ref('')
    const statusFilter = ref('')
    const locationFilter = ref('')
    const dateRangeStart = ref('')
    const dateRangeEnd = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const selectedInventories = ref([])
    const selectAll = ref(false)

    // Modais
    const showNewInventoryModal = ref(false)
    const showCountingModal = ref(false)
    const selectedInventory = ref(null)

    // Formulários
    const newInventory = ref({
      description: '',
      type: '',
      locationId: '',
      responsibleId: '',
      startDate: '',
      endDate: '',
      notes: ''
    })
    
    const countingAssets = ref([])
    
    // Mensagens
    const successMessage = ref('')
    const errorMessage = ref('')
    
    // Computed
    const filteredInventories = computed(() => {
      let filtered = inventories.value || []
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(inventory =>
          inventory.code.toLowerCase().includes(query) ||
          inventory.description.toLowerCase().includes(query) ||
          inventory.responsible?.name?.toLowerCase().includes(query) ||
          inventory.location?.name?.toLowerCase().includes(query)
        )
      }
      
      if (statusFilter.value) {
        // Mapear status exibido para status interno
        const statusMap = {
          'Planejado': 'planned',
          'Em Andamento': 'in_progress',
          'Concluído': 'completed',
          'Cancelado': 'cancelled'
        }
        filtered = filtered.filter(inventory => inventory.status === statusMap[statusFilter.value])
      }
      
      if (locationFilter.value) {
        filtered = filtered.filter(inventory => String(inventory.location?.id) === String(locationFilter.value))
      }
      
      if (dateRangeStart.value || dateRangeEnd.value) {
        filtered = filtered.filter(inventory => {
          const inventoryDate = new Date(inventory.startDate)
          const start = dateRangeStart.value ? new Date(dateRangeStart.value) : new Date('1900-01-01')
          const end = dateRangeEnd.value ? new Date(dateRangeEnd.value) : new Date('2100-12-31')
          return inventoryDate >= start && inventoryDate <= end
        })
      }
      
      return filtered
    })
    
    const totalPages = computed(() => {
      return Math.ceil((filteredInventories.value?.length || 0) / itemsPerPage.value)
    })
    
    const startIndex = computed(() => {
      return (currentPage.value - 1) * itemsPerPage.value
    })
    
    const endIndex = computed(() => {
      return Math.min(startIndex.value + itemsPerPage.value, filteredInventories.value?.length || 0)
    })
    
    const paginatedInventories = computed(() => {
      return (filteredInventories.value || []).slice(startIndex.value, endIndex.value)
    })
    
    // Métodos
    const formatDateLocal = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('pt-BR')
    }

    const formatCurrency = (value) => {
      if (!value) return 'R$ 0,00'
      return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      }).format(value)
    }

    const getWarrantyStatusClass = (warranty) => {
      if (!warranty || !warranty.endDate) return 'warranty-none'
      const status = getWarrantyStatus(warranty.endDate)
      return `warranty-${status}`
    }

    // Função para obter mensagem de status da garantia
    const getWarrantyMessage = (warranty) => {
      if (!warranty || !warranty.endDate) return 'Sem garantia'
      return getWarrantyStatusMessage(warranty.endDate)
    }

    // Função para formatar status da garantia para exibição
    const formatWarrantyStatusDisplay = (warranty) => {
      if (!warranty || !warranty.endDate) return 'Sem Garantia'
      const status = getWarrantyStatus(warranty.endDate)
      return formatWarrantyStatus(status)
    }
    
    const getStatusClass = (status) => {
      const classes = {
        'Planejado': 'status-planned',
        'Em Andamento': 'status-active',
        'Concluído': 'status-completed',
        'Cancelado': 'status-cancelled'
      }
      return classes[status] || ''
    }
    
    const clearFilters = () => {
      searchQuery.value = ''
      statusFilter.value = ''
      locationFilter.value = ''
      dateRangeStart.value = ''
      dateRangeEnd.value = ''
      currentPage.value = 1
    }
    
    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedInventories.value = paginatedInventories.value.map(inventory => inventory.id)
      } else {
        selectedInventories.value = []
      }
    }
    
    const closeNewInventoryModal = () => {
      showNewInventoryModal.value = false
      resetNewInventoryForm()
    }
    
    const resetNewInventoryForm = () => {
      newInventory.value = {
        description: '',
        type: '',
        locationId: '',
        responsibleId: '',
        startDate: '',
        endDate: '',
        notes: ''
      }
    }
    
    const createInventory = async () => {
      try {
        await store.createInventory(newInventory.value)
        successMessage.value = 'Inventário criado com sucesso!'
        closeNewInventoryModal()
        setTimeout(() => {
          successMessage.value = ''
        }, 3000)
      } catch (err) {
        errorMessage.value = err.message
        setTimeout(() => {
          errorMessage.value = ''
        }, 5000)
      }
    }
    
    const viewInventoryDetails = (inventory) => {
      // Implementar visualização de detalhes
      logger.info('Ver detalhes do inventário', { inventoryId: inventory?.id, code: inventory?.code })
    }
    
    const editInventory = (inventory) => {
      // Implementar edição
      logger.info('Editar inventário', { inventoryId: inventory?.id, code: inventory?.code })
    }
    
    const openCountingModal = async (inventory) => {
      selectedInventory.value = inventory
      showCountingModal.value = true
      
      try {
        countingAssets.value = await store.getInventoryAssets(inventory.id)
      } catch (err) {
        errorMessage.value = 'Erro ao carregar ativos para contagem'
        setTimeout(() => {
          errorMessage.value = ''
        }, 5000)
      }
    }
    
    const closeCountingModal = () => {
      showCountingModal.value = false
      selectedInventory.value = null
      countingAssets.value = []
    }
    
    const updateAssetCount = (asset) => {
      asset.counted = asset.countStatus !== 'not_counted'
      asset.hasDiscrepancy = ['not_found', 'damaged', 'wrong_location'].includes(asset.countStatus)
    }
    
    const saveCountingProgress = async () => {
      try {
        await store.updateInventoryCounting(selectedInventory.value.id, countingAssets.value)
        successMessage.value = 'Progresso da contagem salvo com sucesso!'
        closeCountingModal()
        setTimeout(() => {
          successMessage.value = ''
        }, 3000)
      } catch (err) {
        errorMessage.value = 'Erro ao salvar progresso da contagem'
        setTimeout(() => {
          errorMessage.value = ''
        }, 5000)
      }
    }
    
    const exportInventories = async () => {
      try {
        await store.exportInventories('csv', {
          status: statusFilter.value,
          location: locationFilter.value,
          startDate: dateRangeStart.value,
          endDate: dateRangeEnd.value
        })
        successMessage.value = 'Relatório exportado com sucesso!'
        setTimeout(() => {
          successMessage.value = ''
        }, 3000)
      } catch (err) {
        errorMessage.value = 'Erro ao exportar relatório'
        setTimeout(() => {
          errorMessage.value = ''
        }, 5000)
      }
    }
    
    // Watchers
    watch([searchQuery, statusFilter, locationFilter, dateRangeStart, dateRangeEnd], () => {
      currentPage.value = 1
    })
    
    watch(error, (newError) => {
      if (newError) {
        errorMessage.value = newError
        setTimeout(() => {
          store.clearError()
          errorMessage.value = ''
        }, 5000)
      }
    })
    
    // Lifecycle
    onMounted(() => {
      store.fetchInventories()
      assetsStore.fetchAssets?.()
    })
    
    return {
      // Estado
      searchQuery,
      statusFilter,
      locationFilter,
      dateRangeStart,
      dateRangeEnd,
      currentPage,
      selectedInventories,
      selectAll,
      showNewInventoryModal,
      showCountingModal,
      selectedInventory,
      newInventory,
      countingAssets,
      successMessage,
      errorMessage,
      
      // Store (inventário)
      loading,
      totalInventories,
      inventoriesInProgress,
      totalAssetsCount,
      totalDiscrepancies,
      locations,
      responsibles,
      
      // Store (ativos)
      assetsByWarrantyStatus,
      totalAssetsValue,
      totalAssets,
      
      // Computed
      filteredInventories,
      totalPages,
      startIndex,
      endIndex,
      paginatedInventories,
      
      // Métodos
      formatDate: formatDateLocal,
      formatCurrency,
      getStatusClass,
      getWarrantyStatusClass,
      getWarrantyMessage,
      formatWarrantyStatusDisplay,
      clearFilters,
      toggleSelectAll,
      closeNewInventoryModal,
      createInventory,
      viewInventoryDetails,
      editInventory,
      openCountingModal,
      closeCountingModal,
      updateAssetCount,
      saveCountingProgress,
      exportInventories,
      
      // Store instancia
      store
    }
  }
}
</script>

<style scoped>
.physical-inventory {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: #f0f9ff;
  color: #0ea5e9;
}

.stat-icon.active {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon.counted {
  background: #f0fdf4;
  color: #22c55e;
}

.stat-icon.discrepancy {
  background: #fef2f2;
  color: #ef4444;
}

.stat-icon.assets {
  background: #f0f9ff;
  color: #3b82f6;
}

.stat-icon.warranty-active {
  background: #f0fdf4;
  color: #22c55e;
}

.stat-icon.warranty-expiring {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon.value {
  background: #f5f3ff;
  color: #8b5cf6;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 2fr auto;
  gap: 16px;
  align-items: end;
}

.filter-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-range span {
  font-size: 14px;
  color: #666;
}

.results-info {
  margin-bottom: 16px;
  font-size: 14px;
  color: #666;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8fafc;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}

.data-table tr:hover {
  background: #f9fafb;
}

.code {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.inventory-info .description {
  font-weight: 500;
  color: #1a1a1a;
}

.inventory-info .type {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.location-info .name {
  font-weight: 500;
  color: #1a1a1a;
}

.location-info .code {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.responsible-info .name {
  font-weight: 500;
  color: #1a1a1a;
}

.responsible-info .email {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-planned {
  background: #f3f4f6;
  color: #6b7280;
}

.status-active {
  background: #fef3c7;
  color: #d97706;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-cancelled {
  background: #fee2e2;
  color: #dc2626;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 35px;
}

.discrepancy-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.discrepancy-badge.has-discrepancy {
  background: #fee2e2;
  color: #dc2626;
}

.discrepancy-badge.no-discrepancy {
  background: #dcfce7;
  color: #166534;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.pagination-info {
  font-size: 14px;
  color: #666;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal.large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
  padding: 4px;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
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

.counting-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.counting-stats .stat {
  font-size: 14px;
  color: #666;
}

.assets-list {
  max-height: 400px;
  overflow-y: auto;
}

.asset-item {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  gap: 16px;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 12px;
  background: white;
}

.asset-item.counted {
  background: #f0fdf4;
  border-color: #22c55e;
}

.asset-item.discrepancy {
  background: #fef3c7;
  border-color: #f59e0b;
}

.asset-header {
  margin-bottom: 12px;
}

.asset-info .asset-code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.asset-info .asset-name {
  font-weight: 500;
  font-size: 16px;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.asset-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 13px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-row .label {
  font-weight: 500;
  color: #6b7280;
  margin-right: 8px;
}

.detail-row .value {
  color: #1a1a1a;
  text-align: right;
}

.warranty-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.warranty-status.warranty-active {
  background: #dcfce7;
  color: #166534;
}

.warranty-status.warranty-expiring {
  background: #fef3c7;
  color: #d97706;
}

.warranty-status.warranty-expired {
  background: #fee2e2;
  color: #dc2626;
}

.warranty-status.warranty-none {
  background: #f3f4f6;
  color: #6b7280;
}

.warranty-status small {
  display: block;
  font-size: 10px;
  margin-top: 2px;
  opacity: 0.8;
}

.asset-info .asset-location {
  font-size: 12px;
  color: #666;
}

.counting-controls {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

.counting-status {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.text-success {
  color: #22c55e;
}

.text-warning {
  color: #f59e0b;
}

.text-muted {
  color: #9ca3af;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-success {
  background: #22c55e;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #16a34a;
}

.btn-outline {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-sm {
  padding: 8px 12px;
  font-size: 12px;
}

.alert {
  position: fixed;
  top: 24px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 1001;
  max-width: 400px;
}

.alert-success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

@media (max-width: 768px) {
  .physical-inventory {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .modal {
    width: 95%;
    margin: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .asset-item {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .counting-controls {
    grid-template-columns: 1fr;
  }
}
</style>