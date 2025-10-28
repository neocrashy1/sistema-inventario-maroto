<template>
  <div class="service-orders-page">
    <!-- Cabeçalho -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Ordens de Serviço</h1>
          <p class="page-subtitle">Gerencie ordens de serviço e manutenções dos ativos</p>
        </div>
        <div class="header-actions">
          <button 
            @click="exportOrders" 
            class="btn btn-outline"
            :disabled="loading"
          >
            <i class="icon-download"></i>
            Exportar
          </button>
          <button 
            @click="showCreateModal = true" 
            class="btn btn-primary"
          >
            <i class="icon-plus"></i>
            Nova Ordem
          </button>
        </div>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="icon-clipboard"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalOrders }}</div>
          <div class="stat-label">Total de Ordens</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon pending">
          <i class="icon-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ ordersInProgress }}</div>
          <div class="stat-label">Em Andamento</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon overdue">
          <i class="icon-alert"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ overdueOrders }}</div>
          <div class="stat-label">Em Atraso</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon completed">
          <i class="icon-check"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ completedOrders }}</div>
          <div class="stat-label">Concluídas</div>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="search-box">
          <i class="icon-search"></i>
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Buscar por código, descrição, técnico ou ativo..."
            class="search-input"
          />
        </div>
        
        <select v-model="filters.status" class="filter-select">
          <option value="">Todos os Status</option>
          <option value="open">Aberta</option>
          <option value="in_progress">Em Andamento</option>
          <option value="completed">Concluída</option>
          <option value="cancelled">Cancelada</option>
        </select>
        
        <select v-model="filters.priority" class="filter-select">
          <option value="">Todas as Prioridades</option>
          <option value="low">Baixa</option>
          <option value="medium">Média</option>
          <option value="high">Alta</option>
          <option value="urgent">Urgente</option>
        </select>
        
        <select v-model="filters.type" class="filter-select">
          <option value="">Todos os Tipos</option>
          <option value="preventive">Preventiva</option>
          <option value="corrective">Corretiva</option>
          <option value="emergency">Emergencial</option>
        </select>
        
        <button @click="clearFilters" class="btn btn-outline btn-sm">
          <i class="icon-x"></i>
          Limpar
        </button>
      </div>
      
      <div class="filters-row">
        <div class="date-range">
          <label>Período:</label>
          <input
            v-model="filters.dateRange.start"
            type="date"
            class="date-input"
          />
          <span>até</span>
          <input
            v-model="filters.dateRange.end"
            type="date"
            class="date-input"
          />
        </div>
      </div>
    </div>

    <!-- Tabela de Ordens -->
    <div class="table-container">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Carregando ordens de serviço...</p>
      </div>
      
      <div v-else-if="filteredOrders.length === 0" class="empty-state">
        <i class="icon-clipboard"></i>
        <h3>Nenhuma ordem encontrada</h3>
        <p>Não há ordens de serviço que correspondam aos filtros aplicados.</p>
      </div>
      
      <table v-else class="orders-table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Descrição</th>
            <th>Ativo</th>
            <th>Tipo</th>
            <th>Prioridade</th>
            <th>Técnico</th>
            <th>Status</th>
            <th>Data Abertura</th>
            <th>Prazo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in filteredOrders" :key="order.id">
            <td>
              <span class="order-code">{{ order.code }}</span>
            </td>
            <td>
              <div class="order-description">
                <span class="title">{{ order.title }}</span>
                <span class="description">{{ order.description }}</span>
              </div>
            </td>
            <td>
              <div class="asset-info">
                <span class="asset-code">{{ order.assetCode }}</span>
                <span class="asset-name">{{ order.assetName }}</span>
              </div>
            </td>
            <td>
              <span :class="['type-badge', order.type]">
                {{ getTypeLabel(order.type) }}
              </span>
            </td>
            <td>
              <span :class="['priority-badge', order.priority]">
                {{ getPriorityLabel(order.priority) }}
              </span>
            </td>
            <td>
              <div class="technician-info">
                <span class="name">{{ order.assignedTo }}</span>
                <span class="department">{{ order.department }}</span>
              </div>
            </td>
            <td>
              <span :class="['status-badge', order.status]">
                {{ getStatusLabel(order.status) }}
              </span>
            </td>
            <td>{{ formatDate(order.createdAt) }}</td>
            <td>
              <span :class="['due-date', { overdue: isOverdue(order.dueDate) }]">
                {{ formatDate(order.dueDate) }}
              </span>
            </td>
            <td>
              <div class="actions">
                <button 
                  @click="viewOrder(order)" 
                  class="btn btn-sm btn-outline"
                  title="Ver Detalhes"
                >
                  <i class="icon-eye"></i>
                </button>
                <button 
                  v-if="order.status !== 'completed' && order.status !== 'cancelled'"
                  @click="editOrder(order)" 
                  class="btn btn-sm btn-outline"
                  title="Editar"
                >
                  <i class="icon-edit"></i>
                </button>
                <button 
                  v-if="order.status === 'open'"
                  @click="startOrder(order)" 
                  class="btn btn-sm btn-primary"
                  title="Iniciar"
                >
                  <i class="icon-play"></i>
                </button>
                <button 
                  v-if="order.status === 'in_progress'"
                  @click="completeOrder(order)" 
                  class="btn btn-sm btn-success"
                  title="Concluir"
                >
                  <i class="icon-check"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Criar/Editar Ordem -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? 'Editar Ordem de Serviço' : 'Nova Ordem de Serviço' }}</h3>
          <button @click="closeModals" class="modal-close">
            <i class="icon-x"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveOrder" class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label>Título *</label>
              <input
                v-model="orderForm.title"
                type="text"
                required
                placeholder="Título da ordem de serviço"
              />
            </div>
            
            <div class="form-group">
              <label>Tipo *</label>
              <select v-model="orderForm.type" required>
                <option value="">Selecione o tipo</option>
                <option value="preventive">Preventiva</option>
                <option value="corrective">Corretiva</option>
                <option value="emergency">Emergencial</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Prioridade *</label>
              <select v-model="orderForm.priority" required>
                <option value="">Selecione a prioridade</option>
                <option value="low">Baixa</option>
                <option value="medium">Média</option>
                <option value="high">Alta</option>
                <option value="urgent">Urgente</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Ativo *</label>
              <select v-model="orderForm.assetId" required>
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
              <label>Técnico Responsável *</label>
              <select v-model="orderForm.assignedTo" required>
                <option value="">Selecione o técnico</option>
                <option 
                  v-for="technician in technicians" 
                  :key="technician.id" 
                  :value="technician.name"
                >
                  {{ technician.name }} - {{ technician.department }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Data de Vencimento *</label>
              <input
                v-model="orderForm.dueDate"
                type="date"
                required
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>Descrição *</label>
            <textarea
              v-model="orderForm.description"
              required
              rows="4"
              placeholder="Descreva o problema ou serviço a ser realizado..."
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>Observações</label>
            <textarea
              v-model="orderForm.notes"
              rows="3"
              placeholder="Observações adicionais..."
            ></textarea>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">
            Cancelar
          </button>
          <button @click="saveOrder" type="submit" class="btn btn-primary" :disabled="loading">
            {{ showEditModal ? 'Atualizar' : 'Criar' }} Ordem
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Ver Detalhes -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>Detalhes da Ordem de Serviço</h3>
          <button @click="closeModals" class="modal-close">
            <i class="icon-x"></i>
          </button>
        </div>
        
        <div class="modal-body" v-if="selectedOrder">
          <div class="details-grid">
            <div class="detail-section">
              <h4>Informações Gerais</h4>
              <div class="detail-item">
                <label>Código:</label>
                <span>{{ selectedOrder.code }}</span>
              </div>
              <div class="detail-item">
                <label>Título:</label>
                <span>{{ selectedOrder.title }}</span>
              </div>
              <div class="detail-item">
                <label>Tipo:</label>
                <span :class="['type-badge', selectedOrder.type]">
                  {{ getTypeLabel(selectedOrder.type) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Prioridade:</label>
                <span :class="['priority-badge', selectedOrder.priority]">
                  {{ getPriorityLabel(selectedOrder.priority) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Status:</label>
                <span :class="['status-badge', selectedOrder.status]">
                  {{ getStatusLabel(selectedOrder.status) }}
                </span>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Ativo e Responsável</h4>
              <div class="detail-item">
                <label>Ativo:</label>
                <span>{{ selectedOrder.assetCode }} - {{ selectedOrder.assetName }}</span>
              </div>
              <div class="detail-item">
                <label>Técnico:</label>
                <span>{{ selectedOrder.assignedTo }}</span>
              </div>
              <div class="detail-item">
                <label>Departamento:</label>
                <span>{{ selectedOrder.department }}</span>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Datas</h4>
              <div class="detail-item">
                <label>Criada em:</label>
                <span>{{ formatDateTime(selectedOrder.createdAt) }}</span>
              </div>
              <div class="detail-item">
                <label>Prazo:</label>
                <span :class="{ overdue: isOverdue(selectedOrder.dueDate) }">
                  {{ formatDateTime(selectedOrder.dueDate) }}
                </span>
              </div>
              <div class="detail-item" v-if="selectedOrder.startedAt">
                <label>Iniciada em:</label>
                <span>{{ formatDateTime(selectedOrder.startedAt) }}</span>
              </div>
              <div class="detail-item" v-if="selectedOrder.completedAt">
                <label>Concluída em:</label>
                <span>{{ formatDateTime(selectedOrder.completedAt) }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-section full-width">
            <h4>Descrição</h4>
            <p>{{ selectedOrder.description }}</p>
          </div>
          
          <div class="detail-section full-width" v-if="selectedOrder.notes">
            <h4>Observações</h4>
            <p>{{ selectedOrder.notes }}</p>
          </div>
          
          <div class="detail-section full-width" v-if="selectedOrder.resolution">
            <h4>Resolução</h4>
            <p>{{ selectedOrder.resolution }}</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModals" class="btn btn-outline">
            Fechar
          </button>
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
import { useServiceOrdersStore } from '@/stores/serviceOrders'
import { computed, ref, onMounted, watch } from 'vue'

export default {
  name: 'ServiceOrders',
  setup() {
    const store = useServiceOrdersStore()
    
    // Estados reativos
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDetailsModal = ref(false)
    const selectedOrder = ref(null)
    const successMessage = ref('')
    const errorMessage = ref('')
    
    // Formulário
    const orderForm = ref({
      title: '',
      description: '',
      type: '',
      priority: '',
      assetId: '',
      assignedTo: '',
      dueDate: '',
      notes: ''
    })
    
    // Computed properties
    const searchTerm = computed({
      get: () => store.searchTerm,
      set: (value) => store.setSearchTerm(value)
    })
    
    const filters = computed({
      get: () => store.filters,
      set: (value) => store.setFilters(value)
    })
    
    const filteredOrders = computed(() => store.filteredOrders)
    const totalOrders = computed(() => store.totalOrders)
    const ordersInProgress = computed(() => store.ordersInProgress)
    const overdueOrders = computed(() => store.overdueOrders)
    const completedOrders = computed(() => store.completedOrders)
    const loading = computed(() => store.loading)
    const technicians = computed(() => store.technicians)
    const availableAssets = computed(() => store.availableAssets)
    
    // Métodos
    const clearFilters = () => {
      store.clearFilters()
    }
    
    const exportOrders = async () => {
      try {
        await store.exportOrders()
        showSuccess('Dados exportados com sucesso!')
      } catch (error) {
        showError('Erro ao exportar dados')
      }
    }
    
    const viewOrder = (order) => {
      selectedOrder.value = order
      showDetailsModal.value = true
    }
    
    const editOrder = (order) => {
      selectedOrder.value = order
      orderForm.value = {
        title: order.title,
        description: order.description,
        type: order.type,
        priority: order.priority,
        assetId: order.assetId,
        assignedTo: order.assignedTo,
        dueDate: order.dueDate,
        notes: order.notes || ''
      }
      showEditModal.value = true
    }
    
    const startOrder = async (order) => {
      try {
        await store.startOrder(order.id)
        showSuccess('Ordem iniciada com sucesso!')
      } catch (error) {
        showError('Erro ao iniciar ordem')
      }
    }
    
    const completeOrder = async (order) => {
      try {
        await store.completeOrder(order.id)
        showSuccess('Ordem concluída com sucesso!')
      } catch (error) {
        showError('Erro ao concluir ordem')
      }
    }
    
    const saveOrder = async () => {
      try {
        if (showEditModal.value) {
          await store.updateOrder(selectedOrder.value.id, orderForm.value)
          showSuccess('Ordem atualizada com sucesso!')
        } else {
          await store.createOrder(orderForm.value)
          showSuccess('Ordem criada com sucesso!')
        }
        closeModals()
        resetForm()
      } catch (error) {
        showError('Erro ao salvar ordem')
      }
    }
    
    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      showDetailsModal.value = false
      selectedOrder.value = null
      resetForm()
    }
    
    const resetForm = () => {
      orderForm.value = {
        title: '',
        description: '',
        type: '',
        priority: '',
        assetId: '',
        assignedTo: '',
        dueDate: '',
        notes: ''
      }
    }
    
    const showSuccess = (message) => {
      successMessage.value = message
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    }
    
    const showError = (message) => {
      errorMessage.value = message
      setTimeout(() => {
        errorMessage.value = ''
      }, 3000)
    }
    
    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('pt-BR')
    }
    
    const formatDateTime = (date) => {
      return new Date(date).toLocaleString('pt-BR')
    }
    
    const isOverdue = (dueDate) => {
      return new Date(dueDate) < new Date()
    }
    
    const getStatusLabel = (status) => {
      return store.getStatusLabel(status)
    }
    
    const getTypeLabel = (type) => {
      const typeLabels = {
        preventive: 'Preventiva',
        corrective: 'Corretiva',
        emergency: 'Emergencial'
      }
      return typeLabels[type] || type
    }
    
    const getPriorityLabel = (priority) => {
      const priorityLabels = {
        low: 'Baixa',
        medium: 'Média',
        high: 'Alta',
        urgent: 'Urgente'
      }
      return priorityLabels[priority] || priority
    }
    
    // Lifecycle
    onMounted(() => {
      store.fetchOrders()
    })
    
    return {
      // Estados
      showCreateModal,
      showEditModal,
      showDetailsModal,
      selectedOrder,
      successMessage,
      errorMessage,
      orderForm,
      
      // Computed
      searchTerm,
      filters,
      filteredOrders,
      totalOrders,
      ordersInProgress,
      overdueOrders,
      completedOrders,
      loading,
      technicians,
      availableAssets,
      
      // Métodos
      clearFilters,
      exportOrders,
      viewOrder,
      editOrder,
      startOrder,
      completeOrder,
      saveOrder,
      closeModals,
      formatDate,
      formatDateTime,
      isOverdue,
      getStatusLabel,
      getTypeLabel,
      getPriorityLabel
    }
  }
}
</script>

<style scoped>
.service-orders-page {
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

.header-text h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.header-text p {
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
  font-size: 24px;
  color: white;
}

.stat-icon.total { background: #3b82f6; }
.stat-icon.pending { background: #f59e0b; }
.stat-icon.overdue { background: #ef4444; }
.stat-icon.completed { background: #10b981; }

.stat-number {
  font-size: 32px;
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

.filters-row {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.filters-row + .filters-row {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.filter-select {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  min-width: 150px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th {
  background: #f9fafb;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.orders-table td {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: top;
}

.order-code {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #1f2937;
}

.order-description .title {
  display: block;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.order-description .description {
  display: block;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.4;
}

.asset-info .asset-code {
  display: block;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #1f2937;
}

.asset-info .asset-name {
  display: block;
  font-size: 14px;
  color: #6b7280;
}

.technician-info .name {
  display: block;
  font-weight: 600;
  color: #1f2937;
}

.technician-info .department {
  display: block;
  font-size: 14px;
  color: #6b7280;
}

.type-badge, .priority-badge, .status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.type-badge.preventive { background: #dbeafe; color: #1e40af; }
.type-badge.corrective { background: #fef3c7; color: #92400e; }
.type-badge.emergency { background: #fee2e2; color: #dc2626; }

.priority-badge.low { background: #f0f9ff; color: #0369a1; }
.priority-badge.medium { background: #fefce8; color: #ca8a04; }
.priority-badge.high { background: #fef2f2; color: #dc2626; }
.priority-badge.urgent { background: #fdf2f8; color: #be185d; }

.status-badge.open { background: #f0f9ff; color: #0369a1; }
.status-badge.in_progress { background: #fefce8; color: #ca8a04; }
.status-badge.completed { background: #f0fdf4; color: #166534; }
.status-badge.cancelled { background: #f9fafb; color: #6b7280; }

.due-date.overdue {
  color: #dc2626;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 8px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 48px 24px;
  color: #6b7280;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 800px;
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
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.detail-section {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
}

.detail-section.full-width {
  grid-column: 1 / -1;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.detail-item label {
  font-weight: 600;
  color: #6b7280;
  margin-right: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  border: none;
  font-size: 14px;
  transition: all 0.2s;
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
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
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
  font-weight: 600;
  z-index: 1001;
  animation: slideIn 0.3s ease;
}

.alert-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .service-orders-page {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .orders-table {
    font-size: 14px;
  }
  
  .orders-table th,
  .orders-table td {
    padding: 12px 8px;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>