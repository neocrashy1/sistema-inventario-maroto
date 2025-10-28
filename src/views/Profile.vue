<template>
  <div class="profile-page">
    <div class="page-header">
      <h1>Perfil do Usuário</h1>
      <p>Gerencie suas informações pessoais e configurações de conta</p>
    </div>

    <div class="profile-content">
      <!-- Informações Básicas -->
      <div class="profile-card">
        <div class="card-header">
          <h2>Informações Básicas</h2>
          <button 
            v-if="!editingBasicInfo" 
            @click="editingBasicInfo = true"
            class="btn btn-outline"
          >
            <i class="fas fa-edit"></i>
            Editar
          </button>
        </div>

        <div class="profile-avatar-section">
          <div class="avatar-container">
            <div class="user-avatar">
              <i class="fas fa-user"></i>
            </div>
            <button class="change-avatar-btn">
              <i class="fas fa-camera"></i>
            </button>
          </div>
          <div class="avatar-info">
            <h3>{{ authStore.userName }}</h3>
            <p>{{ authStore.userRole === 'admin' ? 'Administrador' : 'Usuário' }}</p>
          </div>
        </div>

        <form @submit.prevent="saveBasicInfo" class="profile-form">
          <div class="form-row">
            <div class="form-group">
              <label for="name">Nome Completo</label>
              <input
                id="name"
                v-model="profileData.name"
                type="text"
                :disabled="!editingBasicInfo"
                required
              >
            </div>
            <div class="form-group">
              <label for="email">E-mail</label>
              <input
                id="email"
                v-model="profileData.email"
                type="email"
                :disabled="!editingBasicInfo"
                required
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="phone">Telefone</label>
              <input
                id="phone"
                v-model="profileData.phone"
                type="tel"
                :disabled="!editingBasicInfo"
                placeholder="(11) 99999-9999"
              >
            </div>
            <div class="form-group">
              <label for="department">Departamento</label>
              <input
                id="department"
                v-model="profileData.department"
                type="text"
                :disabled="!editingBasicInfo"
                placeholder="Ex: TI, RH, Financeiro"
              >
            </div>
          </div>

          <div v-if="editingBasicInfo" class="form-actions">
            <button type="submit" class="btn btn-primary">
              <i class="fas fa-save"></i>
              Salvar Alterações
            </button>
            <button 
              type="button" 
              @click="cancelEditBasicInfo"
              class="btn btn-outline"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>

      <!-- Alterar Senha -->
      <div class="profile-card">
        <div class="card-header">
          <h2>Segurança</h2>
        </div>

        <form @submit.prevent="changePassword" class="profile-form">
          <div class="form-group">
            <label for="currentPassword">Senha Atual</label>
            <input
              id="currentPassword"
              v-model="passwordData.currentPassword"
              type="password"
              required
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="newPassword">Nova Senha</label>
              <input
                id="newPassword"
                v-model="passwordData.newPassword"
                type="password"
                required
                minlength="6"
              >
            </div>
            <div class="form-group">
              <label for="confirmPassword">Confirmar Nova Senha</label>
              <input
                id="confirmPassword"
                v-model="passwordData.confirmPassword"
                type="password"
                required
                minlength="6"
              >
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary">
              <i class="fas fa-key"></i>
              Alterar Senha
            </button>
          </div>
        </form>
      </div>

      <!-- Preferências -->
      <div class="profile-card">
        <div class="card-header">
          <h2>Preferências</h2>
        </div>

        <div class="preferences-section">
          <div class="preference-item">
            <div class="preference-info">
              <h4>Notificações por E-mail</h4>
              <p>Receber notificações sobre atividades do sistema</p>
            </div>
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="preferences.emailNotifications"
                @change="savePreferences"
              >
              <span class="slider"></span>
            </label>
          </div>

          <div class="preference-item">
            <div class="preference-info">
              <h4>Notificações Push</h4>
              <p>Receber notificações em tempo real no navegador</p>
            </div>
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="preferences.pushNotifications"
                @change="savePreferences"
              >
              <span class="slider"></span>
            </label>
          </div>

          <div class="preference-item">
            <div class="preference-info">
              <h4>Tema Escuro</h4>
              <p>Usar tema escuro na interface</p>
            </div>
            <label class="switch">
              <input 
                type="checkbox" 
                v-model="preferences.darkTheme"
                @change="savePreferences"
              >
              <span class="slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Atividade Recente -->
      <div class="profile-card">
        <div class="card-header">
          <h2>Atividade Recente</h2>
        </div>

        <div class="activity-list">
          <div 
            v-for="activity in recentActivity" 
            :key="activity.id"
            class="activity-item"
          >
            <div class="activity-icon">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-content">
              <p class="activity-description">{{ activity.description }}</p>
              <span class="activity-time">{{ formatTime(activity.time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const authStore = useAuthStore()

// State
const editingBasicInfo = ref(false)

const profileData = reactive({
  name: '',
  email: '',
  phone: '',
  department: ''
})

const passwordData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const preferences = reactive({
  emailNotifications: true,
  pushNotifications: false,
  darkTheme: false
})

const recentActivity = ref([
  {
    id: 1,
    description: 'Login realizado com sucesso',
    icon: 'fas fa-sign-in-alt text-success',
    time: new Date(Date.now() - 1000 * 60 * 30) // 30 min ago
  },
  {
    id: 2,
    description: 'Perfil atualizado',
    icon: 'fas fa-user-edit text-primary',
    time: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
  },
  {
    id: 3,
    description: 'Senha alterada',
    icon: 'fas fa-key text-warning',
    time: new Date(Date.now() - 1000 * 60 * 60 * 24) // 1 day ago
  }
])

// Methods
const loadProfileData = () => {
  if (authStore.user) {
    profileData.name = authStore.user.name || ''
    profileData.email = authStore.user.email || ''
    profileData.phone = authStore.user.phone || ''
    profileData.department = authStore.user.department || ''
  }
}

const saveBasicInfo = () => {
  // Aqui você faria a chamada para a API para salvar os dados
  logger.debug('Salvando informações básicas:', profileData)
  
  // Simular sucesso
  editingBasicInfo.value = false
  
  // Atualizar o store local (em uma implementação real, isso viria da API)
  if (authStore.user) {
    authStore.user.name = profileData.name
    authStore.user.email = profileData.email
    authStore.user.phone = profileData.phone
    authStore.user.department = profileData.department
    
    // Atualizar localStorage
    localStorage.setItem('user', JSON.stringify(authStore.user))
  }
}

const cancelEditBasicInfo = () => {
  editingBasicInfo.value = false
  loadProfileData() // Recarregar dados originais
}

const changePassword = () => {
  if (passwordData.newPassword !== passwordData.confirmPassword) {
    alert('As senhas não coincidem!')
    return
  }

  // Aqui você faria a chamada para a API para alterar a senha
  logger.debug('Alterando senha...')
  
  // Simular sucesso
  alert('Senha alterada com sucesso!')
  
  // Limpar campos
  passwordData.currentPassword = ''
  passwordData.newPassword = ''
  passwordData.confirmPassword = ''
}

const savePreferences = () => {
  // Aqui você faria a chamada para a API para salvar as preferências
  logger.debug('Salvando preferências:', preferences)
  
  // Salvar no localStorage
  localStorage.setItem('userPreferences', JSON.stringify(preferences))
}

const loadPreferences = () => {
  onMounted(() => {
    loadUser()
    ;(() => {
      const saved = localStorage.getItem('userPreferences')
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          if (parsed && typeof parsed === 'object') {
            Object.assign(preferences, parsed)
          }
        } catch {
          // conteúdo inválido: ignora silenciosamente
        }
      }
    })()
  })
}

const formatTime = (time) => {
  return formatDistanceToNow(time, { 
    addSuffix: true, 
    locale: ptBR 
  })
}

onMounted(() => {
  loadProfileData()
  loadPreferences()
})
</script>

<style scoped>
.profile-page {
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.page-header p {
  color: var(--text-secondary);
  margin: 0;
}

.profile-content {
  display: grid;
  gap: var(--spacing-xl);
}

.profile-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}

.card-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.profile-avatar-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.avatar-container {
  position: relative;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  border: 2px solid var(--bg-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
}

.avatar-info h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.avatar-info p {
  color: var(--text-secondary);
  margin: 0;
  text-transform: capitalize;
}

.profile-form {
  display: grid;
  gap: var(--spacing-lg);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input {
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled {
  background-color: var(--bg-secondary);
  color: var(--text-muted);
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.btn-outline {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-outline:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.preferences-section {
  display: grid;
  gap: var(--spacing-lg);
}

.preference-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.preference-info h4 {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.preference-info p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 0.875rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border-color);
  transition: 0.4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary-color);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.activity-list {
  display: grid;
  gap: var(--spacing-md);
}

.activity-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.activity-content {
  flex: 1;
}

.activity-description {
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.activity-time {
  color: var(--text-muted);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .profile-avatar-section {
    flex-direction: column;
    text-align: center;
  }
  
  .preference-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }
}
</style>
