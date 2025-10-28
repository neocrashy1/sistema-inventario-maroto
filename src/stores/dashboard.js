import logger from '@/utils/logger'
import { defineStore } from 'pinia'
import { ref, computed, watch, nextTick } from 'vue'
import { useAssetsStore } from './assets'
import { dashboardAPI, alertsAPI, cachedAPI, handleAPIError } from '@/services/api'
import { debounce, createDataUpdateDebounce, createBatchProcessor } from '@/utils/debounce'
import { useOptimizedComputed } from '@/composables/useOptimizedComputed'
import { useDataProcessor } from '@/composables/useWebWorker'

export const useDashboardStore = defineStore('dashboard', () => {
  // Composables para otimização
  const { 
    cachedComputed, 
    optimizedWatch, 
    memoizedComputed, 
    batchedComputed,
    clearCache: clearComputedCache 
  } = useOptimizedComputed()
  
  const {
    initializeDataProcessor,
    processMachineData,
    processChartData,
    calculateMetrics,
    processAlerts,
    calculatePerformance,
    isProcessing: isWorkerProcessing
  } = useDataProcessor()

  // Estado reativo
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)
  const refreshInterval = ref(null)
  
  // Cache e performance
  const dataCache = ref(new Map())
  const pendingRequests = ref(new Set())
  const updateQueue = ref([])
  const isUpdating = ref(false)
  const processingStats = ref({
    lastProcessingTime: 0,
    averageProcessingTime: 0,
    totalProcessedItems: 0
  })
  
  // Métricas de sistema
  const systemMetrics = ref({
    uptime: 0,
    performance: {
      cpu: 0,
      memory: 0,
      disk: 0
    },
    networkStatus: 'online',
    lastBackup: null,
    activeUsers: 0
  })
  
  // Dados de tendências
  const trends = ref({
    assetsGrowth: [],
    valueGrowth: [],
    maintenanceCosts: [],
    utilizationRates: []
  })
  
  // Alertas e notificações
  const alerts = ref([])
  const notifications = ref([])
  
  // Configurações do dashboard
  const dashboardConfig = ref({
    autoRefresh: true,
    refreshRate: 30000, // 30 segundos
    theme: 'light',
    enableWebWorkers: true,
    cacheEnabled: true,
    batchUpdates: true,
    optimizedRendering: true,
    widgets: {
      assetsOverview: true,
      maintenanceAlerts: true,
      financialSummary: true,
      performanceMetrics: true,
      recentActivity: true,
      warrantyExpiration: true
    }
  })

  // Getters computados com memoização
  const assetsStore = useAssetsStore()
  
  // Cache para computed properties pesadas
  const computedCache = ref(new Map())
  const cacheExpiry = ref(new Map())
  
  const kpiMetrics = memoizedComputed(() => {
    const metrics = {
      totalAssets: assetsStore.totalAssets,
      totalValue: assetsStore.totalValue,
      activeAssets: assetsStore.assetsByStatus['Ativo'] || 0,
      maintenanceAssets: assetsStore.assetsByStatus['Manutenção'] || 0,
      expiredWarranties: assetsStore.expiredWarranties.length,
      expiringWarranties: assetsStore.expiringWarrantyAssets.length,
      utilizationRate: calculateUtilizationRate(),
      maintenanceCostMTD: calculateMaintenanceCostMTD()
    }
    
    // Processar métricas com Web Worker se habilitado
    if (dashboardConfig.value.enableWebWorkers) {
      return calculateMetrics(metrics)
    }
    
    return metrics
  }, {
    cacheKey: 'kpiMetrics',
    ttl: 30000, // 30 segundos
    dependencies: () => [
      assetsStore.totalAssets,
      assetsStore.totalValue,
      assetsStore.assetsByStatus,
      assetsStore.expiredWarranties.length,
      assetsStore.expiringWarrantyAssets.length
    ]
  })
  
  const assetsCategoryData = batchedComputed(() => {
    const categories = assetsStore.assetsByCategory
    const chartData = {
      labels: Object.keys(categories),
      datasets: [{
        label: 'Ativos por Categoria',
        data: Object.values(categories),
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
          '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
        ],
        borderWidth: 0
      }]
    }
    
    // Processar dados do gráfico com Web Worker se habilitado
    if (dashboardConfig.value.enableWebWorkers) {
      return processChartData(chartData, 'category')
    }
    
    return chartData
  }, {
    cacheKey: 'assetsCategoryData',
    ttl: 60000, // 60 segundos
    batchDelay: 100,
    dependencies: () => [assetsStore.assetsByCategory]
  })
  
  const assetsStatusData = batchedComputed(() => {
    const statuses = assetsStore.assetsByStatus
    const chartData = {
      labels: Object.keys(statuses),
      datasets: [{
        label: 'Ativos por Status',
        data: Object.values(statuses),
        backgroundColor: [
          '#10B981', // Ativo - Verde
          '#F59E0B', // Manutenção - Amarelo
          '#6B7280', // Inativo - Cinza
          '#3B82F6', // Emprestado - Azul
          '#EF4444'  // Descartado - Vermelho
        ],
        borderWidth: 0
      }]
    }
    
    // Processar dados do gráfico com Web Worker se habilitado
    if (dashboardConfig.value.enableWebWorkers) {
      return processChartData(chartData, 'status')
    }
    
    return chartData
  }, {
    cacheKey: 'assetsStatusData',
    ttl: 60000, // 60 segundos
    batchDelay: 100,
    dependencies: () => [assetsStore.assetsByStatus]
  })
  
  const monthlyTrendsData = computed(() => {
    const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    const currentMonth = new Date().getMonth()
    const last6Months = months.slice(Math.max(0, currentMonth - 5), currentMonth + 1)
    
    return {
      labels: last6Months,
      datasets: [
        {
          label: 'Novos Ativos',
          data: generateTrendData(last6Months.length, 5, 25),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Manutenções',
          data: generateTrendData(last6Months.length, 2, 15),
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    }
  })
  
  const recentActivities = computed(() => [
    {
      id: 1,
      type: 'asset_added',
      title: 'Novo ativo cadastrado',
      description: 'Notebook Dell Latitude 5520 adicionado ao inventário',
      timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 min atrás
      user: 'João Silva',
      icon: 'plus',
      color: 'success'
    },
    {
      id: 2,
      type: 'maintenance_scheduled',
      title: 'Manutenção agendada',
      description: 'Servidor HP ProLiant agendado para manutenção preventiva',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2h atrás
      user: 'Maria Santos',
      icon: 'wrench',
      color: 'warning'
    },
    {
      id: 3,
      type: 'warranty_expired',
      title: 'Garantia expirada',
      description: 'Monitor LG 24" - garantia expirou hoje',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4h atrás
      user: 'Sistema',
      icon: 'alert-triangle',
      color: 'danger'
    },
    {
      id: 4,
      type: 'asset_moved',
      title: 'Ativo movimentado',
      description: 'Impressora HP LaserJet movida para Sala 102',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6), // 6h atrás
      user: 'Carlos Oliveira',
      icon: 'move',
      color: 'info'
    }
  ])
  
  const criticalAlerts = computed(() => [
    {
      id: 1,
      type: 'warranty_expiring',
      title: 'Garantias expirando',
      message: `${kpiMetrics.value.expiringWarranties} ativos com garantia expirando em 30 dias`,
      severity: 'warning',
      count: kpiMetrics.value.expiringWarranties,
      action: 'view_warranties'
    },
    {
      id: 2,
      type: 'maintenance_overdue',
      title: 'Manutenções em atraso',
      message: '3 ativos com manutenção preventiva em atraso',
      severity: 'danger',
      count: 3,
      action: 'view_maintenance'
    },
    {
      id: 3,
      type: 'high_value_assets',
      title: 'Ativos de alto valor',
      message: '12 ativos acima de R$ 10.000 sem seguro atualizado',
      severity: 'info',
      count: 12,
      action: 'view_insurance'
    }
  ])

  // Funções de fetch otimizadas com debounce
  const fetchDashboardDataCore = async (forceRefresh = false) => {
    // Evitar requisições duplicadas
    const requestKey = `dashboard-${forceRefresh}`
    if (pendingRequests.value.has(requestKey)) {
      return
    }
    
    pendingRequests.value.add(requestKey)
    loading.value = true
    error.value = null
    
    try {
      // Verificar cache local primeiro
      if (!forceRefresh && dataCache.value.has('dashboardData')) {
        const cached = dataCache.value.get('dashboardData')
        const cacheAge = Date.now() - cached.timestamp
        
        // Cache válido por 2 minutos
        if (cacheAge < 120000) {
          lastUpdate.value = new Date(cached.timestamp)
          return cached.data
        }
      }
      
      // Buscar dados em paralelo para melhor performance
      const [overviewResponse, systemMetricsData, alertsData, activityData] = await Promise.all([
        cachedAPI.dashboard.getStats({ forceRefresh }),
        fetchSystemMetrics(forceRefresh),
        fetchAlerts(forceRefresh),
        fetchRecentActivity()
      ])
      
      // Armazenar no cache
      const dashboardData = {
        overview: overviewResponse,
        systemMetrics: systemMetricsData,
        alerts: alertsData,
        activity: activityData
      }
      
      dataCache.value.set('dashboardData', {
        data: dashboardData,
        timestamp: Date.now()
      })
      
      lastUpdate.value = new Date()
      
      return dashboardData
      
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = 'Erro ao carregar dados do dashboard: ' + apiError.message
      logger.error('Erro no dashboard:', err)
      
      // Fallback para dados mock em caso de erro
      await fetchMockData()
    } finally {
      loading.value = false
      pendingRequests.value.delete(requestKey)
    }
  }
  
  // Versão debounced da função de fetch
  const fetchDashboardData = createDataUpdateDebounce(fetchDashboardDataCore, {
    delay: 1000,
    maxWait: 5000,
    onError: (error) => {
      logger.error('Erro na atualização do dashboard:', error)
      error.value = 'Erro na atualização automática dos dados'
    }
  })

  const fetchMockData = async () => {
    // Buscar dados dos ativos como fallback
    await assetsStore.fetchAssets()
    
    // Simular busca de métricas do sistema
    await fetchSystemMetrics()
    
    // Atualizar tendências
    updateTrends()
    
    // Buscar alertas mock
    await fetchAlertsFromMock()
  }
  
  const fetchSystemMetrics = async (forceRefresh = false) => {
    try {
      const response = await cachedAPI.dashboard.getMetrics({
        forceRefresh
      })
      systemMetrics.value = response.data
    } catch (err) {
      logger.warn('Failed to fetch system metrics from API, using mock data')
      // Fallback para dados simulados
      await new Promise(resolve => setTimeout(resolve, 500))
      
      systemMetrics.value = {
        uptime: Math.floor(Math.random() * 720) + 24, // 24-744 horas
        performance: {
          cpu: Math.floor(Math.random() * 40) + 20, // 20-60%
          memory: Math.floor(Math.random() * 30) + 40, // 40-70%
          disk: Math.floor(Math.random() * 20) + 60 // 60-80%
        },
        networkStatus: Math.random() > 0.1 ? 'online' : 'offline',
        lastBackup: new Date(Date.now() - 1000 * 60 * 60 * 12), // 12h atrás
        activeUsers: Math.floor(Math.random() * 20) + 5 // 5-25 usuários
      }
    }
  }

  const fetchAlerts = async (forceRefresh = false) => {
    try {
      const response = await cachedAPI.dashboard.getAlerts({
        forceRefresh
      })
      alerts.value = response.data.items || response.data
    } catch (err) {
      logger.warn('Failed to fetch alerts from API, using mock data')
      await fetchAlertsFromMock()
    }
  }

  const fetchRecentActivity = async () => {
    try {
      const response = await dashboardAPI.getRecentActivity()
      // Atualizar atividades recentes se necessário
    } catch (err) {
      logger.warn('Failed to fetch recent activity from API')
    }
  }

  const fetchAlertsFromMock = async () => {
    // Mock alerts data
    alerts.value = [
      {
        id: 1,
        type: 'warning',
        title: 'Garantia próxima do vencimento',
        message: '5 ativos com garantia vencendo em 30 dias',
        timestamp: new Date(Date.now() - 1000 * 60 * 15),
        read: false,
        priority: 'medium'
      },
      {
        id: 2,
        type: 'error',
        title: 'Falha na sincronização',
        message: 'Erro ao sincronizar dados do servidor principal',
        timestamp: new Date(Date.now() - 1000 * 60 * 60),
        read: false,
        priority: 'high'
      }
    ]
  }
  
  const updateTrends = () => {
    const months = 6
    trends.value = {
      assetsGrowth: generateTrendData(months, 10, 50),
      valueGrowth: generateTrendData(months, 50000, 200000),
      maintenanceCosts: generateTrendData(months, 5000, 25000),
      utilizationRates: generateTrendData(months, 70, 95)
    }
  }
  
  const fetchAlertsLegacy = async () => {
    // Simular busca de alertas (legacy)
    await new Promise(resolve => setTimeout(resolve, 300))
    
    alerts.value = [
      {
        id: 1,
        type: 'warning',
        title: 'Backup pendente',
        message: 'Último backup realizado há mais de 24 horas',
        timestamp: new Date(),
        read: false
      },
      {
        id: 2,
        type: 'info',
        title: 'Atualização disponível',
        message: 'Nova versão do sistema disponível',
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
        read: false
      }
    ]
  }
  
  // Auto-refresh otimizado com controle de visibilidade
  const isPageVisible = ref(true)
  const refreshTimeoutId = ref(null)
  
  // Debounced refresh para evitar atualizações excessivas
  const debouncedRefresh = debounce(() => {
    if (isPageVisible.value && dashboardConfig.value.autoRefresh) {
      fetchDashboardData()
    }
  }, 2000) // 2 segundos de debounce
  
  const startAutoRefresh = () => {
    if (dashboardConfig.value.autoRefresh && !refreshInterval.value) {
      // Usar requestAnimationFrame para melhor performance
      const scheduleNextRefresh = () => {
        refreshTimeoutId.value = setTimeout(() => {
          if (isPageVisible.value && dashboardConfig.value.autoRefresh) {
            debouncedRefresh()
          }
          
          if (dashboardConfig.value.autoRefresh) {
            scheduleNextRefresh()
          }
        }, dashboardConfig.value.refreshRate)
      }
      
      scheduleNextRefresh()
      refreshInterval.value = true // Marcar como ativo
    }
  }
  
  const stopAutoRefresh = () => {
    if (refreshInterval.value) {
      clearTimeout(refreshTimeoutId.value)
      debouncedRefresh.cancel()
      refreshInterval.value = null
      refreshTimeoutId.value = null
    }
  }
  
  // Controle de visibilidade da página
  const handleVisibilityChange = () => {
    isPageVisible.value = !document.hidden
    
    if (isPageVisible.value && dashboardConfig.value.autoRefresh) {
      // Atualizar dados quando a página voltar a ficar visível
      nextTick(() => {
        fetchDashboardData(true) // Force refresh
      })
    }
  }
  
  // Listener para visibilidade da página
  if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }
  
  const updateConfig = (newConfig) => {
    dashboardConfig.value = { ...dashboardConfig.value, ...newConfig }
    
    // Reiniciar auto-refresh se necessário
    if (newConfig.autoRefresh !== undefined || newConfig.refreshRate !== undefined) {
      stopAutoRefresh()
      if (dashboardConfig.value.autoRefresh) {
        startAutoRefresh()
      }
    }
  }
  
  const markAlertAsRead = (alertId) => {
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.read = true
    }
  }
  
  const dismissAlert = (alertId) => {
    const index = alerts.value.findIndex(a => a.id === alertId)
    if (index !== -1) {
      alerts.value.splice(index, 1)
    }
  }
  
  const exportDashboardData = (format = 'pdf') => {
    const data = {
      metrics: kpiMetrics.value,
      systemMetrics: systemMetrics.value,
      trends: trends.value,
      alerts: alerts.value,
      generatedAt: new Date().toISOString()
    }
    
    // Implementar exportação
    return data
  }

  // Funções auxiliares
  const calculateUtilizationRate = () => {
    const total = assetsStore.totalAssets
    const active = assetsStore.assetsByStatus['Ativo'] || 0
    return total > 0 ? Math.round((active / total) * 100) : 0
  }
  
  const calculateMaintenanceCostMTD = () => {
    // Simular cálculo de custo de manutenção do mês
    return Math.floor(Math.random() * 50000) + 10000
  }
  
  const generateTrendData = (length, min, max) => {
    return Array.from({ length }, () => 
      Math.floor(Math.random() * (max - min + 1)) + min
    )
  }
  
  const formatUptime = (hours) => {
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    return `${days}d ${remainingHours}h`
  }
  
  // Funções de otimização e limpeza
  const clearCache = () => {
    dataCache.value.clear()
    computedCache.value.clear()
    cacheExpiry.value.clear()
    pendingRequests.value.clear()
    clearComputedCache()
  }
  
  const clearExpiredCache = () => {
    const now = Date.now()
    
    // Limpar cache expirado de computed properties
    for (const [key, expiry] of cacheExpiry.value.entries()) {
      if (expiry <= now) {
        computedCache.value.delete(key)
        cacheExpiry.value.delete(key)
      }
    }
    
    // Limpar cache de dados antigos (mais de 10 minutos)
    for (const [key, data] of dataCache.value.entries()) {
      if (data.timestamp && (now - data.timestamp) > 600000) {
        dataCache.value.delete(key)
      }
    }
  }
  
  // Processador de lote para atualizações
  const batchUpdateProcessor = createBatchProcessor((updates) => {
    // Processar atualizações em lote para melhor performance
    updates.forEach(update => {
      if (update.type === 'kpi') {
        // Invalidar cache de KPIs
        computedCache.value.delete('kpiMetrics')
        cacheExpiry.value.delete('kpiMetrics')
      } else if (update.type === 'chart') {
        // Invalidar cache de gráficos
        computedCache.value.delete('assetsCategoryData')
        computedCache.value.delete('assetsStatusData')
        cacheExpiry.value.delete('assetsCategoryData')
        cacheExpiry.value.delete('assetsStatusData')
      }
    })
  }, 500)
  
  // Limpeza automática de cache a cada 5 minutos
  const cacheCleanupInterval = setInterval(clearExpiredCache, 300000)
  
  // Watcher otimizado para invalidar cache quando dados dos ativos mudarem
  optimizedWatch(
    () => [assetsStore.assets, assetsStore.lastUpdate],
    () => {
      batchUpdateProcessor({ type: 'kpi' })
      batchUpdateProcessor({ type: 'chart' })
    },
    { 
      deep: false,
      debounce: 300,
      immediate: false
    }
  )
  
  // Inicializar Web Workers se habilitado
  const initializeOptimizations = async () => {
    if (dashboardConfig.value.enableWebWorkers) {
      await initializeDataProcessor()
    }
  }

  // Cleanup ao destruir o store
  const cleanup = () => {
    stopAutoRefresh()
    clearCache()
    clearInterval(cacheCleanupInterval)
    
    if (typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
    
    // Cancelar debounces pendentes
    debouncedRefresh.cancel()
    fetchDashboardData.cancel()
    
    // Limpar composables
    clearComputedCache()
  }

  return {
    // Estado
    loading,
    error,
    lastUpdate,
    systemMetrics,
    trends,
    alerts,
    notifications,
    dashboardConfig,
    isUpdating,
    isPageVisible,
    
    // Getters
    kpiMetrics,
    assetsCategoryData,
    assetsStatusData,
    monthlyTrendsData,
    recentActivities,
    criticalAlerts,
    
    // Ações principais
    fetchDashboardData,
    fetchSystemMetrics,
    updateTrends,
    fetchAlerts,
    startAutoRefresh,
    stopAutoRefresh,
    updateConfig,
    markAlertAsRead,
    dismissAlert,
    exportDashboardData,
    formatUptime,
    
    // Funções de otimização
    clearCache,
    clearExpiredCache,
    initializeOptimizations,
    cleanup,
    
    // Estados de performance
    processingStats,
    isWorkerProcessing
  }
})