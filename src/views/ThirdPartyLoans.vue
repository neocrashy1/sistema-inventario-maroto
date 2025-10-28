<template>
  <div class="third-party-loans">
    <!-- Cabeçalho -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">Empréstimos para Terceiros</h1>
          <p class="page-subtitle">Gerencie empréstimos de ativos para empresas e pessoas externas</p>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-outline"
            @click="exportLoans"
            :disabled="loading"
          >
            <i class="fas fa-download"></i>
            Exportar
          </button>
          <button 
            class="btn btn-primary"
            @click="showNewLoanModal = true"
          >
            <i class="fas fa-plus"></i>
            Novo Empréstimo
          </button>
        </div>
      </div>
    </div>

    <!-- Cards de Estatísticas -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-handshake"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ totalLoans }}</div>
          <div class="stat-label">Total de Empréstimos</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ activeLoans.length }}</div>
          <div class="stat-label">Ativos</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon overdue">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ overdueLoans.length }}</div>
          <div class="stat-label">Em Atraso</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon returned">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ returnedLoans.length }}</div>
          <div class="stat-label">Devolvidos</div>
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
            placeholder="Empresa, contato, ativo, código..."
            class="form-input"
          >
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="statusFilter" class="form-select">
            <option value="">Todos os Status</option>
            <option value="Ativo">Ativo</option>
            <option value="Em Atraso">Em Atraso</option>
            <option value="Devolvido">Devolvido</option>
            <option value="Cancelado">Cancelado</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Tipo de Terceiro</label>
          <select v-model="typeFilter" class="form-select">
            <option value="">Todos os Tipos</option>
            <option value="Empresa">Empresa</option>
            <option value="Pessoa Física">Pessoa Física</option>
            <option value="Prestador de Serviço">Prestador de Serviço</option>
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
      <span>{{ filteredLoans.length }} empréstimo(s) encontrado(s)</span>
    </div>

    <!-- Tabela de Empréstimos -->
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
            <th>Terceiro</th>
            <th>Contato</th>
            <th>Ativo</th>
            <th>Data Empréstimo</th>
            <th>Data Prevista</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in paginatedLoans" :key="loan.id">
            <td>
              <input 
                type="checkbox" 
                v-model="selectedLoans"
                :value="loan.id"
              >
            </td>
            <td>
              <span class="code">{{ loan.code }}</span>
            </td>
            <td>
              <div class="third-party-info">
                <div class="name">{{ loan.thirdParty.name }}</div>
                <div class="type">{{ loan.thirdParty.type }}</div>
              </div>
            </td>
            <td>
              <div class="contact-info">
                <div class="contact-name">{{ loan.thirdParty.contactName }}</div>
                <div class="contact-email">{{ loan.thirdParty.contactEmail }}</div>
              </div>
            </td>
            <td>
              <div class="asset-info">
                <div class="asset-name">{{ loan.asset.name }}</div>
                <div class="asset-code">{{ loan.asset.code }}</div>
              </div>
            </td>
            <td>{{ formatDate(loan.loanDate) }}</td>
            <td>{{ formatDate(loan.expectedReturnDate) }}</td>
            <td>
              <span 
                class="status-badge"
                :class="getStatusClass(loan.status)"
              >
                {{ loan.status }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  v-if="loan.status === 'Ativo' || loan.status === 'Em Atraso'"
                  class="btn btn-sm btn-success"
                  @click="openReturnModal(loan)"
                  title="Registrar Devolução"
                >
                  <i class="fas fa-undo"></i>
                </button>
                <button 
                  class="btn btn-sm btn-outline"
                  @click="editLoan(loan)"
                  title="Editar"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  class="btn btn-sm btn-info"
                  @click="viewLoanDetails(loan)"
                  title="Ver Detalhes"
                >
                  <i class="fas fa-eye"></i>
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
        Mostrando {{ startIndex + 1 }} a {{ endIndex }} de {{ filteredLoans.length }} registros
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

    <!-- Modal Novo Empréstimo -->
    <div v-if="showNewLoanModal" class="modal-overlay" @click="closeNewLoanModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Novo Empréstimo para Terceiro</h3>
          <button class="modal-close" @click="closeNewLoanModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="createLoan">
            <div class="form-grid">
              <div class="form-group">
                <label>Tipo de Terceiro *</label>
                <select v-model="newLoan.thirdPartyType" class="form-select" required>
                  <option value="">Selecione o tipo</option>
                  <option value="Empresa">Empresa</option>
                  <option value="Pessoa Física">Pessoa Física</option>
                  <option value="Prestador de Serviço">Prestador de Serviço</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Nome/Razão Social *</label>
                <input 
                  type="text" 
                  v-model="newLoan.thirdPartyName"
                  class="form-input"
                  required
                  placeholder="Nome da empresa ou pessoa"
                >
              </div>
              
              <div class="form-group">
                <label>CNPJ/CPF</label>
                <input 
                  type="text" 
                  v-model="newLoan.thirdPartyDocument"
                  class="form-input"
                  placeholder="Documento de identificação"
                >
              </div>
              
              <div class="form-group">
                <label>Nome do Contato *</label>
                <input 
                  type="text" 
                  v-model="newLoan.contactName"
                  class="form-input"
                  required
                  placeholder="Pessoa responsável"
                >
              </div>
              
              <div class="form-group">
                <label>Email do Contato *</label>
                <input 
                  type="email" 
                  v-model="newLoan.contactEmail"
                  class="form-input"
                  required
                  placeholder="email@exemplo.com"
                >
              </div>
              
              <div class="form-group">
                <label>Telefone</label>
                <input 
                  type="tel" 
                  v-model="newLoan.contactPhone"
                  class="form-input"
                  placeholder="(11) 99999-9999"
                >
              </div>
              
              <div class="form-group">
                <label>Ativo *</label>
                <select v-model="newLoan.assetId" class="form-select" required>
                  <option value="">Selecione o ativo</option>
                  <option 
                    v-for="asset in availableAssetsForLoan" 
                    :key="asset.id"
                    :value="asset.id"
                  >
                    {{ asset.name }} ({{ asset.code }})
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Data do Empréstimo *</label>
                <input 
                  type="date" 
                  v-model="newLoan.loanDate"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group">
                <label>Data Prevista de Devolução *</label>
                <input 
                  type="date" 
                  v-model="newLoan.expectedReturnDate"
                  class="form-input"
                  required
                >
              </div>
              
              <div class="form-group full-width">
                <label>Finalidade do Empréstimo</label>
                <textarea 
                  v-model="newLoan.purpose"
                  class="form-textarea"
                  rows="3"
                  placeholder="Descreva a finalidade do empréstimo..."
                ></textarea>
              </div>
              
              <div class="form-group full-width">
                <label>Observações</label>
                <textarea 
                  v-model="newLoan.notes"
                  class="form-textarea"
                  rows="3"
                  placeholder="Observações adicionais..."
                ></textarea>
              </div>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="closeNewLoanModal">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Criando...' : 'Criar Empréstimo' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal Devolução -->
    <div v-if="showReturnModal" class="modal-overlay" @click="closeReturnModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Registrar Devolução</h3>
          <button class="modal-close" @click="closeReturnModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="loan-summary">
            <h4>{{ selectedLoan?.thirdParty.name }}</h4>
            <p>{{ selectedLoan?.asset.name }} ({{ selectedLoan?.asset.code }})</p>
            <p>Emprestado em: {{ formatDate(selectedLoan?.loanDate) }}</p>
          </div>
          
          <form @submit.prevent="processReturn">
            <div class="form-group">
              <label>Data de Devolução *</label>
              <input 
                type="date" 
                v-model="returnData.returnDate"
                class="form-input"
                required
              >
            </div>
            
            <div class="form-group">
              <label>Condição do Ativo *</label>
              <select v-model="returnData.condition" class="form-select" required>
                <option value="">Selecione a condição</option>
                <option value="Perfeito">Perfeito</option>
                <option value="Bom">Bom</option>
                <option value="Regular">Regular</option>
                <option value="Danificado">Danificado</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Observações da Devolução</label>
              <textarea 
                v-model="returnData.returnNotes"
                class="form-textarea"
                rows="4"
                placeholder="Descreva o estado do ativo e outras observações..."
              ></textarea>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="closeReturnModal">
                Cancelar
              </button>
              <button type="submit" class="btn btn-success" :disabled="loading">
                {{ loading ? 'Processando...' : 'Registrar Devolução' }}
              </button>
            </div>
          </form>
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
import logger from '@/utils/logger'
import { ref, computed, onMounted, watch } from 'vue'
import { useThirdPartyLoansStore } from '@/stores/thirdPartyLoans'

export default {
  name: 'ThirdPartyLoans',
  setup() {
    const store = useThirdPartyLoansStore()
    
    // Estado local
    const searchQuery = ref('')
    const statusFilter = ref('')
    const typeFilter = ref('')
    const dateRangeStart = ref('')
    const dateRangeEnd = ref('')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const selectedLoans = ref([])
    const selectAll = ref(false)
    
    // Modais
    const showNewLoanModal = ref(false)
    const showReturnModal = ref(false)
    const selectedLoan = ref(null)
    
    // Formulários
    const newLoan = ref({
      thirdPartyType: '',
      thirdPartyName: '',
      thirdPartyDocument: '',
      contactName: '',
      contactEmail: '',
      contactPhone: '',
      assetId: '',
      loanDate: new Date().toISOString().split('T')[0],
      expectedReturnDate: '',
      purpose: '',
      notes: ''
    })
    
    const returnData = ref({
      returnDate: new Date().toISOString().split('T')[0],
      condition: '',
      returnNotes: ''
    })
    
    // Mensagens
    const successMessage = ref('')
    const errorMessage = ref('')
    
    // Computed
    const { 
      loans, 
      loading, 
      error,
      totalLoans,
      activeLoans,
      overdueLoans,
      returnedLoans,
      availableAssetsForLoan
    } = store
    
    const filteredLoans = computed(() => {
      let filtered = loans
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(loan =>
          loan.code.toLowerCase().includes(query) ||
          loan.thirdParty.name.toLowerCase().includes(query) ||
          loan.thirdParty.contactName.toLowerCase().includes(query) ||
          loan.thirdParty.contactEmail.toLowerCase().includes(query) ||
          loan.asset.name.toLowerCase().includes(query) ||
          loan.asset.code.toLowerCase().includes(query)
        )
      }
      
      if (statusFilter.value) {
        filtered = filtered.filter(loan => loan.status === statusFilter.value)
      }
      
      if (typeFilter.value) {
        filtered = filtered.filter(loan => loan.thirdParty.type === typeFilter.value)
      }
      
      if (dateRangeStart.value || dateRangeEnd.value) {
        filtered = filtered.filter(loan => {
          const loanDate = new Date(loan.loanDate)
          const start = dateRangeStart.value ? new Date(dateRangeStart.value) : new Date('1900-01-01')
          const end = dateRangeEnd.value ? new Date(dateRangeEnd.value) : new Date('2100-12-31')
          return loanDate >= start && loanDate <= end
        })
      }
      
      return filtered
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredLoans.value.length / itemsPerPage.value)
    })
    
    const startIndex = computed(() => {
      return (currentPage.value - 1) * itemsPerPage.value
    })
    
    const endIndex = computed(() => {
      return Math.min(startIndex.value + itemsPerPage.value, filteredLoans.value.length)
    })
    
    const paginatedLoans = computed(() => {
      return filteredLoans.value.slice(startIndex.value, endIndex.value)
    })
    
    // Métodos
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('pt-BR')
    }
    
    const getStatusClass = (status) => {
      const classes = {
        'Ativo': 'status-active',
        'Em Atraso': 'status-overdue',
        'Devolvido': 'status-returned',
        'Cancelado': 'status-cancelled'
      }
      return classes[status] || ''
    }
    
    const clearFilters = () => {
      searchQuery.value = ''
      statusFilter.value = ''
      typeFilter.value = ''
      dateRangeStart.value = ''
      dateRangeEnd.value = ''
      currentPage.value = 1
    }
    
    const toggleSelectAll = () => {
      if (selectAll.value) {
        selectedLoans.value = paginatedLoans.value.map(loan => loan.id)
      } else {
        selectedLoans.value = []
      }
    }
    
    const closeNewLoanModal = () => {
      showNewLoanModal.value = false
      resetNewLoanForm()
    }
    
    const resetNewLoanForm = () => {
      newLoan.value = {
        thirdPartyType: '',
        thirdPartyName: '',
        thirdPartyDocument: '',
        contactName: '',
        contactEmail: '',
        contactPhone: '',
        assetId: '',
        loanDate: new Date().toISOString().split('T')[0],
        expectedReturnDate: '',
        purpose: '',
        notes: ''
      }
    }
    
    const createLoan = async () => {
      try {
        await store.createLoan(newLoan.value)
        successMessage.value = 'Empréstimo criado com sucesso!'
        closeNewLoanModal()
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
    
    const openReturnModal = (loan) => {
      selectedLoan.value = loan
      returnData.value = {
        returnDate: new Date().toISOString().split('T')[0],
        condition: '',
        returnNotes: ''
      }
      showReturnModal.value = true
    }
    
    const closeReturnModal = () => {
      showReturnModal.value = false
      selectedLoan.value = null
      returnData.value = {
        returnDate: new Date().toISOString().split('T')[0],
        condition: '',
        returnNotes: ''
      }
    }
    
    const processReturn = async () => {
      try {
        await store.returnLoan(selectedLoan.value.id, returnData.value)
        successMessage.value = 'Devolução registrada com sucesso!'
        closeReturnModal()
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
    
    const editLoan = (loan) => {
      // Implementar edição
      logger.debug('Editar empréstimo:', loan)
    }
    
    const viewLoanDetails = (loan) => {
      // Implementar visualização de detalhes
      logger.debug('Ver detalhes do empréstimo:', loan)
    }
    
    const exportLoans = async () => {
      try {
        await store.exportLoans('csv', {
          status: statusFilter.value,
          type: typeFilter.value,
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
    watch([searchQuery, statusFilter, typeFilter, dateRangeStart, dateRangeEnd], () => {
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
      store.fetchLoans()
    })
    
    return {
      // Estado
      searchQuery,
      statusFilter,
      typeFilter,
      dateRangeStart,
      dateRangeEnd,
      currentPage,
      selectedLoans,
      selectAll,
      showNewLoanModal,
      showReturnModal,
      selectedLoan,
      newLoan,
      returnData,
      successMessage,
      errorMessage,
      
      // Store
      loading,
      totalLoans,
      activeLoans,
      overdueLoans,
      returnedLoans,
      availableAssetsForLoan,
      
      // Computed
      filteredLoans,
      totalPages,
      startIndex,
      endIndex,
      paginatedLoans,
      
      // Métodos
      formatDate,
      getStatusClass,
      clearFilters,
      toggleSelectAll,
      closeNewLoanModal,
      createLoan,
      openReturnModal,
      closeReturnModal,
      processReturn,
      editLoan,
      viewLoanDetails,
      exportLoans
    }
  }
}
</script>

<style scoped>
.third-party-loans {
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
  background: #f0fdf4;
  color: #22c55e;
}

.stat-icon.overdue {
  background: #fef2f2;
  color: #ef4444;
}

.stat-icon.returned {
  background: #f0f9ff;
  color: #3b82f6;
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

.third-party-info .name {
  font-weight: 500;
  color: #1a1a1a;
}

.third-party-info .type {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.contact-info .contact-name {
  font-weight: 500;
  color: #1a1a1a;
}

.contact-info .contact-email {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.asset-info .asset-name {
  font-weight: 500;
  color: #1a1a1a;
}

.asset-info .asset-code {
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

.status-active {
  background: #dcfce7;
  color: #166534;
}

.status-overdue {
  background: #fee2e2;
  color: #991b1b;
}

.status-returned {
  background: #dbeafe;
  color: #1e40af;
}

.status-cancelled {
  background: #f3f4f6;
  color: #6b7280;
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

.loan-summary {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.loan-summary h4 {
  margin: 0 0 8px 0;
  color: #1a1a1a;
}

.loan-summary p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
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

.btn-info {
  background: #0ea5e9;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #0284c7;
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
  .third-party-loans {
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
}
</style>