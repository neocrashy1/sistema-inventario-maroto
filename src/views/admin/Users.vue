<template>
  <div class="users-admin">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Usuários</h1>
        <p class="page-subtitle">Gerenciamento de usuários e permissões do sistema</p>
      </div>
      
      <div class="page-actions">
        <button class="btn btn-secondary" @click="exportUsers">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button class="btn btn-primary" @click="openUserModal">
          <i class="fas fa-plus"></i>
          Novo Usuário
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ usersStore.users.length }}</h3>
          <p>Total de Usuários</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon active">
          <i class="fas fa-user-check"></i>
        </div>
        <div class="stat-content">
          <h3>{{ usersStore.activeUsers.length }}</h3>
          <p>Usuários Ativos</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon inactive">
          <i class="fas fa-user-times"></i>
        </div>
        <div class="stat-content">
          <h3>{{ usersStore.inactiveUsers.length }}</h3>
          <p>Usuários Inativos</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-shield"></i>
        </div>
        <div class="stat-content">
          <h3>{{ usersStore.roles.length }}</h3>
          <p>Perfis de Acesso</p>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filters-grid">
        <div class="filter-group">
          <label>Buscar usuário</label>
          <div class="search-input">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Nome, email ou departamento..."
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label>Perfil</label>
          <select v-model="selectedRole">
            <option value="">Todos os perfis</option>
            <option v-for="role in usersStore.roles" :key="role.id" :value="role.id">
              {{ role.name }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Departamento</label>
          <select v-model="selectedDepartment">
            <option value="">Todos os departamentos</option>
            <option v-for="dept in usersStore.departments" :key="dept" :value="dept">
              {{ dept }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="selectedStatus">
            <option value="">Todos</option>
            <option value="active">Ativo</option>
            <option value="inactive">Inativo</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="users-table-container">
      <!-- Loading State -->
      <LoadingState 
        v-if="isLoading" 
        message="Carregando usuários..." 
        :overlay="true" 
      />
      
      <table class="users-table">
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Email</th>
            <th>Perfil</th>
            <th>Departamento</th>
            <th>Status</th>
            <th>Último Login</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
            <td>
              <div class="user-info">
                <div class="user-avatar">
                  <img v-if="user.avatar" :src="user.avatar" :alt="user.name">
                  <i v-else class="fas fa-user"></i>
                </div>
                <div class="user-details">
                  <span class="user-name">{{ user.name }}</span>
                  <span class="user-username">@{{ user.username }}</span>
                </div>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span class="role-badge" :style="{ backgroundColor: getRoleColor(user.role) }">
                {{ getRoleName(user.role) }}
              </span>
            </td>
            <td>{{ user.department }}</td>
            <td>
              <span class="status-badge" :class="user.status">
                {{ user.status === 'active' ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td>
              <span v-if="user.lastLogin" class="last-login">
                {{ formatDateTime(user.lastLogin) }}
              </span>
              <span v-else class="no-login">Nunca logou</span>
            </td>
            <td>
              <div class="action-buttons">
                <button 
                  class="btn-icon" 
                  @click="editUser(user)"
                  title="Editar usuário"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  class="btn-icon" 
                  @click="toggleUserStatus(user.id)"
                  :title="user.status === 'active' ? 'Desativar usuário' : 'Ativar usuário'"
                >
                  <i :class="user.status === 'active' ? 'fas fa-user-slash' : 'fas fa-user-check'"></i>
                </button>
                <button 
                  class="btn-icon warning" 
                  @click="confirmResetPassword(user)"
                  title="Resetar senha do usuário"
                >
                  <i class="fas fa-key"></i>
                </button>
                <button 
                  class="btn-icon danger" 
                  @click="confirmDeleteUser(user)"
                  title="Excluir usuário"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- User Modal -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ editingUser ? 'Editar Usuário' : 'Novo Usuário' }}</h2>
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveUser" class="user-form">
            <div class="form-grid">
              <FormField
                label="Nome Completo"
                type="text"
                v-model="userForm.name"
                :error="getFieldError('name')"
                :is-valid="!hasFieldError('name') && touched.name"
                :class="getFieldClass('name')"
                @blur="handleFieldBlur('name')"
                @input="handleFieldInput('name')"
                required
                placeholder="Digite o nome completo"
              />
              
              <FormField
                label="Email"
                type="email"
                v-model="userForm.email"
                :error="getFieldError('email')"
                :is-valid="!hasFieldError('email') && touched.email"
                :class="getFieldClass('email')"
                @blur="handleFieldBlur('email')"
                @input="handleFieldInput('email')"
                required
                placeholder="usuario@empresa.com"
              />
              
              <FormField
                label="Nome de Usuário"
                type="text"
                v-model="userForm.username"
                :error="getFieldError('username')"
                :is-valid="!hasFieldError('username') && touched.username"
                :class="getFieldClass('username')"
                @blur="handleFieldBlur('username')"
                @input="handleFieldInput('username')"
                required
                placeholder="usuario.nome"
              />
              
              <FormField
                label="Telefone"
                type="tel"
                v-model="userForm.phone"
                :error="getFieldError('phone')"
                :is-valid="!hasFieldError('phone') && touched.phone"
                :class="getFieldClass('phone')"
                @blur="handleFieldBlur('phone')"
                @input="handleFieldInput('phone')"
                placeholder="(11) 99999-9999"
              />
              
              <FormField
                label="Perfil"
                type="select"
                v-model="userForm.role"
                :error="getFieldError('role')"
                :is-valid="!hasFieldError('role') && touched.role"
                :class="getFieldClass('role')"
                @blur="handleFieldBlur('role')"
                @change="handleFieldInput('role')"
                required
                placeholder="Selecione um perfil"
                :options="usersStore.roles.map(role => ({ value: role.id, label: role.name }))"
              />
              
              <FormField
                label="Departamento"
                type="select"
                v-model="userForm.department"
                :error="getFieldError('department')"
                :is-valid="!hasFieldError('department') && touched.department"
                :class="getFieldClass('department')"
                @blur="handleFieldBlur('department')"
                @change="handleFieldInput('department')"
                required
                placeholder="Selecione um departamento"
                :options="usersStore.departments.map(dept => ({ value: dept, label: dept }))"
              />
              
              <FormField
                label="Status"
                type="select"
                v-model="userForm.status"
                :error="getFieldError('status')"
                :is-valid="!hasFieldError('status') && touched.status"
                :class="getFieldClass('status')"
                @blur="handleFieldBlur('status')"
                @change="handleFieldInput('status')"
                placeholder="Selecione o status"
                :options="[
                  { value: 'active', label: 'Ativo' },
                  { value: 'inactive', label: 'Inativo' }
                ]"
              />
            </div>

            <!-- Permissions Section -->
            <div class="permissions-section">
              <h3>Permissões Personalizadas</h3>
              <p class="permissions-note">
                As permissões abaixo são adicionais ao perfil selecionado
              </p>
              
              <div class="permissions-grid">
                <div v-for="category in permissionCategories" :key="category" class="permission-category">
                  <h4>{{ category }}</h4>
                  <div class="permission-items">
                    <label 
                      v-for="permission in getPermissionsByCategory(category)" 
                      :key="permission.id"
                      class="permission-item"
                    >
                      <input 
                        type="checkbox" 
                        :value="permission.id"
                        v-model="userForm.permissions"
                      >
                      <span>{{ permission.name }}</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="modal-actions">
              <button type="button" class="btn btn-outline" @click="closeModal">
                Cancelar
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="!canSubmit"
                :class="{ 'btn-disabled': !canSubmit }"
              >
                {{ editingUser ? 'Atualizar' : 'Criar' }} Usuário
              </button>
            </div>
            
            <!-- Resumo de validação -->
            <div v-if="Object.keys(errors).length > 0" class="validation-summary">
              <h4>Corrija os seguintes erros:</h4>
              <ul>
                <li v-for="(error, field) in errors" :key="field">
                  {{ error }}
                </li>
              </ul>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal small" @click.stop>
        <div class="modal-header">
          <h2>Confirmar Exclusão</h2>
          <button class="modal-close" @click="showDeleteModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p>Tem certeza que deseja excluir o usuário <strong>{{ userToDelete?.name }}</strong>?</p>
          <p class="warning-text">Esta ação não pode ser desfeita.</p>
          
          <div class="modal-actions">
            <button class="btn btn-outline" @click="showDeleteModal = false">
              Cancelar
            </button>
            <button class="btn btn-danger" @click="deleteUser">
              Excluir Usuário
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reset Password Confirmation Modal -->
    <div v-if="showResetPasswordModal" class="modal-overlay" @click="showResetPasswordModal = false">
      <div class="modal small" @click.stop>
        <div class="modal-header">
          <h2>Resetar Senha</h2>
          <button class="modal-close" @click="showResetPasswordModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p>Tem certeza que deseja resetar a senha do usuário <strong>{{ userToResetPassword?.name }}</strong>?</p>
          <p class="info-text">Uma nova senha temporária será gerada e exibida para você.</p>
          
          <div v-if="newTemporaryPassword" class="password-result">
            <h4>Nova Senha Temporária:</h4>
            <div class="password-display">
              <code>{{ newTemporaryPassword }}</code>
              <button class="btn-icon" @click="copyPassword" title="Copiar senha">
                <i class="fas fa-copy"></i>
              </button>
            </div>
            <p class="warning-text">⚠️ Anote esta senha! Ela não será exibida novamente.</p>
          </div>
          
          <div class="modal-actions">
            <button class="btn btn-outline" @click="closeResetPasswordModal">
              {{ newTemporaryPassword ? 'Fechar' : 'Cancelar' }}
            </button>
            <button 
              v-if="!newTemporaryPassword" 
              class="btn btn-warning" 
              @click="resetUserPassword"
            >
              Resetar Senha
            </button>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUsersStore } from '@/stores/users'
