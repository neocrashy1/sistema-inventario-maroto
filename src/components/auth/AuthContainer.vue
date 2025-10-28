<template>
  <div class="auth-container">
    <div class="auth-background">
      <div class="auth-overlay"></div>
      
      <!-- Particles background effect -->
      <div class="particles">
        <div 
          v-for="i in 50" 
          :key="i" 
          class="particle"
          :style="getParticleStyle(i)"
        ></div>
      </div>
    </div>
    
    <div class="auth-content">
      <!-- Logo e branding -->
      <div class="auth-branding">
        <div class="brand-logo">
          <v-icon 
            icon="mdi-monitor-dashboard" 
            size="64" 
            color="primary"
          ></v-icon>
        </div>
        <h1 class="brand-title">Levitiis Monitor</h1>
        <p class="brand-subtitle">Sistema de Monitoramento de Máquinas</p>
      </div>
      
      <!-- Formulários de autenticação -->
      <div class="auth-forms">
        <Transition name="slide-fade" mode="out-in">
          <LoginForm 
            v-if="currentView === 'login'"
            @switch-to-register="currentView = 'register'"
            @login-success="handleLoginSuccess"
          />
          <RegisterForm 
            v-else-if="currentView === 'register'"
            @switch-to-login="currentView = 'login'"
          />
        </Transition>
      </div>
      
      <!-- Footer -->
      <div class="auth-footer">
        <div class="footer-links">
          <v-btn
            variant="text"
            size="small"
            @click="showAbout = true"
          >
            Sobre o Sistema
          </v-btn>
          <span class="divider">•</span>
          <v-btn
            variant="text"
            size="small"
            @click="showHelp = true"
          >
            Ajuda
          </v-btn>
          <span class="divider">•</span>
          <v-btn
            variant="text"
            size="small"
            @click="showContact = true"
          >
            Contato
          </v-btn>
        </div>
        
        <div class="footer-info">
          <p class="copyright">
            © {{ currentYear }} Levitiis Monitor. Todos os direitos reservados.
          </p>
          <p class="version">
            Versão {{ appVersion }}
          </p>
        </div>
      </div>
    </div>

    <!-- Dialog Sobre o Sistema -->
    <v-dialog v-model="showAbout" max-width="500">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-information" class="mr-3"></v-icon>
          Sobre o Sistema
        </v-card-title>
        
        <v-card-text>
          <div class="about-content">
            <div class="system-info">
              <h4>Levitiis Monitor</h4>
              <p>Sistema completo de monitoramento de máquinas Windows com:</p>
              
              <ul class="feature-list">
                <li>Monitoramento em tempo real de CPU, memória e disco</li>
                <li>Sistema de inventário automatizado</li>
                <li>Dashboard interativo com gráficos</li>
                <li>Sistema de chamados e alertas</li>
                <li>Relatórios e análises detalhadas</li>
                <li>Controle de acesso baseado em funções</li>
              </ul>
              
              <div class="tech-stack">
                <h5>Tecnologias Utilizadas:</h5>
                <div class="tech-chips">
                  <v-chip size="small" color="primary" variant="outlined">Vue 3</v-chip>
                  <v-chip size="small" color="primary" variant="outlined">Vuetify</v-chip>
                  <v-chip size="small" color="primary" variant="outlined">FastAPI</v-chip>
                  <v-chip size="small" color="primary" variant="outlined">Python</v-chip>
                  <v-chip size="small" color="primary" variant="outlined">SQLite</v-chip>
                </div>
              </div>
            </div>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showAbout = false">
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Ajuda -->
    <v-dialog v-model="showHelp" max-width="600" scrollable>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-help-circle" class="mr-3"></v-icon>
          Central de Ajuda
        </v-card-title>
        
        <v-card-text style="height: 400px;">
          <div class="help-content">
            <v-expansion-panels variant="accordion">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon icon="mdi-login" class="mr-3"></v-icon>
                  Como fazer login?
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <p>Para acessar o sistema:</p>
                  <ol>
                    <li>Digite seu nome de usuário ou email</li>
                    <li>Digite sua senha</li>
                    <li>Clique em "Entrar"</li>
                  </ol>
                  <p><strong>Credenciais padrão:</strong></p>
                  <ul>
                    <li>Admin: admin / admin123</li>
                    <li>Técnico: tecnico / tecnico123</li>
                    <li>Operador: operador / operador123</li>
                  </ul>
                </v-expansion-panel-text>
              </v-expansion-panel>
              
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon icon="mdi-account-plus" class="mr-3"></v-icon>
                  Como criar uma conta?
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <p>Para criar uma nova conta:</p>
                  <ol>
                    <li>Clique em "Criar conta" na tela de login</li>
                    <li>Preencha todos os campos obrigatórios</li>
                    <li>Escolha sua função no sistema</li>
                    <li>Aceite os termos de uso</li>
                    <li>Clique em "Criar Conta"</li>
                  </ol>
                </v-expansion-panel-text>
              </v-expansion-panel>
              
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon icon="mdi-lock-reset" class="mr-3"></v-icon>
                  Esqueci minha senha
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <p>Para recuperar sua senha:</p>
                  <ol>
                    <li>Clique em "Esqueceu a senha?" na tela de login</li>
                    <li>Digite seu email cadastrado</li>
                    <li>Verifique sua caixa de entrada</li>
                    <li>Siga as instruções do email</li>
                  </ol>
                </v-expansion-panel-text>
              </v-expansion-panel>
              
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon icon="mdi-shield-account" class="mr-3"></v-icon>
                  Níveis de acesso
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <p><strong>Administrador:</strong> Acesso completo ao sistema</p>
                  <p><strong>Técnico:</strong> Gerenciar máquinas e chamados</p>
                  <p><strong>Operador:</strong> Visualizar dados e criar chamados</p>
                  <p><strong>Visualizador:</strong> Apenas visualização</p>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showHelp = false">
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog Contato -->
    <v-dialog v-model="showContact" max-width="500">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-email" class="mr-3"></v-icon>
          Informações de Contato
        </v-card-title>
        
        <v-card-text>
          <div class="contact-content">
            <div class="contact-item">
              <v-icon icon="mdi-email" class="mr-3"></v-icon>
              <div>
                <strong>Email de Suporte:</strong>
                <p>suporte@levitiis.com</p>
              </div>
            </div>
            
            <div class="contact-item">
              <v-icon icon="mdi-phone" class="mr-3"></v-icon>
              <div>
                <strong>Telefone:</strong>
                <p>(11) 9999-9999</p>
              </div>
            </div>
            
            <div class="contact-item">
              <v-icon icon="mdi-clock" class="mr-3"></v-icon>
              <div>
                <strong>Horário de Atendimento:</strong>
                <p>Segunda a Sexta: 8h às 18h</p>
              </div>
            </div>
            
            <div class="contact-item">
              <v-icon icon="mdi-web" class="mr-3"></v-icon>
              <div>
                <strong>Website:</strong>
                <p>www.levitiis.com</p>
              </div>
            </div>
          </div>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showContact = false">
            Fechar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from './LoginForm.vue'
