<template>
  <div class="login-container">
    <v-card class="login-card" elevation="8">
      <v-card-title class="login-header">
        <div class="login-logo">
          <v-icon icon="mdi-monitor-dashboard" size="48" color="primary"></v-icon>
        </div>
        <h2 class="login-title">Sistema de Monitoramento</h2>
        <p class="login-subtitle">Faça login para acessar o dashboard</p>
      </v-card-title>
      
      <v-card-text class="login-content">
        <v-form ref="loginForm" v-model="formValid" @submit.prevent="handleLogin">
          <div class="form-fields">
            <v-text-field
              v-model="credentials.username"
              label="Usuário ou Email"
              variant="outlined"
              prepend-inner-icon="mdi-account"
              :rules="usernameRules"
              :error-messages="fieldErrors.username"
              @input="clearFieldError('username')"
              required
              autofocus
            ></v-text-field>
            
            <v-text-field
              v-model="credentials.password"
              :type="showPassword ? 'text' : 'password'"
              label="Senha"
              variant="outlined"
              prepend-inner-icon="mdi-lock"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPassword = !showPassword"
              :rules="passwordRules"
              :error-messages="fieldErrors.password"
              @input="clearFieldError('password')"
              required
            ></v-text-field>
            
            <div class="login-options">
              <v-checkbox
                v-model="rememberMe"
                label="Lembrar de mim"
                density="compact"
                hide-details
              ></v-checkbox>
              
              <v-btn
                variant="text"
                size="small"
                color="primary"
                @click="showForgotPassword = true"
              >
                Esqueceu a senha?
              </v-btn>
            </div>
          </div>
          
          <v-alert
            v-if="loginError"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="loginError = ''"
          >
            {{ loginError }}
          </v-alert>
          
          <div class="login-actions">
            <v-btn
              type="submit"
              color="primary"
              variant="flat"
              size="large"
              block
              :loading="isLoading"
              :disabled="!formValid"
            >
              <v-icon icon="mdi-login" class="mr-2"></v-icon>
              Entrar
            </v-btn>
            
            <div class="register-link">
              <span class="text-body-2">Não tem uma conta?</span>
              <v-btn
                variant="text"
                color="primary"
                size="small"
                @click="$emit('switch-to-register')"
              >
                Criar conta
              </v-btn>
            </div>
          </div>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Dialog de Recuperação de Senha -->
    <v-dialog v-model="showForgotPassword" max-width="500">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-lock-reset" class="mr-3"></v-icon>
          Recuperar Senha
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-2 mb-4">
            Digite seu email para receber as instruções de recuperação de senha.
          </p>
          
          <v-text-field
            v-model="resetEmail"
            label="Email"
            variant="outlined"
            prepend-inner-icon="mdi-email"
            :rules="emailRules"
            required
          ></v-text-field>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showForgotPassword = false"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="handlePasswordReset"
            :loading="isResetting"
          >
            Enviar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar para notificações -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationColor"
      :timeout="4000"
      location="top right"
    >
      {{ notificationMessage }}
      <template #actions>
        <v-btn
          variant="text"
          @click="showNotification = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Emits
const emit = defineEmits(['switch-to-register'])

// Router and stores
const router = useRouter()
const authStore = useAuthStore()

// Reactive data
const formValid = ref(false)
const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)
const isResetting = ref(false)
const loginError = ref('')
const showForgotPassword = ref(false)
const resetEmail = ref('')

// Form data
const credentials = reactive({
  username: '',
  password: ''
})

// Field errors
const fieldErrors = reactive({
  username: [],
  password: []
})

// Notification system
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationColor = ref('success')

// Validation rules
const usernameRules = [
  v => !!v || 'Usuário é obrigatório',
  v => (v && v.length >= 3) || 'Usuário deve ter pelo menos 3 caracteres'
]

const passwordRules = [
  v => !!v || 'Senha é obrigatória',
  v => (v && v.length >= 6) || 'Senha deve ter pelo menos 6 caracteres'
]

const emailRules = [
  v => !!v || 'Email é obrigatório',
  v => /.+@.+\..+/.test(v) || 'Email deve ser válido'
]

// Methods
const handleLogin = async () => {
  if (!formValid.value) return
  
  isLoading.value = true
  loginError.value = ''
  
  try {
    const loginData = {
      username: credentials.username,
      password: credentials.password,
      remember_me: rememberMe.value
    }
    
    const response = await authStore.login(loginData)
    
    if (response.success) {
      showSuccess('Login realizado com sucesso!')
      
      // Redirecionar para a página principal ou página solicitada
      const redirectTo = router.currentRoute.value.query.redirect || '/dashboard'
      router.push(redirectTo)
    } else {
      loginError.value = response.message || 'Erro ao fazer login'
      
      // Tratar erros específicos de campo
      if (response.field_errors) {
        Object.keys(response.field_errors).forEach(field => {
          if (fieldErrors[field]) {
            fieldErrors[field] = response.field_errors[field]
          }
        })
      }
    }
  } catch (error) {
    logger.error('Login error:', error)
    loginError.value = 'Erro de conexão. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}

const handlePasswordReset = async () => {
  if (!resetEmail.value || !/.+@.+\..+/.test(resetEmail.value)) {
    showError('Por favor, digite um email válido')
    return
  }
  
  isResetting.value = true
  
  try {
    const response = await authStore.requestPasswordReset(resetEmail.value)
    
    if (response.success) {
      showSuccess('Instruções de recuperação enviadas para seu email!')
      showForgotPassword.value = false
      resetEmail.value = ''
    } else {
      showError(response.message || 'Erro ao solicitar recuperação de senha')
    }
  } catch (error) {
    logger.error('Password reset error:', error)
    showError('Erro de conexão. Tente novamente.')
  } finally {
    isResetting.value = false
  }
}

const clearFieldError = (field) => {
  if (fieldErrors[field]) {
    fieldErrors[field] = []
  }
  if (loginError.value) {
    loginError.value = ''
  }
}

// Notification helpers
const showSuccess = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'success'
  showNotification.value = true
}

const showError = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'error'
  showNotification.value = true
}

// Auto-fill for demo purposes (remove in production)
if (import.meta.env.DEV) {
  credentials.username = 'admin'
  credentials.password = 'admin123'
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)) 0%, rgb(var(--v-theme-secondary)) 100%);
  padding: 20px;
}

.login-card {
  max-width: 720px;
  border-radius: 16px;
  overflow: hidden;
}

.login-header {
  text-align: center;
  padding: 32px 24px 24px;
  background: rgb(var(--v-theme-surface));
}

.login-logo {
  margin-bottom: 16px;
}

.login-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: rgb(var(--v-theme-on-surface));
}

.login-subtitle {
  color: rgb(var(--v-theme-on-surface-variant));
  margin: 0;
}

.login-content {
  padding: 24px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.login-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.register-link {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Responsividade */
@media (max-width: 600px) {
  .login-container {
    padding: 16px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .login-header {
    padding: 24px 16px 16px;
  }
  
  .login-content {
    padding: 16px;
  }
  
  .login-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .register-link {
    flex-direction: column;
    gap: 4px;
  }
}

/* Animações */
.login-card {
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover effects */
.login-card :deep(.v-btn) {
  transition: all 0.2s ease;
}

.login-card :deep(.v-btn:hover) {
  transform: translateY(-1px);
}

/* Focus styles */
.login-card :deep(.v-field--focused) {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2);
}

/* Error state */
.login-card :deep(.v-field--error) {
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>