import { usePageLoading } from '@/composables/useLoading'
import { useFormValidation } from '@/composables/useFormValidation'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useToast } from '@/composables/useToast'
import { getUserValidationRules } from '@/utils/userValidations'
import LoadingState from '@/components/common/LoadingState.vue'
import FormField from '@/components/FormField.vue'

const usersStore = useUsersStore()
const { handleError } = useErrorHandler()
const { showSuccess, showError, showWarning } = useToast()

// Loading state
const { isLoading, loadPage } = usePageLoading()

// Estado reativo
const searchTerm = ref('')
const selectedRole = ref('')
const selectedDepartment = ref('')
const selectedStatus = ref('')
const showUserModal = ref(false)
const showDeleteModal = ref(false)
const showResetPasswordModal = ref(false)
const editingUser = ref(null)
const userToDelete = ref(null)
const userToResetPassword = ref(null)
const newTemporaryPassword = ref('')

// Formulário do usuário
const userForm = ref({
  name: '',
  email: '',
  username: '',
  phone: '',
  role: '',
  department: '',
  status: 'active',
  permissions: []
})

// Sistema de validação
const validationRules = getUserValidationRules({
  requirePassword: false,
  optionalFields: ['phone']
})

const {
  errors,
  touched,
  isValid,
  canSubmit,
  validateSingleField,
  validateAllFields,
  touchField,
  clearAllErrors,
  resetForm: resetValidation,
  getFieldClass,
  getFieldError,
  hasFieldError,
  handleFieldBlur,
  handleFieldInput,
  setupRealtimeValidation
} = useFormValidation(userForm, validationRules)

