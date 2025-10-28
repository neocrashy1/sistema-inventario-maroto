<template>
  <div class="quality-monitor">
    <div class="monitor-header">
      <h3>
        <i class="fas fa-chart-line"></i>
        Monitoramento de Qualidade do Projeto
      </h3>
      <div class="monitor-actions">
        <span class="last-update">
          Última atualização: {{ formatTime(lastUpdate) }}
        </span>
        <button class="btn btn-sm btn-primary" @click="refreshMetrics">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        </button>
      </div>
    </div>

    <!-- Score Geral -->
    <div class="quality-score">
      <div class="score-circle" :class="getScoreClass(overallScore)">
        <div class="score-value">{{ overallScore }}%</div>
        <div class="score-label">Score Geral</div>
      </div>
      <div class="score-target">
        <div class="target-info">
          <span class="current">Atual: {{ overallScore }}%</span>
          <span class="target">Meta: {{ targetScore }}%</span>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: (overallScore / targetScore * 100) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Métricas por Sprint -->
    <div class="sprint-metrics">
      <div class="sprint-grid">
        <div 
          v-for="sprint in sprintMetrics" 
          :key="sprint.id"
          class="sprint-card"
          :class="sprint.status"
        >
          <div class="sprint-header">
            <h4>{{ sprint.name }}</h4>
            <span class="sprint-status" :class="sprint.status">
              {{ getStatusLabel(sprint.status) }}
            </span>
          </div>
          <div class="sprint-progress">
            <div class="progress-info">
              <span>{{ sprint.completed }}/{{ sprint.total }} tarefas</span>
              <span>{{ Math.round(sprint.progress) }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: sprint.progress + '%' }"
              ></div>
            </div>
          </div>
          <div class="sprint-tasks">
            <div 
              v-for="task in sprint.tasks" 
              :key="task.id"
              class="task-item"
              :class="task.status"
            >
              <i :class="getTaskIcon(task.status)"></i>
              <span>{{ task.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Métricas Técnicas -->
    <div class="technical-metrics">
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon performance">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="metric-content">
            <h4>Performance</h4>
            <div class="metric-value">{{ technicalMetrics.performance }}%</div>
            <div class="metric-trend" :class="getTrendClass(technicalMetrics.performanceTrend)">
              <i :class="getTrendIcon(technicalMetrics.performanceTrend)"></i>
              {{ technicalMetrics.performanceTrend }}%
            </div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon security">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="metric-content">
            <h4>Segurança</h4>
            <div class="metric-value">{{ technicalMetrics.security }}%</div>
            <div class="metric-trend" :class="getTrendClass(technicalMetrics.securityTrend)">
              <i :class="getTrendIcon(technicalMetrics.securityTrend)"></i>
              {{ technicalMetrics.securityTrend }}%
            </div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon ux">
            <i class="fas fa-user-friends"></i>
          </div>
          <div class="metric-content">
            <h4>UX/UI</h4>
            <div class="metric-value">{{ technicalMetrics.ux }}%</div>
            <div class="metric-trend" :class="getTrendClass(technicalMetrics.uxTrend)">
              <i :class="getTrendIcon(technicalMetrics.uxTrend)"></i>
              {{ technicalMetrics.uxTrend }}%
            </div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon code-quality">
            <i class="fas fa-code"></i>
          </div>
          <div class="metric-content">
            <h4>Qualidade do Código</h4>
            <div class="metric-value">{{ technicalMetrics.codeQuality }}%</div>
            <div class="metric-trend" :class="getTrendClass(technicalMetrics.codeQualityTrend)">
              <i :class="getTrendIcon(technicalMetrics.codeQualityTrend)"></i>
              {{ technicalMetrics.codeQualityTrend }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alertas e Recomendações -->
    <div class="quality-alerts" v-if="alerts.length > 0">
      <h4>
        <i class="fas fa-exclamation-triangle"></i>
        Alertas e Recomendações
      </h4>
      <div class="alerts-list">
        <div 
          v-for="alert in alerts" 
          :key="alert.id"
          class="alert-item"
          :class="alert.type"
        >
          <div class="alert-icon">
            <i :class="getAlertIcon(alert.type)"></i>
          </div>
          <div class="alert-content">
            <h5>{{ alert.title }}</h5>
            <p>{{ alert.message }}</p>
            <span class="alert-time">{{ formatTime(alert.timestamp) }}</span>
          </div>
          <button class="alert-dismiss" @click="dismissAlert(alert.id)">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Estado reativo
const loading = ref(false)
const lastUpdate = ref(new Date())
const refreshInterval = ref(null)

// Configurações
const targetScore = ref(92)
const overallScore = ref(85)

// Métricas dos Sprints
const sprintMetrics = ref([
  {
    id: 'sprint1',
    name: 'Sprint 1 - Fundação UX',
    status: 'in_progress',
    completed: 1,
    total: 3,
    progress: 33,
    tasks: [
      { id: 'loading_states', name: 'Loading States', status: 'pending' },
      { id: 'form_validation', name: 'Validação de Formulários', status: 'pending' },
      { id: 'error_handling', name: 'Tratamento de Erros', status: 'pending' }
    ]
  },
  {
    id: 'sprint2',
    name: 'Sprint 2 - Qualidade & Performance',
    status: 'pending',
    completed: 0,
    total: 3,
    progress: 0,
    tasks: [
      { id: 'code_cleanup', name: 'Limpeza de Código', status: 'pending' },
      { id: 'lazy_loading', name: 'Lazy Loading', status: 'pending' },
      { id: 'unit_tests', name: 'Testes Unitários', status: 'pending' }
    ]
  },
  {
    id: 'sprint3',
    name: 'Sprint 3 - Otimização Avançada',
    status: 'pending',
    completed: 0,
    total: 2,
    progress: 0,
    tasks: [
      { id: 'api_cache', name: 'Cache Inteligente', status: 'pending' },
      { id: 'accessibility', name: 'Acessibilidade', status: 'pending' }
    ]
  }
])

// Métricas Técnicas
const technicalMetrics = ref({
  performance: 82,
  performanceTrend: +3,
  security: 95,
  securityTrend: 0,
  ux: 78,
  uxTrend: +5,
  codeQuality: 85,
  codeQualityTrend: +2
})

// Alertas
const alerts = ref([
  {
    id: 1,
    type: 'warning',
    title: 'Console.log em Produção',
    message: 'Encontrados 23 console.log no código que devem ser removidos.',
    timestamp: new Date()
  },
  {
    id: 2,
    type: 'info',
    title: 'Loading States Inconsistentes',
    message: 'Alguns componentes não possuem loading states implementados.',
    timestamp: new Date()
  }
])

// Computed
const progressToTarget = computed(() => {
  return Math.round((overallScore.value / targetScore.value) * 100)
})

// Métodos
const refreshMetrics = async () => {
  loading.value = true
  try {
    // Simular atualização de métricas
    await new Promise(resolve => setTimeout(resolve, 1000))
    lastUpdate.value = new Date()
    
    // Atualizar score geral baseado no progresso dos sprints
    const totalTasks = sprintMetrics.value.reduce((sum, sprint) => sum + sprint.total, 0)
    const completedTasks = sprintMetrics.value.reduce((sum, sprint) => sum + sprint.completed, 0)
    const progressPercentage = (completedTasks / totalTasks) * 100
    
    // Calcular novo score (85% base + progresso das melhorias)
    overallScore.value = Math.min(92, 85 + Math.round(progressPercentage * 0.07))
    
  } finally {
    loading.value = false
  }
}

const getScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  return 'poor'
}

const getStatusLabel = (status) => {
  const labels = {
    'completed': 'Concluído',
    'in_progress': 'Em Progresso',
    'pending': 'Pendente'
  }
  return labels[status] || status
}

const getTaskIcon = (status) => {
  const icons = {
    'completed': 'fas fa-check-circle',
    'in_progress': 'fas fa-clock',
    'pending': 'fas fa-circle'
  }
  return icons[status] || 'fas fa-circle'
}

const getTrendClass = (trend) => {
  if (trend > 0) return 'positive'
  if (trend < 0) return 'negative'
  return 'neutral'
}

const getTrendIcon = (trend) => {
  if (trend > 0) return 'fas fa-arrow-up'
  if (trend < 0) return 'fas fa-arrow-down'
  return 'fas fa-minus'
}

const getAlertIcon = (type) => {
  const icons = {
    'error': 'fas fa-exclamation-circle',
    'warning': 'fas fa-exclamation-triangle',
    'info': 'fas fa-info-circle',
    'success': 'fas fa-check-circle'
  }
  return icons[type] || 'fas fa-info-circle'
}

const dismissAlert = (alertId) => {
  const index = alerts.value.findIndex(alert => alert.id === alertId)
  if (index !== -1) {
    alerts.value.splice(index, 1)
  }
}

const formatTime = (date) => {
  return new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

// Lifecycle
onMounted(() => {
  refreshMetrics()
  // Auto-refresh a cada 30 segundos
  refreshInterval.value = setInterval(refreshMetrics, 30000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.quality-monitor {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.monitor-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.monitor-header h3 i {
  margin-right: 8px;
  color: #3b82f6;
}

.monitor-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.last-update {
  font-size: 0.875rem;
  color: #6b7280;
}

.quality-score {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background: conic-gradient(from 0deg, #3b82f6 0deg, #3b82f6 var(--progress, 85%), #e5e7eb var(--progress, 85%) 360deg);
}

.score-circle::before {
  content: '';
  position: absolute;
  width: 90px;
  height: 90px;
  background: white;
  border-radius: 50%;
}

.score-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  z-index: 1;
}

.score-label {
  font-size: 0.75rem;
  color: #6b7280;
  z-index: 1;
}

.score-circle.excellent {
  background: conic-gradient(from 0deg, #10b981 0deg, #10b981 var(--progress, 85%), #e5e7eb var(--progress, 85%) 360deg);
}

.score-circle.good {
  background: conic-gradient(from 0deg, #3b82f6 0deg, #3b82f6 var(--progress, 85%), #e5e7eb var(--progress, 85%) 360deg);
}

.score-circle.average {
  background: conic-gradient(from 0deg, #f59e0b 0deg, #f59e0b var(--progress, 85%), #e5e7eb var(--progress, 85%) 360deg);
}

.score-target {
  flex: 1;
}

.target-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.current, .target {
  font-size: 0.875rem;
  color: #6b7280;
}

.current {
  font-weight: 600;
  color: #1f2937;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.sprint-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.sprint-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.sprint-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.sprint-card.completed {
  border-color: #10b981;
  background: #f0fdf4;
}

.sprint-card.in_progress {
  border-color: #3b82f6;
  background: #eff6ff;
}

.sprint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sprint-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.sprint-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.sprint-status.completed {
  background: #dcfce7;
  color: #166534;
}

.sprint-status.in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.sprint-status.pending {
  background: #f3f4f6;
  color: #374151;
}

.sprint-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.875rem;
  color: #6b7280;
}

.sprint-tasks {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #6b7280;
}

.task-item.completed {
  color: #10b981;
}

.task-item.in_progress {
  color: #3b82f6;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.metric-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.metric-icon.performance {
  background: #3b82f6;
}

.metric-icon.security {
  background: #10b981;
}

.metric-icon.ux {
  background: #f59e0b;
}

.metric-icon.code-quality {
  background: #8b5cf6;
}

.metric-content h4 {
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.metric-trend {
  font-size: 0.75rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-trend.positive {
  color: #10b981;
}

.metric-trend.negative {
  color: #ef4444;
}

.metric-trend.neutral {
  color: #6b7280;
}

.quality-alerts h4 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.quality-alerts h4 i {
  margin-right: 8px;
  color: #f59e0b;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.alert-item.error {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.alert-item.warning {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.alert-item.info {
  background: #eff6ff;
  border-left-color: #3b82f6;
}

.alert-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.alert-content {
  flex: 1;
}

.alert-content h5 {
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.alert-content p {
  margin: 0 0 8px 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.alert-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

.alert-dismiss {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.alert-dismiss:hover {
  color: #6b7280;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.75rem;
}

.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>