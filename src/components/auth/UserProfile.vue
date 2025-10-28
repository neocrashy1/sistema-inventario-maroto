<template>
  <div class="user-profile">
    <!-- Avatar e informações básicas -->
    <v-menu offset-y>
      <template v-slot:activator="{ props }">
        <v-btn
          v-bind="props"
          variant="text"
          class="user-profile-btn"
          :loading="authStore.isLoading"
        >
          <v-avatar size="32" class="me-2">
            <v-img
              v-if="user?.avatar"
              :src="user.avatar"
              :alt="user.name"
            />
            <span v-else class="avatar-initials">
              {{ userInitials }}
            </span>
          </v-avatar>
          
          <div class="user-info d-none d-sm-block">
            <div class="user-name">{{ userName }}</div>
            <div class="user-role">{{ userRoleDisplay }}</div>
          </div>
          
          <v-icon class="ms-2">mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      
      <!-- Menu dropdown -->
      <v-list class="user-menu">
        <!-- Informações do usuário -->
        <v-list-item class="user-menu-header">
          <template v-slot:prepend>
            <v-avatar size="40">
              <v-img
                v-if="user?.avatar"
                :src="user.avatar"
                :alt="user.name"
              />
              <span v-else class="avatar-initials">
                {{ userInitials }}
              </span>
            </v-avatar>
          </template>
          
          <v-list-item-title>{{ userName }}</v-list-item-title>
          <v-list-item-subtitle>{{ user?.email }}</v-list-item-subtitle>
        </v-list-item>
        
        <v-divider />
        
        <!-- Opções do menu -->
        <v-list-item @click="goToProfile">
          <template v-slot:prepend>
            <v-icon>mdi-account</v-icon>
          </template>
          <v-list-item-title>Meu Perfil</v-list-item-title>
        </v-list-item>
        
        <v-list-item @click="openChangePassword">
          <template v-slot:prepend>
            <v-icon>mdi-lock-reset</v-icon>
          </template>
          <v-list-item-title>Alterar Senha</v-list-item-title>
        </v-list-item>
        
        <ProtectedComponent permission="system.configure" :show-fallback="false">
          <v-list-item @click="goToSettings">
            <template v-slot:prepend>
              <v-icon>mdi-cog</v-icon>
            </template>
            <v-list-item-title>Configurações</v-list-item-title>
          </v-list-item>
        </ProtectedComponent>
        
        <v-divider />
        
        <v-list-item @click="handleLogout" class="logout-item">
          <template v-slot:prepend>
            <v-icon color="error">mdi-logout</v-icon>
          </template>
          <v-list-item-title class="text-error">Sair</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    
    <!-- Dialog para alterar senha -->
    <v-dialog v-model="showChangePassword" max-width="500">
      <v-card>
        <v-card-title>
          <span class="text-h5">Alterar Senha</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="passwordForm" v-model="passwordFormValid">
            <v-text-field
              v-model="passwordForm.currentPassword"
              label="Senha Atual"
              type="password"
              :rules="[rules.required]"
              variant="outlined"
              class="mb-3"
            />
            
            <v-text-field
              v-model="passwordForm.newPassword"
              label="Nova Senha"
              type="password"
              :rules="[rules.required, rules.minLength]"
              variant="outlined"
              class="mb-3"
            />
            
            <v-text-field
              v-model="passwordForm.confirmPassword"
              label="Confirmar Nova Senha"
              type="password"
              :rules="[rules.required, rules.passwordMatch]"
              variant="outlined"
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="closeChangePassword"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            :loading="changingPassword"
            :disabled="!passwordFormValid"
            @click="submitChangePassword"
          >
            Alterar Senha
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Snackbar para notificações -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAuth } from '@/composables/useAuth'
import ProtectedComponent from './ProtectedComponent.vue'

const router = useRouter()
const authStore = useAuthStore()
const { changePassword, logout } = useAuth()

// State
const showChangePassword = ref(false)
const changingPassword = ref(false)
const passwordFormValid = ref(false)

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const snackbar = reactive({
  show: false,
  message: '',
  color: 'success',
  timeout: 4000
})

// Computed
const user = computed(() => authStore.user)
const userName = computed(() => authStore.userName)
const userInitials = computed(() => authStore.userInitials)
const userRoleDisplay = computed(() => {
  const roleMap = {
    admin: 'Administrador',
    technician: 'Técnico',
    operator: 'Operador',
    viewer: 'Visualizador'
  }
  return roleMap[authStore.userRole] || authStore.userRole
})

// Validation rules
const rules = {
  required: value => !!value || 'Campo obrigatório',
  minLength: value => (value && value.length >= 6) || 'Mínimo 6 caracteres',
  passwordMatch: value => value === passwordForm.newPassword || 'Senhas não coincidem'
}

// Methods
const goToProfile = () => {
  router.push('/profile')
}

const goToSettings = () => {
  router.push('/admin/settings')
}

const openChangePassword = () => {
  showChangePassword.value = true
  resetPasswordForm()
}

const closeChangePassword = () => {
  showChangePassword.value = false
  resetPasswordForm()
}

const resetPasswordForm = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordFormValid.value = false
}

const submitChangePassword = async () => {
  if (!passwordFormValid.value) return
  
  changingPassword.value = true
  
  try {
    const result = await changePassword(
      passwordForm.currentPassword,
      passwordForm.newPassword
    )
    
    if (result.success) {
      showSnackbar('Senha alterada com sucesso!', 'success')
      closeChangePassword()
    } else {
      showSnackbar(result.error || 'Erro ao alterar senha', 'error')
    }
  } catch (error) {
    showSnackbar('Erro interno do servidor', 'error')
  } finally {
    changingPassword.value = false
  }
}

const handleLogout = async () => {
  try {
    await logout()
  } catch (error) {
    showSnackbar('Erro ao fazer logout', 'error')
  }
}

const showSnackbar = (message, color = 'success') => {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}
</script>

<style scoped>
.user-profile-btn {
  text-transform: none !important;
  height: auto !important;
  padding: 8px 12px !important;
}

.user-info {
  text-align: left;
  line-height: 1.2;
}

.user-name {
  font-weight: 500;
  font-size: 0.875rem;
  color: var(--text-primary);
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.avatar-initials {
  font-weight: 600;
  font-size: 0.875rem;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.user-menu {
  min-width: 250px;
}

.user-menu-header {
  background-color: var(--bg-secondary);
  padding: 16px !important;
}

.logout-item:hover {
  background-color: rgba(244, 67, 54, 0.1);
}

:deep(.v-list-item__prepend) {
  margin-inline-end: 12px;
}
</style>