// Computed
const filteredUsers = computed(() => {
  let filtered = usersStore.users

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.name.toLowerCase().includes(term) ||
      user.email.toLowerCase().includes(term) ||
      user.department.toLowerCase().includes(term) ||
      user.username.toLowerCase().includes(term)
    )
  }

  if (selectedRole.value) {
    filtered = filtered.filter(user => user.role === selectedRole.value)
  }

  if (selectedDepartment.value) {
    filtered = filtered.filter(user => user.department === selectedDepartment.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(user => user.status === selectedStatus.value)
  }

  return filtered
})

const permissionCategories = computed(() => {
  const categories = new Set()
  usersStore.permissions.forEach(permission => {
    categories.add(permission.category)
  })
  return Array.from(categories)
})

// Métodos
function getRoleName(roleId) {
  const role = usersStore.getRoleById(roleId)
  return role ? role.name : roleId
}

function getRoleColor(roleId) {
  const role = usersStore.getRoleById(roleId)
  return role ? role.color : '#6b7280'
}

function getPermissionsByCategory(category) {
  return usersStore.permissions.filter(permission => permission.category === category)
}

function formatDateTime(date) {
  if (!date) return ''
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

function openUserModal() {
  showUserModal.value = true
  // Configurar validação em tempo real quando o modal abrir
  setupRealtimeValidation()
}

function editUser(user) {
  editingUser.value = user
  userForm.value = {
    name: user.name,
    email: user.email,
    username: user.username,
    phone: user.phone || '',
    role: user.role,
    department: user.department,
    status: user.status,
    permissions: [...user.permissions]
  }
  openUserModal()
}

function closeModal() {
  showUserModal.value = false
  editingUser.value = null
  resetForm()
}

function resetForm() {
  userForm.value = {
    name: '',
    email: '',
    username: '',
    phone: '',
    role: '',
    department: '',
    status: 'active',
    permissions: []
  }
  // Limpar validações
  clearAllErrors()
  resetValidation()
}

async function saveUser() {
  try {
    // Validar todos os campos antes de salvar
    const isFormValid = await validateAllFields()
    
    if (!isFormValid) {
      showWarning('Por favor, corrija os erros no formulário antes de continuar')
      return
    }
    
    if (editingUser.value) {
      await usersStore.updateUser(editingUser.value.id, userForm.value)
    } else {
      await usersStore.addUser(userForm.value)
    }
    closeModal()
  } catch (error) {
    handleError(error, 'Erro ao salvar usuário')
  }
}

function toggleUserStatus(userId) {
  try {
    usersStore.toggleUserStatus(userId)
  } catch (error) {
    handleError(error, 'Erro ao alterar status do usuário')
  }
}

function confirmDeleteUser(user) {
  userToDelete.value = user
  showDeleteModal.value = true
}

function deleteUser() {
  try {
    usersStore.deleteUser(userToDelete.value.id)
    showDeleteModal.value = false
    userToDelete.value = null
  } catch (error) {
    handleError(error, 'Erro ao excluir usuário')
  }
}

function confirmResetPassword(user) {
  userToResetPassword.value = user
  newTemporaryPassword.value = ''
  showResetPasswordModal.value = true
}

function resetUserPassword() {
  try {
    const tempPassword = generateTemporaryPassword()
    usersStore.resetUserPassword(userToResetPassword.value.id, tempPassword)
    newTemporaryPassword.value = tempPassword
    showSuccess(`Senha do usuário ${userToResetPassword.value.name} foi resetada com sucesso!`)
  } catch (error) {
    handleError(error, 'Erro ao resetar senha do usuário')
  }
}

function generateTemporaryPassword() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%'
  let password = ''
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return password
}

