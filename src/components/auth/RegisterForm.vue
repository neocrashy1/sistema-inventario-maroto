<template>
  <div class="register-container">
    <v-card class="register-card" elevation="8">
      <v-card-title class="register-header">
        <div class="register-logo">
          <v-icon icon="mdi-account-plus" size="48" color="primary"></v-icon>
        </div>
        <h2 class="register-title">Criar Conta</h2>
        <p class="register-subtitle">Preencha os dados para criar sua conta</p>
      </v-card-title>
      
      <v-card-text class="register-content">
        <v-form ref="registerForm" v-model="formValid" @submit.prevent="handleRegister">
          <div class="form-fields">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="userData.first_name"
                  label="Nome"
                  variant="outlined"
                  prepend-inner-icon="mdi-account"
                  :rules="nameRules"
                  :error-messages="fieldErrors.first_name"
                  @input="clearFieldError('first_name')"
                  required
                  autofocus
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="userData.last_name"
                  label="Sobrenome"
                  variant="outlined"
                  :rules="nameRules"
                  :error-messages="fieldErrors.last_name"
                  @input="clearFieldError('last_name')"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            
            <v-text-field
              v-model="userData.username"
              label="Nome de Usuário"
              variant="outlined"
              prepend-inner-icon="mdi-at"
              :rules="usernameRules"
              :error-messages="fieldErrors.username"
              @input="clearFieldError('username')"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="userData.email"
              label="Email"
              type="email"
              variant="outlined"
              prepend-inner-icon="mdi-email"
              :rules="emailRules"
              :error-messages="fieldErrors.email"
              @input="clearFieldError('email')"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="userData.password"
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
            
            <v-text-field
              v-model="userData.password_confirmation"
              :type="showPasswordConfirm ? 'text' : 'password'"
              label="Confirmar Senha"
              variant="outlined"
              prepend-inner-icon="mdi-lock-check"
              :append-inner-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
              :rules="passwordConfirmRules"
              :error-messages="fieldErrors.password_confirmation"
              @input="clearFieldError('password_confirmation')"
              required
            ></v-text-field>
            
            <v-select
              v-model="userData.role"
              :items="roleOptions"
              label="Função"
              variant="outlined"
              prepend-inner-icon="mdi-shield-account"
              :rules="roleRules"
              :error-messages="fieldErrors.role"
              @update:model-value="clearFieldError('role')"
              required
            ></v-select>
            
            <v-textarea
              v-model="userData.department"
              label="Departamento (opcional)"
              variant="outlined"
              prepend-inner-icon="mdi-office-building"
              rows="2"
              :error-messages="fieldErrors.department"
              @input="clearFieldError('department')"
            ></v-textarea>
            
            <div class="register-options">
              <v-checkbox
                v-model="acceptTerms"
                :rules="termsRules"
                required
              >
                <template #label>
                  <span class="text-body-2">
                    Eu aceito os 
                    <v-btn
                      variant="text"
                      size="small"
                      color="primary"
                      @click="showTerms = true"
                    >
                      termos de uso
                    </v-btn>
                    e 
                    <v-btn
                      variant="text"
                      size="small"
                      color="primary"
                      @click="showPrivacy = true"
                    >
                      política de privacidade
                    </v-btn>
                  </span>
                </template>
              </v-checkbox>
              
              <v-checkbox
                v-model="receiveUpdates"
                label="Receber atualizações por email"
                density="compact"
                hide-details
              ></v-checkbox>
            </div>
          </div>
          
          <v-alert
            v-if="registerError"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="registerError = ''"
          >
            {{ registerError }}
          </v-alert>
          
          <div class="register-actions">
            <v-btn
              type="submit"
              color="primary"
              variant="flat"
              size="large"
              block
              :loading="isLoading"
              :disabled="!formValid || !acceptTerms"
            >
              <v-icon icon="mdi-account-plus" class="mr-2"></v-icon>
              Criar Conta
            </v-btn>
            
            <div class="login-link">
              <span class="text-body-2">Já tem uma conta?</span>
              <v-btn
                variant="text"
                color="primary"
                size="small"
                @click="$emit('switch-to-login')"
              >
                Fazer login
              </v-btn>
            </div>
          </div>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Dialog de Termos de Uso -->
    <v-dialog v-model="showTerms" max-width="600" scrollable>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-file-document" class="mr-3"></v-icon>
          Termos de Uso
        </v-card-title>
        
        <v-card-text style="height: 400px;">
          <div class="terms-content">
            <h4>1. Aceitação dos Termos</h4>
            <p>Ao utilizar este sistema de monitoramento, você concorda com estes termos de uso.</p>
            
            <h4>2. Uso Autorizado</h4>
            <p>Este sistema destina-se exclusivamente ao monitoramento de máquinas autorizadas da organização.</p>
            
            <h4>3. Responsabilidades do Usuário</h4>
            <p>O usuário é responsável por manter a confidencialidade de suas credenciais de acesso.</p>
            
            <h4>4. Privacidade e Dados</h4>
            <p>Os dados coletados são utilizados exclusivamente para fins de monitoramento e manutenção.</p>
            
            <h4>5. Limitações de Responsabilidade</h4>
            <p>O sistema é fornecido "como está" sem garantias expressas ou implícitas.</p>
            
            <h4>6. Modificações</h4>
            <p>Estes termos podem ser modificados a qualquer momento mediante notificação.</p>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showTerms = false"
          >
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Política de Privacidade -->
    <v-dialog v-model="showPrivacy" max-width="600" scrollable>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-shield-lock" class="mr-3"></v-icon>
          Política de Privacidade
        </v-card-title>
        
        <v-card-text style="height: 400px;">
          <div class="privacy-content">
            <h4>1. Coleta de Dados</h4>
            <p>Coletamos apenas os dados necessários para o funcionamento do sistema de monitoramento.</p>
            
            <h4>2. Uso dos Dados</h4>
            <p>Os dados são utilizados para monitoramento, análise de performance e manutenção preventiva.</p>
            
            <h4>3. Compartilhamento</h4>
            <p>Os dados não são compartilhados com terceiros sem autorização expressa.</p>
            
            <h4>4. Segurança</h4>
            <p>Implementamos medidas de segurança para proteger os dados coletados.</p>
            
            <h4>5. Retenção</h4>
            <p>Os dados são mantidos pelo tempo necessário para cumprir os objetivos do sistema.</p>
            
            <h4>6. Direitos do Usuário</h4>
            <p>Você tem direito de acessar, corrigir ou solicitar a exclusão de seus dados pessoais.</p>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showPrivacy = false"
          >
            Fechar
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
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Emits
const emit = defineEmits(['switch-to-login'])