import RegisterForm from './RegisterForm.vue'

// Router
const router = useRouter()

// Reactive data
const currentView = ref('login')
const showAbout = ref(false)
const showHelp = ref(false)
const showContact = ref(false)

// Computed properties
const currentYear = computed(() => new Date().getFullYear())
const appVersion = computed(() => '1.0.0')

// Methods
const handleLoginSuccess = (user) => {
  // Redirecionar para o dashboard após login bem-sucedido
  router.push('/dashboard')
}

const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 2
  const duration = Math.random() * 20 + 10
  const delay = Math.random() * 5
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`
  }
}

// Lifecycle
onMounted(() => {
  // Adicionar classe para animação inicial
  document.body.classList.add('auth-page')
})
</script>

<style scoped>
.auth-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    rgb(var(--v-theme-primary)) 0%, 
    rgb(var(--v-theme-secondary)) 50%, 
    rgb(var(--v-theme-accent)) 100%);
  z-index: 1;
}

.auth-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 2;
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 3;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  animation: float infinite ease-in-out;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.1;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 0.3;
  }
}

.auth-content {
  position: relative;
  z-index: 4;
  width: 100%;
  max-width: 1200px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.auth-branding {
  text-align: center;
  color: white;
  margin-bottom: 20px;
}

.brand-logo {
  margin-bottom: 16px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  background: linear-gradient(45deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.auth-forms {
  width: 100%;
  max-width: 800px;
  display: flex;
  justify-content: center;
}

.auth-footer {
  text-align: center;
  color: white;
  opacity: 0.8;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.divider {
  opacity: 0.6;
}

.footer-info {
  font-size: 0.875rem;
}

.copyright {
  margin-bottom: 4px;
}

.version {
  opacity: 0.7;
  margin: 0;
}

/* Dialog styles */
.about-content {
  line-height: 1.6;
}

.system-info h4 {
  color: rgb(var(--v-theme-primary));
  margin-bottom: 12px;
}

.feature-list {
  margin: 16px 0;
  padding-left: 20px;
}

.feature-list li {
  margin-bottom: 8px;
}

.tech-stack {
  margin-top: 20px;
}

.tech-stack h5 {
  margin-bottom: 8px;
  color: rgb(var(--v-theme-secondary));
}

.tech-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.help-content .v-expansion-panel-title {
  font-weight: 500;
}

.contact-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.contact-item div {
  flex: 1;
}

.contact-item strong {
  color: rgb(var(--v-theme-primary));
}

.contact-item p {
  margin: 4px 0 0 0;
  color: rgb(var(--v-theme-on-surface-variant));
}

/* Transitions */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-30px);
  opacity: 0;
}

/* Responsividade */
@media (max-width: 768px) {
  .auth-content {
    padding: 16px;
    gap: 30px;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-subtitle {
    font-size: 1rem;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 4px;
  }
  
  .divider {
    display: none;
  }
}

@media (max-width: 480px) {
  .brand-title {
    font-size: 1.75rem;
  }
  
  .auth-forms {
    max-width: 100%;
  }
}

/* Global auth page styles */
:global(.auth-page) {
  overflow-x: hidden;
}

:global(.auth-page .v-application__wrap) {
  min-height: 100vh;
}
</style>