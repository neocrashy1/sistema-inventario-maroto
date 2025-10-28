<template>
  <div class="test-page">
    <div class="page-header">
      <h1>Teste de Funcionalidades</h1>
      <p>Verificação das funcionalidades básicas da aplicação</p>
    </div>

    <div class="test-sections">
      <!-- Teste da API -->
      <div class="test-section">
        <h2>Teste da Integração com API</h2>
        
        <div class="test-item">
          <h3>Assets API</h3>
          <p><strong>Status:</strong> <span :class="apiStatus.assets.class">{{ apiStatus.assets.message }}</span></p>
          <p><strong>Total de Ativos:</strong> {{ assetsStore.dashboardSummary?.totalAssets || 0 }}</p>
          <p><strong>Valor Total:</strong> {{ formatCurrency(assetsStore.dashboardSummary?.totalValue || 0) }}</p>
          <p><strong>Ativos Ativos:</strong> {{ assetsStore.dashboardSummary?.activeCount || 0 }}</p>
          <p><strong>Em Manutenção:</strong> {{ assetsStore.dashboardSummary?.maintenanceCount || 0 }}</p>
          <button @click="testAssetsAPI" class="btn btn-primary" :disabled="loading.assets">
            {{ loading.assets ? 'Testando...' : 'Testar Assets API' }}
          </button>
        </div>

        <div class="test-item">
          <h3>Dashboard API</h3>
          <p><strong>Status:</strong> <span :class="apiStatus.dashboard.class">{{ apiStatus.dashboard.message }}</span></p>
          <p><strong>Atividades Recentes:</strong> {{ dashboardStore.recentActivities?.length || 0 }}</p>
          <p><strong>Alertas:</strong> {{ dashboardStore.alerts?.length || 0 }}</p>
          <p><strong>Loading:</strong> {{ dashboardStore.loading }}</p>
          <button @click="testDashboardAPI" class="btn btn-primary" :disabled="loading.dashboard">
            {{ loading.dashboard ? 'Testando...' : 'Testar Dashboard API' }}
          </button>
        </div>

        <div class="test-item">
          <h3>Teste Completo</h3>
          <p><strong>Status Geral:</strong> <span :class="overallStatus.class">{{ overallStatus.message }}</span></p>
          <button @click="runFullAPITest" class="btn btn-success" :disabled="loading.full">
            {{ loading.full ? 'Executando Teste Completo...' : 'Executar Teste Completo da API' }}
          </button>
        </div>
      </div>

      <!-- Teste dos Stores -->
      <div class="test-section">
        <h2>Teste dos Stores</h2>
        
        <div class="test-item">
          <h3>Assets Store</h3>
          <p><strong>Total de Ativos:</strong> {{ assetsStore.totalAssets }}</p>
          <p><strong>Valor Total:</strong> {{ formatCurrency(assetsStore.totalValue) }}</p>
          <p><strong>Ativos Ativos:</strong> {{ assetsStore.activeAssets }}</p>
          <p><strong>Ativos em Manutenção:</strong> {{ assetsStore.maintenanceAssets }}</p>
          <p><strong>Categorias:</strong> {{ assetsStore.categories?.length || 0 }}</p>
          <button @click="testAssetsStore" class="btn btn-primary">Testar Assets Store</button>
        </div>

        <div class="test-item">
          <h3>Dashboard Store</h3>
          <p><strong>Atividades Recentes:</strong> {{ dashboardStore.recentActivities?.length || 0 }}</p>
          <p><strong>Loading:</strong> {{ dashboardStore.loading }}</p>
          <button @click="testDashboardStore" class="btn btn-primary">Testar Dashboard Store</button>
        </div>
      </div>

      <!-- Teste de Navegação -->
      <div class="test-section">
        <h2>Teste de Navegação</h2>
        <div class="nav-buttons">
          <router-link to="/" class="btn btn-secondary">Dashboard</router-link>
          <router-link to="/assets" class="btn btn-secondary">Ativos</router-link>
          <router-link to="/movements" class="btn btn-secondary">Movimentações</router-link>
          <router-link to="/reports" class="btn btn-secondary">Relatórios</router-link>
        </div>
      </div>

      <!-- Teste de Componentes -->
      <div class="test-section">
        <h2>Teste de Componentes</h2>
        <div class="component-tests">
          <div class="kpi-card">
            <div class="kpi-icon">
              <i class="fas fa-check"></i>
            </div>
            <div class="kpi-content">
              <h3>123</h3>
              <p>Teste KPI</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Log de Testes -->
      <div class="test-section">
        <h2>Log de Testes</h2>
        <div class="test-log">
          <div v-for="log in testLogs" :key="log.id" class="log-item" :class="log.type">
            <span class="log-time">{{ formatTime(log.time) }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAssetsStore } from '@/stores/assets'
import { useDashboardStore } from '@/stores/dashboard'

// Stores
const assetsStore = useAssetsStore()
const dashboardStore = useDashboardStore()