// Router and stores
const router = useRouter()
const authStore = useAuthStore()

// Reactive data
const formValid = ref(false)
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const acceptTerms = ref(false)
const receiveUpdates = ref(false)
const isLoading = ref(false)
const registerError = ref('')
const showTerms = ref(false)
const showPrivacy = ref(false)

// Form data
const userData = reactive({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  password: '',
  password_confirmation: '',
  role: '',
  department: ''
})

// Field errors
const fieldErrors = reactive({
  first_name: [],
  last_name: [],
  username: [],
  email: [],
  password: [],
  password_confirmation: [],
  role: [],
  department: []
})

// Notification system
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationColor = ref('success')

// Role options
const roleOptions = [
  { title: 'Administrador', value: 'admin' },
  { title: 'Técnico', value: 'technician' },
  { title: 'Operador', value: 'operator' },
  { title: 'Visualizador', value: 'viewer' }
]

// Validation rules
const nameRules = [
  v => !!v || 'Campo obrigatório',
  v => (v && v.length >= 2) || 'Deve ter pelo menos 2 caracteres',
  v => (v && v.length <= 50) || 'Deve ter no máximo 50 caracteres'
]

const usernameRules = [
  v => !!v || 'Nome de usuário é obrigatório',
  v => (v && v.length >= 3) || 'Deve ter pelo menos 3 caracteres',
  v => (v && v.length <= 30) || 'Deve ter no máximo 30 caracteres',
  v => /^[a-zA-Z0-9_]+$/.test(v) || 'Apenas letras, números e underscore são permitidos'
]

const emailRules = [
  v => !!v || 'Email é obrigatório',
  v => /.+@.+\..+/.test(v) || 'Email deve ser válido'
]