function closeResetPasswordModal() {
  showResetPasswordModal.value = false
  userToResetPassword.value = null
  newTemporaryPassword.value = ''
}

function copyPassword() {
  navigator.clipboard.writeText(newTemporaryPassword.value).then(() => {
    showSuccess('Senha copiada para a área de transferência!')
  }).catch((error) => {
    handleError(error, 'Erro ao copiar senha')
  })
}

function exportUsers() {
  try {
    const data = filteredUsers.value.map(user => ({
      Nome: user.name,
      Email: user.email,
      'Nome de Usuário': user.username,
      Perfil: getRoleName(user.role),
      Departamento: user.department,
      Status: user.status === 'active' ? 'Ativo' : 'Inativo',
      'Criado em': formatDateTime(user.createdAt),
      'Último Login': user.lastLogin ? formatDateTime(user.lastLogin) : 'Nunca logou'
    }))
    
    const csv = convertToCSV(data)
    downloadCSV(csv, 'usuarios.csv')
    showSuccessMessage('Relatório exportado com sucesso!')
  } catch (error) {
    showErrorMessage('Erro ao exportar dados')
  }
}

function convertToCSV(data) {
  if (!data.length) return ''
  
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
  ].join('\n')
  
  return csvContent
}

function downloadCSV(csv, filename) {
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



// Lifecycle
onMounted(() => {
  loadPage(() => usersStore.fetchUsers())
})
</script>

<style scoped>
.users-admin {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 24px;
}

.stat-icon.active {
  background: #dcfce7;
  color: #16a34a;
}

.stat-icon.inactive {
  background: #fef2f2;
  color: #dc2626;
}

.stat-content h3 {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px 0;
}

.stat-content p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* Filters Section */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.filters-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 20px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
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
  font-size: 14px;
}