// State
const testLogs = ref([])
const loading = ref({
  assets: false,
  dashboard: false,
  full: false
})

const apiStatus = ref({
  assets: { message: 'Não testado', class: 'text-gray-500' },
  dashboard: { message: 'Não testado', class: 'text-gray-500' }
})

const overallStatus = ref({ message: 'Não testado', class: 'text-gray-500' })

// Methods
const addLog = (message, type = 'info') => {
  testLogs.value.unshift({
    id: Date.now(),
    time: new Date(),
    message,
    type
  })
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value || 0)
}

const formatTime = (time) => {
  return new Date(time).toLocaleTimeString('pt-BR')
}

const testAssetsStore = async () => {
  try {
    addLog('Testando Assets Store...', 'info')
    await assetsStore.fetchAssets()
    addLog(`Assets Store OK - ${assetsStore.totalAssets} ativos carregados`, 'success')
  } catch (error) {
    addLog(`Erro no Assets Store: ${error.message}`, 'error')
  }
}

const testDashboardStore = async () => {
  try {
    addLog('Testando Dashboard Store...', 'info')
    await dashboardStore.fetchDashboardData()
    addLog(`Dashboard Store OK - ${dashboardStore.recentActivities?.length || 0} atividades`, 'success')
  } catch (error) {
    addLog(`Erro no Dashboard Store: ${error.message}`, 'error')
  }
}

const testAssetsAPI = async () => {
  loading.value.assets = true
  try {
    addLog('Testando Assets API...', 'info')
    await assetsStore.fetchDashboardSummary()
    
    if (assetsStore.dashboardSummary) {
      apiStatus.value.assets = { message: 'Conectado', class: 'text-green-600' }
      addLog(`Assets API OK - ${assetsStore.dashboardSummary.totalAssets} ativos`, 'success')
    } else {
      apiStatus.value.assets = { message: 'Dados mock', class: 'text-yellow-600' }
      addLog('Assets API usando dados mock', 'warning')
    }
  } catch (error) {
    apiStatus.value.assets = { message: 'Erro', class: 'text-red-600' }
    addLog(`Erro na Assets API: ${error.message}`, 'error')
  } finally {
    loading.value.assets = false
  }
}

const testDashboardAPI = async () => {
  loading.value.dashboard = true
  try {
    addLog('Testando Dashboard API...', 'info')
    await dashboardStore.fetchDashboardData()
    
    if (dashboardStore.recentActivities?.length > 0) {
      apiStatus.value.dashboard = { message: 'Conectado', class: 'text-green-600' }
      addLog(`Dashboard API OK - ${dashboardStore.recentActivities.length} atividades`, 'success')
    } else {
      apiStatus.value.dashboard = { message: 'Dados mock', class: 'text-yellow-600' }
      addLog('Dashboard API usando dados mock', 'warning')
    }
  } catch (error) {
    apiStatus.value.dashboard = { message: 'Erro', class: 'text-red-600' }
    addLog(`Erro na Dashboard API: ${error.message}`, 'error')
  } finally {
    loading.value.dashboard = false
  }
}

const runFullAPITest = async () => {
  loading.value.full = true
  addLog('Iniciando teste completo da API...', 'info')
  
  try {
    await Promise.all([
      testAssetsAPI(),
      testDashboardAPI()
    ])
    
    const assetsOK = apiStatus.value.assets.message !== 'Erro'
    const dashboardOK = apiStatus.value.dashboard.message !== 'Erro'
    
    if (assetsOK && dashboardOK) {
      overallStatus.value = { message: 'Todas as APIs funcionando', class: 'text-green-600' }
      addLog('Teste completo da API: SUCESSO', 'success')
    } else {
      overallStatus.value = { message: 'Algumas APIs com problemas', class: 'text-yellow-600' }
      addLog('Teste completo da API: PARCIAL', 'warning')
    }
  } catch (error) {
    overallStatus.value = { message: 'Falha geral', class: 'text-red-600' }
    addLog(`Teste completo da API: FALHA - ${error.message}`, 'error')
  } finally {
    loading.value.full = false
  }
}

// Initialize
onMounted(() => {
  addLog('Página de teste carregada', 'info')
  testAssetsStore()
  testDashboardStore()
})
</script>

<style scoped>
.test-page {
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.page-header h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.test-sections {
  display: grid;
  gap: var(--spacing-lg);
}

.test-section {
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.test-section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.test-item {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.test-item h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.nav-buttons {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.component-tests {
  display: flex;
  gap: var(--spacing-md);
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.kpi-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.kpi-content p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.test-log {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.log-item {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-xs);
}

.log-item.info {
  background-color: rgba(6, 182, 212, 0.1);
  color: var(--info-color);
}

.log-item.success {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.log-item.error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.log-time {
  font-size: 0.75rem;
  opacity: 0.7;
  min-width: 80px;
}

.log-message {
  font-size: 0.875rem;
}

.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
}

.btn-secondary {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background-color: var(--bg-tertiary);
}
</style>