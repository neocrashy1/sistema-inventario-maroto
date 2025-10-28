<template>
  <div class="reports">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Relatórios</h1>
        <p class="page-subtitle">Gerencie e gere relatórios do sistema de gestão de ativos</p>
      </div>
      
      <div class="page-actions">
        <button 
          class="btn btn-outline"
          @click="exportReportsList"
          :disabled="loading"
        >
          <i class="fas fa-download"></i>
          Exportar Lista
        </button>
        <button 
          class="btn btn-primary"
          @click="showNewReportModal = true"
        >
          <i class="fas fa-plus"></i>
          Gerar Relatório
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ reportStatistics.total }}</div>
          <div class="stat-label">Total de Relatórios</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon completed">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ reportStatistics.completed }}</div>
          <div class="stat-label">Concluídos</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon processing">
          <i class="fas fa-sync-alt"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ reportStatistics.processing }}</div>
          <div class="stat-label">Processando</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon size">
          <i class="fas fa-hdd"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ reportStatistics.totalSize }} MB</div>
          <div class="stat-label">Tamanho Total</div>
        </div>
      </div>
    </div>

    <!-- Report Types Grid -->
    <div class="section">
      <h2 class="section-title">Tipos de Relatórios Disponíveis</h2>
      <div class="report-types-grid">
        <div 
          v-for="reportType in reportTypes" 
          :key="reportType.id"
          class="report-type-card"
          @click="generateReportFromType(reportType)"
        >
          <div class="report-type-icon" :class="reportType.color">
            <i :class="reportType.icon"></i>
          </div>
          <div class="report-type-content">
            <h3>{{ reportType.name }}</h3>
            <p>{{ reportType.description }}</p>
            <span class="report-type-category">{{ getCategoryName(reportType.category) }}</span>
          </div>
          <div class="report-type-action">
            <i class="fas fa-arrow-right"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="section">
      <h2 class="section-title">Relatórios Gerados</h2>
      <div class="filters-section">
        <div class="filters-grid">
          <div class="filter-group">
            <label>Buscar</label>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="Nome do relatório, gerado por..."
              class="form-input"
            >
          </div>
          
          <div class="filter-group">
            <label>Categoria</label>
            <select v-model="filters.category" class="form-select">
              <option value="">Todas as Categorias</option>
              <option 
                v-for="category in reportCategories" 
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }} ({{ category.count }})
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Status</label>
            <select v-model="filters.status" class="form-select">
              <option value="">Todos os Status</option>
              <option value="completed">Concluído</option>
              <option value="processing">Processando</option>
              <option value="failed">Falhou</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Formato</label>
            <select v-model="filters.format" class="form-select">
              <option value="">Todos os Formatos</option>
              <option value="PDF">PDF</option>
              <option value="Excel">Excel</option>
              <option value="CSV">CSV</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Período</label>
            <select v-model="filters.dateRange" class="form-select">
              <option value="last-7-days">Últimos 7 dias</option>
              <option value="last-30-days">Últimos 30 dias</option>
              <option value="last-90-days">Últimos 90 dias</option>
              <option value="last-year">Último ano</option>
              <option value="all">Todos</option>
            </select>
          </div>
          
          <div class="filter-actions">
            <button class="btn btn-outline btn-sm" @click="clearFilters">
              <i class="fas fa-times"></i>
              Limpar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reports Table -->
    <div class="reports-table-container">
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Carregando relatórios...</p>
      </div>
      
      <div v-else-if="filteredReports.length === 0" class="empty-state">
        <i class="fas fa-file-alt"></i>
        <h3>Nenhum relatório encontrado</h3>
        <p>Não há relatórios que correspondam aos filtros selecionados.</p>
      </div>
      
      <div v-else class="table-wrapper">
        <table class="reports-table">
          <thead>
            <tr>
              <th>Nome do Relatório</th>
              <th>Tipo</th>
              <th>Data de Geração</th>
              <th>Gerado Por</th>
              <th>Status</th>
              <th>Formato</th>
              <th>Tamanho</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in filteredReports" :key="report.id">
              <td>
                <div class="report-name">
                  <i class="fas fa-file-alt"></i>
                  {{ report.name }}
                </div>
              </td>
              <td>
                <span class="report-type-badge">
                  {{ getReportTypeName(report.type) }}
                </span>
              </td>
              <td>{{ formatDate(report.generatedAt) }}</td>
              <td>{{ report.generatedBy }}</td>
              <td>
                <span class="status-badge" :class="report.status">
                  <i class="fas fa-circle"></i>
                  {{ getStatusLabel(report.status) }}
                </span>
              </td>
              <td>
                <span class="format-badge" :class="report.format.toLowerCase()">
                  {{ report.format }}
                </span>
              </td>
              <td>{{ report.size || 'N/A' }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="report.status === 'completed'"
                    class="btn btn-sm btn-outline"
                    @click="downloadReport(report.id)"
                    title="Download"
                  >
                    <i class="fas fa-download"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-danger"
                    @click="deleteReport(report.id)"
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

    <!-- Generate Report Modal -->
    <div v-if="showNewReportModal" class="modal-overlay" @click="showNewReportModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Gerar Novo Relatório</h3>
          <button class="modal-close" @click="showNewReportModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>Tipo de Relatório</label>
            <select v-model="newReport.type" class="form-select">
              <option value="">Selecione um tipo</option>
              <option 
                v-for="type in reportTypes" 
                :key="type.id"
                :value="type.id"
              >
                {{ type.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Formato</label>
            <select v-model="newReport.format" class="form-select">
              <option value="PDF">PDF</option>
              <option value="Excel">Excel</option>
              <option value="CSV">CSV</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Período</label>
            <div class="date-range">
              <input 
                type="date" 
                v-model="newReport.startDate"
                class="form-input"
              >
              <span>até</span>
              <input 
                type="date" 
                v-model="newReport.endDate"
                class="form-input"
              >
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showNewReportModal = false">
            Cancelar
          </button>
          <button 
            class="btn btn-primary"
            @click="generateNewReport"
            :disabled="!newReport.type || generatingReport"
          >
            <i class="fas fa-spinner fa-spin" v-if="generatingReport"></i>
            <i class="fas fa-plus" v-else></i>
            {{ generatingReport ? 'Gerando...' : 'Gerar Relatório' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted } from 'vue'
import { useReportsStore } from '@/stores/reports'

const reportsStore = useReportsStore()

// Estado local
const loading = ref(false)
const searchQuery = ref('')
const showNewReportModal = ref(false)
const generatingReport = ref(false)

const newReport = ref({
  type: '',
  format: 'PDF',
  startDate: '',
  endDate: ''
})

// Getters do store
const { 
  reportTypes, 
  reportCategories, 
  reportStatistics, 
  filters 
} = reportsStore

// Computed
const filteredReports = computed(() => {
  let reports = reportsStore.filteredReports
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    reports = reports.filter(report => 
      report.name.toLowerCase().includes(query) ||
      report.generatedBy.toLowerCase().includes(query)
    )
  }
  
  return reports
})

// Métodos
const generateReportFromType = (reportType) => {
  newReport.value.type = reportType.id
  showNewReportModal.value = true
}

const generateNewReport = async () => {
  if (!newReport.value.type) return
  
  generatingReport.value = true
  
  try {
    await reportsStore.generateReport(newReport.value.type, {
      format: newReport.value.format,
      startDate: newReport.value.startDate,
      endDate: newReport.value.endDate
    })
    
    showNewReportModal.value = false
    resetNewReport()
  } catch (error) {
    logger.error('Erro ao gerar relatório:', error)
  } finally {
    generatingReport.value = false
  }
}

const resetNewReport = () => {
  newReport.value = {
    type: '',
    format: 'PDF',
    startDate: '',
    endDate: ''
  }
}

const downloadReport = (reportId) => {
  reportsStore.downloadReport(reportId)
}

const deleteReport = (reportId) => {
  if (confirm('Tem certeza que deseja excluir este relatório?')) {
    reportsStore.deleteReport(reportId)
  }
}

const exportReportsList = () => {
  reportsStore.exportReportsList('csv')
}

const clearFilters = () => {
  reportsStore.clearFilters()
  searchQuery.value = ''
}

const getCategoryName = (category) => {
  const names = {
    assets: 'Ativos',
    financial: 'Financeiro',
    maintenance: 'Manutenção',
    loans: 'Empréstimos',
    audit: 'Auditoria',
    warranty: 'Garantias'
  }
  return names[category] || category
}

const getReportTypeName = (typeId) => {
  const type = reportTypes.find(t => t.id === typeId)
  return type ? type.name : typeId
}

const getStatusLabel = (status) => {
  const labels = {
    completed: 'Concluído',
    processing: 'Processando',
    failed: 'Falhou'
  }
  return labels[status] || status
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  // Inicializar datas padrão
  const today = new Date()
  const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
  
  newReport.value.startDate = lastMonth.toISOString().split('T')[0]
  newReport.value.endDate = today.toISOString().split('T')[0]
})
</script>

<style scoped>
.reports {
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

.content-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--info-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin-bottom: var(--spacing-lg);
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