.search-input input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-group select {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.filter-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Users Table */
.users-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f9fafb;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  border-bottom: 1px solid #e5e7eb;
}

.users-table td {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
  font-size: 14px;
  color: #374151;
}

.user-row:hover {
  background: #f9fafb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar i {
  color: #9ca3af;
  font-size: 16px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 500;
  color: #111827;
}

.user-username {
  font-size: 12px;
  color: #6b7280;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.inactive {
  background: #fef2f2;
  color: #dc2626;
}

.last-login {
  color: #374151;
}

.no-login {
  color: #9ca3af;
  font-style: italic;
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
  background: #f3f4f6;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #e5e7eb;
  color: #374151;
}

.btn-icon.danger:hover {
  background: #fef2f2;
  color: #dc2626;
}

/* Modal Styles */
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
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal.small {
  max-width: 400px;
}

.modal-header {
  padding: 24px 24px 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #e5e7eb;
  color: #374151;
}

.modal-body {
  padding: 0 24px 24px 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input,
.form-select {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Permissions Section */
.permissions-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #f9fafb;
  border-radius: 8px;
}

.permissions-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.permissions-note {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 20px 0;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.permission-category h4 {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.permission-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.permission-item input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #3b82f6;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.warning-text {
  color: #dc2626;
  font-size: 14px;
  margin: 8px 0 0 0;
}

.info-text {
  color: #6b7280;
  font-size: 14px;
  margin: 8px 0;
}

.password-result {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
}

.password-result h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 16px;
  font-weight: 600;
}

.password-display {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.password-display code {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  background: none;
  border: none;
  padding: 0;
}

.btn-icon {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.btn-icon i {
  color: #6b7280;
  font-size: 14px;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .filters-grid {
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .permissions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .users-admin {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .users-table-container {
    overflow-x: auto;
  }
  
  .users-table {
    min-width: 800px;
  }
  
  .modal {
    margin: 10px;
    max-width: calc(100vw - 20px);
  }
}
</style>

<style scoped>
.users-admin {
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
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin-bottom: var(--spacing-lg);
}

/* Estilos de validação */
.validation-summary {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  color: #dc2626;
}

.validation-summary h4 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.validation-summary ul {
  margin: 0;
  padding-left: var(--spacing-md);
  list-style-type: disc;
}

.validation-summary li {
  font-size: 0.875rem;
  margin-bottom: var(--spacing-xs);
}

.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

/* Estados de validação para campos */
.form-input.error,
.form-select.error {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.form-input.valid,
.form-select.valid {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
}

.form-input.error:focus,
.form-select.error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2);
}

.form-input.valid:focus,
.form-select.valid:focus {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
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