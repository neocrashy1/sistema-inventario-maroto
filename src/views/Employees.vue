<template>
  <div class="employees">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Funcionários</h1>
        <p class="page-subtitle">Gestão completa de colaboradores da empresa</p>
      </div>
      
      <div class="page-actions">
        <button class="btn btn-secondary" @click="exportEmployees">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button class="btn btn-primary" @click="showNewEmployeeModal = true">
          <i class="fas fa-plus"></i>
          Novo Funcionário
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon primary">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Total de Funcionários</div>
          <div class="stat-value">{{ employeesStore.totalEmployees }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="fas fa-user-check"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Funcionários Ativos</div>
          <div class="stat-value">{{ employeesStore.activeEmployees }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="fas fa-user-times"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Funcionários Inativos</div>
          <div class="stat-value">{{ employeesStore.inactiveEmployees }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="fas fa-building"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">Departamentos</div>
          <div class="stat-value">{{ employeesStore.departments.length }}</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters-grid">
        <div class="filter-group">
          <label>Buscar</label>
          <div class="search-input">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="employeesStore.searchTerm"
              placeholder="Nome, email, código ou departamento..."
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label>Departamento</label>
          <select v-model="employeesStore.selectedDepartment">
            <option value="">Todos os departamentos</option>
            <option v-for="dept in employeesStore.departments" :key="dept" :value="dept">
              {{ dept }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="employeesStore.selectedStatus">
            <option value="">Todos os status</option>
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Localização</label>
          <select v-model="employeesStore.selectedLocation">
            <option value="">Todas as localizações</option>
            <option v-for="location in employeesStore.locations" :key="location" :value="location">
              {{ location }}
            </option>
          </select>
        </div>
        
        <div class="filter-actions">
          <button class="btn btn-secondary btn-sm" @click="employeesStore.clearFilters()">
            <i class="fas fa-times"></i>
            Limpar
          </button>
        </div>
      </div>
    </div>

    <!-- Employees Table -->
    <div class="table-container">
      <div class="table-header">
        <h3>Lista de Funcionários ({{ employeesStore.filteredEmployees.length }})</h3>
        <div class="table-actions">
          <button class="btn btn-secondary btn-sm" @click="toggleView">
            <i :class="viewMode === 'table' ? 'fas fa-th' : 'fas fa-list'"></i>
            {{ viewMode === 'table' ? 'Cards' : 'Tabela' }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <LoadingState 
        v-if="isLoading" 
        message="Carregando funcionários..." 
        :overlay="true" 
      />

      <!-- Table View -->
      <div v-if="viewMode === 'table'" class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nome</th>
              <th>Email</th>
              <th>Departamento</th>
              <th>Cargo</th>
              <th>Localização</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in employeesStore.filteredEmployees" :key="employee.id">
              <td>
                <span class="employee-code">{{ employee.code }}</span>
              </td>
              <td>
                <div class="employee-info">
                  <div class="employee-avatar">
                    <img v-if="employee.avatar" :src="employee.avatar" :alt="employee.name">
                    <div v-else class="avatar-placeholder">
                      {{ employee.name.charAt(0).toUpperCase() }}
                    </div>
                  </div>
                  <div class="employee-details">
                    <div class="employee-name">{{ employee.name }}</div>
                    <div class="employee-phone">{{ employee.phone }}</div>
                  </div>
                </div>
              </td>
              <td>{{ employee.email }}</td>
              <td>{{ employee.department }}</td>
              <td>{{ employee.position }}</td>
              <td>{{ employee.location.name }}</td>
              <td>
                <span class="status-badge" :class="employee.status.toLowerCase()">
                  {{ employee.status }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn btn-sm btn-secondary" 
                    @click="viewEmployee(employee)"
                    title="Ver detalhes"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-primary" 
                    @click="editEmployee(employee)"
                    title="Editar"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button 
                    v-if="employee.status === 'Ativo'"
                    class="btn btn-sm btn-warning" 
                    @click="deactivateEmployee(employee)"
                    title="Desativar"
                  >
                    <i class="fas fa-user-times"></i>
                  </button>
                  <button 
                    v-else
                    class="btn btn-sm btn-success" 
                    @click="reactivateEmployee(employee)"
                    title="Reativar"
                  >
                    <i class="fas fa-user-check"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cards View -->
      <div v-else class="cards-grid">
        <div v-for="employee in employeesStore.filteredEmployees" :key="employee.id" class="employee-card">
          <div class="card-header">
            <div class="employee-avatar">
              <img v-if="employee.avatar" :src="employee.avatar" :alt="employee.name">
              <div v-else class="avatar-placeholder">
                {{ employee.name.charAt(0).toUpperCase() }}
              </div>
            </div>
            <div class="employee-basic-info">
              <h4>{{ employee.name }}</h4>
              <p class="employee-code">{{ employee.code }}</p>
              <span class="status-badge" :class="employee.status.toLowerCase()">
                {{ employee.status }}
              </span>
            </div>
          </div>
          
          <div class="card-content">
            <div class="info-row">
              <i class="fas fa-envelope"></i>
              <span>{{ employee.email }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-phone"></i>
              <span>{{ employee.phone }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-building"></i>
              <span>{{ employee.department }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-briefcase"></i>
              <span>{{ employee.position }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ employee.location.name }}</span>
            </div>
          </div>
          
          <div class="card-actions">
            <button class="btn btn-sm btn-secondary" @click="viewEmployee(employee)">
              <i class="fas fa-eye"></i>
              Ver
            </button>
            <button class="btn btn-sm btn-primary" @click="editEmployee(employee)">
              <i class="fas fa-edit"></i>
              Editar
            </button>
            <button 
              v-if="employee.status === 'Ativo'"
              class="btn btn-sm btn-warning" 
              @click="deactivateEmployee(employee)"
            >
              <i class="fas fa-user-times"></i>
              Desativar
            </button>
            <button 
              v-else
              class="btn btn-sm btn-success" 
              @click="reactivateEmployee(employee)"
            >
              <i class="fas fa-user-check"></i>
              Reativar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- New Employee Modal -->
    <div v-if="showNewEmployeeModal" class="modal-overlay" @click="closeNewEmployeeModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>Novo Funcionário</h3>
          <button class="modal-close" @click="closeNewEmployeeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveNewEmployee">
            <div class="form-grid">
              <!-- Dados Pessoais -->
              <div class="form-section">
                <h4>Dados Pessoais</h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>Nome Completo *</label>
                    <input type="text" v-model="newEmployee.name" required>
                  </div>
                  <div class="form-group">
                    <label>Email *</label>
                    <input type="email" v-model="newEmployee.email" required>
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label>Telefone</label>
                    <input type="text" v-model="newEmployee.phone">
                  </div>
                  <div class="form-group">
                    <label>CPF</label>
                    <input type="text" v-model="newEmployee.cpf">
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label>RG</label>
                    <input type="text" v-model="newEmployee.rg">
                  </div>
                  <div class="form-group">
                    <label>Data de Nascimento</label>
                    <input type="date" v-model="newEmployee.birthDate">
                  </div>
                </div>
              </div>

              <!-- Dados Profissionais -->
              <div class="form-section">
                <h4>Dados Profissionais</h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>Departamento *</label>
                    <select v-model="newEmployee.department" required>
                      <option value="">Selecione...</option>
                      <option value="Tecnologia da Informação">Tecnologia da Informação</option>
                      <option value="Marketing">Marketing</option>
                      <option value="Vendas">Vendas</option>
                      <option value="Administração">Administração</option>
                      <option value="Recursos Humanos">Recursos Humanos</option>
                      <option value="Financeiro">Financeiro</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Cargo *</label>
                    <input type="text" v-model="newEmployee.position" required>
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label>Data de Admissão</label>
                    <input type="date" v-model="newEmployee.hireDate">
                  </div>
                  <div class="form-group">
                    <label>Gestor Direto</label>
                    <input type="text" v-model="newEmployee.manager">
                  </div>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label>Salário</label>
                    <input type="number" step="0.01" v-model="newEmployee.salary">
                  </div>
                  <div class="form-group">
                    <label>Horário de Trabalho</label>
                    <input type="text" v-model="newEmployee.workSchedule" placeholder="08:00 - 17:00">
                  </div>
                </div>
              </div>

              <!-- Localização -->
              <div class="form-section">
                <h4>Localização</h4>
                <div class="form-group">
                  <label>Local de Trabalho</label>
                  <select v-model="newEmployee.locationId">
                    <option value="">Selecione...</option>
                    <option value="1">Matriz São Paulo</option>
                    <option value="2">Filial Rio de Janeiro</option>
                    <option value="3">Filial Belo Horizonte</option>
                  </select>
                </div>
              </div>

              <!-- Contato de Emergência -->
              <div class="form-section">
                <h4>Contato de Emergência</h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>Nome</label>
                    <input type="text" v-model="newEmployee.emergencyContact.name">
                  </div>
                  <div class="form-group">
                    <label>Parentesco</label>
                    <input type="text" v-model="newEmployee.emergencyContact.relationship">
                  </div>
                </div>
                <div class="form-group">
                  <label>Telefone</label>
                  <input type="text" v-model="newEmployee.emergencyContact.phone">
                </div>
              </div>

              <!-- Observações -->
              <div class="form-section">
                <h4>Observações</h4>
                <div class="form-group">
                  <label>Notas</label>
                  <textarea v-model="newEmployee.notes" rows="3"></textarea>
                </div>
              </div>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeNewEmployeeModal">
            Cancelar
          </button>
          <button type="submit" class="btn btn-primary" @click="saveNewEmployee">
            <i class="fas fa-save"></i>
            Salvar Funcionário
          </button>
        </div>
      </div>
    </div>

    <!-- Employee Details Modal -->
    <div v-if="showEmployeeDetailsModal" class="modal-overlay" @click="closeEmployeeDetailsModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>Detalhes do Funcionário</h3>
          <button class="modal-close" @click="closeEmployeeDetailsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body" v-if="selectedEmployee">
          <div class="employee-details">
            <div class="employee-header">
              <div class="employee-avatar large">
                <img v-if="selectedEmployee.avatar" :src="selectedEmployee.avatar" :alt="selectedEmployee.name">
                <div v-else class="avatar-placeholder">
                  {{ selectedEmployee.name.charAt(0).toUpperCase() }}
                </div>
              </div>
              <div class="employee-info">
                <h2>{{ selectedEmployee.name }}</h2>
                <p class="employee-code">{{ selectedEmployee.code }}</p>
                <span class="status-badge" :class="selectedEmployee.status.toLowerCase()">
                  {{ selectedEmployee.status }}
                </span>
              </div>
            </div>

            <div class="details-grid">
              <div class="detail-section">
                <h4>Informações Pessoais</h4>
                <div class="detail-item">
                  <label>Email:</label>
                  <span>{{ selectedEmployee.email }}</span>
                </div>
                <div class="detail-item">
                  <label>Telefone:</label>
                  <span>{{ selectedEmployee.phone }}</span>
                </div>
                <div class="detail-item">
                  <label>CPF:</label>
                  <span>{{ selectedEmployee.cpf }}</span>
                </div>
                <div class="detail-item">
                  <label>RG:</label>
                  <span>{{ selectedEmployee.rg }}</span>
                </div>
                <div class="detail-item">
                  <label>Data de Nascimento:</label>
                  <span>{{ formatDate(selectedEmployee.birthDate) }}</span>
                </div>
              </div>

              <div class="detail-section">
                <h4>Informações Profissionais</h4>
                <div class="detail-item">
                  <label>Departamento:</label>
                  <span>{{ selectedEmployee.department }}</span>
                </div>
                <div class="detail-item">
                  <label>Cargo:</label>
                  <span>{{ selectedEmployee.position }}</span>
                </div>
                <div class="detail-item">
                  <label>Data de Admissão:</label>
                  <span>{{ formatDate(selectedEmployee.hireDate) }}</span>
                </div>
                <div class="detail-item">
                  <label>Gestor:</label>
                  <span>{{ selectedEmployee.manager }}</span>
                </div>
                <div class="detail-item">
                  <label>Salário:</label>
                  <span>{{ formatCurrency(selectedEmployee.salary) }}</span>
                </div>
                <div class="detail-item">
                  <label>Horário:</label>
                  <span>{{ selectedEmployee.workSchedule }}</span>
                </div>
              </div>

              <div class="detail-section">
                <h4>Localização</h4>
                <div class="detail-item">
                  <label>Local de Trabalho:</label>
                  <span>{{ selectedEmployee.location.name }}</span>
                </div>
                <div class="detail-item">
                  <label>Endereço:</label>
                  <span>{{ selectedEmployee.location.address }}</span>
                </div>
              </div>

              <div class="detail-section" v-if="selectedEmployee.emergencyContact">
                <h4>Contato de Emergência</h4>
                <div class="detail-item">
                  <label>Nome:</label>
                  <span>{{ selectedEmployee.emergencyContact.name }}</span>
                </div>
                <div class="detail-item">
                  <label>Parentesco:</label>
                  <span>{{ selectedEmployee.emergencyContact.relationship }}</span>
                </div>
                <div class="detail-item">
                  <label>Telefone:</label>
                  <span>{{ selectedEmployee.emergencyContact.phone }}</span>
                </div>
              </div>
            </div>

            <div v-if="selectedEmployee.notes" class="notes-section">
              <h4>Observações</h4>
              <p>{{ selectedEmployee.notes }}</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeEmployeeDetailsModal">
            Fechar
          </button>
          <button type="button" class="btn btn-primary" @click="editEmployee(selectedEmployee)">
            <i class="fas fa-edit"></i>
            Editar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, onMounted } from 'vue'
import { useEmployeesStore } from '@/stores/employees'
import { usePageLoading } from '@/composables/useLoading'
import LoadingState from '@/components/common/LoadingState.vue'

const employeesStore = useEmployeesStore()

// Loading state
const { isLoading, loadPage } = usePageLoading()

// Estado local
const viewMode = ref('table')
const showNewEmployeeModal = ref(false)
const showEmployeeDetailsModal = ref(false)
const selectedEmployee = ref(null)

const newEmployee = ref({
  name: '',
  email: '',
  phone: '',
  cpf: '',
  rg: '',
  birthDate: '',
  hireDate: '',
  department: '',
  position: '',
  manager: '',
  locationId: '',
  salary: 0,
  workSchedule: '',
  contractType: 'CLT',
  status: 'Ativo',
  emergencyContact: {
    name: '',
    relationship: '',
    phone: ''
  },
  notes: ''
})

// Métodos
const toggleView = () => {
  viewMode.value = viewMode.value === 'table' ? 'cards' : 'table'
}

const viewEmployee = (employee) => {
  selectedEmployee.value = employee
  showEmployeeDetailsModal.value = true
}

const editEmployee = (employee) => {
  // TODO: Implementar modal de edição
  logger.debug('Editar funcionário:', employee)
}

const deactivateEmployee = (employee) => {
  if (confirm(`Tem certeza que deseja desativar o funcionário ${employee.name}?`)) {
    employeesStore.deactivateEmployee(employee.id)
  }
}

const reactivateEmployee = (employee) => {
  if (confirm(`Tem certeza que deseja reativar o funcionário ${employee.name}?`)) {
    employeesStore.reactivateEmployee(employee.id)
  }
}

const closeNewEmployeeModal = () => {
  showNewEmployeeModal.value = false
  resetNewEmployee()
}

const closeEmployeeDetailsModal = () => {
  showEmployeeDetailsModal.value = false
  selectedEmployee.value = null
}

const resetNewEmployee = () => {
  newEmployee.value = {
    name: '',
    email: '',
    phone: '',
    cpf: '',
    rg: '',
    birthDate: '',
    hireDate: '',
    department: '',
    position: '',
    manager: '',
    locationId: '',
    salary: 0,
    workSchedule: '',
    contractType: 'CLT',
    status: 'Ativo',
    emergencyContact: {
      name: '',
      relationship: '',
      phone: ''
    },
    notes: ''
  }
}

const saveNewEmployee = () => {
  // Mapear locationId para objeto location
  const locations = {
    '1': { id: 1, name: 'Matriz São Paulo', address: 'Av. Paulista, 1000 - São Paulo/SP' },
    '2': { id: 2, name: 'Filial Rio de Janeiro', address: 'Av. Copacabana, 500 - Rio de Janeiro/RJ' },
    '3': { id: 3, name: 'Filial Belo Horizonte', address: 'Av. Afonso Pena, 300 - Belo Horizonte/MG' }
  }

  const employeeData = {
    ...newEmployee.value,
    location: locations[newEmployee.value.locationId] || locations['1']
  }

  delete employeeData.locationId

  employeesStore.addEmployee(employeeData)
  closeNewEmployeeModal()
}

const exportEmployees = () => {
  // TODO: Implementar exportação
  logger.debug('Exportar funcionários')
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const formatCurrency = (value) => {
  if (!value) return '-'
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

onMounted(() => {
  loadPage(() => employeesStore.fetchEmployees())
})
</script>

<style scoped>
.employees {
  padding: 24px;
  background-color: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-header-content h1 {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 28px;
  font-weight: 600;
}

.page-subtitle {
  margin: 0;
  color: #64748b;
  font-size: 16px;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  color: white;
}

.stat-icon.primary { background: #3b82f6; }
.stat-icon.success { background: #10b981; }
.stat-icon.warning { background: #f59e0b; }
.stat-icon.info { background: #06b6d4; }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.filters-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.filters-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr auto;
  gap: 16px;
  align-items: end;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.search-input {
  position: relative;
}

.search-input i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-input input {
  padding-left: 40px;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.table-header h3 {
  margin: 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
}

.table-responsive {
  overflow-x: auto;
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
  border-bottom: 1px solid #f1f5f9;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.employee-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.employee-avatar.large {
  width: 80px;
  height: 80px;
}

.employee-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-weight: 600;
  color: #6b7280;
  font-size: 16px;
}

.employee-details {
  flex: 1;
}

.employee-name {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 2px;
}

.employee-phone {
  font-size: 14px;
  color: #64748b;
}

.employee-code {
  font-family: 'Courier New', monospace;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #475569;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.ativo {
  background: #dcfce7;
  color: #166534;
}

.status-badge.inativo {
  background: #fef2f2;
  color: #dc2626;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 24px;
}

.employee-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

.employee-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 16px;
}

.employee-basic-info h4 {
  margin: 0 0 4px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.card-content {
  padding: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #64748b;
}

.info-row i {
  width: 16px;
  color: #9ca3af;
}

.card-actions {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  gap: 8px;
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
  max-width: 500px;
  width: 90%;
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
  color: #1e293b;
  font-size: 20px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
}

.form-grid {
  display: grid;
  gap: 24px;
}

.form-section {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.employee-details {
  max-width: 100%;
}

.employee-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.employee-header .employee-info h2 {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 24px;
  font-weight: 600;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.detail-section {
  background: #f8fafc;
  padding: 20px;
  border-radius: 8px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
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
  font-weight: 500;
  color: #6b7280;
  margin-right: 16px;
}

.detail-item span {
  color: #1e293b;
  text-align: right;
}

.notes-section {
  background: #f8fafc;
  padding: 20px;
  border-radius: 8px;
}

.notes-section h4 {
  margin: 0 0 12px 0;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
}

.notes-section p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background: #d97706;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .details-grid {
    grid-template-columns: 1fr;
  }
  
  .employee-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>