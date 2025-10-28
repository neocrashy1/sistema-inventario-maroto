<template>
  <div class="audits">
    <!-- Cabeçalho -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Auditorias</h1>
          <p class="page-subtitle">Gerencie auditorias de ativos e conformidade</p>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-outline"
            @click="exportData"
            :disabled="loading"
          >
            <i class="fas fa-download"></i>
            Exportar
          </button>
          <button 
            class="btn btn-primary"
            @click="showNewAuditModal = true"
          >
            <i class="fas fa-plus"></i>
            Nova Auditoria
          </button>
        </div>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-clipboard-check"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ auditsStore.totalAudits }}</div>
          <div class="stat-label">Total de Auditorias</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-play-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ auditsStore.activeAudits.length }}</div>
          <div class="stat-label">Em Andamento</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon completed">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ auditsStore.completedAudits.length }}</div>
          <div class="stat-label">Concluídas</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon issues">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ auditsStore.auditsWithIssues.length }}</div>
          <div class="stat-label">Com Problemas</div>
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
            placeholder="Título, código, auditor..."
            class="form-input"
          >
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="statusFilter" class="form-select">
            <option value="">Todos os Status</option>
            <option v-for="status in auditsStore.availableStatuses" 
                    :key="status.value" 
                    :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Tipo</label>
          <select v-model="typeFilter" class="form-select">
            <option value="">Todos os Tipos</option>
            <option v-for="type in auditsStore.availableTypes" 
                    :key="type.value" 
                    :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Prioridade</label>
          <select v-model="priorityFilter" class="form-select">
            <option value="">Todas as Prioridades</option>
            <option v-for="priority in auditsStore.availablePriorities" 
                    :key="priority.value" 
                    :value="priority.value">
              {{ priority.label }}
            </option>
          </select>
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
      <span>{{ auditsStore.filteredAudits.length }} auditoria(s) encontrada(s)</span>
    </div>

    <!-- Tabela de Auditorias -->
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
            <th>Título</th>
            <th>Tipo</th>
            <th>Auditor</th>
            <th>Data Início</th>
            <th>Data Fim</th>
            <th>Status</th>
            <th>Progresso</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="audit in paginatedAudits" :key="audit.id">
            <td>
              <input 
                type="checkbox" 
                v-model="selectedAudits"
                :value="audit.id"
              >
            </td>
            <td>
              <span class="code">{{ audit.code }}</span>
            </td>
            <td>
              <div class="audit-title">
                <div class="title">{{ audit.title }}</div>
                <div class="description">{{ audit.description }}</div>
              </div>
            </td>
            <td>
              <span class="type-badge" :class="getTypeClass(audit.type)">
                {{ getTypeLabel(audit.type) }}
              </span>
            </td>
            <td>
              <div class="auditor-info">
                <div class="name">{{ audit.auditor.name }}</div>
                <div class="email">{{ audit.auditor.email }}</div>
              </div>
            </td>
            <td>{{ formatDate(audit.startDate) }}</td>
            <td>{{ formatDate(audit.endDate) }}</td>
            <td>
              <span 
                class="status-badge"
                :class="getStatusClass(audit.status)"
              >
                {{ getStatusLabel(audit.status) }}
              </span>
            </td>
            <td>
              <div class="progress-container">
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :style="{ width: audit.progress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ audit.progress }}%</span>
              </div>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  class="btn-icon"
                  @click="viewAudit(audit)"
                  title="Ver detalhes"
                >
                  <i class="fas fa-eye"></i>
                </button>
                <button 
                  class="btn-icon"
                  @click="editAudit(audit)"
                  title="Editar"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  v-if="audit.status === 'planned'"
                  class="btn-icon success"
                  @click="startAudit(audit)"
                  title="Iniciar auditoria"
                >
                  <i class="fas fa-play"></i>
                </button>
                <button 
                  v-if="audit.status === 'in_progress'"
                  class="btn-icon success"
                  @click="completeAudit(audit)"
                  title="Concluir auditoria"
                >
                  <i class="fas fa-check"></i>
                </button>
                <button 
                  class="btn-icon danger"
                  @click="deleteAudit(audit)"
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

    <!-- Paginação -->
    <div class="pagination-container">
      <div class="pagination-info">
        Mostrando {{ startIndex + 1 }} a {{ endIndex }} de {{ auditsStore.filteredAudits.length }} registros
      </div>
      <div class="pagination">
        <button 
          class="btn btn-outline btn-sm"
          @click="previousPage"
          :disabled="currentPage === 1"
        >
          <i class="fas fa-chevron-left"></i>
          Anterior
        </button>
        
        <div class="page-numbers">
          <button 
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          class="btn btn-outline btn-sm"
          @click="nextPage"
          :disabled="currentPage === totalPages"
        >
          Próxima
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    </div>

    <!-- Modal Nova Auditoria -->
    <div v-if="showNewAuditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Nova Auditoria</h3>
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createAudit">
            <div class="form-grid">
              <div class="form-group">
                <label>Título *</label>
                <input 
                  type="text" 
                  v-model="newAudit.title"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group">
                <label>Tipo *</label>
                <select v-model="newAudit.type" class="form-select" required>
                  <option value="">Selecione o tipo</option>
                  <option v-for="type in auditsStore.availableTypes" 
                          :key="type.value" 
                          :value="type.value">
                    {{ type.label }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Prioridade *</label>
                <select v-model="newAudit.priority" class="form-select" required>
                  <option value="">Selecione a prioridade</option>
                  <option v-for="priority in auditsStore.availablePriorities" 
                          :key="priority.value" 
                          :value="priority.value">
                    {{ priority.label }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Auditor Principal *</label>
                <select v-model="newAudit.auditorId" class="form-select" required>
                  <option value="">Selecione o auditor</option>
                  <option v-for="auditor in auditsStore.uniqueAuditors" 
                          :key="auditor.id" 
                          :value="auditor.id">
                    {{ auditor.name }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Data de Início *</label>
                <input 
                  type="date" 
                  v-model="newAudit.startDate"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group">
                <label>Data de Fim *</label>
                <input 
                  type="date" 
                  v-model="newAudit.endDate"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group full-width">
                <label>Descrição</label>
                <textarea 
                  v-model="newAudit.description"
                  class="form-textarea"
                  rows="3"
                  placeholder="Descreva os objetivos e escopo da auditoria..."
                ></textarea>
              </div>
              
              <div class="form-group full-width">
                <label>Escopo</label>
                <textarea 
                  v-model="newAudit.scope"
                  class="form-textarea"
                  rows="2"
                  placeholder="Defina o escopo da auditoria..."
                ></textarea>
              </div>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="closeModal">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <i class="fas fa-save"></i>
                Criar Auditoria
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal Visualizar Auditoria -->
    <div v-if="showViewModal" class="modal-overlay" @click="closeViewModal">
      <div class="modal large" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedAudit?.title }}</h3>
          <button class="modal-close" @click="closeViewModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="selectedAudit" class="audit-details">
            <div class="details-grid">
              <div class="detail-item">
                <label>Código</label>
                <span>{{ selectedAudit.code }}</span>
              </div>
              <div class="detail-item">
                <label>Tipo</label>
                <span class="type-badge" :class="getTypeClass(selectedAudit.type)">
                  {{ getTypeLabel(selectedAudit.type) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <span class="status-badge" :class="getStatusClass(selectedAudit.status)">
                  {{ getStatusLabel(selectedAudit.status) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Prioridade</label>
                <span class="priority-badge" :class="getPriorityClass(selectedAudit.priority)">
                  {{ getPriorityLabel(selectedAudit.priority) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Auditor Principal</label>
                <span>{{ selectedAudit.auditor.name }}</span>
              </div>
              <div class="detail-item">
                <label>Localização</label>
                <span>{{ selectedAudit.location.name }}</span>
              </div>
              <div class="detail-item">
                <label>Data de Início</label>
                <span>{{ formatDate(selectedAudit.startDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Data de Fim</label>
                <span>{{ formatDate(selectedAudit.endDate) }}</span>
              </div>
              <div class="detail-item">
                <label>Progresso</label>
                <div class="progress-container">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill"
                      :style="{ width: selectedAudit.progress + '%' }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ selectedAudit.progress }}%</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Descrição</h4>
              <p>{{ selectedAudit.description }}</p>
            </div>
            
            <div class="detail-section" v-if="selectedAudit.scope">
              <h4>Escopo</h4>
              <p>{{ selectedAudit.scope }}</p>
            </div>
            
            <div class="detail-section" v-if="selectedAudit.findings.length > 0">
              <h4>Achados ({{ selectedAudit.findings.length }})</h4>
              <div class="findings-list">
                <div v-for="finding in selectedAudit.findings" :key="finding.id" class="finding-item">
                  <div class="finding-header">
                    <span class="finding-title">{{ finding.title }}</span>
                    <span class="severity-badge" :class="getSeverityClass(finding.severity)">
                      {{ getSeverityLabel(finding.severity) }}
                    </span>
                  </div>
                  <p class="finding-description">{{ finding.description }}</p>
                  <div class="finding-meta">
                    <span>Responsável: {{ finding.assignedTo }}</span>
                    <span>Prazo: {{ formatDate(finding.dueDate) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerta -->
    <div v-if="alert.show" class="alert" :class="alert.type">
      {{ alert.message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuditsStore } from '@/stores/audits'

export default {
  name: 'Audits',
  setup() {
    const auditsStore = useAuditsStore()
    
    // Estado reativo
    const loading = ref(false)
    const showNewAuditModal = ref(false)
    const showViewModal = ref(false)
    const selectedAudit = ref(null)
    const selectedAudits = ref([])
    const selectAll = ref(false)
    
    // Filtros
    const searchQuery = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const priorityFilter = ref('')
    
    // Paginação
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    
    // Novo item
    const newAudit = ref({
      title: '',
      description: '',
      type: '',
      priority: '',
      auditorId: '',
      startDate: '',
      endDate: '',
      scope: ''
    })
    
    // Alerta
    const alert = ref({
      show: false,
      type: '',
      message: ''
    })
    
    // Watchers para filtros
    watch([searchQuery, statusFilter, typeFilter, priorityFilter], () => {
      auditsStore.setSearchFilter(searchQuery.value)
      auditsStore.setStatusFilter(statusFilter.value)
      auditsStore.setTypeFilter(typeFilter.value)
      auditsStore.setPriorityFilter(priorityFilter.value)
      currentPage.value = 1
    })
    
    // Computed
    const paginatedAudits = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return auditsStore.filteredAudits.slice(start, end)
    })
    
    const totalPages = computed(() => {
      return Math.ceil(auditsStore.filteredAudits.length / itemsPerPage.value)
    })
    
    const startIndex = computed(() => {
      return (currentPage.value - 1) * itemsPerPage.value
    })
    
    const endIndex = computed(() => {
      return Math.min(startIndex.value + itemsPerPage.value, auditsStore.filteredAudits.length)
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
    
    // Métodos
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('pt-BR')
    }
    
    const getTypeLabel = (type) => {
      const typeObj = auditsStore.availableTypes.find(t => t.value === type)
      return typeObj ? typeObj.label : type
    }
    
    const getStatusLabel = (status) => {
      const statusObj = auditsStore.availableStatuses.find(s => s.value === status)
      return statusObj ? statusObj.label : status
    }
    
    const getPriorityLabel = (priority) => {
      const priorityObj = auditsStore.availablePriorities.find(p => p.value === priority)
      return priorityObj ? priorityObj.label : priority
    }
    
    const getSeverityLabel = (severity) => {
      const severityMap = {
        low: 'Baixa',
        medium: 'Média',
        high: 'Alta',
        critical: 'Crítica'
      }
      return severityMap[severity] || severity
    }
    
    const getTypeClass = (type) => {
      const classMap = {
        inventory: 'type-inventory',
        compliance: 'type-compliance',
        security: 'type-security',
        operational: 'type-operational',
        financial: 'type-financial',
        quality: 'type-quality'
      }
      return classMap[type] || 'type-default'
    }
    
    const getStatusClass = (status) => {
      const classMap = {
        draft: 'status-draft',
        planned: 'status-planned',
        in_progress: 'status-progress',
        completed: 'status-completed',
        cancelled: 'status-cancelled'
      }
      return classMap[status] || 'status-default'
    }
    
    const getPriorityClass = (priority) => {
      const classMap = {
        low: 'priority-low',
        medium: 'priority-medium',
        high: 'priority-high',
        critical: 'priority-critical'
      }
      return classMap[priority] || 'priority-default'
    }
    
    const getSeverityClass = (severity) => {
      const classMap = {
        low: 'severity-low',
        medium: 'severity-medium',
        high: 'severity-high',
        critical: 'severity-critical'
      }
      return classMap[severity] || 'severity-default'
    }
    
    const clearFilters = () => {
      searchQuery.value = ''
      statusFilter.value = ''
      typeFilter.value = ''
      priorityFilter.value = ''
      auditsStore.clearFilters()
    }
    
    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedAudits.value = paginatedAudits.value.map(audit => audit.id)
      } else {
        selectedAudits.value = []
      }
    }
    
    const goToPage = (page) => {
      currentPage.value = page
    }
    
    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    
    const viewAudit = (audit) => {
      selectedAudit.value = audit
      showViewModal.value = true
    }
    
    const editAudit = (audit) => {
      // Implementar edição
      showAlert('info', 'Funcionalidade de edição em desenvolvimento')
    }
    
    const startAudit = async (audit) => {
      try {
        loading.value = true
        await auditsStore.startAudit(audit.id)
        showAlert('success', 'Auditoria iniciada com sucesso!')
      } catch (error) {
        showAlert('error', 'Erro ao iniciar auditoria')
      } finally {
        loading.value = false
      }
    }
    
    const completeAudit = async (audit) => {
      try {
        loading.value = true
        await auditsStore.completeAudit(audit.id)
        showAlert('success', 'Auditoria concluída com sucesso!')
      } catch (error) {
        showAlert('error', 'Erro ao concluir auditoria')
      } finally {
        loading.value = false
      }
    }
    
    const deleteAudit = async (audit) => {
      if (confirm(`Tem certeza que deseja excluir a auditoria "${audit.title}"?`)) {
        try {
          loading.value = true
          await auditsStore.deleteAudit(audit.id)
          showAlert('success', 'Auditoria excluída com sucesso!')
        } catch (error) {
          showAlert('error', 'Erro ao excluir auditoria')
        } finally {
          loading.value = false
        }
      }
    }
    
    const createAudit = async () => {
      try {
        loading.value = true
        
        // Buscar auditor selecionado
        const auditor = auditsStore.uniqueAuditors.find(a => a.id === parseInt(newAudit.value.auditorId))
        
        const auditData = {
          ...newAudit.value,
          auditor: auditor || auditsStore.uniqueAuditors[0],
          location: auditsStore.uniqueLocations[0], // Usar primeira localização disponível
          team: [{ id: auditor?.id || 1, name: auditor?.name || 'Auditor', role: 'Auditor Principal' }]
        }
        
        await auditsStore.addAudit(auditData)
        showAlert('success', 'Auditoria criada com sucesso!')
        closeModal()
      } catch (error) {
        showAlert('error', 'Erro ao criar auditoria')
      } finally {
        loading.value = false
      }
    }
    
    const exportData = () => {
      try {
        const data = auditsStore.exportAudits()
        const csv = convertToCSV(data)
        downloadCSV(csv, 'auditorias.csv')
        showAlert('success', 'Dados exportados com sucesso!')
      } catch (error) {
        showAlert('error', 'Erro ao exportar dados')
      }
    }
    
    const convertToCSV = (data) => {
      if (!data.length) return ''
      
      const headers = Object.keys(data[0])
      const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
      ].join('\n')
      
      return csvContent
    }
    
    const downloadCSV = (csv, filename) => {
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
    
    const closeModal = () => {
      showNewAuditModal.value = false
      newAudit.value = {
        title: '',
        description: '',
        type: '',
        priority: '',
        auditorId: '',
        startDate: '',
        endDate: '',
        scope: ''
      }
    }
    
    const closeViewModal = () => {
      showViewModal.value = false
      selectedAudit.value = null
    }
    
    const showAlert = (type, message) => {
      alert.value = {
        show: true,
        type: type === 'success' ? 'alert-success' : 'alert-error',
        message
      }
      
      setTimeout(() => {
        alert.value.show = false
      }, 3000)
    }
    
    return {
      // Store
      auditsStore,
      
      // Estado
      loading,
      showNewAuditModal,
      showViewModal,
      selectedAudit,
      selectedAudits,
      selectAll,
      
      // Filtros
      searchQuery,
      statusFilter,
      typeFilter,
      priorityFilter,
      
      // Paginação
      currentPage,
      itemsPerPage,
      paginatedAudits,
      totalPages,
      startIndex,
      endIndex,
      visiblePages,
      
      // Formulário
      newAudit,
      
      // Alerta
      alert,
      
      // Métodos
      formatDate,
      getTypeLabel,
      getStatusLabel,
      getPriorityLabel,
      getSeverityLabel,
      getTypeClass,
      getStatusClass,
      getPriorityClass,
      getSeverityClass,
      clearFilters,
      toggleSelectAll,
      goToPage,
      previousPage,
      nextPage,
      viewAudit,
      editAudit,
      startAudit,
      completeAudit,
      deleteAudit,
      createAudit,
      exportData,
      closeModal,
      closeViewModal
    }
  }
}
</script>

<style scoped>
.audits {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-text h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.header-text p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: #e5e7eb;
  color: #6b7280;
}

.stat-icon.active {
  background: #dbeafe;
  color: #3b82f6;
}

.stat-icon.completed {
  background: #dcfce7;
  color: #22c55e;
}

.stat-icon.issues {
  background: #fee2e2;
  color: #ef4444;
}

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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr auto;
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

.results-info {
  margin-bottom: 16px;
  font-size: 14px;
  color: #666;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
}

.data-table tr:hover {
  background: #f9fafb;
}

.code {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.audit-title .title {
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.audit-title .description {
  font-size: 12px;
  color: #666;
}

.auditor-info .name {
  font-weight: 500;
  color: #1a1a1a;
}

.auditor-info .email {
  font-size: 12px;
  color: #666;
}

.type-badge,
.status-badge,
.priority-badge,
.severity-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.type-inventory { background: #dbeafe; color: #1e40af; }
.type-compliance { background: #fef3c7; color: #92400e; }
.type-security { background: #fee2e2; color: #991b1b; }
.type-operational { background: #e0e7ff; color: #3730a3; }
.type-financial { background: #dcfce7; color: #166534; }
.type-quality { background: #f3e8ff; color: #7c2d12; }

.status-draft { background: #f3f4f6; color: #374151; }
.status-planned { background: #dbeafe; color: #1e40af; }
.status-progress { background: #fef3c7; color: #92400e; }
.status-completed { background: #dcfce7; color: #166534; }
.status-cancelled { background: #fee2e2; color: #991b1b; }

.priority-low { background: #f0fdf4; color: #166534; }
.priority-medium { background: #fef3c7; color: #92400e; }
.priority-high { background: #fee2e2; color: #991b1b; }
.priority-critical { background: #fdf2f8; color: #be185d; }

.severity-low { background: #f0fdf4; color: #166534; }
.severity-medium { background: #fef3c7; color: #92400e; }
.severity-high { background: #fee2e2; color: #991b1b; }
.severity-critical { background: #fdf2f8; color: #be185d; }

.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
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

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f3f4f6;
  color: #666;
}

.btn-icon:hover {
  background: #e5e7eb;
}

.btn-icon.success {
  background: #dcfce7;
  color: #166534;
}

.btn-icon.success:hover {
  background: #bbf7d0;
}

.btn-icon.danger {
  background: #fee2e2;
  color: #991b1b;
}

.btn-icon.danger:hover {
  background: #fecaca;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #f3f4f6;
  color: #666;
  font-size: 14px;
}

.page-btn:hover {
  background: #e5e7eb;
}

.page-btn.active {
  background: #3b82f6;
  color: white;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.audit-details {
  max-height: 60vh;
  overflow-y: auto;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-size: 12px;
  font-weight: 500;
  color: #666;
  text-transform: uppercase;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.findings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.finding-item {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.finding-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.finding-title {
  font-weight: 600;
  color: #1a1a1a;
}

.finding-description {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.finding-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
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
  .audits {
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
  
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>