const passwordRules = [
  v => !!v || 'Senha é obrigatória',
  v => (v && v.length >= 8) || 'Senha deve ter pelo menos 8 caracteres',
  v => /(?=.*[a-z])/.test(v) || 'Deve conter pelo menos uma letra minúscula',
  v => /(?=.*[A-Z])/.test(v) || 'Deve conter pelo menos uma letra maiúscula',
  v => /(?=.*\d)/.test(v) || 'Deve conter pelo menos um número'
]

const passwordConfirmRules = [
  v => !!v || 'Confirmação de senha é obrigatória',
  v => v === userData.password || 'Senhas não coincidem'
]

const roleRules = [
  v => !!v || 'Função é obrigatória'
]

const termsRules = [
  v => !!v || 'Você deve aceitar os termos de uso'
]

// Computed properties
const passwordStrength = computed(() => {
  const password = userData.password
  if (!password) return { score: 0, label: '', color: '' }
  
  let score = 0
  if (password.length >= 8) score++
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/\d/.test(password)) score++
  if (/[^a-zA-Z\d]/.test(password)) score++
  
  const levels = [
    { score: 0, label: 'Muito fraca', color: 'error' },
    { score: 1, label: 'Fraca', color: 'error' },
    { score: 2, label: 'Regular', color: 'warning' },
    { score: 3, label: 'Boa', color: 'info' },
    { score: 4, label: 'Forte', color: 'success' },
    { score: 5, label: 'Muito forte', color: 'success' }
  ]
  
  return levels[score] || levels[0]
})

// Methods
const handleRegister = async () => {
  if (!formValid.value || !acceptTerms.value) return
  
  isLoading.value = true
  registerError.value = ''
  
  try {
    const registrationData = {
      ...userData,
      receive_updates: receiveUpdates.value
    }
    
    const response = await authStore.register(registrationData)
    
    if (response.success) {
      showSuccess('Conta criada com sucesso! Faça login para continuar.')
      
      // Limpar formulário
      Object.keys(userData).forEach(key => {
        userData[key] = ''
      })
      acceptTerms.value = false
      receiveUpdates.value = false
      
      // Voltar para login após um delay
      setTimeout(() => {
        emit('switch-to-login')
      }, 2000)
    } else {
      registerError.value = response.message || 'Erro ao criar conta'
      
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
    logger.error('Registration error:', error)
    registerError.value = 'Erro de conexão. Tente novamente.'
  } finally {
    isLoading.value = false
  }
}

const clearFieldError = (field) => {
  if (fieldErrors[field]) {
    fieldErrors[field] = []
  }
  if (registerError.value) {
    registerError.value = ''
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
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, rgb(var(--v-theme-secondary)) 0%, rgb(var(--v-theme-primary)) 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 600px;
  border-radius: 16px;
  overflow: hidden;
}

.register-header {
  text-align: center;
  padding: 32px 24px 24px;
  background: rgb(var(--v-theme-surface));
}

.register-logo {
  margin-bottom: 16px;
}

.register-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: rgb(var(--v-theme-on-surface));
}

.register-subtitle {
  color: rgb(var(--v-theme-on-surface-variant));
  margin: 0;
}

.register-content {
  padding: 24px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}

.register-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.register-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-link {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.terms-content,
.privacy-content {
  line-height: 1.6;
}

.terms-content h4,
.privacy-content h4 {
  margin-top: 16px;
  margin-bottom: 8px;
  color: rgb(var(--v-theme-primary));
}

.terms-content p,
.privacy-content p {
  margin-bottom: 12px;
  text-align: justify;
}

/* Password strength indicator */
.password-strength {
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  background: rgb(var(--v-theme-surface-variant));
}

.strength-bar {
  height: 4px;
  border-radius: 2px;
  margin-top: 4px;
  transition: all 0.3s ease;
}

/* Responsividade */
@media (max-width: 600px) {
  .register-container {
    padding: 16px;
  }
  
  .register-card {
    max-width: 100%;
  }
  
  .register-header {
    padding: 24px 16px 16px;
  }
  
  .register-content {
    padding: 16px;
  }
  
  .login-link {
    flex-direction: column;
    gap: 4px;
  }
}

/* Animações */
.register-card {
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
.register-card :deep(.v-btn) {
  transition: all 0.2s ease;
}

.register-card :deep(.v-btn:hover) {
  transform: translateY(-1px);
}

/* Focus styles */
.register-card :deep(.v-field--focused) {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.2);
}

/* Error state */
.register-card :deep(.v-field--error) {
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>